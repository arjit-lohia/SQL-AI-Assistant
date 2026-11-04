# Local development, Docker and deferred Vercel deployment

Requirements: [specification 01](01-requirements.md), R09, B09 and source/setup/publication deliverables. User: hostable on Vercel; later instruction defers GitHub/Vercel publication.

## Local operation

Support Python 3.12 and Node compatible with selected locked Vite version. Use project `.venv` and `node_modules`; no global package requirement. Dependencies have a checked-in npm lockfile and exact verified Python lockfile. `.env.example` contains names/placeholders only; real `.env` ignored. Load `.env` server-side for local development.

README provides Windows PowerShell and portable shell setup where useful:

1. Create environment; install Python dev requirements/lock and npm ci.
2. Rebuild sample DB if needed with seed script (committed DB works out of the box).
3. Start backend on loopback 8000; frontend Vite on loopback 5173 proxies /api to backend.
4. Or npm run build, then one FastAPI server serves API and dist on 8000.
5. Optional set GROQ_API_KEY/GROQ_MODEL and restart server; verify health says groq.
6. Run backend/build/browser checks and inspect generated artifacts.

Local preview must use the existing app, real API and read-only database. Do not auto-open a GUI window without permission if tooling requires elevated GUI access; a reachable local URL and headless browser checks are sufficient. Keep a development server running for the user's review if requested/appropriate; identify exact URL and provider mode.

## Configuration

| Variable | Scope | Behavior |
| --- | --- | --- |
| GROQ_API_KEY | Server secret | Empty → explicit sample mode; present → live provider; never exposed via VITE_ |
| GROQ_MODEL | Server | Configurable default model; keyless health model null |

No database connection secret is needed for the immutable sample. Model credentials/configuration are server-only, with no browser settings or token input (amendment A04). Do not accept user-selected filesystem paths or provider URLs. Errors log secret-free categories. Provider quotas/timeouts are documented. No cloud account or secret is required to try supported sample examples locally. The default/recommended Groq-hosted model is `openai/gpt-oss-120b`, configurable through GROQ_MODEL.

## Docker contract

Multi-stage Dockerfile builds frontend using Node and locked npm install, then copies dist plus Python/backend/prompt/data assets into slim Python runtime. Install pinned runtime dependencies only; non-root runtime; expose port 8000; start uvicorn on 0.0.0.0; no build tools/dev/node_modules in final image. Environment secrets supplied at run time, not baked into image.

`.dockerignore` excludes .git, .venv, .tools, node_modules, .env, recordings, tests/artifacts and host caches. Compose maps loopback port 8000 and optional server env, with a read-only root filesystem where compatible and a small tmpfs only if required by dependencies. Healthcheck probes /api/health. Database remains immutable and no volume is necessary. Document docker build/run and compose commands. If Docker daemon is unavailable, report unverified build/run rather than invent a successful container test.

## Vercel-ready structure

Use a single project with Vite static frontend and Python ASGI function entrypoint `api/index.py` exporting app. Root `vercel.json` defines build/output and explicit API rewrites while preserving asset/filesystem precedence. Include backend, prompts and sample.db in Python bundle; exclude development/test/video/tool files. Runtime version selected explicitly through Vercel-supported Python configuration.

Python API routing must preserve `/api/health`, `/api/schema`, `/api/chat`, `/api/chat/stream` and `/api/execute`, not only the entrypoint path. Frontend SPA fallback must not swallow API paths. Do not use Cloudflare-specific/Vinext/D1 assumptions; the user's requested host is Vercel. Verify current primary Vercel documentation when implementing final configuration.

## Eventual deployment checklist (deferred)

When user authorizes publication: choose actual GitHub repo/account; initialize/commit clean source; push authorized branch; import into Vercel; set server env; deploy; review deployment protection and deliberately make the reviewer URL public; verify unauthenticated root, schema, chat, streaming, execution and downloads. Use actual production URL in README/submission. Ensure bundle includes sample database and a cold-start request succeeds. If using live AI, configure a real key and test it; if sample-only, disclose limitation prominently.

No GitHub remote, account resource or public deployment is created now. User authorization to create local app does not imply permission to publish later. Public-deployment requirement stays in the submission ledger as deferred by user. Do not use a temporary tunnel or Sites deployment as an unsolicited substitute.

## Acceptance

Fresh environment can reproduce database and build. One-server local URL serves actual app and API. Docker files match runtime and include all assets. Vercel config passes structural inspection and documented source layout. Secrets stay ignored and absent from frontend bundles. Git status contains only intended source/artifacts, and no remote push occurs before user's later instruction.
