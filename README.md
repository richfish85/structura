# Structura

Structura is an evidence-backed hardware reference: find a product, understand its parts, and follow the evidence. Graph-shaped knowledge is backed by one authoritative SQL store.

Status: **First Connected Explorer published as a working reference; real-person trial pending** (2026-09-10). All records remain provisional. There is no claim of census completeness.

Live reference: **https://richfish85.github.io/structura/**

## What

- 54 historical candidates: 20 in the 1997 cohort and 34 in 1998, browsable by year, category and manufacturer.
- A Samsung 970 EVO 500 GB reference, with 16 connected entities and 22 sourced, typed assertions across the bounded example.
- Search, readable dossiers, component navigation, assertion evidence, a 500 GB / 1 TB comparison and an explicit unresolved production-layout question.

## Why

The next research questions should come from trying to understand a device in the explorer. More rows alone do not prove the eventual visual database. This checkpoint joins the historical catalogue to a deeply documented example without changing the SQL authority or hiding uncertainty.

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

Research can be wrong or malicious. Imports retain provenance, reject hash or assertion mismatches, and cannot promote records automatically. The browser interface has no write routes; it escapes text, restricts source links and serves only generated reference assets. Manufacturer performance specifications are labelled as such. Source rights, canonical promotion rules, historical identity disputes and revision-specific package details remain unresolved. No accounts, purchases, compatibility guarantees, price feed or openness score are provided.

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

Run the bounded trial before expanding the dataset. Fix navigation or modelling problems exposed by those tasks, then research the smallest next set of relationships needed to answer them.

Further context: [product brief](docs/product-brief.md), [architecture](docs/architecture.md), [research protocol](docs/multi-agent-research-protocol.md), [decision log](docs/decision-log.md), and [1997 repair status](research_batches/pilot-1997/00_STATUS.md).

## Access and reuse

The repository is public for transparency and portfolio review. It does not currently carry an open-source or dataset licence, and contributions are not yet being accepted. GitHub users may view and fork a public repository under GitHub's terms; no additional permission to reproduce, distribute, or create derivative works is granted here. See [NOTICE.md](NOTICE.md) for third-party material and source-rights boundaries.
