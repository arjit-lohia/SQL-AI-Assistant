# Architecture and behavior specification

Status: COMPLETE before application implementation.

## Runtime and deployment

One Vercel project serves a Vite/React/TypeScript frontend and a Python FastAPI function at `/api`. `vercel.json` routes API requests to `api/index.py`, includes `backend/**`, `prompts/**` and `data/sample.db`, and serves frontend assets from `dist`. Python 3.12. Local FastAPI also serves built frontend for Docker and browser verification. Use Python stdlib sqlite3, SQLGlot for AST parsing/qualification/transpilation and LangGraph for orchestration. An HTTP Groq chat completion call uses `GROQ_API_KEY` only on the server; model configurable through `GROQ_MODEL`. No vendor key reaches the browser.

The sample database is an immutable deployment asset, not a writable serverless filesystem database. Seed locally/build time, commit the small deterministic artifact and open via SQLite URI `mode=ro&immutable=1`. No remote database provision is necessary. Conversations and saved UI preferences live in browser localStorage; each request sends a bounded context window. This avoids reliance on process-local memory on Vercel and isolates browser sessions. A future authenticated multi-device history would use a durable remote store.

## Dataset

Synthetic Northstar Commerce dataset: departments (id/name), employees (id/name/email/department_id/hire_date/salary), customers (id/name/email/city/state/created_at), products (id/name/category/price), orders (id/customer_id/employee_id/order_date/status), order_items (id/order_id/product_id/quantity/unit_price). Foreign keys are declared and enforced in seed. Deterministic dates cover 2023–2025; examples use explicit years. Seed about 120 customers, 24 employees, 18 products, 360 orders and 900 line items. Explain revenue as non-cancelled order-item quantity × historical unit_price; do not confuse current product price with sales value. Seed include California customers and post-January-2024 employees.

## Agent state and graph

State includes request, dialect, bounded history, intent, schema, candidate, validated SQL, SQLite equivalent, explanation, diagnostics, recommendations, plan, result, repair count, response and completed steps. No checkpointer containing shared user data is used.

1. `detect_intent`: classify generate/optimize/debug/follow-up; capture supplied SQL as data.
2. `validate_scope`: deterministic deny of writes/instruction overrides; live classifier or scoped generation makes semantic refusal/clarification decisions. Keyless mode only handles supported sample patterns and pasted queries; other in-schema requests receive a limitation/clarification, never fake AI output.
3. `retrieve_schema`: load introspected schema from the actual database with trusted descriptions and FK list.
4. `generate_sql`: validated structured model response or deterministic sample planner. Debug first records actual validation issue for supplied SQL. Live model gets that issue. Correct obvious unambiguous typos in keyless mode.
5. `validate_sql`: single read-only AST; table and column qualification including CTE/subquery scopes; table-valued/system/external access blocked; only allowlisted pure functions; every join must have a declared FK equality (extra predicates allowed); no cross/natural joins or recursion; compile translated SQLite using EXPLAIN. One model repair attempt; then fail closed.
6. `optimize_sql`: safe formatting; remove only unused simple many-to-one LEFT JOIN whose RHS PK equality makes removal safe. Revalidate output. Generate advisory indexes as prose, never executable CREATE SQL. Cost plan from SQLite.
7. `execute_sql`: optional, only on validated SQL; guarded read-only connection with authorizer, instruction budget/deadline, max 500 rows plus sentinel. Refusal/error never enters this node.
8. `explain_sql`: final explanation, diagnostic and assumptions, sample-engine disclosure, provider label and trace. LLM explanation is derived from accepted SQL; fallback clause-based description must match accepted query.

Stream graph node completion events and validated explanation text as SSE. Only final validated SQL is serialized to the user. Stream endpoint must produce a terminal result/error, handle disconnect and avoid exposing internal state/prompts/keys. Do not claim raw model token streaming: streaming is graph progress and validated response text.

## Safety and resource bounds

Request max 4,000 characters, SQL max 12,000 characters, 16 history turns/24,000 total context chars, enum dialect, Pydantic extra forbid. Read-only SELECT AST allowlist and side-effect denylist; pure scalar/aggregate/window function allowlist. No metadata/system table access, file functions, extensions, attached databases, network functions, SELECT INTO, row locks, recursive CTEs, DDL/DML even nested. Limit nesting/AST size. Validate schema and join semantics outside the LLM. SQLite authorizer denies all actions except bounded reads of known tables and safe functions; EXPLAIN runs under same controls. Progress handler aborts expensive execution. API execution always repeats validation of client-submitted SQL. Runtime errors redact secrets and provider bodies. Body-size middleware bounds incoming JSON, same-origin API, provider timeout and bounded retries. No per-process rate limit marketed as a global abuse solution; optional shared access token can gate paid AI on a public demo, and hosting rate controls are documented.

## UI

Desktop analytical workspace with slim left navigation/history, white/light warm background, ink typography, teal accent, schema explorer drawer and split conversation/query workspace. Header: QueryAtlas, dataset connection status, engine selector, theme. Initial greeting and example cards: customers in California, monthly 2025 revenue, recent employees, top products. Composer supports multiline input, Enter submit/Shift+Enter newline, mode selector, auto-run toggle and disabled/loading state. Query workspace: SQL with line numbers, copy/download; tabs Results/Explanation/Query plan; Run button, row count, runtime, truncation note and CSV download. Conversation can be renamed through first message, selected, created, deleted individually and cleared with explicit local confirmation. Query outputs selected from conversation history must remain tied to the selected turn. Responsive mobile stacks panes and collapses navigation. Keyboard-visible focus, semantic buttons/form labels, reduced-motion support, contrast, aria-live progress/errors. Theme and conversations survive refresh.
