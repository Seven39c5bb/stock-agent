from __future__ import annotations

import time
from typing import Any
from typing import Optional

import requests


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float,
        timeout: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def _extract_response_text(self, data: dict[str, Any]) -> Optional[str]:
        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        output = data.get("output")
        if isinstance(output, list):
            chunks: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") in {"output_text", "text"}:
                        text = part.get("text")
                        if isinstance(text, str) and text.strip():
                            chunks.append(text.strip())
            if chunks:
                return "\n".join(chunks)

        return None

    def chat(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not self.is_enabled():
            return None

        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, requests.RequestException):
            return None

    def chat_with_web_search(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not self.is_enabled():
            return None

        print(f"DEBUG: Using model {self.model} with REAL WEB SEARCH tool...")
        url = f"{self.base_url}/v1/responses"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
            "tools": [{"type": "web_search_preview"}],
            "temperature": self.temperature,
        }

        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=(15, self.timeout))
                response.raise_for_status()
                return self._extract_response_text(response.json())
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.2 * (attempt + 1))
                    continue
                raise RuntimeError(f"web_search 请求失败: {exc}") from exc

        if last_error is not None:
            raise RuntimeError(f"web_search 请求失败: {last_error}") from last_error
        return None
