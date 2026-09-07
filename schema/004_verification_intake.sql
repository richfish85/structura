PRAGMA foreign_keys = ON;

-- Verification is an assertion made during a separate stage. It does not
-- alter an entity's record_status; a human promotion decision remains later.
CREATE TABLE IF NOT EXISTS verification_records (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id),
    identity_status TEXT NOT NULL,
    manufacturer_status TEXT NOT NULL,
    category_status TEXT NOT NULL,
    release_timing_status TEXT NOT NULL,
    confidence TEXT NOT NULL CHECK (confidence IN ('unknown', 'low', 'medium', 'high')),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    source_tier INTEGER NOT NULL CHECK (source_tier BETWEEN 1 AND 4),
    evidence_role TEXT NOT NULL CHECK (evidence_role IN ('supports', 'contradicts', 'context', 'lead_only')),
    locator TEXT,
    evidence_note TEXT NOT NULL,
    conflict_note TEXT,
    verifier TEXT NOT NULL,
    UNIQUE (import_run_id, intake_candidate_record_id)
);

CREATE INDEX IF NOT EXISTS idx_verification_records_candidate ON verification_records(intake_candidate_record_id);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('004_verification_intake');
