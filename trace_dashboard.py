"""Agent Trace Dashboard — inspect agent/tool activity logged to traces/agent-runs.jsonl.

Run with:
    .venv/bin/streamlit run trace_dashboard.py

Reads the structured trace written by the PostToolUse / SubagentStop hooks and lets you:
- browse recent runs (timestamp, tool/agent, status, result preview),
- filter by tool/agent and by success/failure (where the tool's result exposes it),
- click a run to see its full input and output.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
# Prefer the live local trace (gitignored); fall back to the committed sample so
# the dashboard has something to show on Streamlit Cloud, where the live file
# doesn't exist.
LIVE_PATH = PROJECT_DIR / "traces" / "agent-runs.jsonl"
SAMPLE_PATH = PROJECT_DIR / "traces_sample.jsonl"


def resolve_source() -> tuple[Path | None, str]:
    if LIVE_PATH.exists() and LIVE_PATH.stat().st_size > 0:
        return LIVE_PATH, "live"
    if SAMPLE_PATH.exists() and SAMPLE_PATH.stat().st_size > 0:
        return SAMPLE_PATH, "sample"
    return None, "none"


# --- Data loading ----------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_runs(path_str: str, mtime: float) -> list[dict]:
    """Load trace records, newest first. `mtime` busts the cache when the file changes."""
    runs: list[dict] = []
    with open(path_str, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                rec = {"_malformed": True, "raw": line}
            rec["_line"] = i + 1
            runs.append(rec)
    runs.reverse()  # most recent first
    return runs


# --- Derivations -----------------------------------------------------------

def tool_label(rec: dict) -> str:
    """Display name: the tool, or 'Agent → <subagent>' for subagent dispatches."""
    tool = rec.get("tool")
    if tool == "Agent":
        sub = (rec.get("input") or {}).get("subagent_type")
        return f"Agent → {sub}" if sub else "Agent"
    if not tool:
        return rec.get("event", "—")
    return tool


def status_of(rec: dict) -> str:
    """Best-effort success/failure, from whatever the tool's result exposes."""
    result = rec.get("result")
    if result is None:
        return "—"  # e.g. SubagentStop markers carry no result
    if isinstance(result, dict):
        if "success" in result:                       # Skill
            return "success" if result["success"] else "failure"
        if "status" in result:                        # Agent
            return "success" if str(result["status"]).lower() in ("completed", "success", "ok") else "failure"
        if result.get("interrupted"):                 # Bash
            return "failure"
        if result.get("is_error") or result.get("error"):
            return "failure"
    return "success"  # PostToolUse only fires on successful tool completion


def result_preview(rec: dict, limit: int = 140) -> str:
    """A short, human-readable one-liner for the result."""
    result = rec.get("result")
    if result is None:
        return ""
    text = None
    if isinstance(result, dict):
        # Agent results: content is a list of {type, text}
        content = result.get("content")
        if isinstance(content, list):
            text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        elif "stdout" in result:                      # Bash
            text = result.get("stdout") or result.get("stderr") or ""
        elif "numFiles" in result:                    # Glob
            text = f"{result.get('numFiles')} files"
        elif "file" in result:                        # Read
            text = str(result.get("file"))
    if text is None:
        text = json.dumps(result, ensure_ascii=False)
    text = " ".join(text.split())  # collapse whitespace/newlines
    return text[:limit] + ("…" if len(text) > limit else "")


# --- UI --------------------------------------------------------------------

st.set_page_config(page_title="Agent Trace Dashboard", page_icon="🛰️", layout="wide")
st.title("🛰️ Agent Trace Dashboard")

source_path, source_kind = resolve_source()
if source_path is None:
    st.warning(
        "No trace data found. The live trace `traces/agent-runs.jsonl` is created "
        "by the PostToolUse/SubagentStop hooks once agents run, and a committed "
        "`traces_sample.jsonl` provides demo data on deploys."
    )
    st.stop()

runs = load_runs(str(source_path), source_path.stat().st_mtime)
if not runs:
    st.info("Trace file is empty — run an agent or tool and refresh.")
    st.stop()

if source_kind == "sample":
    st.info(
        "Showing the committed **sample** trace (`traces_sample.jsonl`) — no live "
        "`traces/agent-runs.jsonl` present. On your machine, the live trace is used automatically."
    )

# Pre-compute derived fields once.
for r in runs:
    r["_label"] = tool_label(r)
    r["_status"] = status_of(r)
    r["_preview"] = result_preview(r)

# Sidebar: filters
st.sidebar.header("Filters")
if st.sidebar.button("🔄 Refresh", width="stretch"):
    st.cache_data.clear()
    st.rerun()

all_labels = sorted({r["_label"] for r in runs})
all_statuses = sorted({r["_status"] for r in runs})
sel_labels = st.sidebar.multiselect("Tool / agent", all_labels, default=all_labels)
sel_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)
query = st.sidebar.text_input("Search (input/result text)", "")

filtered = [
    r for r in runs
    if r["_label"] in sel_labels
    and r["_status"] in sel_statuses
    and (query.lower() in json.dumps(r, ensure_ascii=False).lower() if query else True)
]

# Top-line metrics
c1, c2, c3 = st.columns(3)
c1.metric("Runs (filtered)", f"{len(filtered)} / {len(runs)}")
c2.metric("Tools / agents", len(all_labels))
c3.metric("Failures", sum(1 for r in runs if r["_status"] == "failure"))

st.caption(
    "Status is derived from each tool's result where available "
    "(Skill `success`, Agent `status`, Bash `interrupted`); other successful "
    "calls show **success** and markers without a result show **—**."
)

if not filtered:
    st.info("No runs match the current filters.")
    st.stop()

# Runs table (most recent first). Click a row to inspect it.
table = [
    {"Time": r.get("ts", ""), "Tool / agent": r["_label"], "Status": r["_status"], "Result preview": r["_preview"]}
    for r in filtered
]
st.subheader("Recent runs")
event = st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    on_select="rerun",
    selection_mode="single-row",
    key="runs_table",
)

# Detail view for the selected run
sel_rows = event.selection["rows"] if event and event.selection else []
if sel_rows:
    rec = filtered[sel_rows[0]]
    st.subheader("Run detail")
    d1, d2, d3 = st.columns(3)
    d1.markdown(f"**Time:** {rec.get('ts','—')}")
    d2.markdown(f"**Tool / agent:** {rec['_label']}")
    d3.markdown(f"**Status:** {rec['_status']}")
    st.caption(f"event: `{rec.get('event','—')}` · session: `{rec.get('session','—')}` · line {rec.get('_line','?')}")

    st.markdown("**Input**")
    st.json(rec.get("input"))
    st.markdown("**Output / result**")
    st.json(rec.get("result"))
else:
    st.info("Select a row above to see its full input and output.")
