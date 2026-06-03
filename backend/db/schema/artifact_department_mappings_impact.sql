-- Department Impact Engine — extend artifact_department_mappings
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py
-- Safe for existing rows: all new columns nullable until impact backfill.

SET NAMES utf8mb4;

ALTER TABLE artifact_department_mappings
    ADD COLUMN impact_summary VARCHAR(256) NULL AFTER mapping_version,
    ADD COLUMN impact_category VARCHAR(64) NULL AFTER impact_summary,
    ADD COLUMN opportunity_type VARCHAR(64) NULL AFTER impact_category,
    ADD COLUMN department_opportunity_score TINYINT UNSIGNED NULL AFTER opportunity_type,
    ADD COLUMN impact_reason VARCHAR(512) NULL AFTER department_opportunity_score,
    ADD COLUMN impact_version VARCHAR(32) NULL AFTER impact_reason;
