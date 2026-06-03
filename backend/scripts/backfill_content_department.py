#!/usr/bin/env python3
"""Backfill department mappings after Content department enablement (v1.1.0)."""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, get_session_factory
from xerago_intelligence.db.connection import probe_connection
from xerago_intelligence.db.models.artifact_department_mapping import (
    ArtifactDepartmentMapping,
)
from xerago_intelligence.db.models.artifact_enrichment import ArtifactEnrichment
from xerago_intelligence.mapping.department_service import DepartmentMappingService
from xerago_intelligence.taxonomy.department_rules import DEPARTMENT_MAPPING_VERSION

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MappingSnapshot:
    total_rows: int
    unique_artifacts: int
    content_artifacts: int
    content_and_martech: int
    content_and_digital_marketing: int
    stale_version_rows: int


@dataclass(frozen=True)
class BackfillSummary:
    total: int
    mapped: int
    skipped: int
    failed: int
    elapsed_time: str
    before: MappingSnapshot
    after: MappingSnapshot


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _content_artifact_ids(session) -> set[str]:
    return set(
        session.scalars(
            select(ArtifactDepartmentMapping.artifact_id)
            .where(ArtifactDepartmentMapping.department_name == "Content")
            .distinct()
        ).all()
    )


def _artifact_ids_for_department(session, department_name: str) -> set[str]:
    return set(
        session.scalars(
            select(ArtifactDepartmentMapping.artifact_id)
            .where(ArtifactDepartmentMapping.department_name == department_name)
            .distinct()
        ).all()
    )


def _collect_snapshot(session) -> MappingSnapshot:
    total_rows = int(
        session.scalar(select(func.count()).select_from(ArtifactDepartmentMapping)) or 0
    )
    unique_artifacts = int(
        session.scalar(
            select(func.count(func.distinct(ArtifactDepartmentMapping.artifact_id)))
        )
        or 0
    )
    content_ids = _content_artifact_ids(session)
    martech_ids = _artifact_ids_for_department(session, "MarTech")
    digital_marketing_ids = _artifact_ids_for_department(session, "Digital Marketing")
    stale_version_rows = int(
        session.scalar(
            select(func.count())
            .select_from(ArtifactDepartmentMapping)
            .where(ArtifactDepartmentMapping.mapping_version != DEPARTMENT_MAPPING_VERSION)
        )
        or 0
    )
    return MappingSnapshot(
        total_rows=total_rows,
        unique_artifacts=unique_artifacts,
        content_artifacts=len(content_ids),
        content_and_martech=len(content_ids & martech_ids),
        content_and_digital_marketing=len(content_ids & digital_marketing_ids),
        stale_version_rows=stale_version_rows,
    )


def _print_migration_report(*, label: str, snapshot: MappingSnapshot) -> None:
    print(f"\n{label}", flush=True)
    print(f"  mapping_version target: {DEPARTMENT_MAPPING_VERSION}", flush=True)
    print(f"  total mapping rows: {snapshot.total_rows}", flush=True)
    print(f"  unique mapped artifacts: {snapshot.unique_artifacts}", flush=True)
    print(f"  artifacts with Content: {snapshot.content_artifacts}", flush=True)
    print(
        f"  Content + MarTech overlap: {snapshot.content_and_martech}",
        flush=True,
    )
    print(
        f"  Content + Digital Marketing overlap: {snapshot.content_and_digital_marketing}",
        flush=True,
    )
    print(f"  rows not on {DEPARTMENT_MAPPING_VERSION}: {snapshot.stale_version_rows}", flush=True)


def _format_elapsed(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def run_backfill(*, dry_run: bool = False) -> BackfillSummary:
    _configure_logging()
    session_factory = get_session_factory()

    with session_factory() as session:
        before = _collect_snapshot(session)

    artifact_ids: list[str]
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

    print("=" * 48, flush=True)
    print("CONTENT DEPARTMENT MAPPING BACKFILL", flush=True)
    print("=" * 48, flush=True)
    _print_migration_report(label="BEFORE", snapshot=before)

    if dry_run:
        print("\nDry run — no mappings updated.", flush=True)
        after = before
    else:
        print(
            f"\nRecomputing department mappings for {total} enriched artifacts...",
            flush=True,
        )
        for index, artifact_id in enumerate(artifact_ids, start=1):
            try:
                with session_factory() as session:
                    service = DepartmentMappingService(session)
                    result = service.map_artifact(artifact_id, force=True)
                    if result is None:
                        skipped += 1
                    else:
                        mapped += 1
                    session.commit()
            except Exception:
                failed += 1
                logger.exception("Failed mapping artifact_id=%s", artifact_id)

            if index % 100 == 0 or index == total:
                print(f"Progress: {index}/{total}", flush=True)

        with session_factory() as session:
            after = _collect_snapshot(session)

    elapsed = _format_elapsed(time.perf_counter() - started)
    _print_migration_report(label="AFTER", snapshot=after)

    print("\nDELTA", flush=True)
    print(
        f"  Content artifacts: {before.content_artifacts} -> {after.content_artifacts} "
        f"(+{after.content_artifacts - before.content_artifacts})",
        flush=True,
    )
    print(
        f"  total mapping rows: {before.total_rows} -> {after.total_rows} "
        f"({after.total_rows - before.total_rows:+d})",
        flush=True,
    )
    print(
        f"  Content + MarTech: {before.content_and_martech} -> {after.content_and_martech}",
        flush=True,
    )
    print(
        "  Content + Digital Marketing: "
        f"{before.content_and_digital_marketing} -> {after.content_and_digital_marketing}",
        flush=True,
    )

    if not dry_run:
        print(
            f"\nDone — mapped={mapped} skipped={skipped} failed={failed} "
            f"elapsed={elapsed}",
            flush=True,
        )

    return BackfillSummary(
        total=total,
        mapped=mapped,
        skipped=skipped,
        failed=failed,
        elapsed_time=elapsed,
        before=before,
        after=after,
    )


def main() -> int:
    if not probe_connection().ok:
        print("FAIL: Cannot connect to MySQL.")
        return 1

    dry_run = "--dry-run" in sys.argv
    try:
        run_backfill(dry_run=dry_run)
    finally:
        dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
