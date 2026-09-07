# Decision Log

## 2026-09-08 — Local repository foundation

### Adopted for the foundation

- Project name: **Structura**; working description: HardwareDB.
- One SQL database is the source of truth.
- The schema is graph-compatible from the beginning through entities and relationships.
- SQLite is the initial local store; PostgreSQL is a later migration option.
- Neo4j or another graph database is optional, later, derived, and read-only relative to SQL.
- Provenance, contradictory evidence, confidence, and review status are first-class.
- The first interface is plain, read-only HTML intended to test information architecture.
- The first census pilot covers 1998 CPU, GPU, and HDD products.
- Research stages are separated; automated agents do not approve their own discoveries.

### Deliberately open

- Product versus family versus board/chip identity rules
- The first deeply modelled object: M.2 NVMe SSD or Ethernet NIC
- Exact canonical-promotion criteria and reviewer identity model
- Community contribution and moderation design
- Hardware openness, repairability, scarcity, and market-control metrics
- Public data and software licensing
- Production stack and hosting
- Visual identity

### Rationale

The durable asset is the ontology, evidence, and normalized records. Storage engines and presentation layers can change. Starting with inspectable SQL and plain HTML lets real use expose modelling failures before design or infrastructure becomes expensive to revise.
