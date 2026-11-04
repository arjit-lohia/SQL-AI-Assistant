# Local deliverable audit

Acceptance source: [product requirements](../specs/01-requirements.md), [deliverable specification](../specs/17-deliverables-and-demo.md) and [amendment A07](../specs/05-amendments.md). All six requested local deliverables are incorporated.

| Deliverable | Concrete artifacts | Verification |
| --- | --- | --- |
| 1. Complete source code | [React frontend](../src/), [FastAPI entrypoint](../api/index.py), [LangGraph/backend](../backend/), [scripts](../scripts/), [tests](../tests/), [npm manifest](../package.json), [npm lock](../package-lock.json), [runtime dependency lock](../requirements.lock), [Dockerfile](../Dockerfile), [Vercel configuration](../vercel.json) | Python tests, TypeScript/production build and browser tests; no generated-only source or missing application modules |
| 2. README with setup instructions | [README.md](../README.md), [environment template](../.env.example) | Windows and macOS/Linux setup, local run/dev/build, model environment configuration, deterministic data creation, tests, Docker and deferred deployment instructions |
| 3. Architecture diagram | [Standalone rendered SVG](architecture.svg), [Mermaid source](architecture.mmd), [architecture explanation](architecture.md) | SVG XML validation; component, storage and model trust boundaries reviewed against actual source |
| 4. LangGraph workflow explanation | [Workflow document](workflow.md), [implemented graph](../backend/agent.py), [orchestration specification](../specs/08-agent-and-prompts.md) | Real compiled StateGraph, node/state/routing explanation, bounded repair, context isolation and streamed public projection; graph/API integration tests |
| 5. Prompts used | Exact [system prompt](../prompts/system.txt) and [repair prompt](../prompts/repair.txt); loaded by [provider.py](../backend/provider.py) | Files exist and are used at runtime; provider request tests verify the model request contract; no separate undocumented model prompt |
| 6. Sample database schema | Executable [DDL](../data/schema.sql), [data dictionary/ER relationships](database.md), [seed script](../scripts/seed.py), [ready-to-use SQLite file](../data/sample.db) | Six tables, five FK relationships, integrity/FK checks, deterministic seed reproduction and read-only execution tests |

## Source organization

```text
api/                 FastAPI and Vercel ASGI entrypoint
backend/             LangGraph, model provider, SQL validation and SQLite access
src/ + public/       React/TypeScript UI, styles and local assets
prompts/             Exact runtime system and repair instructions
data/                Schema DDL and bundled sample database
scripts/             Seed, local launcher, live-model check and recording tooling
tests/               Backend/security/API tests and browser acceptance suite
specs/               Product contracts, detailed design and approved amendments
docs/                Architecture, workflow, schema, security and verification
```

Dependencies are reproducible through npm/Python lockfiles. Installation instructions build `dist` locally; dependencies, build output and secrets are intentionally excluded from source control. The optional live-model integration needs a server-side Groq key; keyless sample mode remains usable without cloud credentials. No real key is included in any deliverable.

## Status boundaries

The six local artifacts are complete. Real-provider quality/connectivity is only verified after configuring and testing an actual key; mocked tests are identified as such. Docker runtime and public Vercel behavior are not claimed verified where unavailable. GitHub/Vercel publication remains deferred by user instruction and does not prevent reviewing these six local artifacts.

Run the verification commands in [README](../README.md). Exact test/build outcomes, diagram/document checks and recorded artifacts are in [verification.md](verification.md). Feature-level traceability is in [spec-coverage.md](spec-coverage.md).
