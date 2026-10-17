# LogiFlow — Session Handoff (DevFest Chennai Agent Wars)

> **READ THIS FIRST.** This is the context file for continuing the LogiFlow build.
> Competition is LIVE. Time is limited. Execute, don't re-research.

---

## What's Happening

Maverick is at **GDG DevFest Chennai 2026** (Oct 17, IIT Madras Research Park).
He's competing in **Agent Wars** — a live tournament where AI agents compete.

**Challenge:** Build an end-to-end **Logistics Handler** agent.

**Judging criteria (in order of importance):**
1. **It must work** — shippable POC quality
2. **Speed / low latency** — fastest wins
3. **Multimodal + complexity** — more sophisticated = better
4. **Feedback loop** — MUST learn from mistakes, self-correct
5. **Efficiency** — smart architecture, not brute force
6. Novelty is secondary — function > flash

---

## Architecture: LogiFlow

Full architecture diagram is in **AGENTS.md** (same directory). Key decisions:

### Dual-Brain Architecture
- **Gemini 3.8 Flash** (Google ADK) — primary LLM for reasoning, generation
- **Jev** (TypeSafe AI) — System 1 fast decision layer (~1ms) for routing, quality gates
- **OpenAI** — available as alternative/fallback (Maverick has $4.90 in credits)

### ADK Agent Structure
- **Google ADK 2.12.0** on Python 3.13 via `uv`
- Correct imports: `from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent`
- Agents expose `root_agent` variable for `adk run` / `adk web` discovery
- Package structure: `logiflow/` with `__init__.py` that does `from . import agent`
- Tools return `dict` (ADK best practice for structured tool output)
- Shared state via `output_key` parameter on agents → `{key_name}` template vars in instructions
- `.env` file at project root is auto-loaded by ADK CLI

### Model Switch
- **Primary:** `gemini-3.8-flash` (Google, free tier: 5 req/min)
- **Alternative:** OpenAI via `gpt-4o-mini` or `gpt-4o` (Maverick has $4.90 credits)
- Implement as env var switch: `LLM_PROVIDER=google` or `LLM_PROVIDER=openai`
- Google ADK supports OpenAI-compatible models — check ADK docs for exact syntax

### Self-Correction Feedback Loop
- ADK native `LoopAgent` wraps Generate → Validate → Critique → Refine cycle
- Max 3 iterations (bounded cost/latency)
- Validator uses Jev for fast quality scoring (not another LLM call)
- Every correction logged to session state for persistent learning
- Past lessons injected into agent context on future requests

### 5 Specialist Sub-Agents
| Agent | Role |
|---|---|
| Shipment Tracker | Track, status, ETA |
| Route Planner | Route optimization, cost calc |
| Inventory Manager | Stock levels, reorder |
| Issue Resolver | Delays, damage, disputes |
| Analytics Agent | Reports, trends, KPIs |

---

## What's Already Built

### Working (verified)
- `~/ssa/devfest-agent/` — uv project, Python 3.13, google-adk 2.12.0
- `battle_agent/` — single agent mode (LlmAgent + 11 tools) ✅ tested
- `battle_multi/` — multi-agent mode (orchestrator + 4 sub-agents) ✅ tested
- `.env` — Gemini API key (working, 5 req/min free tier)
- Tools library in `battle_agent/tools.py` (web_search, fetch_url, analyze_text, extract_entities, summarize_text, calculate, process_json, run_python_code, read_file, write_file, get_current_time)

### NOT built yet (build these NOW)
- `logiflow/` — the actual competition agent package
- Logistics-specific tools (track_shipment, calculate_route, check_inventory, etc.)
- Specialist agents (tracker, planner, inventory, resolver, analytics)
- Router agent with Jev fast-path
- LoopAgent feedback cycle (validator + critique + refine)
- Jev integration layer
- Persistent memory/lessons system
- README.md with flowchart

---

## Build Order (Priority)

| # | What | File(s) | Est. Time |
|---|---|---|---|
| 1 | Domain tools | `logiflow/tools/logistics.py`, `calculation.py`, `data.py` | 20 min |
| 2 | Specialist agents | `logiflow/specialists/*.py` (5 agents) | 20 min |
| 3 | Root pipeline + router | `logiflow/agent.py`, `router.py` | 15 min |
| 4 | Feedback loop | `logiflow/feedback/validator.py`, `loop.py`, `memory.py` | 15 min |
| 5 | Jev layer | `logiflow/jev_layer.py` | 10 min |
| 6 | README + flowchart | `README.md` | 10 min |
| 7 | Test & polish | — | remaining |

