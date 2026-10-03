"""Command-line entry points for recording and running Gauntlet."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import typer
from rich import print
from .sdk import Harness
from .store import save_trace
from .store import load_suite
from .runner import run_suite
app=typer.Typer()
@app.callback()
def main():
    """Record, replay, and score agent reliability suites."""
def load_agent(path: str):
    p=Path(path).resolve(); name=f"gauntlet_dynamic_{p.stem}"
    spec=importlib.util.spec_from_file_location(name,p,submodule_search_locations=[str(p.parent)])
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
    sys.modules[name] = mod; spec.loader.exec_module(mod); return mod
@app.command()
def record(agent_path: str, input: str="Summarize my unread emails and flag anything urgent."):
    agent=load_agent(agent_path); h=Harness(mode="record",agent_name=Path(agent_path).stem); output=agent.run(input,h); path=save_trace(h.trace); print(f"Recorded {len(h.trace.tool_calls)} tools and {len(h.trace.llm_calls)} LLM calls: [green]{path}[/green]")
@app.command()
def run(agent_path: str, input: str="Summarize my unread emails and flag anything urgent.", trials: int=3, only: str|None=None, max_cases: int|None=None, fail_under: float=0):
    suite=run_suite(agent_path,input,trials,max_cases=max_cases,only=only)
    for r in suite.results: print(f"{r.perturbation:20} {r.target_tool_name:14} {r.failure_rate:.0%} {r.worst_severity}")
    print(f"[bold]Robustness score: {suite.score}[/bold]")
    if suite.score < fail_under: raise typer.Exit(1)
@app.command()
def demo():
    import os; os.environ["GAUNTLET_MOCK_LLM"]="1"; user_input="Summarize my unread emails and flag anything urgent."
    vulnerable=run_suite("examples/inbox_pilot/agent.py",user_input,trials=3,only="injection")
    fixed=run_suite("examples/inbox_pilot/agent_fixed.py",user_input,trials=3,only="injection")
    print(f"InboxPilot vulnerable: [red]{vulnerable.score}[/red] | fixed: [green]{fixed.score}[/green]")
@app.command()
def report(suite_id: str, format: str="md"):
    suite=load_suite(suite_id)
    if format == "json": print(suite.model_dump_json(indent=2)); return
    print(f"# Gauntlet report: {suite.agent_name}\n\nRobustness score: **{suite.score}**\n")
    for r in suite.results: print(f"- {r.perturbation} on `{r.target_tool_name}`: {r.worst_severity} ({r.failure_rate:.0%})")
@app.command()
def serve(port: int=8787):
    import uvicorn
    uvicorn.run("gauntlet.server:app",host="127.0.0.1",port=port)
if __name__ == "__main__": app()
