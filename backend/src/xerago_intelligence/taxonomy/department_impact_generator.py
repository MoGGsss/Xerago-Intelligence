"""Rule-based Department Impact Engine generator (no LLM)."""

from __future__ import annotations

import re

from xerago_intelligence.taxonomy.departments import department_slug
from xerago_intelligence.taxonomy.impact_rules import (
    CATEGORY_KEYWORD_RULES,
    DEPARTMENT_CATEGORY_BIAS,
    DEPARTMENT_IMPACT_PROFILES,
    DEPARTMENT_IMPACT_VERSION,
    DEPARTMENT_OPPORTUNITY_BIAS,
    DOMAIN_CATEGORY_DEFAULTS,
    DOMAIN_OPPORTUNITY_DEFAULTS,
    GLOBAL_FALLBACK_CATEGORY,
    GLOBAL_FALLBACK_OPPORTUNITY,
    GLOBAL_FALLBACK_PROFILE,
    MAX_IMPACT_SUMMARY_LENGTH,
    OPPORTUNITY_TYPE_SCORE_WEIGHT,
    SIGNAL_CATEGORY_DEFAULTS,
    SIGNAL_OPPORTUNITY_DEFAULTS,
    SUMMARY_VERB_VARIANTS,
    DepartmentImpactProfile,
)
from xerago_intelligence.taxonomy.impact_slots import (
    extract_capability,
    extract_content_type,
    extract_deliverable,
    extract_product,
    extract_topic,
)
from xerago_intelligence.types.impact import DepartmentImpactInput, DepartmentImpactResult


class DepartmentImpactGenerator:
    """Produce deterministic impact fields for one department mapping row."""

    def generate(self, inputs: DepartmentImpactInput) -> DepartmentImpactResult:
        domain = inputs.domain.strip().lower()
        signal = _normalize_signal(inputs.signal_type)
        dept_slug = department_slug(inputs.department_name) or "strategy-design"
        profile = DEPARTMENT_IMPACT_PROFILES.get(dept_slug, GLOBAL_FALLBACK_PROFILE)
        text = _text_blob(inputs.title, inputs.summary, inputs.why_it_matters)

        category, category_rule = _resolve_category(domain, signal, dept_slug, profile, text)
        opportunity, opportunity_rule = _resolve_opportunity(domain, signal, dept_slug, profile)
        template_id, summary = _resolve_summary(
            inputs=inputs,
            profile=profile,
            signal=signal,
            dept_slug=dept_slug,
            variant_index=_variant_index(inputs.department_name),
        )
        opportunity_score = _compute_opportunity_score(
            relevance=inputs.department_relevance_score,
            opportunity_type=opportunity,
            category_rule=category_rule,
            opportunity_rule=opportunity_rule,
        )
        reason = _build_impact_reason(
            category_rule=category_rule,
            opportunity_rule=opportunity_rule,
            template_id=template_id,
            relevance=inputs.department_relevance_score,
            opportunity_score=opportunity_score,
        )

        return DepartmentImpactResult(
            impact_summary=summary,
            impact_category=category,
            opportunity_type=opportunity,
            department_opportunity_score=opportunity_score,
            impact_reason=reason,
            impact_version=DEPARTMENT_IMPACT_VERSION,
        )


def _normalize_signal(signal_type: str) -> str:
    normalized = signal_type.strip().lower()
    if "/" in normalized:
        return normalized.split("/", 1)[0]
    return normalized


def _text_blob(title: str, summary: str, why_it_matters: str) -> str:
    return " ".join([title, summary, why_it_matters]).lower()


def _variant_index(department_name: str) -> int:
    return sum(ord(char) for char in department_name) % 4


