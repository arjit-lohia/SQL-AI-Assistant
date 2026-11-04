# Deploy QueryAtlas on Vercel

This guide prepares a single Vercel project for the existing React/Vite frontend and Python/FastAPI API. It does not create a deployment. The application source includes the required configuration; actual cloud deployment remains unverified until you publish and check it.

## 1. Push the project to GitHub

Create an empty repository in your GitHub account and push the project root. The root is the folder containing `package.json`, `vercel.json`, `requirements.txt`, `api/` and `src/`.

For the existing local Git repository, if you have not committed/pushed yet:

```powershell
git add .
git commit -m "Prepare QueryAtlas"
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the URL with your repository's actual URL. If `origin` already exists, use that remote or update it deliberately rather than adding it again. `.gitignore` excludes `.env`, local environments, installed dependencies, generated recordings and local reference documents. Include `data/sample.db`, `data/schema.sql`, the prompt files and Python/npm lockfiles in the source.

## 2. Import the repository

In the Vercel dashboard, choose **Add New → Project**, connect GitHub if needed, and import the repository. Use these project settings, matching [vercel.json](../vercel.json):

| Setting | Value |
| --- | --- |
| Root directory | Repository root (`./`) |
| Framework preset | **Vite** |
| Install command | `npm ci` |
| Build command | `npm run build` |
| Output directory | `dist` |
| Python version | `3.12`, provided by [.python-version](../.python-version) |

Keep **Vite** as the selected framework for this mixed frontend/API project. The API is the file-based Python function exported from `api/index.py`; do not change the whole project to the standalone FastAPI preset. Vercel supports Vite projects with functions and Python ASGI handlers. [Vite deployment](https://vercel.com/docs/frameworks/frontend/vite), [Python API functions](https://vercel.com/docs/functions/runtimes/python/api-directory).

## 3. Set server environment variables

Before deploying, add these variables to the Vercel project's environment-variable settings:

| Name | Value | Scope/type |
| --- | --- | --- |
| `GROQ_API_KEY` | Your actual Groq key | Server secret; Production and Preview if you want AI in previews |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Server configuration; same environments |

Your local `.env` is intentionally not uploaded. Enter the values in Vercel; do not commit the file or prefix these names with `VITE_`. If the key is omitted, the deployed app uses the explicitly limited sample mode. Changes to environment variables require a new deployment to take effect. [Vercel environment variables](https://vercel.com/docs/environment-variables).

## 4. Deploy the entire project

Choose **Deploy**. Vercel builds the frontend and installs the root Python requirements for the API. No Docker image, separate Python host or external database is needed for the current read-only sample app.

The checked-in routing sends `/api/*` to the Python function and serves the frontend/static assets separately. `backend/`, `prompts/` and `data/sample.db` are included in the function. The database is a small immutable deployment asset opened read-only; it is not writable persistent serverless storage. Application changes are delivered through subsequent Git pushes/deployments.

## 5. Verify the production domain

Use the project's production domain, such as `https://YOUR-PROJECT.vercel.app`, and open it in a private/incognito window. Check:

1. `/` opens the app and shows the sample database connected.
2. `/api/health` returns `status: ok` and `database: connected`; provider is `groq` when its key is configured, otherwise `sample`.
3. `/api/schema` lists all six business tables.
4. `Show customers in California` returns validated SQL and actual rows; a follow-up preserves the filter.
5. SQL/CSV downloads work and the response shows graph progress.

If the production URL asks for Vercel login and you want public access, inspect the project's Deployment Protection settings. Make the production domain public while retaining preview protection if desired, then retest without a signed-in Vercel session. Production domains and generated deployment URLs can have different protection rules. [Deployment Protection](https://vercel.com/docs/deployment-protection).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Frontend works, `/api/health` does not | Confirm root directory, Vite preset, checked-in API routes and Python function build/runtime logs |
| Database disconnected | Confirm `data/sample.db` was committed and included in the Python function; regenerate locally with `scripts/seed.py` if missing, then redeploy |
| Always says Sample mode | Set `GROQ_API_KEY` for the environment you actually deployed, then redeploy |
| Provider rejects the key/model or returns quota errors | Check the server variable names, Groq account/model access and limits; the app returns safe provider errors |
| Prompt file unavailable / import error | Confirm `prompts/`, `backend/`, `requirements.txt` and `requirements.lock` are committed; inspect function logs |
| API receives HTML | Check the API rewrite precedes the frontend fallback in `vercel.json` |
| Login screen for reviewers | Check the production-domain protection scope and test in a private window |

After successful verification, record the real production and GitHub URLs in [submission.md](submission.md). Local tests validate application behavior; they do not substitute for this deployed smoke test.
