from datetime import date

import pytest
from pydantic import ValidationError

from app.data import SCHEMES
from app.schema import EligibilityClause, Provenance


def test_official_records_have_required_provenance():
    assert SCHEMES
    for scheme in SCHEMES:
        assert scheme.authority
        assert scheme.official_url
        assert scheme.last_verified
        assert scheme.provenance
        for provenance in scheme.provenance:
            assert provenance.authority
            assert provenance.official_url
            assert provenance.last_verified
            assert provenance.document_title
            assert provenance.reference


def test_clause_rejects_missing_provenance():
    with pytest.raises(ValidationError):
        EligibilityClause(id="bad", text="Missing provenance")


def test_last_verified_is_a_real_date():
    for scheme in SCHEMES:
        assert date.fromisoformat(scheme.last_verified).year >= 2024
