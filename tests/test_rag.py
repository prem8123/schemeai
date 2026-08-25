import app.rag as rag


def test_retrieval_returns_full_provenance(monkeypatch):
    monkeypatch.setattr(rag, "RETRIEVAL_MODE", "lexical")
    evidence = rag.retrieve("family income scholarship", top_k=3)
    assert evidence
    for item in evidence:
        assert item.provenance.authority
        assert item.provenance.official_url
        assert item.provenance.last_verified
        assert item.provenance.document_title
        assert item.provenance.reference
        assert item.freshness is not None
