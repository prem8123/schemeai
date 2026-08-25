from .models import StudentProfile
from .rag import retrieve
from .eligibility import rank
from .data import SCHEMES

class SchemeAIOrchestrator:
    """Small deterministic orchestration layer; replace individual steps with LLM agents later."""
    def investigate(self, profile: StudentProfile, query: str):
        evidence = retrieve(query, top_k=5)
        recommendations = rank(profile, SCHEMES)
        return {"evidence": evidence, "recommendations": recommendations}
