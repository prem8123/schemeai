from app.data import DEMO_SCHEMES
from app.eligibility import evaluate
from app.models import StudentProfile


def test_demo_income_match():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG", annual_family_income=200000)
    result = evaluate(p, DEMO_SCHEMES[0])
    assert result.status == "LIKELY_ELIGIBLE"


def test_demo_income_failure():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG", annual_family_income=900000)
    result = evaluate(p, DEMO_SCHEMES[0])
    assert result.status == "NOT_ELIGIBLE"


def test_demo_missing_income_is_unknown():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG")
    result = evaluate(p, DEMO_SCHEMES[0])
    assert result.status == "UNKNOWN"


def test_official_scheme_is_conservative():
    from app.data import SCHEMES

    p = StudentProfile(
        age=20,
        state="Karnataka",
        education_level="UG",
        annual_family_income=200000,
        class12_percentile=90,
        regular_course=True,
        is_diploma=False,
        gap_after_class12=False,
        receives_other_scholarship=False,
    )
    result = evaluate(p, SCHEMES[0])
    assert result.status == "UNKNOWN"
    assert result.scheme.manual_review_required is True
