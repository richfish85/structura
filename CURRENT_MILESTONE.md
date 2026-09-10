# Current milestone

Status: **complete**

Milestone: **Simplified user-testing handouts**

Owner decision: 2026-09-10

## Scope

Create short, separable instructions for three participant groups: current explorer users, PC-pathway concept testers and phone-pathway concept testers. Keep facilitator guidance and expected-answer material outside participant handouts. Correct the existing trial's obsolete localhost-only instruction.

## Acceptance criteria

- [x] A facilitator can select and distribute one handout without additional explanation.
- [x] The live group tests only features currently published.
- [x] PC and phone groups are clearly labelled as concept tests for planned features.
- [x] Instructions avoid collecting names, contact details, account details, serial numbers or device identifiers.
- [x] Each group returns comparable, concise feedback.
- [x] Links resolve and one final documentation review is complete.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `docs/usability-trial.md`
- `docs/user-testing/README.md`
- `docs/user-testing/group-a-live-explorer.md`
- `docs/user-testing/group-b-pc-pathway.md`
- `docs/user-testing/group-c-phone-pathway.md`
- `docs/user-testing/response-template.md`

No application, schema, research, test, generated-site or deployment changes are allowed.

## Tests

After integration, run once:

1. Verify relative Markdown links resolve.
2. Check that participant handouts do not contain observer answers or request identifying information.
3. Run `git diff --check`.
4. Perform one final scope and consistency review.

## Delegation rules

No delegation. This is a bounded documentation milestone.

## Stop conditions

Stop when the acceptance criteria are met and mark the milestone complete. Do not contact participants, record invented results, build prototypes or start pathway implementation.
