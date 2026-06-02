-- Sprint 2A — artifacts table (RSS ingestion)
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_artifacts_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id   CHAR(36)     NOT NULL,
    source_id     VARCHAR(64)  NOT NULL,
    title         TEXT         NOT NULL,
    url           VARCHAR(2048) NOT NULL,
    published_at  DATETIME(6)  NOT NULL,
    raw_content   MEDIUMTEXT   NULL,
    ingested_at   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (artifact_id),
    UNIQUE KEY uq_artifacts_url (url(768)),
    KEY idx_artifacts_source_id (source_id),
    KEY idx_artifacts_published_at (published_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
