# PM Artifact Templates — Path B (AI PM Track)

These are lean/Agile PM artifact templates used alongside engineering projects (P7-P12).
Every artifact is **1 page max** — that's the discipline.

## Templates in this folder

| Template | When to use | Length |
|---|---|---|
| `01_one_page_prd.md` | Every product / feature | 1 page |
| `02_icp.md` | Before sales/marketing motion | 1 page |
| `03_eval_plan.md` | Every AI feature | 1 page |
| `04_gtm_brief.md` | Before launch | 1 page |
| `05_risk_register.md` | Before launch / for compliance | 1 page |
| `06_working_backwards.md` | Early discovery, forces clarity | 1 page (PR-style) |
| `07_buy_vs_build.md` | Before committing to build | 1 page |

## Workflow per project (P7-P12)

Each project gets a dedicated Kanban ticket (#81-#86) with the PM artifacts list.
After the engineering work is done:

1. Copy relevant templates into `pX_xxx/pm/` folder
2. Fill them in based on the project we built
3. Review together for AI-PM-specific framing (eval criteria, cost-per-task, hallucination budget, etc.)

## Why these specific templates

These reflect modern AI PM practice — Marty Cagan / Lenny Rachitsky / Working Backwards influenced.
Skipping waterfall artifacts (long PRDs, Gantt charts, detailed financial models, PMP risk matrices).

## What artifacts each project gets

| Project | PRD | ICP | Eval | GTM | Risk | Working Backwards | Buy-vs-Build |
|---|---|---|---|---|---|---|---|
| P7 Customer Health | ✅ | ✅ | ✅ | ✅ | — | — | — |
| P8 PII Compliance | ✅ | ✅ | ✅ | — | ✅ | — | — |
| P9 Account Memory | ✅ | ✅ | ✅ | ✅ | — | ✅ | — |
| P10 AgentPlatform | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| P11 Contract Analyzer | ✅ | ✅ | ✅ | ✅ | ✅ | — | — |
| P12 Framework Showdown | — | — | — | — | — | — | ✅ (decision framework) |

P12 is more of a research/comparison project — its PM artifact is a decision framework + LinkedIn blog post.
