"""LogiFlow Feedback & Self-Correction Module.

Provides deterministic output validation, persistent lesson memory,
and feedback loop utilities for fast quality control.
"""

from .memory import LessonMemory
from .validator import validate_output, classify_query
from .loop import (
    run_feedback_check,
    record_correction,
    get_lesson_context,
    generate_critique,
    should_refine,
    memory,
)

__all__ = [
    "LessonMemory",
    "validate_output",
    "classify_query",
    "run_feedback_check",
    "record_correction",
    "get_lesson_context",
    "generate_critique",
    "should_refine",
    "memory",
]
