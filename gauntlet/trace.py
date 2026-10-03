"""Pydantic data contracts for recorded agent runs and reliability suites."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

class LLMCall(BaseModel):
    id: str; model: str; messages: list[dict]; response_text: str | None
    tool_calls_requested: list[dict] = Field(default_factory=list)
    prompt_tokens: int = 0; completion_tokens: int = 0; latency_ms: int = 0

class ToolCall(BaseModel):
    id: str; name: str; args: dict; response: Any
    error: str | None = None; latency_ms: int = 0; in_baseline: bool = True; perturbed: bool = False

class Trace(BaseModel):
    run_id: str; agent_name: str; mode: Literal["record", "replay"]; user_input: str
    tool_calls: list[ToolCall] = Field(default_factory=list); llm_calls: list[LLMCall] = Field(default_factory=list)
    final_output: str | None = None; error: str | None = None; total_tokens: int = 0; wall_ms: int = 0
    canaries: list[str] = Field(default_factory=list); started_at: datetime

class Finding(BaseModel):
    oracle: str; severity: Literal["CRITICAL", "HIGH", "SILENT_FAILURE", "RESOURCE", "GRACEFUL", "PASS"]
    message: str; evidence_tool_call_id: str | None = None

class TrialResult(BaseModel):
    trial: int; trace: Trace; findings: list[Finding]
    outcome: Literal["success", "graceful_failure", "silent_failure", "crash"]

class PerturbationResult(BaseModel):
    perturbation: str; category: str; target_tool_call_id: str; target_tool_name: str
    trials: list[TrialResult]; failure_rate: float; worst_severity: str

class SuiteResult(BaseModel):
    suite_id: str; agent_name: str; baseline: Trace; results: list[PerturbationResult]
    score: float; created_at: datetime
