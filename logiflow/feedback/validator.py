"""Output quality validation for LogiFlow.
Uses deterministic checks + heuristics for fast quality scoring.
No LLM calls — pure Python for ~1ms validation.
"""

import re
from typing import Any

# Common English stop words to exclude during relevance extraction
STOP_WORDS: set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "should", "shouldn't", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "won't", "would", "wouldn't", "you", "your",
    "yours", "yourself", "yourselves", "please", "tell", "show", "give", "check",
    "find", "get", "need", "want"
}

# Incomplete ending indicators (conjunctions, prepositions, or dangling words)
INCOMPLETE_TRAILING_WORDS: set[str] = {
    "and", "or", "but", "because", "with", "the", "to", "for", "in", "of", "at",
    "by", "if", "as", "than", "that", "which", "a", "an", "then", "so", "such",
    "from", "into", "about", "is", "are", "was", "were", "including", "such as"
}

# Domain keyword configuration for structure checks
STRUCTURE_REQUIREMENTS: dict[str, dict[str, list[str]]] = {
    "tracking": {
        "status": ["status", "in transit", "delivered", "out for delivery", "pending", "picked up", "dispatched", "delayed", "cancelled", "state", "departed", "arrived"],
        "location": ["location", "facility", "hub", "warehouse", "city", "origin", "destination", "checkpoint", "address", "station", "terminal", "depot"],
        "eta": ["eta", "estimated delivery", "estimated arrival", "expected delivery", "delivery date", "arrival time", "expected by", "time of arrival", "schedule"],
    },
    "route": {
        "distance": ["distance", "miles", "mi", "km", "kilometers", "mileage", "length", "radius"],
        "time": ["time", "duration", "hours", "hrs", "mins", "minutes", "days", "transit time", "travel time", "schedule"],
        "cost": ["cost", "price", "rate", "$", "usd", "fee", "charge", "total cost", "expense", "quote", "pricing", "fuel surcharge"],
    },
    "inventory": {
        "stock": ["stock", "in stock", "out of stock", "stock level", "reorder", "available", "inventory", "on hand", "reserved", "shortage"],
        "quantity": ["quantity", "qty", "units", "count", "items", "volume", "pallets", "pieces", "capacity", "amount", "batch"],
        "warehouse": ["warehouse", "facility", "storage", "depot", "distribution center", "aisle", "bin", "shelf", "bay", "zone", "location"],
    },
    "issue": {
        "resolution": ["resolution", "resolved", "solution", "resolve", "fix", "compensation", "refund", "replacement", "remedy", "settlement"],
        "status": ["status", "investigating", "open", "closed", "pending", "in progress", "escalated", "under review", "assigned", "resolved"],
        "action": ["action", "next steps", "corrective", "dispatch", "contact", "procedure", "plan", "steps to take", "follow-up", "escalate"],
    },
    "report": {
        "metrics": ["metric", "kpi", "rate", "percentage", "%", "performance", "throughput", "efficiency", "benchmark", "ratio", "score"],
        "data": ["data", "total", "average", "count", "table", "statistics", "figures", "volume", "breakdown", "numbers", "dataset"],
        "summary": ["summary", "overview", "finding", "conclusion", "analysis", "trend", "insights", "executive summary", "key takeaway"],
    },
}

