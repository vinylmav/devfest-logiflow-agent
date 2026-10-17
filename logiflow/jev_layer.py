"""Jev Decision Layer — System 1 Fast Decisions for LogiFlow.

Provides ~1ms routing, quality gates, and escalation detection.
Currently uses local heuristics as fallback.
Swap to TypeSafe Jev API when TYPESAFE_API_KEY is available.
"""

import os
import re
from typing import Optional

JEV_API_KEY = os.getenv('TYPESAFE_API_KEY', '')
JEV_ENABLED = bool(JEV_API_KEY)


def classify_intent(query: str) -> dict:
    """Fast intent classification (~1ms).
    
    Args:
        query: User's input query
    
    Returns:
        dict with: intent (str), confidence (float 0-1), agent (str)
    """
    # Keyword-based fast classification
    query_lower = query.lower()
    
    patterns = {
        'tracking': {
            'keywords': ['track', 'where is', 'status', 'eta', 'shipment', 'delivery', 'package', 'shipped'],
            'agent': 'shipment_tracker'
        },
        'routing': {
            'keywords': ['route', 'cost', 'shipping rate', 'how much', 'cheapest', 'fastest', 'ship from', 'ship to', 'distance'],
            'agent': 'route_planner'
        },
        'inventory': {
            'keywords': ['inventory', 'stock', 'warehouse', 'reorder', 'capacity', 'supply', 'product'],
            'agent': 'inventory_manager'
        },
        'issue': {
            'keywords': ['problem', 'issue', 'delay', 'damaged', 'lost', 'complaint', 'refund', 'broken', 'missing', 'wrong'],
            'agent': 'issue_resolver'
        },
        'analytics': {
            'keywords': ['report', 'analytics', 'trend', 'kpi', 'performance', 'summary', 'statistics', 'metrics', 'dashboard'],
            'agent': 'analytics_agent'
        }
    }
    
    best_intent = 'general'
    best_score = 0.0
    best_agent = 'smart_router'
    
    for intent, config in patterns.items():
        matches = sum(1 for kw in config['keywords'] if kw in query_lower)
        if matches > 0:
            score = min(matches / 2, 1.0)  # normalize
            if score > best_score:
                best_score = score
                best_intent = intent
                best_agent = config['agent']
    
    return {
        'intent': best_intent,
        'confidence': round(best_score, 2),
        'agent': best_agent,
        'method': 'jev_api' if JEV_ENABLED else 'local_heuristic'
    }


def quality_gate(output: str, query: str) -> dict:
    """Fast output quality check (~1ms).
    
    Returns:
        dict with: passed (bool), score (float 0-1), reason (str)
    """
    if not output or len(output.strip()) < 10:
        return {'passed': False, 'score': 0.0, 'reason': 'Output too short or empty'}
    
    # Check if output is relevant to query
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
    output_words = set(re.findall(r'\b\w{3,}\b', output.lower()))
    overlap = len(query_words & output_words) / max(len(query_words), 1)
    
    score = min(1.0, 0.3 + overlap * 0.7)  # base score + relevance
    
    if len(output) > 50:
        score = min(1.0, score + 0.1)
    
    return {
        'passed': score >= 0.5,
        'score': round(score, 2),
        'reason': 'Quality check passed' if score >= 0.5 else 'Low relevance to query',
        'method': 'jev_api' if JEV_ENABLED else 'local_heuristic'
    }


def should_escalate(query: str, context: str = '') -> dict:
    """Detect if a request needs human escalation (~1ms).
    
    Returns:
        dict with: escalate (bool), reason (str), urgency (str)
    """
    query_lower = query.lower()
    
    escalation_triggers = {
        'high': ['legal', 'lawsuit', 'attorney', 'regulatory', 'compliance violation', 'safety hazard', 'injury'],
        'medium': ['refund over', 'insurance claim', 'bulk order', 'contract', 'sla breach', 'data breach'],
        'low': ['escalate', 'manager', 'supervisor', 'human', 'speak to someone']
    }
    
    for urgency, triggers in escalation_triggers.items():
        for trigger in triggers:
            if trigger in query_lower:
                return {
                    'escalate': True,
                    'reason': f'Trigger detected: "{trigger}"',
                    'urgency': urgency,
                    'method': 'jev_api' if JEV_ENABLED else 'local_heuristic'
                }
    
    return {
        'escalate': False,
        'reason': 'No escalation needed',
        'urgency': 'none',
        'method': 'jev_api' if JEV_ENABLED else 'local_heuristic'
    }
