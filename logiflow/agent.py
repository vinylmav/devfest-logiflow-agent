"""LogiFlow — Self-Correcting Logistics Handler Agent.

DevFest Chennai 2026 — Agent Wars

Architecture:
  - Dual-Brain: Gemini (reasoning) + Jev (fast ~1ms decisions)
  - 5 Specialist Agents: tracker, planner, inventory, resolver, analytics
  - Self-correcting feedback loop: validate → critique → refine
  - Persistent lesson memory: mistakes are never repeated

Run:
  uv run adk run logiflow
  uv run adk run logiflow "Track shipment SHP-2026-4521"
  uv run adk web .
"""

from .router import router_agent

# ADK discovers root_agent via logiflow/__init__.py → logiflow/agent.py
root_agent = router_agent
