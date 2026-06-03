"""Department mapping orchestration."""

from __future__ import annotations

import logging
from typing import Literal

from sqlalchemy.orm import Session

from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_department_mapping import (
    ArtifactDepartmentMapping,
)
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.artifact_repository import ArtifactRepository
from xerago_intelligence.db.repositories.department_mapping_repository import (
    DepartmentMappingRepository,
)
from xerago_intelligence.db.repositories.enrichment_repository import EnrichmentRepository
from xerago_intelligence.taxonomy.department_impact_generator import (
    DepartmentImpactGenerator,
)
from xerago_intelligence.taxonomy.department_mapper import (
    DepartmentMapper,
    DepartmentMappingInput,
    DepartmentMappingRecord,
    DepartmentMappingResult,
    DepartmentScore,
    primary_department,
)
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION
from xerago_intelligence.taxonomy.impact_rules import DEPARTMENT_IMPACT_VERSION
from xerago_intelligence.types.impact import DepartmentImpactInput

logger = logging.getLogger(__name__)

BackfillImpactStatus = Literal["updated", "skipped", "no_enrichment", "no_mappings"]


class DepartmentMappingService:
    """Compute and persist department relevance and impact from stored enrichment."""

    def __init__(
        self,
        session: Session,
        *,
        mapper: DepartmentMapper | None = None,
        impact_generator: DepartmentImpactGenerator | None = None,
    ) -> None:
        self._session = session
        self._artifacts = ArtifactRepository(session)
        self._enrichments = EnrichmentRepository(session)
        self._mappings = DepartmentMappingRepository(session)
        self._mapper = mapper or DepartmentMapper()
        self._impact_generator = impact_generator or DepartmentImpactGenerator()

    def map_artifact(
        self,
        artifact_id: str,
        *,
        force: bool = False,
    ) -> DepartmentMappingResult | None:
        enrichment = self._enrichments.get_by_artifact_id(artifact_id)
        if enrichment is None:
            return None

        artifact = self._artifacts.get_by_id(artifact_id)

        if not force:
            existing = self._mappings.get_by_artifact_id(artifact_id)
            if existing:
                mapping_current = (
                    existing[0].mapping_version == DEPARTMENT_MAPPING_VERSION
                )
                impact_current = _impacts_are_current(existing)
                if mapping_current and impact_current:
                    return self._to_result(existing)
                if mapping_current and not impact_current:
                    records, generated_impacts = self._records_with_impacts(
                        self._build_mapping_input(enrichment, artifact),
                        tuple(
                            DepartmentScore(
                                department_name=row.department_name,
                                department_relevance_score=row.department_relevance_score,
                            )
                            for row in existing
                        ),
                    )
                    self._mappings.update_impacts(artifact_id, records)
                    self._log_mapping(
                        artifact_id=artifact_id,
                        mapped_departments=[r.department_name for r in records],
                        generated_impacts=generated_impacts,
                        primary=self._primary_from_records(records),
                        impact_only=True,
                    )
                    return self._to_result_from_records(records, existing[0].mapping_version)

        inputs = self._build_mapping_input(enrichment, artifact)
        result = self._mapper.compute(inputs)
        records, generated_impacts = self._records_with_impacts(
            inputs,
            result.departments,
        )
        self._mappings.replace_mappings(
            artifact_id,
            records,
            mapping_version=result.mapping_version,
        )
        self._log_mapping(
            artifact_id=artifact_id,
            mapped_departments=[r.department_name for r in records],
            generated_impacts=generated_impacts,
            primary=primary_department(result),
            impact_only=False,
        )
        return DepartmentMappingResult(
            departments=tuple(
                DepartmentScore(
                    department_name=record.department_name,
                    department_relevance_score=record.department_relevance_score,
                )
                for record in records
            ),
            mapping_version=result.mapping_version,
        )

    def backfill_impacts(
        self,
        artifact_id: str,
        *,
        force: bool = False,
    ) -> BackfillImpactStatus:
        """Impact-only update for existing department mapping rows."""
        enrichment = self._enrichments.get_by_artifact_id(artifact_id)
        if enrichment is None:
            return "no_enrichment"

        existing = self._mappings.get_by_artifact_id(artifact_id)
        if not existing:
            return "no_mappings"

        if not force and _impacts_are_current(existing):
            return "skipped"

        artifact = self._artifacts.get_by_id(artifact_id)
        records, generated_impacts = self._records_with_impacts(
            self._build_mapping_input(enrichment, artifact),
            tuple(
                DepartmentScore(
                    department_name=row.department_name,
                    department_relevance_score=row.department_relevance_score,
                )
                for row in existing
            ),
        )
        self._mappings.update_impacts(artifact_id, records)
        self._log_mapping(
            artifact_id=artifact_id,
            mapped_departments=[r.department_name for r in records],
            generated_impacts=generated_impacts,
            primary=self._primary_from_records(records),
            impact_only=True,
        )
        return "updated"

    def _records_with_impacts(
        self,
        inputs: DepartmentMappingInput,
        departments: tuple[DepartmentScore, ...],
    ) -> tuple[list[DepartmentMappingRecord], int]:
        records: list[DepartmentMappingRecord] = []
        generated_impacts = 0
        for score in departments:
            record, generated = self._record_with_impact(inputs, score)
            records.append(record)
            if generated:
                generated_impacts += 1
        return records, generated_impacts

    def _record_with_impact(
        self,
        inputs: DepartmentMappingInput,
        score: DepartmentScore,
    ) -> tuple[DepartmentMappingRecord, bool]:
        try:
            impact = self._impact_generator.generate(
                DepartmentImpactInput(
                    title=inputs.title,
                    summary=inputs.summary,
                    why_it_matters=inputs.why_it_matters,
                    domain=inputs.domain,
                    signal_type=inputs.signal_type,
                    department_name=score.department_name,
                    department_relevance_score=score.department_relevance_score,
                )
            )
        except Exception:
            logger.exception(
                "Impact generation failed artifact dept=%s",
                score.department_name,
            )
            return DepartmentMappingRecord.from_score(score), False

        return (
            DepartmentMappingRecord(
                department_name=score.department_name,
                department_relevance_score=score.department_relevance_score,
                impact_summary=impact.impact_summary,
                impact_category=impact.impact_category,
                opportunity_type=impact.opportunity_type,
                department_opportunity_score=impact.department_opportunity_score,
                impact_reason=impact.impact_reason,
                impact_version=impact.impact_version,
            ),
            True,
        )

    @staticmethod
    def _build_mapping_input(
        enrichment: ArtifactEnrichment,
        artifact: Artifact | None,
    ) -> DepartmentMappingInput:
        return DepartmentMappingInput(
            domain=enrichment.domain,
            signal_type=enrichment.signal_type,
            summary=enrichment.summary,
            why_it_matters=enrichment.why_it_matters,
            confidence_score=enrichment.confidence_score,
            title=artifact.title if artifact else "",
            source_id=artifact.source_id if artifact else "",
        )

    @staticmethod
    def _log_mapping(
        *,
        artifact_id: str,
        mapped_departments: list[str],
        generated_impacts: int,
        primary: str | None,
        impact_only: bool,
    ) -> None:
        logger.info(
            "Department mapping artifact_id=%s mapped_departments=%s "
            "generated_impacts=%s/%s primary=%s impact_only=%s",
            artifact_id,
            mapped_departments,
            generated_impacts,
            len(mapped_departments),
            primary,
            impact_only,
        )

    @staticmethod
    def _primary_from_records(records: list[DepartmentMappingRecord]) -> str | None:
        if not records:
            return None
        top = max(records, key=lambda row: row.department_relevance_score)
        return top.department_name

    @staticmethod
    def _to_result(rows: list[ArtifactDepartmentMapping]) -> DepartmentMappingResult:
        return DepartmentMappingService._to_result_from_records(
            [
                DepartmentMappingRecord(
                    department_name=row.department_name,
                    department_relevance_score=row.department_relevance_score,
                    impact_summary=row.impact_summary,
                    impact_category=row.impact_category,
                    opportunity_type=row.opportunity_type,
                    department_opportunity_score=row.department_opportunity_score,
                    impact_reason=row.impact_reason,
                    impact_version=row.impact_version,
                )
                for row in rows
            ],
            rows[0].mapping_version if rows else DEPARTMENT_MAPPING_VERSION,
        )

    @staticmethod
    def _to_result_from_records(
        records: list[DepartmentMappingRecord],
        mapping_version: str,
    ) -> DepartmentMappingResult:
        departments = tuple(
            DepartmentScore(
                department_name=record.department_name,
                department_relevance_score=record.department_relevance_score,
            )
            for record in records
        )
        return DepartmentMappingResult(
            departments=departments,
            mapping_version=mapping_version,
        )


def _impacts_are_current(rows: list[ArtifactDepartmentMapping]) -> bool:
    if not rows:
        return False
    return all(
        row.impact_version == DEPARTMENT_IMPACT_VERSION and row.impact_summary
        for row in rows
    )
