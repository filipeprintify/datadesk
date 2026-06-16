# Data-Analyst Evaluation Set

Ground-truth evaluation questions for the `data-analyst` agent. Every expected
answer was **computed directly from `datadesk.db` with SQL** (not estimated), so
each row is true ground truth. Use this to check that the agent (1) maps the
question to the right certified metric/filters and (2) returns the correct
computed figure.

- **Database:** `datadesk.db` (tables: `orders`, `customers`)
- **Computed on:** 2026-06-16, against the committed CSVs
- **How to re-derive:** run each question's SQL via the `datadesk-sqlite` MCP
  server (or `sqlite3 datadesk.db < query`). Re-run after any data change to
  refresh the expected answers.

## Summary

| # | Difficulty | Question | Expected answer |
|---|-----------|----------|-----------------|
| 1 | simple | How many orders are in the dataset? | **60** |
| 2 | simple | How many orders were completed? | **47** |
| 3 | count-distinct | How many distinct customers have placed at least one order? | **23** |
| 4 | filter (customers) | How many customers are on the enterprise plan tier? | **11** |
| 5 | metric | Total net revenue from completed orders (after discounts)? | **$9,226.74** |
| 6 | metric | Average order value (net revenue per completed order)? | **$196.31** |
| 7 | rate | Refund rate across all orders? | **11.67%** (7 of 60) |
| 8 | multi-step | Which product category earned the most gross revenue from completed orders, and how much? | **Electronics — $4,474.94** |
| 9 | multi-step / cross-table | Combined lifetime value of customers who placed ≥1 completed order? | **$103,315.50** (23 customers) |

---

## 1. Total order count — *simple*

**Question:** How many orders are in the dataset?

**Expected answer:** 60

**SQL:**
```sql
SELECT COUNT(*) FROM orders;
```

**How computed:** Row count of the `orders` table, no filters.

---

## 2. Completed order count — *simple (count + filter)*

**Question:** How many orders were completed?

**Expected answer:** 47

**SQL:**
```sql
SELECT COUNT(*) FROM orders WHERE order_status = 'completed';
```

**How computed:** Count of `orders` filtered to `order_status = 'completed'`.
(For reference: 47 completed, 7 refunded, 6 cancelled = 60 total.)

---

## 3. Distinct ordering customers — *count distinct*

**Question:** How many distinct customers have placed at least one order?

**Expected answer:** 23

**SQL:**
```sql
SELECT COUNT(DISTINCT customer_id) FROM orders;
```

**How computed:** Distinct `customer_id` values appearing in `orders`. (All 23
also exist in the `customers` table; 23 of the 40 customers have ordered.)

---

## 4. Enterprise customers — *filter on the customers table*

**Question:** How many customers are on the enterprise plan tier?

**Expected answer:** 11

**SQL:**
```sql
SELECT COUNT(*) FROM customers WHERE plan_tier = 'enterprise';
```

**How computed:** Count of `customers` filtered to `plan_tier = 'enterprise'`.
(Tier split: pro 17, free 12, enterprise 11.)

---

## 5. Total net revenue, completed orders — *metric (financial)*

**Question:** What is the total net revenue from completed orders, after
discounts?

**Expected answer:** $9,226.74

**SQL:**
```sql
SELECT ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2)
FROM orders
WHERE order_status = 'completed';
```

**How computed:** Per the certified **Total Net Revenue** definition — sum of
`quantity * unit_price * (1 - discount_pct/100)` over completed orders only.
Note the `100.0` (float) so integer `discount_pct` divides correctly.

---

## 6. Average order value — *metric (average)*

**Question:** What is the average order value (net revenue per completed order)?

**Expected answer:** $196.31

**SQL:**
```sql
SELECT ROUND(
         SUM(quantity * unit_price * (1 - discount_pct / 100.0)) * 1.0
         / COUNT(*), 2)
FROM orders
WHERE order_status = 'completed';
```

**How computed:** Certified **Average Order Value (AOV)** — net completed
revenue ÷ completed order count = 9,226.74 / 47 = 196.31.

---

## 7. Refund rate — *rate / percentage*

**Question:** What is the refund rate across all orders?

**Expected answer:** 11.67% (7 of 60)

**SQL:**
```sql
SELECT ROUND(
         100.0 * SUM(CASE WHEN order_status = 'refunded' THEN 1 ELSE 0 END)
         / COUNT(*), 2) AS refund_rate_pct
FROM orders;
```

**How computed:** Certified **Refund Rate** — refunded orders ÷ all orders.
7 / 60 = 0.11667 → 11.67%. Accept "≈11.7%" as correct (rounding).

---

## 8. Top product category by revenue — *multi-step (group + sort + pick top)*

**Question:** Which product category generated the most gross revenue from
completed orders, and how much?

**Expected answer:** Electronics — $4,474.94

**SQL:**
```sql
SELECT product_category, ROUND(SUM(quantity * unit_price), 2) AS gross_revenue
FROM orders
WHERE order_status = 'completed'
GROUP BY product_category
ORDER BY gross_revenue DESC
LIMIT 1;
```

**How computed:** Gross revenue (`quantity * unit_price`, pre-discount) by
category over completed orders, sorted descending, top row. Runners-up: Home &
Garden $1,804.93, Sports & Outdoors $1,237.98. (Gross is specified here; a net
variant would multiply by `(1 - discount_pct/100)` — the agent should not
silently switch.)

---

## 9. Lifetime value of completing customers — *multi-step / cross-table join*

**Question:** What is the combined lifetime value of customers who have placed at
least one completed order?

**Expected answer:** $103,315.50 (across 23 customers)

**SQL:**
```sql
SELECT ROUND(SUM(lifetime_value), 2)
FROM customers
WHERE customer_id IN (
  SELECT DISTINCT customer_id FROM orders WHERE order_status = 'completed'
);
```

**How computed:** Joins `customers` to `orders` — sums `lifetime_value` for the
customers whose `customer_id` appears in at least one completed order. All 23
ordering customers have at least one completed order, so this covers 23 of the
40 customers. The trap: this is *not* the same as total lifetime value of all
customers ($181,695.50) — the agent must scope to completing customers only.
