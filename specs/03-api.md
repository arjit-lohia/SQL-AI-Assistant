# API and data contracts

Status: COMPLETE before application implementation.

All endpoints use JSON except SSE. Never return server paths, provider raw errors or API keys.

## GET /api/health

Return `{status:"ok", database:"connected", provider:"groq"|"sample", model:string|null, version:string}` after a read-only database probe. Database failure yields 503. Provider label reflects configuration, not fabricated live verification.

## GET /api/schema

Return dataset name, description, SQLite execution engine, table name/description/row_count, column name/type/nullable/primary_key, foreign keys, and example questions. Schema is introspected from bundled DB, with a checked trusted description map. No user-supplied schema instructions.

## POST /api/chat and /api/chat/stream

Input: `{message:string, dialect:"sqlite"|"postgres"|"mysql"="sqlite", mode:"generate"|"optimize"|"debug"="generate", execute:boolean=false, history:[{role:"user"|"assistant", content:string, sql:string|null}] = []}`. Context SQL is untrusted and independently checked. The live model must resolve ambiguity with a question rather than invent metrics/columns.

Result: `{status:"success"|"refused"|"clarification"|"error", message:string, sql:string|null, dialect, explanation:string, assumptions:string[], diagnostics:string[], suggestions:string[], validation:{valid:boolean,checks:string[]}, cost:Cost|null, result:QueryResult|null, provider:"groq"|"sample", steps:string[], elapsed_ms:number}`. Non-success always has null SQL/cost/result. Responses carry `X-Content-Type-Options: nosniff`, no-store.

SSE: UTF-8 `event: progress` with `{step,label}`; `event: text` with `{delta}` after validation; `event: result` with full result; `event: error` with safe message. Events separated by two newlines; `Cache-Control: no-cache`, `X-Accel-Buffering: no`. HTTP input validation errors occur before streaming. Browser parses chunk boundaries, cancels fetch on abort, preserves retry input and handles terminal errors.

## POST /api/execute

Input `{sql:string, dialect}`. Independent validation then bounded execution. Output `{sql:string,dialect,validation,cost,result}`. Unsafe/malformed input returns 400 with meaningful safe detail. Execution timeout returns 422. No generic arbitrary SQL endpoint.

`QueryResult = {columns:string[], rows:(string|number|boolean|null)[][], row_count:number, truncated:boolean, elapsed_ms:number, engine:"sqlite", max_rows:500}`. Integers/floats/text/null preserved, JSON never emits NaN/Infinity. `Cost = {level:"low"|"medium"|"high", summary:string, plan:[{id:number,parent:number,detail:string}], scans:number, searches:number, temporary_sorts:number, caveat:string}`. Cost is a relative SQLite planner heuristic on synthetic data.

## LLM output

Strict JSON model: `{status:"success"|"refused"|"clarification", sql:string|null, explanation:string, message:string, assumptions:string[], suggestions:string[]}`. Unknown keys refused. Success requires SQL, non-success cannot carry SQL. No markdown extraction that executes fenced text automatically. Strict model output validation precedes AST validation. One correction retry for invalid SQL; malformed JSON/provider failure returns actionable error, never silently pretends the model succeeded.

## Exports

Client-side `.sql` contains selected validated SQL plus dialect/SQLite sample-execution note. CSV uses displayed result with RFC-style double-quote escaping, UTF-8 BOM, CRLF and leading apostrophe for strings starting with formula characters including leading control whitespace. Numeric negative values remain numeric. Download disabled for unavailable data; copy confirms success or a usable clipboard error.
