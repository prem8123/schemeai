from .models import StudentProfile, Scheme, EligibilityResult


def evaluate(profile: StudentProfile, scheme: Scheme) -> EligibilityResult:
    reasons, missing = [], []
    checks, passed = 0, 0

    if scheme.state:
        checks += 1
        if profile.state.strip().lower() == scheme.state.strip().lower():
            passed += 1; reasons.append("State requirement matches.")
        else:
            reasons.append(f"State requirement is {scheme.state}.")

    if scheme.education_levels:
        checks += 1
        if profile.education_level.upper() in {x.upper() for x in scheme.education_levels}:
            passed += 1; reasons.append("Education level matches.")
        else:
            reasons.append("Education level does not match the stated requirement.")

    if scheme.min_age is not None or scheme.max_age is not None:
        checks += 1
        ok = (scheme.min_age is None or profile.age >= scheme.min_age) and (scheme.max_age is None or profile.age <= scheme.max_age)
        if ok:
            passed += 1; reasons.append("Age requirement matches.")
        else:
            reasons.append("Age is outside the stated range.")

    if scheme.max_income is not None:
        checks += 1
        if profile.annual_family_income is None:
            missing.append("annual_family_income")
        elif profile.annual_family_income <= scheme.max_income:
            passed += 1; reasons.append("Family income is within the stated limit.")
        else:
            reasons.append("Family income exceeds the stated limit.")

    if scheme.categories:
        checks += 1
        if not profile.category:
            missing.append("category")
        elif profile.category.upper() in {x.upper() for x in scheme.categories}:
            passed += 1; reasons.append("Category requirement matches.")
        else:
            reasons.append("Category is not listed in the scheme criteria.")

    if scheme.disability_required is not None:
        checks += 1
        if profile.disability == scheme.disability_required:
            passed += 1; reasons.append("Disability criterion matches.")
        else:
            reasons.append("Disability criterion does not match.")

    score = round(passed / checks, 2) if checks else 0.0
    if missing:
        status = "UNKNOWN"
    elif score == 1:
        status = "LIKELY_ELIGIBLE"
    elif score >= 0.5:
        status = "POSSIBLY_ELIGIBLE"
    else:
        status = "NOT_ELIGIBLE"

    return EligibilityResult(scheme=scheme, status=status, score=score, reasons=reasons, missing_information=missing)


def rank(profile: StudentProfile, schemes: list[Scheme]) -> list[EligibilityResult]:
    results = [evaluate(profile, s) for s in schemes]
    order = {"LIKELY_ELIGIBLE": 0, "POSSIBLY_ELIGIBLE": 1, "UNKNOWN": 2, "NOT_ELIGIBLE": 3}
    return sorted(results, key=lambda r: (order[r.status], -r.score, r.scheme.name))
