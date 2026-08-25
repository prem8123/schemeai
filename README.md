# SchemeAI 🎓

**Multilingual AI-Based Scholarship and Education Scheme Eligibility Assistant using RAG**

SchemeAI helps students discover education scholarships and support schemes from a structured profile, retrieves supporting knowledge, evaluates deterministic eligibility rules, and returns evidence-backed recommendations.

## What is implemented

- FastAPI REST API
- Streamlit student UI
- Structured student profiles with Pydantic
- Deterministic eligibility engine with `LIKELY_ELIGIBLE`, `POSSIBLY_ELIGIBLE`, `UNKNOWN`, and `NOT_ELIGIBLE`
- RAG-style evidence retrieval with provenance metadata
- Agent orchestration foundation
- English/Kannada/Hindi status labels
- Knowledge ingestion helper
- Tests and GitHub Actions CI
- Docker + Docker Compose
- Safety disclaimer and official-source provenance design

## Architecture

```text
Student
  ↓
Profile / Natural-language query
  ↓
Planner / Orchestrator
  ├── Retrieval (RAG)
  ├── Eligibility rules
  └── Optional LLM generation
  ↓
Evidence verification
  ↓
Ranked recommendations
  ↓
Explanation + source/page
```

## Important data policy

The repository contains **demo scholarship records only**. They are intentionally labeled as demo data and must not be presented as real eligibility rules. For deployment, ingest current official scheme documents and retain authority, URL, update date, document title, page and section metadata.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open `http://127.0.0.1:8501` for the UI or `http://127.0.0.1:8000/docs` for the API.

## Tests

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

## API examples

`POST /recommend` accepts a JSON student profile and returns ranked schemes.

`GET /search?q=income scholarship` returns retrieved evidence chunks.

`POST /ask` accepts a natural-language question and profile and returns an evidence-grounded response. Without an LLM key it uses a deterministic fallback, so the demo remains runnable offline.

## Production roadmap

1. Replace demo records with verified official scheme sources.
2. Add PDF/HTML parsing and chunk-level provenance.
3. Add dense embeddings + hybrid retrieval + reranking.
4. Connect a production LLM through a configurable provider adapter.
5. Add multilingual generation and Kannada/Hindi query normalization.
6. Add deadline tracking and source freshness checks.
7. Add evaluation sets for retrieval, groundedness, citation precision and eligibility accuracy.
8. Conduct student/stakeholder validation.
