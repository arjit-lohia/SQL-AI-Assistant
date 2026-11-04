import json
import os
import httpx
from pydantic import ValidationError
from backend.database import ROOT
from backend.models import ModelOutput


class ProviderError(RuntimeError):
    pass


def configured():
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def model_name():
    return os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-120b"


async def propose(payload: dict, repair: bool = False) -> ModelOutput:
    system = (ROOT / "prompts/system.txt").read_text(encoding="utf-8")
    if repair:
        system += "\n" + (ROOT / "prompts/repair.txt").read_text(encoding="utf-8")
    model = model_name()
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload)}], "temperature": 0, "max_completion_tokens": 1800, "response_format": {"type": "json_object"}}
    if model.startswith("openai/gpt-oss-"):
        body["reasoning_effort"] = "low"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(18.0, connect=5.0)) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": "Bearer " + os.environ["GROQ_API_KEY"]}, json=body)
            if response.status_code == 401:
                raise ProviderError("The AI provider rejected the server key. Check GROQ_API_KEY and restart the server.")
            if response.status_code == 429:
                raise ProviderError("The AI provider quota or rate limit was reached. Please retry later.")
            if response.is_error:
                raise ProviderError("The AI provider is unavailable or the configured model is unsupported. Check GROQ_MODEL or retry.")
            if len(response.content) > 64000:
                raise ProviderError("The AI provider returned an oversized response. Please retry with a simpler question.")
            data = response.json()
            return ModelOutput.model_validate_json(data["choices"][0]["message"]["content"])
    except httpx.TimeoutException:
        raise ProviderError("The AI provider timed out. Your query was not executed. Please retry.") from None
    except httpx.HTTPError:
        raise ProviderError("Could not connect to the AI provider. Check the server network and retry.") from None
    except (ValidationError, ValueError, KeyError, IndexError, TypeError):
        raise ProviderError("The AI provider returned an invalid structured response. No SQL was executed; please retry.") from None
