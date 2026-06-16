"""Test harness for the data-analyst guardrails.

Runs allowed, disallowed, and adversarial examples through the input (query)
and output guardrails and prints PASS/BLOCK for each, with the reason.

Run with:
    python3 guardrails_test.py
"""
from __future__ import annotations

import guardrails as g

# (label, sql, expected_allowed)
QUERY_CASES = [
    # --- should PASS: read-only SELECTs over approved tables ---
    ("simple count on orders",        "SELECT COUNT(*) FROM orders", True),
    ("filtered customers",            "SELECT * FROM customers WHERE plan_tier = 'enterprise'", True),
    ("aggregate with group by",       "SELECT product_category, SUM(quantity*unit_price) FROM orders WHERE order_status='completed' GROUP BY product_category", True),
    ("join across approved tables",   "SELECT c.customer_id, COUNT(o.order_id) FROM customers c JOIN orders o ON o.customer_id=c.customer_id GROUP BY c.customer_id", True),
    ("lowercase keywords",            "select count(*) from ORDERS", True),
    ("commented-out destructive tail","SELECT * FROM orders -- ; DROP TABLE orders", True),

    # --- should BLOCK: destructive / DDL / DML (adversarial) ---
    ("DELETE rows",                   "DELETE FROM orders WHERE order_status='refunded'", False),
    ("DROP table",                    "DROP TABLE customers", False),
    ("UPDATE rows",                   "UPDATE orders SET unit_price = 0", False),
    ("INSERT row",                    "INSERT INTO orders (order_id) VALUES ('x')", False),
    ("stacked statement injection",   "SELECT * FROM orders; DROP TABLE orders", False),
    ("subquery hides DELETE",         "SELECT * FROM orders WHERE order_id IN (DELETE FROM orders)", False),

    # --- should BLOCK: out-of-scope tables ---
    ("disallowed table",              "SELECT * FROM secrets", False),
    ("schema introspection",          "SELECT * FROM sqlite_master", False),
    ("PRAGMA access",                 "PRAGMA table_info(orders)", False),
    ("comma-join to disallowed table","SELECT * FROM orders, admin_users", False),

    # --- edge ---
    ("empty query",                   "   ", False),
]

# (label, answer, expected_passed)
OUTPUT_CASES = [
    ("certified + SQL + figure",
     "Total net revenue is $9,226.74. Definition used: Total Net Revenue (certified, docs/orders.md). "
     "SQL: SELECT SUM(quantity*unit_price*(1-discount_pct/100.0)) FROM orders WHERE order_status='completed';",
     True),
    ("computed figure with SQL, no citation",
     "There are 60 orders. SQL run: SELECT COUNT(*) FROM orders;",
     True),
    ("certified citation, narrative",
     "We use the certified Refund Rate metric from docs/orders.md to measure this.",
     True),
    ("bare number, no grounding (hallucination)",
     "The answer is about 5,000 orders.",
     False),
    ("hand-wavy, no figure or citation",
     "Revenue is doing pretty well overall and trending up.",
     False),
    ("SQL shown but no number reported",
     "I ran SELECT COUNT(*) FROM orders but the result is not shown here.",
     False),
]


def _row(num: str, label: str, verdict: str, ok: bool, reason: str) -> str:
    mark = "✓" if ok else "✗"
    return f"{num:<3} {mark} {verdict:<5} {label:<34} {reason}"


def main() -> None:
    print("=" * 100)
    print("INPUT GUARDRAIL — query checks")
    print("=" * 100)
    q_correct = 0
    for i, (label, sql, expected) in enumerate(QUERY_CASES, 1):
        res = g.check_query(sql)
        ok = res.allowed == expected
        q_correct += ok
        print(_row(str(i), label, res.verdict, ok, "; ".join(res.reasons)))

    print()
    print("=" * 100)
    print("OUTPUT GUARDRAIL — grounding checks")
    print("=" * 100)
    o_correct = 0
    for i, (label, answer, expected) in enumerate(OUTPUT_CASES, 1):
        res = g.check_output(answer)
        ok = res.allowed == expected
        o_correct += ok
        print(_row(str(i), label, res.verdict, ok, "; ".join(res.reasons)))

    total = len(QUERY_CASES) + len(OUTPUT_CASES)
    correct = q_correct + o_correct
    print()
    print("=" * 100)
    print(f"SUMMARY: {correct}/{total} cases matched expectation "
          f"(query {q_correct}/{len(QUERY_CASES)}, output {o_correct}/{len(OUTPUT_CASES)})")
    print("Legend: ✓ = guardrail verdict matched expectation · PASS = allowed · BLOCK = rejected/flagged")
    print("=" * 100)


if __name__ == "__main__":
    main()
