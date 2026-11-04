# Safety boundaries and known limits

All requests/history/model candidates are untrusted. Trusted schema comes from the six bundled business tables. System policy constrains scope; independent parsing and database controls enforce read-only execution even if a model ignores policy.

Validation parses one SELECT/nonrecursive CTE in the selected dialect, walks all nested nodes, rejects write/DDL/admin/INTO/locking/recursive constructs and external sources, binds scoped columns/tables, verifies declared FK join equality (no OR/cartesian bypass), allowlists functions, strictly translates to SQLite and compiles using guarded EXPLAIN. Optimizations and execution endpoints revalidate. Error text avoids raw candidate parser dumps. Refusal/error/clarification carries no SQL or result.

SQLite opens immutable/read-only and authorizes only SELECT, known-table reads and allowlisted functions. A table-level SQLITE_READ may have an empty column and database=None; the authorizer permits this only for a known business table, while AST checks prohibit alternate database sources and attachments. All write/admin opcodes remain denied.

Bounds: incoming JSON 128 KiB even without Content-Length; message 4,000 chars; SQL 12,000; 16 history turns/24,000 chars; AST 600 nodes/40 nesting levels; SQLite progress handler every 1,000 VM instructions, abort at 1,000 callbacks or 2 seconds; fetch 501 rows and return 500 with truncation. Bounded Groq JSON output and a maximum one repair prevent unbounded agent loops.

Prompt injection defenses include Unicode-normalized request checks, fixed trusted prompts, structured user/history payload, model JSON validation and refusal of instruction overrides/secrets. These are defense in depth, not a claim that every malicious natural-language instruction can be recognized. The LLM has no execution tools, API keys in prompt context or authority to change schema/validator policy.

Conversations are browser-local and scoped per request, not stored globally in a server process. Context SQL is revalidated with dialect metadata. Model secrets/configuration stay server-side in ignored `.env` or server environment variables. There is no browser credential input, settings dialog or access-token storage. API CORS is same-origin. UI renders text safely; no raw model HTML. CSV neutralizes formula strings; downloads are actual bounded results.

Limits are deliberately conservative: complex derived joins, unknown functions, unsupported vendor semantics and ambiguous metrics may be rejected/clarified. Native PostgreSQL/MySQL execution is absent. The database is synthetic with no tenant isolation requirements; production RBAC, identity, mutable remote storage and distributed rate limiting are separate future work. When publicly deploying a paid key, configure provider budgets and hosting abuse controls; a local-memory counter would not suffice.
