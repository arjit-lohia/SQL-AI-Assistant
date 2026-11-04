# Runtime workflow and prompts

`backend/agent.py` compiles `langgraph.graph.StateGraph(State)` once. Each HTTP request supplies fresh state; there is no global message memory or user-data checkpointer. `run_events` streams actual node updates and projects only public progress plus the terminal response. `api/index.py` serves both nonstream JSON and SSE from that same graph.

| Node | Actual behavior and route |
| --- | --- |
| detect_intent | Uses selected generate/optimize/debug mode and follow-up markers. |
| validate_scope | Blocks recognized unrelated requests, destructive/injected instructions and parsed writes. With live AI, unfamiliar business wording is passed to the schema-constrained model for semantic refusal/clarification instead of requiring an exact keyword match. Refusal routes straight to explain_sql. |
| retrieve_schema | Introspects actual bundled tables/FKs/indexes; revalidates latest assistant SQL in its original dialect and converts it to canonical SQLite. Bad context terminates safely. |
| generate_sql | Live structured Groq proposal or explicitly labeled deterministic sample planner. Diagnoses pasted SQL first. Valid optimize/debug input is retained for deterministic optimization, avoiding unproven model rewrites. |
| validate_sql | SQLGlot AST/scoped schema/FK/function checks and guarded SQLite compilation, plus a check for lost filters in additive single-table refinements. Success → optimize_sql; initial live-model failure → repair_sql; subsequent failure → explain_sql with no SQL. |
| repair_sql | One additional strict model proposal with safe validation diagnostics. Success proposal returns to validate_sql; refusal/clarification/provider error terminates. |
| optimize_sql | Formatting, narrowly proven unused LEFT JOIN removal, revalidation, index advice and actual EXPLAIN QUERY PLAN. |
| execute_sql | Optional when auto-run enabled; guarded immutable SQLite, deadline/instruction budget, 500-row cap. |
| explain_sql | Derives explanation from the final accepted SQL and shapes success/refusal/clarification/error. Failed paths have null SQL/result/cost. |

The graph recursion limit is 24; provider requests are bounded to 18 seconds each (connect 5 seconds), with a maximum two provider calls per turn. Database work uses separate bounded connections. API errors redact raw model/SQL/parser traces. Structured responses reject extra fields, invalid status/SQL combinations and oversized notes.

Exact prompts: [system.txt](../prompts/system.txt) and [repair.txt](../prompts/repair.txt). `backend/provider.py` reads these files at runtime and sends the structured `payload()` from agent.py: task, output dialect, message, revalidated canonical previous SQL, trusted actual schema, bounded history and validation issue. Provider URL is fixed; neither a user nor model can select a network endpoint or database path. No model tool executes SQL.

SSE emits allowlisted progress labels. Explanation text is emitted incrementally only after acceptance; the final result is authoritative. This is graph-progress and validated-response streaming, not unvalidated model-token streaming. The browser supports abort, chunk buffering and terminal-event checks.

Keyless mode shares every guard and graph node but handles only documented patterns and narrow corrections. A configured provider failure does not fall back silently. Mock provider tests verify repair/failure contracts; without a real key, live model quality/connectivity is explicitly unverified.

Architecture: [rendered SVG](architecture.svg), [Mermaid source](architecture.mmd). Detailed design and acceptance: [specs](../specs/README.md).

## State and model-input construction

The typed `State` carries the validated `ChatRequest`, intent, trusted schema, revalidated canonical previous SQL, untrusted `ModelOutput` candidate, validator-owned accepted SQL, diagnostics, suggestions, repair count, actual plan/results and terminal response. Each request begins with fresh state. A new candidate is never treated as validated merely because it appears in history or a model response.

`payload()` builds the actual model input as a JSON data object with `task`, `dialect`, `message`, `previous_sql`, `schema`, bounded `history` and `validation_issue`. `provider.propose()` sends the exact versioned system prompt as the system message and this JSON as the user message. A repair call appends the versioned repair instruction. No API key is part of either message: the key is used only in the server-to-provider Authorization header.

The generation branch accepts a strict success/refusal/clarification model object. Refusal and clarification terminate without SQL. SQL validation failure can trigger one repair when a live provider is configured; another failure terminates safely. The optimizer only applies a proven redundant-LEFT-JOIN rewrite and revalidates it. Execution is a separate optional node and a separately validating endpoint. The explanation is derived from the final accepted SQL, avoiding stale model explanations after optimization.

Related design contracts: [agent/prompt specification](../specs/08-agent-and-prompts.md), [API model](../specs/03-api.md), [validation/guardrails](../specs/10-sql-validation-and-guardrails.md) and [context](../specs/12-conversation-and-context.md).

## Dialects and follow-ups

The workspace selector chooses SQLite, PostgreSQL or MySQL syntax for the next request. Previous SQL is always validated in its original dialect and canonicalized to SQLite before refining. Existing responses/downloads keep their own dialect; actual execution and costs remain SQLite-based.

After customers from Austin, a joined-before refinement adds an account-creation cutoff without removing Austin. Sample mode composes this through the AST, with an explicit assumption about what joined means. Live generation receives the same previous SQL even for follow-ups beginning with Show. The [context checker](../backend/context.py) compares top-level WHERE conjuncts for simple single-table additive refinements, normalizing column aliases. Missing conditions trigger the existing bounded repair; repeated failure returns no SQL/results. Explicit replacement/reset, supplied SQL and changes to another table are excluded. This conservative check may reject equivalent predicate rewrites; complex joins/subqueries still rely on model interpretation plus schema validation, not a general semantic proof. See [specification 18](../specs/18-dialects-follow-ups-and-setup.md).
