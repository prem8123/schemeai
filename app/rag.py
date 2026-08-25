from dataclasses import dataclass
import re
from .data import SCHEMES

@dataclass
class Evidence:
    scheme_id: str
    scheme_name: str
    source: str
    page: str | None
    text: str
    score: float


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def retrieve(query: str, top_k: int = 5) -> list[Evidence]:
    q = tokenize(query)
    scored = []
    for s in SCHEMES:
        corpus = " ".join([s.name, s.description, s.benefit, s.source_text, s.authority, s.state or ""])
        tokens = tokenize(corpus)
        score = len(q & tokens) / max(1, len(q))
        if score > 0:
            scored.append(Evidence(s.id, s.name, s.source, s.source_page, s.source_text, round(score, 3)))
    return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]
