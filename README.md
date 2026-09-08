# Structura

Structura is a provenance-first hardware census and relationship explorer: **graph-shaped knowledge backed by one canonical SQL database**.

Status: local foundation / ontology v0.1 proposal. There is no public deployment and no claim of census completeness.

## What

The first useful version is a searchable catalogue of hardware products, manufacturers, categories, and release timing. Its schema can also express relationships such as:

```text
product -> MANUFACTURED_BY -> company
device  -> CONTAINS        -> component
SSD     -> COMMUNICATES_USING -> PCIe
SSD     -> IMPLEMENTS      -> NVMe
standard -> STANDARDIZED_BY -> organization
```

The long-term research question is larger than specifications: how do technical design, standardisation, integration, repairability, supplier structure, and vendor control change across product generations? Structura records the evidence needed to investigate that question; it does not assume the conclusion.

## Why

Existing product catalogues, manuals, teardowns, repair guides, standards, reviews, and market records expose different fragments of hardware knowledge. Structura aims to join those fragments into a reviewable dataset where uncertainty and conflicting evidence remain visible.

## How

The local foundation uses only Python's standard library and SQLite.

```powershell
cd C:/Users/roosd/Downloads/Portfolio/structura
python -m structura init
python -m structura check
python -m structura serve
```

Then open `http://127.0.0.1:8000`. The explorer is deliberately plain and read-only. Stop it with `Ctrl+C`.

The generated database is `data/structura.db` and is ignored by Git. Schema and proposed ontology changes live in versioned SQL files instead.

### Run the launch-cohort mini demo

This builds a separate disposable review database, imports the scout, independent-verification, normalization-proposal, and audit artifacts without promoting them, and renders plain static HTML from SQL:

```powershell
python -m structura init --db data/mini-demo.db
python -m structura import-batch --db data/mini-demo.db --candidates research_batches/pilot-1998-cpu/01_scout_candidates.csv --sources research_batches/pilot-1998-cpu/01_sources.csv --stage scouting
python -m structura import-verification --db data/mini-demo.db --verification research_batches/pilot-1998-cpu/02_verification.csv
python -m structura import-normalization --db data/mini-demo.db --normalization research_batches/pilot-1998-cpu/03_normalization_proposal.csv
python -m structura import-audit --db data/mini-demo.db --audit research_batches/pilot-1998-cpu/04_audit_findings.csv
python -m structura import-batch --db data/mini-demo.db --candidates research_batches/pilot-1998-cpu/jobs/job-1998-cpu-scout-desktop-server-002/runs/run-20260908T000519Z-luna-desktop-server-02/candidates.csv --sources research_batches/pilot-1998-cpu/jobs/job-1998-cpu-scout-desktop-server-002/runs/run-20260908T000519Z-luna-desktop-server-02/sources.csv --stage scouting
python -m structura import-batch --db data/mini-demo.db --candidates research_batches/pilot-1998-cpu/jobs/job-1998-cpu-scout-mobile-upgrade-003/runs/run-20260908T000519Z-luna-mobile-upgrade-03/candidates.csv --sources research_batches/pilot-1998-cpu/jobs/job-1998-cpu-scout-mobile-upgrade-003/runs/run-20260908T000519Z-luna-mobile-upgrade-03/sources.csv --stage scouting
python -m structura import-verification --db data/mini-demo.db --verification research_batches/pilot-1998-cpu/jobs/job-1998-cpu-verify-omissions-004/runs/run-20260908T001533Z-terra-verifier-04/verification.csv
python -m structura render-review --db data/mini-demo.db --output exports/mini-demo
python -m structura check --db data/mini-demo.db
```

Open `exports/mini-demo/index.html`. Repeating any import is safe: the exact input digest is recognized and no duplicate run, proposal, assertion, or finding rows are added.

## Implementation

```text
research intake
     |
     v
agent files -> validate/hash -> non-canonical SQL review staging
                                      |
                                      +----> plain static HTML
                                      |
                verification -> normalization -> audit -> human review
                                                               |
                                                               v
                                                        canonical status
                                                               |
                                                               v
                                                    CSV / graph export later
```

- `schema/001_initial.sql` defines entities, product details, relationships, sources, and evidence links.
- `schema/002_seed_ontology.sql` supplies a proposed, revisable relationship vocabulary.
- `schema/003_research_intake.sql` through `007_audit_findings.sql` preserve immutable import runs, raw candidate rows, verification evidence, normalization proposals, and audit leads separately from canonical promotion.
- `data/intake/` contains blank handoff templates for research stages.
- `structura/` contains database setup, validation, and the local HTML explorer.
- `docs/` records product boundaries, architecture, research workflow, ontology, and risks.

## Assumptions

- SQLite is sufficient for one local writer and early research batches.
- The initial problem is a catalogue/census problem, not a deep graph-traversal problem.
- Release timing may be partial or disputed and must support `NULL`/unknown values.
- Ontology v0.1 is proposed rather than locked; evidence from diverse devices should change it.
- Visual identity remains open until the information architecture proves useful.

## Threat and risk notes

- Research imports may contain false claims, prompt-injection text, malicious URLs, or poisoned normalization suggestions.
- A tidy graph can amplify a weak claim. Evidence quality and review status must remain visible downstream.
- Manufacturer naming, product-family boundaries, announcement dates, and retail availability are common ambiguity points.
- Source excerpts and scraped datasets may carry copyright or licensing restrictions.
- SQLite is not the intended multi-user contribution backend.
- Openness, repairability, scarcity, and market-control metrics are not yet defined and must not be presented as objective scores.

See [Threat and risk notes](docs/threat-and-risk-notes.md) for controls.

## Validation steps

```powershell
python -m unittest discover -s tests -v
python -m structura init --db data/validation.db
python -m structura check --db data/validation.db
python -m structura stats --db data/validation.db
```

Checklist:

- [x] Independent local Git repository
- [x] Versioned relational schema
- [x] Graph-compatible entity/relationship core
- [x] Evidence and contradiction model
- [x] Proposed ontology seed
- [x] Blank research intake templates
- [x] Read-only local HTML explorer
- [x] Automated schema and web tests
- [ ] Agree what counts as a product versus a family, chip, or board
- [x] Scout the first bounded 1998 CPU candidate batch
- [x] Independently verify the CPU candidates
- [x] Propose normalization for the CPU candidates
- [x] Audit the CPU candidates for duplicates and omissions
- [x] Demonstrate idempotent SQL intake and plain static HTML generation
- [x] Expand and independently verify the twelve CPU omission leads
- [ ] Resolve the OverDrive identity and Xeon 450 event flags
- [ ] Expand the pilot to GPU and HDD candidates after the CPU criteria review
- [ ] Define the human promotion gate from verified to canonical
- [ ] Test the ontology on one deeply modelled object
- [ ] Select a licence before publishing or accepting contributions

## Current decisions and open questions

See [Product brief](docs/product-brief.md), [Architecture](docs/architecture.md), [Ontology v0.1](docs/ontology-v0.1.md), [Research workflow](docs/research-workflow.md), [research criteria v0.3](docs/research-criteria-v0.3.md), [CPU pilot status](research_batches/pilot-1998-cpu/00_STATUS.md), and [Decision log](docs/decision-log.md).
