from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import StudentProfile, RecommendationResponse
from .data import SCHEMES
from .eligibility import rank
from .rag import retrieve
from .llm import LLMClient

app = FastAPI(title="SchemeAI", version="0.3.0", description="Scholarship and education scheme eligibility assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

DISCLAIMER = "Informational matching only. Verify current eligibility and application details with the official scheme authority before applying."

@app.get("/")
def root():
    return {"name": "SchemeAI", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "llm_configured": LLMClient().available(), "scheme_count": len(SCHEMES)}

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

@app.post("/ask")
def ask(profile: StudentProfile, question: str, language: str = "en"):
    evidence = retrieve(question, top_k=5)
    results = rank(profile, SCHEMES)
    answer = LLMClient().answer(question, [e.__dict__ for e in evidence])
    return {"question": question, "language": language, "answer": answer, "recommendations": [r.model_dump() for r in results[:5]], "evidence": [e.__dict__ for e in evidence], "disclaimer": DISCLAIMER}
