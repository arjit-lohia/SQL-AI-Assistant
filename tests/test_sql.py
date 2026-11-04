import hashlib
import sqlite3
from contextlib import closing
import pytest
from backend import database
from backend.sql import validate, optimize, explain, InvalidSQL


@pytest.mark.parametrize("sql", [
    "DELETE FROM customers", "UPDATE customers SET name='x'", "INSERT INTO customers(id) VALUES(9)",
    "DROP TABLE orders", "ALTER TABLE orders ADD x TEXT", "TRUNCATE TABLE orders",
    "SELECT id FROM customers; DROP TABLE customers", "SELECT id INTO backup FROM customers",
    "WITH x AS (DELETE FROM customers RETURNING *) SELECT * FROM x", "PRAGMA table_info(customers)",
    "SELECT * FROM sqlite_master", "SELECT * FROM sqlite_schema", "SELECT * FROM pragma_table_info('customers')",
    "SELECT readfile('/etc/passwd') FROM customers", "SELECT load_extension('x') FROM customers",
    "SELECT sleep(10) FROM customers", "SELECT * FROM other.customers", "SELECT * FROM unknown",
    "SELECT phone FROM customers", "SELECT name FROM customers c JOIN orders o ON c.id=o.id",
    "SELECT c.id FROM customers c CROSS JOIN orders o", "SELECT c.id FROM customers c, orders o",
    "SELECT c.id FROM customers c JOIN orders o ON c.id=o.customer_id OR 1=1",
    "WITH RECURSIVE x(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM x) SELECT * FROM x",
    "SELECT id FROM customers c JOIN orders o ON c.id=o.customer_id", "SELECT id FROM customers FOR UPDATE",
])
def test_reject(sql):
    with pytest.raises(InvalidSQL):
        validate(sql)


@pytest.mark.parametrize("sql", [
    "SELECT name FROM customers WHERE state='California'",
    "SELECT name FROM customers WHERE name='Drop' OR name='Update'",
    "SELECT c.id FROM customers c JOIN orders o ON o.customer_id=c.id",
    "SELECT c.id FROM customers c JOIN orders o ON c.id=o.customer_id AND o.status='completed'",
    "WITH c AS (SELECT id, name FROM customers) SELECT name FROM c",
    "SELECT name FROM customers WHERE id IN (SELECT customer_id FROM orders)",
    "SELECT c.name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.id)",
    "SELECT state, COUNT(*) AS total FROM customers GROUP BY state ORDER BY total DESC",
    "SELECT name, ROW_NUMBER() OVER (ORDER BY id) AS n FROM customers",
    "SELECT id FROM customers UNION SELECT id FROM employees",
])
def test_accept(sql):
    q = validate(sql)
    assert database.execute(q.sqlite)["row_count"] >= 0


def test_safe_join_removal():
    q = validate("SELECT o.id FROM orders o LEFT JOIN customers c ON o.customer_id=c.id ORDER BY o.id")
    rewritten, notes, _, _ = optimize(q, "sqlite")
    assert "JOIN" not in rewritten.sql
    assert notes
    assert database.execute(q.sqlite)["rows"] == database.execute(rewritten.sqlite)["rows"]


@pytest.mark.parametrize("sql", [
    "SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id=c.id",
    "SELECT o.id,c.name FROM orders o LEFT JOIN customers c ON o.customer_id=c.id",
    "SELECT o.id FROM orders o LEFT JOIN customers c ON o.customer_id=c.id WHERE c.state='California'",
    "SELECT * FROM orders o LEFT JOIN customers c ON o.customer_id=c.id",
    "SELECT o.id FROM orders o INNER JOIN customers c ON o.customer_id=c.id",
])
def test_unsafe_join_removal_not_applied(sql):
    rewritten, notes, _, _ = optimize(validate(sql), "sqlite")
    assert "JOIN" in rewritten.sql
    assert not notes


def test_authorizer_and_immutable():
    before = hashlib.sha256(database.DB_PATH.read_bytes()).digest()
    with closing(database.connect()) as db:
        for sql in ["DELETE FROM customers", "SELECT * FROM sqlite_master", "PRAGMA user_version", "ATTACH DATABASE ':memory:' AS x"]:
            with pytest.raises(sqlite3.DatabaseError):
                db.execute(sql)
    assert hashlib.sha256(database.DB_PATH.read_bytes()).digest() == before


def test_row_limit_and_zero():
    q = validate("SELECT * FROM order_items ORDER BY id")
    result = database.execute(q.sqlite)
    assert result["row_count"] == 500 and result["truncated"]
    empty = database.execute(validate("SELECT name FROM customers WHERE id=-1").sqlite)
    assert empty["rows"] == [] and empty["columns"] == ["name"]


def test_indexes_and_plan():
    _, _, advice, plan = optimize(validate("SELECT name FROM customers WHERE state='California'"), "sqlite")
    assert any("already" in a for a in advice)
    assert plan["plan"] and plan["searches"] >= 1 and "heuristic" in plan["caveat"]


def test_schema_integrity():
    counts = {t["name"]: t["row_count"] for t in database.schema()["tables"]}
    assert counts == {"departments":4,"employees":24,"customers":120,"products":18,"orders":360,"order_items":900}
    with closing(database.connect(False)) as db:
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_execution_deadline():
    with closing(database.connect(timeout=0)) as db:
        with pytest.raises(sqlite3.OperationalError, match="interrupted"):
            # Exercise the DB guard independently with enough VM work to hit its
            # callback interval; the public AST validator separately rejects this join.
            db.execute("SELECT SUM(a.quantity * b.quantity) FROM order_items a, order_items b").fetchone()


def test_ast_bounds():
    expression = "SELECT " + ",".join(f"id + {i} AS n{i}" for i in range(160)) + " FROM customers"
    with pytest.raises(InvalidSQL, match="complex"):
        validate(expression)


def test_nested_join_and_nonexistent_scoped_source():
    for text in ["WITH c AS (SELECT id FROM imaginary) SELECT id FROM c", "SELECT name FROM customers WHERE id IN (SELECT fake_id FROM orders)"]:
        with pytest.raises(InvalidSQL):
            validate(text)


def test_explanations_distinguish_dates_and_numbers():
    assert "on or after January 1, 2024" in explain(validate("SELECT name FROM employees WHERE hire_date >= '2024-01-01'"))
    assert "salary is at least 70000" in explain(validate("SELECT name FROM employees WHERE salary >= 70000"))


def test_seed_is_repeatable_and_does_not_change_bundled_database(tmp_path,monkeypatch):
    from scripts import seed
    original = hashlib.sha256(database.DB_PATH.read_bytes()).digest()
    (tmp_path / "data").mkdir()
    (tmp_path / "data/schema.sql").write_text((database.ROOT / "data/schema.sql").read_text(), encoding="utf-8")
    monkeypatch.setattr(seed,"ROOT",tmp_path)
    seed.build()
    first = (tmp_path / "data/sample.db").read_bytes()
    seed.build()
    assert first == (tmp_path / "data/sample.db").read_bytes()
    assert hashlib.sha256(database.DB_PATH.read_bytes()).digest() == original
