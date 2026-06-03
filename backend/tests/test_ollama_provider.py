"""Tests for Ollama AI provider."""

from __future__ import annotations

import io
import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.ai.providers.ollama import OllamaClient  # noqa: E402
from xerago_intelligence.config.settings import Settings  # noqa: E402


@contextmanager
def _strict_cp1252_stdout():
    """Simulate Windows console stdout that rejects non-cp1252 characters."""
    buffer = io.BytesIO()
    wrapper = io.TextIOWrapper(buffer, encoding="cp1252", errors="strict")
    previous = sys.stdout
    sys.stdout = wrapper
    try:
        yield wrapper
    finally:
        sys.stdout = previous


def _build_client() -> OllamaClient:
    settings = Settings(
        ollama_base_url="http://ollama.test",
        ollama_model="gpt-oss:20b",
        ollama_timeout_seconds=30.0,
    )
    client = OllamaClient(settings)
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "model": "gpt-oss:20b",
        "response": '{"summary":"narrow\u202fspace"}',
        "thinking": "model trace with non\u2011breaking hyphen",
        "total_duration": 1_234_567_890,
        "done": True,
    }
    client._session.post = MagicMock(return_value=mock_response)
    return client


def test_generate_survives_unicode_on_strict_cp1252_stdout() -> None:
    client = _build_client()

    with _strict_cp1252_stdout():
        result = client.generate("classify this article")

    assert result.text == '{"summary":"narrow\u202fspace"}'
    assert result.model == "gpt-oss:20b"
    assert result.provider == "ollama"


def test_generate_does_not_log_full_response_at_info(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _build_client()

    with caplog.at_level(logging.INFO):
        with _strict_cp1252_stdout():
            client.generate("classify this article")

    info_messages = " ".join(record.getMessage() for record in caplog.records)
    assert "non\u2011breaking hyphen" not in info_messages
    assert "narrow\u202fspace" not in info_messages
    assert "Ollama generate complete" in info_messages
    assert "response_len=" in info_messages
    assert "source_field=response" in info_messages
    assert "total_duration_ns=1234567890" in info_messages
