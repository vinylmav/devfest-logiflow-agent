"""LogiFlow model configuration.

Reads LLM_PROVIDER env var to select the model backend.
  LLM_PROVIDER=google  → gemini-3.8-flash (default, free tier 5 req/min)
  LLM_PROVIDER=openai  → gpt-4o-mini ($4.90 credits)
"""

import os
from pathlib import Path

# Explicitly load .env file from project root if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

_PROVIDER = os.getenv("LLM_PROVIDER", "google").lower().strip()

if _PROVIDER == "openai":
    MODEL = "gpt-4o-mini"
else:
    MODEL = "gemini-3.8-flash"
