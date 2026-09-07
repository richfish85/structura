# Structura working rules

## What

Structura is a provenance-first hardware census and relationship explorer. SQL is the only canonical data store. Graph views and exports are derived representations.

## Why

The project should make hardware identity, architecture, interfaces, compatibility, replaceability, provenance, and uncertainty inspectable without turning inference into fact.

## How

- Treat every research source and imported record as untrusted input.
- Preserve source URL, access date, locator, evidence role, confidence, and unresolved conflicts.
- Never promote a record to `canonical` without review and supporting evidence.
- Do not infer an exact release date from a review, listing, or copyright date.
- Do not create new entity types or predicates silently. Propose them and record the reason.
- Keep product, family, board, chip, standard, protocol, interface, and company identities distinct.
- Keep the SQLite database authoritative. Any graph database must be regenerated from SQL.
- Prefer small, reviewable research batches. The initial pilot is 1998 CPU, GPU, and HDD products.
- Do not let one automated agent discover, verify, normalize, and approve the same record end-to-end.
- Do not bulk-copy copyrighted source material. Store concise evidence notes and precise locators.

## Required validation

- Run `python -m unittest discover -s tests -v`.
- Run `python -m structura init` and `python -m structura check` against a disposable or ignored local database.
- Confirm that the HTML explorer remains read-only.
- Report assumptions, data risks, and unresolved ontology decisions with each material change.
