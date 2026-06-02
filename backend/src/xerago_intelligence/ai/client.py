"""AI provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from xerago_intelligence.config.settings import Settings, get_settings


@dataclass(frozen=True)
class GenerateResult:
    """Normalized LLM generate response."""

    text: str
    model: str
    provider: str


class AIClient(ABC):
    """Provider-agnostic text generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @abstractmethod
    def generate(self, prompt: str, *, json_mode: bool = False) -> GenerateResult:
        """Run a completion and return the primary text output."""


def create_ai_client(settings: Settings | None = None) -> AIClient:
    """Factory for the configured AI provider."""
    cfg = settings or get_settings()
    provider = (cfg.llm_provider or "ollama").strip().lower()
    if provider == "ollama":
        from xerago_intelligence.ai.providers.ollama import OllamaClient

        return OllamaClient(cfg)
    raise ValueError(f"Unsupported LLM provider: {provider!r}")
