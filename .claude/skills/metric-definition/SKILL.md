# Metric Definition Skill

## Description

This skill produces standardized, certified metric definitions for datasets. Use this skill whenever the user asks to "define metrics", "write metric specs", "build a metric catalog", "document metrics", or "create metric definitions" for a dataset or data model.

## Trigger Phrases

Activate this skill when the user says things like:
- "Define metrics for this dataset"
- "Write metric specs"
- "Build a metric catalog"
- "Document these metrics"
- "Create metric definitions"
- "What metrics can we derive from this data?"
- "Spec out the KPIs"
- "Define the business metrics"

## Instructions

When defining metrics, produce a standardized certified definition for each metric using the format below.

### Metric Definition Template

For each metric, create a definition block with these required sections:

```
## [Metric Name]

**Definition:**
[Plain-language explanation of what this metric measures and why it matters]

**Formula:**
```
[Exact calculation formula using column names, SQL-style or mathematical notation]
```

**Source Columns:**
- `column_name` — brief description of what this column provides

**Filters & Business Rules:**
- [List any filters applied, e.g., "Only includes orders where order_status = 'completed'"]
- [List business logic, e.g., "Excludes test accounts", "Counts unique customers only"]

**Grain:**
[The level of detail — e.g., "Per order", "Per customer", "Per day"]

**Dimensions:**
[List dimensions this metric can be sliced by]
- dimension_name — description

**Caveats:**
- [Known limitations, edge cases, or interpretation warnings]
- [Data quality issues to be aware of]
- [When this metric might be misleading]
```

### Output Structure

1. **Header**: Start with a title like "# Metric Catalog: [Dataset Name]"
2. **Overview**: Brief paragraph describing the dataset and the metrics being defined
3. **Metric Definitions**: One definition block per metric, using the template above
4. **Metric Summary Table**: End with a quick-reference table:

| Metric | Type | Grain | Primary Use |
|--------|------|-------|-------------|
| Metric Name | count/sum/avg/rate/ratio | grain | one-line purpose |

### Best Practices

1. **Be precise**: Formulas should be unambiguous and reproducible
2. **Use actual column names**: Reference real columns from the dataset in backticks
3. **Explicit filters**: Always state what's included AND excluded
4. **Warn about pitfalls**: Caveats section should help users avoid misinterpretation
5. **Business context**: Definitions should be understandable by non-technical stakeholders

### Metric Types to Consider

When building a catalog, consider defining metrics across these categories:
- **Volume metrics**: Counts, totals (e.g., Total Orders, Total Revenue)
- **Financial metrics**: Revenue, costs, margins, averages (e.g., AOV, LTV)
- **Rate metrics**: Percentages, ratios (e.g., Refund Rate, Conversion Rate)
- **Time-based metrics**: Trends, cohorts, periods (e.g., Monthly Active Users)
- **Segmented metrics**: Breakdowns by dimension (e.g., Revenue by Country)

## Example Output

```markdown
# Metric Catalog: Orders Dataset

This catalog defines the certified business metrics derived from the orders dataset, covering order volume, revenue, and fulfillment metrics.

---

## Total Revenue

**Definition:**
The total monetary value of all completed orders, representing gross sales before any adjustments.

**Formula:**
```
SUM(quantity * unit_price * (1 - discount_pct/100))
WHERE order_status = 'completed'
```

**Source Columns:**
- `quantity` — number of units purchased
- `unit_price` — price per unit in USD
- `discount_pct` — discount percentage applied (0-100)
- `order_status` — fulfillment status of the order

**Filters & Business Rules:**
- Only includes orders where `order_status = 'completed'`
- Excludes refunded and cancelled orders
- Discount is applied as a percentage reduction

**Grain:**
Per order (can be aggregated to any time period)

**Dimensions:**
- `order_date` — daily, weekly, monthly trends
- `country` — geographic breakdown
- `product_category` — category performance

**Caveats:**
- Does not account for shipping costs or taxes
- Refunds processed after completion are not subtracted
- Currency is assumed to be USD for all orders

---

## Metric Summary

| Metric | Type | Grain | Primary Use |
|--------|------|-------|-------------|
| Total Revenue | sum | per order | Track gross sales performance |
```
