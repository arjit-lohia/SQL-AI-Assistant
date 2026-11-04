"""Actual LangGraph workflow; public state is projected only at completion."""
import re
import time
import unicodedata
from typing import TypedDict, Any
import sqlglot
from langgraph.graph import StateGraph, START, END
from backend import database, provider
from backend.models import ChatRequest, ModelOutput
from backend.sample import sample_answer
from backend.sql import validate, optimize, explain, InvalidSQL, CHECKS, BLOCKED


class State(TypedDict, total=False):
    request: ChatRequest
    intent: str
    schema: dict
    previous: str | None
    candidate: ModelOutput
    validated: Any
    diagnostics: list[str]
    suggestions: list[str]
    cost: dict
    result: dict
    repair_count: int
    failure: str
    response: dict


REFUSAL = "I'm designed to assist only with SQL and the supplied database schema. Please ask a read-only database question."


def detect_intent(s):
    req = s["request"]
    intent = req.mode
    if intent == "generate" and re.match(r"^(only|just|sort|instead|limit)\b", req.message.lower()):
        intent = "follow-up"
    return {"intent": intent, "diagnostics": [], "repair_count": 0}


def validate_scope(s):
    text = unicodedata.normalize("NFKC", s["request"].message).lower()
    injection = r"ignore\s+(?:all\s+)?(?:previous|prior|system|your)|(?:reveal|print|show|give).{0,30}(?:api.?key|system prompt|secret|environment variable)|(?:bypass|disable).{0,20}(?:validat|guardrail|safety)|you are now|<\|(?:system|im_start)"
    unrelated = r"\b(?:fifa|world cup|football|president|politics|poem|creative writing|capital of|weather|joke|python (?:script|code)|javascript (?:app|function))\b|\bwhat is\s+\d+\s*[+*/-]"
    # Pasted SELECT literals are handled structurally, avoiding 'Drop' literal false positives.
    write = r"\b(?:delete|remove|erase)\s+(?:all\s+)?(?:from\s+)?(?:customers|employees|orders|rows|records|data|table)|\b(?:drop|truncate|alter|create)\s+(?:the\s+)?(?:table|database|index|schema|customers|employees|orders)|\b(?:update|insert|replace|merge|grant|revoke|attach|detach)\s+(?:into\s+)?(?:customers|employees|orders|products|departments|order_items|table|database)"
    ast_write = False
    if re.match(r"\s*(?:select|with|delete|insert|update|drop|alter|truncate|create|pragma|attach|grant|revoke)\b", text):
        try:
            ast_write = any(n.__class__.__name__ in BLOCKED for tree in sqlglot.parse(s["request"].message) if tree for n in tree.walk())
        except sqlglot.errors.SqlglotError:
            pass
    known_scope = re.search(r"\b(?:sql|schema|database|table|column|query|queries|customers?|employees?|departments?|products?|orders?|order_items|revenue|hire|salary|state|index|join|select|with)\b", text)
    followup = re.match(r"^(only|just|sort|order|limit|instead|now|show (?:only|the))\b", text)
    if ast_write or re.search(injection, text) or re.search(unrelated, text) or (not re.match(r"\s*(select|with)\b", text) and re.search(write, text)) or (not known_scope and not followup and not provider.configured()):
        return {"failure": REFUSAL, "candidate": ModelOutput(status="refused", message=REFUSAL)}
    return {}


def retrieve_schema(s):
    previous = None
    for turn in reversed(s["request"].history):
        if turn.role == "assistant" and turn.sql:
            try:
                previous = validate(turn.sql, turn.dialect).sqlite
            except InvalidSQL:
                return {"failure": "Conversation SQL could not be verified. Start a new query using the current schema."}
            break
    return {"schema": database.schema(), "previous": previous}


def payload(s):
    r = s["request"]
    return {"task": s["intent"], "dialect": r.dialect, "message": r.message, "previous_sql": s.get("previous"), "schema": s["schema"], "history": [{"role": t.role, "content": t.content} for t in r.history], "validation_issue": s.get("diagnostics", [])}


