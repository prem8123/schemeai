from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Provenance(BaseModel):
    authority: str = Field(min_length=2)
    official_url: HttpUrl
    last_verified: date
    document_title: str = Field(min_length=2)
    reference: str = Field(min_length=1, description="Page, section, question, clause, or heading reference")
    source_type: Literal["pdf", "html", "portal", "notice"]
    fetched_at: datetime | None = None
    content_hash: str | None = None


class EligibilityClause(BaseModel):
    id: str = Field(min_length=2)
    text: str = Field(min_length=5)
    provenance: Provenance
    machine_checkable: bool = False
    field: str | None = None
    operator: str | None = None
    value: Any | None = None
    critical: bool = True


class EligibilityRule(BaseModel):
    clause_id: str
    field: str
    operator: Literal["==", "!=", "<", "<=", ">", ">=", "in"]
    value: Any
    provenance: Provenance
    critical: bool = True


class SchemeRecord(BaseModel):
    id: str = Field(min_length=2)
    name: str = Field(min_length=2)
    scheme_type: Literal["scholarship", "education_support"]
    authority: str = Field(min_length=2)
    official_url: HttpUrl
    last_verified: date
    document_title: str = Field(min_length=2)
    description: str = Field(min_length=5)
    benefit: str = Field(min_length=2)
    application_url: HttpUrl | None = None
    clauses: list[EligibilityClause] = Field(min_length=1)
    freshness_days: int = Field(default=90, ge=1)
    manually_reviewed: bool = False
    manual_review_reason: str | None = None

    @field_validator("clauses")
    @classmethod
    def clauses_must_have_provenance(cls, value: list[EligibilityClause]) -> list[EligibilityClause]:
        if not value:
            raise ValueError("At least one provenance-tagged eligibility clause is required")
        return value


class FreshnessStatus(BaseModel):
    last_verified: date
    stale: bool
    stale_after_days: int
    age_days: int


class Evidence(BaseModel):
    scheme_id: str
    scheme_name: str
    text: str
    score: float
    retrieval_mode: str
    provenance: Provenance
    freshness: FreshnessStatus


class IngestionIssue(BaseModel):
    level: Literal["error", "warning"]
    message: str
    source: str


class IngestionResult(BaseModel):
    accepted: int
    rejected: int
    issues: list[IngestionIssue] = []
