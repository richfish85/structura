PRAGMA foreign_keys = ON;

-- Review decisions are append-only evidence assessments. They never change an
-- entity's canonical status and retain the submitted run that made each call.
CREATE TABLE IF NOT EXISTS discrepancy_review_runs (
    id INTEGER PRIMARY KEY,
    run_key TEXT NOT NULL UNIQUE,
    research_batch_id INTEGER NOT NULL REFERENCES research_batches(id),
    input_digest TEXT NOT NULL CHECK (length(input_digest) = 64),
    decision_path TEXT NOT NULL,
    decision_count INTEGER NOT NULL CHECK (decision_count > 0),
    importer TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (research_batch_id, input_digest)
);

CREATE TABLE IF NOT EXISTS candidate_discrepancy_reviews (
    id INTEGER PRIMARY KEY,
    discrepancy_review_run_id INTEGER NOT NULL REFERENCES discrepancy_review_runs(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id),
    discrepancy_level TEXT NOT NULL CHECK (discrepancy_level IN ('L0', 'L1', 'L2', 'L3', 'L4')),
    disposition TEXT NOT NULL CHECK (disposition IN ('no_action', 'retain_for_review', 'needs_evidence', 'restructure_required', 'excluded_from_cohort')),
    decision_rationale TEXT NOT NULL,
    resolving_evidence TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    UNIQUE (discrepancy_review_run_id, intake_candidate_record_id)
);

CREATE INDEX IF NOT EXISTS idx_candidate_discrepancy_reviews_candidate
    ON candidate_discrepancy_reviews(intake_candidate_record_id);

CREATE TABLE IF NOT EXISTS candidate_discrepancy_review_types (
    candidate_discrepancy_review_id INTEGER NOT NULL REFERENCES candidate_discrepancy_reviews(id) ON DELETE CASCADE,
    discrepancy_type TEXT NOT NULL CHECK (discrepancy_type IN ('none', 'identity', 'granularity', 'date_precision', 'channel_availability', 'shipment_status', 'cohort_boundary', 'source_conflict', 'category', 'scope')),
    PRIMARY KEY (candidate_discrepancy_review_id, discrepancy_type)
);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('010_discrepancy_review');
