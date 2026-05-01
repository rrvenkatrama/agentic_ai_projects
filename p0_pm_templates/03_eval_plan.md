# [Feature Name] — Eval Plan

**Author:** Rajesh Ramani · **Date:** YYYY-MM-DD

## What we're evaluating

[Specific AI behavior — e.g., "Churn prediction accuracy on 6-month historical data"]

## Eval Dataset

| | |
|---|---|
| **Source** | [Production data / synthetic / curated golden set] |
| **Size** | [N examples — minimum to be statistically meaningful] |
| **Sampling strategy** | [random / stratified / adversarial] |
| **Labels** | [Who labels? Manual / automatic / both?] |
| **Refresh cadence** | [How often will dataset be updated?] |

## Success Metrics & Thresholds

| Metric | Target | Threshold (ship?) | Floor (kill?) |
|---|---|---|---|
| [Primary — e.g., precision] | 70% | ≥60% | <40% |
| [Secondary — e.g., recall] | 50% | ≥40% | <25% |
| [Latency] | <2s p95 | <5s p95 | >10s p95 |
| [Cost / call] | <$0.10 | <$0.30 | >$1.00 |
| [Hallucination rate] | <2% | <5% | >10% |

## Eval Frameworks Used

- [ ] **Ragas** (RAG-specific: context precision, faithfulness, answer relevancy)
- [ ] **DeepEval** (LLM unit tests — assert_relevancy, assert_factual)
- [ ] **Promptfoo** (A/B test prompts side-by-side)
- [ ] **LangSmith** (trace-based evaluation, dataset evals)
- [ ] **Custom evaluators** (domain-specific)

## Regression Suite

- Run on every commit / PR
- Fails the build if metrics drop > X% from baseline
- Specific tests:
  - [ ] [Test 1 — golden output for canonical query]
  - [ ] [Test 2 — adversarial prompt injection]
  - [ ] [Test 3 — edge case behavior]

## Production Monitoring (after ship)

| Signal | How we monitor | Alert threshold |
|---|---|---|
| [Quality drift] | [Daily eval against fresh sample] | [>5% drop triggers review] |
| [Cost spike] | [Per-tenant daily cost] | [>2× baseline triggers alert] |
| [Latency] | [p95 / p99 dashboards] | [Above SLA] |
| [User-reported errors] | [Thumbs down rate] | [>5%] |

## Iteration Plan

- **Week 1:** Baseline eval — establish current performance
- **Week 2-4:** Prompt iteration — A/B test 5+ variants in Promptfoo
- **Week 5+:** Model selection (Claude vs GPT-4o vs Gemini) cost/quality trade-off
- **Continuous:** Weekly review of regression results

---

*If you can't measure success, you can't ship the feature.*
