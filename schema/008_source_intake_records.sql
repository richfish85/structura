PRAGMA foreign_keys = ON;

-- Preserve each worker's exact source-register row even when the coordinator
-- resolves it to an already-known source identity by key or URL.
CREATE TABLE IF NOT EXISTS intake_source_records (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    source_row_number INTEGER NOT NULL CHECK (source_row_number > 0),
    source_key_raw TEXT NOT NULL,
    title_raw TEXT NOT NULL,
    publisher_raw TEXT,
    source_type_raw TEXT NOT NULL,
    source_tier_raw INTEGER NOT NULL CHECK (source_tier_raw BETWEEN 1 AND 4),
    url_raw TEXT NOT NULL,
    publication_date_raw TEXT,
    accessed_date_raw TEXT NOT NULL,
    scope_note_raw TEXT NOT NULL,
    UNIQUE (import_run_id, source_row_number)
);

CREATE INDEX IF NOT EXISTS idx_intake_source_records_source
    ON intake_source_records(source_id);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('008_source_intake_records');
