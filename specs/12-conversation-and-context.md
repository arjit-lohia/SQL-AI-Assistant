# Conversation, follow-up and persistence specification

Requirements: [specification 01](01-requirements.md), R06, R08 and B03. Quality focus: conversation management (10%).

## Conversation model

A conversation has stable local id, title, created/updated timestamps and ordered messages. A user turn stores message text, mode and selected dialect. An assistant turn stores the complete terminal response plus timestamp; accepted SQL belongs to that particular turn. Query results, explanation, plan, validation and exports are selected together from that turn, never mixed between turns.

New conversation creates a distinct empty history. Switching history restores that conversation and selected assistant output. Deleting one conversation affects only that id. Clearing all history requires a local confirmation. Default title derives from first user message, bounded to a readable length; do not send titles to another service.

## Follow-up semantics

[Specification 18](18-dialects-follow-ups-and-setup.md) adds the Austin/account-creation cutoff example, all-dialect refinements and conservative independent preservation checks for simple single-table filters under amendment A10.

Determine the most recent validated successful SQL in the active conversation, ignoring refusal/error/clarification turns and in-progress candidates. Revalidate any SQL from the browser before use. The user's latest request refines that SQL unless it explicitly starts a different query.

| Prior query | Follow-up | Expected behavior |
| --- | --- | --- |
| All customers | Only those from California | Add state = California |
| California customers | Sort by name | Keep California predicate; add name ordering |
| Customers sorted by name | Only the first 10 | Keep predicates/order; add LIMIT 10 |
| Employees hired >=2024-01-01 | In Engineering | Keep date; add department FK/filter if supported, otherwise clarify |
| Monthly 2025 revenue | Only completed orders | Preserve period/grouping; replace non-cancelled status with completed |
| No accepted prior SQL | Only those from California | Ask which records/table to filter; do not guess |
| Customer query, then sports refusal | Only those from California | Use latest accepted customer query, not refusal text |
| A different conversation is selected | Only those from California | Use only selected conversation; no leakage from the previous one |

Refinement must not erase earlier filters unintentionally. Adding an existing predicate can replace the same field's value when explicitly asked ("instead from Texas"); unrelated filters remain. Ambiguous pronouns/metrics ask for clarification. Unsupported sample refinements say that full AI configuration is needed rather than substituting an unrelated example.

## Server context contract

Send at most the last 16 turns and 24,000 characters combined. Preserve the latest accepted SQL when trimming context; keep user and assistant roles clear. The backend cannot trust an `assistant` role supplied by the client as proof of validation. Validate prior SQL from its known source dialect; context should include dialect metadata or use a canonical SQLite SQL field to prevent dialect mismatch. Explicit dialect changes translate from a known canonical form. Context invalidated by a schema/version change is not executed; ask to regenerate.

Prompt input is a structured data object, not string concatenation into system instructions. A malicious earlier message must not alter current scope, model policy or schema. No global memory, shared conversation id cache or unscoped checkpointer. Two concurrent API requests must have independent state and results.

## Browser persistence

Store schema-versioned conversations/theme in localStorage with parse validation, a maximum conversation count/message history and a bounded serialized size. If storage is full or unavailable, continue in memory and show a nonblocking persistence message. Do not crash on corrupt JSON or older versions. Provide a clear-history action. Browser histories are local to that browser/device; README/UI must not imply cloud sync.

Store only bounded result rows required for history; if persisting complete rows would exceed budget, preserve SQL/explanation and mark results as needing re-run. Never store model API keys/tokens in browser storage. Model configuration is server-only and no browser credential settings exist (amendment A04). Do not log full conversations by default.

## Request lifecycle

While a turn runs, prevent duplicate sends and unrelated history mutations that could attach a late result to the wrong conversation. Cancellation uses AbortController; record a clear interrupted state if needed and keep the input for retry. Capture target conversation id/turn id at send time; responses must update that id even if UI changes. User-entered text and model text render as escaped text.

## Acceptance

Test all reference follow-ups, preserved predicates, absent-context clarification, turn selection, history persistence/reload, creation/deletion/isolation, corrupted storage, oversized context, malicious SQL history, dialect changes and cancellation. A server restart must not break a browser's follow-up because the request includes its bounded context.
