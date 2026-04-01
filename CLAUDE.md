# AI Engineer Program — Claude Context

## What This Is
A project-based 4-month self-training curriculum to become an Agentic AI Engineer.
Claude acts as trainer/guide — building every project together, explaining concepts inline.
No passive video courses — learning by doing, with deeplearning.ai shorts on-demand as needed.

## The Person
- Rajesh Ramani, 54, program manager background (infrastructure domain, Apple)
- CS degree 1989, languages: C, C++, PHP, decent Python, web apps
- AWS Certified Solutions Architect Associate
- 15+ years away from core dev, returning now
- Real-world agentic work at Onemyle startup (augments this training)
- Goal: Agentic AI Engineer positions within 4 months (by ~July 2026)

## Kanban Tracking
- Tool: MyKanban at http://192.168.1.150:3002
- Project: "AI Engineering Readiness" (Project ID: 3)
- Login: rajramani@msn.com / yanni123
- All 31 tickets created (IDs #17–#47)
- Move tickets: Backlog → Todo → In Progress → Done as work progresses

## Python Environment
- Repo: ~/ai/ai_engineer_program/
- Venv: ~/ai/ai_engineer_program/.venv/
- Activate: source .venv/bin/activate
- Keys: copy .env.example to .env, add ANTHROPIC_API_KEY etc.

## The 8-Project Curriculum

| # | Folder | Project | Key Tech | Kanban Tickets | Month |
|---|--------|---------|----------|----------------|-------|
| P1 | p1_toolbot | ToolBot — CLI agent with tools | async Python, Pydantic v2, Claude tool_use, streaming | #17–20 | 1 |
| P2 | p2_doctalk | DocTalk — PDF Q&A with citations | Embeddings, chunking, Chroma, RAG, LangChain | #21–24 | 1 |
| P3 | p3_researchbot | ResearchBot — multi-step web research | LangGraph, checkpointing, human-in-loop, Redis | #25–28 | 2 |
| P4 | p4_stocksage | StockSage — stock analysis agent | Multi-agent, yfinance, Finnhub, RAG, LangGraph | #29–33 | 2–3 |
| P5 | p5_reviewcrew | ReviewCrew — GitHub PR code reviewer | CrewAI, role-based agents, GitHub API | #34–36 | 3 |
| P6 | p6_mcp | MCP++ — extend Onemyle MCP server | MCP spec, SSE, resources, prompt templates | #37–39 | 3 |
| P7 | p7_observable | ObservableAgent — observability + evals | LangSmith, LangFuse, eval harnesses | #40–42 | 3 |
| P8 | p8_platform | AgentPlatform — production deploy | Docker, k3s, GitHub Actions CI/CD | #43–45 | 4 |

## Concepts Covered (by project)
- P1: async/await, Pydantic v2, tool_use loop, streaming, system prompts, context management
- P2: embeddings, cosine similarity, chunking strategies, RAG pipeline, LangChain abstractions
- P3: LangGraph StateGraph, typed state, nodes/edges, checkpointing, human-in-the-loop
- P4: multi-tool orchestration, structured output, domain RAG, agent synthesis, financial APIs
- P5: CrewAI agents/tasks/crew, agent specialization, parallel execution, hierarchical agents
- P6: MCP spec, SSE transport, tool schemas, resource protocol, prompt templates
- P7: LangSmith tracing, span hierarchy, eval datasets, evaluator functions, LangFuse dashboards
- P8: Docker multi-stage builds, k8s manifests, secrets management, GitHub Actions

## Training Resources (on-demand, not upfront)
| Course | Platform | When to use |
|--------|----------|-------------|
| LangChain for LLM Application Development — Andrew Ng | deeplearning.ai | Before P2 |
| AI Agents in LangGraph | deeplearning.ai | Before P3 |
| Multi-Agent Systems with CrewAI | deeplearning.ai | Before P5 |
| Evaluating and Debugging Generative AI | deeplearning.ai | Before P7 |
| Complete Agentic AI Engineering Course | Udemy (owned) | Reference throughout |

## LLM Coverage
All three major LLMs are used across the curriculum — not Claude-only:
- **Anthropic Claude** (claude-opus-4-6) — primary, tool_use, MCP
- **OpenAI** (gpt-4o) — function calling, comparison patterns
- **Google Gemini** — function calling, multi-modal
All three API keys are in .env: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY

## Claude's Role as Trainer
- Give Rajesh coding goals — let him write the code, then review and correct inline
- Do NOT scaffold everything — only scaffold to unblock, not replace the learning
- Explain every concept as it appears in real code (not abstract)
- Give daily tasks sized for ~2–3 hours of focused work
- Point to deeplearning.ai shorts only when concept needs lecture reinforcement
- Move Kanban tickets as milestones are hit
- Run a 5–8 question quiz at end of EVERY project before moving to the next one
- Weekly plan tickets: #46 (Week 1), #47 (Week 2) — add more each week

## Training Style (Non-negotiable)
1. **Interactive coding** — Give a goal + any needed context/signature. Rajesh writes it. Review after.
2. **End-of-project quiz** — Before starting next project, quiz on concepts from the one just completed.
   Questions should reference actual code from the project, not abstract theory.

## Daily Plan Structure
Each session: Claude gives the day's task, Rajesh codes it, concepts explained inline.
Weekly plan tickets in Kanban track the week's goals.

## Current Status (as of 2026-03-30)
- [x] Repo created, venv set up, workspace file created
- [x] Kanban project + 31 tickets created
- [x] .env created with ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY
- [x] Dependencies installed: anthropic, openai, google-generativeai, pydantic, python-dotenv
- [x] P1 ToolBot — IN PROGRESS (Ticket #17)
  - [x] Phase A (Claude): agent.py with tool loop — DONE (2026-03-30)
  - [x] Phase A+: Add streaming to agent.py — DONE (2026-03-30)
  - [x] Phase B: OpenAI function calling version — DONE (2026-03-31)
  - [x] Phase C: Gemini function calling version — DONE (2026-03-31)

## Related Projects
- Onemyle / reel-analysis-lib: ~/ai/Onemyle/reel-analysis-lib (real-world agent deployment)
- MyKanban: ~/ai/mykanban (the Kanban tool used to track this program)
- Onemyle MCP server: related to P6 MCP++ project
