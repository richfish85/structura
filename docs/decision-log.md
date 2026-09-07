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

## 2026-09-08 — CPU scout pass 01

### Observed

- Manufacturer sources distinguish announcement, introduction, system availability, component availability, boxed availability, first shipment, and volume shipment.
- Family-level launch dates cannot safely be inherited by speed grades or SKUs.
- Quarter-only and retrospective evidence is common enough to require explicit treatment.
- Frequency labels do not provide stable ordering part numbers, and suffixes such as `300A` are identity-bearing.
- The Pentium II Xeon 400 MHz cache options immediately challenge a one-row-per-frequency model.

### Candidate decisions for review

- Add typed product events rather than expanding the meaning of `release_date`.
- Track source independence separately from source tier and source count.
- Decide whether the first 1998 population is a launch cohort or a full commercially-present census.
- Define family, model/variant, and orderable SKU boundaries before normalization.

No scout candidate was verified, normalized, imported, or promoted.
