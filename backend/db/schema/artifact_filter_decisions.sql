-- Negative intelligence filter decisions (pre-enrichment gate)
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS artifact_filter_decisions (
    decision_id       CHAR(36)         NOT NULL,
    artifact_id       CHAR(36)         NOT NULL,
    filter_version    VARCHAR(32)      NOT NULL,
    negative_score    TINYINT UNSIGNED NOT NULL,
    skip_threshold    TINYINT UNSIGNED NOT NULL,
    decision          VARCHAR(16)      NOT NULL,
    skip_reason       TEXT             NULL,
    matched_keywords  JSON             NOT NULL,
    evaluated_at      DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (decision_id),
    UNIQUE KEY uq_artifact_filter_version (artifact_id, filter_version),
    KEY idx_filter_decision (decision, filter_version),
    KEY idx_filter_artifact (artifact_id),
    CONSTRAINT fk_artifact_filter_decisions_artifact
        FOREIGN KEY (artifact_id) REFERENCES artifacts (artifact_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
