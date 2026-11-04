# Specification amendments

## A01 — local delivery, 2026-11-05

User instruction after specs completion: "Make this app locally, deployment on github, we will do later when I'll tell". Complete implementation, local validation, sample database, documentation and demo locally. Prepare Vercel/GitHub configuration but do not publish or request deployment credentials. D01/D08 publication and submission links are intentionally deferred by the user, not implementation completion gates. Local Git initialization is allowed; no remote creation/push.

## A02 — detailed specification review

User requested an expanded requirements review and multiple detailed specs. Implementation paused while specifications 06–17 plus the index were completed. Total after expansion: 18 Markdown files, approximately 13,365 words. These detailed contracts supplement 01–04; this was completed before application implementation resumed.

## A03 — source-aware context and valid supplied SQL

Turn payloads include source dialect metadata, so prior SQL is validated in its original dialect and converted to canonical SQLite before refinement. A valid pasted query in optimize/debug mode goes directly through deterministic validation/optimization rather than allowing an LLM to apply an unproven semantic rewrite. These details implement the existing context and optimization safety contracts explicitly.

## A04 — no settings UI; environment-only model configuration

User requested removal of Settings & help and configuration of the model API key only in the server's `.env`. Remove the settings entry/dialog and unused browser access-token configuration; remove the optional shared-token gate, since this synthetic sample app no longer has a token-entry flow. Preserve history management by moving confirmed clear-all into the conversation list. API keys and model selection remain server-only, with `.env` ignored by Git; no browser storage or model-key input. Add/update local environment instructions and regression coverage for absence of settings and credential fields.

For the requested free-model recommendation, use the current Groq free-plan catalog rather than assuming the old Llama default remains free. Set the suggested/default model to `openai/gpt-oss-120b`, hosted by Groq. Keep `GROQ_MODEL` overridable in `.env`. Use low reasoning effort for GPT-OSS models with the existing bounded JSON request/independent validation. Keep live-provider verification explicitly pending until a real key is configured. This amendment supersedes earlier optional-token/settings references and the previous default model.

## A05 — single schema entry, fixed viewport, visible theme toggle

User requested removal of the redundant sidebar Database explorer entry, keeping View schema in the top bar. The main document must fit the dynamic viewport without horizontal/vertical page scrolling; chat/history overflow stays inside those panels, and the full query workspace scrolls internally so SQL, results, explanation and plan remain reachable. Remove old minimum heights that force document overflow. On narrow screens use explicit Chat/Query pane controls instead of stacking two tall panels beyond the viewport; accepted queries open the Query pane, and returning to Chat exposes the composer. Schema dialog retains its own bounded scrolling. Theme becomes a visible Light/Dark switch with clear labels/icons, keyboard operation, checked state and existing persisted preference. Validate desktop, short laptop, tablet and mobile dimensions with real long-query/result content, panel scrolling and both theme directions. This supersedes the original mobile stacked layout.

## A06 — simple, expanded workbench

User requested removal of the introductory eyebrow, headline, subtitle and SQL dialect option above the two panels, plus the inactive SQL assistant card below New conversation. Remove those elements rather than relocating them. Reduce outer workspace gutters, use the available width without an arbitrary maximum, and modestly narrow the desktop sidebar so both panels become wider as well as taller. Retain schema access, theme switch, useful history controls, mobile pane navigation and internal scrolling. New UI queries use SQLite, matching the sample database; backend/API SQLite/PostgreSQL/MySQL support and source-dialect metadata for historical queries remain intact. Update browser expectations and recording automation to no longer depend on the removed dialect selector. Verify panel position/available space and the existing viewport/scroll behavior after simplification.

## A07 — specification-based documentation and deliverable audit

User requested that all project-authored documentation, code, prompts and demo captions refer to the specification set rather than an external project brief. The authoritative product contract is specification 01 and its detailed companion specifications, with amendments in this file. Remove external-brief filenames, links and provenance descriptions; preserve every functional requirement and acceptance condition. Audit and provide six local deliverables: complete source, setup README, architecture diagram, orchestration workflow explanation, exact runtime prompts and sample database schema. Link each deliverable to concrete artifacts and relevant specifications. Refresh affected runtime wording and recorded captions without changing SQL semantics. Validate documentation links, diagrams, prompt loading, schema integrity and the local build/tests; preserve user secrets and the existing publication deferral.

## A08 — icon-only theme switch, softer dark palette and deployment guidance

User requested removing visible Light/Dark text from the theme switch, retaining sun/moon icons, switch state, keyboard accessibility, tooltip and persisted preference. Preserve light-mode colors. Replace the dark-mode green cast with neutral blue-gray surfaces, softer off-white text, muted teal accents and subtle separators. Adapt dark-mode inputs, code highlighting, buttons, selected states and warning/error badges so hard-coded light backgrounds do not glare. Check dark screenshots and readable contrast for core text/actions while retaining fixed-viewport behavior.

User also requested Vercel deployment instructions. Review checked-in configuration against current official guidance and provide a project-specific guide: GitHub import, root/build/output settings, Python entrypoint and bundled immutable database, server-only environment variables, deployment/public-access verification and troubleshooting. Do not publish, push, inspect private environment values or create account resources; publication remains deferred until explicitly requested.

## A09 — self-contained Python deployment requirements

The reported Vercel build passes the frontend but fails while parsing the runtime manifest's `-r requirements.lock` include. Publish a flat `requirements.txt` containing the exact existing runtime pins, preserving versions. Keep it synchronized with `requirements.lock` through the lock-generation script, so regeneration cannot restore the failing include wrapper. Use the canonical flat manifest for production installation; retain local test requirements separately. Verify every runtime line parses as an exact package requirement, lock/manifest pin sets match, generation produces a self-contained manifest, pip accepts the file, and backend regressions pass. Document committing the fix and redeploying without claiming the remote deployment was verified.
