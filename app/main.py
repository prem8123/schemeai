from __future__ import annotations

import logging
import time
import uuid
from collections import Counter

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .data import SCHEMES
from .eligibility import rank
from .freshness import stale_schemes
from .llm import LLMClient
from .logging_config import configure_logging
from .models import RecommendationResponse, StudentProfile
from .rag import retrieve
from .security import clean_user_text

configure_logging()
logger = logging.getLogger("schemeai.api")
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="SchemeAI",
    version="0.4.0",
    description="Scholarship and education scheme eligibility assistant with provenance-first RAG",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


@app.middleware("http")
async def request_metrics(request: Request, call_next):
    request_id = str(uuid.uuid4())
    started = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


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
    stale = stale_schemes()
    return {"stale": stale, "stale_count": len(stale)}


@app.post("/recommend", response_model=RecommendationResponse)
@limiter.limit("30/minute")
def recommend(
    request: Request,
    profile: StudentProfile,
    query: str | None = Query(default=None, max_length=1000),
    language: str = Query(default="en", pattern="^(en|kn|hi)$"),
):
    safe_query = clean_user_text(query) if query else None
    results = rank(profile, SCHEMES)
    distribution = Counter(r.status for r in results)
    logger.info("eligibility_distribution", extra={"tier_distribution": dict(distribution)})
    return RecommendationResponse(
        query=safe_query,
        language=language,
        profile=profile,
        results=results[:10],
        disclaimer=DISCLAIMER,
    )


@app.get("/search")
@limiter.limit("30/minute")
def search(request: Request, q: str = Query(min_length=2, max_length=1000), top_k: int = Query(default=5, ge=1, le=20)):
    safe_query = clean_user_text(q, 1000)
    evidence = retrieve(safe_query, top_k)
    logger.info("retrieval_complete", extra={"retrieval_hits": len(evidence), "top_k": top_k})
    return {"query": safe_query, "evidence": [e.model_dump() for e in evidence]}


@app.post("/ask")
@limiter.limit("20/minute")
def ask(
    request: Request,
    profile: StudentProfile,
    question: str = Query(min_length=2, max_length=2000),
    language: str = Query(default="en", pattern="^(en|kn|hi)$"),
):
    safe_question = clean_user_text(question)
    evidence = retrieve(safe_question, top_k=5)
    results = rank(profile, SCHEMES)
    client = LLMClient()
    answer = client.answer(safe_question, [e.model_dump() for e in evidence])
    logger.info("retrieval_complete", extra={"retrieval_hits": len(evidence), "top_k": 5})
    return {
        "question": safe_question,
        "language": language,
        "answer": answer,
        "recommendations": [r.model_dump() for r in results[:5]],
        "evidence": [e.model_dump() for e in evidence],
        "disclaimer": DISCLAIMER,
    }
