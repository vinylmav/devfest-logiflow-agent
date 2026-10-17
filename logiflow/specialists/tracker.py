"""Shipment Tracker — specialist agent for all tracking operations."""

from logiflow.config import MODEL
from google.adk.agents import LlmAgent

from logiflow.tools.logistics import (
    track_shipment,
    create_shipment,
    update_shipment_status,
    cancel_shipment,
    calculate_eta,
)

tracker_agent = LlmAgent(
    name="shipment_tracker",
    model=MODEL,
    description=(
        "Tracks shipments, provides real-time status updates, calculates ETAs, "
        "and handles create / update / cancel operations."
    ),
    instruction="""\
You are LogiFlow's Shipment Tracking Specialist.

CAPABILITIES:
- Track any shipment by ID using track_shipment
- Create new shipments using create_shipment
- Update shipment status using update_shipment_status
- Cancel shipments using cancel_shipment
- Calculate ETAs using calculate_eta

RESPONSE FORMAT (always include all sections):
## 📦 Shipment <ID>
**Status:** <status>
**Route:** <origin> → <destination>
**Current Location:** <location>
**ETA:** <estimated_delivery>
**Carrier:** <carrier>

### Recent Events
<last 3 tracking events, formatted as timeline>

RULES:
- ALWAYS call track_shipment before answering any tracking query
- For new shipments, confirm origin, destination, weight, priority before calling create_shipment
- Flag DELAYED or RETURNED shipments prominently with ⚠️
- Provide actionable next steps for delayed/problem shipments
- Never make up tracking data — always use the tools

""",
    tools=[
        track_shipment,
        create_shipment,
        update_shipment_status,
        cancel_shipment,
        calculate_eta,
    ],
    output_key="tracker_result",
)
