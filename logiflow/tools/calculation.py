"""Calculation tools for LogiFlow — math, ETA, cost, capacity.

All functions return dicts (ADK best practice).
Pure Python, no external dependencies.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timedelta
from typing import Any


def _hash_distance(origin: str, destination: str) -> float:
    """Deterministic pseudo-distance between two locations (50–3000 km)."""
    key = f"{origin.strip().lower()}:{destination.strip().lower()}"
    h = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
    return 50.0 + (h % 29500) / 10.0


def calculate_distance(origin: str, destination: str) -> dict[str, Any]:
    """Estimate the road distance and drive time between two locations.

    Args:
        origin: Starting location (city or address).
        destination: Ending location (city or address).

    Returns:
        A dict with distance_km and estimated_drive_time_hours.
    """
    if not origin.strip() or not destination.strip():
        return {"status": "error", "error": "Both origin and destination must be provided."}

    if origin.strip().lower() == destination.strip().lower():
        return {
            "status": "success",
            "origin": origin.strip(),
            "destination": destination.strip(),
            "distance_km": 0.0,
            "estimated_drive_time_hours": 0.0,
        }

    dist = round(_hash_distance(origin, destination), 1)
    avg_speed_kmph = 65.0  # typical highway average
    drive_hours = round(dist / avg_speed_kmph, 2)

    return {
        "status": "success",
        "origin": origin.strip(),
        "destination": destination.strip(),
        "distance_km": dist,
        "estimated_drive_time_hours": drive_hours,
    }


def calculate_fuel_cost(
    distance_km: float,
    fuel_price_per_liter: float = 1.5,
    fuel_efficiency_kmpl: float = 8.0,
) -> dict[str, Any]:
    """Calculate fuel cost for a logistics trip.

    Args:
        distance_km: Total trip distance in kilometres.
        fuel_price_per_liter: Fuel price per litre in USD (default: 1.50).
        fuel_efficiency_kmpl: Vehicle fuel efficiency in km/litre (default: 8.0).

    Returns:
        A dict with liters_needed, total_cost, and cost_per_km.
    """
    if distance_km < 0:
        return {"status": "error", "error": "distance_km must be >= 0."}
    if fuel_efficiency_kmpl <= 0:
        return {"status": "error", "error": "fuel_efficiency_kmpl must be > 0."}

    liters = distance_km / fuel_efficiency_kmpl
    total_cost = round(liters * fuel_price_per_liter, 2)
    cost_per_km = round(total_cost / max(distance_km, 0.001), 4)

    return {
        "status": "success",
        "distance_km": round(distance_km, 2),
        "fuel_price_per_liter": fuel_price_per_liter,
        "fuel_efficiency_kmpl": fuel_efficiency_kmpl,
        "liters_needed": round(liters, 2),
        "total_cost": total_cost,
        "cost_per_km": cost_per_km,
    }


def calculate_delivery_window(
    shipping_method: str,
    distance_km: float,
) -> dict[str, Any]:
    """Calculate a delivery window based on shipping method and distance.

    Args:
        shipping_method: One of 'ground', 'express', 'overnight', 'freight'.
        distance_km: Route distance in kilometres (used to adjust ground/freight).

    Returns:
        A dict with min_days, max_days, and expected_date.
    """
    method = shipping_method.strip().lower()

    base_windows = {
        "ground":    {"min": 3, "max": 7},
        "express":   {"min": 2, "max": 3},
        "overnight": {"min": 1, "max": 1},
        "freight":   {"min": 7, "max": 14},
    }

    window = base_windows.get(method, base_windows["ground"])
    min_days = window["min"]
    max_days = window["max"]

    # Distance modifier: add 1 day per 1000 km over 500 km for ground/freight
    if method in ("ground", "freight") and distance_km > 500:
        extra = math.floor((distance_km - 500) / 1000)
        min_days = min(min_days + extra, max_days)

    expected_date = (datetime.now() + timedelta(days=max_days)).strftime("%Y-%m-%d")

    return {
        "status": "success",
        "shipping_method": method,
        "distance_km": round(distance_km, 1),
        "min_days": min_days,
        "max_days": max_days,
        "expected_date": expected_date,
    }


def calculate_warehouse_capacity(
    current_stock: int,
    max_capacity: int,
    incoming: int = 0,
    outgoing: int = 0,
) -> dict[str, Any]:
    """Calculate warehouse capacity utilisation after pending movements.

    Args:
        current_stock: Units currently in the warehouse.
        max_capacity: Maximum warehouse capacity in units.
        incoming: Pending incoming stock units (not yet received).
        outgoing: Pending outgoing shipments (not yet dispatched).

    Returns:
        A dict with utilization_percent, available_space, and status.
    """
    if max_capacity <= 0:
        return {"status": "error", "error": "max_capacity must be > 0."}

    projected = max(0, current_stock + incoming - outgoing)
    utilization = round((projected / max_capacity) * 100, 1)
    available = max(0, max_capacity - projected)

    if utilization >= 100:
        capacity_status = "overflow"
    elif utilization >= 85:
        capacity_status = "critical"
    elif utilization >= 60:
        capacity_status = "high"
    else:
        capacity_status = "optimal"

    return {
        "status": "success",
        "current_stock": current_stock,
        "max_capacity": max_capacity,
        "incoming": incoming,
        "outgoing": outgoing,
        "projected_stock": projected,
        "utilization_percent": utilization,
        "available_space": available,
        "capacity_status": capacity_status,
    }


def calculate_shipping_rate(
    weight_kg: float,
    volume_cbm: float = 0.0,
    distance_km: float = 0.0,
    is_hazardous: bool = False,
) -> dict[str, Any]:
    """Calculate a detailed shipping rate with dimensional weight comparison.

    Args:
        weight_kg: Actual cargo weight in kilograms.
        volume_cbm: Cargo volume in cubic metres (0 = not provided).
        distance_km: Route distance in kilometres (0 = local/flat rate).
        is_hazardous: Whether cargo is classified as hazardous material.

    Returns:
        A dict with actual_weight, dimensional_weight, chargeable_weight,
        base_rate, distance_surcharge, hazmat_surcharge, and total_rate.
    """
    actual_weight = max(round(float(weight_kg), 2), 0.01)

    # Dimensional weight: CBM × 1000 (air/courier standard 1 CBM = 167 kg skipped for road)
    dim_weight = round(volume_cbm * 280, 2) if volume_cbm > 0 else 0.0
    chargeable_weight = max(actual_weight, dim_weight)

    # Base rate: $2.80 per chargeable kg
    base_rate = round(chargeable_weight * 2.80, 2)

    # Distance surcharge: $0.003 per km per kg
    distance_surcharge = round(distance_km * chargeable_weight * 0.003, 2) if distance_km > 0 else 0.0

    # Hazmat surcharge: 35% of base
    hazmat_surcharge = round(base_rate * 0.35, 2) if is_hazardous else 0.0

    total_rate = round(base_rate + distance_surcharge + hazmat_surcharge, 2)

    return {
        "status": "success",
        "actual_weight_kg": actual_weight,
        "dimensional_weight_kg": dim_weight,
        "chargeable_weight_kg": chargeable_weight,
        "base_rate": base_rate,
        "distance_surcharge": distance_surcharge,
        "hazmat_surcharge": hazmat_surcharge,
        "total_rate": total_rate,
        "is_hazardous": is_hazardous,
    }


CALCULATION_TOOLS = [
    calculate_distance,
    calculate_fuel_cost,
    calculate_delivery_window,
    calculate_warehouse_capacity,
    calculate_shipping_rate,
]
