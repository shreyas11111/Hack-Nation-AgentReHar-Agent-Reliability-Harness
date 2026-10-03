"""Public harness API for safely recording and replaying agent tool/LLM calls."""
from __future__ import annotations
import functools, os, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from .trace import Trace, ToolCall, LLMCall
from .mock_llm import MockLLM

class Harness:
    def __init__(self, mode="off", baseline: Trace | None=None, perturbation=None, target_id: str | None=None, agent_name="agent"):
        self.mode, self.baseline, self.perturbation, self.target_id = mode, baseline, perturbation, target_id
        self.trace = Trace(run_id=uuid.uuid4().hex, agent_name=agent_name, mode="replay" if mode == "replay" else "record", user_input="", started_at=datetime.now(timezone.utc))
        self._consumed: set[str] = set()
    @classmethod
    def from_env(cls, **kwargs): return cls(mode=os.getenv("GAUNTLET_MODE", "off"), **kwargs)
    def begin(self, user_input: str): self.trace.user_input = user_input; self._started = time.perf_counter()
    def finish(self, output: str | None):
        self.trace.final_output = output; self.trace.wall_ms = int((time.perf_counter()-self._started)*1000)
        self.trace.total_tokens = sum(x.prompt_tokens+x.completion_tokens for x in self.trace.llm_calls); return self.trace
    def plant_canary(self):
        token = "GAUNTLET-CANARY-" + uuid.uuid4().hex[:8]; self.trace.canaries.append(token); return token
    def tool(self, fn: Callable):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs): return self._invoke_tool(fn, args, kwargs)
        return wrapped
    def _invoke_tool(self, fn, args, kwargs):
        started=time.perf_counter(); name=fn.__name__; call_args=dict(kwargs)
        if args: call_args.update({f"arg{i}": v for i,v in enumerate(args)})
        matched=None
        if self.mode == "replay" and self.baseline:
            candidates=[x for x in self.baseline.tool_calls if x.name==name and x.id not in self._consumed]
            matched=next((x for x in candidates if x.args==call_args), candidates[0] if candidates else None)
            if matched: self._consumed.add(matched.id)
        try:
            if self.mode == "replay":
                if matched is None: response={"status":"ok", "id":"fake-"+uuid.uuid4().hex[:8]}; base=False; changed=False
                else:
                    response=matched.response; base=True; changed=matched.id==self.target_id and self.perturbation is not None
                    if changed: response=self.perturbation.apply(matched, self.baseline)
            else: response=fn(*args, **kwargs); base=True; changed=False
            self.trace.tool_calls.append(ToolCall(id=f"t{len(self.trace.tool_calls)}", name=name, args=call_args, response=response, latency_ms=int((time.perf_counter()-started)*1000), in_baseline=base, perturbed=changed))
            return response
        except Exception as exc:
            self.trace.tool_calls.append(ToolCall(id=f"t{len(self.trace.tool_calls)}", name=name, args=call_args, response=None, error=str(exc), latency_ms=int((time.perf_counter()-started)*1000), in_baseline=matched is not None, perturbed=matched is not None and matched.id==self.target_id))
            raise
    def llm_client(self): return MockLLM() if os.getenv("GAUNTLET_MOCK_LLM") == "1" else __import__("openai").OpenAI()
    def wrap_llm(self, client): return _WrappedClient(client, self)

class _WrappedCompletions:
    def __init__(self, inner, harness): self.inner,self.harness=inner,harness
    def create(self, *args, **kwargs):
        started=time.perf_counter(); result=self.inner.create(*args, **kwargs); message=result.choices[0].message
        calls=[{"name": x.function.name, "args": __import__("json").loads(x.function.arguments)} for x in (getattr(message,"tool_calls",None) or [])]
        usage=getattr(result,"usage",None)
        self.harness.trace.llm_calls.append(LLMCall(id=f"l{len(self.harness.trace.llm_calls)}", model=getattr(result,"model",kwargs.get("model","unknown")), messages=kwargs.get("messages",[]), response_text=getattr(message,"content",None), tool_calls_requested=calls, prompt_tokens=getattr(usage,"prompt_tokens",0) or 0, completion_tokens=getattr(usage,"completion_tokens",0) or 0, latency_ms=int((time.perf_counter()-started)*1000)))
        return result
class _WrappedClient:
    def __init__(self, client,harness): self.chat=type("Chat",(),{"completions":_WrappedCompletions(client.chat.completions,harness)})()
