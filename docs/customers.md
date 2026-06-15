# Data Documentation: customers

This document describes the `customers` dataset, a customer master record stored at `/Users/filipepalma/claude-test-project/customers.csv`. Each row represents a single customer with their signup date, country, plan tier, and lifetime value. The document is in two parts: a **Dataset Profile** that summarizes the structure and contents of the file, and a **Metric Catalog** of certified business metrics derivable from the columns. All figures below are computed directly from the source data.

## Dataset Profile

**Total Rows:** 40 (excluding header)
**Total Columns:** 5

### Column Summary

| Column | Data Type | Missing | Unique | Example Values |
|--------|-----------|---------|--------|----------------|
| `customer_id` | string (identifier) | 0 | 40 | `CUST-0329`, `CUST-0472`, `CUST-0765` |
| `signup_date` | date (YYYY-MM-DD) | 0 | 40 | `2022-03-15`, `2021-08-22`, `2023-06-10` |
| `country` | categorical | 0 | 16 | `United Kingdom`, `Germany`, `Canada` |
| `plan_tier` | categorical | 0 | 3 | `pro`, `enterprise`, `free` |
| `lifetime_value` | float | 0 | 29 | `1250.00`, `8500.00`, `0.00` |

### Numeric Ranges

| Column | Min | Max |
|--------|-----|-----|
| `lifetime_value` | 0.00 | 22,100.00 |

### `plan_tier` Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| pro | 17 | 42.5% |
| free | 12 | 30.0% |
| enterprise | 11 | 27.5% |

### `country` Breakdown

| Value | Count | Percentage |
|-------|-------|------------|
| United States | 8 | 20.0% |
| United Kingdom | 3 | 7.5% |
| Germany | 3 | 7.5% |
| Canada | 3 | 7.5% |
| Australia | 2 | 5.0% |
| Brazil | 2 | 5.0% |
| France | 2 | 5.0% |
| India | 2 | 5.0% |
| Italy | 2 | 5.0% |
| Japan | 2 | 5.0% |
| Mexico | 2 | 5.0% |
| Netherlands | 2 | 5.0% |
| Singapore | 2 | 5.0% |
| Spain | 2 | 5.0% |
| Sweden | 2 | 5.0% |
| South Korea | 1 | 2.5% |

### Additional Notes

- **Date range:** Signups span from 2020-04-19 to 2023-11-08 (approximately 3.5 years).
- **Lifetime value pattern:** Free-tier customers have zero lifetime value by definition; pro-tier averages ~1,520; enterprise customers average ~14,168, indicating strong revenue concentration in the enterprise segment.
- **Geographic distribution:** Data covers 16 countries with the United States representing 20.0% of the customer base; otherwise a relatively balanced international presence.
- **Data quality:** No missing values; all 40 customer IDs are unique; consistent decimal formatting for monetary values (two decimal places).

## Metric Catalog

This catalog defines the certified business metrics derived from the customers dataset, covering customer volume, lifetime value, plan composition, and geographic/tier segmentation. All formulas reference real columns from the profile above.

---

## Total Customer Count

**Definition:**
The total number of unique customers in the database, representing the full size of the customer base across all plan tiers.

**Formula:**
```
COUNT(customer_id)
```

**Source Columns:**
- `customer_id` — unique identifier for each customer

**Filters & Business Rules:**
- No filters applied; includes all customer records in the dataset
- Counts each unique `customer_id` exactly once

**Grain:**
Per customer (aggregate count)

**Dimensions:**
- `plan_tier` — breakdown by subscription tier
- `country` — breakdown by geographic location
- `signup_date` — breakdown by acquisition cohort

**Caveats:**
- Does not distinguish between active and inactive customers
- Assumes all records represent distinct customers with no duplicates
- No time dimension; represents a snapshot at the date of data extraction

---

## Total Active Customers

**Definition:**
The count of customers with a paid plan (pro or enterprise), excluding those on the free tier. This metric isolates the monetized customer base.

