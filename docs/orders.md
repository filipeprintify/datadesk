# Data Documentation: orders

This document describes the `orders` dataset, a transactional e-commerce order log stored at `/Users/filipepalma/claude-test-project/orders.csv`. Each row represents a single customer order with its date, customer, product category, pricing, discount, destination country, and fulfillment status. The document is in two parts: a **Dataset Profile** that summarizes the structure and contents of the file, and a **Metric Catalog** of certified business metrics derivable from the columns. All figures below are computed directly from the source data.

## Dataset Profile

**Total Rows:** 60 (excluding header)
**Total Columns:** 9

### Column Summary

| Column | Data Type | Missing | Unique | Example Values |
|--------|-----------|---------|--------|----------------|
| `order_id` | string (identifier) | 0 | 60 | `ORD-10001`, `ORD-10023`, `ORD-10060` |
| `order_date` | date (YYYY-MM-DD) | 0 | 60 | `2024-01-03`, `2024-02-15`, `2024-04-28` |
| `customer_id` | string (identifier) | 0 | 23 | `CUST-2847`, `CUST-1923`, `CUST-6783` |
| `product_category` | categorical | 0 | 8 | `Electronics`, `Clothing`, `Home & Garden` |
| `quantity` | integer | 0 | 7 | `1`, `3`, `8` |
| `unit_price` | float | 0 | 50 | `299.99`, `49.95`, `1299.00` |
| `discount_pct` | integer (percentage) | 0 | 6 | `0`, `10`, `25` |
| `country` | categorical | 0 | 16 | `United States`, `Canada`, `Japan` |
| `order_status` | categorical (status) | 0 | 3 | `completed`, `refunded`, `cancelled` |

### Numeric Ranges

| Column | Min | Max |
|--------|-----|-----|
| `quantity` | 1 | 8 |
| `unit_price` | 6.99 | 1,299.00 |
| `discount_pct` | 0 | 25 |

### `product_category` Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| Electronics | 12 | 20.0% |
| Clothing | 10 | 16.7% |
| Home & Garden | 7 | 11.7% |
| Sports & Outdoors | 7 | 11.7% |
| Books | 6 | 10.0% |
| Beauty | 6 | 10.0% |
| Toys & Games | 6 | 10.0% |
| Food & Grocery | 6 | 10.0% |

### `country` Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| United States | 16 | 26.7% |
| United Kingdom | 6 | 10.0% |
| Canada | 5 | 8.3% |
| Germany | 5 | 8.3% |
| Australia | 4 | 6.7% |
| France | 4 | 6.7% |
| Japan | 3 | 5.0% |
| Brazil | 3 | 5.0% |
| Netherlands | 2 | 3.3% |
| Spain | 2 | 3.3% |
| India | 2 | 3.3% |
| Mexico | 2 | 3.3% |
| Italy | 2 | 3.3% |
| Sweden | 2 | 3.3% |
| South Korea | 1 | 1.7% |
| Singapore | 1 | 1.7% |

### `order_status` Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| completed | 47 | 78.3% |
| refunded | 7 | 11.7% |
| cancelled | 6 | 10.0% |

### Additional Notes

- **Date range:** Orders span `2024-01-03` to `2024-04-28` (roughly four months). Order dates are unique and increase monotonically with `order_id`, indicating a clean sequential log with no duplicate timestamps.
- **Repeat customers:** 60 orders map to only 23 distinct customers, so there is meaningful repeat-purchase behavior. `CUST-2847` is the most frequent buyer (appears multiple times across categories).
- **Pricing skew:** `unit_price` is right-skewed — the mean (~164.18) sits well above the median (~79.75), driven by a few high-ticket Electronics items up to 1,299.00.
- **Discounts:** 33 of 60 orders (55.0%) carry a non-zero discount; the rest are at full price. Discount values are coarse, clustering at 0, 5, 10, 15, 20, and 25 percent.
- **Data quality:** No missing values in any column. `order_id` is fully unique and suitable as a primary key. `discount_pct` is stored as a whole-number percentage (0-100), not a fraction.
- **Currency:** No currency column is present; all `unit_price` values are assumed to be a single currency (USD) for metric calculations.

## Metric Catalog

This catalog defines the certified business metrics derived from the orders dataset, covering order volume, revenue, average order value, discounting, refunds/cancellations, customer repeat behavior, and segmented breakdowns. All formulas reference real columns from the profile above.

---

## Total Orders

**Definition:**
The total number of order records in the dataset, regardless of fulfillment outcome. Measures overall order volume.

**Formula:**
```
COUNT(order_id)
```

