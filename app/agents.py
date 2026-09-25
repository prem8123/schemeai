from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .data import SCHEMES
from .eligibility import rank
from .llm import LLMClient
from .models import StudentProfile
from .rag import retrieve


@dataclass(frozen=True)
class AgentStep:
    name: str
    status: str
    detail: str


class SchemeAIOrchestrator:
    """Planner-style orchestration with deterministic safety boundaries.

    The LLM may assist with answering, but it does not decide eligibility.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()

    def plan(self, query: str) -> list[str]:
        query = query.strip()
        if not query:
            return ["eligibility"]

        plan = ["retrieval", "eligibility"]
        question_terms = ("why", "explain", "how", "what", "which", "can i")
        if any(term in query.lower() for term in question_terms):
            plan.append("answer")
        return plan

    def investigate(
        self,
        profile: StudentProfile,
        query: str,
        language: str = "en",
    ) -> dict[str, Any]:
        plan = self.plan(query)
        steps: list[AgentStep] = []
        evidence = []
        recommendations = []
        answer = None

        if "retrieval" in plan:
            evidence = retrieve(query, top_k=5)
            steps.append(
                AgentStep(
                    name="retrieval",
                    status="completed",
                    detail=f"Retrieved {len(evidence)} provenance-backed evidence items.",
                )
            )

        recommendations = rank(profile, SCHEMES)
        steps.append(
            AgentStep(
                name="eligibility",
                status="completed",
                detail=f"Evaluated {len(recommendations)} schemes with deterministic rules.",
            )
        )

        if "answer" in plan:
            answer = self.llm.answer(
                query,
                [item.model_dump() for item in evidence],
                language=language,
            )
            steps.append(
                AgentStep(
                    name="answer",
                    status="completed",
                    detail="Generated an evidence-grounded response.",
                )
            )

        return {
            "plan": plan,
            "steps": [step.__dict__ for step in steps],
            "evidence": evidence,
            "recommendations": recommendations,
            "answer": answer,
        }
