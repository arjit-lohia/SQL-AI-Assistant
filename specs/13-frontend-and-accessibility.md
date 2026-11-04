# Frontend, responsive interaction and accessibility specification

Requirements: [specification 01](01-requirements.md), R08, B01 and B05, with approved UI amendments. Quality focus: frontend usability (10%).

## Screen structure

Build a simple business-data workspace. Left rail: QueryAtlas brand, New conversation and chronological conversation history with confirmed clear-all action; no inactive SQL assistant card (amendment A06). View schema in the top bar is the only schema-explorer entry; no duplicate sidebar entry (amendment A05). No Settings & help entry/dialog or browser credential fields (amendment A04). Top bar retains an icon-only sun/moon theme switch with an accessible name, checked state, keyboard support, tooltip and persisted preference (amendment A08). Dark mode uses soft slate surfaces, muted teal accents, subdued off-white text and theme-appropriate warning/code/button colors; retain the light-mode palette. Keep the introductory eyebrow/headline/subtitle removed. Amendment A10 restores a compact SQLite/PostgreSQL/MySQL selector inside the query workspace header, applying to the next turn while historical SQL retains its source dialect. Main region starts directly with the conversation and query workspace, using narrower outer gutters and the available width, sized to the dynamic viewport with no document scrolling. Chat, history and query workspace overflow internally. Mobile collapses history to a drawer and exposes Chat/Query pane buttons; accepted queries open Query and returning to Chat exposes the composer. All core functionality remains reachable at 320–390 px widths without stacking tall panels outside the viewport.

Use a readable system sans font, monospaced SQL, light warm canvas, dark ink and restrained teal. Dark mode follows initial system preference unless overridden, then persists user choice. Color must not be the only status indicator. No imagery is necessary for a SQL workbench; use an established icon library rather than generate decorative assets.

## Component/state requirements

| Component | Empty / normal | Loading / error |
| --- | --- | --- |
| Chat | Welcome, SQL-only description and four real example prompts | Visible pending turn, graph progress, cancellation and safe failure |
| Composer | Labeled textarea, generate/optimize/debug mode, submit, auto-run | Disable duplicate send; preserve failed input; Enter/Shift+Enter behavior |
| SQL panel | Validated SQL, line numbers, dialect badge and checks | Empty guidance before success; no raw candidate during generation |
| Explanation | Plain-English final query meaning, assumptions, diagnostics and advice | Distinguish clarification/refusal from system error |
| Results | Real columns/rows, row count, elapsed time, SQLite label, CSV | Run prompt before execution; running state; zero rows; truncation; execution error |
| Query plan | Real plan steps and relative cost/caveat | No plan for invalid SQL; actionable unavailable state |
| History | Titles, active indication, create/select/delete | Empty history, bounded persistence notice |
| Schema | Six tables, columns/types/keys, relationship information, row counts | Connecting/disconnected; retry fetch; never empty fake schema |

Required panels may use tabs, but SQL and its explanation must be easy to locate without sending another request. A refusal does not leave stale SQL displayed as the refused turn's output; selecting an earlier accepted turn explicitly restores it.

## Actions

- Click example: populate/send its real question through the same API path.
- Send: append user turn, clear input after acceptance, show progress, append terminal assistant turn and select its output.
- Mode: controls intent, with help text explaining pasted SQL for optimize/debug.
- Run query: send selected validated SQL/dialect to independently validating execute endpoint. Update the same turn's result/plan. Disable for no SQL, running/invalid output.
- Copy SQL: use clipboard, announce success; display manual-copy guidance if unavailable.
- Download SQL/results: files contain actual selected query/result. Disable actions until data exists.
- Select dialect: applies to new turns; existing turns retain their original dialect and clear labeling. A follow-up translates canonical context correctly.
- New/delete/clear history: obey context specification; destructive local clearing asks confirmation.
- Model configuration: server-only `.env`/environment variables, with read-only provider/sample status in the UI. No browser key/token entry or settings flow.

## Streaming UX

Progress labels reflect actual graph events (checking scope, loading schema, generating, validating, optimizing, running, explaining). Do not fake time-based backend progress. Once accepted, incremental explanation is readable while the terminal result arrives. Screen reader announcements are throttled to stage changes/terminal result rather than every character. Abort and terminal network errors release loading state and expose retry.

## SQL highlighting

Tokenize into keyword, identifier, string, number, comment and punctuation styles. Render tokens as React text nodes, never `dangerouslySetInnerHTML`. A string containing `<script>` remains visible text. Preserve whitespace and offer horizontal scrolling inside the code block, not whole-page overflow. Long queries and tables scroll in their bounded panels; mobile controls wrap.

## Accessibility

Semantic landmarks, headings, form labels, tab names/states and real buttons. All icon-only controls have accessible names and title hints. Visible keyboard focus, comfortable targets, readable contrast and reduced-motion support. Modals/drawers manage focus, close on Escape and restore focus to trigger. Tabs expose active state and keyboard-operable controls. Errors use role alert; progress uses polite live region. Keyboard users can submit, copy, run, export, switch history/theme and inspect schema. Do not hijack Enter in a textarea while a composition event is active.

## Acceptance

Desktop 1440×900 and mobile 390×844 show no page-level horizontal overflow. Test dark/light persistence, keyboard submission, selection of older outputs, disabled actions, loading/error/zero rows, schema retry, copy/export and theme contrast. Capture desktop/mobile screenshots of actual working query state. No browser console errors during main flows; report observed accessibility limits rather than claim a full formal audit.
