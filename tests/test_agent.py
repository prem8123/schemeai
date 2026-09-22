from app.agent import Route, plan
def test_agent_routes_eligibility():
    assert plan("Am I eligible for this scholarship?").route == Route.ELIGIBILITY
def test_agent_routes_evidence():
    assert plan("What documents are required?").route == Route.RETRIEVAL
def test_agent_routes_both():
    assert plan("Am I eligible and what documents should I submit?").route == Route.BOTH
