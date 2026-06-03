-- Phase 8 — centralized RSS source registry
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py
-- Seed:   python scripts/seed_rss_sources.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS rss_sources (
    source_id          VARCHAR(64)   NOT NULL,
    source_name        VARCHAR(255)  NOT NULL,
    source_url         VARCHAR(2048) NOT NULL,
    rss_url            VARCHAR(2048) NOT NULL,
    source_tier        TINYINT       NOT NULL,
    active_flag        TINYINT(1)    NOT NULL DEFAULT 1,
    failure_count      INT           NOT NULL DEFAULT 0,
    last_success_at    DATETIME(6)   NULL,
    last_failure_at    DATETIME(6)   NULL,
    last_health_status VARCHAR(16)   NULL,
    last_run_at        DATETIME(6)   NULL,
    created_at         DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at         DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (source_id),
    UNIQUE KEY uq_rss_sources_rss_url (rss_url(768)),
    KEY idx_rss_sources_tier_active (source_tier, active_flag),
    CONSTRAINT chk_rss_sources_tier CHECK (source_tier IN (1, 2, 3))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rss_source_runs (
    run_id              CHAR(36)      NOT NULL,
    source_id           VARCHAR(64)   NOT NULL,
    started_at          DATETIME(6)   NOT NULL,
    finished_at         DATETIME(6)   NOT NULL,
    status              VARCHAR(16)   NOT NULL,
    http_status         INT           NULL,
    entries_fetched     INT           NOT NULL DEFAULT 0,
    entries_inserted    INT           NOT NULL DEFAULT 0,
    entries_skipped_dup INT           NOT NULL DEFAULT 0,
    entries_skipped_cursor INT        NOT NULL DEFAULT 0,
    error_message       TEXT          NULL,
    PRIMARY KEY (run_id),
    KEY idx_rss_source_runs_source_started (source_id, started_at DESC),
    CONSTRAINT fk_rss_source_runs_source
        FOREIGN KEY (source_id) REFERENCES rss_sources (source_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
