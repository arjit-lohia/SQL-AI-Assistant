import asyncio
from backend.agent import run_events
from backend.models import ChatRequest


async def main():
    for dialect in ["sqlite", "postgres", "mysql"]:
        for question in ["Show customers in California", "Monthly revenue for 2025", "Top 5 products by revenue", "Show all employees hired after January 2024"]:
            async for event, data in run_events(ChatRequest(message=question, dialect=dialect, execute=True)):
                if event == "result":
                    print(dialect, question, data["status"], data["message"], data["diagnostics"], (data["result"] or {}).get("row_count"))


asyncio.run(main())
