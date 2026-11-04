"""Explicitly limited keyless examples, never marketed as live model reasoning."""
import difflib
import re
import sqlglot
from sqlglot import exp
from backend.models import ModelOutput
from backend import database


def candidate(sql, assumptions=None):
    return ModelOutput(status="success", sql=sql, assumptions=assumptions or [], message="Validated SQL is ready.")


def sample_answer(message: str, mode: str, previous: str | None):
    text = message.lower().strip()
    pasted = re.search(r"\b(select|with)\b", message, re.I)
    if pasted:
        sql = message[pasted.start():].strip().strip("`").strip()
        if mode == "debug":
            # Only unique close schema spellings; the full validator remains final.
            try:
                tree = sqlglot.parse_one(sql, read="sqlite")
                tables = list(database.mapping())
                for table in tree.find_all(exp.Table):
                    if table.name.lower() not in tables:
                        matches = difflib.get_close_matches(table.name.lower(), tables, n=2, cutoff=0.72)
                        if len(matches) != 1:
                            return ModelOutput(status="clarification", message="Which existing table did you mean? Please check the schema explorer.")
                        table.set("this", exp.to_identifier(matches[0]))
                selected = {t.name.lower() for t in tree.find_all(exp.Table)}
                columns = {name for table in selected for name in database.mapping().get(table, {})}
                for col in tree.find_all(exp.Column):
                    if col.name.lower() not in columns:
                        normalized = [c for c in columns if c.replace("_", "") == col.name.lower().replace("_", "")]
                        matches = normalized or difflib.get_close_matches(col.name.lower(), sorted(columns), n=2, cutoff=0.75)
                        if len(matches) != 1:
                            return ModelOutput(status="clarification", message="The correction is ambiguous. Which schema column did you mean?")
                        col.set("this", exp.to_identifier(matches[0]))
                sql = tree.sql(dialect="sqlite")
            except sqlglot.errors.SqlglotError:
                return ModelOutput(status="clarification", message="Sample mode can correct clear table/column typos. Configure GROQ_API_KEY for more complex syntax debugging.")
        return candidate(sql)
    if re.search(r"\b(best|active|recent|sales|expensive)\b", text) and not ("revenue" in text or "2024" in text):
        return ModelOutput(status="clarification", message="Which metric and time period should define that request? For example: top customers by non-cancelled revenue in 2025.")
    # Narrow refinements compose through an AST rather than replacing prior SQL.
    if previous and (re.match(r"^(only|just|sort|order|limit|instead|now|show (?:only|the (?:first|top)))\b", text)):
        tree = sqlglot.parse_one(previous, read="sqlite")
        real_tables = [t for t in tree.find_all(exp.Table) if t.name.lower() in database.mapping()]
        customer = next((t for t in real_tables if t.name.lower() == "customers"), None)
        if "california" in text and customer:
            tree = tree.where(exp.column("state", table=customer.alias_or_name).eq("California"), append=True)
        elif re.search(r"sort|order", text) and "name" in text and customer:
            tree.set("order", exp.Order(expressions=[exp.Ordered(this=exp.column("name", table=customer.alias_or_name), desc="desc" in text)]))
        elif (limit := re.search(r"(?:first|top|limit|only)\s+(\d{1,3})", text)):
            tree = tree.limit(int(limit.group(1)))
        elif "completed" in text and any(t.name.lower() == "orders" for t in real_tables):
            target = next(t for t in real_tables if t.name.lower() == "orders")
            for node in list(tree.find_all(exp.NEQ)):
                if isinstance(node.left, exp.Column) and node.left.name == "status":
                    node.replace(node.left.copy().eq("completed"))
            tree = tree.where(exp.column("status", table=target.alias_or_name).eq("completed"), append=True)
        else:
            return ModelOutput(status="clarification", message="Please specify the field and filter to apply. Full conversational refinements require GROQ_API_KEY on the server.")
        return candidate(tree.sql(dialect="sqlite"))
    if re.match(r"^(only|just|sort|instead)\b", text) and not previous:
        return ModelOutput(status="clarification", message="Which records should I refine? Start with a query such as 'Show all customers'.")
    if re.fullmatch(r"(?:show|list|find|get)(?: me)?(?: all)? customers(?: (?:in|from) california)?[.!?]?", text):
        conditions = " WHERE state = 'California'" if "california" in text else ""
        return candidate("SELECT id, name, email, city, state, created_at FROM customers" + conditions)
    if "employee" in text and "2024" in text and re.search(r"(?:after|since|on or after) january", text):
        return candidate("SELECT id, name, email, department_id, hire_date, salary FROM employees WHERE hire_date >= '2024-01-01' ORDER BY hire_date", ["This query uses the specified inclusive January 1, 2024 boundary."])
    if "monthly" in text and "revenue" in text and "2025" in text:
        return candidate("SELECT STRFTIME('%Y-%m', o.order_date) AS month, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue FROM orders o JOIN order_items oi ON oi.order_id = o.id WHERE o.order_date >= '2025-01-01' AND o.order_date < '2026-01-01' AND o.status <> 'cancelled' GROUP BY STRFTIME('%Y-%m', o.order_date) ORDER BY month", ["Revenue includes completed and processing orders; cancelled orders are excluded. Values are synthetic USD."])
    if "top" in text and "product" in text and "revenue" in text:
        n = int(re.search(r"\b(\d{1,2})\b", text).group(1)) if re.search(r"\b(\d{1,2})\b", text) else 5
        return candidate(f"SELECT p.name, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON oi.order_id = o.id WHERE o.status <> 'cancelled' GROUP BY p.id, p.name ORDER BY revenue DESC, p.name LIMIT {n}", ["Revenue uses historical order-item prices across 2024–2025, excluding cancelled orders."])
    if re.fullmatch(r"(?:count|how many)(?: all)? (?:departments|employees|customers|products|orders|order_items)(?: are there)?[.!?]?", text):
        names = [t for t in database.mapping() if re.search(r"\b" + t + r"\b", text)]
        if len(names) == 1:
            return candidate(f"SELECT COUNT(*) AS total FROM {names[0]}")
    return ModelOutput(status="clarification", message="I can help with the supplied schema. Sample mode supports the example questions and pasted SELECT queries. Configure GROQ_API_KEY on the server for full natural-language generation, or specify an existing table and field.")
