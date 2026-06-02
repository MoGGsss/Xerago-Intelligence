-- Sprint 3B — classification validation columns
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

ALTER TABLE artifact_enrichments
    ADD COLUMN confidence_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN validation_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    ADD COLUMN classification_reason TEXT NULL;
