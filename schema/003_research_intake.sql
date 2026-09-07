PRAGMA foreign_keys = ON;

-- Imported work remains a reviewable staging record.  This is deliberately
-- separate from a decision to promote any entity to canonical status.
CREATE TABLE IF NOT EXISTS research_import_runs (
    id INTEGER PRIMARY KEY,
    run_key TEXT NOT NULL UNIQUE,
    research_batch_id INTEGER NOT NULL REFERENCES research_batches(id),
    pipeline_stage TEXT NOT NULL
        CHECK (pipeline_stage IN ('planned', 'scouting', 'verification', 'normalization', 'audit', 'human_review', 'paused')),
    input_digest TEXT NOT NULL CHECK (length(input_digest) = 64),
    candidate_path TEXT NOT NULL,
    source_path TEXT,
    candidate_count INTEGER NOT NULL CHECK (candidate_count >= 0),
    source_count INTEGER NOT NULL CHECK (source_count >= 0),
    importer TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (research_batch_id, input_digest)
);

CREATE INDEX IF NOT EXISTS idx_research_import_runs_batch ON research_import_runs(research_batch_id);

-- Raw hand-off fields are retained so future agents and reviewers can see
-- exactly what the import received before any normalisation decision.
CREATE TABLE IF NOT EXISTS intake_candidate_records (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL UNIQUE REFERENCES entities(id) ON DELETE CASCADE,
    source_row_number INTEGER NOT NULL CHECK (source_row_number > 0),
    candidate_key TEXT NOT NULL,
    manufacturer_raw TEXT NOT NULL,
    product_name_raw TEXT NOT NULL,
    model_number_raw TEXT,
    product_type_raw TEXT NOT NULL,
    announced_date_raw TEXT,
    release_date_raw TEXT,
    market_scope_raw TEXT,
    source_1_url TEXT NOT NULL,
    source_2_url TEXT,
    notes TEXT NOT NULL,
    UNIQUE (import_run_id, candidate_key)
);

CREATE INDEX IF NOT EXISTS idx_intake_candidate_records_run ON intake_candidate_records(import_run_id);
CREATE INDEX IF NOT EXISTS idx_intake_candidate_records_key ON intake_candidate_records(candidate_key);

CREATE TABLE IF NOT EXISTS research_import_run_sources (
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    PRIMARY KEY (import_run_id, source_id)
);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('003_research_intake');
