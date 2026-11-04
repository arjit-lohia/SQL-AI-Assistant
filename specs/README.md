# QueryAtlas specification set

Source of truth: [Product requirements and acceptance contract](01-requirements.md), the detailed specifications linked below, and [approved amendments](05-amendments.md). This set distinguishes product requirements, user instructions and implementation choices.

The initial specifications were completed before implementation. At the user's request, application implementation paused for an expanded requirements review and completion of the detailed specifications below. Configuration, database DDL/seed and request models must follow these contracts and their approved amendments.

## Authority and status

1. User instructions govern delivery timing: spec-first development; create the missing sample database; local app now; GitHub and Vercel publication later when explicitly requested.
2. Specification 01 defines product scope, including the additional features requested by the user.
3. Detailed specifications define implementation and acceptance, including resource limits, design language, provider configuration and architecture.
4. A spec is a requirement, never evidence that its implementation works. Verification belongs in the coverage ledger and test results.

All detailed specifications below are COMPLETE as design contracts. Implementation/validation status is tracked separately. Publication is DEFERRED BY USER. Live provider verification requires a configured server-side key.

## Reading order

| Document | Purpose |
| --- | --- |
| [01-requirements](01-requirements.md) | Complete R/B/D traceability and release contract |
| [02-design](02-design.md) | Cross-system architecture and initial behavior contract |
| [03-api](03-api.md) | Wire format and request/response models |
| [04-validation-and-delivery](04-validation-and-delivery.md) | Initial verification and handoff gates |
| [05-amendments](05-amendments.md) | User-authorized changes, including deferred publication |
| [06-product-and-source-audit](06-product-and-source-audit.md) | Page-by-page audit, personas, journeys, evaluator weights and ambiguity decisions |
| [07-database-and-schema](07-database-and-schema.md) | Tables, keys, metrics, seed invariants and serverless storage |
| [08-agent-and-prompts](08-agent-and-prompts.md) | Real LangGraph state machine, routing, model contract and prompts |
| [09-sql-generation-and-dialects](09-sql-generation-and-dialects.md) | Generation rules, examples, three dialects and semantic limits |
| [10-sql-validation-and-guardrails](10-sql-validation-and-guardrails.md) | Validation pipeline, join rules, threat model and refusals |
| [11-optimization-debugging-and-cost](11-optimization-debugging-and-cost.md) | Safe rewrites, correction, indexes and EXPLAIN estimates |
| [12-conversation-and-context](12-conversation-and-context.md) | Follow-ups, isolation, browser persistence and history safety |
| [13-frontend-and-accessibility](13-frontend-and-accessibility.md) | Screens, component states, responsive behavior and keyboard access |
| [14-api-streaming-and-exports](14-api-streaming-and-exports.md) | HTTP/SSE lifecycle, error semantics, CSV/copy/download |
| [15-testing-and-evaluation](15-testing-and-evaluation.md) | Detailed unit, integration, adversarial and browser acceptance matrix |
| [16-local-docker-and-vercel](16-local-docker-and-vercel.md) | Local operation, reproducible builds, Docker and deferred Vercel deployment |
| [17-deliverables-and-demo](17-deliverables-and-demo.md) | Every deliverable, 3–5 minute recording and honest submission ledger |

## Change discipline

Amend a design contract before implementing changed behavior. Revalidate affected acceptance tests after changes. Do not silently weaken validation to make examples pass. If a supported query cannot be validated safely, clarify or report a limitation. Each feature must connect to a requirement in this specification set or the user's explicit instruction.
