# Acceptance, verification and delivery specification

Status: COMPLETE. Specifications 01–04 are now finished; application implementation may begin.

## Automated verification

Backend unit cases: AST write denial including writable CTE and SELECT INTO; one-statement rule; unknown/ambiguous columns; unknown and metadata tables; external catalogs/functions; correct FK joins and incorrect join keys; CTEs/subqueries/aggregates/window functions; safe indexed LEFT JOIN removal and unsafe join retention; limits/time budget; SQL literal false positives; SQLite/PostgreSQL/MySQL render/parse/execute; strict structured output; injection; schema seed integrity; dialect semantic caveats.

Graph/API cases: employee date example; customer California follow-up; revenue joins/grouping; debug misspelled column with actual diagnosis; optimize request and index advice; out-of-scope refusal; destructive and mixed-scope requests; ambiguity clarification; zero rows; execution cap; direct execution validation; bad enum/oversized body; streamed terminal result and progress; independent conversation contexts; malicious history; mocked provider JSON/timeout/invalid SQL/repair. Live-provider test is opt-in with a real key and must be distinguished from mocked integration tests.

Browser cases: load app and schema; example submits real request; SQL/explanation/results; follow-up and history navigation; new conversation; dialect switch; copy and .sql/CSV download; dark preference; mobile viewport; retry after error; no console errors. Capture desktop/mobile screenshots. Build TypeScript and Vite production bundle. Verify Python import/dependency resolution and compile. Use stable locked/pinned dependencies after successful installation.

## Demo video (target 3:20–4:00)

Record the actual local or deployed app with readable viewport and timed captions (narration if available). Show: introduction/dataset/schema (25s); California customers and actual results (30s); follow-up (25s); employee date request (20s); monthly revenue joins/dialect/cost (35s); debug/optimization/index recommendations (35s); refusal/injection (25s); dark/mobile/export/history (25s); architecture/deployment and honest provider mode disclosure (20s). Do not imply sample mode is a live LLM. Bundle actual recording, transcript and re-record command; do not commit huge binary recordings to Git without a justified distribution strategy.

## Documentation/artifacts

README: quickstart for frontend + API, single-server built app, actual env names, model/key setup, dataset reproduction, security controls and limits, Docker, Vercel deployment/public-access verification, test commands, citations to primary implementation docs. Architecture diagram in Mermaid and a standalone SVG. Workflow and exact prompt files linked. Schema DDL, seed script, data dictionary and SQLite artifact included. Assumptions: synthetic commerce schema replaces absent supplied schema; read-only data; public synthetic-only access; client-local history; fixed dates; SQLite sample execution for all supported render dialects; estimates are relative planner observations.

## Completion ledger

Track every R/B/D item in `docs/spec-coverage.md` with code/docs/tests and verified status. `docs/submission.md` holds GitHub URL, public Vercel URL and demo file/link only when real. External publication needs authorized account access; finish all reviewable work before requesting any remaining approval. Never mark requirements complete solely because deployment/config files or a video script exist.