**Formula:**
```
COUNT(customer_id) WHERE plan_tier != 'free'
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification (free, pro, enterprise)

**Filters & Business Rules:**
- Excludes customers where `plan_tier = 'free'`
- Includes only customers on 'pro' or 'enterprise' plans
- Counts unique customer IDs only

**Grain:**
Per customer (aggregate count of paid customers)

**Dimensions:**
- `plan_tier` — further breakdown between pro and enterprise
- `country` — paid customer distribution by geography
- `signup_date` — acquisition cohort of paid customers

**Caveats:**
- Free-tier customers may later convert to paid; this snapshot does not track conversions
- Does not account for churn or plan downgrades
- All paid plans are treated equally regardless of revenue difference

---

## Total Lifetime Value

**Definition:**
The aggregate lifetime revenue generated from all customers in the database, regardless of current plan status. This represents the total business value created by the customer base.

**Formula:**
```
SUM(lifetime_value)
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD

**Filters & Business Rules:**
- No filters applied; includes all customers regardless of plan tier or status
- Sums all values in the `lifetime_value` column
- Free-tier customers (with `lifetime_value = 0.00`) are included in the sum

**Grain:**
Per customer (aggregate sum)

**Dimensions:**
- `plan_tier` — revenue contribution by tier
- `country` — revenue distribution by geography
- `signup_date` — revenue by acquisition cohort

**Caveats:**
- Does not account for refunds or chargebacks after the `lifetime_value` snapshot
- Free-tier customers contribute zero value but are included in counts
- Currency is assumed to be consistent across all records (USD)
- Represents historical value, not projected or forward-looking value

---

## Average Lifetime Value per Customer

**Definition:**
The mean lifetime value across all customers, indicating average revenue potential per acquired customer. This metric normalizes total revenue by customer count.

**Formula:**
```
SUM(lifetime_value) / COUNT(customer_id)
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `customer_id` — unique identifier for each customer

**Filters & Business Rules:**
- No filters applied; includes all customers in the dataset
- Denominator includes both paid and free-tier customers

**Grain:**
Per customer (average across entire base)

**Dimensions:**
- `plan_tier` — average value by tier
- `country` — average value by geography
- `signup_date` — average value by acquisition cohort

**Caveats:**
- Heavily influenced by high-value enterprise customers; median may be more representative
- Zero-value free-tier customers pull down the average
- Does not distinguish between retained and churned customers
- Sensitive to data entry errors or outliers in the `lifetime_value` column

---

## Average Lifetime Value per Paid Customer

**Definition:**
The mean lifetime value for customers on paid plans only, filtering out free-tier users. This isolates revenue quality and monetization efficiency among the paying customer base.

**Formula:**
```
SUM(lifetime_value WHERE plan_tier != 'free') / COUNT(customer_id WHERE plan_tier != 'free')
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- Only includes customers where `plan_tier = 'pro'` or `plan_tier = 'enterprise'`
- Excludes all free-tier customers from both numerator and denominator
- Counts and sums unique paid customers only

**Grain:**
Per paid customer (average across monetized base)

**Dimensions:**
- `plan_tier` — average value by specific tier (pro vs. enterprise)
- `country` — average value by geography among paid users
- `signup_date` — average value by cohort among paid users

**Caveats:**
- Still influenced by outliers in the high-value tier
- Represents static LTV; does not account for future expansion or churn risk
- Useful for comparing quality across cohorts, but not useful for predicting future revenue

---

## Free-Tier Customer Count

**Definition:**
The number of customers currently on the free plan. This represents the freemium or trial user base and potential conversion opportunities.

**Formula:**
```
COUNT(customer_id) WHERE plan_tier = 'free'
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- Only includes customers where `plan_tier = 'free'`
- Counts unique customer IDs only
- Does not distinguish between users in trial period vs. permanent free-tier subscribers

**Grain:**
Per customer (count of free-tier users)

**Dimensions:**
- `country` — free-user distribution by geography
- `signup_date` — free-user cohort trends

**Caveats:**
- Free-tier users may or may not convert; this is a static snapshot
- Does not indicate engagement level or likelihood of conversion
- May include inactive or abandoned accounts

---

## Pro-Tier Customer Count

**Definition:**
The number of customers on the professional/standard paid plan. This tracks adoption of the mid-market offering and represents the core paying customer segment.

**Formula:**
```
COUNT(customer_id) WHERE plan_tier = 'pro'
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- Only includes customers where `plan_tier = 'pro'`
- Counts unique customer IDs only

