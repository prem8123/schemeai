from app.data import SCHEMES
from app.eligibility import evaluate
from app.models import StudentProfile


def test_income_and_education_match():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG", category="GENERAL", annual_family_income=200000)
    result = evaluate(p, SCHEMES[0])
    assert result.status == "LIKELY_ELIGIBLE"


def test_income_failure():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG", category="GENERAL", annual_family_income=900000)
    result = evaluate(p, SCHEMES[0])
    assert result.status == "NOT_ELIGIBLE"


def test_missing_income_is_unknown():
    p = StudentProfile(age=20, state="Karnataka", education_level="UG", category="GENERAL")
    result = evaluate(p, SCHEMES[0])
    assert result.status == "UNKNOWN"
