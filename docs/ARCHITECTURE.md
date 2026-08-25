# SchemeAI Architecture

## Current MVP

Student profile -> eligibility engine + retrieval -> evidence-backed ranked schemes -> UI.

## Production target

1. Input layer: web/mobile/voice and multilingual text.
2. Profile extraction: structured Pydantic schema.
3. Planner: decide retrieval, rules and optional calculations.
4. Retrieval: hybrid lexical + embedding search with reranking.
5. Eligibility engine: deterministic rules first; LLM only for interpretation of ambiguous text.
6. Verification: every material claim must link to an authoritative source and page/section.
7. Recommendation: rank by eligibility confidence, benefit, deadline and user constraints.
8. Response: explain why a scheme matched and what information is missing.
9. Evaluation: retrieval recall, groundedness, citation precision, eligibility accuracy and user task completion time.

## Safety

SchemeAI is an information assistant, not an authority. Current official sources must be checked before an application. If required evidence is missing or contradictory, return UNKNOWN instead of guessing.
