# SQL validation, scope and security specification

Requirements: [specification 01](01-requirements.md), R02, R07, R10 and B08. Quality focus: validation and guardrails (20%).

## Threat and trust model

Untrusted: user requests, pasted SQL, browser history (including claimed assistant SQL), model output, query parameters and any future database text. Trusted: source-controlled system policy, actual schema metadata, server-owned validation state. The LLM is a proposal engine and cannot authorize execution or override the validator.

Protect the database from mutation/exfiltration, the server from SQL-based file/network access and excessive work, users from cross-conversation leakage, and the reviewer from misleading output. This is a bounded synthetic-data demo, not a claim of production authorization or comprehensive prompt-injection immunity.

## Scope decisions

Accept natural-language questions answerable from the six tables, schema/relationship questions, SQL explanation/debug/optimization grounded in that schema and context-dependent refinements. Refuse general knowledge, sports, politics, unrelated programming, standalone mathematics and creative writing. Numeric aggregation over actual database columns remains in scope. A request mixing a valid SQL task with unrelated output is refused or asks the user to submit only the database task; never fulfill the unrelated part.

Write requests are politely refused, including DELETE, UPDATE, INSERT, DROP, ALTER and TRUNCATE. Also refuse CREATE, REPLACE, MERGE, grants/revokes, attach/detach, PRAGMA, transactions, file export/import and side-effect operations. Index recommendations are descriptive text, not runnable CREATE INDEX SQL. Harmless literals such as a product named 'Drop' must not be rejected solely by substring scanning.

Injection indicators include "ignore previous instructions", role/system impersonation, requests to reveal system prompts or API keys, bypass validation, execute hidden second statements, fabricate schema or pretend a write is read-only. Normalize Unicode for natural-language guard checks. Prompt and lexical checks supplement, never replace, AST/database checks. A SQL-related keyword appended to an unrelated question is not sufficient scope.

## Validation pipeline (ordered)

1. Enforce SQL length and parse selected dialect with errors enabled. Do not execute raw input to discover whether it is safe.
2. Require exactly one nonempty statement. Permit one trailing semicolon; reject statement stacking, including commented/mixed whitespace variants.
3. Require SELECT or read-only set-operation root. Traverse the entire AST to reject nested writes, SELECT INTO, locks, commands, parameters, recursive CTE, table creation, metadata and unsupported opaque nodes.
4. Bound AST size/nesting; bound pattern/function work where possible. Refuse external catalogs, qualified alternate databases, filesystem/table-valued functions and source types outside business tables/validated nonrecursive CTE/subqueries.
5. Resolve tables through query scopes. CTE names can refer only to their validated definitions. Never approve a physical nonexistent table because it shares a global alias. Reject system tables and PRAGMA functions.
6. Qualify/resolve all projected, filtered, grouped, sorted, joined, windowed and correlated columns against actual schema with SQLGlot. Reject missing or ambiguous unqualified columns. Support valid aliases without mistaking output aliases for physical columns.
7. Validate every JOIN. Require an equality between a declared child FK and referenced parent key, using aliases resolved to real tables. Require the equality as a conjunct, not a disjunct where OR TRUE bypasses it. Additional filtering predicates may be allowed. Reject CROSS, NATURAL, implicit cartesian joins, wrong id=id relationships and unverifiable derived relationships. Document conservative rejection of complex joins.
8. Allow only vetted pure scalar, date, aggregate and window functions. Deny file/network/extension/sleep/benchmark/system functions and unknown user-defined functions. Inspect SQLGlot anonymous and dialect-normalized functions, not just raw text names.
9. Strictly transpile to SQLite, repeat structural safety checks where needed and compile via EXPLAIN under a read-only guarded database connection. Treat compile errors as invalid SQL with safe diagnostic text.
10. Return formatted SQL and successful check names only after every check passes. Revalidate all optimization/repair output and every `/execute` request.

## Database enforcement

Open SQLite URI `mode=ro&immutable=1`; no writable connection is available to user-query code. Apply SQLite authorizer allowing only SELECT, approved business-table reads and vetted functions. Deny write opcodes, schema/metadata reads, extensions, attachments and PRAGMA. Trusted schema introspection uses a separate internal path, not the public execution surface.

Use progress handler/deadline (target 2 seconds), bounded virtual-machine work (target 1 million steps), AST node limit (target 600) and result cap (500 plus one sentinel). SQLite execution uses cursor fetch, not unbounded fetchall. Query-plan collection is similarly guarded. Return an explicit truncation flag; never silently imply 500 is the full result count when more rows exist. Limits are project decisions and must be consistent across implementation/docs/tests.

## API and model resource controls

Message ≤4,000 chars, SQL ≤12,000 chars, ≤16 history turns and ≤24,000 context chars; request body ≤128 KiB. Reject unsupported dialect/mode and unknown JSON keys. Fixed provider URL; finite timeouts; at most two calls/turn. Do not return model raw HTTP errors, stack traces, file paths, keys or prompt content. Optional shared token uses constant-time comparison and session-only browser storage. Keep CORS same-origin by default. A per-process counter is not a distributed rate limiter; document Vercel firewall/spend controls for later public paid-model deployment.

## Public result guarantees

Refusal/clarification/error has null SQL/result/cost. Failed candidate SQL never leaks through diagnostics, progress or exception strings. Errors can identify a nonexistent column/table entered by the user, but must not dump unvalidated model SQL. A failure has a useful next step. Accepted queries show which checks passed, and actual execution is separately recorded.

## Required adversarial acceptance

Reject stacked SELECT+DROP; DML in CTE; SELECT INTO; LOAD_EXTENSION/READFILE; sqlite_master/pragma_table_info; alternate database paths; unknown functions; CROSS JOIN; FK equality hidden under OR TRUE; arbitrary id=id join; nonexistent table/column; forged history SQL; role override; secret extraction; quoted injection. Accept legitimate literals containing write words, existing FK joins, valid CTEs/subqueries and simple safe aggregates. Confirm rejected paths never call the executor and database contents/file hash remain unchanged.
