"""Deterministic guardrails for the data-analyst flow.

These are enforced in code, not prompts — they do not call an LLM and give the
same verdict every time. Two layers:

- `check_query()`  — an INPUT guardrail: only allows read-only single-statement
  SELECTs against the approved tables (orders, customers); rejects anything
  destructive (DELETE/DROP/UPDATE/…), multi-statement, or out-of-scope.
- `check_output()` — an OUTPUT guardrail: flags answers that are not grounded
  in a certified definition or a computed figure (i.e. likely fabricated).

Note: query parsing uses dependency-free regex normalization. For a hardened
production deployment a real SQL parser (e.g. sqlglot) is recommended; the regex
checks here defend against the common destructive / out-of-scope cases and the
adversarial tricks in the test harness.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

APPROVED_TABLES = {"orders", "customers"}

# Statement types / actions that must never run through the read-only analyst.
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE",
    "TRUNCATE", "MERGE", "UPSERT", "INTO", "ATTACH", "DETACH", "PRAGMA",
    "VACUUM", "REINDEX", "GRANT", "REVOKE", "EXEC", "EXECUTE",
]
_FORBIDDEN_RE = re.compile(r"\b(" + "|".join(FORBIDDEN_KEYWORDS) + r")\b", re.I)

# Clause keywords that terminate a FROM list when extracting table names.
_FROM_TERMINATORS = r"\bWHERE\b|\bGROUP\b|\bORDER\b|\bHAVING\b|\bLIMIT\b|\bJOIN\b|\bON\b|\bUNION\b|\)|$"


@dataclass
class GuardrailResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        return "PASS" if self.allowed else "BLOCK"


# --- Query normalization helpers ------------------------------------------

def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)   # block comments
    sql = re.sub(r"--[^\n]*", " ", sql)                # line comments
    return sql


def _blank_string_literals(sql: str) -> str:
    """Replace '...' string literals with '' so keywords inside data aren't matched."""
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def _split_statements(sql: str) -> list[str]:
    return [s.strip() for s in sql.split(";") if s.strip()]


def _extract_tables(sql: str) -> list[str]:
    """Best-effort table names referenced by FROM/JOIN, incl. comma-joins."""
    tables: list[str] = []
    for m in re.finditer(r"\bFROM\b(.*?)(?=" + _FROM_TERMINATORS + r")", sql, re.I | re.S):
        for part in m.group(1).split(","):
            toks = part.strip().split()
            if toks and not toks[0].startswith("("):
                tables.append(toks[0])
    for m in re.finditer(r"\bJOIN\s+([^\s(]+)", sql, re.I):
        tables.append(m.group(1))
    norm = []
    for t in tables:
        t = t.strip().strip('`"[]').split(".")[-1].lower()  # drop quotes & schema prefix
        if t and not t.startswith("("):
            norm.append(t)
    return norm


# --- INPUT guardrail -------------------------------------------------------

def check_query(sql: str) -> GuardrailResult:
    """Allow only a read-only single-statement SELECT over approved tables."""
    reasons: list[str] = []
    if not sql or not sql.strip():
        return GuardrailResult(False, ["empty query"])

    no_comments = _strip_comments(sql)
    statements = _split_statements(no_comments)

    if len(statements) == 0:
        return GuardrailResult(False, ["no executable statement (only comments?)"])
    if len(statements) > 1:
        return GuardrailResult(
            False,
            [f"multiple statements not allowed ({len(statements)} found)"],
            {"statements": statements},
        )

    stmt = statements[0]
    scan = _blank_string_literals(stmt)  # for keyword checks, ignore string contents

    # 1) Must be a SELECT.
    if not re.match(r"^\s*SELECT\b", scan, re.I):
        first = (scan.strip().split() or ["?"])[0].upper()
        reasons.append(f"only SELECT is allowed (statement starts with '{first}')")

    # 2) No destructive / DDL / DML keywords anywhere.
    forbidden_found = sorted({m.group(1).upper() for m in _FORBIDDEN_RE.finditer(scan)})
    if forbidden_found:
        reasons.append(f"forbidden keyword(s): {', '.join(forbidden_found)}")

    # 3) Every referenced table must be approved.
    tables = _extract_tables(scan)
    disallowed = sorted({t for t in tables if t not in APPROVED_TABLES})
    if disallowed:
        reasons.append(f"out-of-scope table(s): {', '.join(disallowed)}")

    allowed = not reasons
    return GuardrailResult(
        allowed,
        reasons or ["read-only SELECT over approved tables"],
        {"tables": sorted(set(tables))},
    )


# --- OUTPUT guardrail ------------------------------------------------------

_SQL_EVIDENCE_RE = re.compile(r"\bSELECT\b[\s\S]{0,4000}?\bFROM\b", re.I)
_CITATION_RE = re.compile(r"docs/(?:orders|customers)\.md|\bcertified\b|definition used", re.I)
_NUMBER_RE = re.compile(r"\d")


def check_output(answer: str) -> GuardrailResult:
    """Flag answers not grounded in a certified definition or a computed figure."""
    text = answer or ""
    has_sql = bool(_SQL_EVIDENCE_RE.search(text))
    has_number = bool(_NUMBER_RE.search(text))
    has_citation = bool(_CITATION_RE.search(text))

    grounded_certified = has_citation
    grounded_computed = has_sql and has_number

    reasons: list[str] = []
    if not (grounded_certified or grounded_computed):
        if not has_citation:
            reasons.append("no certified-definition citation (e.g. docs/*.md, 'certified', 'Definition used')")
        if not has_sql:
            reasons.append("no computed figure shown (no SQL query in the answer)")
        elif not has_number:
            reasons.append("SQL present but no numeric figure reported")

    passed = grounded_certified or grounded_computed
    return GuardrailResult(
        passed,
        reasons or ["grounded in a certified definition and/or a computed figure"],
        {"has_sql": has_sql, "has_number": has_number, "has_citation": has_citation},
    )
