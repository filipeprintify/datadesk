"""Data Catalog — a simple Streamlit UI to browse datadesk.db and its docs.

Run with:
    .venv/bin/streamlit run catalog_app.py

Lets you:
- see the list of tables with their row counts,
- pick a table to view its columns and a sample of rows,
- read the generated documentation (profile + metric catalog) for each dataset.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

import load_csvs

PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "datadesk.db"
DOCS_DIR = PROJECT_DIR / "docs"
SAMPLE_ROWS = 100


# --- Database bootstrap -----------------------------------------------------

@st.cache_resource(show_spinner="Building database from CSV files…")
def ensure_database() -> str:
    """Rebuild datadesk.db from the committed CSVs if it isn't present.

    Streamlit Community Cloud clones the repo fresh and datadesk.db is
    gitignored, so the database won't exist on first run. We rebuild it from the
    committed CSV files via load_csvs.build_database(). Cached as a resource so
    it runs once per container, not on every rerun.
    """
    if not DB_PATH.exists():
        load_csvs.build_database(DB_PATH)
    return str(DB_PATH)


# --- Data access -----------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    # check_same_thread=False is safe here: Streamlit reruns are single-threaded
    # per session and we only ever read.
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(show_spinner=False)
def list_tables() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
    return [r[0] for r in rows]


@st.cache_data(show_spinner=False)
def row_count(table: str) -> int:
    with get_connection() as conn:
        return conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]


@st.cache_data(show_spinner=False)
def columns(table: str) -> pd.DataFrame:
    with get_connection() as conn:
        info = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
    return pd.DataFrame(
        [{"Column": r[1], "Type": r[2] or "—", "Primary Key": "yes" if r[5] else ""} for r in info]
    )


@st.cache_data(show_spinner=False)
def sample_rows(table: str, limit: int = SAMPLE_ROWS) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {limit}', conn)


@st.cache_data(show_spinner=False)
def doc_for(table: str) -> str | None:
    """Return the markdown doc for a table, if docs/<table>.md exists."""
    path = DOCS_DIR / f"{table}.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


# --- UI --------------------------------------------------------------------

st.set_page_config(page_title="Data Catalog", page_icon="📊", layout="wide")
st.title("📊 Data Catalog")

# Build the database from the committed CSVs if it isn't already present
# (e.g. on a fresh Streamlit Community Cloud deploy).
try:
    ensure_database()
except Exception as exc:  # surface a clear message instead of a raw traceback
    st.error(
        f"Could not build the database from the CSV files: {exc}\n\n"
        "Ensure the source CSVs are present, or build locally with "
        "`python3 load_csvs.py`."
    )
    st.stop()

tables = list_tables()
if not tables:
    st.warning("No tables found in the database.")
    st.stop()

# Sidebar: overview of tables with row counts + a picker.
st.sidebar.header("Tables")
overview = pd.DataFrame(
    {"Table": tables, "Rows": [row_count(t) for t in tables]}
)
st.sidebar.dataframe(overview, hide_index=True, width="stretch")
selected = st.sidebar.selectbox("Select a table", tables)

st.header(f"`{selected}`")
st.caption(f"{row_count(selected):,} rows · {len(columns(selected))} columns")

tab_schema, tab_sample, tab_docs = st.tabs(["Columns", "Sample rows", "Documentation"])

with tab_schema:
    st.subheader("Columns")
    st.dataframe(columns(selected), hide_index=True, width="stretch")

with tab_sample:
    st.subheader(f"Sample rows (first {SAMPLE_ROWS})")
    st.dataframe(sample_rows(selected), hide_index=True, width="stretch")

with tab_docs:
    doc = doc_for(selected)
    if doc:
        st.markdown(doc)
    else:
        st.info(
            f"No documentation found for `{selected}`. "
            f"Expected a file at `docs/{selected}.md`."
        )
