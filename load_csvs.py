#!/usr/bin/env python3
"""Load CSV files into a local SQLite database.

Re-runnable: each table is dropped and recreated from its source CSV on every
run, so the database always reflects the current CSV contents. Uses only the
Python standard library (no pandas required).

Usage:
    python3 load_csvs.py                # load the default tables below
    python3 load_csvs.py --db other.db  # use a different database file
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Mapping of table name -> source CSV file. Add entries here to load more.
TABLES = {
    "orders": "orders.csv",
    "customers": "customers.csv",
}


def infer_type(values: list[str]) -> str:
    """Infer a SQLite column type (INTEGER, REAL, or TEXT) from sample values."""
    seen = [v for v in values if v != ""]
    if not seen:
        return "TEXT"

    def is_int(v: str) -> bool:
        try:
            int(v)
            return True
        except ValueError:
            return False

    def is_float(v: str) -> bool:
        try:
            float(v)
            return True
        except ValueError:
            return False

    if all(is_int(v) for v in seen):
        return "INTEGER"
    if all(is_float(v) for v in seen):
        return "REAL"
    return "TEXT"


def load_table(conn: sqlite3.Connection, table: str, csv_path: Path) -> int:
    """Drop and recreate `table` from `csv_path`. Returns the row count loaded."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Infer a type per column from the loaded rows.
    col_types = []
    for i, name in enumerate(header):
        col_types.append((name, infer_type([r[i] for r in rows if i < len(r)])))

    cols_ddl = ", ".join(f'"{name}" {ctype}' for name, ctype in col_types)
    placeholders = ", ".join("?" for _ in header)

    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS "{table}"')
    cur.execute(f'CREATE TABLE "{table}" ({cols_ddl})')
    cur.executemany(
        f'INSERT INTO "{table}" VALUES ({placeholders})',
        rows,
    )
    conn.commit()
    return len(rows)


def build_database(db_path: str | Path = "datadesk.db") -> dict[str, int]:
    """Build (or rebuild) the SQLite database from the configured CSVs.

    Drops and recreates every table in TABLES from its source CSV. Returns a
    mapping of table name -> row count loaded. Importable so other code (e.g. a
    Streamlit app) can rebuild the database on startup without shelling out.
    """
    db_path = Path(db_path)
    if not db_path.is_absolute():
        db_path = (PROJECT_DIR / db_path).resolve()

    conn = sqlite3.connect(db_path)
    counts: dict[str, int] = {}
    try:
        for table, csv_name in TABLES.items():
            counts[table] = load_table(conn, table, PROJECT_DIR / csv_name)
    finally:
        conn.close()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        default="datadesk.db",
        help="SQLite database file to create/update (default: datadesk.db)",
    )
    args = parser.parse_args()

    db_path = (PROJECT_DIR / args.db).resolve()
    print(f"Loading into {db_path}")
    counts = build_database(db_path)

    # Confirm by counting straight from the database.
    conn = sqlite3.connect(db_path)
    try:
        for table, csv_name in TABLES.items():
            verified = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            status = "ok" if verified == counts[table] else "MISMATCH"
            print(f"  {table:<12} <- {csv_name:<16} {verified} rows [{status}]")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
