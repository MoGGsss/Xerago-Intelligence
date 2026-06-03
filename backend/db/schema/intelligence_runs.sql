-- Phase 9 — intelligence refresh cycle monitoring
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS intelligence_runs (
    run_id              CHAR(36)      NOT NULL,
    started_at          DATETIME(6)   NOT NULL,
    completed_at        DATETIME(6)   NULL,
    sources_polled      INT           NOT NULL DEFAULT 0,
    articles_found      INT           NOT NULL DEFAULT 0,
    articles_inserted   INT           NOT NULL DEFAULT 0,
    articles_filtered   INT           NOT NULL DEFAULT 0,
    articles_enriched   INT           NOT NULL DEFAULT 0,
    articles_scored     INT           NOT NULL DEFAULT 0,
    status              VARCHAR(16)   NOT NULL DEFAULT 'running',
    error_message       TEXT          NULL,
    PRIMARY KEY (run_id),
    KEY idx_intelligence_runs_started (started_at DESC),
    KEY idx_intelligence_runs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
