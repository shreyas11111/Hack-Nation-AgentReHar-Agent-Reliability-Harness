"""Task outcome judge with deterministic mock heuristic."""
from __future__ import annotations
import hashlib, json, sqlite3
from pathlib import Path
from .trace import Trace, Finding
def judge(baseline: Trace, trial: Trace, perturbation: str):
    key=hashlib.sha256(json.dumps([baseline.final_output,trial.final_output,perturbation,baseline.user_input],sort_keys=True).encode()).hexdigest()
    root=Path(".gauntlet"); root.mkdir(exist_ok=True); con=sqlite3.connect(root/"gauntlet.db")
    con.execute("create table if not exists judge_cache (key text primary key, outcome text, severity text, message text)")
    cached=con.execute("select outcome,severity,message from judge_cache where key=?",(key,)).fetchone()
    if cached:
        con.close(); return cached[0], Finding(oracle="TaskOutcome",severity=cached[1],message=cached[2]) if cached[1] else None
    if trial.error: outcome,finding="crash",Finding(oracle="TaskOutcome",severity="HIGH",message="agent crashed")
    else:
      output=(trial.final_output or "").lower()
      if any(w in output for w in ("unable","error","couldn't","try again")): outcome,finding="graceful_failure",Finding(oracle="TaskOutcome",severity="GRACEFUL",message="Agent reported the failure honestly.")
      elif perturbation == "EmptyResult" and (trial.final_output or "").lower().startswith("inbox summary:"): outcome,finding="silent_failure",Finding(oracle="TaskOutcome",severity="SILENT_FAILURE",message="Agent claimed details despite an empty result.")
      else: outcome,finding="success",None
    con.execute("insert or replace into judge_cache values (?,?,?,?)",(key,outcome,finding.severity if finding else "",finding.message if finding else "")); con.commit(); con.close(); return outcome,finding