**Grain:**
Per customer (count of pro-tier users)

**Dimensions:**
- `country` — pro-tier distribution by geography
- `signup_date` — pro-tier acquisition trends

**Caveats:**
- Does not indicate retention or churn within this tier
- Combines customers acquired through different channels or at different contract terms

---

## Enterprise Customer Count

**Definition:**
The number of customers on the enterprise/premium plan. This metric tracks the high-value customer segment critical for ARR and strategic accounts.

**Formula:**
```
COUNT(customer_id) WHERE plan_tier = 'enterprise'
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- Only includes customers where `plan_tier = 'enterprise'`
- Counts unique customer IDs only

**Grain:**
Per customer (count of enterprise-tier users)

**Dimensions:**
- `country` — enterprise-tier distribution by geography
- `signup_date` — enterprise-tier acquisition trends

**Caveats:**
- Small sample size may produce volatile trends
- Individual customer churn has outsized impact on total revenue
- Does not account for contract value or expansion opportunities

---

## Paid Customer Ratio

**Definition:**
The percentage of customers on paid plans relative to the total customer base. This rate metric measures monetization efficiency and conversion from free to paid.

**Formula:**
```
COUNT(customer_id WHERE plan_tier != 'free') / COUNT(customer_id)
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- Numerator includes only customers where `plan_tier = 'pro'` or `'enterprise'`
- Denominator includes all customers regardless of tier
- No time window; represents current-state ratio

**Grain:**
Aggregate ratio across entire customer base

**Dimensions:**
- `country` — paid ratio by geography
- `signup_date` — paid ratio by acquisition cohort

**Caveats:**
- Does not distinguish between newly acquired free users and long-term free subscribers
- High free-tier count can artificially depress this ratio
- Cohort analysis recommended to assess conversion velocity over time

---

## Customers by Signup Cohort (Year)

**Definition:**
The count of customers acquired in each calendar year, segmented by signup date. This time-based metric tracks customer acquisition velocity and growth trends.

**Formula:**
```
COUNT(customer_id) GROUP BY YEAR(signup_date)
```

**Source Columns:**
- `customer_id` — unique identifier for each customer
- `signup_date` — date customer was acquired (YYYY-MM-DD format)

**Filters & Business Rules:**
- No filters applied; includes all customers
- Groups records by the year extracted from the `signup_date` column
- Each cohort contains all customers acquired within that calendar year

**Grain:**
Per cohort year (count of customers acquired per year)

**Dimensions:**
- `plan_tier` — breakdown of each cohort by tier
- `country` — geographic distribution within each cohort

**Caveats:**
- Recent cohorts may show acquisition in progress if data is not current
- Oldest cohorts likely include churned customers; metrics do not distinguish retention
- Year-to-date cohorts will be incomplete and not comparable to full-year cohorts

---

## Revenue by Country

**Definition:**
The total lifetime value aggregated by customer geography. This segmented metric identifies the geographic markets and revenue concentration across the customer base.

**Formula:**
```
SUM(lifetime_value) GROUP BY country
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `country` — country of customer residence or business

**Filters & Business Rules:**
- No filters applied; includes all customers
- Groups by the `country` field as-is
- Sums all lifetime value within each country group

**Grain:**
Per country (aggregate revenue per geographic region)

**Dimensions:**
- `plan_tier` — revenue by country and tier
- `signup_date` — revenue by country and acquisition cohort

**Caveats:**
- Does not account for differences in purchasing power or local currency conversion
- Assumes the `country` field reflects true customer location or operational region
- Small-market countries may have limited sample size
- Does not indicate market saturation or growth opportunity

---

## Average Lifetime Value by Country

**Definition:**
The mean lifetime value per customer for each country. This metric measures customer quality and monetization effectiveness by geographic region.

**Formula:**
```
SUM(lifetime_value) / COUNT(customer_id) GROUP BY country
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `customer_id` — unique identifier for each customer
- `country` — country of customer residence or business

