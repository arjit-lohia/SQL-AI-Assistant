# Setup instructions

These steps run the frontend and API together locally. Start in the project folder containing `package.json`, `requirements.txt` and `api/`.

## Prerequisites

- Python **3.12**, available as `python` on Windows or `python3` on macOS/Linux.
- Node.js **20.17+ or 22**, with npm.
- No separate database installation: [data/sample.db](../data/sample.db) is included.
- An optional Groq API key for full AI generation. Keyless sample mode needs no account.

## Windows / PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci
npm run build
npm start
```

Using the Python executable directly avoids PowerShell activation-policy problems. If `python` is unavailable but the Python launcher is installed, use `py -3.12 -m venv .venv` for the first command.

## macOS / Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
npm run build
npm start
```

The launcher automatically selects the virtual environment's Python on either platform.

## Open and stop the app

Open **http://127.0.0.1:8000**. One Python server serves both the production frontend and `/api`. No login is required. Stop it with **Ctrl+C**. On later runs use `npm start`; rebuild with `npm run build` after frontend changes.

For runtime dependencies alone, install `requirements.txt`; the quick start installs `requirements-dev.txt` so the test suite is ready too. Runtime pins are flat in `requirements.txt` for Vercel and synchronized with `requirements.lock`. Regenerate both through [lock_dependencies.py](../scripts/lock_dependencies.py) only after intentional dependency upgrades.

## Optional live model

If `.env` does not exist, copy `.env.example` to `.env`. Otherwise edit the existing file without overwriting its values.

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Obtain your key from [Groq](https://console.groq.com/keys). Restart the server after changing environment values. The UI and `/api/health` identify sample or configured AI mode. A configured provider error is reported rather than silently falling back to sample answers.

The API key belongs only in the server environment. `.env` is ignored by Git; never commit it, paste it into chat, or put it in a `VITE_` variable. There is no settings page or browser credential storage. Model access and quotas depend on your provider account.

To test a real configured provider deliberately:

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_live
```

On macOS/Linux replace the executable with `.venv/bin/python`. This makes real requests using your provider quota. Mock-provider tests alone do not verify live model quality.

## First queries and dialects

Select **SQLite**, **PostgreSQL** or **MySQL** in the query workspace header. This chooses the output syntax for your next request; historical SQL retains its original dialect. All execution and query plans use the read-only SQLite sample database, including translated PostgreSQL/MySQL output. Unsupported translations fail validation rather than claiming native execution.

Sample mode supports these examples:

```text
Show all customers
Only those from California
Sort by name
Only the first 10
```

```text
Give all people from Austin
Show people who joined before 24th Oct, 2024
```

The second conversation keeps `city = 'Austin'` and adds `created_at < '2024-10-24'`. People means customers; joined means account creation. Other valid date formats include `2024-10-24` and `24 October 2024`. Invalid or ambiguous dates ask for clarification.

Other supported examples: `Show all employees hired after January 2024` (inclusive January 1), `Monthly revenue for 2025`, `Top 5 products by revenue`, table counts and pasted read-only SELECTs. Sample mode supports clear unique schema typo repairs in Debug mode and safe optimization. Other requests clarify that full natural-language support requires the live model.

Use **New conversation** to clear context. Conversations and theme are stored in the current browser with bounded history; there is no account sync. You can delete individual conversations or clear all history in the sidebar. Follow-ups send recent messages and revalidated SQL, so a backend restart does not require shared server memory.

## Frontend development

Start the API in one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.index:app --host 127.0.0.1 --port 8000
```

In another terminal, run `npm run dev` and open the URL Vite prints. Vite proxies `/api` to port 8000. The backend needs restarting after Python or environment changes; Vite refreshes frontend edits automatically.

## Database

The six-table commerce database has 1,426 synthetic rows. It is immutable at runtime and safe to bundle for serverless reads. [Schema and relationships](database.md) describe tables and fields. Revenue uses historical line-item values from non-cancelled orders; data spans 2023–2025 and uses synthetic USD amounts.

To rebuild the same dataset:

```powershell
.\.venv\Scripts\python.exe scripts/seed.py
```

Restart the backend afterward because connections/schema caches assume a fixed asset. No runtime writes or database volume are required.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm run build
npx playwright install chromium
npm run test:e2e
.\.venv\Scripts\python.exe -m scripts.verify_deliverables
```

Use `.venv/bin/python` on macOS/Linux. Browser tests start an isolated sample-mode server on **8001**, leaving your app on 8000 and private `.env` configuration untouched. See [verification.md](verification.md) for actual outcomes and limitations.

Queries are independently validated before execution, limited to 500 returned rows and protected by time/VM-step budgets. CSV exports the displayed rows. See [security.md](security.md) for SQL restrictions, limits and production considerations.

## Docker

With Docker and Compose available:

```sh
docker compose up --build
```

Or build/run directly after creating `.env` as described above:

```sh
docker build -t queryatlas .
docker run --rm -p 127.0.0.1:8000:8000 --env-file .env queryatlas
```

Open port 8000. The multi-stage build includes React, pinned Python runtime dependencies and the database, and runs as a non-root user. Compose uses a read-only filesystem. Container execution is only verified when a Docker daemon is available; consult the verification report.

## Vercel

Follow [the deployment guide](vercel-deployment.md) for GitHub import, build settings, Python entrypoint, server environment variables and production checks. The checked-in configuration bundles the immutable SQLite database; no database provisioning is needed. Persistent writes would require a separate database design.

No remote push or deployment is performed by local setup. Verify your actual deployment before adding its public URL to [submission.md](submission.md).

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Missing `dist/index.html` | Run `npm run build` before `npm start`. |
| Python/module not found | Create `.venv` with Python 3.12 and install the Python requirements using that environment's executable. |
| Port 8000 already in use | Stop the earlier app or set `QUERYATLAS_PORT` for `npm start`; use the matching browser URL. Vite's development proxy still expects port 8000. |
| Sample mode after adding a key | Save the root `.env`, check the variable name and restart the backend. An already-set process environment value takes precedence. |
| Provider rejects key, times out or reaches quota | Check server configuration and provider account, then retry. No SQL is executed from a failed response. |
| A sample request asks for clarification | Use the listed examples/pasted SELECTs or configure the live model. |
| New follow-up unexpectedly broadens results | Check it is in the same conversation; additive refinements should retain filters. Simple single-table lost-filter candidates trigger one repair and fail safely if still incorrect. Complex-query intent remains model-dependent. |
| Vercel Python requirement parse error | Commit the flat `requirements.txt` and redeploy that commit. See deployment troubleshooting; do not replace it with a nested lockfile include. |
| Large demo video absent from a clone | Recordings are ignored by Git. See [transcript](../artifacts/demo-transcript.md); run the built app on 8000 and `npm run demo` to record again. |
