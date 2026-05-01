# [Capability] — Buy vs Build Analysis

**Author:** Rajesh Ramani · **Date:** YYYY-MM-DD

## Decision

**Recommendation:** [BUY / BUILD / HYBRID]
**Confidence:** [High / Medium / Low]
**Decision date:** [When this needs to be locked]

## What we need (the capability)

[1 paragraph — what problem are we trying to solve. Be specific about the OUTCOME, not the technology.]

## Options Evaluated

### Option 1 — BUY [vendor/product name]

| | |
|---|---|
| **Cost (Year 1)** | $[total — license + integration + training] |
| **Cost (Year 3)** | $[3-year TCO] |
| **Time to value** | [weeks to first usable result] |
| **Customization** | [low / medium / high — what's locked, what's flexible] |
| **Risks** | [vendor lock-in, pricing changes, deprecation, integration debt] |
| **Strengths** | [what they're good at — usually best-in-class for narrow capability] |

### Option 2 — BUILD in-house

| | |
|---|---|
| **Cost (Year 1)** | $[engineer-months × loaded cost + infra] |
| **Cost (Year 3)** | $[Y3 TCO including maintenance] |
| **Time to value** | [weeks to first MVP] |
| **Customization** | High — we own everything |
| **Risks** | [scope creep, ongoing maintenance, team turnover, opportunity cost] |
| **Strengths** | [strategic IP, perfectly tailored, no vendor dependency] |

### Option 3 — HYBRID (if applicable)

[Buy core + build differentiation on top, or buy now + build later]

## Decision Framework

| Criterion | Weight | Buy score | Build score | Why |
|---|---|---|---|---|
| Strategic differentiation | High / Med / Low | 1-5 | 1-5 | [Is this part of our moat?] |
| Time to market | High / Med / Low | 1-5 | 1-5 | [How fast do we need this?] |
| Total cost of ownership | High / Med / Low | 1-5 | 1-5 | [3-year cost view] |
| Team capacity | High / Med / Low | 1-5 | 1-5 | [Do we have the engineers?] |
| Vendor risk | High / Med / Low | 1-5 | 1-5 | [Lock-in, pricing, deprecation] |
| Quality bar | High / Med / Low | 1-5 | 1-5 | [Will buy meet our quality needs?] |
| **Total** | | [score] | [score] | |

## The Tipping Question

> "If we built this and got it wrong, would it kill the company?
> If we bought this and the vendor disappeared, would it kill the company?"

[1 paragraph answering both directions]

## Recommendation Rationale

[3-4 sentences. Why this option, what we're trading off, what we'll watch for.]

## Reversibility Plan

**If we BUY:** [Exit strategy — how do we extract data and migrate if needed?]
**If we BUILD:** [Sunset strategy — under what conditions would we switch to a vendor?]

---

*Buy commodity. Build differentiation. Hybrid the rest.*
