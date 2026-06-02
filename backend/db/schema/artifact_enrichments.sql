-- Sprint 3A — LLM enrichment results per artifact
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS artifact_enrichments (
    enrichment_id   CHAR(36)      NOT NULL,
    artifact_id     CHAR(36)      NOT NULL,
    summary         TEXT          NOT NULL,
    why_it_matters  TEXT          NOT NULL,
    domain          VARCHAR(64)   NOT NULL,
    signal_type     VARCHAR(128)  NOT NULL,
    provider        VARCHAR(32)   NOT NULL,
    model           VARCHAR(128)  NOT NULL,
    prompt_version  VARCHAR(32)   NOT NULL,
    raw_response    MEDIUMTEXT    NULL,
    confidence_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
    validation_status VARCHAR(32)  NOT NULL DEFAULT 'pending',
    classification_reason TEXT      NULL,
    strategic_score   TINYINT UNSIGNED NULL,
    priority_level    VARCHAR(16)   NULL,
    score_reason      TEXT          NULL,
    scored_at         DATETIME(6)   NULL,
    enriched_at     DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (enrichment_id),
    UNIQUE KEY uq_artifact_enrichments_artifact_id (artifact_id),
    KEY idx_artifact_enrichments_domain (domain),
    CONSTRAINT fk_artifact_enrichments_artifact
        FOREIGN KEY (artifact_id) REFERENCES artifacts (artifact_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