**Source Columns:**
- `order_id` — unique identifier for each order

**Filters & Business Rules:**
- No status filter; includes completed, refunded, and cancelled orders
- Each `order_id` is counted once (the field is fully unique)

**Grain:**
Per order (aggregable to any time period)

**Dimensions:**
- `order_date` — daily, weekly, or monthly trends
- `country` — geographic breakdown
- `product_category` — category mix
- `order_status` — outcome mix

**Caveats:**
- Includes orders that never generated revenue (cancelled/refunded); use Completed Orders for realized demand
- Current sample is only 60 rows over four months, so time-based slices are thin

---

## Completed Orders

**Definition:**
The number of orders that were successfully fulfilled, representing realized demand.

**Formula:**
```
COUNT(order_id) WHERE order_status = 'completed'
```

**Source Columns:**
- `order_id` — unique order identifier
- `order_status` — fulfillment status of the order

**Filters & Business Rules:**
- Only includes orders where `order_status = 'completed'`
- Excludes `refunded` and `cancelled` orders

**Grain:**
Per order

**Dimensions:**
- `order_date`, `country`, `product_category`

**Caveats:**
- An order marked `completed` here may later be refunded outside this snapshot; status reflects the data as captured
- In this sample, 47 of 60 orders (78.3%) are completed

---

## Total Net Revenue

**Definition:**
The total monetary value of completed orders after applying line-item discounts. This is the primary realized-sales metric.

**Formula:**
```
SUM(quantity * unit_price * (1 - discount_pct / 100))
WHERE order_status = 'completed'
```

**Source Columns:**
- `quantity` — number of units purchased
- `unit_price` — price per unit
- `discount_pct` — discount percentage applied (0-100)
- `order_status` — fulfillment status

**Filters & Business Rules:**
- Only includes `order_status = 'completed'`
- Discount applied as a percentage reduction off the line total
- Excludes refunded and cancelled orders

**Grain:**
Per order (aggregable to any period)

**Dimensions:**
- `order_date` — revenue trend over time
- `country` — revenue by geography
- `product_category` — revenue by category

**Caveats:**
- Excludes shipping, taxes, and fees
- Currency is assumed uniform (USD); no currency column exists
- For this sample, net revenue on completed orders is ~9,226.74; net revenue across all statuses is ~11,106.95

---

## Gross Merchandise Value (GMV)

**Definition:**
The total value of all order line items before discounts and before any status filtering — a measure of gross demand placed.

**Formula:**
```
SUM(quantity * unit_price)
```

**Source Columns:**
- `quantity` — units purchased
- `unit_price` — price per unit

**Filters & Business Rules:**
- No status filter and no discount applied
- Represents list-price demand, not realized revenue

**Grain:**
Per order

**Dimensions:**
- `order_date`, `country`, `product_category`, `order_status`

**Caveats:**
- Overstates realized revenue because it ignores discounts and cancellations/refunds
- For this sample, GMV across all orders is ~12,148.51

---

## Average Order Value (AOV)

**Definition:**
The average net revenue generated per completed order. Indicates typical order size in monetary terms.

**Formula:**
```
SUM(quantity * unit_price * (1 - discount_pct / 100)) / COUNT(order_id)
WHERE order_status = 'completed'
```

**Source Columns:**
- `quantity`, `unit_price`, `discount_pct` — line value components
- `order_status` — fulfillment status

**Filters & Business Rules:**
- Restricted to `order_status = 'completed'`
- Numerator is net (post-discount) revenue; denominator is completed order count

**Grain:**
Per order, averaged

**Dimensions:**
- `country`, `product_category`, `order_date`

**Caveats:**
- Sensitive to high-ticket outliers (e.g., 1,299.00 Electronics items) given the small sample; consider median alongside the mean
- Choice of numerator (net vs. gross) materially changes the value — this metric uses net

---

## Refund Rate

**Definition:**
The share of orders that were refunded, used as a quality and customer-satisfaction signal.

**Formula:**
```
COUNT(order_id WHERE order_status = 'refunded') / COUNT(order_id)
```

**Source Columns:**
- `order_id` — order identifier
- `order_status` — fulfillment status

**Filters & Business Rules:**
- Numerator: orders with `order_status = 'refunded'`
- Denominator: all orders (any status)

**Grain:**
Rate across an order population

**Dimensions:**
- `product_category`, `country`, `order_date`

**Caveats:**
- Order-count based, not revenue-weighted; a few high-value refunds can have outsized financial impact not reflected here
- In this sample the refund rate is 11.7% (7 of 60)

---

## Cancellation Rate

