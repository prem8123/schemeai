# Official Scheme Data

This directory contains provenance-first records derived from government/official portals. Every eligibility clause must retain an issuing authority, official URL, last-verified date, document title, and page/section/question reference.

Current records:

- **PM-USP CSSS** — eligibility clauses are sourced from the Ministry of Education's official 2025-26 FAQ. The National Scholarship Portal currently lists the scheme for AY 2026-27 renewal applications, so current portal status and the older FAQ must be treated separately.
- **PM-Vidyalaxmi** — clauses are sourced from the official PM-Vidyalaxmi portal and Ministry of Education sources; QHEI membership and current conditions still require verification.
- **Post Matric Scholarship for Students with Disabilities** — eligibility fields are sourced from the current official DEPwD scholarship page; the portal's current AY 2026-27 listing is separately available on NSP.

All three records are marked for manual review where current conditions cannot be fully machine-verified. Do not place fabricated or unverifiable scheme rules here. Use `scripts/ingest_official.py` to ingest an official PDF/HTML source.
