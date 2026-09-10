# Public pathway implementation plan

Status: **approved sequence; implementation not started**

## Principle

Build one reusable intent-to-evidence path over the SQL authority. PC and phone screens may use different language, but they must share identity, relationship, constraint, evidence, status and result rules. Do not create hand-written verdict pages or independent compatibility tables.

## Stage 0 — Baseline the explorer

Run the existing [real-person trial](usability-trial.md) against the published connected explorer. Record navigation and evidence-comprehension failures before changing the shared visual language.

**Gate:** Three sessions are recorded and repeated failures are identified. Stop if users cannot distinguish a device, component, relationship and evidence source; repair that foundation before pathway work.

## Stage 1 — Define the shared decision contract

Work two complete examples on paper and against the current schema: one PC configuration and one phone–charger–cable combination. Define the minimum representation for:

- user intent and supplied observations;
- applicable requirement or desired capability;
- device, component, port, protocol and policy identities;
- constraints such as version, region, firmware state, power profile and cable rating;
- evidence-backed atomic findings;
- deterministic result category, explanation and `as of` date.

Prefer derived findings over a coarse stored `COMPATIBLE_WITH` assertion. Propose schema or ontology changes only after both examples expose the same missing concept.

**Gate:** The same contract expresses both worked examples without pathway-specific truth stores or unsupported inference.

## Stage 2 — Prove visual confirmation

Create one reusable relationship-path view using the current SSD example first. It must show selected object, related parts or standards, direction of each relationship, evidence state and unresolved links. Detailed language remains behind progressive disclosure, with a text equivalent for every visual.

**Gate:** New users can identify the decisive relationship and its evidence. Diagram position is never interpreted as a physical-layout claim.

## Stage 3 — Build two bounded evidence packets

Research through the existing scout, verifier, normalizer, auditor and human-review boundary.

- **PC slice:** three configurations covering a configuration check, a replaceable-component question and a platform limitation or documented unknown.
- **Phone slice:** two phones, two chargers and three cables covering ordinary charging, one named fast-charging success, one documented limit and one unknown cable.

Select examples for evidence quality and distinct reasoning paths, not brand coverage. Keep policy versions and regional/model variants explicit.

**Gate:** Every displayed finding traces to evidence; every missing decisive fact produces `unknown` rather than a guessed verdict.

## Stage 4 — Implement the shared pathway shell

Add a task-first entry: identify device(s), choose intent, view result, expand the visual path, then inspect evidence. Implement the result engine as deterministic queries over the authoritative snapshot. Render static, shareable result examples before considering accounts, live device detection or user submissions.

**Gate:** Both pathways use the same evaluator and visual components. Rebuilding from the frozen manifest reproduces the pages and result categories.

## Stage 5 — Test immediate usability

Run five short sessions per pathway with people unfamiliar with the model. Test whether they can:

1. select the intended devices and task;
2. find the decisive constraint within two minutes;
3. distinguish fit, capability, enabled state and observed behavior;
4. open the supporting evidence;
5. explain the result without database terminology;
6. recognize an unknown without converting it into certainty.

**Gate:** At least four of five participants per pathway complete the core explanation unassisted. Any repeated serious misconception blocks expansion.

## Stage 6 — Expand from observed demand

Add the smallest relationship or product set needed by repeated user questions. Candidate extensions include PC repairability and upgrade paths, then phone data, display, wireless charging and docking capabilities. Coverage counts, rankings, commerce and community features require separate milestones.

Evidence-gathering quests, gamified participation and object-centred community features are exploratory later increments in the repository [roadmap](../ROADMAP.md). They must not be folded into pathway delivery without separate evidence-governance, privacy, abuse and moderation decisions.

## Milestone order

1. Existing explorer trial.
2. Shared decision contract and schema-gap proposal.
3. Reusable visual relationship path.
4. Bounded PC and phone research packets.
5. Shared pathway shell and deterministic evaluation.
6. Two real-person trials and evidence-led refinement.

Each item is a separate milestone with its own allowed files, tests and stop condition. Do not begin the next automatically.
