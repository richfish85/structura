PRAGMA foreign_keys = ON;

-- Normalization is a proposal layer. It deliberately does not rewrite the
-- raw hand-off or promote the linked entity.
CREATE TABLE IF NOT EXISTS normalization_proposals (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id),
    normalized_manufacturer TEXT NOT NULL,
    normalized_display_name TEXT NOT NULL,
    entity_granularity TEXT NOT NULL
        CHECK (entity_granularity IN ('family', 'model_variant', 'sku_unresolved')),
    parent_intake_candidate_record_id INTEGER REFERENCES intake_candidate_records(id),
    normalized_category TEXT NOT NULL,
    qualifying_event_type TEXT NOT NULL,
    normalized_launch_date TEXT,
    date_precision TEXT NOT NULL
        CHECK (date_precision IN ('exact', 'month', 'quarter', 'year', 'range', 'unknown')),
    market_channel_notes TEXT,
    decision_status TEXT NOT NULL
        CHECK (decision_status IN ('proposed', 'review_required', 'blocked')),
    rationale TEXT NOT NULL,
    open_questions TEXT,
    normalizer TEXT NOT NULL,
    UNIQUE (import_run_id, intake_candidate_record_id)
);

CREATE INDEX IF NOT EXISTS idx_normalization_candidate
    ON normalization_proposals(intake_candidate_record_id);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('006_normalization_proposals');
