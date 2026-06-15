# Dataset Profiler Skill

## Description

This skill produces a standardized profile for datasets and CSV files. Use this skill whenever the user asks to "profile", "summarize", "describe", or "analyze" a dataset, data file, or CSV.

## Non-Negotiable Rule: Compute, Never Estimate

**Every figure in the profile MUST be computed by running actual code against the file. Never estimate, eyeball, or infer a number from reading the data.**

This applies to all of: row counts, column counts, missing/null counts, unique/distinct counts, minimums, maximums, sums, averages, medians, category counts, and percentages.

- Run real code (e.g. a Bash one-liner, an `awk`/`sort`/`uniq` pipeline, or a Python/`pandas` script) against the file to derive each value.
- Report ONLY values that came back from that code. If a number was not computed, it does not go in the profile.
- Percentages must be calculated from the computed counts, not approximated.
- Never sample the first N rows and extrapolate to the whole file — every count, sum, and breakdown must reflect the complete dataset.
- If you cannot execute code against the file for some reason, STOP and say so explicitly. Do not fill in estimated or placeholder figures.

Estimating from a visual scan of the data is the primary cause of profiling errors (wrong counts, percentages that don't sum to 100%) and is strictly prohibited.

## Trigger Phrases

Activate this skill when the user says things like:
- "Profile this dataset"
- "Summarize the CSV"
- "Describe this data file"
- "What's in this dataset?"
- "Give me a profile of [filename]"
- "Analyze this CSV"
- "Tell me about this data"

## Instructions

When profiling a dataset, always produce the following standardized output. Per the **Non-Negotiable Rule** above, every count, percentage, unique value, range, sum, average, and breakdown below must be produced by running code against the file — report only computed values, never estimates.

### 1. Dataset Overview
State the total number of rows (excluding header) and columns.

### 2. Column Summary Table

Create a markdown table with these columns:

| Column | Data Type | Missing | Unique | Example Values |
|--------|-----------|---------|--------|----------------|

For each column:
- **Data Type**: Infer the type (string, integer, float, date, boolean, categorical)
- **Missing**: Count of null/empty values
- **Unique**: Count of distinct values
- **Example Values**: Show 3 representative examples in backticks

### 3. Numeric Ranges Table

For all numeric columns, create a table showing:

| Column | Min | Max |
|--------|-----|-----|

Format large numbers with commas. Include decimals where appropriate.

### 4. Categorical/Status Breakdown

For any column that appears to be a status field or has low cardinality (< 15 unique values), provide a breakdown:

| Value | Count | Percentage |
|-------|-------|------------|

Calculate percentages to one decimal place.

### 5. Notes Section

End with a short "Additional Notes" section highlighting:
- Date ranges (if date columns exist)
- Notable patterns (e.g., repeat customers, skewed distributions)
- Data quality observations
- Any anomalies detected

## Output Format

Use GitHub-flavored markdown with clear section headers (###). Keep tables clean and aligned. Use backticks for example values in the column summary.

## Example Output Structure

```
## Dataset Profile: [filename]

**Total Rows:** X (excluding header)

### Column Summary

| Column | Data Type | Missing | Unique | Example Values |
|--------|-----------|---------|--------|----------------|
| col1   | string    | 0       | 50     | `val1`, `val2`, `val3` |

### Numeric Ranges

| Column | Min | Max |
|--------|-----|-----|
| amount | 0   | 100 |

### [Category Column] Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| A     | 30    | 60.0%      |

### Additional Notes
- Date range: ...
- Notable patterns: ...
```
