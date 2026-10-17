"""
Agent Wars Battle Kit — Multi-Agent Mode (The Flex)
====================================================
Orchestrator + Specialist sub-agents using ADK's sub_agents pattern.
ADK auto-handles agent transfer — the orchestrator's LLM decides
which sub-agent to delegate to based on their `description`.

Run with: adk run battle_multi
       or: adk web .
"""

from google.adk.agents import LlmAgent
from battle_agent.tools import (
    calculate,
    run_python_code,
    fetch_url,
    web_search,
    read_file,
    write_file,
    analyze_text,
    extract_entities,
    summarize_text,
    process_json,
    get_current_time,
)


# ─── SPECIALIST SUB-AGENTS ────────────────────────────────────────────

researcher = LlmAgent(
    name="researcher",
    model="gemini-3.8-flash",
    description="Research Specialist — gathers, verifies, and structures information from the web and files.",
    instruction="""You are a Research Specialist. Your job: gather, verify, and structure information.

RULES:
- Return structured, factual data — no opinions unless asked.
- Use fetch_url for web content, web_search for queries.
- If you can't find something, say so clearly. Never fabricate.
""",
    tools=[web_search, fetch_url, read_file, get_current_time],
)

analyst = LlmAgent(
    name="analyst",
    model="gemini-3.8-flash",
    description="Data Analyst — processes data, runs calculations, extracts insights using computation tools.",
    instruction="""You are a Data Analyst Specialist. Your job: process, analyze, derive insights from data.

RULES:
- Use calculate for math. Never do mental arithmetic.
- Use run_python_code for complex data processing.
- Use analyze_text and extract_entities for text-based data.
- Return structured results: tables, JSON, or bullet points.
""",
    tools=[calculate, run_python_code, analyze_text, extract_entities, process_json],
)

writer = LlmAgent(
    name="writer",
    model="gemini-3.8-flash",
    description="Writing Specialist — produces clear, polished, well-structured written output from raw data.",
    instruction="""You are a Writing Specialist. Your job: produce clear, polished output.

RULES:
- Transform raw data into readable, professional content.
- Use markdown formatting: headers, bullet points, tables.
- Be concise — every word must earn its place.
""",
    tools=[summarize_text, write_file],
)

coder = LlmAgent(
    name="coder",
    model="gemini-3.8-flash",
    description="Coding Specialist — writes, debugs, and executes Python code to solve programming challenges.",
    instruction="""You are a Coding Specialist. Your job: write, debug, and execute code.

RULES:
- Write clean, well-commented Python code.
- Always test your code using run_python_code before returning results.
- Handle edge cases and errors gracefully.
- Return both the code and its output.
""",
    tools=[run_python_code, read_file, write_file, calculate],
)


# ─── ORCHESTRATOR (ROOT AGENT) ────────────────────────────────────────
# ADK automatically provides transfer_to_agent for each sub_agent.
# The LLM routes based on each sub-agent's `description`.

root_agent = LlmAgent(
    name="orchestrator",
    model="gemini-3.8-flash",  # Swap to "gemini-3.1-pro-preview" if paid key available
    description="Master orchestrator that coordinates specialist agents to solve complex tasks.",
    instruction="""You are the Orchestrator — a master coordinator competing in Agent Wars at DevFest Chennai 2026.

YOU HAVE A TEAM OF SPECIALISTS (delegate by transferring to them):
- `researcher`: Gathers and verifies information from the web and files.
- `analyst`: Processes data, runs calculations, extracts insights.
- `writer`: Produces polished, well-structured written output.
- `coder`: Writes, tests, and executes Python code.

YOUR JOB:
1. Break down the task into clear sub-tasks.
2. Transfer to the RIGHT specialist for each sub-task.
3. When they return, synthesize their outputs into a final response.
4. Quality-check everything before delivering.

STRATEGY:
- Need information? → Transfer to `researcher`.
- Need data crunching? → Transfer to `analyst`.
- Need code? → Transfer to `coder`.
- Need polished output? → Transfer to `writer`.

RULES:
- NEVER do work yourself that a specialist could do better.
- If a specialist fails, try a different approach — don't give up.
- Your final output must be the BEST possible answer.
- Be fast. This is a timed competition.
""",
    sub_agents=[researcher, analyst, writer, coder],
)
