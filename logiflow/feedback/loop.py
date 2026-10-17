"""Feedback loop utilities for LogiFlow.
Provides the generate-validate-critique-refine cycle.
"""

from typing import Any
from .validator import validate_output, classify_query
from .memory import LessonMemory

# Global lesson memory instance for feedback loop operations
memory = LessonMemory()


def run_feedback_check(query: str, output: str) -> dict[str, Any]:
    """Run a single feedback check on agent output.

    Classifies query, validates output against expected structure and quality,
    and retrieves relevant past lessons learned.

    Args:
        query: The user's original query.
        output: The agent's generated output text.

    Returns:
        dict with:
            - passed (bool): True if quality score >= 60.
            - score (int): Numeric score (0-100).
            - query_type (str): Classified category ('tracking', 'route', etc.).
            - issues (list[str]): Identified issues.
            - suggestions (list[str]): Actionable suggestions.
            - relevant_lessons (list[dict]): Historical corrections for similar queries.
    """
    query_type = classify_query(query)
    validation = validate_output(output, query, query_type)
    lessons = memory.get_relevant_lessons(query)

    return {
        "passed": validation["passed"],
        "score": validation["score"],
        "query_type": query_type,
        "issues": validation["issues"],
        "suggestions": validation["suggestions"],
        "relevant_lessons": lessons,
    }


def record_correction(query: str, original: str, corrected: str, reason: str) -> dict[str, Any]:
    """Record a correction for future learning.

    Args:
        query: The original user query.
        original: The faulty output.
        corrected: The improved output.
        reason: Explanation of what was corrected.

    Returns:
        Created lesson record dictionary.
    """
    return memory.add_lesson(query, original, corrected, reason)


def get_lesson_context(query: str) -> str:
    """Get formatted lesson context for prompt injection.

    Args:
        query: Current user query.

    Returns:
        Formatted lesson string for prompt injection, or 'No relevant past lessons.'
    """
    return memory.format_for_prompt(query)


def generate_critique(feedback_result: dict[str, Any]) -> str:
    """Generate actionable critique text from feedback check results.

    Used by refinement agents to understand what needs improvement.

    Args:
        feedback_result: Dictionary returned from run_feedback_check.

    Returns:
        Critique string detailing issues, suggestions, and historical lessons.
    """
    if feedback_result.get("passed", False):
        return "Output meets quality standards. No revision required."

    critique_sections: list[str] = [
        f"Validation Score: {feedback_result.get('score', 0)}/100 (FAIL)"
    ]

    issues = feedback_result.get("issues", [])
    if issues:
        critique_sections.append("Issues Found:\n" + "\n".join(f"- {i}" for i in issues))

    suggestions = feedback_result.get("suggestions", [])
    if suggestions:
        critique_sections.append("Recommended Corrections:\n" + "\n".join(f"- {s}" for s in suggestions))

    relevant_lessons = feedback_result.get("relevant_lessons", [])
    if relevant_lessons:
        critique_sections.append(
            "Relevant Past Corrections:\n"
            + "\n".join(
                f"- When query was '{l.get('query')}': '{l.get('correction')}' (Reason: {l.get('reason')})"
                for l in relevant_lessons
            )
        )

    return "\n\n".join(critique_sections)


def should_refine(feedback_result: dict[str, Any]) -> bool:
    """Check if feedback result indicates refinement is required.

    Args:
        feedback_result: Output from run_feedback_check.

    Returns:
        True if the output failed quality checks, False otherwise.
    """
    return not feedback_result.get("passed", True)
