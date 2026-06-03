"""Negative keyword scoring for pre-enrichment filtering."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from xerago_intelligence.filtering.negative_keywords import (
    NEGATIVE_FILTER_RULE_ID,
    NEGATIVE_FILTER_VERSION,
    NEGATIVE_KEYWORDS,
    NEGATIVE_PHRASES,
    SALE_ALLOWLIST,
)

TITLE_KEYWORD_POINTS = 3
BODY_KEYWORD_POINTS = 1
TITLE_PHRASE_POINTS = 5
BODY_PHRASE_POINTS = 3

DEFAULT_SKIP_THRESHOLD = 5


@dataclass(frozen=True)
class NegativeFilterInput:
    title: str
    raw_content: str | None = None


@dataclass(frozen=True)
class NegativeFilterResult:
    negative_score: int
    skip_threshold: int
    should_skip: bool
    skip_reason: str | None
    matched_keywords: tuple[str, ...]
    matched_in_title: tuple[str, ...] = ()
    matched_in_body: tuple[str, ...] = ()
    filter_version: str = NEGATIVE_FILTER_VERSION
    rule_id: str = NEGATIVE_FILTER_RULE_ID


class NegativeScorer:
    """Compute negative intelligence score from artifact title and body."""

    def __init__(self, *, skip_threshold: int = DEFAULT_SKIP_THRESHOLD) -> None:
        self._skip_threshold = max(1, skip_threshold)
        self._keyword_patterns = {
            keyword: re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            for keyword in NEGATIVE_KEYWORDS
        }

    def evaluate(self, inputs: NegativeFilterInput) -> NegativeFilterResult:
        title = _normalize_text(inputs.title)
        body = _normalize_text(inputs.raw_content or "")
        blob = f"{title} {body}".strip()

        title_matches: set[str] = set()
        body_matches: set[str] = set()
        score = 0

        for phrase in NEGATIVE_PHRASES:
            normalized_phrase = _normalize_text(phrase)
            if normalized_phrase in title:
                title_matches.add(phrase)
                score += TITLE_PHRASE_POINTS
            elif normalized_phrase in body:
                body_matches.add(phrase)
                score += BODY_PHRASE_POINTS

        for keyword in NEGATIVE_KEYWORDS:
            if keyword == "sale" and _sale_allowlisted(blob):
                continue
            pattern = self._keyword_patterns[keyword]
            if pattern.search(title):
                title_matches.add(keyword)
                score += TITLE_KEYWORD_POINTS
            elif body and pattern.search(body):
                body_matches.add(keyword)
                score += BODY_KEYWORD_POINTS

        matched = tuple(sorted(title_matches | body_matches))
        should_skip = score >= self._skip_threshold
        skip_reason = None
        if should_skip:
            skip_reason = (
                f"{NEGATIVE_FILTER_RULE_ID}: negative_score={score} "
                f"threshold={self._skip_threshold} matched={list(matched)}"
            )

        return NegativeFilterResult(
            negative_score=score,
            skip_threshold=self._skip_threshold,
            should_skip=should_skip,
            skip_reason=skip_reason,
            matched_keywords=matched,
            matched_in_title=tuple(sorted(title_matches)),
            matched_in_body=tuple(sorted(body_matches)),
        )


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _sale_allowlisted(blob: str) -> bool:
    return any(token in blob for token in SALE_ALLOWLIST)
