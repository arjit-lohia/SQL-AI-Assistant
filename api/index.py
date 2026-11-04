"""Vercel ASGI entrypoint. The same app serves the local built frontend."""
from contextlib import closing
import asyncio
import json
import logging
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from backend import database, provider
from backend.agent import run_events
from backend.models import ChatRequest, ExecuteRequest
from backend.sql import validate, CHECKS, InvalidSQL

log = logging.getLogger("queryatlas")
app = FastAPI(title="QueryAtlas", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)


class RequestBoundary:
    """Bound request bodies even when Content-Length is omitted or dishonest."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        async def secure_send(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers += [(b"x-content-type-options", b"nosniff"), (b"referrer-policy", b"same-origin")]
                if scope["path"].startswith("/api"):
                    headers.append((b"cache-control", b"no-store"))
                else:
                    headers.append((b"content-security-policy", b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"))
                message["headers"] = headers
            await send(message)
        if scope["method"] in {"POST", "PUT", "PATCH"}:
            chunks, length = [], 0
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                length += len(message.get("body", b""))
                if length > 131072:
                    return await JSONResponse({"detail": "Request is too large. Shorten the query or conversation."}, status_code=413)(scope, receive, secure_send)
                chunks.append(message.get("body", b""))
                if not message.get("more_body"):
                    break
            sent = False
            async def replay():
                nonlocal sent
                if not sent:
                    sent = True
                    return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
                return await receive()
            await self.app(scope, replay, secure_send)
        else:
            await self.app(scope, receive, secure_send)


app.add_middleware(RequestBoundary)


@app.get("/api/health")
def health():
    try:
        with closing(database.connect()) as db:
            db.execute("SELECT id FROM customers LIMIT 1").fetchone()
        return {"status": "ok", "database": "connected", "provider": "groq" if provider.configured() else "sample", "model": provider.model_name() if provider.configured() else None, "version": "1.0.0"}
    except sqlite3.Error:
        return JSONResponse({"status": "error", "database": "disconnected", "message": "Sample database is unavailable. Rebuild it with scripts/seed.py."}, status_code=503)


@app.get("/api/schema")
def get_schema():
    try:
        return database.schema()
    except sqlite3.Error:
        raise HTTPException(503, "The sample schema is unavailable. Rebuild the sample database.") from None


def safe_error(exc):
    log.warning("Request failed: %s", type(exc).__name__)
    if isinstance(exc, sqlite3.OperationalError) and "interrupt" in str(exc).lower():
        return "The query exceeded the sample execution budget. Please simplify it."
    return "The request could not be completed safely. Check the query and schema, then retry."


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        async for event, data in run_events(request):
            if event == "result":
                return data
    except Exception as exc:
        raise HTTPException(422, safe_error(exc)) from None


@app.post("/api/chat/stream")
async def stream(request: ChatRequest):
    def frame(name, data):
        return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False, allow_nan=False)}\n\n"
    async def events():
        try:
            async for event, data in run_events(request):
                if event == "result" and data.get("explanation"):
                    words = data["explanation"].split(" ")
                    for i in range(0, len(words), 8):
                        yield frame("text", {"delta": (" " if i else "") + " ".join(words[i:i+8])})
                        await asyncio.sleep(0.015)
                yield frame(event, data)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            yield frame("error", {"message": safe_error(exc)})
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/execute")
def execute(request: ExecuteRequest):
    try:
        accepted = validate(request.sql, request.dialect)
        return {"sql": accepted.sql, "dialect": request.dialect, "validation": {"valid": True, "checks": CHECKS}, "cost": database.query_plan(accepted.sqlite), "result": database.execute(accepted.sqlite)}
    except InvalidSQL as exc:
        raise HTTPException(400, str(exc)) from None
    except sqlite3.Error as exc:
        raise HTTPException(422, safe_error(exc)) from None


if (ROOT / "dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="frontend")
