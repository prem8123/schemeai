from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from .eligibility import rank
from .rag import retrieve

class Route(StrEnum):
    ELIGIBILITY="eligibility"
    RETRIEVAL="retrieval"
    BOTH="eligibility+retrieval"

@dataclass(frozen=True)
class AgentPlan:
    route: Route
    reason: str

def plan(question):
    q=(question or "").lower()
    eligibility_terms=("eligible","eligibility","qualify","qualification","can i get","am i","ಅರ್ಹ","पात्र","योग्य")
    evidence_terms=("what is","how much","documents","deadline","apply","application","benefit","rule","why","proof","source","ಅರ್ಜಿ","ದಾಖಲೆ","ಲಾಭ","आवेदन","दस्तावेज़","लाभ")
    e=any(x in q for x in eligibility_terms); r=any(x in q for x in evidence_terms)
    if e and r: return AgentPlan(Route.BOTH,"Question needs eligibility reasoning and supporting evidence.")
    if e: return AgentPlan(Route.ELIGIBILITY,"Question is primarily an eligibility question.")
    return AgentPlan(Route.RETRIEVAL,"Question is primarily an evidence retrieval question.")

def run(question,profile,schemes,top_k=5):
    selected=plan(question); results=[]; evidence=[]
    if selected.route in (Route.ELIGIBILITY,Route.BOTH): results=rank(profile,schemes)[:10]
    if selected.route in (Route.RETRIEVAL,Route.BOTH) and question: evidence=retrieve(question,top_k)
    return {"route":selected.route.value,"route_reason":selected.reason,"recommendations":results,"evidence":evidence}
