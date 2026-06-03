#!/usr/bin/env python3
"""Read-only pipeline status report for Xerago Intelligence Engine."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, or_, select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, session_scope
from xerago_intelligence.db.connection import probe_connection
from xerago_intelligence.db.models.artifact import Artifact
from xerago_intelligence.db.models.artifact_department_mapping import (
    ArtifactDepartmentMapping,
)
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.department_mapping_repository import (
    DepartmentMappingRepository,
)


@dataclass(frozen=True)
class PipelineStatus:
    artifacts: int
    enrichments: int
    scored: int
    mappings: int
    impacts: int
    pending_enrichments: int
    pending_scores: int
    pending_mappings: int
    pending_impacts: int


def collect_pipeline_status() -> PipelineStatus:
    with session_scope() as session:
        artifacts = int(session.scalar(select(func.count()).select_from(Artifact)) or 0)
        enrichments = int(
            session.scalar(select(func.count()).select_from(ArtifactEnrichment)) or 0
        )
        scored = int(
            session.scalar(
                select(func.count())
                .select_from(ArtifactEnrichment)
                .where(ArtifactEnrichment.strategic_score.is_not(None))
            )
            or 0
        )
        mappings = int(
            session.scalar(select(func.count()).select_from(ArtifactDepartmentMapping))
            or 0
        )
        impacts = int(
            session.scalar(
                select(func.count())
                .select_from(ArtifactDepartmentMapping)
                .where(ArtifactDepartmentMapping.impact_summary.is_not(None))
                .where(ArtifactDepartmentMapping.impact_summary != "")
            )
            or 0
        )

        pending_enrichments = int(
            session.scalar(
                select(func.count())
                .select_from(Artifact)
                .outerjoin(
                    ArtifactEnrichment,
                    Artifact.artifact_id == ArtifactEnrichment.artifact_id,
                )
                .where(ArtifactEnrichment.artifact_id.is_(None))
            )
            or 0
        )
        pending_scores = int(
            session.scalar(
                select(func.count())
                .select_from(ArtifactEnrichment)
                .where(ArtifactEnrichment.strategic_score.is_(None))
            )
            or 0
        )

        mapping_repo = DepartmentMappingRepository(session)
        pending_mappings = mapping_repo.count_unmapped_enriched()
        pending_impacts = int(
            session.scalar(
                select(func.count())
                .select_from(ArtifactDepartmentMapping)
                .where(
                    or_(
                        ArtifactDepartmentMapping.impact_summary.is_(None),
                        ArtifactDepartmentMapping.impact_summary == "",
                    )
                )
            )
            or 0
        )

    return PipelineStatus(
        artifacts=artifacts,
        enrichments=enrichments,
        scored=scored,
        mappings=mappings,
        impacts=impacts,
        pending_enrichments=pending_enrichments,
        pending_scores=pending_scores,
        pending_mappings=pending_mappings,
        pending_impacts=pending_impacts,
    )


def print_pipeline_status(status: PipelineStatus) -> None:
    print("=" * 48)
    print("PIPELINE STATUS")
    print("=" * 15)
    print()
    print(f"Artifacts: {status.artifacts}")
    print(f"Enrichments: {status.enrichments}")
    print(f"Scored: {status.scored}")
    print(f"Mappings: {status.mappings}")
    print(f"Impacts: {status.impacts}")
    print()
    print(f"Pending Enrichments: {status.pending_enrichments}")
    print(f"Pending Scores: {status.pending_scores}")
    print(f"Pending Mappings: {status.pending_mappings}")
    print(f"Pending Impacts: {status.pending_impacts}")


def main() -> int:
    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    try:
        print_pipeline_status(collect_pipeline_status())
    finally:
        dispose_engine()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
