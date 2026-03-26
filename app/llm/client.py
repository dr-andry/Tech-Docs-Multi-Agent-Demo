# app/llm/client.py

import asyncio
import requests
from app.config import GEMMA_BASE_URL, MODEL_NAME, TEMPERATURE, TIMEOUT


class GemmaClient:
    def __init__(self):
        self.base_url = GEMMA_BASE_URL

    async def chat(self, messages, tools=None):
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": TEMPERATURE,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=TIMEOUT
        ))
        response.raise_for_status()

        return response.json()["choices"][0]["message"]