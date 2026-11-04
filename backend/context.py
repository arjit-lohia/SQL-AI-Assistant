"""Conservative checks for additive refinements; not a SQL equivalence prover."""
import re
import sqlglot
from sqlglot import exp
from backend.sql import InvalidSQL


def resets_context(message: str) -> bool:
    return bool(re.search(
        r"\b(?:instead|rather than|start over|new query|from scratch|"
        r"(?:remove|clear|ignore|replace|without)\b.{0,40}\b(?:filter|condition|restriction)s?|"
        r"all (?:the )?(?:customers|people|employees))\b", message, re.I
    ))


def _simple_table(tree):
    tables = list(tree.find_all(exp.Table))
    if not isinstance(tree, exp.Select) or len(tables) != 1:
        return None
    if tree.args.get("with_") or tree.args.get("joins") or tree.find(exp.Subquery):
        return None
    return tables[0].name.lower()


def _conjuncts(node):
    if isinstance(node, exp.Paren):
        return _conjuncts(node.this)
    if isinstance(node, exp.And):
        return _conjuncts(node.this) + _conjuncts(node.expression)
    normalized = node.copy()
    for column in normalized.find_all(exp.Column):
        column.set("table", None)
        column.set("this", exp.to_identifier(column.name.lower()))
    return [normalized]


def check_preserved_filters(previous: str | None, candidate: str, message: str, mode: str):
    if not previous or mode != "generate" or resets_context(message):
        return
    if re.match(r"\s*(?:select|with)\b", message, re.I):
        return  # Explicit supplied SQL defines a new query.
    before = sqlglot.parse_one(previous, read="sqlite")
    after = sqlglot.parse_one(candidate, read="sqlite")
    source = _simple_table(before)
    if not source or source != _simple_table(after) or not before.args.get("where"):
        return
    required = _conjuncts(before.args["where"].this)
    actual = _conjuncts(after.args["where"].this) if after.args.get("where") else []
    if any(term not in actual for term in required):
        raise InvalidSQL(
            "This follow-up dropped an earlier filter. Retain every previous WHERE "
            "condition and add the requested refinement, unless the user explicitly replaces it."
        )
