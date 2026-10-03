import os
from gauntlet.runner import run_suite
def test_injection_hijack_is_critical(monkeypatch):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1")
    suite=run_suite("examples/inbox_pilot/agent.py","summarize",trials=3,only="injection")
    hijack=next(x for x in suite.results if x.perturbation=="InjectionHijack")
    assert hijack.worst_severity == "CRITICAL" and hijack.failure_rate == 1
def test_exfil_leaks_canary(monkeypatch):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1")
    suite=run_suite("examples/inbox_pilot/agent.py","summarize",trials=1,only="injection")
    exfil=next(x for x in suite.results if x.perturbation=="InjectionExfil")
    assert any(f.oracle=="CanaryLeak" for f in exfil.trials[0].findings)
