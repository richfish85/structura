PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS entity_types (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    ontology_status TEXT NOT NULL DEFAULT 'proposed'
        CHECK (ontology_status IN ('proposed', 'approved', 'deprecated'))
);

CREATE TABLE IF NOT EXISTS predicates (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    relationship_family TEXT NOT NULL,
    description TEXT NOT NULL,
    inverse_code TEXT REFERENCES predicates(code),
    ontology_status TEXT NOT NULL DEFAULT 'proposed'
        CHECK (ontology_status IN ('proposed', 'approved', 'deprecated'))
);

CREATE TABLE IF NOT EXISTS research_batches (
    id INTEGER PRIMARY KEY,
    batch_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    scope_note TEXT NOT NULL,
    workflow_status TEXT NOT NULL DEFAULT 'planned'
        CHECK (workflow_status IN ('planned', 'scouting', 'verification', 'normalization', 'audit', 'human_review', 'complete', 'paused')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    source_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    publisher TEXT,
    source_type TEXT NOT NULL DEFAULT 'other',
    source_tier INTEGER NOT NULL CHECK (source_tier BETWEEN 1 AND 4),
    url TEXT,
    archive_url TEXT,
    publication_date TEXT,
    accessed_date TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (url IS NOT NULL OR archive_url IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    entity_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    entity_type_code TEXT NOT NULL REFERENCES entity_types(code),
    description TEXT,
    record_status TEXT NOT NULL DEFAULT 'candidate'
        CHECK (record_status IN ('candidate', 'verified', 'review_required', 'canonical', 'retired', 'example')),
    confidence TEXT NOT NULL DEFAULT 'unknown'
        CHECK (confidence IN ('unknown', 'low', 'medium', 'high')),
    research_batch_id INTEGER REFERENCES research_batches(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type_code);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(record_status);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);

CREATE TABLE IF NOT EXISTS product_details (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    model_number TEXT,
    announced_date TEXT,
    release_date TEXT,
    release_year INTEGER CHECK (release_year IS NULL OR release_year BETWEEN 1800 AND 2200),
    date_precision TEXT NOT NULL DEFAULT 'unknown'
        CHECK (date_precision IN ('exact', 'month', 'year', 'range', 'unknown')),
    market_scope TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_product_release_year ON product_details(release_year);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES entities(id),
    predicate_code TEXT NOT NULL REFERENCES predicates(code),
    object_id INTEGER NOT NULL REFERENCES entities(id),
    assertion_status TEXT NOT NULL DEFAULT 'candidate'
        CHECK (assertion_status IN ('candidate', 'verified', 'review_required', 'canonical', 'retired', 'example')),
    confidence TEXT NOT NULL DEFAULT 'unknown'
        CHECK (confidence IN ('unknown', 'low', 'medium', 'high')),
    valid_from TEXT,
    valid_to TEXT,
    notes TEXT,
    research_batch_id INTEGER REFERENCES research_batches(id),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (subject_id <> object_id),
    UNIQUE (subject_id, predicate_code, object_id, valid_from)
);

CREATE INDEX IF NOT EXISTS idx_relationships_subject ON relationships(subject_id);
CREATE INDEX IF NOT EXISTS idx_relationships_object ON relationships(object_id);
CREATE INDEX IF NOT EXISTS idx_relationships_predicate ON relationships(predicate_code);

CREATE TABLE IF NOT EXISTS entity_evidence (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    field_name TEXT NOT NULL DEFAULT 'identity',
    evidence_role TEXT NOT NULL DEFAULT 'supports'
        CHECK (evidence_role IN ('supports', 'contradicts', 'context', 'lead_only')),
    locator TEXT,
    evidence_note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_id, source_id, field_name, evidence_role, locator)
);

CREATE TABLE IF NOT EXISTS relationship_evidence (
    id INTEGER PRIMARY KEY,
    relationship_id INTEGER NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    evidence_role TEXT NOT NULL DEFAULT 'supports'
        CHECK (evidence_role IN ('supports', 'contradicts', 'context', 'lead_only')),
    locator TEXT,
    evidence_note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (relationship_id, source_id, evidence_role, locator)
);

CREATE TABLE IF NOT EXISTS review_events (
    id INTEGER PRIMARY KEY,
    object_kind TEXT NOT NULL CHECK (object_kind IN ('entity', 'relationship', 'source', 'ontology')),
    object_key TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    rationale TEXT NOT NULL,
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('001_initial');
