from __future__ import annotations

from datetime import date

from .data import SCHEMES


def refresh_status(last_verified: str, threshold_days: int) -> dict:
    verified = date.fromisoformat(last_verified)
    age_days = (date.today() - verified).days
    return {
        "last_verified": verified.isoformat(),
        "stale": age_days > threshold_days,
        "stale_after_days": threshold_days,
        "age_days": age_days,
    }


def stale_schemes() -> list[dict]:
    output = []
    for scheme in SCHEMES:
        if scheme.freshness and scheme.freshness.stale:
            output.append({
                "scheme_id": scheme.id,
                "scheme_name": scheme.name,
                "last_verified": scheme.freshness.last_verified.isoformat(),
                "stale_after_days": scheme.freshness.stale_after_days,
                "age_days": scheme.freshness.age_days,
            })
    return output
