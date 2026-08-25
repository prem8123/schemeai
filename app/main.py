from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .data import SCHEMES
from .eligibility import rank
from .freshness import stale_schemes
from .llm import LLMClient
from .models import RecommendationResponse, StudentProfile
from .rag import retrieve

app = FastAPI(
    title="SchemeAI",
    version="0.3.0",
    description="Scholarship and education scheme eligibility assistant with provenance-first RAG",
)
DISCLAIMER = (
    "Informational matching only. Verify current eligibility and application details with the official scheme authority. "
    "SchemeAI never replaces the official application portal or scheme authority."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "SchemeAI", "status": "running", "docs": "/docs", "data_mode": "official-plus-separated-demo-fixtures"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_configured": LLMClient().available(),
        "scheme_count": len(SCHEMES),
        "stale_scheme_count": len(stale_schemes()),
    }


@app.get("/schemes")
def schemes():
    return {"count": len(SCHEMES), "schemes": [s.model_dump() for s in SCHEMES]}


@app.get("/freshness")
def freshness():
    return {"stale": stale_schemes(), "stale_count": len(stale_schemes())}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(
    profile: StudentProfile,
    query: str | None = Query(default=None, max_length=1000),
    language: str = Query(default="en", pattern="^(en|kn|hi)$"),
):
    results = rank(profile, SCHEMES)
    return RecommendationResponse(
        query=query,
        language=language,
        profile=profile,
        results=results[:10],
        disclaimer=DISCLAIMER,
    )


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=1000), top_k: int = Query(default=5, ge=1, le=20)):
    evidence = retrieve(q, top_k)
    return {"query": q, "evidence": [e.model_dump() for e in evidence]}


@app.post("/ask")
def ask(
    profile: StudentProfile,
    question: str = Query(min_length=2, max_length=2000),
    language: str = Query(default="en", pattern="^(en|kn|hi)$"),
):
    evidence = retrieve(question, top_k=5)
    results = rank(profile, SCHEMES)
    client = LLMClient()
    answer = client.answer(question, [e.model_dump() for e in evidence])
    return {
        "question": question,
        "language": language,
        "answer": answer,
        "recommendations": [r.model_dump() for r in results[:5]],
        "evidence": [e.model_dump() for e in evidence],
        "disclaimer": DISCLAIMER,
    }
