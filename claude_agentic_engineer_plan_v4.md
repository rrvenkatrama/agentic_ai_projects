# Agentic AI Engineer Training Plan — v4
> Rajesh Ramani | Start: 2026-03-30 | Target: ~2026-07-30 | 16 weeks

---

## Goal
Become hireable as an Agentic AI Engineer at mid-to-senior level within 4 months.
Build 11 real projects. Cover all frameworks, protocols, security, deployment, and interview prep.

---

## The Person
- Program manager background (infrastructure domain, Apple)
- CS degree: C, C++, PHP, decent Python, web apps
- AWS Certified Solutions Architect Associate
- Real-world agentic work at Onemyle startup (augments training)
- Local k3s cluster at 192.168.1.156 (control plane)

---

## Training Principles
1. **Hands-on only** — code every concept, no passive watching
2. **All 3 LLMs** — Claude, OpenAI, Gemini across projects
3. **Quiz at end of every project** — before moving to next
4. **Daily tasks** — ~2-3 hours focused work per session
5. **Cheatsheet updated continuously** — interview-ready reference

---

## The 11 Projects

| # | Folder | Project | Key Tech | Kanban | Month |
|---|---|---|---|---|---|
| P1 | p1_toolbot | ToolBot — CLI agent, 3 LLMs | async, Pydantic v2, tool_use, streaming | #17–20 | 1 |
| P2 | p2_doctalk | DocTalk — PDF Q&A + citations | Embeddings, Chroma→Qdrant, RAG, LangChain | #21–24 | 1 |
| P3 | p3_researchbot | ResearchBot — multi-step web research | LangGraph, checkpointing, human-in-loop, A2A intro | #25–28 | 2 |
| P4 | p4_stocksage | StockSage — stock analysis agent | Multi-agent, Mem0 memory, reasoning model selection | #29–33 | 2 |
| P5 | p5_reviewcrew | ReviewCrew — GitHub PR reviewer | CrewAI, OpenAI Agents SDK, parallel execution | #34–36 | 3 |
| P6 | p6_mcp | MCP++ + A2A — Onemyle MCP server | MCP spec, SSE, A2A protocol, agent interoperability | #37–39 | 3 |
| P7 | p7_observable | ObservableAgent — observability + evals | LangSmith, Langfuse, Arize Phoenix, security evals | #40–42 | 3 |
| P8 | p8_security | SecurityGuard — agent security | OWASP LLM Top 10, prompt injection, NeMo Guardrails, memory poisoning | #48 | 3 |
| P9 | p9_memory | MemoryAgent — long-term memory | Mem0, Zep, episodic/semantic/procedural memory, knowledge graphs | #49 | 3–4 |
| P10 | p10_platform | AgentPlatform — production deploy | Docker, k3s (local), AWS Bedrock, Terraform, GitHub Actions | #43–45 | 4 |
| P11 | p11_multimodal | MultiModalBot — vision + audio agent | GPT-4o vision, Gemini multimodal, document analysis, audio pipeline | #50 | 4 |

---

## 16-Week Sprint Plan

### Month 1 — Foundations (Weeks 1–4)

**Week 1** — Tool loops, 3 LLMs, streaming
- P1 ToolBot: Claude (tool_use + streaming), OpenAI (function calling), Gemini (google-genai)
- Concepts: async/await, Pydantic v2, tool loop, streaming, TOOL_MAP pattern
- Kanban: #17, #18, #19

