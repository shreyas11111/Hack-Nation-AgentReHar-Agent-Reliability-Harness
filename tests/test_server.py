from fastapi.testclient import TestClient
from gauntlet.server import app
def test_suite_api(monkeypatch):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1")
    from gauntlet.runner import run_suite
    suite=run_suite("examples/inbox_pilot/agent.py","summarize",trials=1,max_cases=1)
    client=TestClient(app)
    assert client.get("/api/suites").status_code == 200
    assert client.get(f"/api/suites/{suite.suite_id}").status_code == 200
    assert client.get("/").status_code == 200
