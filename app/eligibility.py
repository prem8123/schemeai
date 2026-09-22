from __future__ import annotations

from typing import Any

from .models import EligibilityResult, Scheme, StudentProfile

SUPPORTED_STATUSES = ("LIKELY_ELIGIBLE", "POSSIBLY_ELIGIBLE", "UNKNOWN", "NOT_ELIGIBLE")


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "==":
        return actual == expected
    if operator == "!=":
        return actual != expected
    if operator == "<":
        return actual < expected
    if operator == "<=":
        return actual <= expected
    if operator == ">":
        return actual > expected
    if operator == ">=":
        return actual >= expected
    if operator == "in":
        return actual in expected
    raise ValueError(f"Unsupported eligibility operator: {operator}")


def evaluate(profile: StudentProfile, scheme: Scheme) -> EligibilityResult:
    """Evaluate only machine-checkable rules.

    Missing inputs are never treated as passes. A critical failed rule means
    NOT_ELIGIBLE; missing inputs or manual review requirements mean UNKNOWN.
    The score is an evidence-completeness indicator, not a probability.
    """
    reasons: list[str] = []
    missing: list[str] = []
    critical_fail = False
    advisory_fail = False
    passed = 0
    checks = len(scheme.eligibility_rules)

    if not scheme.eligibility_rules:
        return EligibilityResult(
            scheme=scheme,
            status="UNKNOWN",
            score=0.0,
            reasons=["No machine-checkable eligibility rules are loaded for this scheme."],
            missing_information=[],
        )

    for rule in scheme.eligibility_rules:
        actual = getattr(profile, rule.field, None)
        if actual is None:
            missing.append(rule.field)
            reasons.append(
                f"Missing {rule.field}; this condition cannot be evaluated from the supplied profile "
                f"(source: {rule.provenance.reference})."
            )
            continue
        try:
            ok = _compare(actual, rule.operator, rule.value)
        except (TypeError, ValueError):
            reasons.append(
                f"Could not safely evaluate {rule.field}; human review is required "
                f"(source: {rule.provenance.reference})."
            )
            missing.append(rule.field)
            continue

        if ok:
            passed += 1
            reasons.append(f"{rule.field} satisfies the documented rule.")
        elif rule.critical:
            critical_fail = True
            reasons.append(f"{rule.field} does not satisfy a required documented rule.")
        else:
            advisory_fail = True
            reasons.append(f"{rule.field} does not satisfy an advisory documented rule.")

    score = round(passed / checks, 2) if checks else 0.0

    if critical_fail:
        status = "NOT_ELIGIBLE"
    elif missing or scheme.manual_review_required:
        status = "UNKNOWN"
        if scheme.manual_review_required and scheme.manual_review_reason:
            reasons.append(scheme.manual_review_reason)
    elif advisory_fail:
        status = "POSSIBLY_ELIGIBLE"
    else:
        status = "LIKELY_ELIGIBLE"

    return EligibilityResult(
        scheme=scheme,
        status=status,
        score=score,
        reasons=reasons,
        missing_information=sorted(set(missing)),
    )


def rank(profile: StudentProfile, schemes: list[Scheme]) -> list[EligibilityResult]:
    results = [evaluate(profile, s) for s in schemes]
    order = {"LIKELY_ELIGIBLE": 0, "POSSIBLY_ELIGIBLE": 1, "UNKNOWN": 2, "NOT_ELIGIBLE": 3}
    return sorted(results, key=lambda r: (order[r.status], -r.score, r.scheme.name))
