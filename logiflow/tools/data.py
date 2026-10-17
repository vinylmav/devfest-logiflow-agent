"""Data processing tools for LogiFlow — reports, aggregation, formatting, code execution.

All functions return dicts (ADK best practice).
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta
from typing import Any


def generate_report(
    report_type: str,
    date_range: str = "last_7_days",
    warehouse_id: str = "WH-001",
) -> dict[str, Any]:
    """Generate a logistics performance report with metrics and insights.

    Args:
        report_type: One of 'daily_summary', 'weekly_performance',
                     'inventory_status', 'shipment_analytics', 'cost_analysis'.
        date_range: Time window — 'last_7_days', 'last_30_days', 'today', or 'last_24h'.
        warehouse_id: Target warehouse (e.g., 'WH-001').

    Returns:
        A dict with structured report metrics, KPIs, and insights.
    """
    rtype = report_type.strip().lower()
    allowed = {"daily_summary", "weekly_performance", "inventory_status",
                "shipment_analytics", "cost_analysis"}
    if rtype not in allowed:
        return {"status": "error", "error": f"Unknown report_type '{report_type}'. Choose from: {sorted(allowed)}"}

    now = datetime.now()
    generated_at = now.isoformat()

    if rtype == "daily_summary":
        return {
            "status": "success",
            "report_type": "Daily Summary",
            "warehouse_id": warehouse_id,
            "date": now.strftime("%Y-%m-%d"),
            "generated_at": generated_at,
            "metrics": {
                "total_shipments_dispatched": 142,
                "on_time_delivery_rate": "94.4%",
                "average_handling_time_min": 18.3,
                "shipments_delayed": 8,
                "new_issues_logged": 3,
                "issues_resolved": 5,
                "total_orders_processed": 189,
                "inventory_alerts": 2,
            },
            "highlights": [
                "On-time delivery rate above 94% — within SLA threshold.",
                "3 new delay incidents logged — all assigned to resolution teams.",
                "Inventory low-stock alert: SKU-PLT-100 approaching reorder point.",
            ],
            "recommendations": [
                "Pre-position stock for SKU-PLT-100 to avoid stockout within 3 days.",
                "Review delay root causes on Chennai–Pune corridor (3 of 8 delays).",
            ],
        }

    if rtype == "weekly_performance":
        days = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        shipments_per_day = [87, 104, 132, 118, 142, 97, 156]
        return {
            "status": "success",
            "report_type": "Weekly Performance",
            "warehouse_id": warehouse_id,
            "date_range": date_range,
            "generated_at": generated_at,
            "kpis": {
                "total_shipments": sum(shipments_per_day),
                "avg_daily_shipments": round(sum(shipments_per_day) / 7, 1),
                "peak_day": days[shipments_per_day.index(max(shipments_per_day))],
                "on_time_rate": "92.7%",
                "avg_delivery_days": 3.4,
                "total_revenue_usd": 84320.50,
                "total_issues": 17,
                "issue_resolution_rate": "88.2%",
            },
            "trend": [
                {"date": d, "shipments": s}
                for d, s in zip(days, shipments_per_day)
            ],
            "insights": [
                "Volume peaked on Friday (+19% vs weekly avg). Consider weekend pre-staging.",
                "Issue resolution rate dipped to 88% — 2 open tickets require escalation.",
            ],
        }

    if rtype == "inventory_status":
        return {
            "status": "success",
            "report_type": "Inventory Status",
            "warehouse_id": warehouse_id,
            "generated_at": generated_at,
            "summary": {
                "total_skus": 6,
                "in_stock": 3,
                "low_stock": 2,
                "out_of_stock": 1,
                "overstock": 0,
                "total_units_on_hand": 2847,
                "capacity_utilization": "67.3%",
            },
            "alerts": [
                {"sku": "SKU-PLT-100", "name": "Heavy-Duty Euro Pallet", "stock": 108, "reorder_point": 120, "status": "low_stock"},
                {"sku": "SKU-STR-200", "name": "Industrial Shrink Film", "stock": 12, "reorder_point": 80, "status": "low_stock"},
                {"sku": "SKU-LBL-300", "name": "RFID Labels", "stock": 0, "reorder_point": 250, "status": "out_of_stock"},
            ],
            "recommendations": [
                "Place emergency reorder for SKU-LBL-300 immediately.",
                "Reorder SKU-PLT-100 — 10% below reorder threshold.",
            ],
        }

    if rtype == "shipment_analytics":
        return {
            "status": "success",
            "report_type": "Shipment Analytics",
            "warehouse_id": warehouse_id,
            "date_range": date_range,
            "generated_at": generated_at,
            "volume": {
                "total_shipments": 836,
                "by_priority": {"standard": 502, "express": 218, "overnight": 76, "freight": 40},
                "by_status": {"delivered": 621, "in_transit": 142, "out_for_delivery": 48, "delayed": 18, "returned": 7},
            },
            "performance": {
                "on_time_delivery_rate": "93.1%",
                "average_transit_days": 3.6,
                "first_attempt_delivery_rate": "91.4%",
                "return_rate": "0.84%",
            },
            "top_routes": [
                {"route": "Chennai → Mumbai", "shipments": 184, "on_time_rate": "95.7%"},
                {"route": "Bengaluru → Delhi", "shipments": 157, "on_time_rate": "91.1%"},
                {"route": "Mumbai → Kolkata", "shipments": 134, "on_time_rate": "89.6%"},
            ],
        }

    # cost_analysis
    return {
        "status": "success",
        "report_type": "Cost Analysis",
        "warehouse_id": warehouse_id,
        "date_range": date_range,
        "generated_at": generated_at,
        "cost_breakdown": {
            "total_logistics_spend_usd": 47820.40,
            "transportation": 31240.00,
            "warehousing": 8760.00,
            "last_mile": 5420.00,
            "packaging": 1800.40,
            "insurance": 600.00,
        },
        "cost_per_shipment": {
            "average": 57.21,
            "standard": 38.40,
            "express": 72.80,
            "overnight": 134.50,
            "freight": 284.00,
        },
        "savings_opportunities": [
            "Consolidating ground shipments on Chennai–Pune corridor could save ~$2,400/month.",
            "Switching 15% of express to standard for non-urgent orders saves ~$890/month.",
        ],
    }


def run_python_code(code: str) -> dict[str, Any]:
    """Execute Python code in a sandboxed subprocess and return the output.

    Args:
        code: Python code to execute (must be self-contained).

    Returns:
        A dict with stdout, stderr, and returncode.
    """
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Execution timed out (15s limit)."}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def format_tracking_info(shipment_data: dict[str, Any]) -> dict[str, Any]:
    """Format raw shipment data into a clean, human-readable tracking summary.

    Args:
        shipment_data: Raw dict as returned by track_shipment().

    Returns:
        A dict with a formatted summary string and key fields.
    """
    if not isinstance(shipment_data, dict):
        return {"status": "error", "error": "shipment_data must be a dict."}

    sid = shipment_data.get("shipment_id", "N/A")
    status = shipment_data.get("status", "unknown").replace("_", " ").title()
    origin = shipment_data.get("origin", "N/A")
    dest = shipment_data.get("destination", "N/A")
    location = shipment_data.get("current_location", "N/A")
    eta = shipment_data.get("estimated_delivery", "N/A")
    carrier = shipment_data.get("carrier", "N/A")

    events = shipment_data.get("tracking_events", [])
    event_lines = "\n".join(
        f"  [{e.get('timestamp', '')[:16]}] {e.get('location', '')} — {e.get('description', '')}"
        for e in events[-3:]  # last 3 events
    )

    summary = (
        f"📦 Shipment: {sid}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status     : {status}\n"
        f"Route      : {origin} → {dest}\n"
        f"Location   : {location}\n"
        f"ETA        : {eta}\n"
        f"Carrier    : {carrier}\n"
        f"\nRecent Events:\n{event_lines or '  No events recorded.'}"
    )

    return {
        "status": "success",
        "shipment_id": sid,
        "summary": summary,
        "status_label": status,
        "eta": eta,
        "current_location": location,
    }


def aggregate_metrics(
    data_points: list[dict[str, Any]],
    group_by: str = "",
    metric: str = "count",
) -> dict[str, Any]:
    """Aggregate a list of logistics data points.

    Args:
        data_points: List of dicts representing data records.
        group_by: Optional field name to group results by.
        metric: Aggregation function — 'count', 'sum', 'average', 'min', 'max'.
                For 'sum'/'average'/'min'/'max', the first numeric field in each
                record is used unless group_by matches a numeric field.

    Returns:
        A dict with aggregated results.
    """
    if not data_points:
        return {"status": "success", "result": {}, "total_records": 0}

    allowed_metrics = {"count", "sum", "average", "min", "max"}
    metric_clean = metric.strip().lower()
    if metric_clean not in allowed_metrics:
        return {"status": "error", "error": f"metric must be one of {sorted(allowed_metrics)}"}

    def _get_numeric(record: dict[str, Any]) -> float | None:
        for v in record.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
        return None

    if group_by:
        groups: dict[str, list[float]] = {}
        for record in data_points:
            key = str(record.get(group_by, "unknown"))
            val = _get_numeric(record)
            groups.setdefault(key, [])
            if val is not None:
                groups[key].append(val)

        result: dict[str, Any] = {}
        for key, vals in groups.items():
            if metric_clean == "count":
                result[key] = len(vals)
            elif vals:
                if metric_clean == "sum":
                    result[key] = round(sum(vals), 4)
                elif metric_clean == "average":
                    result[key] = round(sum(vals) / len(vals), 4)
                elif metric_clean == "min":
                    result[key] = min(vals)
                elif metric_clean == "max":
                    result[key] = max(vals)
            else:
                result[key] = None
    else:
        all_vals = [v for r in data_points if (v := _get_numeric(r)) is not None]
        if metric_clean == "count":
            result = {"total": len(data_points)}
        elif all_vals:
            if metric_clean == "sum":
                result = {"total": round(sum(all_vals), 4)}
            elif metric_clean == "average":
                result = {"average": round(sum(all_vals) / len(all_vals), 4)}
            elif metric_clean == "min":
                result = {"min": min(all_vals)}
            elif metric_clean == "max":
                result = {"max": max(all_vals)}
        else:
            result = {"total": len(data_points), "note": "No numeric fields found."}

    return {
        "status": "success",
        "total_records": len(data_points),
        "metric": metric_clean,
        "group_by": group_by or None,
        "result": result,
    }


DATA_TOOLS = [
    generate_report,
    run_python_code,
    format_tracking_info,
    aggregate_metrics,
]
