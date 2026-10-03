"""Small JSON and SQLite persistence layer."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from .trace import Trace, SuiteResult
ROOT=Path(".gauntlet")
def save_trace(trace: Trace):
    (ROOT/"traces").mkdir(parents=True,exist_ok=True); path=ROOT/"traces"/f"{trace.run_id}.json"; path.write_text(trace.model_dump_json(indent=2)); return path
def save_suite(suite: SuiteResult):
    ROOT.mkdir(exist_ok=True); (ROOT/"suites").mkdir(exist_ok=True); (ROOT/"suites"/f"{suite.suite_id}.json").write_text(suite.model_dump_json(indent=2))
    con=sqlite3.connect(ROOT/"gauntlet.db"); con.execute("create table if not exists suites (id text primary key, agent text, score real, created_at text)"); con.execute("insert or replace into suites values (?,?,?,?)",(suite.suite_id,suite.agent_name,suite.score,suite.created_at.isoformat())); con.commit(); con.close()
def load_suite(suite_id: str): return SuiteResult.model_validate_json((ROOT/"suites"/f"{suite_id}.json").read_text())
