from datetime import datetime, timezone
from gauntlet.trace import Trace
def test_trace_roundtrip():
    trace=Trace(run_id="x",agent_name="a",mode="record",user_input="hi",started_at=datetime.now(timezone.utc))
    assert Trace.model_validate_json(trace.model_dump_json()).run_id == "x"
