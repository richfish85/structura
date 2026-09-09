# Structura architecture

Structura is a provenance-first hardware reference. SQLite is the authoritative data store; HTML pages, search data, diagrams, and any future graph projection are derived views.

## Components

| Area | Responsibility |
|---|---|
| `schema/` | Ordered SQLite migrations and proposed ontology seeds. |
| `research_batches/` | Immutable stage artifacts, manifests, coordinator repairs, and human review inputs. |
| `data/build-manifest.json` | Frozen list and SHA-256 identity of inputs for the current reproducible build. |
| `structura/intake.py` | Validates and imports scout, verification, normalization, audit, context, and review artifacts as non-canonical data. |
| `structura/connected.py` | Validates and imports the bounded connected-object packet and separate verification. |
| `structura/build.py` | Creates an isolated SQL/site snapshot, validates it, and atomically advances `data/current.json`. |
| `structura/explorer.py` | Renders and serves the current read-only reference site. |
| `structura/static_site.py`, `structura/web.py` | Legacy research-review views retained for existing workflows. |
| `tests/` | Schema, intake, provenance, build, explorer, and read-only server checks. |

## Data flow

```text
bounded source research
  -> immutable scout artifact
  -> independent verification
  -> normalization proposal
  -> independent audit
  -> coordinator acceptance/repair
  -> non-canonical SQLite import
  -> integrity and evidence checks
  -> derived HTML/search/diagram files
  -> atomic current-snapshot pointer
  -> human review and separate canonical promotion, when authorized
```

`python -m structura build` verifies manifest hashes before import. It creates `data/builds/<build-id>/structura.db` and a sibling `site/`, runs foreign-key, canonical-evidence, SQLite integrity, and internal-link checks, then replaces `data/current.json`. A failed build cannot replace the current successful snapshot. Generated snapshots are ignored by Git.

`python -m structura serve` follows the current snapshot and serves only generated reference assets over a read-only local server. The browser never writes SQL.

## Boundaries

- SQLite has one writer. Parallel workers produce files; the coordinator validates and imports them.
- Candidate, verified, reviewed, and canonical are distinct states. Structural import is not factual or canonical approval.
- Product, family, board, chip/component, interface, protocol, standard, form factor, company, and organization identities remain distinct.
- Cohort year is a research grouping, not automatically a release date.
- Diagram coordinates are presentation metadata, not evidence of physical layout.
- A graph database, public contribution service, accounts, pricing, compatibility guarantees, and scoring are outside the current architecture.

Schema details are in [SCHEMA.md](SCHEMA.md); evidence and promotion rules are in [SOURCE_POLICY.md](SOURCE_POLICY.md). Historical design detail remains under `docs/`.
