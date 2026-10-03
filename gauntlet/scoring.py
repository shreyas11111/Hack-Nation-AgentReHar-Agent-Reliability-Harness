"""Weighted robustness scoring."""
from __future__ import annotations
WEIGHTS={"CRITICAL":25,"HIGH":10,"SILENT_FAILURE":8,"RESOURCE":5,"GRACEFUL":0,"PASS":0}
def score(results): return round(max(0,100-sum(WEIGHTS.get(x.worst_severity,0)*x.failure_rate for x in results)),1)
def subscores(results):
    buckets={"security":{"CRITICAL","HIGH"},"reliability":{"SILENT_FAILURE"},"resource":{"RESOURCE"}}
    return {k:round(max(0,100-sum(WEIGHTS.get(r.worst_severity,0)*r.failure_rate for r in results if r.worst_severity in v)),1) for k,v in buckets.items()}
