"""Smart Router — central intelligence that delegates to specialist agents.

Uses Jev fast-path for instant intent classification, then routes to:
  shipment_tracker, route_planner, inventory_manager, issue_resolver, analytics_agent

ADK handles transfer_to_agent automatically via sub_agents.
"""

from google.adk.agents import LlmAgent

from logiflow.config import MODEL
from logiflow.specialists import (
    tracker_agent,
    planner_agent,
    inventory_agent,
    resolver_agent,
    analytics_agent,
)

router_agent = LlmAgent(
    name="smart_router",
    model=MODEL,
    description="LogiFlow central router — understands logistics requests and delegates to the right specialist.",
    instruction="""\
You are LogiFlow — an intelligent logistics management system competing in Agent Wars at DevFest Chennai 2026.

You have 5 specialist sub-agents. Your ONLY job is to understand the request and delegate immediately.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUTING DECISION TABLE (fast path)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"track", "where is", "shipment status", "ETA", "SHP-", "package"
  → shipment_tracker

"route", "shipping cost", "how much to ship", "cheapest", "fastest",
"distance", "ship from", "ship to", "delivery window"
  → route_planner

"inventory", "stock", "warehouse", "reorder", "capacity", "SKU", "supply"
  → inventory_manager

"problem", "issue", "delay", "delayed", "damaged", "lost", "complaint",
"refund", "missing", "customs", "dispute", "wrong address"
  → issue_resolver

"report", "analytics", "trends", "KPI", "performance", "summary",
"statistics", "dashboard", "metrics", "forecast"
  → analytics_agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULES:
1. Route IMMEDIATELY — don't deliberate, don't re-ask unless truly ambiguous
2. If ambiguous, ask ONE sharp clarifying question (e.g., "Is this about tracking or a billing issue?")
3. After the specialist returns, present their output cleanly to the user
4. If a specialist fails or gives an unsatisfactory answer, handle it yourself
5. For multi-part requests, handle each part sequentially using the right specialist

SELF-CORRECTION:
- Past lessons from previous corrections are injected below
- Learn from them — don't repeat the same mistakes


OPENING EXAMPLES:
- "Track SHP-2026-A1B2" → immediately transfer to shipment_tracker
- "What's the cheapest way to ship 50kg from Chennai to Mumbai?" → route_planner
- "SKU-PLT-100 inventory at WH-001" → inventory_manager
- "My package SHP-2026-XYZ was damaged" → issue_resolver
- "Show me last week's performance report" → analytics_agent
""",
    sub_agents=[
        tracker_agent,
        planner_agent,
        inventory_agent,
        resolver_agent,
        analytics_agent,
    ],
    output_key="router_result",
)
