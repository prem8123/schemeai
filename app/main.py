from __future__ import annotations
import logging, os, time, uuid
from collections import Counter
from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from .agent import run as run_agent
from .auth import require_api_key
from .data import SCHEMES
from .freshness import stale_schemes
from .language import detect_supported_language
from .llm import LLMClient
from .logging_config import configure_logging
from .models import RecommendationResponse, StudentProfile
from .rag import retrieve
from .security import clean_user_text

configure_logging()
logger=logging.getLogger("schemeai.api")
limiter=Limiter(key_func=get_remote_address,default_limits=["60/minute"])
app=FastAPI(title="SchemeAI",version="0.6.0",description="Multilingual scholarship and education scheme assistant with provenance-first Agentic RAG")
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
DISCLAIMER="Informational matching only. Verify current eligibility, deadlines, documents, institution status, and application details with the official scheme authority. SchemeAI never replaces the official portal."
allowed_origins=[x.strip() for x in os.getenv("SCHEMEAI_ALLOWED_ORIGINS","*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=allowed_origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])

@app.middleware("http")
async def request_metrics(request:Request,call_next):
    request_id=str(uuid.uuid4()); started=time.perf_counter()
    response=await call_next(request)
    response.headers["X-Request-ID"]=request_id
    logger.info("request_complete",extra={"request_id":request_id,"path":request.url.path,"method":request.method,"status_code":response.status_code,"latency_ms":round((time.perf_counter()-started)*1000,2)})
    return response

@app.get("/")
def root():
    return {"name":"SchemeAI","status":"running","docs":"/docs","data_mode":"official-plus-separated-demo-fixtures","agentic_rag":True}

@app.get("/health")
def health():
    return {"status":"ok","llm_configured":LLMClient().available(),"api_key_protection":bool(os.getenv("SCHEMEAI_API_KEY")),"retrieval_mode":os.getenv("SCHEMEAI_RETRIEVAL_MODE","dense"),"scheme_count":len(SCHEMES),"stale_scheme_count":len(stale_schemes())}

@app.get("/schemes")
def schemes(_:None=Depends(require_api_key)):
    return {"count":len(SCHEMES),"schemes":[s.model_dump(mode="json") for s in SCHEMES]}

@app.get("/freshness")
def freshness(_:None=Depends(require_api_key)):
    stale=stale_schemes()
    return {"stale":stale,"stale_count":len(stale)}

@app.post("/recommend",response_model=RecommendationResponse)
@limiter.limit("30/minute")
def recommend(request:Request,profile:StudentProfile,_:None=Depends(require_api_key),query:str|None=Query(default=None,max_length=1000),language:str=Query(default="en",pattern="^(en|kn|hi)$")):
    safe_query=clean_user_text(query) if query else None
    result=run_agent(safe_query,profile,SCHEMES,top_k=5)
    recommendations=result["recommendations"]
    logger.info("agent_complete",extra={"route":result["route"],"tier_distribution":dict(Counter(r.status for r in recommendations))})
    return RecommendationResponse(query=safe_query,language=language,profile=profile,results=recommendations,disclaimer=DISCLAIMER)

@app.get("/search")
@limiter.limit("30/minute")
def search(request:Request,_:None=Depends(require_api_key),q:str=Query(min_length=2,max_length=1000),top_k:int=Query(default=5,ge=1,le=20)):
    safe_query=clean_user_text(q,1000)
    evidence=retrieve(safe_query,top_k)
    return {"query":safe_query,"detected_language":detect_supported_language(safe_query),"evidence":[e.model_dump(mode="json") for e in evidence]}

@app.post("/ask")
@limiter.limit("20/minute")
def ask(request:Request,profile:StudentProfile,_:None=Depends(require_api_key),question:str=Query(min_length=2,max_length=2000),language:str=Query(default="en",pattern="^(en|kn|hi)$")):
    safe_question=clean_user_text(question,2000)
    detected_language=detect_supported_language(safe_question,fallback=language)
    result=run_agent(safe_question,profile,SCHEMES,top_k=5)
    evidence=result["evidence"]
    answer=LLMClient().answer(safe_question,[e.model_dump(mode="json") for e in evidence],language=detected_language)
    return {"question":safe_question,"language":detected_language,"route":result["route"],"route_reason":result["route_reason"],"answer":answer,"recommendations":[r.model_dump(mode="json") for r in result["recommendations"][:5]],"evidence":[e.model_dump(mode="json") for e in evidence],"disclaimer":DISCLAIMER}
