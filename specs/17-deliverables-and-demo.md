# Deliverables, demo recording and submission specification

Requirements: [specification 01](01-requirements.md), D01–D09, with [approved amendments](05-amendments.md). This is the final handoff checklist, not permission to publish now.

## Deliverable inventory

| Deliverable | Required artifact and acceptance |
| --- | --- |
| Complete source code | Backend, frontend, scripts, tests, prompts, configuration and dependency locks; no missing proprietary service or generated-only UI |
| GitHub repository | Locally prepared clean Git repository; actual remote URL deferred by user's instruction; no fake placeholder presented as real |
| README / setup | Working local commands, environment names, provider/sample distinction, sample DB, test/run/build, Docker and Vercel steps, access expectations and limitations |
| Architecture diagram | Mermaid source plus standalone rendered SVG; show browser, FastAPI, real LangGraph, provider, validation and read-only DB boundaries |
| Workflow explanation | Node/state/routing/repair description corresponding to implemented graph; context and safety decisions |
| Prompts used | Exact production system/repair files, payload construction and model config; docs link to source |
| Sample database schema | DDL, ER/data dictionary, deterministic seed, bundled DB and metric definitions |
| Demo video | Actual playable 3–5 minute screen recording with readable app behavior, truthful captions/narration and measured duration |
| Public deployed link | User-deferred; later real unauthenticated working Vercel URL verified from outside local server |
| Development assumptions | Explicit synthetic schema, read-only data, local history, sample provider limitations, dialect execution and cost caveats |

`docs/spec-coverage.md` maps all R/B/D IDs to source/tests/evidence and status. `docs/deliverables.md` audits the six local artifacts requested by the user. `docs/submission.md` provides local review URL, actual video file and the two deferred publication items. `docs/verification.md` reports checks performed and unverified boundaries. Do not conflate configuration with a verified deployment or demo script with a video.

## README contents

Lead with what the assistant does and how to run locally. Include architecture and workflow links, key features, exact setup commands, provider setup, supported keyless examples, schema/date/revenue semantics, three dialect scope, API overview, guardrails/resource limits, tests, Docker, Vercel and known limits. State no login required for local synthetic dataset, environment-only model configuration, browser-local conversation privacy and how to clear history from the conversation list. Link specs as design artifacts.

Document the specified synthetic commerce schema and user-directed local-only delivery. Do not describe specified publication deliverables as optional merely because publication is deferred. Cite current official LangGraph/SQLGlot/Groq/Vercel documentation where technical choices depend on them; derived application behavior comes from code/tests, not documentation claims.

## Recording storyboard (target 3:40)

| Time | Scene | Visible evidence |
| --- | --- | --- |
| 00:00–00:25 | Introduction | QueryAtlas, SQL-only purpose, provider mode and synthetic data; open schema |
| 00:25–00:55 | Customers | Ask California question, show progress, validated SQL, explanation, actual rows |
| 00:55–01:20 | Follow-up | Refine previous query; show retained state filter/order/limit |
| 01:20–01:40 | Specified employee example | Inclusive 2024-01-01 query and matching dates |
| 01:40–02:15 | Revenue and cost | Real FK joins/aggregation, SQLite UI/API dialect disclosure and real plan caveat |
| 02:15–02:50 | Debug and optimize | Error diagnosis/correction, formatting, safe join removal and index advice |
| 02:50–03:15 | Guardrails | Out-of-scope refusal, destructive request or instruction override blocked; no SQL/result leak |
| 03:15–03:40 | Frontend/delivery | CSV/SQL exports, dark mode/history/mobile view, local architecture/setup and publication deferred |

Timings may vary, but final artifact duration must be between 180 and 300 seconds. The recording must show actual app interactions and readable pauses, not a static slide deck stretched to duration. Captions or narration explain transitions; disclose sample mode if no key. A model-verified recording is only claimed if a real provider was configured and used.

Recording script is reproducible, saves under artifacts/ and does not mutate app source or bypass safety checks. Browser recording should not capture desktop notifications, environment secret settings, filesystem secrets or account tokens. Include a transcript with narration/caption text. Provide a playable format (WebM or MP4) and measure duration using media tooling. Keep large videos out of Git by default; local artifact remains available to the user and can later be uploaded to an approved destination.

## Final status language

Report implemented/verified items concisely with file links and local run URL. Report keyless/live-provider status exactly. Report Docker validation limit if no daemon. Clearly state GitHub/Vercel publication deferred per user's request. Never claim publication links are complete while absent. The local app can be complete even though the user's requested publication phase remains deferred.

## Expanded specification completion gate

Files 01–17 plus the index collectively specify the product contract, all requested additional features and the user's sample-database/local-delivery instructions. This detailed set was completed before application implementation resumed. Future behavior changes require an amendment before code changes. Verification of implementation remains a separate phase.
