-- Sprint 2B — per-source ingest cursor state
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS ingest_cursors (
    source_id           VARCHAR(64)  NOT NULL,
    cursor_value        TEXT         NOT NULL,
    last_entry_id       VARCHAR(255) NULL,
    last_published_at   DATETIME(6)  NULL,
    updated_at          DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
