PRAGMA foreign_keys = ON;

-- A report-shaped verification hand-off retains its richer raw fields rather
-- than squeezing date precision, inclusion advice, or open questions into a
-- canonical entity before review.
CREATE TABLE IF NOT EXISTS verification_report_records (
    id INTEGER PRIMARY KEY,
    verification_record_id INTEGER NOT NULL UNIQUE REFERENCES verification_records(id) ON DELETE CASCADE,
    inclusion_recommendation TEXT NOT NULL,
    verified_event_type TEXT NOT NULL,
    verified_timing_raw TEXT NOT NULL,
    date_precision_raw TEXT NOT NULL,
    source_1_url TEXT NOT NULL,
    source_1_locator TEXT,
    source_1_evidence TEXT NOT NULL,
    source_2_url TEXT,
    source_2_locator TEXT,
    source_2_evidence TEXT,
    contradictions_or_limits TEXT,
    unresolved_questions TEXT,
    verifier_notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verification_evidence_references (
    verification_record_id INTEGER NOT NULL REFERENCES verification_records(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    source_position INTEGER NOT NULL CHECK (source_position IN (1, 2)),
    locator TEXT,
    evidence_note TEXT NOT NULL,
    PRIMARY KEY (verification_record_id, source_position)
);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('005_verification_report_intake');