**Definition:**
The share of orders that were cancelled before fulfillment, indicating demand that did not convert to revenue.

**Formula:**
```
COUNT(order_id WHERE order_status = 'cancelled') / COUNT(order_id)
```

**Source Columns:**
- `order_id` — order identifier
- `order_status` — fulfillment status

**Filters & Business Rules:**
- Numerator: orders with `order_status = 'cancelled'`
- Denominator: all orders

**Grain:**
Rate across an order population

**Dimensions:**
- `product_category`, `country`, `order_date`

**Caveats:**
- Does not distinguish customer- vs. merchant-initiated cancellations (not captured in the data)
- In this sample the cancellation rate is 10.0% (6 of 60)

---

## Discount Penetration

**Definition:**
The share of orders that received any discount, measuring how reliant sales are on promotional pricing.

**Formula:**
```
COUNT(order_id WHERE discount_pct > 0) / COUNT(order_id)
```

**Source Columns:**
- `order_id` — order identifier
- `discount_pct` — discount percentage applied

**Filters & Business Rules:**
- Numerator: orders with `discount_pct > 0`
- Denominator: all orders (any status)

**Grain:**
Rate across an order population

**Dimensions:**
- `product_category`, `country`, `order_date`

**Caveats:**
- Counts presence of a discount, not its depth; pair with average `discount_pct` for magnitude
- In this sample, 55.0% of orders (33 of 60) carry a discount

---

## Unique Customers

**Definition:**
The number of distinct customers who placed at least one order, used as a reach/base-size measure.

**Formula:**
```
COUNT(DISTINCT customer_id)
```

**Source Columns:**
- `customer_id` — customer identifier

**Filters & Business Rules:**
- Distinct count of `customer_id`
- No status filter by default; can be restricted to completed orders

**Grain:**
Per customer

**Dimensions:**
- `country`, `product_category`, `order_date` (active customers per period)

**Caveats:**
- A customer appearing in only cancelled/refunded orders still counts unless completed-only filtering is applied
- This dataset has 23 unique customers across 60 orders

---

## Orders per Customer (Repeat Rate)

**Definition:**
The average number of orders placed per distinct customer, a proxy for repeat-purchase behavior and loyalty.

**Formula:**
```
COUNT(order_id) / COUNT(DISTINCT customer_id)
```

**Source Columns:**
- `order_id` — order identifier
- `customer_id` — customer identifier

**Filters & Business Rules:**
- No status filter by default
- Both numerator and denominator drawn from the same order population

**Grain:**
Per customer, averaged

**Dimensions:**
- `country`, `product_category`, `order_date`

**Caveats:**
- An average masks distribution; a few heavy repeat buyers can inflate it
- In this sample the ratio is ~2.6 orders per customer (60 / 23)

---

## Revenue by Segment

**Definition:**
Net completed revenue broken out by a chosen dimension (category or country), used to identify top-performing segments.

**Formula:**
```
SUM(quantity * unit_price * (1 - discount_pct / 100))
WHERE order_status = 'completed'
GROUP BY <product_category | country>
```

**Source Columns:**
- `quantity`, `unit_price`, `discount_pct` — line value components
- `order_status` — fulfillment status
- `product_category` / `country` — segmentation dimension

**Filters & Business Rules:**
- Only includes `order_status = 'completed'`
- One grouping dimension applied per view

**Grain:**
Per segment (per category or per country)

**Dimensions:**
- `product_category` — category-level revenue
- `country` — geography-level revenue
- Can be further crossed with `order_date` for trends

**Caveats:**
- Small per-segment counts in this sample make individual segment totals noisy (e.g., Singapore and South Korea each have 1 order)
- High-ticket categories (Electronics) dominate revenue despite moderate order counts

---

## Metric Summary

| Metric | Type | Grain | Primary Use |
|--------|------|-------|-------------|
| Total Orders | count | per order | Track overall order volume |
| Completed Orders | count | per order | Measure realized, fulfilled demand |
| Total Net Revenue | sum | per order | Track post-discount realized sales |
| Gross Merchandise Value (GMV) | sum | per order | Measure gross list-price demand |
| Average Order Value (AOV) | avg | per order | Gauge typical order size |
| Refund Rate | rate | order population | Monitor refunds / quality |
| Cancellation Rate | rate | order population | Monitor non-converting demand |
| Discount Penetration | rate | order population | Assess reliance on promotions |
| Unique Customers | count | per customer | Measure customer base size |
| Orders per Customer | ratio | per customer | Gauge repeat-purchase behavior |
| Revenue by Segment | sum | per segment | Compare category/country performance |
