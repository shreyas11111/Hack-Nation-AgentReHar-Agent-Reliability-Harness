# Gauntlet

Chaos engineering for AI agents: record a run, perturb tool data safely, judge the response, and score robustness. GIF placeholder: `docs/demo.gif`.

## 60-second quickstart

```bash
uv sync
GAUNTLET_MOCK_LLM=1 uv run gauntlet demo
uv run gauntlet serve
```

`uv` was unavailable in the development environment, so the equivalent validated fallback was `.venv/bin/python -m pytest` after `python -m venv .venv` and pip installation.

## Test your own agent in five lines

```python
from gauntlet import Harness
h = Harness.from_env()
@h.tool
def lookup(q: str): return [{"result": q}]
client = h.wrap_llm(h.llm_client())
def run(user_input: str, harness: Harness) -> str: ...
```

| Perturbations | Oracles |
|---|---|
| latency, timeout, 500, 429, truncated JSON, schema drift, empty data, bloat, three prompt injections | canary leak, unauthorized recipient, new sensitive tool, looping, token blowup, hang, task outcome |

Safety: replay never executes an out-of-baseline tool call. Only test agents you own or are authorized to test.

CI example: `GAUNTLET_MOCK_LLM=1 uv run gauntlet run agent.py --fail-under 80`.
Chaos engineering for AI agents. Record a real agent run, replay it with broken APIs, malformed data, and prompt injections, and get a robustness score showing what your agent actually does when the world breaks.
