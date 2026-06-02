-- Sprint 4 — strategic scoring columns
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

ALTER TABLE artifact_enrichments
    ADD COLUMN strategic_score TINYINT UNSIGNED NULL,
    ADD COLUMN priority_level VARCHAR(16) NULL,
    ADD COLUMN score_reason TEXT NULL,
    ADD COLUMN scored_at DATETIME(6) NULL;
