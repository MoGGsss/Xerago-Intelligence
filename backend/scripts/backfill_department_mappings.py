#!/usr/bin/env python3
"""Backfill department mappings for enriched artifacts."""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, get_session_factory
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.db.repositories.department_mapping_repository import (
    DepartmentMappingRepository,
)
from xerago_intelligence.mapping.department_service import DepartmentMappingService
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackfillSummary:
    total: int
    mapped: int
    skipped: int
    failed: int
    elapsed_time: str


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _artifact_ids_needing_mapping(session_factory) -> list[str]:
    from xerago_intelligence.db.models.artifact_department_mapping import (
        ArtifactDepartmentMapping,
    )

    with session_factory() as session:
        repo = DepartmentMappingRepository(session)
        if (
            repo.count_unmapped_enriched() == 0
            and repo.count_stale(DEPARTMENT_MAPPING_VERSION) == 0
        ):
            return []

        mapped_ids = set(
            session.scalars(
                select(ArtifactDepartmentMapping.artifact_id).distinct()
            ).all()
        )
        enriched_ids = list(
            session.scalars(
                select(ArtifactEnrichment.artifact_id).order_by(
                    ArtifactEnrichment.enriched_at.asc()
                )
            ).all()
        )

        if not mapped_ids:
            return enriched_ids

        stale_ids = set(
            session.scalars(
                select(ArtifactDepartmentMapping.artifact_id)
                .where(
                    ArtifactDepartmentMapping.mapping_version
                    != DEPARTMENT_MAPPING_VERSION
                )
                .distinct()
            ).all()
        )
        unmapped_ids = [aid for aid in enriched_ids if aid not in mapped_ids]
        target_ids = sorted(set(unmapped_ids) | stale_ids, key=enriched_ids.index)
        return target_ids


def _format_elapsed(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def run_backfill(*, force: bool = False) -> BackfillSummary:
    _configure_logging()
    session_factory = get_session_factory()

    with session_factory() as session:
        repo = DepartmentMappingRepository(session)
        print(
            f"Unmapped enriched artifacts: {repo.count_unmapped_enriched()}",
            flush=True,
        )
        print(
            f"Stale mapping version rows: {repo.count_stale(DEPARTMENT_MAPPING_VERSION)}",
            flush=True,
        )

    artifact_ids = _artifact_ids_needing_mapping(session_factory)
    if force:
        with session_factory() as session:
            artifact_ids = list(
                session.scalars(
                    select(ArtifactEnrichment.artifact_id).order_by(
                        ArtifactEnrichment.enriched_at.asc()
                    )
                ).all()
            )

    total = len(artifact_ids)
    mapped = 0
    skipped = 0
    failed = 0
    started = time.perf_counter()

    print(
        f"Backfill department mappings ({DEPARTMENT_MAPPING_VERSION}) — {total} artifacts",
        flush=True,
    )

    for index, artifact_id in enumerate(artifact_ids, start=1):
        try:
            with session_factory() as session:
                service = DepartmentMappingService(session)
                result = service.map_artifact(artifact_id, force=force)
                if result is None:
                    skipped += 1
                else:
                    mapped += 1
                session.commit()
        except Exception:
            failed += 1
            logger.exception("Failed mapping artifact_id=%s", artifact_id)

        if index % 50 == 0 or index == total:
            print(f"Progress: {index}/{total}", flush=True)

    elapsed = _format_elapsed(time.perf_counter() - started)
    summary = BackfillSummary(
        total=total,
        mapped=mapped,
        skipped=skipped,
        failed=failed,
        elapsed_time=elapsed,
    )
    print(
        f"Done — mapped={summary.mapped} skipped={summary.skipped} "
        f"failed={summary.failed} elapsed={summary.elapsed_time}",
        flush=True,
    )
    return summary


def main() -> int:
    force = "--force" in sys.argv
    try:
        run_backfill(force=force)
    finally:
        dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
