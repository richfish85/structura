# Mini Demo Plan — SQL to Static HTML

Status: **implemented and retained as the SQL-to-static foundation**

## What

Build a lightweight demonstration in which separately produced research outputs are validated into SQLite and rendered from SQLite as plain static HTML.

This goal is complete. The current connected explorer and public Pages deployment build on this pipeline; this document remains the implementation record for the original mini demo.

```text
agent-owned files
      |
      v
validate + hash + stage
      |
      v
   SQLite
      |
      v
deterministic static HTML
```

The static site is an inspection surface, not a second database. It should remain useful with CSS and JavaScript absent.

## Why

Multiple research agents should be able to work concurrently without writing to the same database or files. A single controlled merge step can then reject malformed or duplicated outputs, preserve run provenance, and make every displayed record traceable to SQL.

## How

### Research side

- Each job has a unique batch, stage, job, and run identifier.
- Each agent owns a separate output path.
- Outputs contain no canonical status changes.
- A result manifest records role, model, source policy, input/output files, counts, and completion state.

### Merge side

- Validate file structure, allowed statuses, identifiers, URLs, and required evidence fields.
- Hash the exact input so a retry is idempotent.
- Use one SQLite transaction per accepted result.
- Keep the original stage and run provenance.
- Reject conflicting attempts to reuse an identifier with different content.

### Display side

- Generate an index, batch page, import-run pages, candidate pages, and linked source references from SQLite.
- Display stage, confidence, unknowns, conflicts, source origin, and evidence notes visibly.
- Use semantic HTML links, headings, lists, and tables.
- Do not require a running server, JavaScript, CSS, a framework, or network access to browse generated pages.
- Produce pages deterministically so unchanged SQL produces unchanged output.

## Mini-demo acceptance checklist

- [x] Initialize a fresh SQLite database from versioned migrations.
- [x] Ingest the CPU scout, verification, normalization, and audit material into non-canonical candidate/staging records.
- [x] Repeating the same import creates no duplicate records.
- [x] A changed payload that collides with staged candidate identity is rejected for human resolution.
- [x] Malformed input fails before any partial write.
- [x] Generate static HTML from SQLite, not directly from CSV.
- [x] The generated homepage links to the CPU batch, whose page links all imported candidate records.
- [x] Every displayed factual claim shows its stage and source context.
- [x] Display normalization proposals per candidate and audit/omission findings at batch and candidate level.
- [x] Static output contains no JavaScript dependency and remains readable without styling.
- [x] Automated tests cover ingestion, idempotency, rejection, rendering, and escaping.
- [x] The full demo runs using Python's standard library and SQLite only.

## Assumptions

- Agents exchange small CSV/JSON files through the repository filesystem.
- SQLite has one controlled writer; agents never open it directly.
- Static generation is sufficient for human review at the current scale.
- A later coordinator can queue many read/research jobs while serializing only the short merge operations.

## Threat and risk notes

- CSV formula text, HTML, URLs, and source prose are untrusted and must be escaped or validated.
- Hashes establish payload identity, not truth.
- Primary-source marketing claims still require evidence-aware interpretation.
- A deterministic build can consistently reproduce an incorrect record; review status must remain prominent.
- File-based coordination needs recovery rules for abandoned, duplicated, or partially completed runs.

## Validation steps

1. Run unit tests against temporary databases and output folders.
2. Run the pipeline twice against the same inputs and compare counts/output hashes.
3. Submit an intentionally malformed fixture and confirm the database remains unchanged.
4. Open generated pages locally and follow the index-to-batch-to-record-to-source path.
5. Confirm no imported entity receives canonical status and no relationship is created by staging imports.