def _resolve_category(
    domain: str,
    signal: str,
    dept_slug: str,
    profile: DepartmentImpactProfile,
    text: str,
) -> tuple[str, str]:
    candidates: list[tuple[int, str, str]] = []

    for keywords, category, rule_id in CATEGORY_KEYWORD_RULES:
        if any(keyword in text for keyword in keywords):
            candidates.append((100, category, rule_id))

    if domain in DOMAIN_CATEGORY_DEFAULTS:
        category, rule_id = DOMAIN_CATEGORY_DEFAULTS[domain]
        candidates.append((60, category, rule_id))

    if signal in SIGNAL_CATEGORY_DEFAULTS:
        category, rule_id = SIGNAL_CATEGORY_DEFAULTS[signal]
        candidates.append((70, category, rule_id))

    if dept_slug in DEPARTMENT_CATEGORY_BIAS:
        category, rule_id = DEPARTMENT_CATEGORY_BIAS[dept_slug]
        candidates.append((80, category, rule_id))

    for sig, category in profile.category_by_signal:
        if sig == signal and category:
            candidates.append((105, category, f"CAT-PROFILE-{dept_slug.upper()}-{sig}"))

    candidates.append((50, profile.default_category, f"CAT-PROFILE-DEFAULT-{dept_slug}"))

    if not candidates:
        return GLOBAL_FALLBACK_CATEGORY, "CAT-FALLBACK"

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def _resolve_opportunity(
    domain: str,
    signal: str,
    dept_slug: str,
    profile: DepartmentImpactProfile,
) -> tuple[str, str]:
    candidates: list[tuple[int, str, str]] = []

    if signal in SIGNAL_OPPORTUNITY_DEFAULTS:
        opportunity, rule_id = SIGNAL_OPPORTUNITY_DEFAULTS[signal]
        candidates.append((70, opportunity, rule_id))

    if domain in DOMAIN_OPPORTUNITY_DEFAULTS:
        opportunity, rule_id = DOMAIN_OPPORTUNITY_DEFAULTS[domain]
        candidates.append((60, opportunity, rule_id))

    if dept_slug in DEPARTMENT_OPPORTUNITY_BIAS:
        opportunity, rule_id = DEPARTMENT_OPPORTUNITY_BIAS[dept_slug]
        candidates.append((80, opportunity, rule_id))

    for sig, opportunity in profile.opportunity_by_signal:
        if sig == signal:
            candidates.append((85, opportunity, f"OPP-PROFILE-{dept_slug.upper()}-{sig}"))

    candidates.append((50, profile.default_opportunity, f"OPP-PROFILE-DEFAULT-{dept_slug}"))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def _resolve_summary(
    *,
    inputs: DepartmentImpactInput,
    profile: DepartmentImpactProfile,
    signal: str,
    dept_slug: str,
    variant_index: int,
) -> tuple[str, str]:
    template = profile.summary_default
    template_id = f"TPL-{dept_slug.upper()}-DEFAULT"

    for sig, summary_template in profile.summary_by_signal:
        if sig == signal:
            template = summary_template
            template_id = f"TPL-{dept_slug.upper()}-{sig.upper()}"
            break

    apply_variant = template_id.endswith("-DEFAULT")
    rendered = _render_template(
        template,
        title=inputs.title,
        summary=inputs.summary,
        why_it_matters=inputs.why_it_matters,
        variant_index=variant_index,
        apply_variant=apply_variant,
    )
    return template_id, _finalize_summary(rendered)


def _render_template(
    template: str,
    *,
    title: str,
    summary: str,
    why_it_matters: str,
    variant_index: int,
    apply_variant: bool,
) -> str:
    if "{" not in template:
        rendered = template
    else:
        mapping = {
            "capability": extract_capability(title, summary, why_it_matters),
            "content_type": extract_content_type(title, summary, why_it_matters),
            "deliverable": extract_deliverable(title, summary, why_it_matters),
            "product": extract_product(title, summary, why_it_matters),
            "topic": extract_topic(title, summary, why_it_matters),
        }
        rendered = template.format(**mapping)

    if apply_variant:
        return _apply_verb_variant(rendered, variant_index)
    return rendered


def _apply_verb_variant(text: str, variant_index: int) -> str:
    for base, variants in SUMMARY_VERB_VARIANTS.items():
        if text.startswith(base):
            replacement = variants[variant_index % len(variants)]
            return replacement + text[len(base) :]
    return text


def _finalize_summary(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        cleaned = "Monitor developments for departmental readiness."
    if cleaned[-1] not in ".!?":
        cleaned = f"{cleaned}."
    if cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    if len(cleaned) > MAX_IMPACT_SUMMARY_LENGTH:
        trimmed = cleaned[: MAX_IMPACT_SUMMARY_LENGTH - 1].rstrip()
        if " " in trimmed:
            trimmed = trimmed.rsplit(" ", 1)[0]
        cleaned = f"{trimmed}."
    return cleaned


def _compute_opportunity_score(
    *,
    relevance: int,
    opportunity_type: str,
    category_rule: str,
    opportunity_rule: str,
) -> int:
    type_weight = OPPORTUNITY_TYPE_SCORE_WEIGHT.get(opportunity_type, 8)
    rule_boost = 0
    if category_rule.startswith("CAT-KW"):
        rule_boost += 4
    if opportunity_rule.startswith("OPP-DEPT"):
        rule_boost += 3
    raw = int(round(relevance * 0.88 + type_weight + rule_boost))
    return max(0, min(100, raw))


def _build_impact_reason(
    *,
    category_rule: str,
    opportunity_rule: str,
    template_id: str,
    relevance: int,
    opportunity_score: int,
) -> str:
    return (
        f"category={category_rule}|opportunity={opportunity_rule}|"
        f"template={template_id}|relevance={relevance}|opp_score={opportunity_score}"
    )
