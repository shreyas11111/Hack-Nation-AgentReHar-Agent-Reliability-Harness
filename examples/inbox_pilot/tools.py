"""Safe local-only InboxPilot tools."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).parent
def read_inbox(limit: int = 5) -> list[dict]: return json.loads((ROOT/"fixtures/inbox.json").read_text())[:limit]
def search_web(query: str) -> list[dict]: return [{"title":"Acme help","url":"https://help.acme.com","snippet":f"Results for {query}"}]
def get_calendar(date: str) -> list[dict]: return [{"title":"Design review","start":f"{date}T14:00","end":f"{date}T15:00"}]
def send_email(to: str, subject: str, body: str) -> dict:
    path=Path(".gauntlet/outbox.jsonl"); path.parent.mkdir(exist_ok=True)
    with path.open("a") as f: f.write(json.dumps({"to":to,"subject":subject,"body":body})+"\n")
    return {"status":"ok","id":"local-email"}