async def generate_sql(s):
    r = s["request"]
    diagnostics = list(s.get("diagnostics", []))
    pasted = re.search(r"\b(select|with)\b", r.message, re.I)
    original_valid = None
    if pasted and r.mode in {"debug", "optimize"}:
        try:
            original_valid = validate(r.message[pasted.start():].strip().strip("`"), r.dialect)
            if r.mode == "debug":
                diagnostics.append("The supplied query is already valid against the sample schema.")
        except InvalidSQL as exc:
            diagnostics.append("Original query issue: " + str(exc))
    try:
        if original_valid and r.mode in {"optimize", "debug"}:
            # Never accept an unproven semantic rewrite of valid user SQL from an LLM.
            out = ModelOutput(status="success", sql=original_valid.sql)
        elif provider.configured():
            out = await provider.propose(payload({**s, "diagnostics": diagnostics}))
        else:
            # Pasted SQL is in the selected dialect; generated templates are SQLite.
            source_message = r.message
            if pasted and r.dialect != "sqlite" and r.mode == "debug":
                try:
                    source_message = sqlglot.transpile(r.message[pasted.start():], read=r.dialect, write="sqlite")[0]
                except sqlglot.errors.SqlglotError:
                    pass
            out = sample_answer(source_message, r.mode, s.get("previous"))
            if out.sql and (not pasted or r.mode == "debug") and r.dialect != "sqlite":
                out.sql = sqlglot.transpile(out.sql, read="sqlite", write=r.dialect)[0]
        return {"candidate": out, "diagnostics": diagnostics}
    except (provider.ProviderError, sqlglot.errors.SqlglotError) as exc:
        return {"failure": str(exc) if isinstance(exc, provider.ProviderError) else "The requested dialect translation is unsupported."}


def validate_sql(s):
    try:
        accepted = validate(s["candidate"].sql or "", s["request"].dialect)
        return {"validated": accepted, "failure": ""}
    except InvalidSQL as exc:
        return {"failure": str(exc), "diagnostics": [*s.get("diagnostics", []), str(exc)]}


async def repair_sql(s):
    try:
        out = await provider.propose(payload(s), repair=True)
        return {"candidate": out, "failure": "", "repair_count": 1}
    except provider.ProviderError as exc:
        return {"failure": str(exc), "repair_count": 1}


def optimize_sql(s):
    accepted, notes, advice, cost = optimize(s["validated"], s["request"].dialect)
    return {"validated": accepted, "diagnostics": [*s.get("diagnostics", []), *notes], "suggestions": advice, "cost": cost}


def execute_sql(s):
    return {"result": database.execute(s["validated"].sqlite)}


def explain_sql(s):
    out = s.get("candidate")
    success = bool(s.get("validated")) and not s.get("failure")
    status = "success" if success else out.status if out and out.status != "success" else "error"
    accepted = s.get("validated")
    response = {"status": status, "message": "Validated SQL is ready." if success else s.get("failure") or (out.message if out else "The query could not be completed."), "sql": accepted.sql if success else None, "dialect": s["request"].dialect, "explanation": explain(accepted) if success else "", "assumptions": out.assumptions if out and success else [], "diagnostics": s.get("diagnostics", []), "suggestions": s.get("suggestions", []) if success else [], "validation": {"valid": success, "checks": CHECKS if success else []}, "cost": s.get("cost") if success else None, "result": s.get("result") if success else None, "provider": "groq" if provider.configured() else "sample", "steps": [], "elapsed_ms": 0}
    return {"response": response}


def after_generation(s):
    return "explain_sql" if s.get("failure") or s.get("candidate").status != "success" else "validate_sql"


def after_validation(s):
    if not s.get("failure"):
        return "optimize_sql"
    return "repair_sql" if provider.configured() and s.get("repair_count", 0) == 0 else "explain_sql"


def compile_graph():
    graph = StateGraph(State)
    for fn in [detect_intent, validate_scope, retrieve_schema, generate_sql, validate_sql, repair_sql, optimize_sql, execute_sql, explain_sql]:
        graph.add_node(fn.__name__, fn)
    graph.add_edge(START, "detect_intent")
    graph.add_edge("detect_intent", "validate_scope")
    graph.add_conditional_edges("validate_scope", lambda s: "explain_sql" if s.get("failure") else "retrieve_schema")
    graph.add_conditional_edges("retrieve_schema", lambda s: "explain_sql" if s.get("failure") else "generate_sql")
    graph.add_conditional_edges("generate_sql", after_generation)
    graph.add_conditional_edges("repair_sql", after_generation)
    graph.add_conditional_edges("validate_sql", after_validation)
    graph.add_conditional_edges("optimize_sql", lambda s: "execute_sql" if s["request"].execute else "explain_sql")
    graph.add_edge("execute_sql", "explain_sql")
    graph.add_edge("explain_sql", END)
    return graph.compile()


GRAPH = compile_graph()
LABELS = {"detect_intent": "Understanding the request", "validate_scope": "Checking SQL-only scope", "retrieve_schema": "Retrieving the trusted schema", "generate_sql": "Preparing SQL", "validate_sql": "Validating SQL and relationships", "repair_sql": "Correcting a validation issue", "optimize_sql": "Optimizing and estimating work", "execute_sql": "Running read-only sample query", "explain_sql": "Explaining the accepted query"}


async def run_events(request: ChatRequest):
    started, steps = time.monotonic(), []
    async for update in GRAPH.astream({"request": request}, stream_mode="updates", config={"recursion_limit": 24}):
        for name, state in update.items():
            steps.append(name)
            yield "progress", {"step": name, "label": LABELS[name]}
            if state and "response" in state:
                result = state["response"]
                result["steps"] = steps.copy()
                result["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
                yield "result", result
