from datetime import datetime, timezone
import pytest
from gauntlet.perturb import ALL_PERTURBATIONS, Timeout, Http500, RateLimit429
from gauntlet.trace import ToolCall, Trace
def test_perturbations_transform_or_raise(monkeypatch):
    monkeypatch.setenv("GAUNTLET_LATENCY_SCALE","0")
    call=ToolCall(id="t0",name="read_inbox",args={},response=[{"subject":"hello","body":"body"}])
    trace=Trace(run_id="x",agent_name="x",mode="record",user_input="",started_at=datetime.now(timezone.utc))
    for cls in ALL_PERTURBATIONS:
        if cls in (Timeout, Http500, RateLimit429):
            with pytest.raises(Exception): cls().apply(call,trace)
        else: cls().apply(call,trace)
