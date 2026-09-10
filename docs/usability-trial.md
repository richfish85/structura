# First Connected Explorer — real-person trial

Status: **not run**. No participant results have been recorded. Automated checks are documented separately.

## What

A 10–15 minute session with three people who have not helped build the explorer. Richard can take one slot if useful; record prior familiarity so that result is not mistaken for a new-user result. Use participant labels P1, P2 and P3; names and contact details are unnecessary.

## Why

We need to know whether people can find hardware, understand a relationship and notice an evidence limit without a guided explanation. This is a small formative trial, not proof of general usability or learning effectiveness.

## How

Send the participant the simplified [Group A handout](user-testing/group-a-live-explorer.md) and [response template](user-testing/response-template.md). Use the published reference at https://richfish85.github.io/structura/. No participants have been contacted by the agent.

Read only: "This is a working hardware reference. Please say what you are looking for and what you expect to happen. We are testing the site, not you."

Give these tasks one at a time. Do not explain the route or vocabulary in advance. Stop a task after about three minutes or if the participant wants to stop. If you give a hint, record it as assisted.

1. Find the Intel Celeron 300A in the 1998 material. Explain what it was intended for and find the evidence behind one performance result.
2. Open the Samsung 970 EVO 500 GB. Find its controller, then find what evidence connects that controller to the SSD.
3. Explain what M.2, PCIe and NVMe mean in this example. Does seeing one of those labels establish that the drive works in any similarly named slot?
4. Compare the 500 GB and 1 TB models. Name one difference and one condition attached to the performance figures.
5. Find something the reference does not yet establish. Explain what would be needed to resolve it.

Finish with: "What was hardest to find? What would you expect to do next?"

## Observer reference — do not show before the tasks

1. The Celeron dossier includes Basic PC purpose and SPEC CPU95 results with configuration and source disclosures. A generic CPU score or unsupported cache-speed causal conclusion is not the intended answer.
2. Phoenix is the documented controller designation. Its incoming relationship or the SSD's contains arrow leads to the manufacturer datasheet, page locator, scope and provisional assessment.
3. Physical format, interface and command protocol are separate. The current example makes no blanket host-compatibility assertion.
4. DRAM capacity and listed sequential-write rates differ; manufacturer up-to figures depend on TurboWrite and test conditions. Reads are listed at the same rate.
5. Exact NAND/DRAM package counts, markings and positions for a specific production revision remain unknown. Revision-matched assembly evidence or an attributable teardown would be needed.

## Results — blank until observed

| Participant | Prior familiarity / device | Task | Outcome: unassisted, assisted, failed or skipped | Approx. time | Exact confusion or observation | Hint given |
|---|---|---|---|---|---|---|
| Pending | | | | | | |

For each participant, also record their own explanation of form/interface/protocol, whether they noticed provisional status, and their requested next action. Capture observations before proposing fixes.

## Decision after the trial

- [ ] Three real sessions recorded, including prior familiarity.
- [ ] At least two participants independently find the product, component relationship and its evidence.
- [ ] No observed false certainty about compatibility, physical layout or measured performance is left unaddressed.
- [ ] Repeated navigation failures become the next implementation work.
- [ ] Any change affecting a failed task is checked again with a person.

If these checks fail, the milestone stays open. Do not average away a serious misconception with a task-completion score. Research only the smallest additional claim set needed by a concrete observed question.
