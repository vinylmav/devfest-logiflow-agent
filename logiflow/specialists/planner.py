"""Route Planner — specialist agent for routing and cost optimisation."""

from logiflow.config import MODEL
from google.adk.agents import LlmAgent

from logiflow.tools.logistics import (
    calculate_route,
    estimate_shipping_cost,
    calculate_eta,
)
from logiflow.tools.calculation import (
    calculate_distance,
    calculate_fuel_cost,
    calculate_delivery_window,
    calculate_shipping_rate,
)

planner_agent = LlmAgent(
    name="route_planner",
    model=MODEL,
    description=(
        "Optimises delivery routes, calculates shipping costs, compares methods, "
        "and plans efficient multi-stop logistics paths."
    ),
    instruction="""\
You are LogiFlow's Route Planning & Cost Optimisation Specialist.

CAPABILITIES:
- Calculate optimal routes (distance / time / cost modes) using calculate_route
- Estimate shipping costs with full breakdown using estimate_shipping_cost
- Compute distances and drive times using calculate_distance
- Calculate fuel costs for fleet planning using calculate_fuel_cost
- Determine delivery windows by method using calculate_delivery_window
- Compute detailed shipping rates with dimensional weight using calculate_shipping_rate

RESPONSE FORMAT:
## 🗺️ Route: <origin> → <destination>
**Optimised For:** <distance | time | cost>
**Total Distance:** <X> km
**Estimated Transit Time:** <Y> hours
**Fuel Cost:** $<Z>

### Route Segments
<table of segments with distance and time>

### Cost Comparison
| Method    | Cost    | Days    |
|-----------|---------|---------|
| Ground    | $XX.XX  | 5-7     |
| Express   | $XX.XX  | 2-3     |
| Overnight | $XX.XX  | 1       |

### Recommendation
<best option based on user's priority>

RULES:
- ALWAYS call calculate_route before answering route queries
- Compare at least 2 shipping methods when cost is mentioned
- Show full cost breakdown — never just a total
- Highlight the recommended option based on user's stated priority
- Use calculate_fuel_cost for fleet/fleet-cost queries

""",
    tools=[
        calculate_route,
        estimate_shipping_cost,
        calculate_eta,
        calculate_distance,
        calculate_fuel_cost,
        calculate_delivery_window,
        calculate_shipping_rate,
    ],
    output_key="planner_result",
)
