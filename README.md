# Structura

Structura is an evidence-backed hardware tracker: a durable record of products, components, standards, capabilities, relationships and change over time. Find a product, understand its parts, and follow the evidence. Graph-shaped knowledge is backed by one authoritative SQL store.

Status: **SQL foundation and First Connected Explorer published; reusable visual confirmation and real-person testing are next** (2026-09-10). All records remain provisional. There is no claim of census completeness.

Live reference: **https://richfish85.github.io/structura/**

## What

- 54 historical candidates: 20 in the 1997 cohort and 34 in 1998, browsable by year, category and manufacturer.
- A Samsung 970 EVO 500 GB reference, with 16 connected entities and 22 sourced, typed assertions across the bounded example.
- Search, readable dossiers, component navigation, assertion evidence, a 500 GB / 1 TB comparison and an explicit unresolved production-layout question.
- Two locked public-use concepts: PC lifecycle readiness and phone charging capability. Neither is implemented yet.

## Why

Structura aims to become a definitive tracker through traceable identities, relationships, evidence, conflicts and known gaps. More rows alone do not prove that goal. The current checkpoint joins a historical catalogue to one deeply documented object; the next work tests whether people can understand that record visually and use it to answer a practical question.

## Product direction

1. **Tracked knowledge:** SQL remains authoritative.
2. **Visual confirmation:** derived views reveal components, standards, relationships, evidence and unknowns.
3. **Immediate use:** bounded pathways answer practical PC and phone questions from the shared record.

Gamified testing, evidence-gathering quests and an object-centred community are exploratory possibilities. They are not current features or approved implementation scope. See the [roadmap](ROADMAP.md).

## How

Python 3.10+ and its standard library are sufficient. From this directory:

```powershell
python -m structura build
python -m structura check
python -m structura serve --port 8770
```

Open [the local reference](http://127.0.0.1:8770/). Stop the server with Ctrl+C. Rebuild and refresh to view a new successful snapshot.

The build verifies the frozen inputs in `data/build-manifest.json`, applies all migrations, imports the historical and connected packets, checks SQL integrity, renders the site and checks every internal link. Only then does it atomically update `data/current.json`. Failed builds leave the previous successful snapshot available. Generated SQL, pages, file hashes and status are retained together under `data/builds/<build-id>/`; they are ignored by Git. A code change or new packet requires another build.

`check`, `stats` and `serve` use the current snapshot by default when one exists. `init --db <path>` still creates an empty research database. For the older intake-review interface, use `serve --review --db <path>`. The [previous README and manual pilot recipe](docs/archive/README-before-connected-explorer-20260909.md) are preserved as historical documentation, not the current build instructions.

## Implementation

```text
Frozen scout + separate verification + coordinator normalization
                            |
                       hash checks
                            |
                   SQLite snapshot
                            |
            integrity checks + HTML rendering
                            |
                 local link validation
                            |
                  current checkpoint
```

`schema/011_connected_reference.sql` adds the bounded connected model. `structura/connected.py` binds imported assertions to the assessed research packet. `structura/build.py` owns the snapshot lifecycle. `structura/explorer.py` renders read-only HTML with small local search assets. There is no second database or external service dependency.

## Assumptions

Candidate counts mix families, models, chips and boards; they are not equivalent-product or market-coverage counts. Cohort years remain separate from claimed release events. The SSD diagram shows documented constituent descriptions, not inspected packages or real board positions. Supported and qualified source assessments do not confer canonical approval.

Three relationship terms remain explicitly proposed: MEMBER_OF_FAMILY, CONFIGURATION_OF and REVISION_OF. See the [connected ontology proposal](docs/connected-ontology.md).

## Threat and risk notes

Research can be wrong or malicious. Imports retain provenance, reject hash or assertion mismatches, and cannot promote records automatically. The browser interface has no write routes; it escapes text, restricts source links and serves only generated reference assets. Manufacturer performance specifications are labelled as such. Source rights, canonical promotion rules, historical identity disputes and revision-specific package details remain unresolved. No submissions, accounts, purchases, compatibility guarantees, price feed, gamification or social features are provided.

## Validation

```powershell
python -m unittest discover -s tests -v
python -m structura init --db data/validation.db
python -m structura check --db data/validation.db
python -m structura build
python -m structura check
```

See [validation evidence](docs/connected-explorer-validation.md), the [milestone checklist](docs/first-connected-explorer.md), and the [real-person trial](docs/usability-trial.md). Agent browser checks do not count as participant results.

## Next step

Run the bounded [real-person trial](docs/usability-trial.md) before expanding the dataset. Use its findings to define the shared decision contract and the first reusable visual relationship path. The [testing pack](docs/user-testing/README.md) is ready to distribute.

Further context: [roadmap](ROADMAP.md), [product brief](docs/product-brief.md), [architecture](docs/architecture.md), [public pathways](docs/public-use-cases.md), [research protocol](docs/multi-agent-research-protocol.md), [decision log](docs/decision-log.md), and [1997 repair status](research_batches/pilot-1997/00_STATUS.md).

## Access and reuse

The repository is public for transparency and portfolio review. It does not currently carry an open-source or dataset licence, and contributions are not yet being accepted. GitHub users may view and fork a public repository under GitHub's terms; no additional permission to reproduce, distribute, or create derivative works is granted here. See [NOTICE.md](NOTICE.md) for third-party material and source-rights boundaries.
