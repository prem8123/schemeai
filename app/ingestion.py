from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .schema import EligibilityClause, IngestionIssue, IngestionResult, Provenance, SchemeRecord


@dataclass
class ExtractedChunk:
    text: str
    reference: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _chunks(text: str, size: int = 180, overlap: int = 30) -> list[str]:
    words = _clean(text).split()
    out: list[str] = []
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + size])
        if chunk:
            out.append(chunk)
    return out


def fetch_source(source: str, timeout: int = 30) -> tuple[str, list[ExtractedChunk]]:
    if source.startswith("http://") or source.startswith("https://"):
        response = requests.get(source, timeout=timeout, headers={"User-Agent": "SchemeAI/1.0"})
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" in content_type or source.lower().endswith(".pdf"):
            tmp = Path("/tmp/schemeai-source.pdf")
            tmp.write_bytes(response.content)
            return extract_pdf(tmp)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = _clean(soup.get_text(" "))
        return text, [ExtractedChunk(c, f"HTML chunk {i + 1}") for i, c in enumerate(_chunks(text))]

    path = Path(source)
    if path.suffix.lower() == ".pdf":
        return extract_pdf(path)
    text = _clean(path.read_text(encoding="utf-8"))
    return text, [ExtractedChunk(c, f"Text chunk {i + 1}") for i, c in enumerate(_chunks(text))]


def extract_pdf(path: Path) -> tuple[str, list[ExtractedChunk]]:
    reader = PdfReader(str(path))
    all_text: list[str] = []
    chunks: list[ExtractedChunk] = []
    for number, page in enumerate(reader.pages, start=1):
        text = _clean(page.extract_text() or "")
        if not text:
            continue
        all_text.append(text)
        for i, chunk in enumerate(_chunks(text)):
            chunks.append(ExtractedChunk(chunk, f"PDF page {number}, chunk {i + 1}"))
    return "\n".join(all_text), chunks


def validate_record(record: SchemeRecord) -> list[IngestionIssue]:
    issues: list[IngestionIssue] = []
    if not record.authority.strip():
        issues.append(IngestionIssue(level="error", message="Missing issuing authority", source=record.id))
    if not str(record.official_url).strip():
        issues.append(IngestionIssue(level="error", message="Missing official source URL", source=record.id))
    if not record.last_verified:
        issues.append(IngestionIssue(level="error", message="Missing last-verified date", source=record.id))
    for clause in record.clauses:
        if not clause.provenance.authority or not clause.provenance.official_url or not clause.provenance.last_verified:
            issues.append(IngestionIssue(level="error", message=f"Clause {clause.id} is missing provenance", source=record.id))
    return issues


def ingest_document(
    source: str,
    authority: str,
    official_url: str,
    document_title: str,
    last_verified: date,
    scheme_id: str,
    scheme_name: str,
    scheme_type: str = "scholarship",
) -> tuple[SchemeRecord, IngestionResult]:
    _, chunks = fetch_source(source)
    content_hash = hashlib.sha256("\n".join(c.text for c in chunks).encode("utf-8")).hexdigest()
    provenance_base = {
        "authority": authority,
        "official_url": official_url,
        "last_verified": last_verified,
        "document_title": document_title,
        "source_type": "pdf" if source.lower().endswith(".pdf") else "html",
        "fetched_at": datetime.now(timezone.utc),
        "content_hash": content_hash,
    }
    clauses = [
        EligibilityClause(
            id=f"{scheme_id}-chunk-{i + 1}",
            text=chunk.text,
            provenance=Provenance(reference=chunk.reference, **provenance_base),
        )
        for i, chunk in enumerate(chunks)
    ]
    record = SchemeRecord(
        id=scheme_id,
        name=scheme_name,
        scheme_type=scheme_type,  # type: ignore[arg-type]
        authority=authority,
        official_url=official_url,
        last_verified=last_verified,
        document_title=document_title,
        description=f"Officially sourced record ingested from {urlparse(official_url).netloc}.",
        benefit="See the official scheme document for current benefits.",
        clauses=clauses,
    )
    issues = validate_record(record)
    errors = [i for i in issues if i.level == "error"]
    result = IngestionResult(accepted=0 if errors else len(clauses), rejected=len(errors), issues=issues)
    return record, result
