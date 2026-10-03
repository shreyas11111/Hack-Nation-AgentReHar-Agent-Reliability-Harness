def test_vulnerable_and_fixed(monkeypatch):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1")
    from gauntlet.runner import run_suite
    bad=run_suite("examples/inbox_pilot/agent.py","summarize",trials=1,only="injection")
    good=run_suite("examples/inbox_pilot/agent_fixed.py","summarize",trials=1,only="injection")
    assert bad.score <= 50 and good.score >= 80
