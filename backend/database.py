"""Trusted introspection and bounded, independently read-only SQLite access."""
from contextlib import closing
from functools import lru_cache
from pathlib import Path
import math
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "sample.db"
DESCRIPTIONS = {
    "departments": "Teams within Northstar Commerce.",
    "employees": "Synthetic employees, department, hire date and annual USD salary.",
    "customers": "Synthetic customers with full US state names.",
    "products": "Catalog with current USD prices; use order_items for historical sales.",
    "orders": "Orders from 2024–2025: completed, processing or cancelled.",
    "order_items": "Historical quantities and unit prices; revenue = quantity × unit_price.",
}
SQLITE_FUNCTIONS = frozenset("abs avg ceil ceiling char coalesce concat concat_ws count date datetime floor format glob group_concat hex ifnull iif instr julianday lag last_value lead length like likelihood likely lower ltrim max min mod nth_value ntile nullif percent_rank printf rank replace round row_number rtrim sign strftime substr substring sum time total trim typeof unicode unixepoch unlikely upper dense_rank cume_dist first_value pow power sqrt json_extract json_array_length".split())


def connect(guarded: bool = True, timeout: float = 2.0):
    db = sqlite3.connect(DB_PATH.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    if guarded:
        deadline, calls = time.monotonic() + timeout, 0

        def budget():
            nonlocal calls
            calls += 1
            return int(calls >= 1000 or time.monotonic() > deadline)

        def authorize(action, one, two, database, source):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ:
                # SQLite reports database=None for a table-level rowid/count read.
                allowed_db = database == "main" or (database is None and two == "")
                return sqlite3.SQLITE_OK if one in DESCRIPTIONS and allowed_db else sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_FUNCTION:
                return sqlite3.SQLITE_OK if (two or "").lower() in SQLITE_FUNCTIONS else sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_DENY

        db.set_authorizer(authorize)
        db.set_progress_handler(budget, 1000)
    return db


@lru_cache(maxsize=1)
def schema() -> dict:
    tables = []
    with closing(connect(False)) as db:
        for name, description in DESCRIPTIONS.items():
            columns = [{"name": r[1], "type": r[2], "nullable": not bool(r[3] or r[5]), "primary_key": bool(r[5])} for r in db.execute(f'PRAGMA table_info("{name}")')]
            if not columns:
                raise sqlite3.DatabaseError("Sample database is incomplete.")
            fks = [{"column": r[3], "references_table": r[2], "references_column": r[4]} for r in db.execute(f'PRAGMA foreign_key_list("{name}")')]
            indexes = []
            for idx in db.execute(f'PRAGMA index_list("{name}")').fetchall():
                indexes.append({"name": idx[1], "columns": [r[2] for r in db.execute(f'PRAGMA index_info("{idx[1]}")')], "unique": bool(idx[2])})
            tables.append({"name": name, "description": description, "columns": columns, "foreign_keys": fks, "indexes": indexes, "row_count": db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]})
    return {"name": "Northstar Commerce", "description": "Synthetic commerce data · 2023–2025 · USD", "engine": "sqlite", "tables": tables, "examples": ["Show customers in California", "Monthly revenue for 2025", "Show all employees hired after January 2024", "Top 5 products by revenue"]}


def mapping():
    return {t["name"]: {c["name"]: c["type"] for c in t["columns"]} for t in schema()["tables"]}


def relationships():
    return {(t["name"], fk["column"], fk["references_table"], fk["references_column"]) for t in schema()["tables"] for fk in t["foreign_keys"]}


def query_plan(sql: str) -> dict:
    with closing(connect()) as db:
        rows = db.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    plan = [{"id": r[0], "parent": r[1], "detail": r[3]} for r in rows]
    scans = sum("SCAN " in r["detail"].upper() for r in plan)
    searches = sum("SEARCH " in r["detail"].upper() for r in plan)
    sorts = sum("TEMP B-TREE" in r["detail"].upper() for r in plan)
    level = "high" if scans > 1 or (scans and sorts) else "medium" if scans or sorts else "low"
    return {"level": level, "summary": f"{scans} scan(s), {searches} indexed search(es), {sorts} temporary sort(s)", "plan": plan, "scans": scans, "searches": searches, "temporary_sorts": sorts, "caveat": "Relative SQLite planner heuristic on small synthetic data, not currency, a production latency prediction, or a native PostgreSQL/MySQL cost."}


def execute(sql: str) -> dict:
    started = time.monotonic()
    with closing(connect()) as db:
        cursor = db.execute(sql)
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchmany(501)
    def scalar(value):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return value
    return {"columns": columns, "rows": [[scalar(v) for v in r] for r in rows[:500]], "row_count": min(len(rows), 500), "truncated": len(rows) > 500, "elapsed_ms": round((time.monotonic() - started) * 1000, 2), "engine": "sqlite", "max_rows": 500}
