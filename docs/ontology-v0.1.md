# Hardware Ontology v0.1 — Proposed

## What

This is a working vocabulary for testing real hardware records. Every type and predicate is `proposed`, not locked canon.

## Why

The OSI model describes network communication well but does not fully express physical mounting, electricity, power, thermal behaviour, control, containment, replaceability, manufacturing, standards, ownership, or constraint. Structura treats OSI as one view within a broader system graph rather than inventing a taller layer stack.

## How

### Proposed entity types

Product, product family, company, component, category, interface, protocol, standard, form factor, organization, software, and firmware.

### Proposed relationship families

| Family | Initial predicate examples | Question it should answer |
|---|---|---|
| Classification | `INSTANCE_OF` | What kind of thing is this? |
| Physical | `OCCUPIES`, `CONTAINS` | Where is it and what is inside it? |
| Mechanical | `CONFORMS_TO` | What shape, mount, or keying does it follow? |
| Power | `RECEIVES_POWER_FROM` | Where does its electrical power originate? |
| Signal/protocol | `CONNECTS_VIA`, `COMMUNICATES_USING`, `IMPLEMENTS` | How do signals and commands cross boundaries? |
| Logical/control | `EXPOSES`, `CONTROLLED_BY`, `REQUIRES` | What controls or depends on it? |
| Compatibility | `COMPATIBLE_WITH`, `REPLACEABLE_WITH` | Under what stated scope can it work or substitute? |
| Manufacturing/integration | `MANUFACTURED_BY`, `DESIGNED_BY`, `INTEGRATES` | Who made/designed it and which functions are combined? |
| Ownership/constraint | `OWNED_BY`, `LICENSED_BY`, `RESTRICTED_BY` | Which entity controls or limits it? |
| Standardisation | `STANDARDIZED_BY` | Which institution maintains the relevant specification? |

### Flows the model may need to represent

Data, power, control, thermal, and mechanical relationships are distinct. `CONNECTS_VIA` is deliberately provisional because it may become too vague when physical, electrical, and signal relationships are tested.

## Open ontology questions

- What distinguishes a sellable product, product family, chip, board, and configuration?
- Should physical, electrical, and signal connections receive separate predicates immediately?
- How should compatibility scope encode firmware version, region, revision, and configuration?
- Is replaceability a direct relationship or a conclusion derived from compatible constraints?
- How should thermal paths and measurements be represented?
- Which facts belong in typed product columns versus relationship assertions?
- How should time-bound ownership, licensing, and supplier relationships be modelled?
