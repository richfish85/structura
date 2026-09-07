PRAGMA foreign_keys = ON;

-- Audit findings remain observations and leads. A proposed candidate key is
-- not an entity and cannot enter the cohort without a later scout/verify gate.
CREATE TABLE IF NOT EXISTS audit_findings (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES research_import_runs(id) ON DELETE CASCADE,
    finding_key TEXT NOT NULL,
    finding_type TEXT NOT NULL
        CHECK (finding_type IN ('duplicate', 'family_variant_overlap', 'date_inheritance', 'scope_error', 'category_error', 'omission_lead', 'evidence_gap')),
    severity TEXT NOT NULL CHECK (severity IN ('info', 'low', 'medium', 'high')),
    finding TEXT NOT NULL,
    source_url TEXT,
    source_locator TEXT,
    source_evidence TEXT,
    recommended_next_action TEXT NOT NULL,
    disposition TEXT NOT NULL CHECK (disposition IN ('open', 'resolved_no_change', 'follow_up')),
    auditor TEXT NOT NULL,
    UNIQUE (import_run_id, finding_key)
);

CREATE TABLE IF NOT EXISTS audit_finding_candidate_refs (
    audit_finding_id INTEGER NOT NULL REFERENCES audit_findings(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id),
    PRIMARY KEY (audit_finding_id, intake_candidate_record_id)
);

CREATE INDEX IF NOT EXISTS idx_audit_candidate_ref
    ON audit_finding_candidate_refs(intake_candidate_record_id);

CREATE TABLE IF NOT EXISTS audit_finding_proposed_keys (
    audit_finding_id INTEGER NOT NULL REFERENCES audit_findings(id) ON DELETE CASCADE,
    proposed_candidate_key TEXT NOT NULL,
    PRIMARY KEY (audit_finding_id, proposed_candidate_key)
);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('007_audit_findings');
