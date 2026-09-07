# Research Criteria v0.1 — Draft From CPU Scout 01

Status: **candidate criteria for review**. These rules are not yet a locked research policy.

## What

These criteria define what a researcher must record before a historical hardware candidate can advance beyond scouting.

## Why

The first 1998 CPU sample showed that product identity and release timing are more ambiguous than a flat `manufacturer, model, year` row suggests. The criteria keep that ambiguity visible and comparable.

## How

### 1. Define the census event

Every inclusion must state which event places the product in scope:

- announced
- introduced
- first shipped
- shipped in volume
- available in systems
- available as a component
- available boxed/retail
- documented as commercially present

Do not collapse these events into a generic release date.

### 2. Preserve date precision

Allowed evidence precision should include exact day, month, quarter, year, bounded range, and unknown. A quarter-only statement stays quarter-only. A source published later may support an earlier interval without creating an exact date.

### 3. Separate family, variant, and SKU

Record whether the source identifies:

- brand
- product family
- named model or speed grade
- configuration variant
- orderable SKU or part number

Do not apply a family launch date to each model. Do not treat clock frequency as an ordering part number.

### 4. Preserve manufacturer wording

Store the source's exact product wording separately from normalized display names and aliases. Meaningful suffixes such as `300A` must survive normalization.

### 5. Scope availability

Record market segment, geography, channel, and platform where the source supports them. System availability, OEM component availability, and boxed retail availability may differ.

### 6. Distinguish source count from independence

Two company publications repeating the same announcement are not two independent confirmations. Record publisher/origin, publication date, contemporary versus retrospective status, and whether the source adds new evidence.

### 7. Require event-level evidence

Identity evidence does not automatically prove release timing. Each material field—identity, manufacturer, classification, event date, configuration, and market scope—should be traceable to a source locator or concise evidence note.

### 8. Preserve contradictions and absence

Conflicting dates remain separate assertions until reviewed. Failure to locate a part number or launch-speed list is `unknown`, not evidence that none existed.

### 9. Keep conclusions out of census records

Compatibility, performance, openness, repairability, scarcity, and market-control conclusions require their own evidence and later criteria. Marketing claims may be recorded as attributed claims, not database conclusions.

### 10. Make completeness measurable

Each batch needs a declared population boundary and stopping rule. A launch cohort, commercially present census, regional retail census, and manufacturer-announced list are different datasets.

## Candidate acceptance gate

A scout record is ready for verification when it has:

- a stable candidate key
- raw manufacturer and product wording
- a declared entity granularity guess
- at least one in-scope event claim
- the event's evidence precision
- market/channel scope where known
- at least one source URL and evidence note
- explicit unknowns and conflicts

## Questions created by the pilot

1. Is the first dataset a **1998 launch cohort** or a **full commercially-present 1998 census**?
2. Should different cache configurations at one frequency be variants beneath one model, or separate product records?
3. Do we want product events as first-class rows before verification begins?
4. Should `quarter` become an explicit date precision, or should quarters remain bounded ranges?
5. Which event qualifies a product for the public-facing year navigation?
