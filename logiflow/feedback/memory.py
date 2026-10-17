"""Persistent lesson memory for LogiFlow's self-correction system.
Stores lessons learned from corrections so mistakes aren't repeated.
"""

import json
import os
import re
from datetime import datetime
from typing import Any

LESSON_FILE = os.path.join(os.path.dirname(__file__), ".lessons.json")

# Stop words to ignore during query tokenization
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
    "yours", "yourself", "yourselves", "please", "tell", "show", "give", "check"
}


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase keywords, removing stop words."""
    if not text:
        return set()
    tokens = re.findall(r"\b[a-zA-Z0-9_\-#]{2,}\b", text.lower())
    return {t for t in tokens if t not in STOP_WORDS}


class LessonMemory:
    """Stores and retrieves lessons learned from agent self-correction cycles."""

    def __init__(self, filepath: str = LESSON_FILE):
        self.filepath = filepath
        self.lessons: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load lessons from disk."""
        if not os.path.exists(self.filepath):
            self.lessons = []
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.lessons = data
                else:
                    self.lessons = []
        except (json.JSONDecodeError, OSError):
            self.lessons = []

    def _save(self) -> None:
        """Persist lessons to disk."""
        dirname = os.path.dirname(os.path.abspath(self.filepath))
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.lessons, f, indent=2, ensure_ascii=False)

    def add_lesson(self, query: str, original_output: str, correction: str, reason: str) -> dict[str, Any]:
        """Record a lesson learned from a correction.

        Args:
            query: The original user query.
            original_output: The faulty output produced before correction.
            correction: The corrected output or guidance.
            reason: Why the original output failed or required correction.

        Returns:
            The created lesson record dictionary.
        """
        lesson = {
            "id": f"lesson_{len(self.lessons) + 1}_{int(datetime.now().timestamp() * 1000)}",
            "query": (query or "").strip(),
            "original_output": (original_output or "").strip(),
            "correction": (correction or "").strip(),
            "reason": (reason or "").strip(),
            "timestamp": datetime.now().isoformat(),
        }
        self.lessons.append(lesson)
        self._save()
        return lesson

    def get_relevant_lessons(self, query: str, max_lessons: int = 3) -> list[dict[str, Any]]:
        """Retrieve lessons relevant to a query using keyword overlap.

        1. Tokenizes both the query and stored lesson queries.
        2. Scores by word overlap (prioritizing query matches, then reason matches).
        3. Returns top N matches with score > 0.

        Args:
            query: The incoming query to match against.
            max_lessons: Maximum number of lessons to return.

        Returns:
            List of matching lesson dictionaries, sorted by relevance descending.
        """
        if not query or not self.lessons:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scored_lessons: list[tuple[float, dict[str, Any]]] = []

        for lesson in self.lessons:
            lesson_query_tokens = _tokenize(lesson.get("query", ""))
            lesson_reason_tokens = _tokenize(lesson.get("reason", ""))

            # Calculate overlap score
            query_overlap = len(query_tokens & lesson_query_tokens)
            reason_overlap = len(query_tokens & lesson_reason_tokens)

            # Query token overlap weighted 3x over reason overlap
            total_score = (query_overlap * 3.0) + (reason_overlap * 1.0)

            if total_score > 0:
                scored_lessons.append((total_score, lesson))

        # Sort descending by score
        scored_lessons.sort(key=lambda item: item[0], reverse=True)

        return [item[1] for item in scored_lessons[:max_lessons]]

    def format_for_prompt(self, query: str) -> str:
        """Format relevant lessons as a string for injection into agent prompts.

        Args:
            query: Current user query.

        Returns:
            Formatted string of lessons or 'No relevant past lessons.'
        """
        lessons = self.get_relevant_lessons(query)
        if not lessons:
            return "No relevant past lessons."

        lines: list[str] = []
        for lesson in lessons:
            q = lesson.get("query", "").strip()
            c = lesson.get("correction", "").strip()
            r = lesson.get("reason", "").strip()
            lines.append(f'- Previously, when asked about "{q}", the correction was: "{c}" (Reason: {r})')

        return "\n".join(lines)

    def get_stats(self) -> dict[str, Any]:
        """Return memory statistics.

        Returns:
            Dictionary with lesson counts, file status, and timestamp.
        """
        return {
            "total_lessons": len(self.lessons),
            "filepath": self.filepath,
            "exists": os.path.exists(self.filepath),
            "last_updated": self.lessons[-1]["timestamp"] if self.lessons else None,
        }

    def clear(self) -> None:
        """Clear all stored lessons and update disk storage."""
        self.lessons = []
        self._save()
