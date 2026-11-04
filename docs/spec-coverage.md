# Specification coverage ledger

Source: [Product requirements](../specs/01-requirements.md), the [detailed specifications](../specs/README.md) and [approved amendments](../specs/05-amendments.md). Status distinguishes working local behavior from account-dependent publication and live-provider verification. The [six-deliverable audit](deliverables.md) links the complete local handoff.

| ID | Requirement / bonus | Source and evidence | Local status |
| --- | --- | --- | --- |
| R01 | Natural language → SQL | agent.py, provider.py, sample.py; reference queries in test_agent_api.py | Sample paths tested; live Groq path implemented/mocked; real key verification pending |
| R02 | Syntax/table/column/FK/read-only validation | sql.py + database authorizer; test_sql.py adversarial cases | Verified locally |
| R03 | Plain-English explanation | sql.explain, App explanation panel; browser tests | Verified locally |
| R04 | Readability/performance/index advice/join removal | sql.optimize; safe/unsafe rewrite equivalence tests | Verified locally |
| R05 | Diagnose/explain/correct SQL errors | generate_sql original validation; sample typo correction/model path; API/browser tests | Verified local/sample; live model mocked |
| R06 | Context modifies previous query | canonical prior SQL, per-turn dialect; history/follow-up/isolation tests | Verified locally |
| R07 | SQL-only refusal | validate_scope + system prompt; tests for sports/politics/code/math/creative/mixed scope | Verified tested cases; no claim of perfect NLP classification |
| R08 | All required frontend controls | Chat, SQL, explanation, history, loading/errors, copy in App.tsx | Browser verified |
| B01 | Dark/stream/download SQL/results | Theme persistence, SSE progress + accepted text, .sql/CSV | Browser/API verified |
| R09 | LangGraph + relational DB/backend | Actual StateGraph; FastAPI; bundled sample.db | Verified locally |
| R10 | Expected workflow + clarify | Explicit graph conditional edges; bounded repair and strict JSON; tests | Verified locally |
| B02 | SQL execution | Guarded SQLite /api/execute, optional auto-run | Verified locally |
| B03 | Follow-ups | Customers → California → sorting/limit; separate histories | Verified locally |
| B04 | Cost estimate | Real EXPLAIN QUERY PLAN; scan/search/sort heuristic, caveat | Verified locally; SQLite only |
| B05 | SQL highlighting | Escaped React token nodes and line numbers | Browser verified |
| B06 | SQLite/Postgres/MySQL | Backend/API SQLGlot read/render/strict translation; reference matrix | All three API dialects tested; simplified UI uses SQLite per user amendment A06 |
| B07 | CSV export | lib.toCSV; actual result downloads, quoting/formula test | Browser verified |
| B08 | Prompt injection protection | Versioned policy, scope checks, AST/schema/authorizer; forged context tests | Defense in depth implemented/tested |
| B09 | Docker deployment | Dockerfile, .dockerignore, compose.yaml | Files prepared; Docker unavailable here, build/run unverified |
| B10 | Unit + integration tests | tests/test_sql.py, test_agent_api.py, tests/browser | Passing local suite; see verification.md |
| D01 | Source/GitHub | All application/config/test/script files present | Local source complete; remote publication deferred by user |
| D02 | README/setup | README.md with Windows/Linux/local/model/Docker/Vercel steps | Complete local instructions |
| D03 | Architecture | docs/architecture.mmd + SVG | Included |
| D04 | Workflow explanation | docs/workflow.md and real graph source | Included |
| D05 | Exact prompts | prompts/system.txt + repair.txt, referenced at runtime | Included |
| D06 | Sample schema | schema.sql, deterministic seed.py, sample.db, database.md | Included/verified |
| D07 | 3–5 minute demo | artifacts/queryatlas-demo.webm + transcript and recording script | Current **3:26.68** recording, media metadata verified; captions reference specs |
| D08 | Public deployed link | Vercel-ready config + README publication checklist | Deferred by user; no public URL claimed |
| D09 | Submission/assumptions | docs/submission.md, README semantics/limits | Included; real publication links intentionally pending |

Implementation follows spec-first contracts and the user's local-only amendment. GitHub/live-link publication remains deferred until authorized publication and unauthenticated deployment verification.
