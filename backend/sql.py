"""LLM-independent AST/schema/FK validation. No candidate is trusted."""
from contextlib import closing
from dataclasses import dataclass
from datetime import date
import sqlite3
import sqlglot
from sqlglot import exp, ErrorLevel
from sqlglot.errors import SqlglotError
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import traverse_scope, Scope
from backend import database


class InvalidSQL(ValueError):
    pass


CHECKS = ["Single read-only statement", "Syntax checked", "Tables and columns verified", "Foreign-key joins verified", "Functions allowlisted", "SQLite compilation passed"]
BLOCKED = frozenset("Insert Update Delete Drop Alter Create TruncateTable Merge Command Into Lock Transaction Commit Rollback Pragma Attach Detach Copy Grant Revoke Execute Use Set LoadData Parameter Placeholder SessionParameter".split())
FUNCTIONS = frozenset("ABS AVG CEIL CEILING COALESCE CONCAT CONCAT_WS COUNT DATE DATETIME DATE_ADD DATE_SUB DATEDIFF DATE_DIFF DATE_TRUNC DENSE_RANK EXTRACT FIRST_VALUE FLOOR GROUP_CONCAT IF IFNULL IIF INSTR JULIANDAY LAG LAST_VALUE LEAD LENGTH LOWER LTRIM MAX MIN MOD NTH_VALUE NTILE NULLIF PERCENT_RANK RANK REPLACE ROUND ROW_NUMBER RTRIM SIGN SQRT STRFTIME SUBSTR SUBSTRING SUM TIME TIME_TO_STR TIMESTAMP_TO_TIME TOTAL TRIM TRY_CAST CAST TYPEOF UNIXEPOCH UPPER CUME_DIST JSON_EXTRACT JSON_ARRAY_LENGTH".split())


@dataclass
class Validated:
    sql: str
    sqlite: str
    tree: exp.Expression
    qualified: exp.Expression