**Week 2** — P1 wrap + embeddings intro
- P1: System prompts, context management, multi-turn memory (#20)
- P1 quiz → P2 start: embeddings theory, first embed API call, manual PDF chunking
- Concepts: system prompts, context window limits, tokenization, cosine similarity
- Kanban: #20, #21

**Week 3** — PDF Q&A + vector DB
- P2 DocTalk: chunking strategies, Chroma pipeline, RAG with LangChain, citations
- Upgrade: Qdrant as production alternative to Chroma
- Concepts: chunking (fixed, semantic, recursive), embedding models, retrieval strategies
- Kanban: #22, #23

**Week 4** — Prompt engineering depth
- P2 complete + standalone prompt engineering module
- Topics: system prompt design, few-shot examples, chain-of-thought, ReAct pattern
- P2 quiz
- Kanban: #24

---

### Month 2 — Orchestration (Weeks 5–8)

**Week 5** — LangGraph stateful agents
- P3 ResearchBot: StateGraph, typed state, nodes/edges, conditional routing
- Concepts: state machines, graph topology, LangGraph vs LangChain
- Kanban: #25, #26

**Week 6** — Human-in-loop + A2A intro
- P3: checkpointing, human-in-the-loop, Redis state persistence
- A2A protocol intro: what it is, MCP vs A2A, when to use each
- P3 quiz
- Kanban: #27, #28

**Week 7** — Multi-agent + memory systems
- P4 StockSage: multi-tool orchestration, yfinance/Finnhub, domain RAG
- Add Mem0 memory layer to agent
- Concepts: Mem0 vs Zep vs LangMem, memory types (working/procedural/semantic/episodic)
- Kanban: #29, #30, #31

**Week 8** — Reasoning model selection + P4 wrap
- P4: structured output, agent synthesis, financial report generation
- Concept: o3 vs Sonnet vs DeepSeek-R1 — cost/performance/latency tradeoffs
- P4 quiz
- Kanban: #32, #33

---

### Month 3 — Advanced Patterns (Weeks 9–12)

**Week 9** — CrewAI + OpenAI Agents SDK
- P5 ReviewCrew: role-based agents, task decomposition, parallel execution
- Build OpenAI Agents SDK version for comparison
- Concepts: hierarchical vs flat multi-agent topologies, token overhead of orchestration
- Kanban: #34, #35, #36

**Week 10** — MCP + A2A depth
- P6 MCP++: extend Onemyle MCP server, SSE transport, resources, prompt templates
- Add A2A protocol: build agent-to-agent communication
- Concepts: MCP spec, tool schemas, resource protocol, A2A task lifecycle
- Kanban: #37, #38, #39

**Week 11** — Observability + evals
- P7 ObservableAgent: LangSmith tracing, span hierarchy, eval datasets
- Add Langfuse (self-hosted) + Arize Phoenix
- Add security-focused evals (prompt injection detection)
- P7 quiz
- Kanban: #40, #41, #42

**Week 12** — Agent security
- P8 SecurityGuard: implement and test prompt injection defenses
- OWASP LLM Top 10 — cover each category with code examples
- NeMo Guardrails integration, Llama Guard basics
- Memory poisoning attack + defense demo
- P8 quiz
- Kanban: #48

---

### Month 4 — Production + Interview (Weeks 13–16)

**Week 13** — Long-term memory systems
- P9 MemoryAgent: build agent with Mem0 persistent memory + Zep episodic memory
- Implement all 4 memory types in a single agent
- Concepts: knowledge graphs, temporal context, memory retrieval strategies
- P9 quiz
- Kanban: #49

**Week 14** — Containers + k3s + GitHub Actions + AWS Bedrock
- P10 AgentPlatform local: Docker multi-stage build, deploy to your k3s cluster at 192.168.1.156
- P10 AWS: deploy same agent to AWS Bedrock AgentCore + Terraform for infra
- GitHub Actions CI/CD pipeline:
  - Cloud-hosted runners: lint, test, build Docker image, push to registry
  - Self-hosted runners on local servers (192.168.1.156 + Mac): pull image and deploy via systemd/k3s
  - Secrets management in GitHub Actions (API keys, SSH keys)
  - Multi-environment workflow: push to main → deploy to local; tag release → deploy to AWS
- Concepts: Terraform basics, Bedrock AgentCore vs self-hosted, self-hosted runner setup, cost modeling
- Kanban: #43, #44, #45

**Week 15** — Multi-modal agents
- P11 MultiModalBot: vision agent with GPT-4o (image analysis, document QA)
- Audio pipeline with Gemini 3.1 Flash Live
- Multi-modal RAG (images + text in same vector store)
- P11 quiz
- Kanban: #50

**Week 16** — Interview intensive
- System design: design a production agentic system end-to-end (whiteboard style)
- Mock interviews: 5 technical questions per day from cheatsheet
- Portfolio review: README files, GitHub polish, talking points for each project
- Interview prep + negotiation prep
- Final cheatsheet review

---

## Missing Topics (Now Covered)

| Topic | Where Covered | Why Critical |
|---|---|---|
| Agent security — OWASP LLM Top 10, prompt injection | P8 | 73% of prod deployments affected; interview topic |
| A2A protocol | P3 + P6 | Equal to MCP importance; 50+ enterprise partners |
| Memory systems — Mem0, Zep, episodic/semantic | P4 + P9 | Highly demanded, differentiator skill |
| AWS Bedrock AgentCore | P10 | Most in-demand cloud AI platform for agent roles |
| Reasoning model selection (o3/DeepSeek-R1) | P4 concept | Employers ask when to use which model and why |
| Qdrant (production vector DB) | P2 | Chroma→Qdrant is the standard dev→prod path |
| OpenAI Agents SDK | P5 | Growing fast; counter to LangChain abstractions |
| Prompt engineering module | Week 4 | Foundation for all senior-level work |
| Multi-modal agents | P11 | $3.85B market, 29% YoY growth |
| Interview prep intensive | Week 16 | Dedicated time, not scattered |

---

## Weekly Concept Deep-Dives

| Week | Topic |
|---|---|
| 1 | Pydantic v2, async patterns |
| 2 | RAG pipeline theory, tokenization |
| 3 | Vector DB selection guide (Chroma/Qdrant/Pinecone/pgvector) |
| 4 | Chain-of-thought, few-shot, system prompt design |
| 5 | StateGraph, typed state, ReAct pattern |
| 6 | A2A vs MCP — protocol comparison |
| 7 | Memory architecture (working/procedural/semantic/episodic) |
| 8 | Reasoning models: o3 vs Sonnet vs DeepSeek-R1 |
| 9 | Multi-agent topologies (hierarchical, flat, debate) |
| 10 | Agent protocol ecosystem (MCP/A2A/ACP) |
| 11 | LLM-as-a-judge, eval datasets, regression suites |
| 12 | OWASP LLM Top 10 taxonomy |
| 13 | Knowledge graphs, temporal memory, Zep architecture |
| 14 | Terraform, Bedrock AgentCore, cost modeling |
| 15 | Multi-modal pipelines, latency optimization |
| 16 | System design patterns for production agentic systems |

---

## Infrastructure Used

| Asset | Project |
|---|---|
| Local k3s at 192.168.1.156 | P10 — deploy agent platform to own cluster |
| AWS SAA certification | P10 — Bedrock + Terraform |
| Onemyle real-world project | P6 MCP++ (direct), P9 memory layer |
| MyKanban app | All projects — dogfood your own tool |

---

## Key Frameworks Covered

| Framework | Project | Tier |
|---|---|---|
| LangChain | P2 | Production leader |
| LangGraph | P3, P4 | Production leader |
| CrewAI | P5 | Production leader |
| OpenAI Agents SDK | P5 | Growing fast |
| MCP | P6 | Non-negotiable |
| A2A | P3, P6 | Non-negotiable |
| Mem0 / Zep | P4, P9 | Differentiator |
| LangSmith / Langfuse / Arize | P7 | Required |
| NeMo Guardrails | P8 | Required |
| AWS Bedrock | P10 | Most in-demand cloud |

---

## Target Job Profile
- Title: Agentic AI Engineer / AI Engineer / LLM Engineer
- Level: Mid to Senior
- Stack: Python, LangGraph/CrewAI, Claude/GPT-4o/Gemini, MCP, A2A, AWS
- Target: Mid to Senior level roles

---

## Phase II — Beyond 4 Months (GPU + Local Model Training)

> Requires: NVIDIA gaming GPU system added as k3s worker node at 192.168.1.156

### Phase II Projects

| # | Folder | Project | Key Tech | Focus |
|---|--------|---------|----------|-------|
| P12 | p12_gpu_cluster | GPUCluster — NVIDIA k3s worker | NVIDIA device plugin, GPU operator, CUDA containers, k3s GPU scheduling | Infrastructure |
| P13 | p13_local_llm | LocalLLM — self-hosted model server | Ollama, vLLM, Llama 3.2 / Mistral / Phi-4-mini, OpenAI-compatible API | Inference |
| P14 | p14_finetune | DocTuner — fine-tune on your documents | Hugging Face transformers, PEFT, QLoRA, Unsloth, Llama 3.2 1B/3B | Training |
| P15 | p15_rag_vs_ft | RAG vs Fine-Tune — benchmark both | Compare P2 RAG pipeline vs P14 fine-tuned model on same document set | Evaluation |
| P16 | p16_nanogpt | NanoGPT — build LLM from scratch | Pure PyTorch, multi-head attention, BPE tokenizer, training loop, text generation | Fundamentals |

---

### P12 — GPUCluster
**Goal:** Add the NVIDIA gaming GPU machine as a k3s worker node and schedule GPU workloads on it.

**What you'll build:**
- Install k3s agent on GPU machine, join cluster at 192.168.1.156
- Install NVIDIA Container Toolkit + NVIDIA device plugin for k3s
- Deploy a test CUDA pod (`nvidia/cuda` image) and verify GPU access inside container
- Configure node labels/taints so GPU pods route to GPU node automatically

**Key concepts:** NVIDIA device plugin, resource limits (`nvidia.com/gpu: 1`), node selectors, GPU operator vs manual install, CUDA version compatibility

---

### P13 — LocalLLM
**Goal:** Run open source LLMs locally on your GPU, served via OpenAI-compatible API.

**What you'll build:**
- Deploy Ollama in a CUDA container on the GPU k3s node
- Serve Llama 3.2 3B, Mistral 7B, Phi-4-mini — all from local GPU
- Compare inference speed, quality, memory usage across models
- Expose via ClusterIP service so other agents in the cluster can call it

**Key concepts:** Ollama vs vLLM, VRAM requirements per model, quantization (4-bit, 8-bit), OpenAI API compatibility, model selection trade-offs (speed vs quality vs size)

---

### P14 — DocTuner
**Goal:** Fine-tune a small open source model on your own documents so it can answer questions about them directly — no retrieval, knowledge baked in.

**What you'll build:**
- Prepare a document dataset (your own docs, converted to instruction format)
- Fine-tune Llama 3.2 1B or Phi-4-mini using QLoRA (fits on gaming GPU, even 8GB VRAM)
- Use Unsloth for 2x faster training with lower memory
- Evaluate before/after on domain-specific Q&A
- Save as GGUF format, serve via Ollama

**Key concepts:** Full fine-tune vs LoRA vs QLoRA, rank/alpha hyperparameters, instruction format (Alpaca/ChatML), overfitting on small datasets, GGUF quantization, Hugging Face Hub

**Hardware requirement:** 8GB+ VRAM for 1B model with QLoRA; 12GB+ for 3B model

---

### P15 — RAG vs Fine-Tune
**Goal:** Rigorous comparison of the two main approaches to domain Q&A — decide when to use which.

**What you'll build:**
- Same document set, same questions, two pipelines:
  - Pipeline A: P2 RAG (Qdrant + Claude/GPT-4o)
  - Pipeline B: P14 fine-tuned local model
- Evaluation framework: correctness, latency, cost, hallucination rate
- Decision matrix: when RAG wins, when fine-tuning wins

**Key concepts:** Retrieval vs parametric knowledge, catastrophic forgetting, cost of fine-tuning vs cost of inference, knowledge freshness, hybrid approaches (RAG + fine-tuned retriever)

---

### Phase II Prerequisites
| Requirement | Notes |
|---|---|
| GPU machine on LAN | Any NVIDIA GPU — GTX 1080 minimum, RTX 30xx/40xx ideal |
| VRAM | 8GB minimum (1B QLoRA), 12GB+ recommended (3B QLoRA / 7B inference) |
| CUDA 12.x | Install before adding to cluster |
| Ubuntu 22.04+ | Same OS family as cluster |
| Disk | 50GB+ free for model weights |

---

### P16 — NanoGPT — Build an LLM from Scratch

**Goal:** Implement a GPT-style transformer from scratch in pure PyTorch — every component by hand, no HuggingFace shortcuts. Train it on a domain corpus. Watch it learn to generate text.

**Why this project:** Once you've built every piece yourself, you understand every LLM forever. Attention mechanisms, positional encoding, the training loop — it stops being magic. This is the project that separates engineers who use LLMs from engineers who understand them.

**What you'll build — every component from scratch:**

| Component | What you implement |
|---|---|
| Tokenizer | BPE (byte-pair encoding) or character-level tokenizer |
| Embedding layer | Token embeddings + positional encodings (learned or sinusoidal) |
| Multi-head self-attention | Q/K/V projections, scaled dot-product attention, causal mask |
| Feed-forward block | 2-layer MLP with GELU activation per transformer block |
| Layer normalization | Pre-norm architecture (modern GPT style) |
| Transformer blocks | Stack N blocks (attention + FFN + residual connections) |
| Language model head | Linear projection → vocab logits |
| Training loop | AdamW optimizer, cosine LR schedule, gradient clipping |
| Text generation | Autoregressive sampling — temperature, top-k, top-p |
| Evaluation | Perplexity on held-out set, qualitative text samples |

**Model scale (realistic for gaming GPU):**

| Config | Params | VRAM | Train time |
|---|---|---|---|
| Tiny (learn the concepts) | ~1M | <1GB | Minutes |
| Small (actually useful) | ~10M | ~2GB | 1–2 hours |
| Medium (GPT-2 small scale) | ~50M | ~4GB | 4–8 hours |

Start tiny, verify it learns, scale up once the code is correct.

**Training corpus options:**
- Apple internal documentation (domain-specific, small, fast to train)
- Your Onemyle codebase + docs (teaches it your project's language)
- Wikipedia subset for a general-purpose mini-model
- Financial filings (pairs with StockSage for a thematic arc)

**Key concepts:** Attention is all you need (the paper), autoregressive language modeling, causal masking, why residual connections matter, the role of layer norm placement, loss = cross-entropy over next token prediction, why transformers scale but RNNs don't, the difference between pre-training and fine-tuning at the architecture level

**Reference:** Andrej Karpathy's nanoGPT (study it after you've written your own — not before)

**Hardware requirement:** Any NVIDIA GPU with 4GB+ VRAM. Even a CPU works for the tiny model to verify correctness.

---

*Plan version 4 — approved 2026-04-01*
*Phase II added 2026-04-02 (P12–P16)*
*Previous versions: v1 (8 projects, 8 weeks implied) → v4 (11 projects, 16 weeks explicit)*
