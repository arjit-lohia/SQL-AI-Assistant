# Detailed test plan and evaluation evidence

Requirements: [specification 01](01-requirements.md), B10 and the release/quality gates. Tests validate behavior and security boundaries rather than mirror implementation details.

## Test environment

Use deterministic bundled SQLite database, pytest backend suite, FastAPI HTTP test client and Playwright browser suite. Test model integration through an injected/mock HTTP boundary for reliable CI; optional live-key suite separately proves provider connectivity. Browser tests run against a built local app/API and use real sample execution. Do not depend on random model wording for deterministic acceptance.

## Generation and data matrix

| ID | Input | Expected proof |
| --- | --- | --- |
| G01 | Specified employee date example | Existing fields; inclusive date predicate; every returned hire date meets it |
| G02 | All customers | 120 source rows, projected columns valid |
| G03 | California customers | Nonempty result; every state California |
| G04 | Monthly revenue 2025 | FK joins, non-cancelled assumption, months sorted; independent SQL aggregate agrees |
| G05 | Top 5 products by revenue | Five or fewer actual products, descending metric, deterministic tie order |
| G06 | Request missing phone column | Clarification; null SQL/results |
| G07 | Best customers | Clarify metric/time period |
| G08 | Future date with no matches | Success with headings and no rows; no fabricated matches |
| G09 | Dialect matrix | Reference query parses/renders in sqlite/postgres/mysql; SQLite translations match stable results |
| G10 | Unsupported dialect-specific feature | Clear error/clarification; no lossy success claim |

## Validator and security matrix

| ID | Case | Expected |
| --- | --- | --- |
| S01 | DELETE/UPDATE/INSERT/DROP/ALTER/TRUNCATE requests | Polite refusal before generation/execution |
| S02 | Stacked SELECT; DROP, comments/casing variants | Reject multiple statements |
| S03 | Writable CTE, SELECT INTO, locks, recursive CTE | Reject nested side effects/unsupported structures |
| S04 | Unknown business table/column, ambiguous name | Reject before return; safe diagnosis |
| S05 | Valid FK joins with aliases/reversed equality | Accept |
| S06 | Unrelated id=id, CROSS/NATURAL/comma join | Reject |
| S07 | FK condition OR TRUE | Reject bypass |
| S08 | sqlite_master/sqlite_schema/PRAGMA/system funcs | Reject public metadata access |
| S09 | readfile/load_extension/sleep/network funcs | Reject unsafe/unknown function |
| S10 | External db/catalog/table-valued sources | Reject |
| S11 | Ignore rules/system role/secret extraction | Refuse; never reveal prompt/key |
| S12 | Sports/politics/general knowledge/code/math/poem | Refuse each class, including SQL keyword bait |
| S13 | Literal contains 'drop'/'update'/HTML | Accept when otherwise valid; safe text rendering |
| S14 | Huge body/message/history/AST/deep nesting | Bounded rejection, no crash/hang |
| S15 | Expensive nonrecursive safe query | Execution interrupted or capped within budget |
| S16 | Forged assistant history with DML | Revalidate/refuse; no prior trust inheritance |
| S17 | SQL client asks execute with safe-looking flag | Full independent validation still runs |
| S18 | Database hash before/after test suite | Unchanged; read-only guarantees proven |

## Optimization/debug/cost matrix

| ID | Case | Expected |
| --- | --- | --- |
| O01 | Poorly formatted valid SQL | Formatted, equivalent results |
| O02 | Unused LEFT JOIN many-to-one parent | Join removed, result multiset identical |
| O03 | Unused LEFT JOIN to many-side | Retained; no duplicate-row loss |
| O04 | RHS projection/filter/order/SELECT * | Join retained |
| O05 | INNER/derived/complex joins | Retain unless rule proves safety |
| O06 | Indexed filter | Existing index recognized; no false missing-index claim |
| O07 | Scan/temp sort query | Actual plan data plus meaningful advice/caveat |
| D01 | Unique misspelling e.g. hiredate | Original issue explained; corrected hire_date validates |
| D02 | Ambiguous misspelling/column intent | Clarification, no guessed correction |
| D03 | Valid query in debug mode | State valid, return formatted accepted version |
| D04 | Repair candidate still invalid/unsafe | At most one repair; no SQL leaks |

## Context and graph matrix

| ID | Case | Expected |
| --- | --- | --- |
| C01 | Customers → California → sort name → top 10 | Prior predicates retained; refinements compose |
| C02 | No prior query + "only those" | Clarification |
| C03 | Two interleaved independent histories | No cross-talk |
| C04 | Refusal after valid query then refinement | Latest valid SQL retained as context |
| C05 | Dialect changed between turns | Canonical/source-aware context translation |
| L01 | Successful graph | Real nodes in intended order; validated before optimize/execute |
| L02 | Scope refusal | Early terminal path; no provider/executor for deterministic refusal |
| L03 | Structured model malformed JSON/extra fields | Safe error; no execution |
| L04 | Model refusal/clarification | Null SQL/cost/result |
| L05 | Invalid model SQL then good repair | Two calls maximum; corrected validation succeeds |
| L06 | Provider 401/429/timeout/5xx | Useful redacted error; no silent sample substitution |
| L07 | Sample mode | Clearly labeled; unsupported request clarifies honestly |

## API/browser checks

API: health/schema counts; request enums/extra keys; execute 400/422; server-only key/model settings and no key exposure; oversized chunked body; SSE progress/text/result boundaries and no raw candidate; stream disconnect cleanup; results types/null/zero/truncation. Check database unavailable behavior separately.

Browser: initial dataset/provider; examples; generate/run; results/explanation/plan; follow-up; optimize/debug; refusal; copy/download; CSV escaping/formula protection; theme persistence; conversation select/delete/new/reload; mobile overflow; accessible labels/keyboard; no console errors; failed network/cancel releases loading. Capture desktop and mobile screenshots.

## Release checks and evidence

Required local gates: dependency resolution; seed integrity/repeatability; Python tests; TypeScript/Vite build; browser suite; 3–5 minute actual recording with measured duration. Docker build/run when a daemon exists; otherwise perform source/config checks and explicitly state unexecuted Docker validation. Validate deployment config structure locally but never label it a deployed app.

Record exact command, count, outcome and relevant environment in `docs/verification.md`. Avoid claiming a passing mock validates a real LLM or a local smoke test validates Vercel. Fix observed failures, rerun affected tests, then rerun final appropriate gates once stable. No claim that green tests prove every possible SQL construct or adversarial prompt safe.
