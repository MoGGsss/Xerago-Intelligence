"""Ollama provider — POST /api/generate."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from xerago_intelligence.ai.client import AIClient, GenerateResult
from xerago_intelligence.config.settings import Settings

logger = logging.getLogger(__name__)


class OllamaClient(AIClient):
    """Calls a local or remote Ollama instance."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._timeout = settings.ollama_timeout_seconds
        self._session = requests.Session()

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str, *, json_mode: bool = False) -> GenerateResult:
        """
        Run Ollama /api/generate.

        ``json_mode`` is ignored — gpt-oss and similar models do not reliably
        support ``format: json``; enrichment uses prompt + parser instead.
        """
        if json_mode:
            logger.warning(
                "OllamaClient ignores json_mode=True; use prompt + JSON parser"
            )

        url = f"{self._base_url}/api/generate"
        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }

        logger.debug(
            "Ollama generate start — model=%s url=%s prompt_chars=%s",
            self._model,
            url,
            len(prompt),
        )

        started = time.perf_counter()
        response = self._session.post(
            url,
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        http_ms = (time.perf_counter() - started) * 1000
        data = response.json()
        if not isinstance(data, dict):
            raise OllamaResponseError(
                "Ollama response body is not a JSON object",
                raw=data,
            )

        text, source_field = _extract_generate_text(data)
        model = str(data.get("model") or self._model)
        total_duration_ns = data.get("total_duration")

        logger.info(
            "Ollama generate complete — model=%s response_len=%s source_field=%s "
            "http_ms=%.1f total_duration_ns=%s",
            model,
            len(text),
            source_field,
            http_ms,
            total_duration_ns,
        )
        logger.debug(
            "Ollama raw response JSON: %s",
            json.dumps(data, ensure_ascii=False, default=str),
        )
        logger.debug("Ollama mapped text: %s", text)

        if not text:
            raise OllamaResponseError(
                "Ollama response contained no extractable text "
                f"(checked: response, message.content, text, content, thinking); "
                f"keys present: {sorted(data.keys())}",
                raw=data,
            )

        return GenerateResult(
            text=text,
            model=model,
            provider=self.provider_name,
        )


def _extract_generate_text(data: dict[str, Any]) -> tuple[str, str]:
    """
    Map Ollama /api/generate JSON to completion text.

    Official field for non-streaming generate: ``response`` (final answer).
    Chat-style proxies may use ``message.content``. ``thinking`` is a last resort
    when ``response`` is empty (reasoning-only models).
    """
    candidates: list[tuple[str, Any]] = [
        ("response", data.get("response")),
    ]

    message = data.get("message")
    if isinstance(message, dict):
        candidates.append(("message.content", message.get("content")))

    candidates.extend(
        [
            ("text", data.get("text")),
            ("content", data.get("content")),
            ("thinking", data.get("thinking")),
        ]
    )

    for field, value in candidates:
        if isinstance(value, str) and value.strip():
            if field == "thinking":
                logger.warning(
                    "Ollama 'response' empty — using 'thinking' field for mapped text"
                )
            return value.strip(), field

    # Preserve which field was present but empty (for diagnostics)
    for field, value in candidates:
        if isinstance(value, str):
            return value.strip(), field

    return "", "none"


class OllamaResponseError(Exception):
    def __init__(self, message: str, *, raw: object) -> None:
        super().__init__(message)
        self.raw = raw
