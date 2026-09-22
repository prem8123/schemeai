from datetime import date
from app.eligibility import evaluate
from app.models import Scheme, StudentProfile
from app.schema import EligibilityRule, Provenance

def p():
    return Provenance(authority="Test Authority",official_url="https://example.gov/test",last_verified=date.today(),document_title="Test document",reference="Section 1",source_type="html")
def s(manual=False):
    x=p()
    return Scheme(id="test",name="Test Scheme",authority="Test Authority",description="Test",benefit="Test benefit",source="https://example.gov/test",source_text="Test",provenance=[x],eligibility_rules=[
        EligibilityRule(clause_id="income",field="annual_family_income",operator="<=",value=450000,provenance=x,critical=True),
        EligibilityRule(clause_id="regular",field="regular_course",operator="==",value=True,provenance=x,critical=True)],manual_review_required=manual,manual_review_reason="Manual verification required" if manual else None)
def profile(**kwargs):
    base={"age":20,"state":"Karnataka","education_level":"UG"}; base.update(kwargs); return StudentProfile(**base)
def test_missing_input_is_unknown_not_pass():
    r=evaluate(profile(annual_family_income=200000),s()); assert r.status=="UNKNOWN"; assert "regular_course" in r.missing_information
def test_critical_failure_is_not_eligible():
    assert evaluate(profile(annual_family_income=900000,regular_course=True),s()).status=="NOT_ELIGIBLE"
def test_all_known_rules_pass_is_likely_eligible():
    assert evaluate(profile(annual_family_income=200000,regular_course=True),s()).status=="LIKELY_ELIGIBLE"
def test_manual_review_blocks_likely_eligible():
    assert evaluate(profile(annual_family_income=200000,regular_course=True),s(manual=True)).status=="UNKNOWN"
