# Local verification report

Environment: Windows, Python 3.12.4, Node 20.17.0. Date: 2026-11-05 (user's Asia/Calcutta context). This file records observed checks, not claims based solely on configuration.

| Check | Outcome |
| --- | --- |
| Requirements review | Product requirements and detailed specification set reviewed; approved amendments incorporated |
| Spec-first | Initial four contracts completed before application code; detailed review paused implementation and expanded to 17 numbered files plus index |
| Database seed | Built 6 tables / 1,426 records; integrity and FK checks passed |
| Backend / security / graph / API | `python -m pytest -q`: **95 passing tests** after environment-only model/settings update |
| Production frontend | `npm run build`: TypeScript + Vite build passed |
| Browser acceptance | `npm run test:e2e`: **15 tests passed**; actual isolated local API/database used |
| Screenshots | Desktop/mobile captures generated and visually reviewed |
| Demo recording | Refreshed `npm run demo`: actual captioned WebM, **00:03:26.68** measured by FFmpeg; 1440×1000, VP9, 25 fps |
| Dependencies | Verified runtime/test closure pinned; npm installation audit reported zero known vulnerabilities |
| Docker | Docker CLI/daemon unavailable; Dockerfile/compose provided, container build/run not verified |
| Live Groq | This audit uses keyless sample instances and mocked provider integration; actual provider inference is not claimed verified and private `.env` values are not inspected |
| GitHub/Vercel | Publication deferred by user; no public deployment/URL verification claimed |

Backend test coverage includes unsafe SQL/metadata/function/external-source denial, FK joins, CTE/subqueries/windows, schema validation, safe join-removal equivalence/counterexamples, zero/capped rows, immutable authorizer, actual plans/index advice, three-dialect examples, scope, follow-ups, history safety, debugging, body/auth limits, SSE and one bounded model repair. Provider JSON/timeout contracts use mocks.

Browser coverage: real sample query/results; follow-up; explanation/checks/plan; clipboard/SQL/CSV; history reload/select; schema; dark persistence; output dialect; typo debug; refusal and disabled run; mobile overflow; manual execution; no matches; cap; retry from server error; corrupt history; formula-safe CSV. Captures do not constitute a formal comprehensive accessibility audit.

Backend baseline: **95 Python tests passed**, including deadline/AST bounds, provider HTTP-error redaction, cross-dialect numerical revenue equivalence, ambiguity, semantic live-scope routing, date/numeric explanation accuracy, byte-for-byte repeatable seeding and protection against unproved live-model optimization rewrites. The latest UI-only revision passed the TypeScript/Vite production build and **15 Playwright tests**. Checks include server-only model selection/key use, no key exposure in metadata, absence of browser credential fields, and confirmation/cancellation of clearing history from the sidebar. Python source compilation passed at initial delivery. `pip check` found no broken requirements; pinned runtime/dev install dry-run resolved successfully.

UI amendment A05 verification: the sidebar Database explorer duplicate is absent; View schema in the top bar opens the schema dialog. The visible Light/Dark switch supports keyboard Space, checked-state announcements, both directions and persistence after refresh. Seven real long-query/result cases at 1440×1000, 1366×768, 1024×640, 820×900, 390×844, 360×640 and 320×568 verify document width/height remain within the viewport, document scroll position stays zero, and the query workspace actually scrolls. Narrow-screen Chat/Query pane navigation keeps the composer reachable. Desktop/mobile screenshots were refreshed and visually reviewed, with an extra `artifacts/workspace-scroll.png` capture. Browser tests now launch a separate keyless server on 8001, so a user's live `.env` and local app on 8000 remain untouched.

UI amendment A06 verification: removed the introductory eyebrow/headline/subtitle, dialect selector and inactive sidebar assistant card. Narrowed the desktop sidebar from 244 to 220 px, reduced workspace gutters and removed its maximum-width cap. The production build and all 14 browser tests passed again. Desktop cases also assert panels begin within 100 px of the viewport top, occupy more than viewport height minus 150 px, and span the available width with at most 40 px total outer gutters. Existing fixed-page/internal-scroll, mobile, history, theme and query behavior remains covered. New UI queries use SQLite; all three backend/API dialects remain supported.

Model configuration lives only in the ignored server `.env` (GROQ_API_KEY/GROQ_MODEL). Groq-hosted `openai/gpt-oss-120b` is the default, using low reasoning effort. Private key configuration is left untouched and live inference is not part of this local audit. Current screenshots and the refreshed video show the simplified UI.

A local Git repository on branch main was initialized. No remote exists and nothing was pushed. Secret/build/environment/video ignore checks passed. The local review server was stopped after verification; run `npm start` to reopen the built app at http://127.0.0.1:8000.

Current media inspection found a playable VP9 WebM, duration **206.68 seconds**, satisfying the 180–300 second demo specification. Captions disclose keyless sample mode, actual SQLite execution and specification-defined behavior. Transcript interaction timestamps stop around 196 seconds; encoded media duration includes recording startup/close frames. A representative frame was extracted for visual review.

Deliverable amendment A07: all six local deliverables are present and linked in README and `docs/deliverables.md`. `python -m scripts.verify_deliverables` passed, verifying 137 local links, valid architecture SVG/Mermaid source, all nine documented compiled graph nodes, both exact runtime prompt files and six schema tables/five FK relationships with database integrity checks. Direct external-brief references were removed from project-authored text, runtime assumptions, prompts and demo captions. Coverage is now `docs/spec-coverage.md`. Final checks passed: **95 Python tests**, **14 browser tests**, source compilation and the production frontend build. The isolated recording server was stopped; the user's app and private environment values were left untouched.

Public Vercel behavior and arbitrary live-model accuracy remain outside local verification until publication/key configuration is authorized.

Theme/deployment amendment A08: the switch has no visible text and retains its accessible name, checked state, keyboard operation and persisted theme. Light colors are unchanged; dark mode uses neutral slate surfaces, muted teal actions and theme-appropriate syntax/status/dialog styling. All 15 browser tests passed, including measured contrast of at least 4.5:1 for explanatory text, SQL keywords/strings, the enabled primary action, plan-cost badge and refusal badge. Dark welcome/query/plan/schema screenshots were captured with finite animations settled and visually reviewed. Vercel configuration was reviewed against current official guidance; a project-specific guide was added without account actions or publication. The earlier recorded demo predates this cosmetic theme revision; current screenshots show the new appearance.
