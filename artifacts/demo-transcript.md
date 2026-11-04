# QueryAtlas demo transcript

Mode: keyless sample, actual local API/database; captions only.

0.3s — QueryAtlas · a focused SQL assistant
This recording uses the clearly labeled keyless sample mode. A server-side Groq key enables full schema-bound AI. All results shown are real SQLite data.

10.4s — A real sample database, ready for serverless hosting
Six related business tables contain 1,426 synthetic records. The bundled database is immutable and is opened read-only at runtime.

22.4s — Natural language → validated SQL → actual results
Ask for customers in California. Every query must pass syntax, table, column, function and foreign-key checks before it can be returned.

38.0s — SQL explained in plain English
The explanation describes the accepted query. Independent validation checks and existing-index advice are visible here.

48.0s — Follow-ups preserve the previous query
“Sort by name” refines the California query rather than starting over. The state filter stays in place.

73.0s — Employee hire-date example
The SQL generation specification defines an inclusive January 1, 2024 boundary. Execution returns only matching hire dates.

90.5s — Revenue through declared relationships
The simplified UI uses SQLite. Monthly 2025 revenue uses declared order/item relationships and historical line prices, excluding cancelled orders. Additional output dialects remain supported by the API.

106.1s — Real EXPLAIN, a relative work estimate
This is the actual SQLite sample plan, not a monetary cost or production latency prediction. Execution is independently capped and timed.

118.2s — Debugging diagnoses the original mistake
The supplied hiredate column does not exist. Debug mode explains the issue and returns a corrected, independently validated hire_date query.

132.8s — Optimization applies only proven safe rewrites
This unused LEFT JOIN points to a unique customer primary key, so removing it preserves order rows. Unused joins to a many-side table are retained.

147.3s — Scope and write guardrails
General knowledge is refused. Destructive SQL is refused before execution. A model proposal cannot bypass the independent AST validator or SQLite authorizer.

170.8s — A complete local workbench
Dark mode, persistent conversation history, SQL highlighting, copy, SQL downloads and formula-safe CSV exports are included. PostgreSQL/MySQL output executes on SQLite sample data.

183.0s — Spec-first delivery · local app complete
The repository includes detailed specs, exact prompts, architecture, tests and Docker/Vercel setup. GitHub and public Vercel publication are deferred at the user’s request.

Interaction duration: 196.0 seconds.
