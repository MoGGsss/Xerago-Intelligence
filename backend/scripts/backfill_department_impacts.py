#!/usr/bin/env python3
"""Backfill Department Impact Engine fields on existing department mappings."""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, or_, select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from xerago_intelligence.db import dispose_engine, get_session_factory
from xerago_intelligence.db.models.artifact_department_mapping import (
    ArtifactDepartmentMapping,
)
from xerago_intelligence.db.repositories.department_mapping_repository import (
    DepartmentMappingRepository,
)
from xerago_intelligence.mapping.department_service import DepartmentMappingService
from xerago_intelligence.taxonomy.impact_rules import DEPARTMENT_IMPACT_VERSION

logger = logging.getLogger(__name__)
PROGRESS_INTERVAL = 25


@dataclass(frozen=True)
class BackfillSummary:
    processed: int
    updated: int
    skipped: int
    failed: int
    elapsed_time: str


@dataclass(frozen=True)
class BackfillOptions:
    dry_run: bool = False
    force: bool = False
    artifact_id: str | None = None


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_options(argv: list[str]) -> BackfillOptions:
    artifact_id: str | None = None
    for index, arg in enumerate(argv):
        if arg == "--artifact-id" and index + 1 < len(argv):
            artifact_id = argv[index + 1].strip()
        elif arg.startswith("--artifact-id="):
            artifact_id = arg.split("=", 1)[1].strip()
    return BackfillOptions(
        dry_run="--dry-run" in argv,
        force="--force" in argv,
        artifact_id=artifact_id or None,
    )


def _needs_impact_filter():
    return or_(
        ArtifactDepartmentMapping.impact_summary.is_(None),
        ArtifactDepartmentMapping.impact_version.is_(None),
        ArtifactDepartmentMapping.impact_version != DEPARTMENT_IMPACT_VERSION,
    )


def _artifact_ids_needing_impact(
    session_factory,
    *,
    force: bool,
    artifact_id: str | None,
) -> list[str]:
    if artifact_id:
        return [artifact_id]

    with session_factory() as session:
        if force:
            stmt = (
                select(
                    ArtifactDepartmentMapping.artifact_id,
                    func.min(ArtifactDepartmentMapping.mapped_at).label("first_mapped_at"),
                )
                .group_by(ArtifactDepartmentMapping.artifact_id)
                .order_by(func.min(ArtifactDepartmentMapping.mapped_at).asc())
            )
        else:
            stmt = (
                select(
                    ArtifactDepartmentMapping.artifact_id,
                    func.min(ArtifactDepartmentMapping.mapped_at).label("first_mapped_at"),
                )
                .where(_needs_impact_filter())
                .group_by(ArtifactDepartmentMapping.artifact_id)
                .order_by(func.min(ArtifactDepartmentMapping.mapped_at).asc())
            )
        rows = session.execute(stmt).all()
        return [str(row.artifact_id) for row in rows]


def _format_elapsed(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def run_backfill(options: BackfillOptions) -> BackfillSummary:
    _configure_logging()
    session_factory = get_session_factory()

    with session_factory() as session:
        repo = DepartmentMappingRepository(session)
        print(
            f"Rows missing impact: {repo.count_missing_impact()}",
            flush=True,
        )
        print(
            f"Rows with stale impact version: {repo.count_stale_impact(DEPARTMENT_IMPACT_VERSION)}",
            flush=True,
        )

    artifact_ids = _artifact_ids_needing_impact(
        session_factory,
        force=options.force,
        artifact_id=options.artifact_id,
    )

    processed = 0
    updated = 0
    skipped = 0
    failed = 0
    started = time.perf_counter()
    total = len(artifact_ids)

    mode = "DRY-RUN" if options.dry_run else "LIVE"
    print(
        f"Backfill department impacts ({DEPARTMENT_IMPACT_VERSION}) [{mode}] — "
        f"{total} artifacts (force={options.force})",
        flush=True,
    )

    if options.dry_run:
        for artifact_id in artifact_ids[:10]:
            print(f"  would process: {artifact_id}", flush=True)
        if total > 10:
            print(f"  ... and {total - 10} more", flush=True)
        elapsed = _format_elapsed(time.perf_counter() - started)
        summary = BackfillSummary(
            processed=total,
            updated=0,
            skipped=0,
            failed=0,
            elapsed_time=elapsed,
        )
        print(
            f"Done — processed={summary.processed} updated={summary.updated} "
            f"skipped={summary.skipped} failed={summary.failed} "
            f"elapsed={summary.elapsed_time}",
            flush=True,
        )
        return summary

    for index, artifact_id in enumerate(artifact_ids, start=1):
        processed += 1
        try:
            with session_factory() as session:
                service = DepartmentMappingService(session)
                status = service.backfill_impacts(artifact_id, force=options.force)
                if status == "updated":
                    updated += 1
                    session.commit()
                elif status == "skipped":
                    skipped += 1
                else:
                    skipped += 1
                    logger.warning(
                        "Skipped artifact_id=%s reason=%s",
                        artifact_id,
                        status,
                    )
        except Exception:
            failed += 1
            logger.exception("Failed impact backfill artifact_id=%s", artifact_id)

        if index % PROGRESS_INTERVAL == 0 or index == total:
            print(f"Progress: {index}/{total}", flush=True)

    elapsed = _format_elapsed(time.perf_counter() - started)
    summary = BackfillSummary(
        processed=processed,
        updated=updated,
        skipped=skipped,
        failed=failed,
        elapsed_time=elapsed,
    )
    print(
        f"Done — processed={summary.processed} updated={summary.updated} "
        f"skipped={summary.skipped} failed={summary.failed} "
        f"elapsed={summary.elapsed_time}",
        flush=True,
    )
    return summary


def main() -> int:
    options = _parse_options(sys.argv[1:])
    try:
        run_backfill(options)
    finally:
        dispose_engine()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
