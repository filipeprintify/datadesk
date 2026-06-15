# Dataset Profiler Skill

## Description

This skill produces a standardized profile for datasets and CSV files. Use this skill whenever the user asks to "profile", "summarize", "describe", or "analyze" a dataset, data file, or CSV.

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

When profiling a dataset, always produce the following standardized output:

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
