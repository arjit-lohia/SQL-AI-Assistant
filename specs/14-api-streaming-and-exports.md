# API lifecycle, streaming, errors and export specification

Requirements: [specification 01](01-requirements.md), R08–R09, B01–B02 and B07. Wire models are in 03-api; this document specifies behavior.

## HTTP surface

| Endpoint | Purpose | Success | Failure |
| --- | --- | --- | --- |
| GET /api/health | Probe actual bundled database; identify provider/model/version | 200 connected | 503 disconnected, safe detail |
| GET /api/schema | Actual trusted business schema and examples | 200 metadata | 503 safe unavailable |
| POST /api/chat | Full terminal graph response | 200 status success/refused/clarification/error | 422 invalid request; 413 body too large |
| POST /api/chat/stream | Same graph via SSE | 200 text/event-stream and terminal event | Pre-stream request errors as JSON; post-start safe error event |
| POST /api/execute | Revalidate, plan and execute selected SQL | 200 result/cost/checks | 400 invalid/unsafe SQL; 422 execution budget |

Refusal/clarification are domain outcomes, not transport failures. Never hide request validation failures under success. Server logs can include safe exception categories and request ids; no prompts/keys/full raw model payload by default. Use no-store for API responses. Add nosniff and appropriate content security policy to the frontend. API same-origin avoids permissive credentialed CORS.

## SSE lifecycle

Input is the same as nonstream chat. Validate body limits and Pydantic model before opening the stream. The synthetic sample app has no browser-token authentication flow (amendment A04). SSE frames are UTF-8 `event: name\ndata: JSON\n\n`. Allowed events: progress, text, result, error. Public graph projection only, no raw state dumps. At most one terminal result/error. Clean generator shutdown when the client disconnects.

Progress contains stable step name and human label from actual graph completion. Text deltas contain only the accepted explanation after validation. Result contains the complete typed response, authoritative even when text deltas were partially lost. Client must handle HTTP chunk boundaries splitting UTF-8 characters/lines/events using a streaming decoder and buffer. A truncated stream without a terminal event becomes an actionable network error, never an eternal spinner.

Nonstream endpoint is useful for tests/integrations and returns identical final semantic content. A streaming response that has started cannot change its HTTP code; report terminal failures as error events. Do not retry a generation automatically after partial output in a way that creates duplicate turns.

## Execution lifecycle

Execute never accepts a client-side `validated=true` claim. It parses and validates SQL afresh using the supplied known dialect, builds the SQLite equivalent and executes under guarded connection limits. Result JSON preserves null/string/numeric types and does not contain Python-specific date/decimal/bytes objects, NaN or infinity. SQLite text dates remain strings. Empty result includes column headings and rows=[]; no rows is successful.

Fetch 501 rows for a maximum of 500 returned rows; the extra row only determines `truncated`. `row_count` means returned count, not unbounded total matching rows. `max_rows` and engine are explicit. Duration is monotonic measured database execution time, separate from graph elapsed time. A failed new execution should not relabel an old result as fresh; preserve old result only with a visible state tied to its prior execution.

## CSV contract

Export only the currently selected execution result, including column headers in displayed order. Use UTF-8 BOM, comma delimiter, CRLF, quoted fields and doubled embedded quotes. Null is an empty CSV field. Numeric values remain numeric including negatives. Strings beginning with `=`, `+`, `-`, `@`, tab, CR/LF or control whitespace followed by a formula trigger are prefixed with an apostrophe to reduce spreadsheet formula execution. Quoting alone is not formula protection. Never export HTML as a spreadsheet.

Include a filename tied to query/date (safe fixed filename is acceptable); report truncation before/alongside export so users know it contains displayed capped rows. CSV fulfills the specified results-download feature; additional formats are outside the current scope. Disabled export indicates why no result exists.

## SQL and clipboard contract

Download actual accepted formatted SQL as `.sql`, with comments indicating output dialect and SQLite sample execution where applicable. Do not include secrets, internal prompts, rejected candidates or index DDL. Copy contains executable accepted SQL without line numbers or UI labels. Clipboard success feedback is temporary and accessible; rejection shows guidance. Object URLs for downloads are revoked after use.

## Error copy

Errors identify what the user can do: configure server key, retry provider, choose an existing column/table, clarify a metric, shorten a request, or simplify a query exceeding limits. Refusal explains SQL-only/read-only scope politely. No raw tracebacks/provider response bodies. Do not disclose secret configuration values to explain configuration failures.

## Acceptance

Use API tests for status/error/body-size/model-environment cases and full SSE parsing. Browser tests assert terminal loading cleanup, actual .sql content, formula-safe CSV, selected-turn association, zero rows, row caps, copy feedback and cancel/retry. Rejected SQL must never reach database execution.
