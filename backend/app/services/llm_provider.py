import json
from typing import Iterator

import requests


class ProviderError(RuntimeError):
    """Raised when the configured model provider cannot complete a request."""


class OpenAICompatibleProvider:
    """Streaming chat adapter for OpenAI-compatible /v1/chat/completions APIs."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 120,
                 max_output_tokens: int = 1200, temperature: float = 0.4):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

    @property
    def is_configured(self) -> bool:
        # Local HTTP inference servers (for example Ollama) may not require a key.
        # Hosted HTTPS providers normally do. An explicit API key is accepted for either.
        local_http = self.base_url.startswith("http://")
        return bool(self.base_url and self.model and (self.api_key or local_http))

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        if not self.is_configured:
            raise ProviderError("AI provider is not configured. Set LLM_MODEL and provider settings.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_output_tokens,
        }

        try:
            with requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=(10, self.timeout),
            ) as response:
                if not response.ok:
                    raise ProviderError(
                        f"Model provider returned HTTP {response.status_code}. Check the model name, API key, and provider quota."
                    )

                for raw_line in response.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    if isinstance(raw_line, bytes):
                        raw_line = raw_line.decode("utf-8", errors="replace")
                    line = raw_line.strip()
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    if line == "[DONE]":
                        break
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    choices = event.get("choices") or []
                    if not choices:
                        continue
                    delta = (choices[0].get("delta") or {}).get("content")
                    if isinstance(delta, str) and delta:
                        yield delta
                    elif isinstance(delta, list):
                        for part in delta:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text = part.get("text")
                                if text:
                                    yield text
        except requests.Timeout as exc:
            raise ProviderError("The AI provider timed out. Please try again.") from exc
        except requests.RequestException as exc:
            raise ProviderError("Could not connect to the AI provider. Check provider settings.") from exc


class AnthropicMessagesProvider:
    """Native Anthropic Messages API adapter with text-delta streaming."""

    def __init__(self, base_url: str, api_key: str, model: str, api_version: str,
                 timeout: int = 120, max_output_tokens: int = 1200, temperature: float = 0.4):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.api_version = api_version.strip()
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model and self.api_version)

    def stream_chat(self, messages: list[dict]) -> Iterator[str]:
        if not self.is_configured:
            raise ProviderError("Anthropic provider requires LLM_MODEL, LLM_API_KEY, and ANTHROPIC_VERSION.")

        system_parts = [item["content"] for item in messages if item.get("role") == "system"]
        chat_messages = [
            {"role": item["role"], "content": item["content"]}
            for item in messages if item.get("role") in {"user", "assistant"}
        ]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": self.api_version,
        }
        payload = {
            "model": self.model,
            "max_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "system": "\n\n".join(system_parts),
            "messages": chat_messages,
            "stream": True,
        }
        try:
            with requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                stream=True,
                timeout=(10, self.timeout),
            ) as response:
                if not response.ok:
                    raise ProviderError(
                        f"Anthropic returned HTTP {response.status_code}. Check model name, API key, and account quota."
                    )
                for raw_line in response.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    if isinstance(raw_line, bytes):
                        raw_line = raw_line.decode("utf-8", errors="replace")
                    line = raw_line.strip()
                    if not line.startswith("data:"):
                        continue
                    try:
                        event = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") != "content_block_delta":
                        continue
                    delta = event.get("delta") or {}
                    if delta.get("type") == "text_delta" and delta.get("text"):
                        yield delta["text"]
        except requests.Timeout as exc:
            raise ProviderError("Anthropic request timed out. Please try again.") from exc
        except requests.RequestException as exc:
            raise ProviderError("Could not connect to Anthropic. Check provider settings.") from exc