def _structure(tree):
    if not isinstance(tree, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise InvalidSQL("Only a read-only SELECT query or non-recursive CTE is allowed.")
    nodes = list(tree.walk())
    if len(nodes) > 600:
        raise InvalidSQL("This query is too complex. Please simplify it.")
    for node in nodes:
        if node.__class__.__name__ in BLOCKED:
            raise InvalidSQL("Only read-only queries are supported. Data changes and administrative operations are refused.")
        if isinstance(node, exp.With) and node.args.get("recursive"):
            raise InvalidSQL("Recursive CTEs are outside the sample execution limits.")
        if isinstance(node, exp.Table):
            if node.db or node.catalog or not isinstance(node.this, exp.Identifier):
                raise InvalidSQL("External databases and table functions are not allowed.")
        if isinstance(node, exp.Func):
            name = node.name.upper() if isinstance(node, exp.Anonymous) else node.sql_name()
            if name not in FUNCTIONS and name not in {"AND", "OR", "CASE", "IF", "EXISTS", "TS_OR_DS_TO_TIMESTAMP", "TS_OR_DS_TO_DATE", "STR_TO_TIME"}:
                raise InvalidSQL(f"The function {name} is not in the approved read-only function list.")
    # Explicit nesting limit, independent of SQL length/AST count.
    for node in nodes:
        depth, parent = 0, node.parent
        while parent:
            depth += 1
            if depth > 40:
                raise InvalidSQL("The query is nested too deeply.")
            parent = parent.parent


def _sources_and_joins(tree):
    tables = database.mapping()
    fks = database.relationships()
    for scope in traverse_scope(tree):
        sources = {}
        for alias, (_, source) in scope.selected_sources.items():
            if isinstance(source, exp.Table):
                name = source.name.lower()
                if name not in tables:
                    raise InvalidSQL(f"Table '{name}' is not in the provided schema.")
                sources[alias.lower()] = name
            elif not isinstance(source, Scope):
                raise InvalidSQL("Unsupported query source.")
        for join in scope.expression.args.get("joins") or []:
            on = join.args.get("on")
            if join.args.get("method") == "NATURAL" or join.args.get("kind") == "CROSS" or not on:
                raise InvalidSQL("Joins must use an explicit declared foreign-key relationship.")
            if any(isinstance(n, exp.Or) for n in on.walk()):
                raise InvalidSQL("Join OR conditions cannot establish a safe foreign-key relationship.")
            target = join.this.alias_or_name.lower()
            valid = False
            for term in on.flatten() if isinstance(on, exp.And) else [on]:
                if not isinstance(term, exp.EQ) or not isinstance(term.left, exp.Column) or not isinstance(term.right, exp.Column):
                    continue
                left, right = term.left, term.right
                a, b = left.table.lower(), right.table.lower()
                if target not in (a, b) or a == b:
                    continue
                key = (sources.get(a), left.name.lower(), sources.get(b), right.name.lower())
                if key in fks or (key[2], key[3], key[0], key[1]) in fks:
                    valid = True
            if not valid:
                raise InvalidSQL("Join keys must match a declared foreign key; unrelated id columns or derived relationships cannot be assumed.")


def validate(sql: str, dialect: str = "sqlite") -> Validated:
    if not sql.strip() or len(sql) > 12000:
        raise InvalidSQL("SQL must contain 1–12,000 characters.")
    if dialect not in {"sqlite", "postgres", "mysql"}:
        raise InvalidSQL("Choose SQLite, PostgreSQL or MySQL.")
    try:
        statements = sqlglot.parse(sql, read=dialect, error_level=ErrorLevel.RAISE)
        if len(statements) != 1 or statements[0] is None:
            raise InvalidSQL("Exactly one read-only SQL statement is allowed.")
        tree = statements[0]
        _structure(tree)
        # Resolve real sources before qualify can infer a fabricated relation.
        for scope in traverse_scope(tree):
            for _, source in scope.selected_sources.values():
                if isinstance(source, exp.Table) and source.name.lower() not in database.mapping():
                    raise InvalidSQL(f"Table '{source.name}' is not in the provided schema.")
        qualified = qualify(tree.copy(), dialect=dialect, schema=database.mapping(), validate_qualify_columns=True, quote_identifiers=False, identify=False)
        _sources_and_joins(qualified)
        sqlite_sql = qualified.sql(dialect="sqlite", unsupported_level=ErrorLevel.RAISE)
        _structure(sqlglot.parse_one(sqlite_sql, read="sqlite"))
        with closing(database.connect()) as db:
            db.execute("EXPLAIN " + sqlite_sql).fetchmany(1)
        return Validated(tree.sql(dialect=dialect, pretty=True, comments=False), sqlite_sql, tree, qualified)
    except InvalidSQL:
        raise
    except (SqlglotError, sqlite3.Error, ValueError, RecursionError) as exc:
        # SQLGlot parse errors embed raw candidate text; do not echo them.
        if isinstance(exc, sqlglot.errors.OptimizeError):
            reason = str(exc).split("\n")[0][:220]
            raise InvalidSQL(f"Schema validation: {reason}") from None
        if isinstance(exc, sqlite3.Error):
            raise InvalidSQL(f"SQLite validation: {str(exc)[:180]}") from None
        raise InvalidSQL("SQL syntax or dialect translation is invalid or unsupported. Check the selected dialect and schema.") from None


def optimize(value: Validated, dialect: str):
    tree = value.tree.copy()
    notes = []
    # Narrow proof: unused RHS of LEFT JOIN to a unique parent PK.
    if isinstance(tree, exp.Select) and not tree.find(exp.Star) and not tree.args.get("with_"):
        aliases = {t.alias_or_name.lower(): t.name.lower() for t in tree.find_all(exp.Table)}
        joins = list(tree.args.get("joins") or [])
        for join in joins:
            if join.side != "LEFT" or not isinstance(join.this, exp.Table):
                continue
            alias = join.this.alias_or_name.lower()
            on = join.args.get("on")
            if not isinstance(on, exp.EQ) or not all(isinstance(x, exp.Column) for x in [on.left, on.right]):
                continue
            rhs, lhs = (on.left, on.right) if on.left.table.lower() == alias else (on.right, on.left)
            key = (aliases.get(lhs.table.lower()), lhs.name.lower(), aliases.get(alias), rhs.name.lower())
            if key not in database.relationships():
                continue
            if any(not c.table or c.table.lower() == alias for c in tree.find_all(exp.Column) if not c.find_ancestor(exp.Join) is join):
                continue
            tree.set("joins", [j for j in tree.args.get("joins", []) if j is not join])
            notes.append(f"Removed unused LEFT JOIN to {aliases[alias]}; its primary key guarantees at most one matching row.")
    candidate = validate(tree.sql(dialect=dialect), dialect)
    cost = database.query_plan(candidate.sqlite)
    advice = []
    if tree.find(exp.Star):
        advice.append("Select only the columns you need instead of SELECT * to reduce transfer and clarify intent.")
    if cost["temporary_sorts"]:
        advice.append("The sample planner uses a temporary sort; an index aligned with filtering and ordering may reduce that work on larger data.")
    referenced = {t.name.lower() for t in candidate.tree.find_all(exp.Table)}
    where = candidate.qualified.find(exp.Where)
    if where:
        alias_map = {t.alias_or_name.lower(): t.name.lower() for t in candidate.qualified.find_all(exp.Table)}
        for col in where.find_all(exp.Column):
            name = alias_map.get(col.table.lower())
            meta = next((t for t in database.schema()["tables"] if t["name"] == name), None)
            if not meta:
                continue
            indexed = any(c["name"] == col.name and c["primary_key"] for c in meta["columns"]) or any(i["columns"] and i["columns"][0] == col.name for i in meta["indexes"])
            advice.append(f"{name}.{col.name} already has a leading index or primary key." if indexed else f"Consider an index on {name}.{col.name} for repeated selective filters; measure the plan before adding it.")
    if not advice:
        advice.append("Primary and foreign-key indexes are present in the sample. Recheck selectivity and plans on production-sized data.")
    return candidate, notes, list(dict.fromkeys(advice)), cost


def explain(value: Validated) -> str:
    def words(node):
        if isinstance(node, exp.Column):
            return node.name.replace("_", " ")
        if isinstance(node, (exp.Cast, exp.Alias, exp.Paren)):
            return words(node.this)
        if isinstance(node, exp.Literal):
            try:
                parsed = date.fromisoformat(node.this)
                return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"
            except ValueError:
                return str(node.this)
        if isinstance(node, exp.TimeToStr):
            fmt = node.args.get("format")
            return "calendar month" if fmt and fmt.this == "%Y-%m" else "formatted date"
        if isinstance(node, exp.And):
            return words(node.left) + "; and " + words(node.right)
        if isinstance(node, exp.Or):
            return "either " + words(node.left) + " or " + words(node.right)
        comparisons = {exp.EQ: "is", exp.NEQ: "is not", exp.GT: "is greater than", exp.GTE: "is at least", exp.LT: "is less than", exp.LTE: "is at most"}
        for cls, phrase in comparisons.items():
            if isinstance(node, cls):
                if isinstance(node.right, exp.Literal):
                    try:
                        date.fromisoformat(node.right.this)
                        phrase = {exp.GTE:"is on or after", exp.GT:"is after", exp.LT:"is before", exp.LTE:"is on or before", exp.EQ:"is", exp.NEQ:"is not"}[cls]
                    except ValueError:
                        pass
                return f"{words(node.left)} {phrase} {words(node.right)}"
        if isinstance(node, exp.In):
            return words(node.this) + " matches one of the requested values or subquery records"
        if isinstance(node, exp.Between):
            return f"{words(node.this)} is between {words(node.args['low'])} and {words(node.args['high'])}, inclusive"
        if isinstance(node, exp.Ordered):
            return words(node.this) + (" (highest first)" if node.args.get("desc") else " (ascending)")
        if isinstance(node, exp.Mul):
            return words(node.left) + " multiplied by " + words(node.right)
        if isinstance(node, exp.Sum):
            return "the total of " + words(node.this)
        if isinstance(node, exp.Count):
            return "the matching record count"
        if isinstance(node, exp.Round):
            return words(node.this)
        if isinstance(node, exp.Star):
            return "all available fields"
        # Keep uncommon clauses truthful while offering readable common cases.
        return node.sql(dialect="sqlite").replace("_", " ")

    tree = value.tree
    tables = list(dict.fromkeys(t.name for t in tree.find_all(exp.Table) if t.name.lower() in database.mapping()))
    parts = ["This read-only query retrieves data from " + ", ".join(t.replace("_", " ") for t in tables) + "."]
    where = tree.find(exp.Where)
    if where:
        parts.append("It keeps records where " + words(where.this) + ".")
    if tree.find(exp.Sum):
        parts.append("It totals the specified values; quantity multiplied by historical unit_price represents revenue.")
    if tree.find(exp.Count):
        parts.append("It counts the matching records within each requested group.")
    group = tree.find(exp.Group)
    if group:
        parts.append("Results are grouped by " + ", ".join(words(e) for e in group.expressions) + ".")
    order = tree.find(exp.Order)
    if order:
        parts.append("It sorts by " + ", ".join(words(e) for e in order.expressions) + ".")
    limit = tree.find(exp.Limit)
    if limit:
        parts.append(f"It returns at most {limit.expression.sql()} rows.")
    if tree.find(exp.Join):
        parts.append("Tables are linked using the declared foreign-key relationships.")
    return " ".join(parts)
