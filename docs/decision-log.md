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

## 2026-09-08 — First census population locked

### Adopted

- The first dataset is the **1998 launch cohort**.
- It covers products newly introduced or first commercially shipped during 1998.
- Products launched earlier and merely remaining commercially available in 1998 are outside this first dataset.
- This cohort must not be described as a full census of the 1998 market.

### Still open

- Whether manufacturer announcement alone can ever qualify when introduction or first-shipment evidence is unavailable
- Which launch event controls public year navigation when introduction, system availability, component shipment, and boxed availability differ

## 2026-09-08 — Launch-cohort mini demo

### Adopted

- Agent workers write isolated, immutable CSV/JSON artifacts rather than sharing a database writer.
- One coordinator validates and hashes accepted artifacts before importing them.
- Pre-review imports are explicitly non-canonical candidate/staging records.
- Exact retries are idempotent; changed payloads that collide with existing candidate keys require a human merge decision.
- The demonstration renders deterministic, unstyled static HTML from SQLite and requires no JavaScript, framework, or running server.
- Canonical promotion remains a separate transaction after a recorded human decision.

### Verification outcome

- All ten bounded CPU candidates retain enough first-party evidence to remain in the human-review queue.
- The Celeron 266 has an exact introduction date but an unresolved exact commercial-availability date.
- Pentium II Xeon 400 cache variants remain a product-granularity question.
- AMD-K6-2 350 and 400 timing remains quarter-precision and must not be converted into exact dates.

### Still open

- Wire job/result manifest identity directly into the SQL import ledger.
- Define the normalization proposal format and independent omission/duplicate audit.
- Define and test the recorded human canonical-promotion transaction.
