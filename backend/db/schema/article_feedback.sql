-- Article feedback per department (useful / not relevant)
-- MySQL 8.0+ | utf8mb4
--
-- Apply: python scripts/apply_schema.py

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS article_feedback (
    feedback_id       CHAR(36)         NOT NULL,
    artifact_id       CHAR(36)         NOT NULL,
    department_name   VARCHAR(64)      NOT NULL,
    feedback_type     VARCHAR(16)      NOT NULL,
    feedback_reason   VARCHAR(32)      NULL,
    created_at        DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (feedback_id),
    UNIQUE KEY uq_article_feedback_artifact_department (artifact_id, department_name),
    KEY idx_article_feedback_artifact (artifact_id),
    KEY idx_article_feedback_department (department_name),
    CONSTRAINT fk_article_feedback_artifact
        FOREIGN KEY (artifact_id) REFERENCES artifacts (artifact_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_article_feedback_type
        CHECK (feedback_type IN ('positive', 'negative')),
    CONSTRAINT chk_article_feedback_reason_values
        CHECK (
            feedback_reason IS NULL
            OR feedback_reason IN (
                'wrong_department',
                'too_technical',
                'already_known',
                'low_business_impact',
                'duplicate_content',
                'not_relevant'
            )
        ),
    CONSTRAINT chk_article_feedback_reason_required
        CHECK (
            (feedback_type = 'positive' AND feedback_reason IS NULL)
            OR (feedback_type = 'negative' AND feedback_reason IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