---

## File Structure Target

```
~/ssa/devfest-agent/
├── logiflow/                    # ← THE COMPETITION AGENT
│   ├── __init__.py              #   from . import agent
│   ├── agent.py                 #   root_agent (SequentialAgent pipeline)
│   ├── router.py                #   Smart router (Jev fast-path + LLM fallback)
│   ├── specialists/
│   │   ├── __init__.py
│   │   ├── tracker.py           #   Shipment tracking
│   │   ├── planner.py           #   Route planning
│   │   ├── inventory.py         #   Inventory management
│   │   ├── resolver.py          #   Issue resolution
│   │   └── analytics.py         #   Analytics & reporting
│   ├── feedback/
│   │   ├── __init__.py
│   │   ├── validator.py         #   Output quality validation
│   │   ├── loop.py              #   LoopAgent feedback cycle
│   │   └── memory.py            #   Persistent lesson storage
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── logistics.py         #   Domain tools (track, route, inventory)
│   │   ├── calculation.py       #   Math, ETA, cost estimation
│   │   └── data.py              #   Data processing, JSON, file I/O
│   └── jev_layer.py             #   Jev integration (routing, quality gates)
├── battle_agent/                # (old single-agent mode, keep as reference)
├── battle_multi/                # (old multi-agent mode, keep as reference)
├── AGENTS.md                    # Architecture diagram + design doc
├── HANDOFF.md                   # THIS FILE
├── .env                         # API keys
├── pyproject.toml               # uv project config
└── README.md                    # Competition README with flowchart
```

---

## API Keys & Environment

```env
# In .env (auto-loaded by ADK)
GOOGLE_API_KEY=<already set, working>
GOOGLE_GENAI_USE_VERTEXAI=FALSE
OPENAI_API_KEY=<Maverick needs to add this>
TYPESAFE_API_KEY=<Maverick needs to get from console.typesafe.ai>
LLM_PROVIDER=google  # or "openai"
```

- **Gemini:** Free tier, 5 req/min for gemini-3.8-flash. gemini-3.1-pro-preview is PAID ONLY (zero free quota).
- **OpenAI:** $4.90 credits available. Use gpt-4o-mini for cost efficiency.
- **Jev:** Needs TypeSafe API key from console.typesafe.ai. Free tier available.

---

## ADK Quick Reference

```python
# Correct imports (ADK 2.12.0)
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

# Agent with tools
agent = LlmAgent(
    name="agent_name",           # unique identifier
    model="gemini-3.8-flash",    # or OpenAI model string
    description="What this agent does (used by parent for routing)",
    instruction="System prompt with {state_var} template vars",
    tools=[tool_fn1, tool_fn2],  # Python functions
    output_key="result_key",     # saves output to session state
)

# Multi-agent (auto-transfer)
parent = LlmAgent(
    name="parent",
    model="gemini-3.8-flash",
    instruction="Delegate to sub-agents by name...",
    sub_agents=[child1, child2],
)

# Sequential pipeline
pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[step1, step2, step3],  # runs in order
)

# Feedback loop
loop = LoopAgent(
    name="feedback_loop",
    sub_agents=[generator, validator],  # repeats until max_iterations
    max_iterations=3,
)

# Tools return dicts
def my_tool(param: str) -> dict:
    """Docstring becomes function-calling schema."""
    return {"status": "success", "data": "..."}
```

```bash
# Run commands
uv run adk run logiflow                    # interactive
uv run adk run logiflow "query here"       # single shot
uv run adk web .                           # browser UI
```

---

## Maverick's Preferences (For Doc/Lyra)
- He's Maverick. You're Doc Hudson (also Lyra).
- Be direct. No fluff. Ship quality.
- Execute mode — don't teach, just build.
- This is a TIMED COMPETITION. Speed > perfection.
- He uses uv, not pip. Python 3.13.
- Test after building. Don't ask permission to run commands.

---

## Status
- **Time:** Competition started ~12:00 PM, Agent Wars qualifiers at 12:00 PM
- **Current:** Architecture designed, need to BUILD logiflow/ package
- **Next step:** Start coding logiflow/ — tools first, then agents, then feedback loop
- **Blocker:** Maverick needs to add OPENAI_API_KEY and TYPESAFE_API_KEY to .env
