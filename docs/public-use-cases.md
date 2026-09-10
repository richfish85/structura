# Locked public use cases

Status: **product direction approved; not implemented**

These are entry pathways into Structura's shared hardware record. They do not own separate facts or become separate products.

## Shared promise

**Choose what you own, choose what you want to do, see what the evidence establishes, and follow the hardware path behind the answer.**

Every pathway follows the same sequence:

```text
identify device(s) -> choose intent -> bounded result
                   -> visual relationship path
                   -> evidence, constraints and unknowns
```

Results must be derived from versioned entities, relationships and claims in SQL. They carry an `as of` date and never infer a blanket compatibility statement from connector shape, marketing name or one component alone.

## Use case 1: Can I keep this PC?

**2026 scenario:** A non-specialist has a working Windows 10 PC and wants to understand its Windows 11 readiness before configuring, upgrading or replacing it.

**Inputs**

- Exact PC model or a bounded sample configuration.
- Relevant installed configuration when it can differ from the model baseline.
- User intent: understand Windows 11 readiness.
- Optional observed result from Windows PC Health Check; user observation remains distinct from sourced product data.

**Result vocabulary**

- `requirements evidenced as met`
- `configuration check needed`
- `replaceable component may block readiness`
- `platform requirement not met`
- `unknown or conflicting evidence`

The explanation identifies each applicable requirement, the tracked hardware or setting related to it, and the source supporting the conclusion. It distinguishes capability from enabled state and minimum eligibility from suitability or performance.

**Evidence boundary**

Use current Microsoft requirements and processor policy, manufacturer model/configuration documentation, and attributable observations. Date the policy snapshot. Do not claim that Microsoft will offer an upgrade, that an undocumented firmware setting exists, or that changing hardware guarantees eligibility.

**Not promised**

- Installation instructions, bypasses or security advice.
- A general PC performance score.
- Purchase, replacement or disposal recommendations.
- Coverage of every shipped configuration under a family name.

## Use case 2: Will this phone charging setup do what I expect?

**Scenario:** A smartphone user wants to combine a phone, charger and cable for ordinary charging or a named fast-charging mode.

**Inputs**

- Exact phone model and relevant region or revision when required.
- Exact charger model and port.
- Exact cable or an explicitly unknown cable.
- User intent: charge or use a named fast-charging capability.

**Result vocabulary**

- `physical connection fits`
- `ordinary charging evidenced`
- `named fast-charging mode evidenced`
- `works with a documented limit`
- `required capability missing`
- `unknown or conflicting evidence`

The explanation shows the complete phone–cable–charger path. Connector, protocol, power profile, cable rating and device limit remain separate facts. The weakest or unknown link constrains the result.

**Evidence boundary**

Use manufacturer model documentation, applicable standards and certification records where available. Treat advertised maximums as conditional claims. Do not infer cable capability from appearance or USB-C shape, and do not call an unverified combination safe.

**Not promised**

- Charger rankings or shopping recommendations.
- Predicted charge time or battery-health outcome without suitable evidence.
- Authentication of unmarked or counterfeit accessories.
- Data, display or docking compatibility in the first slice.

## Shared acceptance rule

A pathway is useful only if a new user can reach a result, explain the decisive relationship and open its evidence without learning Structura's internal vocabulary. `Unknown` is a valid result. A plausible but unsupported answer is a failure.
