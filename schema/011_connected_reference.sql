PRAGMA foreign_keys = ON;

-- Proposed in docs/connected-ontology.md. These narrow relations avoid claiming
-- that a specification is a physical package or an interchangeable product.
INSERT OR IGNORE INTO predicates(code,label,relationship_family,description,ontology_status) VALUES
('MEMBER_OF_FAMILY','member of family','classification','A specific product model belongs to a named product family.','proposed'),
('CONFIGURATION_OF','configuration of','classification','A specified width or configuration of an interface.','proposed'),
('REVISION_OF','revision of','classification','An identified revision of a protocol or specification.','proposed');

CREATE TABLE IF NOT EXISTS connected_imports (
    id INTEGER PRIMARY KEY,
    packet_key TEXT NOT NULL UNIQUE,
    packet_sha256 TEXT NOT NULL,
    verification_sha256 TEXT NOT NULL,
    scout_agent TEXT NOT NULL,
    verifier_agent TEXT NOT NULL,
    CHECK(scout_agent <> verifier_agent)
);
CREATE TABLE IF NOT EXISTS reference_entities (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id),
    connected_import_id INTEGER NOT NULL REFERENCES connected_imports(id),
    short_description TEXT NOT NULL,
    category TEXT,
    manufacturer TEXT,
    context_year INTEGER,
    context_year_basis TEXT,
    model_number TEXT,
    role_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relationship_details (
    relationship_id INTEGER PRIMARY KEY REFERENCES relationships(id),
    relationship_key TEXT NOT NULL UNIQUE,
    connected_import_id INTEGER NOT NULL REFERENCES connected_imports(id),
    scope TEXT NOT NULL,
    assessment TEXT NOT NULL CHECK(assessment IN ('supported','qualified')),
    verifier_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reference_claims (
    id INTEGER PRIMARY KEY,
    claim_key TEXT NOT NULL UNIQUE,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    related_entity_id INTEGER REFERENCES entities(id),
    connected_import_id INTEGER NOT NULL REFERENCES connected_imports(id),
    kind TEXT NOT NULL CHECK(kind IN ('fact','comparison','unresolved')),
    title TEXT NOT NULL,
    statement TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('supported','qualified','unknown')),
    limits TEXT NOT NULL,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    locator TEXT NOT NULL,
    evidence_role TEXT NOT NULL CHECK(evidence_role IN ('supports','context')),
    verifier_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visual_regions (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id),
    parent_entity_id INTEGER NOT NULL REFERENCES entities(id),
    label TEXT NOT NULL,
    x REAL NOT NULL CHECK(x >= 0 AND x <= 100),
    y REAL NOT NULL CHECK(y >= 0 AND y <= 100),
    width REAL NOT NULL CHECK(width > 0 AND width <= 100),
    height REAL NOT NULL CHECK(height > 0 AND height <= 100),
    CHECK(x + width <= 100 AND y + height <= 100)
);
INSERT OR IGNORE INTO schema_migrations(version) VALUES ('011_connected_reference');