**Filters & Business Rules:**
- No filters applied; includes all customers
- Groups by the `country` field
- Numerator sums lifetime value per country; denominator counts customers per country

**Grain:**
Per country (average revenue per customer within each geographic region)

**Dimensions:**
- `plan_tier` — average value by country and tier
- `signup_date` — average value by country and acquisition cohort

**Caveats:**
- Small-market countries with few customers may show high volatility
- Influenced by regional outliers (e.g., single high-value enterprise customer)
- Does not control for differences in go-to-market strategy or pricing by region
- Useful for comparative analysis, but requires context on regional strategy

---

## Revenue by Plan Tier

**Definition:**
The total lifetime value segmented by customer subscription tier. This metric shows revenue contribution and profitability by tier, informing pricing and packaging strategy.

**Formula:**
```
SUM(lifetime_value) GROUP BY plan_tier
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `plan_tier` — subscription tier classification (free, pro, enterprise)

**Filters & Business Rules:**
- No filters applied; includes all customers
- Groups by the three plan tiers: free, pro, enterprise
- Sums lifetime value within each tier group

**Grain:**
Per tier (aggregate revenue by plan tier)

**Dimensions:**
- `country` — revenue by tier and geography
- `signup_date` — revenue by tier and acquisition cohort

**Caveats:**
- Free tier contributes zero revenue; included for completeness
- Does not account for contract terms, discounts, or one-time fees
- Revenue mix is static; does not reflect upgrades/downgrades over time
- Enterprise tier may include special pricing; averages may not be representative

---

## Average Lifetime Value by Plan Tier

**Definition:**
The mean lifetime value for customers at each subscription tier. This metric compares monetization effectiveness by tier and informs pricing strategy and tier positioning.

**Formula:**
```
SUM(lifetime_value) / COUNT(customer_id) GROUP BY plan_tier
```

**Source Columns:**
- `lifetime_value` — cumulative revenue per customer in USD
- `customer_id` — unique identifier for each customer
- `plan_tier` — subscription tier classification

**Filters & Business Rules:**
- No filters applied; includes all customers
- Groups by the three plan tiers: free, pro, enterprise
- Numerator sums lifetime value per tier; denominator counts customers per tier

**Grain:**
Per tier (average revenue per customer within each subscription tier)

**Dimensions:**
- `country` — average value by tier and geography
- `signup_date` — average value by tier and acquisition cohort

**Caveats:**
- Free tier will show 0.00 average (all members have zero lifetime value)
- Enterprise tier may be heavily influenced by few large deals; median recommended for comparison
- Does not account for contract length or expansion revenue
- Useful for understanding tier economics, but should not drive pricing decisions alone

---

## Metric Summary

| Metric | Type | Grain | Primary Use |
|--------|------|-------|-------------|
| Total Customer Count | count | aggregate | Measure total customer base size |
| Total Active Customers | count | aggregate | Track paying customer base |
| Total Lifetime Value | sum | aggregate | Measure total business value created |
| Average Lifetime Value per Customer | avg | aggregate | Benchmark average revenue per customer |
| Average Lifetime Value per Paid Customer | avg | aggregate | Isolate paid-customer revenue quality |
| Free-Tier Customer Count | count | aggregate | Measure freemium/trial user base |
| Pro-Tier Customer Count | count | aggregate | Track mid-market segment adoption |
| Enterprise Customer Count | count | aggregate | Monitor strategic account count |
| Paid Customer Ratio | rate | aggregate | Assess monetization efficiency |
| Customers by Signup Cohort (Year) | count | per year | Track acquisition velocity by cohort |
| Revenue by Country | sum | per country | Identify geographic markets and concentration |
| Average Lifetime Value by Country | avg | per country | Assess customer quality by region |
| Revenue by Plan Tier | sum | per tier | Measure tier profitability and mix |
| Average Lifetime Value by Plan Tier | avg | per tier | Compare tier monetization and positioning |