# Classification keyword patterns
CLASSIFICATION_PATTERNS: dict[str, list[str]] = {
    "tracking": [
        "track", "tracking", "where is", "status", "eta", "shipment", "delivery",
        "package", "shipped", "carrier", "waybill", "consignment", "in transit",
        "parcel", "courier", "where's"
    ],
    "route": [
        "route", "routing", "distance", "shipping rate", "shipping cost", "freight rate",
        "cheapest route", "fastest route", "transit time", "ship from", "ship to",
        "origin", "destination", "waypoint", "multimodal", "carrier selection",
        "how much to ship", "freight", "transport cost", "miles", "kilometers"
    ],
    "inventory": [
        "inventory", "stock", "warehouse", "reorder", "sku", "restock", "storage",
        "pallet", "shelf", "bin", "capacity", "supply level", "available units",
        "safety stock", "stockout", "on hand", "replenish"
    ],
    "issue": [
        "issue", "problem", "delay", "delayed", "damage", "damaged", "lost",
        "complaint", "refund", "broken", "missing", "dispute", "claim", "incident",
        "exception", "stolen", "wrong item", "late delivery", "damage claim"
    ],
    "report": [
        "report", "analytics", "trend", "kpi", "metrics", "summary", "dashboard",
        "performance", "statistics", "forecast", "audit", "daily summary",
        "weekly report", "monthly report", "throughput", "quarterly"
    ],
}


def classify_query(query: str) -> str:
    """Fast query classification using keyword matching.

    Args:
        query: User's input query string.

    Returns:
        One of 'tracking', 'route', 'inventory', 'issue', 'report', or 'general'.
    """
    if not query or not query.strip():
        return "general"

    query_lower = query.lower()
    scores: dict[str, int] = {cat: 0 for cat in CLASSIFICATION_PATTERNS}

    for category, keywords in CLASSIFICATION_PATTERNS.items():
        for kw in keywords:
            # Match word boundary or phrase
            if " " in kw:
                if kw in query_lower:
                    scores[category] += 2  # Multi-word phrase matches are stronger
            else:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, query_lower):
                    scores[category] += 1

    best_category = max(scores, key=lambda k: scores[k])
    if scores[best_category] > 0:
        return best_category

    return "general"


def _extract_key_terms(text: str) -> list[str]:
    """Extract meaningful search terms from text, omitting stop words."""
    raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-#]{2,}\b", text.lower())
    return [token for token in raw_tokens if token not in STOP_WORDS]


def _check_completeness(output: str) -> tuple[bool, str]:
    """Check if output ends completely without being truncated mid-sentence."""
    trimmed = output.strip()
    if not trimmed:
        return False, "Output is empty"

    # Valid sentence/markdown endings
    valid_terminal_chars = {".", "!", "?", "\"", "'", ")", "]", "}", "`", "|", ">"}

    # Check trailing character
    last_char = trimmed[-1]

    # Trailing truncation indicators
    if trimmed.endswith("...") or trimmed.endswith("…"):
        return False, "Output ends with an ellipsis (...), suggesting truncation"

    if last_char in {",", ";", ":", "-", "/"}:
        return False, f"Output ends abruptly with punctuation '{last_char}'"

    # Check trailing word
    last_word_match = re.search(r"\b([a-zA-Z]+)\b[^\w]*$", trimmed)
    if last_word_match:
        last_word = last_word_match.group(1).lower()
        if last_word in INCOMPLETE_TRAILING_WORDS:
            return False, f"Output ends with dangling word '{last_word}'"

    # If it ends with markdown closing code block or table row
    if trimmed.endswith("```") or trimmed.endswith("|"):
        return True, "Valid markdown closure"

    # Check terminal punctuation on the final line
    lines = [line.strip() for line in trimmed.splitlines() if line.strip()]
    last_line = lines[-1] if lines else trimmed

    if last_line[-1] in valid_terminal_chars:
        return True, "Valid terminal punctuation"

    # If the last line is a header or list item that is reasonably self-contained
    if re.match(r"^(#+|-|\*|\d+\.)\s+", last_line):
        return True, "Valid formatted item closure"

    return False, "Output does not conclude with terminal punctuation (. ! ?)"


