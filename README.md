# QueryAtlas

Ask questions about a sample commerce database, get validated SQL, and explore the results.

![QueryAtlas desktop](artifacts/desktop.png)

- Generate, debug and optimize read-only SQL with a real LangGraph workflow.
- Choose **SQLite, PostgreSQL or MySQL** output in the query workspace.
- Refine queries in conversation while keeping previous filters.
- Inspect explanations, results and query plans; copy SQL or export CSV.
- Use the included database immediately, with an optional server-side Groq model.

**All queries execute against the bundled SQLite database.** PostgreSQL/MySQL output is translated and validated before execution; native database connections are not included.

## Quick start

Install **Python 3.12** and **Node.js 20.17+ or 22**, then run these commands from the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci
npm run build
npm start
```

Open **http://127.0.0.1:8000**. The included database needs no setup or external service. Stop the app with Ctrl+C; use `npm start` to run it again.

**[Complete setup instructions](docs/setup.md)** include macOS/Linux commands, development mode, environment configuration, tests, Docker and troubleshooting.

## Enable the AI model

Create `.env` from `.env.example` if it does not already exist. Add your server-side credentials and restart the app:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Without a key, the app uses clearly labelled **Sample mode**, which supports documented examples and pasted SELECT queries. Full natural-language generation requires the model. Keep `.env` private; never use a frontend `VITE_` variable for the key.

## Try a conversation

```text
Give all people from Austin
Show people who joined before 24th Oct, 2024
Sort by name
Only the first 10
```

Here, people means customers and joined means account creation. Each follow-up retains earlier filters. Change the SQL dialect before your next question; start a **New conversation** for an unrelated request.

Other examples: `Show customers in California`, `Monthly revenue for 2025`, and `Top 5 products by revenue`.

## Verify and deploy

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm run build
npx playwright install chromium
npm run test:e2e
```

[Vercel deployment guide](docs/vercel-deployment.md) · [Validation results and limits](docs/verification.md) · [Demo video](artifacts/queryatlas-demo.webm) · [Demo transcript](artifacts/demo-transcript.md)

## Submission deliverables

| Deliverable | Where to find it |
| --- | --- |
| Complete source | [Frontend](src/), [API](api/), [backend](backend/), [scripts](scripts/) and [tests](tests/) |
| Setup instructions | This README and the [complete setup guide](docs/setup.md) |
| Architecture diagram | [Diagram](docs/architecture.svg) and [explanation](docs/architecture.md) |
| LangGraph workflow | [Nodes, state and routing](docs/workflow.md) |
| Prompts used | [System prompt](prompts/system.txt) and [repair prompt](prompts/repair.txt) |
| Sample database schema | [SQL schema](data/schema.sql), [data dictionary](docs/database.md) and [ready-to-use database](data/sample.db) |

Built to the [project specifications](specs/README.md). See [security](docs/security.md), [deliverable audit](docs/deliverables.md) and [submission checklist](docs/submission.md) for review details.
