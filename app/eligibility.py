from __future__ import annotations

from typing import Any

from .models import EligibilityResult, Scheme, StudentProfile


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
    reasons: list[str] = []
    missing: list[str] = []
    checks = len(scheme.eligibility_rules)
    passed = 0

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
            reasons.append(f"Need {rule.field} to evaluate: {rule.provenance.reference}.")
            continue
        try:
            ok = _compare(actual, rule.operator, rule.value)
        except (TypeError, ValueError):
            ok = False
            reasons.append(f"Could not safely evaluate {rule.field}; human review is required.")
        if ok:
            passed += 1
            reasons.append(f"{rule.field} satisfies the documented rule.")
        else:
            reasons.append(f"{rule.field} does not satisfy the documented rule.")

    score = round(passed / checks, 2) if checks else 0.0
    if any("does not satisfy" in r for r in reasons):
        status = "NOT_ELIGIBLE"
    elif missing or scheme.manual_review_required:
        status = "UNKNOWN"
        if scheme.manual_review_required and scheme.manual_review_reason:
            reasons.append(scheme.manual_review_reason)
    elif score == 1:
        status = "LIKELY_ELIGIBLE"
    else:
        status = "POSSIBLY_ELIGIBLE"

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
