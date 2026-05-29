"""Load and validate registry YAML files from the repository."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from xerago_intelligence.config import Settings, get_settings
from xerago_intelligence.registry.models import RegistryBundle, ReposRegistry, SourcesRegistry


class RegistryError(Exception):
    """Raised when registry files cannot be loaded or validated."""


def load_sources_registry(
    *,
    path: Path | None = None,
    settings: Settings | None = None,
) -> SourcesRegistry:
    """Load and validate registry/sources.yaml."""
    settings = settings or get_settings()
    file_path = path or settings.sources_yaml_path
    data = _read_yaml(file_path)
    try:
        return SourcesRegistry.model_validate(data)
    except ValidationError as exc:
        raise RegistryError(f"Invalid sources registry: {file_path}") from exc


def load_repos_registry(
    *,
    path: Path | None = None,
    settings: Settings | None = None,
) -> ReposRegistry:
    """Load and validate registry/repos.yaml."""
    settings = settings or get_settings()
    file_path = path or settings.repos_yaml_path
    data = _read_yaml(file_path)
    try:
        return ReposRegistry.model_validate(data)
    except ValidationError as exc:
        raise RegistryError(f"Invalid repos registry: {file_path}") from exc


def load_registry(
    *,
    settings: Settings | None = None,
) -> RegistryBundle:
    """Load both sources and repos registries."""
    settings = settings or get_settings()
    root = settings.resolve_project_root()
    sources = load_sources_registry(settings=settings)
    repos = load_repos_registry(settings=settings)
    return RegistryBundle(
        project_root=str(root),
        sources=sources,
        repos=repos,
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RegistryError(f"Registry file not found: {path}")
    try:
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise RegistryError(f"YAML parse error: {path}") from exc
    if not isinstance(raw, dict):
        raise RegistryError(f"Expected mapping at root of {path}")
    return raw
