#!/usr/bin/env python3
"""PreToolUse hook: enforce the query guardrail on mcp__datadesk-sqlite__read_query.

Reads the hook payload on stdin, runs the SQL through guardrails.check_query(),
and DENIES the tool call (before it reaches the database) if the guardrail
rejects it. Allowed queries emit nothing, so they continue through the normal
permission flow.

Fails closed: if the guardrail module can't be loaded, the query is denied
rather than silently allowed.
"""
import json
import os
import sys

sys.path.insert(0, os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


try:
    import guardrails
except Exception as exc:  # fail closed — a missing guardrail must not mean "allow"
    deny(f"query guardrail unavailable ({exc}); blocking by default")

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # unparseable payload — let the normal flow decide

query = (payload.get("tool_input") or {}).get("query", "")
result = guardrails.check_query(query)
if not result.allowed:
    deny("Query guardrail blocked this SQL: " + "; ".join(result.reasons))

# Allowed: emit nothing so the call proceeds through normal permissions.
sys.exit(0)
