-- Department intelligence mappings per artifact
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS artifact_department_mappings (
    mapping_id                  CHAR(36)         NOT NULL,
    artifact_id                 CHAR(36)         NOT NULL,
    department_name             VARCHAR(64)      NOT NULL,
    department_relevance_score  TINYINT UNSIGNED NOT NULL,
    mapping_version             VARCHAR(32)      NOT NULL,
    impact_summary              VARCHAR(256)     NULL,
    impact_category             VARCHAR(64)      NULL,
    opportunity_type            VARCHAR(64)      NULL,
    department_opportunity_score TINYINT UNSIGNED NULL,
    impact_reason               VARCHAR(512)     NULL,
    impact_version              VARCHAR(32)      NULL,
    mapped_at                   DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (mapping_id),
    UNIQUE KEY uq_artifact_department (artifact_id, department_name),
    KEY idx_department_score (department_name, department_relevance_score),
    KEY idx_artifact_department_artifact (artifact_id),
    CONSTRAINT fk_artifact_department_mappings_artifact
        FOREIGN KEY (artifact_id) REFERENCES artifacts (artifact_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
