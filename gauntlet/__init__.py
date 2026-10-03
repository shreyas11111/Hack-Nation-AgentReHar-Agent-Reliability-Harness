"""Gauntlet public SDK."""
from .sdk import Harness
def tool(harness: Harness): return harness.tool
def wrap_llm(client, harness: Harness): return harness.wrap_llm(client)
__all__=["Harness", "tool", "wrap_llm"]
