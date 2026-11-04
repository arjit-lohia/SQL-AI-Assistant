# SQL optimization, debugging and cost specification

Requirements: [specification 01](01-requirements.md), R04, R05 and B04. These are required product behaviors, not merely documentation suggestions.

## Optimization inputs and outcomes

Explicit optimize mode accepts a pasted SELECT or a natural-language optimization request with SQL in context. Validate the original query before semantics-preserving rewrites. Unsafe SQL is refused; malformed SQL is diagnosed as a debugging need. Return readable formatted SQL, actual rewrite diagnostics, advisory improvements and index considerations. Return no unvalidated SQL.

Readability includes normalized keyword casing, indentation, clause line breaks and stable alias handling. Formatting cannot change selected columns, row multiplicity, predicates, ordering, aggregation or null behavior. Do not report formatting alone as a measured performance gain.

## Safe unnecessary-join removal

Implement a deliberately narrow provable rewrite:

- Join is a simple LEFT JOIN from the preserved side to a known parent table.
- Its ON clause is one FK = unique/primary parent-key equality, with alias resolution established.
- No RHS column is referenced in SELECT, WHERE, GROUP BY, HAVING, ORDER BY, window clauses, another join or a correlated expression.
- No SELECT * whose expansion includes RHS values; no using/natural/cross/recursive/derived ambiguity.
- Parent uniqueness means at most one RHS row; removing the unused LEFT JOIN preserves left row count even if no parent exists.
- Revalidate the rewritten SQL and compile it. If proof/check fails, retain the join and provide advice.

Example: `SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id` cannot be removed: orders is many-side and can multiply customer rows. `SELECT o.id FROM orders o LEFT JOIN customers c ON o.customer_id = c.id` can be removed when c is unused because customers.id is unique. An unused INNER JOIN is retained unless a separate proof of nullability and referential completeness exists; the initial implementation does not attempt that rewrite.

Tests compare full ordered/multiset results before and after safe rewrites on synthetic data and include counterexamples that must retain joins.

## Performance and index advice

Inspect filters, joins, ordering, aggregation and SQLite EXPLAIN plan. Explain SELECT * projection cost; leading-wildcard LIKE and functions on indexed predicates; temporary sorts; full scans where visible. Recommend equality/range/join indexes by table/column and possible composite ordering in prose. Check existing PK/unique/secondary indexes before claiming an index is missing. Do not emit DDL or attempt to create indexes. Warn that extra indexes have write/storage costs only when relevant to the actual recommendation, not as a generic warning flow.

No SQL rewrite based solely on model confidence is trusted. If a model proposes a changed query, validate it and restrict automatic transformations to the proven rule; potentially semantic changes are suggestions for the user to review rather than silently applied.

## Debugging flow

1. Identify original supplied SQL and source dialect; never run malformed original SQL.
2. Attempt structural/schema/SQLite compilation validation and capture a safe issue category: syntax, unknown table, unknown column, ambiguous column, invalid join or unsupported function/dialect feature.
3. Explain the problem in plain English, such as `employes` is not an available table or `hiredate` differs from actual `hire_date`.
4. Ask the live model for a minimal correction constrained to actual schema and original intent. In sample mode only fix uniquely identifiable close spellings/syntax cases; do not invent a business meaning.
5. Validate correction with the full pipeline, allowing one bounded live repair if needed.
6. Return corrected SQL, original diagnosis and why the correction fixes it. Preserve valid predicates/ordering. Auto-execute only the corrected validated SQL if requested.

If multiple columns are plausible (name exists in several tables) ask which table/relationship the user intends. If the query is already valid, state that and return a validated formatted version with optional suggestions. Debug mode does not authorize destructive input.

## Cost estimation

Run actual SQLite `EXPLAIN QUERY PLAN` against the accepted SQLite equivalent. Return plan id/parent/detail rows and counts of SCAN, SEARCH and temporary sort usage. Display a coarse relative work label using a documented heuristic: high for multiple full scans or scan+temp sort; medium for a scan/temp sort; low for indexed searches/no scan. Base interpretation on actual planner strings, not model imagination.

Include this caveat: a relative SQLite planner heuristic on small synthetic data; not currency, native PostgreSQL/MySQL planner cost or a production latency prediction. Empty plans and unknown plan patterns must not fabricate numbers. Runtime elapsed time is measured separately and only available for actually executed queries. A low estimate does not exempt execution from limits.

## Acceptance

Verify formatting retains semantics; safe LEFT JOIN is removed; many-side/used/INNER joins are retained; real indexes recognized; appropriate advice appears for a scan/sort; original diagnostics are preserved; unambiguous typo corrected; ambiguous fix clarifies; invalid correction never returns SQL. For cost, assert plan rows come from the database and the caveat exists across all output dialects.
