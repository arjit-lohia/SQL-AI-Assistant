# Selectable dialects, reliable refinements and setup delivery

This contract supplements specifications 09 and 12 under amendment A10. It is written before application changes.

## Output dialect

- Put an accessible SQL dialect selector in the existing query workspace header, with SQLite (default), PostgreSQL and MySQL. Disable it during generation/execution. Do not restore the removed introductory banner.
- The selector affects the next request. Existing responses, execution, copy/download and context retain their own original dialect; changing the selector alone never relabels an old SQL result.
- All three outputs use the existing independent parser/validator and strict translation. Actual execution and plans remain on bundled read-only SQLite. Native PostgreSQL/MySQL servers are outside this change; the UI and README must state the distinction.
- Switching dialect mid-conversation refines the latest validated query using its source dialect, preserving its filters and order.

## Follow-up behavior

- Requests in one conversation refine the most recent accepted SQL, including after refusal/clarification turns. New conversation has no previous query.
- In keyless sample mode, support `Give all people from Austin` as customers in that city, and `Show people who joined before 24th Oct, 2024` as an added `customers.created_at < '2024-10-24'`. State explicitly that people means customers and joined means account creation. Support the same cutoff with ISO dates and ordinary full/abbreviated month names; invalid dates clarify. Employee hire dates use hire_date only when employees are unambiguously selected. Do not invent employee city data.
- Add predicates through the SQL AST, retaining prior WHERE, projection, ordering and limit. Keep existing California/sort/limit/completed-order follow-ups. Without context, a pronoun/people-only date refinement clarifies rather than guessing.
- Live model receives canonical previous SQL, recent history and explicit preservation instructions even when the message starts with `Show` rather than `Only`.
- Independently detect lost top-level WHERE conjuncts for additive refinements of simple single-table SELECTs. Normalize aliases before comparison. A dropped predicate goes through the existing one-repair route; a repeated failure exposes no SQL/results. Do not silently merge arbitrary model SQL or claim general semantic equivalence. Complex joins/subqueries remain governed by prompts and existing schema validation.
- Allow deliberate new SQL, topic changes to a different table, and explicit reset/replacement/removal language to change filters. Exact predicate preservation is conservative: equivalent rewrites can be rejected with a repair diagnostic rather than accepted without proof. No native-engine or live-provider quality claim follows from mock tests.

## Documentation delivery

- README should be short: purpose/features, Windows quick start, optional server-only model configuration, an example refinement, test command pointers, deployment link and six deliverable links.
- Provide docs/setup.md with Python/Node prerequisites, complete Windows and macOS/Linux steps, existing .env preservation, sample/live modes, development commands, deterministic database rebuild, tests, Docker, Vercel guide and common failures. No external brief references.
- Keep existing useful setup information accessible rather than deleting it. Add setup to the automated deliverable audit and update documentation claims about dialect UI.

## Acceptance

1. Backend tests execute Austin plus cutoff in all three dialects and check every returned city/date, preserve sort and prior state, verify resets, absent context and invalid dates.
2. Mock provider tests cover previous SQL payloads, alias-normalized preservation, lost-filter repair and repeated-loss rejection; no real API calls or .env inspection.
3. Browser test switches SQLite to PostgreSQL to MySQL in one conversation, checks generated date syntax, cumulative filters, exports' dialect metadata, history reload and fresh-conversation isolation. Existing viewport/theme/accessibility tests continue to pass.
4. Run Python suite, TypeScript/Vite build, browser suite and deliverable/link audit. Record actual outcomes and limits.
