from fastapi import FastAPI
from .models import StudentProfile, RecommendationResponse
from .data import SCHEMES
from .eligibility import rank
from .rag import retrieve

app = FastAPI(title="SchemeAI", version="0.1.0", description="AI-ready scholarship and education scheme eligibility assistant")

DISCLAIMER = "SchemeAI provides informational matching only. Always verify eligibility and application details against the current official scheme authority before applying."

@app.get("/")
def root():
    return {"name": "SchemeAI", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/schemes")
def schemes():
    return {"count": len(SCHEMES), "schemes": [s.model_dump(exclude={"source_text"}) for s in SCHEMES]}

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(profile: StudentProfile, query: str | None = None, language: str = "en"):
    results = rank(profile, SCHEMES)
    return RecommendationResponse(query=query, language=language, profile=profile, results=results[:10], disclaimer=DISCLAIMER)

@app.get("/search")
def search(q: str, top_k: int = 5):
    return {"query": q, "evidence": [e.__dict__ for e in retrieve(q, top_k)]}
