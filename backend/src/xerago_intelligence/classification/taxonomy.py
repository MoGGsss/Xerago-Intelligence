"""Load domain and signal taxonomies from docs/categories.md."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

_DOMAIN_REGISTRY_START = "### Domain Registry"
_DOMAIN_REGISTRY_END = "### Domain Mapping Rules"
_PART2_START = "## Part 2: Signal Event Type Taxonomy"
_PART2_END = "## Cross-Reference:"

_L1_HEADER_RE = re.compile(r"^### L1: `([^`]+)`\s*$")
_SLUG_CELL_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|", re.MULTILINE)


@dataclass(frozen=True)
class CategoryTaxonomy:
    """Parsed taxonomy from categories.md."""

    domains: frozenset[str]
    signal_l1: frozenset[str]
    signal_l2: frozenset[str]
    l1_to_l2: dict[str, frozenset[str]] = field(default_factory=dict)

    def all_signal_slugs(self) -> frozenset[str]:
        return self.signal_l1 | self.signal_l2


def load_taxonomy(categories_path: Path) -> CategoryTaxonomy:
    text = categories_path.read_text(encoding="utf-8")
    domains = _parse_domains(text)
    signal_l1, signal_l2, l1_to_l2 = _parse_signal_types(text)
    return CategoryTaxonomy(
        domains=frozenset(domains),
        signal_l1=frozenset(signal_l1),
        signal_l2=frozenset(signal_l2),
        l1_to_l2={key: frozenset(value) for key, value in l1_to_l2.items()},
    )


def _parse_domains(text: str) -> set[str]:
    start = text.find(_DOMAIN_REGISTRY_START)
    end = text.find(_DOMAIN_REGISTRY_END, start)
    if start < 0 or end < 0:
        raise ValueError("Could not locate Domain Registry section in categories.md")
    section = text[start:end]
    return {match.group(1) for match in _SLUG_CELL_RE.finditer(section)}


def _parse_signal_types(text: str) -> tuple[set[str], set[str], dict[str, set[str]]]:
    start = text.find(_PART2_START)
    end = text.find(_PART2_END, start)
    if start < 0 or end < 0:
        raise ValueError("Could not locate Signal Event Type section in categories.md")

    signal_l1: set[str] = set()
    signal_l2: set[str] = set()
    l1_to_l2: dict[str, set[str]] = {}
    current_l1: str | None = None

    for line in text[start:end].splitlines():
        l1_match = _L1_HEADER_RE.match(line)
        if l1_match:
            current_l1 = l1_match.group(1).strip()
            signal_l1.add(current_l1)
            l1_to_l2.setdefault(current_l1, set())
            continue

        slug_match = _SLUG_CELL_RE.match(line)
        if slug_match and current_l1 and "L2 Slug" not in line:
            slug = slug_match.group(1).strip()
            signal_l2.add(slug)
            l1_to_l2[current_l1].add(slug)

    return signal_l1, signal_l2, l1_to_l2


@lru_cache(maxsize=4)
def get_taxonomy(categories_path: str) -> CategoryTaxonomy:
    return load_taxonomy(Path(categories_path))


def get_default_taxonomy() -> CategoryTaxonomy:
    from xerago_intelligence.config import get_settings

    path = get_settings().resolve_project_root() / "docs" / "categories.md"
    return get_taxonomy(str(path.resolve()))
