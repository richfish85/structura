# Current milestone

Status: **complete**

Milestone: **Lock public use cases and pathway plan**

Owner decision: 2026-09-10

## Scope

Define two public entry pathways into Structura—the 2026 PC lifecycle question and the phone charging/capability question—and plan their implementation. Preserve Structura as the definitive evidence-backed hardware tracker: the pathways are derived views over shared SQL knowledge, not separate comparison products.

## Acceptance criteria

- [x] The product brief states the tracker, visual-confirmation and immediate-use layers.
- [x] Both use cases have a fixed audience, question, input, result vocabulary, evidence boundary and non-goals.
- [x] A shared interaction and data contract prevents duplicated pathway-specific truth.
- [x] The implementation plan defines bounded stages, dependencies, acceptance gates and stop conditions.
- [x] The decision is recorded and all new references resolve.
- [x] One documentation check and one final review pass are complete.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `docs/product-brief.md`
- `docs/public-use-cases.md`
- `docs/pathway-implementation-plan.md`
- `docs/decision-log.md`
- `BACKLOG.md` only for non-blocking discoveries

No schema, application, research packet, test, generated site or deployment changes are allowed.

## Tests

After integration, run once:

1. Verify every relative Markdown link in the changed documents resolves.
2. Search the changed documents for conflicting product claims and deprecated pathway names.
3. Run `git diff --check`.
4. Perform one final scope and consistency review.

## Delegation rules

No delegation. This is a bounded documentation milestone.

## Stop conditions

Stop when the acceptance criteria are met and mark this milestone complete. Do not implement schema changes, evaluators, visual components, pathway pages or new research packets.
