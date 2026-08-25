from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import Scheme
from .schema import EligibilityRule, EligibilityClause, FreshnessStatus, Provenance

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_PATH = ROOT / "data" / "official" / "schemes.jsonl"
DEMO_PATH = ROOT / "data" / "demo" / "schemes.jsonl"


def _freshness(last_verified: str, stale_after_days: int) -> FreshnessStatus:
    verified = date.fromisoformat(last_verified)
    age = (date.today() - verified).days
    return FreshnessStatus(
        last_verified=verified,
        stale=age > stale_after_days,
        stale_after_days=stale_after_days,
        age_days=age,
    )


def _load(path: Path) -> list[Scheme]:
    if not path.exists():
        return []
    records: list[Scheme] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        clauses = [EligibilityClause.model_validate(c) for c in raw.get("clauses", [])]
        rules = [
            EligibilityRule(
                clause_id=c.id,
                field=c.field,
                operator=c.operator,
                value=c.value,
                provenance=c.provenance,
            )
            for c in clauses
            if c.machine_checkable and c.field and c.operator
        ]
        provenance = list({
            p.model_dump_json(): p
            for c in clauses
            for p in [c.provenance]
        }.values())
        records.append(
            Scheme(
                id=raw["id"],
                name=raw["name"],
                authority=raw["authority"],
                description=raw["description"],
                scheme_type=raw.get("scheme_type", "scholarship"),
                benefit=raw["benefit"],
                application_url=raw.get("application_url"),
                official_url=raw["official_url"],
                last_verified=raw["last_verified"],
                source=raw["official_url"],
                source_page=clauses[0].provenance.reference if clauses else None,
                source_text=" ".join(c.text for c in clauses),
                provenance=provenance,
                eligibility_rules=rules,
                freshness=_freshness(raw["last_verified"], int(raw.get("freshness_days", 90))),
                manual_review_required=bool(raw.get("manual_review_required", False)),
                manual_review_reason=raw.get("manual_review_reason"),
            )
        )
    return records


SCHEMES = _load(OFFICIAL_PATH)
DEMO_SCHEMES = _load(DEMO_PATH)
