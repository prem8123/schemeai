# SchemeAI 🎓

**Multilingual AI-Based Scholarship and Education Scheme Eligibility Assistant using RAG**

> ## ⚠️ Eligibility safety notice
> SchemeAI is an **informational matching and evidence-retrieval system**, not an official government eligibility authority. Never treat an `LIKELY_ELIGIBLE` result as a final award decision. Always verify the current scheme specification, deadline, documents, institution status, and application rules on the linked official source before applying.
>
> The repository now separates **verified official-source records** from synthetic demo fixtures. Official records are intentionally conservative and some are marked `manual_review_required` when current conditions cannot be fully machine-verified.

## What is implemented

- FastAPI REST API with strict Pydantic request/response models
- Streamlit student UI and deployable web frontend
- Deterministic eligibility engine with `LIKELY_ELIGIBLE`, `POSSIBLY_ELIGIBLE`, `UNKNOWN`, and `NOT_ELIGIBLE`
- Provenance-first scheme records: authority, official URL, verification date, document title, and page/section/question reference
- Official-source PDF/HTML ingestion with validation and content hashing
- Multilingual dense embeddings + cross-encoder reranking
- Freshness/staleness tracking surfaced by API
- Evidence responses containing full provenance metadata
- English/Kannada/Hindi language detection and grounded answer generation
- Rate limiting, input sanitization, optional API-key protection, JSON logs, and secret-safety CI checks
- 40-case labeled evaluation set plus multilingual retrieval evaluation
- Pre-commit, Ruff, Black, mypy, pytest, GitHub Actions, Docker and Render/Netlify configuration

## Architecture

```text
Student question/profile
        ↓
Language detection
        ↓
Planner / deterministic eligibility engine
        ├── Dense multilingual embeddings
        ├── Cross-encoder reranker
        ├── Provenance-aware evidence
        └── Freshness checks
        ↓
Eligibility + evidence verification
        ↓
Optional LLM answer generation
        ↓
Localized evidence-backed response
```

## Data policy

`data/official/` contains records derived from official government/portal sources and every eligibility clause carries provenance. `data/demo/` contains synthetic fixtures for tests only and must never be presented as real scholarship rules.

Current official records include PM-USP CSSS and PM-Vidyalaxmi. The PM-USP record uses the Ministry of Education's official 2025-26 FAQ and separately acknowledges that the live 2026-27 portal status must be rechecked. PM-Vidyalaxmi records use current official portal/Ministry sources and still require current QHEI verification.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

The production RAG mode downloads the configured multilingual embedding/reranker models on first use. For offline tests:

```bash
set SCHEMEAI_RETRIEVAL_MODE=lexical   # Windows
export SCHEMEAI_RETRIEVAL_MODE=lexical # macOS/Linux
pytest -q
```

## Official ingestion

```bash
python scripts/ingest_official.py <OFFICIAL_SOURCE_URL_OR_FILE> \
  --authority "Department / Ministry" \
  --official-url "https://official.example" \
  --document-title "Official scheme document" \
  --last-verified 2026-08-25 \
  --scheme-id example-scheme \
  --scheme-name "Example Scheme"
```

Missing authority, official URL, or verification date is rejected rather than silently accepted.

## Evaluation

```bash
python scripts/evaluate.py --retrieval-mode lexical
python scripts/evaluate_multilingual.py
```

The evaluation suite reports precision/recall per eligibility tier, retrieval/citation-provenance metrics, and false positives. The citation metric is currently a retrieval-level provenance proxy; claim-level citation precision will be added when the LLM response evaluator is enabled.

## Security and privacy

See [`PRIVACY.md`](PRIVACY.md). `.env` files are ignored, CI scans tracked files for common secret patterns, and raw student profile fields are not intentionally logged.

## Deployment

The repository includes `render.yaml` for the FastAPI backend and `netlify.toml` for the web frontend. A deployment URL is **not claimed here until a live deployment is verified**.

## Project status

The system is a production-oriented student project foundation. Before public use, replace/expand the official dataset, verify every scheme against its current authoritative specification, run dense retrieval and multilingual evaluations, complete native-speaker review of Kannada/Hindi explanations, and establish a real data-retention/deletion workflow.
