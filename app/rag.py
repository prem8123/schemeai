from __future__ import annotations

import os
from functools import lru_cache

from .data import SCHEMES
from .schema import Evidence

EMBEDDING_MODEL = os.getenv("SCHEMEAI_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RERANKER_MODEL = os.getenv("SCHEMEAI_RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RETRIEVAL_MODE = os.getenv("SCHEMEAI_RETRIEVAL_MODE", "dense").lower()


def _documents():
    docs = []
    for scheme in SCHEMES:
        for clause in scheme.provenance:
            docs.append((scheme, clause, scheme.source_text))
    # provenance is unique per source, while source_text is the combined clause corpus.
    # Prefer clause-level retrieval by pairing each provenance record with its reference text.
    docs = []
    for scheme in SCHEMES:
        for rule in scheme.eligibility_rules:
            docs.append((scheme, rule.provenance, next(c.text for c in _clauses(scheme) if c.id == rule.clause_id)))
        for clause in _clauses(scheme):
            if not any(d[1].reference == clause.provenance.reference for d in docs if d[0].id == scheme.id):
                docs.append((scheme, clause.provenance, clause.text))
    return docs


def _clauses(scheme):
    # Reconstruct clause-level text from the scheme source corpus when the loader does not
    # retain raw clauses. Official JSONL remains the source of truth for provenance.
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "data" / "official" / "schemes.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        if raw["id"] == scheme.id:
            from .schema import EligibilityClause
            return [EligibilityClause.model_validate(c) for c in raw["clauses"]]
    return []


@lru_cache(maxsize=1)
def _dense_models():
    if RETRIEVAL_MODE != "dense":
        return None, None
    from sentence_transformers import CrossEncoder, SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL), CrossEncoder(RERANKER_MODEL)


@lru_cache(maxsize=1)
def _dense_index():
    model, _ = _dense_models()
    docs = _documents()
    texts = [d[2] for d in docs]
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return docs, embeddings


def _lexical(query: str, top_k: int):
    import re
    q = set(re.findall(r"[\w]+", query.lower()))
    scored = []
    for scheme, provenance, text in _documents():
        tokens = set(re.findall(r"[\w]+", text.lower()))
        score = len(q & tokens) / max(1, len(q))
        if score > 0:
            scored.append((scheme, provenance, text, score))
    return sorted(scored, key=lambda x: x[3], reverse=True)[:top_k]


def retrieve(query: str, top_k: int = 5) -> list[Evidence]:
    if not query.strip():
        return []
    if RETRIEVAL_MODE != "dense":
        candidates = _lexical(query, top_k)
        return [
            Evidence(
                scheme_id=s.id,
                scheme_name=s.name,
                text=text,
                score=round(score, 4),
                retrieval_mode="lexical-test-fallback",
                provenance=p,
                freshness=s.freshness,
            )
            for s, p, text, score in candidates
        ]

    model, reranker = _dense_models()
    docs, embeddings = _dense_index()
    query_embedding = model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
    similarities = embeddings @ query_embedding
    candidate_count = min(len(docs), max(top_k * 4, 10))
    indices = similarities.argsort()[::-1][:candidate_count]
    candidates = [docs[i] for i in indices]
    pairs = [[query, c[2]] for c in candidates]
    rerank_scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, rerank_scores), key=lambda x: float(x[1]), reverse=True)[:top_k]
    return [
        Evidence(
            scheme_id=s.id,
            scheme_name=s.name,
            text=text,
            score=round(float(score), 4),
            retrieval_mode="dense+cross-encoder-reranker",
            provenance=p,
            freshness=s.freshness,
        )
        for (s, p, text), score in ranked
    ]