def validate_output(output: str, query: str, expected_type: str = "general") -> dict[str, Any]:
    """Validate agent output quality.

    Performs 4 deterministic checks:
    1. Length check: non-empty and >= 20 chars for non-trivial queries.
    2. Relevance check: key terms from query appear in output.
    3. Structure check: expected domain concepts present for expected_type.
    4. Completeness check: output doesn't end mid-sentence.

    Args:
        output: The agent's output text.
        query: The original user query.
        expected_type: Type of expected output
            ('tracking', 'route', 'inventory', 'issue', 'report', 'general').

    Returns:
        dict with:
            - score (int): Quality score between 0 and 100.
            - passed (bool): True if score >= 60.
            - issues (list[str]): Detected problems.
            - suggestions (list[str]): Suggested fixes.
    """
    issues: list[str] = []
    suggestions: list[str] = []

    # Normalized inputs
    clean_output = (output or "").strip()
    clean_query = (query or "").strip()
    norm_type = expected_type.lower() if expected_type else "general"

    # 1. Length check (Max 25 pts)
    length_score = 25
    is_non_trivial = len(clean_query) >= 5 or len(clean_query.split()) > 1

    if not clean_output:
        return {
            "score": 0,
            "passed": False,
            "issues": ["Output is empty."],
            "suggestions": ["Provide a comprehensive answer addressing the user query."],
        }

    if is_non_trivial and len(clean_output) < 20:
        length_score = 5
        issues.append(f"Output is too short ({len(clean_output)} chars). Non-trivial queries require at least 20 chars.")
        suggestions.append("Provide a more comprehensive and detailed response.")
    elif len(clean_output) < 40 and is_non_trivial:
        length_score = 15

    # 2. Relevance check (Max 25 pts)
    relevance_score = 25
    query_key_terms = _extract_key_terms(clean_query)

    if query_key_terms:
        output_lower = clean_output.lower()
        matched_terms = [t for t in query_key_terms if t in output_lower]
        overlap_ratio = len(matched_terms) / len(query_key_terms)

        if overlap_ratio == 0:
            relevance_score = 0
            missing_preview = ", ".join(query_key_terms[:4])
            issues.append(f"Output lacks key terms from query (missing: {missing_preview}).")
            suggestions.append("Explicitly reference the identifiers, entities, or parameters mentioned in the query.")
        elif overlap_ratio < 0.4:
            relevance_score = 12
            missing_terms = [t for t in query_key_terms if t not in matched_terms]
            missing_preview = ", ".join(missing_terms[:3])
            issues.append(f"Output has low query overlap ({int(overlap_ratio * 100)}%). Missing terms: {missing_preview}.")
            suggestions.append("Incorporate more context and specific terms from the user request.")

    # 3. Structure check (Max 30 pts)
    structure_score = 30
    if norm_type in STRUCTURE_REQUIREMENTS:
        reqs = STRUCTURE_REQUIREMENTS[norm_type]
        output_lower = clean_output.lower()
        matched_sections: list[str] = []
        missing_sections: list[str] = []

        for section_name, keywords in reqs.items():
            if any(kw in output_lower for kw in keywords):
                matched_sections.append(section_name)
            else:
                missing_sections.append(section_name)

        if len(matched_sections) == 0:
            structure_score = 5
            req_names = " or ".join(reqs.keys())
            issues.append(f"'{norm_type}' output missing expected domain sections (must mention {req_names}).")
            suggestions.append(f"Ensure the response includes information regarding {req_names}.")
        elif len(matched_sections) < len(reqs):
            # Partial coverage
            coverage_pct = len(matched_sections) / len(reqs)
            structure_score = int(15 + coverage_pct * 15)
            missing_str = ", ".join(missing_sections)
            suggestions.append(f"Consider also adding details on {missing_str} for a complete {norm_type} response.")

    # 4. Completeness check (Max 20 pts)
    completeness_score = 20
    is_complete, completeness_reason = _check_completeness(clean_output)
    if not is_complete:
        completeness_score = 0
        issues.append(f"Output appears incomplete: {completeness_reason}.")
        suggestions.append("Ensure the final thought concludes cleanly with terminal punctuation.")

    # Total Score calculation
    total_score = max(0, min(100, length_score + relevance_score + structure_score + completeness_score))
    passed = total_score >= 60

    return {
        "score": total_score,
        "passed": passed,
        "issues": issues,
        "suggestions": suggestions,
    }
