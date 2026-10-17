"""
Battle-ready tool library for Agent Wars @ DevFest Chennai 2026.

Every tool returns a dict (ADK best practice for structured tool output).
Proper docstrings + type hints → ADK auto-generates function-calling schemas.
"""

import json
import subprocess
import re
import math
import urllib.request
import urllib.parse
from datetime import datetime


# ─── Web & Information ─────────────────────────────────────────────────

def web_search(query: str) -> dict:
    """Search the web for information on a given topic.

    Args:
        query: The search query string.

    Returns:
        A dict with the search query and guidance to use training knowledge.
    """
    return {
        "status": "success",
        "query": query,
        "note": "Use your training knowledge to provide the best answer for this query.",
    }


def fetch_url(url: str) -> dict:
    """Fetch and return the text content from a given URL.

    Args:
        url: The URL to fetch content from.

    Returns:
        A dict with the fetched content or an error message.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        clean = re.sub(r"<[^>]+>", " ", content)
        clean = re.sub(r"\s+", " ", clean).strip()
        return {"status": "success", "url": url, "content": clean[:5000]}
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}


# ─── Text Processing ──────────────────────────────────────────────────

def analyze_text(text: str) -> dict:
    """Analyze text and return statistics: word count, sentence count,
    character count, average lengths, and most common words.

    Args:
        text: The text to analyze.

    Returns:
        A dict with text statistics.
    """
    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_freq: dict[str, int] = {}
    for w in words:
        w_clean = re.sub(r"[^a-zA-Z]", "", w.lower())
        if len(w_clean) > 2:
            word_freq[w_clean] = word_freq.get(w_clean, 0) + 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "character_count": len(text),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        "top_words": dict(top_words),
    }


def extract_entities(text: str) -> dict:
    """Extract named entities (emails, URLs, dates, numbers, capitalized phrases)
    from text using regex pattern matching.

    Args:
        text: The text to extract entities from.

    Returns:
        A dict with categorized entities.
    """
    return {
        "emails": re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text),
        "urls": re.findall(r"https?://[^\s<>\"']+", text),
        "dates": re.findall(
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
            r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s*\d{4}\b",
            text,
        ),
        "numbers": re.findall(r"\b\d+\.?\d*\b", text)[:20],
        "capitalized_phrases": re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text),
    }


def summarize_text(text: str, max_sentences: int = 3) -> dict:
    """Create an extractive summary by selecting the most important sentences
    based on word frequency scoring.

    Args:
        text: The text to summarize.
        max_sentences: Maximum number of sentences in the summary.

    Returns:
        A dict with the summary text.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if len(sentences) <= max_sentences:
        return {"summary": " ".join(sentences)}

    all_words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq: dict[str, int] = {}
    for w in all_words:
        freq[w] = freq.get(w, 0) + 1

    scored = []
    for i, sent in enumerate(sentences):
        words = re.findall(r"\b[a-zA-Z]{3,}\b", sent.lower())
        score = sum(freq.get(w, 0) for w in words) / max(len(words), 1)
        if i < 2:
            score *= 1.5
        scored.append((score, i, sent))

    scored.sort(reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[1])
    return {"summary": " ".join(s[2] for s in top)}


# ─── Data & Computation ───────────────────────────────────────────────

def calculate(expression: str) -> dict:
    """Safely evaluate a mathematical expression.

    Args:
        expression: A math expression string (e.g., '2 * (3 + 4)', 'sqrt(144)').

    Returns:
        A dict with the expression and its result, or an error.
    """
    safe_ns: dict = {
        "__builtins__": {},
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "len": len, "pow": pow,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "log2": math.log2,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e, "ceil": math.ceil, "floor": math.floor,
    }
    try:
        result = eval(expression, safe_ns)
        return {"status": "success", "expression": expression, "result": result}
    except Exception as e:
        return {"status": "error", "expression": expression, "error": str(e)}


def process_json(json_string: str, operation: str = "prettify") -> dict:
    """Process JSON data — parse, validate, prettify, extract keys, or flatten.

    Args:
        json_string: The JSON string to process.
        operation: One of 'prettify', 'validate', 'keys', 'flatten'.

    Returns:
        A dict with the processed output or an error.
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON: {e}"}

    if operation == "validate":
        return {"status": "success", "valid": True, "type": type(data).__name__}
    elif operation == "keys":
        if isinstance(data, dict):
            return {"status": "success", "keys": list(data.keys())}
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return {"status": "success", "keys": list(data[0].keys())}
        return {"status": "error", "error": "Cannot extract keys from this type."}
    elif operation == "flatten":
        flat: dict = {}

        def _flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _flatten(v, f"{prefix}{k}.")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _flatten(v, f"{prefix}{i}.")
            else:
                flat[prefix.rstrip(".")] = obj

        _flatten(data)
        return {"status": "success", "flattened": flat}
    else:
        return {"status": "success", "prettified": json.dumps(data, indent=2)}


# ─── Code Execution ───────────────────────────────────────────────────

def run_python_code(code: str) -> dict:
    """Execute Python code in a subprocess and return the output.

    Args:
        code: Python code to execute.

    Returns:
        A dict with stdout, stderr, and return code.
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
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ─── File I/O ──────────────────────────────────────────────────────────

def read_file(filepath: str) -> dict:
    """Read and return the contents of a file.

    Args:
        filepath: Path to the file to read.

    Returns:
        A dict with file contents or an error.
    """
    try:
        with open(filepath) as f:
            content = f.read()
        truncated = len(content) > 10000
        return {
            "status": "success",
            "filepath": filepath,
            "content": content[:10000],
            "truncated": truncated,
            "total_chars": len(content),
        }
    except Exception as e:
        return {"status": "error", "filepath": filepath, "error": str(e)}


def write_file(filepath: str, content: str) -> dict:
    """Write content to a file, creating it if it doesn't exist.

    Args:
        filepath: Path to the file to write.
        content: The content to write.

    Returns:
        A dict confirming the write or an error.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return {"status": "success", "filepath": filepath, "chars_written": len(content)}
    except Exception as e:
        return {"status": "error", "filepath": filepath, "error": str(e)}


def get_current_time() -> dict:
    """Get the current date and time.

    Returns:
        A dict with the current datetime.
    """
    now = datetime.now()
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "day": now.strftime("%A"),
        "iso": now.isoformat(),
    }


# ─── Tool Registries ──────────────────────────────────────────────────

ALL_TOOLS = [
    web_search, fetch_url,
    analyze_text, extract_entities, summarize_text,
    calculate, process_json, run_python_code,
    read_file, write_file, get_current_time,
]

TEXT_TOOLS = [analyze_text, extract_entities, summarize_text]
DATA_TOOLS = [calculate, process_json, run_python_code]
IO_TOOLS = [web_search, fetch_url, read_file, write_file, get_current_time]
