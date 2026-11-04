# Local handoff and publishing checklist

Current delivery: local implementation. The user explicitly deferred GitHub and Vercel publication until a later instruction.

| Item | Location / state |
| --- | --- |
| App | http://127.0.0.1:8000 when the local server is running |
| Source | This project directory; publication not performed |
| GitHub URL | Deferred by user — no remote repository created/pushed |
| Public deployed URL | Deferred by user — no Vercel deployment performed |
| Setup | [README quick start](../README.md) and [complete setup instructions](setup.md) |
| Demo | ../artifacts/queryatlas-demo.webm — **3:26.68**, actual captioned local recording (ignored large binary) |
| Transcript | ../artifacts/demo-transcript.md |
| Schema/seed | ../data/schema.sql, ../scripts/seed.py, ../data/sample.db |
| Architecture/workflow | architecture.svg, architecture.mmd, workflow.md |
| Exact prompts | ../prompts/system.txt, ../prompts/repair.txt |
| Specifications | ../specs/README.md |
| Verification and coverage | verification.md, spec-coverage.md, deliverables.md |

No test login is required for the synthetic sample. Sample mode requires no cloud key and is explicitly limited. Live Groq generation needs server-side GROQ_API_KEY and optional GROQ_MODEL in `.env`; there are no browser credential settings. No real-provider verification is claimed without a key.

Assumptions: replace missing supplied schema with authorized synthetic commerce dataset; read-only bundled SQLite; browser-local history; explicit fixed-year examples; non-cancelled historical revenue; three output dialects with SQLite sample execution; relative SQLite plan estimate; no production accounting/tenant auth claims.

When publication is authorized, use the user's chosen GitHub and Vercel destinations, configure secrets, verify a publicly accessible cold deployment without login and update these entries with real links. Upload the actual video to an approved destination if a shareable video URL is required. These publication deliverables are defined in [specification 17](../specs/17-deliverables-and-demo.md) and deferred under amendment A01.
