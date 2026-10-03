"""FastAPI server for persisted suites, runs, progress events, and dashboard assets."""
from __future__ import annotations
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from .store import ROOT, load_suite
from .runner import run_suite
app=FastAPI(title="Gauntlet")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
_events={}
class RunRequest(BaseModel):
    agent_path: str; user_input: str="Summarize my unread emails and flag anything urgent."; trials: int=3; only: str|None=None
def _suites():
    return [load_suite(p.stem) for p in (ROOT/"suites").glob("*.json")] if (ROOT/"suites").exists() else []
@app.get("/api/suites")
def suites(): return [{"id":s.suite_id,"agent":s.agent_name,"score":s.score,"created_at":s.created_at} for s in _suites()]
@app.get("/api/suites/{suite_id}")
def suite(suite_id: str):
    try: return load_suite(suite_id)
    except FileNotFoundError: raise HTTPException(404,"suite not found")
@app.get("/api/suites/{suite_id}/results/{idx}/trials/{trial}")
def trial(suite_id: str, idx: int, trial: int):
    s=load_suite(suite_id)
    try: return s.results[idx].trials[trial]
    except IndexError: raise HTTPException(404,"trial not found")
@app.post("/api/run")
async def run(req: RunRequest):
    # The real suite ID is known when the safe, local task completes; expose a pending token meanwhile.
    token="pending-"+str(len(_events)+1); _events[token]=["event: progress\ndata: started\n\n"]
    async def work():
        s=await asyncio.to_thread(run_suite,req.agent_path,req.user_input,req.trials,4,None,req.only); _events[token].append(f"event: complete\ndata: {s.suite_id}\n\n")
    asyncio.create_task(work()); return {"suite_id":token}
@app.get("/api/run/{suite_id}/events")
async def events(suite_id: str):
    async def stream():
        sent=0
        while True:
            items=_events.get(suite_id,[])
            while sent<len(items):
                item=items[sent]; sent+=1; yield item
                if "complete" in item: return
            await asyncio.sleep(.1)
    return StreamingResponse(stream(),media_type="text/event-stream")
DIST=Path(__file__).resolve().parents[1]/"dashboard"/"dist"
@app.get("/")
def dashboard():
    page=DIST/"index.html"
    if not page.exists(): raise HTTPException(404,"Build dashboard with npm run build first.")
    return FileResponse(page)
