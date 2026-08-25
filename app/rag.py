from __future__ import annotations

import os
from functools import lru_cache

from .data import SCHEMES
from .schema import EligibilityClause, Evidence

EMBEDDING_MODEL = os.getenv(
    "SCHEMEAI_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
RERANKER_MODEL = os.getenv(
    "SCHEMEAI_RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
)
RETRIEVAL_MODE = os.getenv("SCHEMEAI_RETRIEVAL_MODE", "dense").lower()


def _clauses(scheme):
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "official" / "schemes.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        if raw["id"] == scheme.id:
            return [EligibilityClause.model_validate(c) for c in raw["clauses"]]
    return []


def _documents():
    docs = []
    for scheme in SCHEMES:
        for clause in _clauses(scheme):
            docs.append((scheme, clause.provenance, clause.text))
    return docs


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
    rerank_scores = reranker.predict([[query, c[2]] for c in candidates])
    ranked = sorted(zip(candidates, rerank_scores), key=lambda x: float(x[1]), reverse=True)[:top_k]
    return [
        Evidence(
            scheme_id=s.id,
            scheme_name=s.name,
            text=text,
            score=round(float(score), 4),
            retrieval_mode="dense+multilingual-cross-encoder-reranker",
            provenance=p,
            freshness=s.freshness,
        )
        for (s, p, text), score in ranked
    ]
