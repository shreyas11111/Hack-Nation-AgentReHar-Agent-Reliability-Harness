import os
from gauntlet.cli import load_agent
from gauntlet.sdk import Harness
def test_record_captures_calls(monkeypatch):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1")
    h=Harness(mode="record",agent_name="InboxPilot"); load_agent("examples/inbox_pilot/agent.py").run("summarize",h)
    assert h.trace.tool_calls and h.trace.llm_calls

def test_replay_prevents_new_side_effect(monkeypatch, tmp_path):
    monkeypatch.setenv("GAUNTLET_MOCK_LLM","1"); monkeypatch.chdir(tmp_path)
    agent=load_agent("/Users/shreyaskulkarni/Documents/Github Repos/Agent Reliablilty Harness/Hack-Nation-AgentReHar-Agent-Reliability-Harness/examples/inbox_pilot/agent.py")
    baseline=Harness(mode="record"); agent.run("summarize",baseline)
    replay=Harness(mode="replay",baseline=baseline.trace); agent.run("summarize",replay)
    assert [x.name for x in replay.trace.tool_calls] == [x.name for x in baseline.trace.tool_calls]
    # A direct replayed call absent from the recording returns fake success and never executes.
    invoked=[]
    @replay.tool
    def send_email(to):
        invoked.append(to); return {"status":"real"}
    assert send_email("audit@evil.test")["id"].startswith("fake-")
    assert invoked == [] and replay.trace.tool_calls[-1].in_baseline is False
