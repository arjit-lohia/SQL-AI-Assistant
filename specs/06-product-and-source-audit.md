# Product and specification audit

## Requirement coverage

| Requirement area | Coverage obligation | Detailed specification |
| --- | --- | --- |
| Product/runtime | SQL query agent, LangGraph orchestration, source, setup, architecture, prompts, schema and recorded demo | 01, 08, 16, 17 |
| Objective | Task-oriented schema-bound assistant; SQL-only scope; guardrails and usable UI | 08, 10, 13 |
| Business questions | SQL generation, validation, explanation and optional sample execution | 07, 09, 10, 14 |
| R01 generation | Natural language and the specified employee hire-date example | 09 |
| R02 validation | Existing tables/columns, correct joins/syntax, read-only; refuse destructive operations | 10 |
| R03 explanation | Plain-English meaning of the accepted query | 09, 13 |
| R04 optimization | Readability, performance/index advice and proven redundant-join removal | 11 |
| R05 debugging | Identify the original issue, explain it and validate the correction | 11 |
| R06 context | Customers → California refines the previous query | 12 |
| R07 scope | Refuse unrelated general knowledge, sports, politics, programming, mathematics and creative writing | 10, 15 |
| R08 frontend | Chat, SQL, explanation, history, loading, errors and copy SQL | 13 |
| Additional UI | Theme switch, streaming, SQL/results downloads and user-approved simplification | 13, 14, 05 |
| R09 backend | Actual LangGraph, FastAPI, relational database and schema-bound generation | 07, 08, 16 |
| R10 workflow | Intent → scope → schema → generation → validation → optimization → optional execution → explanation, with terminal refusal/clarification branches | 08 |
| Guardrails | No destructive SQL or invented schema; validate first and clarify ambiguity | 09, 10, 11 |
| Deliverables | All six requested local artifacts, plus recorded demo and preparation for deferred publication | 17 |
| Evaluation | Seven weighted quality categories | Evaluation table below; 15 |
| Additional features | Execution, follow-ups, plans, highlighting, dialect API support, CSV, injection protection, Docker and tests | Feature table below |
| Publication | GitHub/live app links remain deferred under amendment A01 | 16, 17, 05 |
| Quality | Focused agent, accurate translation, safety, intuitive UX and maintainable code | All specifications and release gates |

This audit maps the full product contract in specification 01 to the detailed specifications. The sample commerce schema is defined in specification 07; no production/private dataset is assumed.

## Users and journeys

- Business analyst: asks an English commerce question; reads the explanation; optionally runs it; downloads results without writing SQL.
- SQL reviewer: inspects schema and generated query, examines validation/query plans, and optimizes or debugs pasted SQL. The API supports additional output dialects.
- Technical reviewer: starts locally using README, confirms real LangGraph nodes and safeguards, tries follow-ups/refusals and inspects complete source and recording.

Primary journey: open app → inspect connected sample database → choose an example or type a question → see workflow progress → receive validated SQL and explanation → run → inspect real tabular results → export. Secondary journeys: optimize/debug, continue a conversation, inspect past turns, switch theme or recover from an error.

## Evaluation priorities

| Quality criterion | Weight | Evidence required |
| --- | --- | --- |
| Agent design | 25% | Actual LangGraph compile/invoke/stream; documented state, branches and bounded repair |
| SQL accuracy | 25% | Grounded prompts, deterministic schema, expected SQL/result fixtures and dialect tests |
| Validation / guardrails | 20% | AST/schema/FK/database checks; adversarial tests; fail-closed execution |
| Conversation | 10% | Follow-up acceptance tests and independent persistent histories |
| UI/UX | 10% | Accessible responsive working interface with real loading/errors |
| Code quality | 5% | Typed contracts, bounded functions, clean modules, pinned dependencies |
| Documentation | 5% | Reproducible README, diagram, exact prompts, assumptions and verified coverage |

## Additional feature coverage

| Feature | Planned proof |
| --- | --- |
| Execute SQL | Real SQLite results and authorizer/limit tests |
| Follow-up | California filter modifies latest validated customer query |
| Cost estimate | Real SQLite EXPLAIN plus explicit relative-estimate caveat |
| Highlighting | Safe SQL token components visible in output |
| Dialects | SQLite/PostgreSQL/MySQL API support with tested transpilation; simplified UI uses SQLite |
| CSV | Actual escaped download from displayed result |
| Injection protection | Prompt separation plus independent guardrail tests |
| Docker | Multi-stage image, compose, run instructions; report whether daemon test ran |
| Unit/integration tests | Runnable test suites and recorded outcomes |

## Decisions that must be visible

- "Hired after January 2024" uses the boundary defined in specification 09: hire_date on/after 2024-01-01. Mention the inclusive boundary in the explanation. Other ambiguous date phrases ask for clarification.
- Keyless sample mode is an additional convenience, not fulfillment of unrestricted LLM reasoning. Its supported examples work, its limitations are explicit, and a server-side Groq key enables general schema-bound AI requests.
- Multi-dialect support means validated SQL generation/rendering for three dialects. All demo execution uses SQLite; do not imply three database servers exist.
- A query plan heuristic is not monetary billing, an actual optimizer cost, or a PostgreSQL/MySQL EXPLAIN plan.
- Local-only delivery is the user's latest instruction. Keep required public submission items visible as deferred, not falsely complete.
- No authentication is needed for synthetic sample data. Model configuration is server-only under amendment A04; production identity/multi-tenant permissions are outside this product scope.

## Product acceptance

The app must let a reviewer finish the specified examples without editing files, distinguish error/refusal/clarification, show only validated SQL, and identify the actual execution engine. API responses also identify their output dialect. There are no fake query results, fabricated provider responses, fake deployment links or script-only substitutes for a video.
