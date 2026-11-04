# Product requirements and acceptance contract

Status: COMPLETE before application implementation. This specification is the authoritative product requirements and acceptance contract, elaborated by the [specification set](README.md). User additions include creating the sample database and preparing the app for Vercel. Implementation must follow these specifications and [approved amendments](05-amendments.md); changes require an explicit spec amendment first.

## Product

Build QueryAtlas, a SQL-only business data assistant. A reviewer can inspect a supplied schema, ask business questions, see validated SQL and a plain-English explanation, optimize/debug pasted SQL, refine an earlier query, execute against real sample data, and export SQL/results. No login is required for the public sample dataset. Data is synthetic.

## Traceability

| ID | Requirement | Acceptance and implementation contract |
| --- | --- | --- |
| R01 | 3.1 natural language to SQL | Live Groq model receives only the trusted schema, bounded conversation and user request. Return valid SQL for employees hired on/after 2024-01-01 and arbitrary in-schema business requests. Keyless mode explicitly identifies its limited deterministic sample capability. |
| R02 | 3.2 validation | Parse a single SELECT/CTE AST, bind every table/column, validate declared join relationships, compile against SQLite before returning SQL. Reject writes anywhere in the AST, multiple statements, external catalogs, unsafe functions, recursion and system tables. |
| R03 | 3.3 explanation | Every accepted query has an accurate plain-English explanation. Validation failures never return unvalidated candidate SQL. |
| R04 | 3.4 optimization | Format SQL, report actionable performance advice and index recommendations as text, and remove demonstrably redundant unused many-to-one LEFT JOINs only when the referenced key is unique and semantics are preserved. Revalidate any rewrite. |
| R05 | 3.5 debugging | Diagnose the supplied query first; explain the original error and return a separately validated correction. Ambiguous fixes ask for clarification. Never execute malformed original SQL. |
| R06 | 3.6 context | Follow-ups use the latest validated SQL; "Show all customers" then "Only those from California" adds a state filter. Persist independent conversation histories locally; history is untrusted and revalidated server-side. |
| R07 | 3.7 scope | Politely refuse general knowledge, sports, politics, unrelated programming, arithmetic and creative writing. A SQL keyword alone must not authorize an unrelated task. |
| R08 | frontend required | Responsive chat, SQL panel, explanation, conversation history, loading/progress, usable errors and copy SQL. |
| B01 | frontend bonuses | Dark/light preference; true server-sent progress followed by incremental validated explanation; download .sql and query results. Never stream raw model SQL before validation. |
| R09 | backend/framework | Python FastAPI and actual compiled LangGraph StateGraph. Real SQLite relational database; no JSON-array query simulation. |
| R10 | workflow/guardrails | Intent → scope → schema → generation/debug → validation with one bounded repair → optimization with revalidation → optional execution → explanation → response. Clarification/refusal terminate before execution. |
| B02 | SQL execution | Explicit Run query action; optional auto-run toggle; read-only SQLite connection, authorizer, timeout, 500-row cap and truncation signal. |
| B03 | follow-up support | Context contract R06 and tests across repeated turns and independent histories. |
| B04 | cost estimate | EXPLAIN QUERY PLAN on sample SQLite, scans/searches/temp sorts and coarse low/medium/high work estimate with caveat; never invent money or engine-native PostgreSQL/MySQL estimates. |
| B05 | syntax highlighting | Safe React-rendered SQL tokens; no unsanitized HTML. |
| B06 | multiple dialects | Generate, parse, validate and render SQLite/PostgreSQL/MySQL with SQLGlot. Translate accepted queries into SQLite for sample execution; clearly disclose the execution engine. Reject unsupported translations. |
| B07 | CSV export | Real result CSV, proper escaping and spreadsheet-formula protection. |
| B08 | injection protection | Trusted fixed prompts; structured bounded model output; treat user/history/schema values as data; refuse instruction overrides, secret extraction, write SQL. Independent AST + database controls remain authoritative even if model is compromised. |
| B09 | Docker | Multi-stage Docker image serves built frontend and API; compose example; non-root runtime, bundled database, no runtime writes required. |
| B10 | tests | Meaningful unit/security, API/graph integration, and browser tests for core flows, downloads, accessibility basics and responsive UI. |
| D01 | source / GitHub repo | Complete clean source, ignored secrets/builds, dependency manifests, real Git repo; publish only to an authorized GitHub destination. Record real repo link when available. |
| D02 | README/setup | Local, Docker and Vercel steps, secrets, keyless limitations, synthetic data, model setup, assumptions, validation commands and verified results. |
| D03 | architecture diagram | Mermaid source plus rendered standalone diagram. |
| D04 | workflow explanation | Node responsibilities, branches, bounded repair and state/context trust model documented. |
| D05 | prompts | Exact production prompts in versioned files; linked from docs. |
| D06 | sample schema | Versioned DDL, deterministic seed script and deployable SQLite file; ER relationships and data dictionary. |
| D07 | demo video | Actual 3–5 minute screen recording of the running app; include reproducible recording script and transcript. A script alone is not the deliverable. |
| D08 | public deployed link | Actual publicly accessible working Vercel URL, verified unauthenticated. Requires account access; do not substitute a local URL or invent deployment. |
| D09 | submission/assumptions | Submission checklist with real links, access instructions and explicit outstanding external dependencies. |

## Release gates

All specs 01–04 must be written before application code. Passing backend/security tests, frontend production build and browser smoke tests are implementation gates. Live model, GitHub publication, public Vercel verification and recording are reported separately with actual evidence. Missing credentials must never be presented as completed deployment or AI verification.
