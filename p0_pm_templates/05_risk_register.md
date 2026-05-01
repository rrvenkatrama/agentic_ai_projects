# [Product Name] — Risk Register

**Author:** Rajesh Ramani · **Date:** YYYY-MM-DD

## Top 5 Risks (ranked by impact × probability)

### Risk 1: [Name — e.g., "Hallucination on regulatory advice"]

| | |
|---|---|
| **Impact** | Critical / High / Med / Low + 1-line description of what breaks |
| **Probability** | High / Med / Low + why we think so |
| **Detection** | How we'd notice (eval drift, user complaints, monitor) |
| **Mitigation (preemptive)** | What we do BEFORE launch to reduce risk |
| **Response (reactive)** | What we do IF it happens (kill switch, rollback, comms) |
| **Owner** | Who is responsible |

### Risk 2: [Name]
[Same structure]

### Risk 3: [Name]
[Same structure]

### Risk 4: [Name]
[Same structure]

### Risk 5: [Name]
[Same structure]

## AI-Specific Risk Categories (consider each)

| Category | Common risks |
|---|---|
| **Hallucination** | Made-up facts, fabricated citations, wrong calculations |
| **Cost runaway** | Recursive tool calls, unbounded loops, rate-limit retries |
| **Latency** | Multi-step agents timing out, cold-starts, model queuing |
| **Privacy / PII leakage** | User data ending up in prompts, logs, embeddings |
| **Prompt injection** | User input that overrides system prompt, exfiltrates data |
| **Bias / fairness** | Model outputs differ by user demographic |
| **Model deprecation** | Underlying API model retired, breaking behavior change |
| **Vendor lock-in** | Built on proprietary API with no exit path |
| **Compliance** | GDPR data retention, SOC2 logging, HIPAA PHI handling |
| **Reputation** | Public failure mode → social media incident |

## Kill Switches (production safety)

- [ ] Per-tenant rate limiting (cap tokens / requests per day)
- [ ] Daily budget alerts + auto-pause at threshold
- [ ] Manual override / "stop all agents" button
- [ ] Eval-driven auto-rollback (if quality drops > X%)
- [ ] Confidence threshold gating (block low-confidence outputs from auto-execution)

## Acceptable Trade-offs (explicit)

- "We accept [X% error rate] in exchange for [benefit]"
- "We accept [latency Y] in exchange for [cost saving]"
- "We accept [feature limitation] to ship in [timeframe]"

These should be **written down and agreed** with stakeholders, not buried.

---

*Risk-driven PM is honest PM. Pretending nothing will go wrong is how products get killed.*
