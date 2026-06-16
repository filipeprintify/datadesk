---
name: prd-writer
description: >-
  Use this skill whenever the user asks to write a PRD or product requirements
  document — e.g. "write a PRD for X", "draft a product requirements doc", "spec
  out this feature as a PRD", "turn this idea into a PRD". It produces a PRD in a
  consistent structure (problem statement; background & context; goals & success
  metrics; scope, in and out; key requirements; risks & open questions; appendix
  of supporting data). Its non-negotiable rule: every quantitative claim in the
  PRD must be backed by a real figure computed from our data, never invented or
  estimated.
---

# PRD Writer Skill

## Description

This skill produces a Product Requirements Document (PRD) in a single,
consistent structure. Use it whenever the user asks to write, draft, or spec a
PRD or product requirements document for a feature, product, or initiative.

## Trigger Phrases

Activate this skill when the user says things like:

- "Write a PRD for [feature/product]"
- "Draft a product requirements document"
- "Spec this out as a PRD"
- "Turn this idea into a PRD"
- "Create a requirements doc for [X]"
- "I need a PRD covering [X]"

## Non-Negotiable Rule: Every Number Must Be Real

**Any quantitative claim in the PRD MUST be backed by a real figure from our
data. Never invent, estimate, guess, or use a placeholder number.**

This applies to every count, percentage, revenue figure, growth rate, average,
benchmark, target, or any other number that asserts a fact about our data,
users, or business.

- **Compute it.** Derive the figure from the actual data — query the project's
  SQLite database (`datadesk-sqlite` via MCP / `datadesk.db`) with SQL, cite a
  certified metric definition from `docs/`, or use the `data-analyst` agent to
  compute it. Report only values that came back from real data.
- **Cite the source.** Every number in the PRD must name where it came from
  (e.g. "9,226.74 net revenue on completed orders — `orders` table, computed
  2026-06-16" or "per the certified AOV metric in `docs/orders.md`"). Put the
  supporting query or reference in the Appendix.
- **If a figure is not available, do NOT fabricate one.** State the gap
  explicitly: put it in **Open Questions** as a number to be sourced, or write
  "[figure needed: …]". An honest gap is required; an invented number is
  forbidden.
- **Targets and goals must be grounded too.** A success metric like "increase
  X by 20%" must reference the real current baseline it is measured against; if
  the baseline is unknown, flag it rather than picking a number.

A PRD that contains an unsourced or estimated number has failed this skill's
core requirement.

## Instructions

When writing a PRD, always produce the following sections in this order.

### 1. Problem Statement
A concise statement of the problem being solved and who has it. One short
paragraph. Avoid solutioning here — describe the problem, not the feature.

### 2. Background & Context
Why this matters now: relevant history, current behavior, and the data that
motivates the work. Quantitative context here must follow the Non-Negotiable
Rule (real, cited figures).

### 3. Goals & Success Metrics
- **Goals:** the outcomes this work should achieve (bulleted).
- **Success metrics:** how success is measured. Each metric should name the
  current baseline (a real, cited figure) and the target. If a baseline cannot
  be sourced from the data, flag it in Open Questions rather than inventing one.
- **Non-goals (optional):** outcomes explicitly not being pursued.

### 4. Scope
Two clearly separated lists:
- **In scope:** what this work will deliver.
- **Out of scope:** what it explicitly will not do (to prevent scope creep).

### 5. Key Requirements
The core requirements, as a numbered or bulleted list. Where useful, mark
priority (e.g. P0/P1/P2 or Must/Should/Could). Keep each requirement
testable and unambiguous.

### 6. Risks & Open Questions
- **Risks:** what could go wrong and the rough likelihood/impact.
- **Open questions:** unresolved decisions and **any figures that still need to
  be sourced from the data** (per the Non-Negotiable Rule).

### 7. Appendix: Supporting Data
The evidence base for every quantitative claim in the document. For each figure
cited above, include the value, its source (table/metric/doc), and the exact
SQL query or reference used to obtain it, so the numbers are reproducible.

## Output Format

Use GitHub-flavored markdown. Start with a title (`# PRD: <name>`) and a short
metadata line (author, date, status). Use `##` for each of the seven sections
above, in order. Keep prose tight; prefer bullets and tables over long
paragraphs. Format numbers readably (thousands separators, currency,
percentages) and keep each one traceable to the Appendix.

## Example Structure

```markdown
# PRD: <Feature Name>

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Status:** Draft

## Problem Statement
<one paragraph>

## Background & Context
<why now; cited figures only>

## Goals & Success Metrics
**Goals**
- <goal>

**Success Metrics**
| Metric | Current baseline (sourced) | Target |
|--------|----------------------------|--------|
| <metric> | <real figure + source> | <target> |

## Scope
**In scope**
- <item>

**Out of scope**
- <item>

## Key Requirements
1. **[P0]** <requirement>
2. **[P1]** <requirement>

## Risks & Open Questions
**Risks**
- <risk>

**Open Questions**
- <question / figure still to be sourced>

## Appendix: Supporting Data
| Claim | Value | Source | Query / reference |
|-------|-------|--------|-------------------|
| <claim> | <value> | <table/metric/doc> | <SQL or citation> |
```
