PRAGMA foreign_keys = ON;

-- Purpose and benchmark research is enrichment evidence, not a promotion
-- stage.  It therefore has its own immutable import run rather than being
-- folded into the scout/verify/normalize/audit chain.
CREATE TABLE IF NOT EXISTS context_import_runs (
    id INTEGER PRIMARY KEY,
    run_key TEXT NOT NULL UNIQUE,
    research_batch_id INTEGER NOT NULL REFERENCES research_batches(id),
    input_digest TEXT NOT NULL CHECK (length(input_digest) = 64),
    intent_path TEXT NOT NULL,
    benchmark_path TEXT NOT NULL,
    source_path TEXT NOT NULL,
    intent_count INTEGER NOT NULL CHECK (intent_count >= 0),
    benchmark_count INTEGER NOT NULL CHECK (benchmark_count >= 0),
    source_count INTEGER NOT NULL CHECK (source_count >= 0),
    importer TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (research_batch_id, input_digest)
);

CREATE TABLE IF NOT EXISTS context_import_run_sources (
    context_import_run_id INTEGER NOT NULL REFERENCES context_import_runs(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    PRIMARY KEY (context_import_run_id, source_id)
);

-- Preserve the worker's exact source-register wording even when its source
-- resolves to a URL already known by the global source register.
CREATE TABLE IF NOT EXISTS context_source_records (
    id INTEGER PRIMARY KEY,
    context_import_run_id INTEGER NOT NULL REFERENCES context_import_runs(id) ON DELETE CASCADE,
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
    UNIQUE (context_import_run_id, source_row_number)
);

CREATE TABLE IF NOT EXISTS product_intent_claims (
    id INTEGER PRIMARY KEY,
    context_import_run_id INTEGER NOT NULL REFERENCES context_import_runs(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id) ON DELETE CASCADE,
    claim_scope TEXT NOT NULL
        CHECK (claim_scope IN ('manufacturer_stated', 'independently_interpreted', 'inferred')),
    problem_addressed TEXT NOT NULL,
    target_user TEXT NOT NULL,
    engineering_response TEXT NOT NULL,
    confidence TEXT NOT NULL CHECK (confidence IN ('unknown', 'low', 'medium', 'high')),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    source_locator TEXT,
    evidence_note TEXT NOT NULL,
    limitations TEXT,
    researcher TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_product_intent_candidate
    ON product_intent_claims(intake_candidate_record_id);

CREATE TABLE IF NOT EXISTS benchmark_observations (
    id INTEGER PRIMARY KEY,
    context_import_run_id INTEGER NOT NULL REFERENCES context_import_runs(id) ON DELETE CASCADE,
    intake_candidate_record_id INTEGER NOT NULL REFERENCES intake_candidate_records(id) ON DELETE CASCADE,
    comparison_group_key TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    result_value REAL NOT NULL,
    result_unit TEXT NOT NULL,
    higher_is_better INTEGER NOT NULL CHECK (higher_is_better IN (0, 1)),
    system_configuration TEXT NOT NULL,
    test_date TEXT,
    result_provenance TEXT NOT NULL
        CHECK (result_provenance IN ('standards_body_vendor_submitted', 'independent_contemporary', 'manufacturer_claim', 'reproduced')),
    confidence TEXT NOT NULL CHECK (confidence IN ('unknown', 'low', 'medium', 'high')),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    source_locator TEXT,
    limitations TEXT,
    researcher TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_benchmark_candidate
    ON benchmark_observations(intake_candidate_record_id);
CREATE INDEX IF NOT EXISTS idx_benchmark_comparison_group
    ON benchmark_observations(comparison_group_key, benchmark_name, metric_name);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('009_product_context');
