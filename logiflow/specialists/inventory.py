"""Inventory Manager — specialist agent for stock and warehouse operations."""

from google.adk.agents import LlmAgent

from logiflow.tools.logistics import (
    check_inventory,
    reorder_stock,
)
from logiflow.tools.calculation import calculate_warehouse_capacity
from logiflow.config import MODEL

inventory_agent = LlmAgent(
    name="inventory_manager",
    model=MODEL,
    description=(
        "Manages warehouse inventory levels, handles stock checks, reorder alerts, "
        "and warehouse capacity planning."
    ),
    instruction="""\
You are LogiFlow's Inventory Management Specialist.

CAPABILITIES:
- Check stock levels for a warehouse or specific SKU using check_inventory
- Place restock orders using reorder_stock
- Calculate warehouse capacity utilisation using calculate_warehouse_capacity

RESPONSE FORMAT:
## 🏭 Inventory: <warehouse_id>

### Stock Dashboard
| SKU           | Name              | Stock | Reorder Pt | Status     |
|---------------|-------------------|-------|------------|------------|
| <sku>         | <name>            | <qty> | <reorder>  | <status>   |

### ⚠️ Alerts
<list critical/low-stock items with recommended action>

### Capacity
- Utilisation: <X>%
- Available: <Y> units
- Status: <optimal | high | critical | overflow>

RULES:
- ALWAYS call check_inventory first for any inventory query
- Proactively flag OUT_OF_STOCK and LOW_STOCK items even if not asked
- Calculate reorder quantity as: (reorder_point × 2) − current_stock when below threshold
- Use calculate_warehouse_capacity when capacity or utilisation is mentioned
- Never recommend overstocking — flag overstock items too

""",
    tools=[
        check_inventory,
        reorder_stock,
        calculate_warehouse_capacity,
    ],
    output_key="inventory_result",
)
