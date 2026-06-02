"""Validate enrichment classifications against categories.md."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from xerago_intelligence.classification.taxonomy import (
    CategoryTaxonomy,
    get_default_taxonomy,
    get_taxonomy,
)


class MatchLevel(str, Enum):
    EXACT = "exact"
    PARTIAL = "partial"
    UNCERTAIN = "uncertain"
    INVALID = "invalid"


@dataclass(frozen=True)
class FieldValidation:
    field: str
    value: str
    level: MatchLevel
    detail: str


@dataclass(frozen=True)
class ClassificationValidation:
    domain: FieldValidation
    signal_type: FieldValidation

    @property
    def is_valid(self) -> bool:
        return (
            self.domain.level != MatchLevel.INVALID
            and self.signal_type.level != MatchLevel.INVALID
        )


class ClassificationValidator:
    """Verify domain and signal_type against the official taxonomy."""

    def __init__(self, taxonomy: CategoryTaxonomy | None = None) -> None:
        self._taxonomy = taxonomy or get_default_taxonomy()

    @classmethod
    def from_categories_file(cls, path: Path) -> ClassificationValidator:
        return cls(get_taxonomy(str(path.resolve())))

    def validate(self, domain: str, signal_type: str) -> ClassificationValidation:
        domain_result = self._validate_domain(domain)
        signal_result = self._validate_signal_type(signal_type)
        return ClassificationValidation(
            domain=domain_result,
            signal_type=signal_result,
        )

    def _validate_domain(self, raw: str) -> FieldValidation:
        value = _normalize_slug(raw)
        if not value:
            return FieldValidation(
                field="domain",
                value=raw,
                level=MatchLevel.INVALID,
                detail="domain is empty",
            )

        if value in self._taxonomy.domains:
            return FieldValidation(
                field="domain",
                value=value,
                level=MatchLevel.EXACT,
                detail=f"domain '{value}' is in categories.md taxonomy",
            )

        hyphenated = value.replace("_", "-")
        if hyphenated in self._taxonomy.domains:
            return FieldValidation(
                field="domain",
                value=hyphenated,
                level=MatchLevel.PARTIAL,
                detail=f"domain normalized from '{raw}' to '{hyphenated}'",
            )

        candidates = _near_matches(hyphenated, self._taxonomy.domains)
        if candidates:
            return FieldValidation(
                field="domain",
                value=value,
                level=MatchLevel.UNCERTAIN,
                detail=f"domain not in taxonomy; similar: {', '.join(candidates)}",
            )

        return FieldValidation(
            field="domain",
            value=value,
            level=MatchLevel.INVALID,
            detail=f"domain '{value}' not found in categories.md taxonomy",
        )

    def _validate_signal_type(self, raw: str) -> FieldValidation:
        value = _normalize_slug(raw)
        if not value:
            return FieldValidation(
                field="signal_type",
                value=raw,
                level=MatchLevel.INVALID,
                detail="signal_type is empty",
            )

        if "/" in value:
            l1_part, l2_part = value.split("/", 1)
            l1_part = l1_part.strip()
            l2_part = l2_part.strip()
            if l1_part in self._taxonomy.signal_l1 and l2_part in self._taxonomy.l1_to_l2.get(
                l1_part, frozenset()
            ):
                return FieldValidation(
                    field="signal_type",
                    value=value,
                    level=MatchLevel.EXACT,
                    detail=f"L1/L2 '{l1_part}/{l2_part}' is in categories.md taxonomy",
                )
            if l1_part in self._taxonomy.signal_l1:
                return FieldValidation(
                    field="signal_type",
                    value=value,
                    level=MatchLevel.PARTIAL,
                    detail=f"L1 '{l1_part}' valid but L2 '{l2_part}' is not in taxonomy",
                )
            return FieldValidation(
                field="signal_type",
                value=value,
                level=MatchLevel.INVALID,
                detail=f"signal_type '{value}' not in categories.md taxonomy",
            )

        if value in self._taxonomy.signal_l1:
            return FieldValidation(
                field="signal_type",
                value=value,
                level=MatchLevel.EXACT,
                detail=f"signal L1 '{value}' is in categories.md taxonomy",
            )

        if value in self._taxonomy.signal_l2:
            parents = [
                l1
                for l1, l2_set in self._taxonomy.l1_to_l2.items()
                if value in l2_set
            ]
            return FieldValidation(
                field="signal_type",
                value=value,
                level=MatchLevel.PARTIAL,
                detail=(
                    f"signal L2 '{value}' is valid (L1 options: {', '.join(parents)})"
                ),
            )

        hyphenated = value.replace("_", "-")
        if hyphenated in self._taxonomy.signal_l1:
            return FieldValidation(
                field="signal_type",
                value=hyphenated,
                level=MatchLevel.PARTIAL,
                detail=f"signal_type normalized from '{raw}' to L1 '{hyphenated}'",
            )

        all_signals = self._taxonomy.all_signal_slugs()
        candidates = _near_matches(hyphenated, all_signals)
        if candidates:
            return FieldValidation(
                field="signal_type",
                value=value,
                level=MatchLevel.UNCERTAIN,
                detail=f"signal_type not in taxonomy; similar: {', '.join(candidates)}",
            )

        return FieldValidation(
            field="signal_type",
            value=value,
            level=MatchLevel.INVALID,
            detail=f"signal_type '{value}' not found in categories.md taxonomy",
        )


def _normalize_slug(value: str) -> str:
    return value.strip().lower()


def _near_matches(value: str, options: frozenset[str], *, max_distance: int = 2) -> list[str]:
    matches: list[str] = []
    for option in options:
        if abs(len(option) - len(value)) > max_distance:
            continue
        if _levenshtein(value, option) <= max_distance:
            matches.append(option)
    return sorted(matches)[:3]


def _levenshtein(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, start=1):
        current = [i]
        for j, char_right in enumerate(right, start=1):
            cost = 0 if char_left == char_right else 1
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + cost,
                )
            )
        previous = current
    return previous[-1]
