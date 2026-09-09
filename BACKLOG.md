# Structura backlog

This file holds non-blocking discoveries. An entry is not permission to implement it. Move work into [CURRENT_MILESTONE.md](CURRENT_MILESTONE.md) only through an explicit milestone decision.

## Product and data

- **Run the real-person explorer trial.** Three sessions and the task script remain pending in `docs/usability-trial.md`. Use observed failures to choose later navigation or modelling work.
- **Define the canonical promotion procedure.** The schema has status fields and `review_events`, but the complete human approval transaction and policy for ontology promotion still need a future milestone.
- **Resolve selected historical identity/event questions.** OverDrive product identity, Xeon 450 shipment status, and other open audit findings remain visible; choose a bounded subset rather than treating all findings as one task.
- **Choose code, data, and contribution licences before accepting contributions or encouraging reuse.** The repository is publicly visible without an open-source/data licence; `NOTICE.md` records the current boundary. A future contribution milestone should also cover image rights, takedown handling, governance, and redistribution.

## Validation hardening

- **Bind normalized source/qualification choices to independent review.** The final connected-object audit found that a future normalized packet could pair assessed values with another registered source or contradictory comparison limits. The current packet is correct. Evidence: `research_batches/connected-970-evo/jobs/audit-004/runs/audit-20260909-final-01/audit.json`.
- **Bind or derive diagram labels.** A future packet can keep a valid component endpoint while supplying a misleading display label. The current three labels are correct. Consider deriving labels from controlled entity display data in a dedicated milestone.

## Later architecture questions

- Define backup and rollback procedures before the SQL corpus becomes difficult to rebuild.
- Revisit PostgreSQL or graph projection only when concurrency or traversal requirements are demonstrated. SQLite remains authoritative today.
- Threat-model accounts, write-capable contributions, or authentication before adding them. The current public site is generated, static, and read-only.

Keep entries concise: discovery, impact, evidence/location, and the condition that would justify scheduling it.
