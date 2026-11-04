"""Opt-in live provider smoke test; requires a real configured server-side key."""
import asyncio
from dotenv import load_dotenv
from backend.database import ROOT
load_dotenv(ROOT / ".env")
from backend import provider
from backend.agent import run_events
from backend.models import ChatRequest


async def main():
    if not provider.configured():
        raise SystemExit("No GROQ_API_KEY configured. Live verification was NOT performed.")
    cases = ["Show customers in California", "Show all employees hired after January 2024", "Monthly revenue for 2025"]
    for message in cases:
        async for event, data in run_events(ChatRequest(message=message, execute=True)):
            if event == "result":
                if data["status"] != "success" or not data["result"]:
                    raise SystemExit(f"Live verification failed: {data['message']}")
                print(f"PASS live/{provider.model_name()}: {message}; {data['result']['row_count']} rows")


if __name__ == "__main__":
    asyncio.run(main())
