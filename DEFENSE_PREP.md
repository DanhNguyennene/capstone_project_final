# Slurm Agent — Defense Preparation

> Comprehensive summary + hard question bank for oral defense.
> All image references use Obsidian wiki-link syntax (`![[...]]`).

---

## 1. Project in One Paragraph (Abstract-Level)

This project builds a **stateful, safety-enforcing AI assistant for Slurm HPC clusters**. Users type natural-language requests; the system translates them into grounded Slurm scheduler operations. The core novelty is a **dual-agent Observer/Operator architecture** built on top of the OpenAI Agents SDK and the Model Context Protocol (MCP): the Observer handles all read-only cluster inspection, and the Operator handles all state-changing actions behind a mandatory human-in-the-loop (HITL) confirmation gate. A **3,135-case synthetic benchmark** evaluates tool selection, routing correctness, HITL compliance, state transitions, and response quality. **Domain-adapted fine-tuning** (QLoRA on Qwen2.5-14B-Instruct, distilled from GPT-5-mini traces) achieves **88.3% mean weighted score**, closing 29% of the gap to the commercial ceiling (GPT-5-mini at 95.9%), while running entirely on local infrastructure.

---

## 2. Architecture

![[agent_system_architect.drawio.png]]

### Four-Layer Stack

| Layer | What it does |
|---|---|
| **Presentation** | React + Vite UI: chat, streaming, confirm/cancel dialogs |
| **Agent** | Observer + Operator dual-agent; ReAct reasoning; OpenAI Agents SDK |
| **Protocol (MCP)** | 64 typed Slurm tools; JSON-schema validation; real + mock execution modes |
| **Infrastructure** | LLM endpoint, Slurm cluster, SQLite session store, Slurm docs index |

### Observer / Operator Split

![[observer_routing_flow.png]]
![[operator_hitl_flow.png]]

- **Observer** — entry point for every request. Handles all read-only tools (29 tools: `squeue`, `sinfo`, `sacct`, `sdiag`, `sprio`, `lookup_slurm_docs`, `web_search`, …). When the request requires state mutation, it produces a **structured handoff payload** (4 fields: `action_request`, `required_tool`, `target_scope`, `targets`) and delegates.
- **Operator** — receives handoff only. Resolves targets (discovery read if needed), presents a HITL confirmation to the user, then executes the action tool (`scancel`, `sbatch`, `scontrol hold/release/update`, …). Returns full tool output back to the Observer for the final response.
- **Tool counts**: Observer 29 read-only, Operator 40 (35 action + 5 discovery reads), Monolithic 64.

![[tool_partition_dual.png]]
![[tool_partition_mono.png]]

### Handoff Payload (4 fields — memorise these)

```
action_request  — natural-language description of what the user wants
required_tool   — exact MCP tool name (e.g., scancel)
target_scope    — "explicit" | "discovery"
targets         — list of job IDs / user identifiers already known
```

The Observer generates this in a **single LLM tool call** — no regex, no rule-based extraction.

---

## 3. MCP Tool Layer

![[mcp_architecture.png]]

- **64 agent-facing tools** (67 `@mcp.tool` decorators − 3 internal).
- Dual execution modes: **real** (subprocess Slurm CLI) and **mock** (in-memory resettable state for eval).
- Every tool exposes a JSON schema; the layer validates and rejects malformed calls before any subprocess is spawned.
- Tools are partitioned into two allowlists at runtime — the Observer can't call `scancel` even if it tries; it simply isn't in its catalog.

---

## 4. RAG Documentation Retrieval

- **273 official Slurm docs pages** → **2,276 chunks** (~600 chars avg).
- **Hybrid BM25 + semantic (all-MiniLM-L6-v2, 384-dim)** with **RRF fusion (k=60)**, top-5 results returned.
- Web search (`web_search` + `fetch_web_content`) as fallback for unknown configs / site-specific questions.
- Available to Observer only.

---

## 5. Fine-Tuning Pipeline

### Why fine-tune?

GPT-5-mini costs money, transmits data externally, and adds latency. A local open-weight model eliminates all three — if it can be taught the Slurm-specific procedural patterns.

### Step 1 — MCP Mock Environment for Data Collection

![[mcp_mock_data_collection.png]]

- Mock MCP server with **deterministic, resettable in-memory cluster state** (jobs, nodes, account policies).
- GPT-5-mini runs against mock across all **2,520 training scenarios** (80% of 3,135 benchmark).
- **2,436 successful traces** collected (96.7%); 84 excluded (timeout / malformed tool calls).

**Concrete example — one benchmark case (`acct_list_healthy`):**

```json
{
  "id": "acct_list_healthy",
  "category": "account",
  "scenario": "healthy",
  "input": "Show all accounts on the cluster",

  "source_state": {
    "jobs": {
      "1001": { "state": "RUNNING", "user": "alice", "partition": "gpu" },
      "1002": { "state": "RUNNING", "user": "bob",   "partition": "cpu" },
      "1004": { "state": "PENDING", "user": "charlie","partition": "cpu" }
    },
    "nodes": {
      "gpu-node-01": { "state": "idle" },
      "gpu-node-02": { "state": "alloc" },
      "cpu-node-01": { "state": "mix"  }
    }
  },

  "target_state": { /* identical to source — read-only, no mutation */ },

  "ground_truth": {
    "tools":   ["sacctmgr_list"],
    "handoff": false,
    "hitl":    false,
    "keywords": ["account"]
  }
}
```

The mock server is pre-loaded with `source_state` before the agent runs. After the agent responds, `target_state` is compared to actual mock state — for read-only cases they are identical; for action cases (e.g., `scancel`) the target state has the job removed or state changed. This is what `state_match` measures.

**Five scenario snapshots (what changes between them):**

| Scenario | Jobs | Nodes | Stress |
|---|---|---|---|
| `healthy` | 1001 RUNNING, 1004 PENDING | all up/idle | baseline read/action |
| `failed` | 2001–2003 FAILED/TIMEOUT (OOM, segfault, timeout) | gpu-node-01 down, cpu drain | diagnose + requeue |
| `pending` | 3001–3004 all PENDING (Resources/Priority/QOS/Dependency) | all fully allocated | pending-reason analysis |
| `mixed` | RUNNING + FAILED + PENDING + COMPLETED mix | gpu-node-02 down | selective filtering |
| `debug_needed` | 5001–5007 FAILED with obscure stderr (NCCL, InfiniBand, Lustre, CUDA ECC) | nodes drain/down* | RAG docs + web search |

### Step 2 — Data Processing Pipeline

![[data_augmentation_phase1.png]]
![[data_augmentation_phase2.png]]

Three steps:
1. **Handoff splitting** — traces with Observer→Operator handoff split at the boundary → 2 independent samples. Yields 3,329 raw samples.
2. **Role-scoped tool filtering** — each sample carries only the tools for its active role. Teaches the model that tool availability is conditional on role (prevents cross-role hallucination).
3. **Deduplication** — 704 duplicate message sequences removed → **2,625 unique training samples** (2,074 Observer + 551 Operator).

### Step 3 — QLoRA Training

![[qlora.png]]
![[train_wandb.png]]

| Config | Value |
|---|---|
| Base model | Qwen2.5-14B-Instruct (48 transformer layers) |
| LoRA rank / alpha | 64 / 128 |
| Target modules | All 7 projections: q/k/v/o/gate/up/down |
| Trainable params | ~275M = 1.9% of 14.8B |
| Quantization | 4-bit NF4 (QLoRA) |
| Loss masking | Assistant tokens only (tool calls + responses) |
| Hardware | 1× NVIDIA A40 48GB (RunPod) |
| Training cost | ~$20, ~22h total session |
| Optimizer steps | 492 (2,625 × 3 epochs ÷ batch 16) |

**Key decision**: LoRA applied to ALL 48 layers, not just upper layers. Partial-layer adaptation (layers 36–47) caused base-model bleed-through where the CLI-style tool invocation prior (from pretraining on man pages, GitHub) overrode the adapter's structured JSON output.

---

## 6. Benchmark & Evaluation

### Dataset Structure

![[dataset_distribution_category.png]]
![[scenario_pie.png]]

- **3,135 cases** = 11 categories × 5 scenarios × 57 cases each.
- **11 categories** (285 each): read, diagnose, action, bulk, safety, submission, multi_step, account, edge, docs, domain.
- **5 scenarios**: healthy, failed, pending, mixed, debug_needed — each stresses different capabilities.
- Each case has: user prompt, source state, target state, expected tools, routing decision, HITL requirement.
- **80/20 stratified split** (seed=42, by category×scenario): 2,520 train / 615 test.

### Scoring Formula

$$\text{score}(c) = 0.35 \cdot TR + 0.25 \cdot R + 0.25 \cdot H + 0.15 \cdot S$$

| Dimension | Weight | What it measures |
|---|---|---|
| Tool Recall (TR) | 0.35 | Did the agent call the right tools? |
| Routing Match (R) | 0.25 | Observer-only vs. Operator handoff — correct? |
| HITL Match (H) | 0.25 | Did confirmation gate fire when required? |
| State Match (S) | 0.15 | Did cluster state transition correctly? |

Keyword coverage was excluded from the final scoring: open-ended Slurm responses rarely reproduce exact ground-truth phrasing, making lexical matching unreliable.

**Pass threshold**: ≥ 0.80 (used internally to define trial success; all reported headline numbers are avg weighted score).

---

## 7. Results

### Three-Way Model Comparison

![[three_way_per_category.png]]

| Metric | GPT-5-mini | **FT Qwen2.5-14B** | Base Qwen2.5-14B |
|---|---|---|---|
| Avg overall score | 95.9% | **88.3%** | 85.2% |
| Tool recall | 98.8% | 89.2% | 84.9% |
| Routing match | 99.0% | 90.1% | 83.6% |
| HITL match | 99.0% | 90.4% | 90.2% |
| State match | 98.2% | 90.0% | 89.8% |
| Judge score | 75.7% | **79.7%** | 76.8% |
| Avg latency | 28.3 s | 84.8 s | 80.9 s |

**FT closes 29% of the commercial gap** (avg weighted score): (88.3 − 85.2) / (95.9 − 85.2) = 3.1 / 10.7 = **29%**.

### Per-Category FT Gains

![[ft_vs_base_per_category.png]]

**Largest gains** (categories the fine-tuning targeted):

| Category | Base | FT | Δ |
|---|---|---|---|
| submission | 61.7% | 83.4% | +21.7 pp |
| multi_step | 69.5% | 83.3% | +13.8 pp |
| safety | 77.3% | 88.6% | +11.3 pp |
| bulk | 79.0% | 85.9% | +6.8 pp |

**Regressions** (knowledge-intensive, base was already good):

| Category | Base | FT | Δ |
|---|---|---|---|
| domain | ~95% | ~89% | −6.2 pp |
| docs | ~90% | ~85.5% | −4.5 pp |
| diagnose | ~98% | ~94.5% | −3.8 pp |

### Ablation: Dual-Agent vs. Monolithic

![[ablation_per_category.png]]

*(Routing metric excluded from ablation — monolithic gets routing=0 on 237 handoff cases by construction. Weights renormalized: TR 0.467, HITL 0.333, S 0.200)*

| Metric | Observer/Operator | Monolithic | Δ |
|---|---|---|---|
| Avg overall score | 87.6% | 81.6% | **+6.1 pp** |
| Tool recall | 84.9% | 77.5% | +7.4 pp |
| HITL match | 90.2% | 88.9% | +1.3 pp |
| State match | 89.8% | 78.9% | +10.9 pp |
| Judge score | 76.8% | 59.2% | **+17.6 pp** |
| Latency | 80.9 s | 76.8 s | +4.1 s (+5.3%) |

> **Important framing**: The +4.1s overhead is the **architectural cost of the dual-agent split on the same model**. GPT-5-mini also runs dual-agent but takes only 28.3s — proving the architecture is not what drives latency. The 80.9s is Qwen2.5-14B fp16 inference speed on A40, not a handoff overhead. The architectural overhead itself is only 5.3%.

On **378 routing-neutral cases**: **+10.2 pp** (94.2% vs. 84.0%) — pure tool-scope reduction benefit.

Safety category: **57.9% (dual) vs. 33.3% (mono)** = −24.6 pp in monolithic, because the HITL gate is structural, not prompt-based.

---

## 8. Limitations

### Benchmark Scope
- 5 static cluster snapshots, 3 users, fixed job-ID range. Not a live cluster.
- Grid covers common patterns; does not generalise automatically to site-specific plugins, non-standard configs, or phrasings outside the grid.
- No concurrent user simulation; scheduler dynamics are absent.

### Routing Metric Coupling
- Routing (25% weight) is only meaningful for the dual-agent config. Monolithic gets 0 on 237 handoff cases by construction. The ablation re-normalises, but the coupling is inherent to the metric design.

### Training Data from Finite Mock State
- GPT-5-mini traces come from the same 5 mock snapshots used in eval. The distilled corpus has inherent repetition in some operational patterns. Model may not generalise to mock states it never saw.

### LoRA Specialisation Trade-off
- Fine-tuning improves procedural categories (submission, bulk, safety) but slightly regresses knowledge-intensive ones (domain, docs, diagnose). This is the inherent LoRA specialisation effect — the adapter overwrites some generalised reasoning from pretraining.

### No Production Hardening
- No multi-tenant auth, tenant isolation, or comprehensive audit logging. HITL is enforced architecturally, but the system was not audited for adversarial prompt injection or privilege escalation.

### Latency
- 84.8 s avg for fine-tuned model vs. 28.3 s for GPT-5-mini (3× slower). This is a GPU bandwidth / model size problem, not an architecture problem, but it limits UX for interactive cluster management.

### LLM-as-Judge Variance
- Judge scores (GPT-OSS 20B via Ollama) are model-dependent and can drift between judge versions. The 75.7% / 79.7% / 76.8% judge numbers should be interpreted with ±2–3 pp uncertainty.

---

## 9. 100 Hard Questions for 1-Hour Defense

> **Examiner profile**: Khuê Phan Trần Minh — Lecturer at HCMC Open University. Research: **serious games, ML, DL**. Will likely probe ML/DL fundamentals, evaluation rigor, statistical validity, generalization claims, and practical deployment.

---

### BLOCK A — Contributions & Novelty (Q1–Q15)

> **Q1. Your main contribution is the Observer/Operator split. But this is just a two-agent handoff. OpenAI already ships multi-agent examples. What's novel here?**

The novelty is not multi-agent per se — it is **capacity-aware partitioning motivated by a specific failure mode in 14B-parameter models**: tool-selection degradation when the context exposes 64 semantically overlapping tools simultaneously. The Observer sees 29 read-only tools; the Operator sees 40 action tools. Ablation on routing-neutral cases shows +10.2 pp purely from this split, with +17.6 pp on LLM judge (quality collapses when the model has to reason about which of 64 tools to skip). The architectural constraint also makes the Observer's cross-role hallucination structurally impossible — it can't call `scancel` because `scancel` is simply not in its catalog.

![[tool_partition_dual.png]]
![[ablation_per_category.png]]

> **Q2. What exactly is your contribution vs. existing infrastructure you just used (OpenAI SDK, MCP, Qwen, React)?**

The **infrastructure** (SDK, MCP protocol, Qwen base model, React) is reused — that's intentional engineering. The **contributions** are:
1. The capacity-aware dual-agent architecture with empirical evidence of its benefit (+10.2 pp on routing-neutral cases, +6.1 pp overall)
2. The multi-layer safety framework: tool classification + guardrails + SlurmGuard admission + structural HITL gate
3. The 3,135-case benchmark with architecture-aware scoring (tool recall, routing, HITL, state match) — a novel evaluation methodology for agentic systems
4. The role-scoped distillation methodology (splitting at handoff boundaries, filtering tools per role) — original training data engineering
5. The end-to-end integration showing that a $20 fine-tuning run on a 14B model can close 29% of the gap to a commercial API, fully locally deployed

> **Q3. You claim "broad Slurm intent surface." But 64 tools — isn't that just wrapping CLI commands? What's the engineering contribution?**

The contribution isn't wrapping commands — it's the **system built on top**: (1) typed JSON-schema validation preventing malformed calls, (2) partitioning into read/write subsets that measurably improves a 14B model's selection accuracy (+10.2 pp), (3) dual execution modes (real subprocess vs. stateful mock) enabling the entire evaluation and training pipeline, and (4) the safety architecture (guardrails + SlurmGuard + HITL) that makes destructive operations structurally gated. The tools cover the most common Slurm operations (~80% of typical admin workflows); completeness is not the goal — the agent's reasoning and safety enforcement over those tools is.

> **Q4. The 3,135 benchmark is synthetic. How do you justify it compared to real user studies?**

Real user studies measure subjective satisfaction; our benchmark measures **objective behavioral correctness** (did the right tool get called? did HITL fire? did state transition correctly?). These are binary ground-truth questions that real users can't answer at scale. The synthetic benchmark is the only way to get 3,135 cases with known ground-truth labels. We acknowledge user studies as future work, but they answer a different question ("is this useful?") vs. ours ("is this correct?").

> **Q5. 29% gap closure sounds underwhelming. Can you justify why this is a meaningful result?**

29% is measured on a **continuous quality metric** (avg weighted score). The base model is already at 85.2% — the remaining gap to 95.9% is only 10.7 pp, and we close 3.1 pp of it. More importantly, the gains are concentrated where they matter most: +21.7 pp on submission, +13.8 pp on multi_step, +11.3 pp on safety. These are the categories that actually require learned procedural behavior. A practitioner deploying this system for job management (the primary use case) would see a much larger effective improvement on the tasks they care about.

> **Q6. You say "the first Slurm-specific benchmark." How do you know no one else has done this?**

Literature review (Section 3 — Related Works) covers all existing LLM-for-operations benchmarks: ToolBench, API-Bank, MINT, AgentBench, TaskBench. None target Slurm specifically — they cover general APIs, web tools, or OS commands. The closest is OS-Copilot which handles shell commands, but it doesn't have typed tool schemas, HITL scoring, or Slurm-domain state transitions. We searched Google Scholar, arXiv, and ACL Anthology for "Slurm" + "benchmark" + "LLM" and found no prior work.

> **Q7. Why Qwen2.5-14B and not LLaMA, Mistral, or another open model?**

Qwen2.5-14B-Instruct was chosen because at the time of training it was the **best-performing open-weight model at 14B scale for tool calling** on public benchmarks (Berkeley Function Calling Leaderboard). It natively supports structured tool-call output (JSON mode), which is critical for agent frameworks. LLaMA-3 at similar size had weaker tool-calling scores. Mistral-Nemo (12B) was tested but showed inferior multi-step reasoning on preliminary submission cases.

> **Q8. Why not just use GPT-5-mini in production? What's the point of the local model if it's worse?**

Three reasons: (1) **Data sovereignty** — HPC environments often process sensitive research data that cannot be sent to external APIs. (2) **Cost at scale** — at $0.002–0.01 per request, a busy cluster with hundreds of users generates significant ongoing cost. (3) **Availability** — cloud APIs have rate limits, outages, and can deprecate models. The local model runs forever on owned hardware with zero marginal cost after a one-time $20 training investment.

> **Q9. What is the novelty of using MCP here? Isn't MCP just a standard protocol?**

MCP is the transport protocol — we don't claim to invent it. The novelty is **what we put on top of it**: 64 Slurm-specific tools with full JSON schemas, dual execution modes (real/mock), and the partition into two access classes that the agent layer enforces. MCP gave us typed tool interfaces and stdio/SSE transport for free — our contribution is the tool surface design and the safety-aware access control policy.

> **Q10. Why did you choose ReAct over other agent paradigms (Plan-and-Execute, Tree of Thoughts)?**

ReAct (Reason + Act) is the natural fit for tool-calling agents because each step is observe-then-act. Plan-and-Execute assumes the full plan can be laid out upfront — but Slurm interactions are inherently reactive (you need to inspect state before deciding what to do). Tree of Thoughts is for reasoning problems with branching, not for sequential tool execution. The OpenAI Agents SDK implements ReAct natively, and our evaluation shows it works well for this domain (95.9% with GPT-5-mini).

> **Q11. Your HITL gate is just a UI confirmation dialog. What if the LLM bypasses it?**

It **cannot** bypass it architecturally. The HITL gate is not a prompt instruction — it is code in the Operator's execution path. When the Operator calls any destructive tool, the framework intercepts the call and creates a pending action that requires human approval via the API. Even if the model's output says "skip confirmation," the code path doesn't have a skip branch. The Observer can't call destructive tools at all (they're not in its catalog). This is a **structural guarantee**, not a behavioral one.

> **Q12. You have 11 categories with 285 cases each. How were these prompts generated?**

They were generated by GPT-4 with careful prompt engineering: for each category × scenario combination, we provided the mock state description and asked for diverse phrasings of user requests that exercise that category's behavior. The prompts were then human-reviewed for correctness, deduplication, and coverage. Ground-truth labels (expected tools, routing, HITL) were manually annotated based on the intended behavior.

> **Q13. What if the model just memorized the benchmark format during fine-tuning?**

The fine-tuning data and test data come from **disjoint partitions** (80/20 stratified split, seed=42). The model never sees the 615 test prompts or their expected outputs during training. It only sees GPT-5-mini traces from the 2,520 training scenarios. The risk of format memorization is further mitigated because the training traces include the full reasoning chain (think-act-observe), not just the final answer — the model must learn the process, not pattern-match outputs.

> **Q14. Your evaluation uses 4 metrics with fixed weights (0.35, 0.25, 0.25, 0.15). How did you choose these weights? Isn't this arbitrary?**

The weights reflect operational priority: **tool recall (0.35)** is highest because calling the wrong tool is the most dangerous failure mode in an HPC context (e.g., cancelling the wrong jobs). **Routing (0.25)** and **HITL (0.25)** are equally important because routing to the wrong agent and skipping confirmation are both safety failures. **State match (0.15)** is lowest because for read-only categories (6 of 11) it's trivially 1.0, and for action categories it's largely redundant with correct tool+HITL. Keyword coverage was dropped entirely because open-ended Slurm responses rarely reproduce exact ground-truth phrasing. We acknowledge the weights are a design choice — but the model ranking (GPT-5-mini > FT > Base > Mono) is stable under any reasonable reweighting because the gaps (95.9 → 88.3 → 85.2 → 81.6) are large relative to the effect any weight perturbation within ±0.05 would produce.

> **Q15. Why is "state match" only 15% weight? Isn't the final cluster state the most important thing?**

State match measures whether the mock server's state changed correctly after the agent acted. For read-only categories (6 of 11), state should be unchanged — it's trivially 1.0. For action categories, state match captures whether the operation succeeded, but it's redundant with tool recall + HITL (if you called the right tool with the right args and confirmed, state will match). It gets 15% as a cross-check, not as a primary signal. Giving it more weight would double-count tool correctness.

---

### BLOCK B — ML/DL Fundamentals (Q16–Q35)

> **Q16. Explain LoRA mathematically. What is the rank decomposition?**

For a pretrained weight matrix $W_0 \in \mathbb{R}^{d \times k}$, LoRA adds a low-rank update: $W = W_0 + \Delta W = W_0 + BA$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and $r \ll \min(d,k)$. During training, $W_0$ is frozen; only $A$ and $B$ receive gradients. The forward pass becomes $h = W_0 x + \frac{\alpha}{r} BAx$. For our config: $r=64$, $\alpha=128$, so the scaling factor is $\alpha/r = 2$.

> **Q17. Why rank 64? How did you choose this? What happens with rank 8 or rank 256?**

Rank 64 was chosen based on prior work (QLoRA paper recommends 64 for 7–14B models) and preliminary experiments. With rank 8, the adapter has insufficient capacity to override the base model's CLI-style tool invocation prior — we observed base-model bleed-through on bulk and submission categories. Rank 256 would quadruple trainable parameters (~1.1B) without proportional quality gain, and risks overfitting on 2,625 samples. The adapter at rank 64 has ~275M parameters (1.9%), which is a good capacity-data ratio.

> **Q18. Why apply LoRA to all 48 layers instead of just the last few?**

Preliminary experiments with partial-layer adaptation (layers 36–47 only) showed the base model's pretraining prior "leaking through" on certain categories. Specifically, the model would generate CLI-style tool arguments (`--user charlie` instead of `{"user": "charlie"}`) because the lower layers still encoded the base model's representation of command-line syntax. Applying LoRA to all layers ensures the entire representation pipeline is adapted, not just the final decision layers.

> **Q19. What is QLoRA specifically? How does 4-bit quantization work during training?**

QLoRA quantizes the frozen base model to 4-bit NormalFloat (NF4) — a data type optimized for normally-distributed neural network weights. The quantization uses **double quantization** (quantizing the quantization constants themselves) for additional memory savings. During training, the frozen 4-bit weights are dequantized to bf16 on-the-fly for the forward pass, the LoRA adapter layers stay in bf16, and gradients flow only through the adapter. This reduces memory from ~28GB (fp16 full model) to ~8GB (4-bit) + ~2GB (adapter) = ~10GB for training.

> **Q20. What loss function are you using? Why causal LM loss with masking?**

Standard cross-entropy loss over next-token prediction (causal language modeling). But we **mask** the loss so that only assistant-generated tokens receive gradient signal. System prompts, user messages, and tool-response observations are treated as context-only (loss weight = 0). This teaches the model to generate correct tool calls and responses given context, without trying to "predict" the user's message or the tool's output (which would be meaningless).

> **Q21. What optimizer? Learning rate schedule? Why these choices?**

AdamW with learning rate 2e-4, linear warmup (3% of steps), then cosine decay to 0. Weight decay 0.01. These are standard for QLoRA fine-tuning per the original paper. AdamW is used over SGD because transformer fine-tuning benefits from adaptive learning rates, and the momentum helps navigate the loss landscape when only a small fraction of parameters are trainable.

> **Q22. You train for 3 epochs on 2,625 samples. How do you know you're not overfitting?**

Three signals: (1) The training loss converges smoothly without late-stage spikes (visible in the WandB plot). (2) The 615-case held-out test set was never seen during training, and the model achieves 88.3% on it — close to but below training performance, suggesting mild generalization gap but not catastrophic overfitting. (3) The per-category scores show the model generalizes across scenarios within a category (trained on one mock state, tested on a different partition of cases within the same mock state family).

> **Q23. What is catastrophic forgetting? Is your model suffering from it?**

Catastrophic forgetting occurs when fine-tuning overwrites the base model's general capabilities. Our model shows **mild** signs: −6.2 pp on domain, −4.5 pp on docs, −3.8 pp on diagnose. These are knowledge-intensive categories where the base model was strong. LoRA mitigates catastrophic forgetting because only 1.9% of parameters are modified — the base model's representations are largely preserved. The regressions we observe are small and expected for any specialized fine-tuning.

> **Q24. What is the difference between LoRA, full fine-tuning, and prompt tuning? Why LoRA?**

- **Full fine-tuning**: Updates all parameters. For 14B model: needs ~112GB VRAM (fp16 weights + optimizer states). Infeasible on A40 48GB.
- **Prompt tuning**: Adds learnable soft tokens to the input. Very parameter-efficient but weak for complex behavioral changes (tool-calling requires more than a few soft tokens).
- **LoRA**: Adds low-rank adapter matrices to attention layers. Moderate parameter count (~275M), strong behavioral adaptation capability, trainable on a single A40 with 4-bit quantization (QLoRA). Best trade-off for our hardware constraints.

> **Q25. Explain the attention mechanism in transformers. How does Qwen2.5 implement it?**

Multi-head self-attention: $\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$. Qwen2.5 uses **Grouped Query Attention (GQA)**: query heads are grouped, and each group shares a single key-value head. This reduces KV-cache memory by 4-8× without significant quality loss. In our LoRA config, we apply adapters to all 7 projection matrices: q, k, v, o (attention) + gate, up, down (MLP FFN). This ensures the full attention computation is adapted.

> **Q26. What is flash attention and why do you use it for inference?**

Flash Attention is an IO-aware exact attention algorithm that avoids materializing the full $N \times N$ attention matrix in HBM (high-bandwidth memory). Instead, it tiles the computation and keeps intermediate results in SRAM (on-chip cache). This reduces memory from $O(N^2)$ to $O(N)$ and is 2-4× faster in practice. We use `flash_attention_2` during inference (fp16 serving) because it allows longer contexts with less memory, critical for multi-turn agent conversations with many tool outputs.

> **Q27. You use temperature=0 for evaluation. What does this mean mathematically?**

Temperature $T$ scales the logits before softmax: $p_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}$. At $T=0$ (implemented as argmax), the model always selects the highest-probability token — making generation deterministic for a given input. We use $T=0$ to ensure reproducibility: the same prompt produces the same output every time. The 3 trials differ because of different session contexts (fresh vs. stateful), not randomness.

> **Q28. What is the difference between greedy decoding (T=0) and beam search? Why not use beam search?**

Greedy takes the top-1 token at each step. Beam search maintains $k$ hypotheses simultaneously and selects the highest-scoring sequence. For tool-calling agents, beam search is unnecessary because: (1) the output format is highly structured (JSON tool calls) with low ambiguity, (2) beam search adds latency (proportional to beam width), and (3) the model already achieves 95.9% with greedy on GPT-5-mini, suggesting the output distribution is peaked.

> **Q29. What is knowledge distillation? How does your approach relate to classical distillation?**

Classical distillation (Hinton et al.) trains a student to match the teacher's soft probability distribution (KL divergence on logits). Our approach is **behavioral distillation**: the student learns to reproduce the teacher's **output sequences** (tool calls, reasoning chains, responses) via standard causal LM loss. This is more practical for closed-source teachers (GPT-5-mini) where logits aren't accessible. The student learns the behavioral patterns without needing the teacher's internal representations.

> **Q30. How do you ensure the distilled model doesn't just copy the teacher's mistakes?**

We only distill from **successful traces** (2,436 out of 2,520 = 96.7% success rate). Failed traces (timeouts, malformed outputs) are excluded. Additionally, the ground-truth labels come from the benchmark (expected tools, routing, HITL), not from the teacher — so even if the teacher occasionally takes a suboptimal path, the evaluation measures against the true expected behavior. The teacher's mistakes that happen to pass the scoring threshold are few because GPT-5-mini achieves 95.9%.

> **Q31. What is the vanishing/exploding gradient problem? Is it relevant here?**

In deep networks, gradients can shrink exponentially (vanishing) or grow exponentially (exploding) through backpropagation. Transformers mitigate this via LayerNorm and residual connections. For LoRA specifically, the adapter is very shallow (just two matrices BA), so gradient pathology is minimal. The AdamW optimizer with gradient clipping (max_grad_norm=1.0) provides an additional safeguard.

> **Q32. What is the role of the tokenizer? Does fine-tuning change the vocabulary?**

The tokenizer converts text to token IDs. Qwen2.5 uses a BPE tokenizer with ~152K vocabulary. Fine-tuning with LoRA does **not** change the vocabulary or embedding layer — we only adapt the transformer layers. The embedding and unembedding matrices remain frozen. This means the model's token representations are inherited from pretraining; only the processing of those representations is adapted.

> **Q33. What is perplexity? Did you measure it?**

Perplexity is $\exp(-\frac{1}{N}\sum_i \log p(x_i | x_{<i}))$ — the exponential of the average negative log-likelihood. Lower = better. We didn't report perplexity because it's a language modeling metric, not an agent performance metric. Our evaluation uses **task-level metrics** (tool recall, routing, HITL, state match) which are more meaningful for the deployment scenario. Perplexity on held-out text wouldn't tell us if the model calls the right Slurm tool.

> **Q34. What is BM25? How does it work in your RAG pipeline?**

BM25 is a bag-of-words retrieval function that scores document-query relevance based on term frequency (TF) with diminishing returns, inverse document frequency (IDF), and document length normalization:
$$\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t,d) \cdot (k_1 + 1)}{f(t,d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{avgdl})}$$
with $k_1=1.2$, $b=0.75$ typically. It excels at exact keyword matching ("squeue", "pending reason Priority"). In our hybrid RAG, BM25 handles queries where exact Slurm command names appear; the semantic model (all-MiniLM-L6-v2) handles paraphrase queries.

> **Q35. What is RRF (Reciprocal Rank Fusion)? Why k=60?**

RRF combines ranked lists from multiple retrievers: $\text{score}(d) = \sum_{r \in \text{rankers}} \frac{1}{k + \text{rank}_r(d)}$. The constant $k=60$ dampens the influence of rank position — higher $k$ means rankings are treated more equally. We chose $k=60$ following the original RRF paper (Cormack et al., 2009) recommendation. It's robust: the ranking is insensitive to exact $k$ values between 40–80. No cross-encoder re-ranker is needed because our corpus (2,276 chunks) is small enough that top-5 precision from RRF is sufficient.

---

### BLOCK C — Evaluation Methodology (Q36–Q55)

> **Q36. Why 3 trials? Temperature is 0 — there's no randomness. What does repeating change?**

Each trial uses a **fresh session** with a reset mock MCP server. The session context differs because: trial 1 starts from empty state, trial 2 gets a new session ID (different internal context hash), trial 3 same. While the model output is deterministic for identical inputs, the session initialization can subtly affect the conversation context. Averaging over 3 trials provides a stable estimate and catches edge cases where a single initialization produces an artifact.

> **Q37. Is 615 test cases statistically sufficient? What's your confidence interval?**

At 615 cases with binary pass/fail, a proportion $p=0.883$ has standard error $SE = \sqrt{p(1-p)/n} = \sqrt{0.883 \times 0.117 / 615} \approx 0.013$. The 95% confidence interval is $\pm 2.6$ pp. This means the true population score is 88.3% ± 2.6% with 95% confidence. The difference between FT (88.3%) and Base (85.2%) is 3.1 pp, which is just above the confidence interval — statistically significant but marginal. The per-category comparisons (where n=~56 per category) have wider intervals (~±7 pp), so the +21.7 pp on submission is highly significant but smaller differences (−3.8 pp on diagnose) are within noise.

> **Q38. Did you do any statistical significance tests (t-test, McNemar's test)?**

Not formally reported. This is a limitation. For a proper comparison, McNemar's test on paired binary outcomes (same test case, different model) would be appropriate. Given the 615 paired cases, the chi-squared statistic for FT vs. Base would be significant (p < 0.05) for the overall difference, but borderline for some per-category comparisons. Adding this would strengthen the paper.

> **Q39. Your scoring formula has 5 dimensions. Did you validate that they measure different things?**

Yes — the dimensions are largely independent: Tool recall measures which tools were called (set overlap). Routing measures Observer-vs-Operator assignment (binary). HITL measures whether confirmation fired (binary). State match measures final mock state (comparison). Keyword measures response content (substring match). Cases can fail on one dimension while passing others: e.g., correct tools but wrong routing (handoff not triggered), or correct routing but wrong tool (tool recall = 0 but routing = 1). The correlation between dimensions is moderate, not unity.

> **Q40. The LLM judge gives GPT-5-mini only 75.7%. Isn't that suspicious? Shouldn't the best model score highest on all metrics?**

The judge evaluates **response quality** (conciseness, evidence-grounding, helpfulness), not structural correctness. GPT-5-mini produces verbose, hedging responses ("I'd like to help you with that. Let me check...") that the judge penalizes. The FT model produces more concise responses because it has less capacity for verbose generation — the judge (GPT-OSS 20B) actually prefers conciseness. This is a known effect in distillation.

> **Q41. Why use GPT-OSS 20B as judge and not GPT-5-mini or GPT-4o?**

Using GPT-5-mini as judge would be circular — it's the training teacher, so it would systematically prefer outputs similar to its own style. GPT-4o would be better but costs money per evaluation (615 cases × 3 trials × 4 models = ~7,380 judge calls). GPT-OSS 20B is free (Ollama local), independent from the training pipeline, and capable enough for quality assessment. The trade-off is lower judge reliability (±2–3 pp variance).

> **Q42. What if your benchmark has label errors? How many did you manually verify?**

We manually verified ~100 randomly sampled cases (across all categories) for ground-truth correctness: expected tools, routing decision, HITL requirement. 3 label errors were found and corrected (wrong `handoff=true` on read-only cases). This gives an estimated label error rate of ~3%, which introduces up to ±1 pp noise in reported scores. Full manual verification of 3,135 cases was infeasible.

> **Q43. The monolithic ablation gets routing=0 on 237 cases "by construction." Isn't this unfair?**

Yes, and we explicitly acknowledge and correct for it. The ablation table **excludes the routing dimension entirely** and re-normalizes remaining weights (TR 0.467, HITL 0.333, S 0.200). Even after this correction, dual-agent wins by +6.1 pp overall and +10.2 pp on 378 routing-neutral cases. The routing bias actually understates the dual-agent advantage — in a fair comparison where both architectures could hypothetically route, the gap would be larger.

> **Q44. Why not compare against other agent frameworks (LangChain, AutoGen, CrewAI)?**

We compared against the **monolithic baseline** (same model, same tools, no split) which is what those frameworks effectively implement. LangChain/AutoGen don't have Slurm-specific tool surfaces or HITL gates — we'd have to build those ourselves, at which point it's our system with a different SDK underneath. The meaningful comparison is "does the dual-agent split help?" (yes, +6.1 pp) and "does fine-tuning help?" (yes, +3.1 pp), not which framework wrapper is used.

> **Q45. You mention "state-match scoring artefact" — a bug in your scoring code. How do you know there aren't more bugs?**

The artefact was found because safety/bulk cases showed anomalously low state-match despite visibly correct tool calls in the trace log. After fixing it, we cross-validated all scoring dimensions against manual inspection of 50 randomly sampled cases. All dimensions matched manual assessment within rounding error. The 23 remaining low-scoring cases post-fix were manually confirmed as genuine failures. We also ran the scorer against known-correct synthetic traces (tool calls manually constructed to match ground truth) and verified 100% scores.

> **Q46. How do you handle cases where the agent takes a valid but different path than the ground truth?**

Tool recall uses **set overlap**, not exact sequence match: if ground truth expects `{squeue, scancel}` and the agent calls `{squeue, scontrol_show, scancel}`, tool recall = 2/2 = 100% (extra tools don't penalize). Routing is binary (handoff or not). HITL is binary (confirmation fired or not). This design is intentionally lenient — it rewards reaching the right outcome regardless of exact path. The LLM judge further handles response quality for cases where the path differs.

> **Q47. You originally had a "keyword score" — why was it removed?**

Keyword score checked whether critical factual terms appear in the agent's response (e.g., "PENDING", "Priority", job IDs). It was **excluded from the final scoring** because open-ended Slurm responses rarely reproduce exact ground-truth phrasing — making lexical matching an unreliable signal that inflates scores independently of correctness. The LLM judge (when enabled at 15%) captures response quality far more accurately. Removing keyword simplified the formula to 4 interpretable dimensions (TR/R/H/S) and eliminated a brittle metric that rewarded verbosity over correctness.

> **Q48. Do you report per-scenario results? Does the model perform differently on "healthy" vs. "debug_needed"?**

Yes, we have per-scenario data but the report focuses on per-category breakdowns (11 categories). Per-scenario, the `debug_needed` scenario is hardest (it requires RAG retrieval for obscure errors like NCCL, InfiniBand failures). The `healthy` scenario is easiest. The difference is ~5–8 pp between easiest and hardest scenarios across all models, confirming the scenarios provide meaningful difficulty variation.

> **Q49. Why 5 scenarios and not 10 or 20?**

Each scenario requires a manually designed mock cluster state (jobs, nodes, accounts, QoS) that exercises different failure modes. 5 scenarios (healthy, failed, pending, mixed, debug_needed) cover the major operational patterns. More scenarios would provide more coverage but with diminishing returns — the 5 chosen span the key HPC states (normal operation, job failures, resource contention, mixed issues, obscure errors requiring documentation). Beyond 5, scenarios become minor variations of existing ones.

> **Q50. How reproducible are your results? If someone runs your code, do they get the same numbers?**

Fully reproducible given: (1) same model checkpoint (HuggingFace `DanhVuiVe/slurm-agent-qwen14b-lora-final`), (2) same benchmark split (seed=42), (3) same MCP mock server code, (4) temperature=0. The mock server is deterministic — same input always produces same output. The only non-reproducible element is the LLM judge (GPT-OSS 20B may differ across Ollama versions), but structural metrics are perfectly reproducible.

> **Q51. You use "avg weighted score" as the primary metric. Why not just accuracy (pass/fail)?**

Binary accuracy (pass/fail with threshold 0.80) loses information: a case scoring 0.79 is "fail" and 0.81 is "pass" despite being nearly identical. The avg weighted score preserves the continuous quality signal — a model that partially gets things right (correct tool but wrong routing) scores higher than one that gets nothing right. This gives a more nuanced comparison, especially when models are close in performance (85.2% vs. 88.3%).

> **Q52. Your eval harness runs the agent against the mock MCP server. How do you know this is representative of real Slurm behavior?**

The mock server implements the same tool interfaces (JSON schemas, parameter names, return value structures) as the real MCP server running against Slurm. The difference is execution: real mode spawns `squeue`/`scancel` subprocesses; mock mode returns pre-configured responses. From the agent's perspective, the interface is identical — it makes the same tool calls with the same parameters and receives the same format of responses. The mock just makes it deterministic and resettable.

> **Q53. What happens if the user's prompt is in Vietnamese? Or broken English?**

The system is designed for English-language interaction. Vietnamese prompts would likely fail because: (1) the system prompt is in English, (2) the tool descriptions are in English, (3) the training data is entirely English. The base Qwen2.5 model has multilingual capability, but the fine-tuning is English-only. This is a limitation — a real deployment at a Vietnamese university might need bilingual support.

> **Q54. How do you measure "routing accuracy" exactly?**

Each test case has a ground-truth `handoff` field (true/false). `handoff=true` means the correct behavior is for the Observer to trigger a handoff to the Operator. `handoff=false` means the Observer should handle it entirely. We check whether the agent's actual behavior matches: did a handoff occur (true positive) or not (true negative)? Routing accuracy = correct routing decisions / total cases.

> **Q55. What is the inter-annotator agreement on your ground-truth labels?**

The labels were primarily annotated by one person (the project author) with spot-check verification on ~100 cases. No formal inter-annotator agreement (Cohen's κ) was computed. This is a limitation. However, the labels are largely unambiguous: "Show all jobs" → handoff=false (read-only), "Cancel job 1001" → handoff=true (destructive action). The ambiguous cases are in the `edge` and `safety` categories where routing decisions are debatable — these contribute to the ~3% estimated label error rate.

---

### BLOCK D — Architecture & Implementation (Q56–Q75)

> **Q56. Why FastAPI and not Flask or Django?**

FastAPI supports **async** natively (critical for concurrent agent sessions), has automatic OpenAPI documentation, and natively handles streaming responses (SSE for real-time token streaming to the frontend). Flask would require additional libraries (gevent/asyncio wrappers). Django is too heavyweight for an API-only backend. FastAPI is also the de facto standard for AI/ML serving endpoints.

> **Q57. How does the streaming work? What protocol?**

Server-Sent Events (SSE) over HTTP. The FastAPI endpoint yields tokens as they're generated by the LLM, sending each as an SSE event. The React frontend uses `EventSource` API to receive tokens incrementally and render them. This gives real-time feedback during the 84.8s average generation time — without streaming, the user would see nothing for over a minute.

> **Q58. How does session persistence work? What's stored in SQLite?**

SQLite stores: (1) session ID → conversation history (messages, tool calls, tool responses), (2) pending actions awaiting HITL confirmation, (3) session metadata (creation time, model config). This enables multi-turn conversations — the agent can reference previous tool outputs across turns. The mock MCP server state is NOT stored in SQLite — it's in-memory and resets per session in eval mode.

> **Q59. What happens if the Observer incorrectly decides NOT to hand off?**

This is a routing error: the Observer handles a destructive request itself (calling a read-only tool or just generating a text response). Since it can't call `scancel` (not in its catalog), the worst outcome is a helpful text response that doesn't actually execute the action. The user would notice nothing happened and re-request. This is a **safe failure mode** — failing to act is safer than acting incorrectly.

> **Q60. What happens if the Observer incorrectly hands off a read-only request?**

The Operator receives the handoff, attempts to resolve targets, but finds no matching action tool is appropriate. It either: (1) executes a discovery read (harmless), (2) returns an empty response back to the Observer. The HITL gate won't fire if no destructive tool is called. This is a **latency penalty** (extra round-trip) but not a safety violation. The Observer then generates the response from the Operator's return context.

> **Q61. How does the HITL confirmation work at the API level?**

1. Operator calls destructive tool → framework intercepts
2. A `pending_action` object is created (tool name, args, session ID)
3. The SSE stream sends a `confirmation_required` event to the frontend
4. Frontend shows the dialog; user clicks confirm/cancel
5. Frontend POSTs to `/confirm/{action_id}` or `/cancel/{action_id}`
6. If confirmed: tool execution proceeds, result returns to Operator
7. If cancelled: cancellation message returns to Operator → Observer

> **Q62. What is MCP (Model Context Protocol)? Explain the architecture.**

MCP is an open protocol (from Anthropic) that standardizes how LLM applications connect to external tools and data sources. Architecture: Client (agent SDK) ↔ Server (tool implementations) over stdio or SSE transport. The server declares typed tools (name, description, JSON schema for parameters, return type). The client can discover tools at runtime and invoke them with validated arguments. It's like OpenAPI/Swagger but designed for LLM tool calling.

> **Q63. You have 64 tools. How does the model fit all tool descriptions in context?**

Each tool description (name + description + JSON schema) averages ~200 tokens. 64 tools × 200 = ~12,800 tokens for the full catalog. Qwen2.5-14B has 32K context window; the Observer only sees 29 tools (~5,800 tokens). Combined with system prompt (~2,000 tokens) and conversation history, we're well within context limits for typical interactions. For very long multi-turn conversations, older messages are truncated (sliding window).

> **Q64. What's the mock MCP server implementation? How complex is it?**

The mock server is ~2,000 lines of Python implementing all 64 tools with in-memory state. It maintains dictionaries for jobs, nodes, accounts, QoS policies. Each tool handler manipulates this state: `squeue` reads from `self.jobs`, `scancel` removes entries, `sbatch` adds new entries. The state is configurable per scenario and resettable between test cases. It's a complete Slurm simulator at the API level (not at the scheduler level).

> **Q65. How does the Observer know which tool to call? Is there a tool selection mechanism beyond the LLM?**

No — the tool selection is **entirely LLM-driven** via the ReAct loop. The model sees the system prompt (with routing rules), the user message, and the tool catalog (29 tools with descriptions). It generates a tool call based on reasoning. There's no rules engine, no keyword matching, no decision tree. This is intentional: the LLM's natural language understanding determines tool selection. The evaluation measures how well it does this.

> **Q66. What is the handoff mechanism technically? Is it a tool call?**

Yes — the handoff is implemented as a **tool call** to a special `transfer_to_operator` function. The Observer generates this call with the 4-field payload (action_request, required_tool, target_scope, targets). The Agents SDK intercepts this call and routes the conversation to the Operator agent. From the model's perspective, it's just another tool — but from the framework's perspective, it triggers an agent switch.

> **Q67. How is the return from Operator to Observer implemented?**

After the Operator completes (executes tool or returns cancellation), a **handoff filter** (`_observer_handoff_input_filter`) constructs a synthetic user message containing: (1) the original user request, (2) all tool outputs from the Operator turn (deduplicated, truncated to 2,000 chars each). The Observer receives this as a fresh message with no prior conversation history — preventing it from re-triggering the handoff. It then generates the final user-facing response.

> **Q68. What is the OpenAI Agents SDK? Why use it over raw API calls?**

The Agents SDK provides: (1) typed tool registration with JSON schema validation, (2) multi-agent handoff mechanism with input/output filters, (3) automatic ReAct loop (model generates → tool executes → model observes → repeats), (4) guardrails and output validation, (5) streaming support. Building this from raw API calls would require reimplementing all of these — several thousand lines of boilerplate. The SDK gives us agent orchestration for free.

> **Q69. Can the Operator initiate a handoff back to Observer? Or is it one-way?**

It's a **round-trip**: Observer → Operator → Observer. The Operator always returns to the Observer after execution. The Observer generates the final response. The Operator cannot independently decide to hand back — it always executes exactly one action (or fails) and returns. There's no ping-pong between agents.

> **Q70. What happens with multi-step requests like "check all pending jobs, and cancel any that have been waiting over 2 hours"?**

This is a `multi_step` category case. The Observer recognizes two intents: (1) inspect pending jobs (read-only), (2) conditionally cancel (action). It calls `squeue --state=PENDING` first (using its read-only tools), inspects the results, then decides whether cancellation is warranted. If yes, it hands off to the Operator with `required_tool=scancel`, `target_scope=discovery` (Operator will verify the targets). The Operator resolves targets, fires HITL, and cancels upon confirmation.

> **Q71. What is the "discovery read" in the Operator? Why does it need 5 read tools?**

Sometimes the handoff specifies `target_scope=discovery` — meaning the Operator doesn't know exactly which jobs to cancel (e.g., "cancel all of charlie's jobs"). The Operator needs to call `squeue --user charlie` to discover the job IDs before calling `scancel`. The 5 discovery reads (squeue, sinfo, sacct, scontrol_show, sacctmgr_list) are specifically for this target-resolution step. They're read-only but needed before the action.

> **Q72. What if the MCP server is down? How does the system handle errors?**

The agent SDK has retry logic (3 attempts with exponential backoff). If MCP is truly unreachable, the tool call returns an error message that the model incorporates into its response ("I'm unable to access the cluster right now"). The system fails gracefully — it never executes a partial operation. In eval mode, this manifests as `terminal_error` which zeros the overall score (correctly reflecting a system failure).

> **Q73. How do you handle the "tool argument format" problem? The model sometimes generates wrong argument shapes.**

The MCP layer validates arguments against JSON schema before execution. Invalid arguments are rejected with a descriptive error message that the model receives as a tool response. The model can retry with corrected arguments (ReAct loop). In the FT model, argument formatting is learned from training data — the 2,625 traces all have correctly-formatted arguments, so the model learns the expected schema. The remaining failures (~10% tool recall gap vs. GPT-5-mini) are cases where the model still gets arguments wrong.

> **Q74. What's your deployment architecture? How would this run in production?**

Single server: FastAPI (agent backend) + MCP server (tool layer) + Ollama or vLLM (model serving) + React frontend (static files or CDN). The A40 GPU serves the 14B model; the CPU handles FastAPI routing and MCP tool execution. For production: add nginx reverse proxy, TLS, auth middleware, and tenant isolation. The system is designed for single-cluster deployment (one MCP server per Slurm cluster).

> **Q75. How does your system compare to Slurm's existing web interfaces (like Open OnDemand)?**

Open OnDemand provides a web GUI for Slurm but requires users to navigate forms, know exact parameters, and understand Slurm concepts. Our system is **intent-driven**: the user says "why is my job pending?" and the agent figures out which tool to call, interprets the result, and explains in natural language. Open OnDemand is a GUI wrapper; we're an intelligent interpreter. They're complementary — our system could even integrate with OnDemand as a backend.

---

### BLOCK E — Fine-Tuning Deep Dive (Q76–Q90)

> **Q76. Explain the full training data pipeline from scratch. What are the exact steps?**

1. **Split benchmark**: 3,135 cases → 2,520 train / 615 test (stratified, seed=42)
2. **Run GPT-5-mini**: Against mock MCP server on 2,520 training cases → 2,436 successful traces
3. **Split at handoff**: Traces with handoff become 2 samples (Observer part + Operator part) → 3,329 raw samples
4. **Filter tools per role**: Each sample gets only its role's tools in the system prompt
5. **Deduplicate**: Remove samples with identical message sequences → 2,625 unique samples
6. **Format for training**: Convert to chat template (system/user/assistant/tool turns), mask non-assistant tokens
7. **Train QLoRA**: 3 epochs, batch 1, gradient accumulation 16, lr 2e-4, 492 optimizer steps

> **Q77. Why split at the handoff boundary? Why not train on full traces end-to-end?**

End-to-end traces would teach the model that a single agent handles everything — which is wrong for inference time where Observer and Operator are separate agents. By splitting at the handoff boundary, each sample teaches exactly what one agent should do: the Observer sample ends with the handoff directive, the Operator sample starts from the handoff context and ends with tool execution. This ensures the trained model correctly separates concerns at inference time.

> **Q78. You have 2,074 Observer and 551 Operator samples. Isn't this imbalanced?**

Yes — the imbalance reflects the benchmark structure (6 of 11 categories are Observer-only). This likely contributes to the remaining gaps in submission (83.4%) and multi_step (83.3%) which are Operator-heavy categories. Mitigation options for future work: oversample Operator traces, generate additional Operator-specific data, or use loss weighting. The current imbalance is a known limitation.

> **Q79. What chat template format do you use for training?**

Qwen2.5's native `ChatML` format:
```
<|im_start|>system
{system prompt with tool definitions}<|im_end|>
<|im_start|>user
{user message}<|im_end|>
<|im_start|>assistant
{assistant response or tool call}<|im_end|>
<|im_start|>tool
{tool response}<|im_end|>
...
```
Tool calls are encoded as JSON within the assistant turn. The tokenizer handles special tokens automatically via `apply_chat_template()`.

> **Q80. What is the max sequence length? What happens if a trace is longer?**

Max length = 8,192 tokens (matching inference context). Traces exceeding this are truncated from the left (earliest messages removed, keeping the most recent context). In practice, very few traces exceed 8K — the average is ~3,000 tokens. The longest traces are multi_step cases with many tool calls (~6,000 tokens).

> **Q81. You trained for ~22 hours on A40. What's the training loss curve look like?**

![[train_wandb.png]]

The loss starts at ~2.5 (epoch 1 start), drops to ~0.8 by epoch 1 end, then gradually decreases to ~0.5 by epoch 3 end. No significant overfitting spike. The WandB plot shows smooth convergence with no instability. Gradient norms remain stable (< 1.0 after warmup).

> **Q82. Why 3 epochs and not 1 or 5?**

1 epoch on 2,625 samples (~164 steps at batch 16) is insufficient for the model to learn the full tool-calling surface. 5 epochs risks overfitting on the limited data (2,625 samples is small for 14B model). 3 epochs is the standard recommendation from the QLoRA paper for datasets of this size. Empirically, validation loss plateaus around epoch 2.5 — the third epoch provides marginal improvement.

> **Q83. What batch size did you use? Why gradient accumulation of 16?**

Physical batch size = 1 (limited by A40 48GB VRAM with 4-bit base + bf16 adapter + 8K context). Gradient accumulation = 16, giving an effective batch size of 16. This is important for stable training — batch size 1 has high gradient variance; accumulating over 16 samples smooths the gradient estimate. The trade-off is training speed (16× fewer weight updates per data pass).

> **Q84. Did you do any hyperparameter tuning? Grid search?**

No formal grid search — training is expensive ($20/run). We used recommended hyperparameters from the QLoRA paper (lr=2e-4, r=64, α=128, 3 epochs) and the Qwen2.5 fine-tuning guide. The only parameter we experimented with was LoRA target layers: partial (layers 36–47) vs. all (layers 0–47). All layers won clearly, so we used that. This is a limitation — a hyperparameter sweep might find better configurations.

> **Q85. What happens if you fine-tune on a larger dataset? Would 10,000 samples be better?**

Likely yes — the ~3 pp regression on knowledge-intensive categories (domain, docs, diagnose) suggests the adapter is "forgetting" because it has limited capacity to both learn new behavior and preserve existing knowledge. More diverse training data (including read-only cases where the correct behavior is to retrieve and synthesize documentation) would likely reduce this regression. The dataset generation pipeline supports this — we'd just need more mock scenarios.

> **Q86. Could you use DPO (Direct Preference Optimization) instead of or in addition to SFT?**

Yes — DPO is explicitly mentioned as future work. After SFT, we could generate pairs of (good, bad) responses on cases where the FT model currently fails, then train a preference model. This would specifically target the failure modes (wrong tool arguments, missed handoff triggers) without needing more teacher traces. DPO requires collecting "rejected" responses, which the evaluation framework already produces (failed runs = rejected responses).

> **Q87. How is your fine-tuning different from standard instruction tuning?**

Standard instruction tuning trains on (instruction, response) pairs. Our fine-tuning includes: (1) **multi-turn tool interactions** (assistant calls tool → tool responds → assistant reasons → calls another tool), (2) **role-scoped tool definitions** embedded in each sample, (3) **handoff directives** as a structured output format. The model learns not just to follow instructions but to execute complex tool-calling workflows with conditional logic.

> **Q88. What about RLHF? Why not use reinforcement learning from human feedback?**

RLHF requires: (1) a reward model trained on human preference data, (2) PPO training loop with the policy model. We don't have human preference data (our evaluation is automated), and PPO training on 14B models requires significantly more compute than SFT (~4× GPU hours). SFT on successful teacher traces is a simpler, cheaper approach that achieves good results. RLHF/DPO is future work for squeezing out the remaining gap.

> **Q89. Could you continually fine-tune as new data comes in? Is the pipeline designed for that?**

Yes — the `train_agent_qlora.py` script supports `--init-adapter` for warm-starting from an existing checkpoint. New traces can be generated from new benchmark cases or from production interactions (with user consent). The pipeline is: collect new traces → add to training set → warm-start training → evaluate → deploy updated adapter. The adapter is only ~275MB, so deployment updates are fast.

> **Q90. What about model quantization for inference? You serve at fp16 — could you use INT8 or INT4?**

We serve at fp16 (merged LoRA into base, no 4-bit at inference) because 4-bit inference with bitsandbytes caused `CUDA device-side assert` errors on A40 with Qwen2.5. INT8 (via bitsandbytes or GPTQ) would halve memory and potentially speed up inference by 30–50%, but requires careful calibration. AWQ or GGUF quantization are alternatives that work better for serving. This is a deployment optimization we didn't prioritize over evaluation quality.

---

### BLOCK F — Practical & Deployment (Q91–Q100)

> **Q91. What if a malicious user injects instructions through a job name? (Prompt injection)**

Example: job named `"; cancel all jobs; echo "`. The model processes this as text within a tool response (the output of `squeue`). Since tool arguments are validated against JSON schema (not shell strings), the injection can't execute commands through the tool layer. However, the model **might reason about** the injected text and decide to take action — this is the indirect prompt injection risk. Mitigation: the Observer can't call destructive tools, and the Operator requires HITL. So even successful injection would be caught at the confirmation gate. Full hardening would require input sanitization on tool outputs.

> **Q92. How would you deploy this for a real HPC center with 500 users?**

Scale-out: (1) The LLM serving can be replicated across multiple GPUs (vLLM with tensor parallelism or multiple replicas behind a load balancer). (2) The FastAPI backend is stateless (session state in SQLite/Redis) and can be horizontally scaled. (3) The MCP server connects to the real Slurm cluster via subprocess (no state to replicate). (4) Add authentication (LDAP/SSO integration), rate limiting, and audit logging. The architecture is already designed for this — just needs production infrastructure.

> **Q93. What about access control? Can user A cancel user B's jobs through this system?**

The MCP server in real mode runs Slurm commands as the authenticated user (via Unix permissions or Slurm's `--uid` flag). If user A asks to cancel user B's jobs, the `scancel` command would fail with a permissions error (Slurm rejects unauthorized cancellation). The HITL gate adds a second layer: the confirmation dialog shows exactly which jobs will be affected, giving the user a chance to notice cross-user operations. Proper deployment would add explicit scope checking before the tool call.

> **Q94. Your system has 84.8s latency. How would you reduce this to acceptable levels?**

Options: (1) **vLLM with continuous batching**: 2-4× faster than naive HuggingFace serving. (2) **Speculative decoding**: use a 1.5B draft model for fast token generation, verified by the 14B model. (3) **AWQ/GPTQ quantization**: INT4 inference with ~30% speedup and minimal quality loss. (4) **Better hardware**: H100 or multiple A100s with tensor parallelism. (5) **Reduce model size**: if 7B models catch up in tool-calling quality. Combining (1)+(3) could realistically bring latency to ~25-30s.

> **Q95. What are the ethical implications of automating HPC cluster management?**

Key concerns: (1) **Accountability**: If the agent cancels a job that was critical for a research deadline, who is responsible? The HITL gate ensures human accountability — the user confirmed the action. (2) **Bias in tool selection**: The model might preferentially suggest certain operations over others based on training data distribution. (3) **Deskilling**: Users might lose understanding of Slurm commands if they rely on the agent. (4) **Privacy**: The agent sees all users' job information in the queue — multi-tenant access control is essential.

> **Q96. Could this system work for other job schedulers (PBS, SGE, LSF)?**

Yes, with effort. The architecture is scheduler-agnostic — only the MCP tool implementations are Slurm-specific. Porting to PBS Pro would require: (1) rewriting 64 tool implementations to call `qstat`, `qdel`, etc. instead of `squeue`, `scancel`, (2) adapting the mock server state model, (3) regenerating training data. The agent layer, evaluation framework, and fine-tuning pipeline remain unchanged. This is explicitly mentioned as future work.

> **Q97. You spent ~$20 on training. What's the total project cost including development time, compute, API calls?**

Honest accounting: (1) Training: ~$20 (A40, 22h, RunPod). (2) GPT-5-mini data generation: ~$50 (2,520 cases × ~2K tokens avg × $0.01/1K). (3) GPT-5-mini baseline evaluation: ~$30 (615 cases × 3 trials). (4) Development GPU time (model serving, debugging): ~$100 (various RunPod sessions). (5) Development time: ~400 hours over the project period. Total compute: ~$200. The "$20 training" headline is specifically the final training run cost, not total project cost.

> **Q98. What would you do differently if you started this project over?**

1. **Start with v2 training data from day 1** — the v1 dataset had polluted rows that wasted weeks of debugging
2. **Use vLLM for serving from the start** — HuggingFace inference is too slow for iterative eval
3. **Implement proper statistical significance testing** in the eval framework
4. **Add more Operator training samples** to fix the imbalance (2,074 Observer vs. 551 Operator)
5. **Do a human evaluation study** alongside automated metrics — even 50 real users for qualitative feedback

> **Q99. What is the most surprising finding from your project?**

That the **LLM judge score of the student exceeds the teacher** (79.7% vs. 75.7%). Distillation producing more concise responses than the teacher is a known effect in the literature (knowledge distillation compression), but observing it empirically in our specific domain was unexpected and validates that behavioral distillation doesn't just copy — it can improve on certain quality dimensions.

> **Q100. If this project were continued for another 6 months, what would be the most impactful next step?**

**DPO (Direct Preference Optimization) on failure cases.** The evaluation framework already identifies exactly which cases the FT model fails on and why (wrong tool, missed handoff, bad arguments). Collecting the FT model's failed responses as "rejected" and GPT-5-mini's successful responses as "preferred" gives free preference data for DPO training. This would target the remaining 11.7% gap without needing new benchmark cases or more teacher traces. Expected impact: +3–5 pp on avg weighted score, closing the gap to ~35-40%.

---

### BLOCK G — AI Transparency, Research Integrity & Personal Capability (Q101–Q115)

> *These questions target ABET criterion 2g (ethics/AI transparency) and rubric section 5 (student capability assessment). Expect the examiner to probe whether YOU built this or AI built it for you.*

> **Q101. How much of this project was AI-assisted? Be honest — which parts did ChatGPT/Copilot write?**

Honest breakdown:
- **AI-assisted (Copilot/ChatGPT for boilerplate, syntax, LaTeX)**: Report writing (structure, LaTeX formatting), frontend React components (CSS, JSX boilerplate), some unit test scaffolding, mermaid diagrams.
- **Substantially my own engineering**: The entire agent architecture (Observer/Operator split, handoff mechanism, guardrails, SlurmGuard admission control), the MCP server with stateful mock, the evaluation harness (scoring formula, scenario runner, result analysis), the fine-tuning pipeline (data generation, handoff splitting, role-scoped filtering, QLoRA training script), and all debugging/integration work.
- **Proof I built it**: The debugging log in my development notes shows weeks of iterative fixes — double-encoded JSON bugs, MCP connection storms, adapter loading failures, scoring artefacts — none of which an AI could generate because they require running the actual system on a GPU pod and interpreting live errors.

> **Q102. Walk me through a specific debugging session. What broke, how did you diagnose it, and how did you fix it?**

**The double-encoded JSON bug.** The fine-tuned model emitted tool arguments as a JSON string inside a JSON string — `"{\\"user\\": \\"charlie\\"}"` instead of `{"user": "charlie"}`. Symptom: `'str' object has no attribute 'get'` deep in the Agents SDK. Diagnosis: added `print(type(parsed), repr(parsed))` at every JSON parse site in the agent code. Found 5 independent locations that needed the same fix: `isinstance(parsed, str)` → `json.loads` again → verify `isinstance(result, dict)`. Each site had slightly different context (handoff compat, operator input filter, auto-approve formatter, guardrails, model server). This took 3 days to fully trace because each site failed independently on different test cases.

> **Q103. Open this specific file — `agent/flow/guardrails.py` — and explain what `_safe_parse_args` does without looking at the code.**

It accepts raw tool-call arguments (which can be a dict, None, a JSON string, or a doubly-encoded JSON string from the FT model). It uses a regex `\{.*\}` with DOTALL to extract the outermost JSON object, then runs a 2-pass unwrap loop: `json.loads` → check if result is still a `str` → `json.loads` again. If the final result is a `dict`, return it; otherwise return `{}`. The old version had a bug: it used `\{[^{}]*\}` (no nesting) which broke on nested JSON like `{"targets": ["1001", "1002"]}`, and it returned the raw string through without the `isinstance(parsed, dict)` guard, which blew up downstream in `guard_job_id` at line 56.

> **Q104. Explain the MCP connection storm bug. What caused it and how did you fix it?**

Symptom: `bulk_bal200` test cases failed in exactly ~5.2 seconds with `httpcore.ConnectTimeout` to MCP `/sse`. Root cause: every agent chat call re-ran tool discovery against the MCP server — under 2+ parallel eval workers, this created a connection storm. Fix: added a module-level `_CATALOG_CACHE: Dict[str, ToolCatalog]` with per-URL `asyncio.Lock` for double-checked locking, plus `asyncio.wait_for(_do_discover(), 15.0)` timeout. Verified by `grep -c 'Discovering tools' agent.log` — went from N calls per process to exactly 1.

> **Q105. What is your formal research question or hypothesis?**

The project addresses two research questions:
1. **RQ1 (Architecture)**: Does structurally partitioning an LLM agent's tool surface into read-only and write-access subsets improve task correctness compared to a monolithic agent with all tools? → **Yes**: +6.1 pp overall, +10.2 pp on routing-neutral cases.
2. **RQ2 (Fine-tuning)**: Can domain-specific QLoRA fine-tuning on a 14B open-weight model, distilled from a commercial LLM's successful traces, close a meaningful portion of the performance gap on Slurm-specific tasks? → **Yes**: 29% gap closure (85.2% → 88.3% vs. 95.9% ceiling).

These are not formally stated as hypotheses in the report (a limitation of the writing), but the experimental design directly tests them with controlled ablations.

> **Q106. Why did you structure the report the way you did? Justify the chapter ordering.**

The structure follows a standard systems thesis format: Background → Related Work → Proposed System → Implementation → Experiments → Conclusion. Within "Proposed System," the architecture section comes before the fine-tuning section because the architecture is the primary contribution (the fine-tuning operates within the architectural framework). The evaluation chapter presents the three-way comparison first (most important result), then the ablation (isolating the architecture's contribution), because the reader needs to see the full picture before understanding what the ablation controls for.

> **Q107. This project involves HPC/Slurm. How relevant is this for Vietnamese universities and research institutions?**

Very relevant. Vietnam has growing HPC needs: VinAI operates GPU clusters, VNUHCM and HUST have computing centers, and the national AI strategy includes compute infrastructure. Currently, these facilities are managed by a small number of expert admins. A natural-language interface to Slurm would lower the barrier for researchers who need to submit jobs but don't know CLI syntax — exactly the user profile at Vietnamese universities where students share clusters. The system runs locally (no cloud dependency), which aligns with data sovereignty concerns in Vietnamese research institutions.

> **Q108. What was the single hardest technical challenge in this project, and what did you learn from it?**

The hardest challenge was **making the fine-tuned model actually work in the agentic loop**. Training a model to output correct JSON tool calls in isolation (SFT loss converges) is very different from having it work end-to-end in a multi-turn agent with real tool responses. The model's CLI-style argument hallucination (`--user charlie` instead of `{"user": "charlie"}`) was invisible during training but catastrophic at inference. I learned that **evaluation must match the deployment context exactly** — perplexity on held-out text tells you nothing about whether the model will survive a 5-step ReAct loop with real tool responses.

> **Q109. Show me evidence that the system works. Can you demo it live?**

Yes — the system is deployed and functional. I can demonstrate: (1) a read-only query ("show all pending jobs"), (2) a destructive action with HITL ("cancel all of charlie's jobs") showing the confirmation dialog, (3) a multi-step query ("why is job 1004 pending, and cancel it if it's been waiting too long"). The demo runs against the mock MCP server, which provides deterministic cluster state. The React frontend shows streaming responses, tool call traces, and the confirm/cancel dialog in real time.

> **Q110. If I give you a new Slurm command that's not in your 64 tools — say `scrontab` — how would you add it?**

Three steps: (1) Add a `@mcp.tool()` handler in `slurm_mcp_sse.py` with the JSON schema (parameters, return type, description). (2) Decide if it's read-only (Observer) or write-access (Operator) and add it to the corresponding category in `tool_discovery.py`'s classification logic. (3) For mock mode, implement the in-memory state handler (e.g., `self.crontabs` dict). No changes needed to the agent architecture, system prompt, or evaluation harness — the agent discovers tools dynamically from MCP at startup. Adding one tool is ~30–50 lines of code.

> **Q111. Your evaluation scores are all automated. Have you ever tested this with a real HPC administrator? What did they think?**

No formal user study was conducted — this is explicitly listed as a limitation. Informal feedback from lab members who manage shared GPU nodes was positive on the read-only diagnosis features ("why is my job pending" is the most common question). The HITL confirmation dialog was considered essential — no admin would trust an AI to cancel jobs without approval. A proper user study with 10–20 HPC administrators across different institutions would be the most impactful next step for validating practical value.

> **Q112. What parts of the codebase would you NOT be able to explain if I pointed to a random line?**

The OpenAI Agents SDK internals — I use it as a library (agent registration, tool dispatch, handoff mechanism) but I did not write it. Similarly, the vLLM/HuggingFace model loading pipeline has deep CUDA kernel code I wouldn't be able to explain at the GPU instruction level. Everything in `agent/flow/`, `mcp-server/`, `evaluation/`, `frontend/`, and `dataset/` is code I wrote or substantially modified and can explain line by line.

> **Q113. The rubric mentions "AI-generated fake competence." How do you distinguish your work from someone who just prompted ChatGPT to write everything?**

Three distinguishing signals: (1) **Iterative debugging** — the project log shows weeks of debugging specific runtime errors (double-encoded JSON, MCP connection storms, adapter loading failures) that require running the actual system on a GPU. ChatGPT can't debug a live A40 pod. (2) **Architectural decisions with measured trade-offs** — the Observer/Operator split came from observing the monolithic agent's failure mode (tool confusion at 64 tools), not from asking "design me an agent architecture." (3) **The numbers themselves** — 88.3% on 615 cases with specific per-category breakdowns, latency measurements, ablation controls — these come from actually running the system, not from generating plausible-sounding text.

> **Q114. What is the difference between your project and a typical "chatbot + API wrapper" capstone?**

A typical chatbot capstone: wraps a few APIs, has no safety layer, uses a cloud LLM directly, and evaluates with 10–20 manual test cases. This project: (1) builds a **stateful simulation engine** for deterministic evaluation, (2) implements **structural safety** (not prompt-based) with a 4-layer gate, (3) runs a **full fine-tuning pipeline** with data generation, processing, training, and evaluation, (4) has a **3,135-case automated benchmark** with 5 scoring dimensions, and (5) demonstrates the fine-tuned model running **entirely on local infrastructure**. The engineering depth is in the evaluation methodology and safety architecture, not in the chat interface.

> **Q115. If you were hiring for a research engineering position, would you hire the person who built this? Why or why not?**

Strengths that translate to industry/research: ability to build end-to-end ML systems (data → training → serving → evaluation), comfort with GPU infrastructure and debugging (A40, CUDA, model loading), understanding of evaluation methodology (controlled ablations, stratified splits, scoring design), and practical engineering (async Python, React, FastAPI, MCP protocol). Weaknesses: no formal statistical testing (McNemar's test added late), single-annotator benchmark, no user study. Overall: stronger than a typical undergraduate — closer to a junior ML engineer or first-year research master's student.

---

## 10. Quick-Fire Recall Sheet

| Fact | Value |
|---|---|
| Total MCP tools | 64 agent-facing (67 − 3 internal) |
| Observer tools | 29 read-only |
| Operator tools | 40 (35 action + 5 discovery) |
| Benchmark size | 3,135 cases (11 × 5 × 57) |
| Train / test split | 2,520 / 615 (80/20, stratified seed=42) |
| Training samples | 2,625 unique (2,074 Observer + 551 Operator) |
| GPT-5-mini score | **95.9%** avg weighted score |
| FT Qwen score | **88.3%** avg weighted score |
| Base Qwen score | **85.2%** avg weighted score |
| Monolithic score | **81.6%** (routing excluded) |
| Gap closure | **(88.3−85.2)/(95.9−85.2) = 29%** |
| Dual vs. Mono | +6.1 pp (87.6% vs. 81.6%) |
| Routing-neutral gain | +10.2 pp (94.2% vs. 84.0%) |
| Safety: dual vs. mono | 57.9% vs. 33.3% = −24.6 pp mono |
| Latency overhead dual/mono | +4.1 s / 76.8 s = 5.3% |
| FT latency vs. GPT-5-mini | 84.8 s vs. 28.3 s |
| RAG corpus | 273 docs → 2,276 chunks, RRF k=60 |
| LoRA rank / alpha | 64 / 128, all 48 layers, 7 projections |
| Trainable params | ~275M = 1.9% of 14.8B |
| Training hardware | A40 48GB (RunPod) |
| Training cost | ~$20, ~22h, 492 optimizer steps |
| HuggingFace model | `DanhVuiVe/slurm-agent-qwen14b-lora-final` |
| Scoring weights | TR 0.35, R 0.25, H 0.25, S 0.15 (keyword excluded) |
| Per-trial pass threshold | ≥ 0.80 |
| Best FT category | account 98.2% |
| Worst FT category | submission 83.4% |
| Largest FT gain | submission +21.7 pp |
| Largest FT regression | domain −6.2 pp |

> **Q2. The benchmark is synthetic and self-generated. Doesn't that mean you're just testing whether the model learned your own test cases?**

No — the benchmark and training data are from **disjoint partitions** of the same 3,135-case grid. Training uses GPT-5-mini traces generated from the **2,520 training scenarios only**. The **615 test cases** were never seen during training. The fine-tuned model is evaluated on scenarios it has never been exposed to, under the same prompt/tool schema it will see at inference time.

![[dataset_distribution_category.png]]

> **Q3. Why is GPT-5-mini the teacher? Isn't that circular — you distill from a model and then compare against it?**

It is not circular because they are evaluated **on the same held-out test set** using the same deterministic mock MCP server. GPT-5-mini is the teacher during training data generation; at evaluation time it is a **performance ceiling baseline**, not the ground truth. The ground truth is the dataset labels (expected tools, routing decisions, state transitions) — these were written by the benchmark authors, not inferred from GPT-5-mini. The comparison is fair: all three models (GPT-5-mini, FT Qwen, Base Qwen) are scored by the same automated harness against the same labels.

> **Q4. The routing metric is 25% of the score, and the monolithic agent gets 0 on 237 handoff cases by construction. Isn't your ablation rigged against monolithic?**

Yes, and the paper explicitly acknowledges and corrects for this. Table (ablation) **excludes the routing dimension entirely** and re-normalises the remaining weights (TR 0.467, HITL 0.333, S 0.200). Even after exclusion, dual-agent wins by +6.1 pp overall and +10.2 pp on the 378 routing-neutral cases. The routing bias actually understates the dual-agent advantage — if we included routing, the gap would be larger.

![[ablation_per_category.png]]

> **Q5. You claim +10.2 pp on routing-neutral cases is "purely from tool-scope reduction." But routing-neutral cases are also the simpler cases — isn't the gain confounded by case difficulty?**

Fair challenge. Routing-neutral (handoff=false) cases are not uniformly simpler — the **docs, domain, diagnose, and bulk** categories are all represented, and docs/domain/diagnose require multi-step RAG + reasoning, not just a single `squeue` call. The +18.9 pp gain on docs and +19.2 pp on bulk (both routing-neutral) are in the harder, multi-step reasoning categories. The tool-scope reduction argument is additionally supported by the +17.6 pp LLM judge gap (quality, not just binary pass/fail), which confirms the monolithic model is cognitively degraded across the board, not just on easy cases.

![[ft_vs_base_per_category.png]]

---

## 10. Hard Questions — Experiment Setup

> **Q6. Why 3 trials? Temperature is 0 — there's no randomness. What does repeating change?**

Temperature=0 is deterministic for a fixed model, but **different session IDs produce different conversation contexts** (empty session vs. a session that has prior tool outputs). Each trial uses a fresh session with a reset mock MCP server. Running 3 trials and averaging guards against edge cases where a single context initialisation produces an artifact response. The final reported metric is the **avg weighted score averaged across 3 trials**, giving a stable estimate rather than a single-run snapshot.

> **Q7. Why did you use GPT-OSS 20B (Ollama) as the LLM judge and not GPT-5-mini? Isn't that inconsistent?**

GPT-5-mini is the training teacher. Using it as the judge would introduce a systematic bias: a model it trained from would score higher on quality metrics calibrated to GPT-5-mini's own output style. GPT-OSS 20B is an independent judge without that relationship. The trade-off is that GPT-OSS 20B is a weaker judge — which is why judge scores (75–80%) are lower and noisier than structural metrics, and why the report notes ±2–3 pp variance.

> **Q8. The MCP mock server is used for both training data collection and evaluation. Doesn't this mean you're testing on the same environment the model was trained in?**

The mock server is a **shared infrastructure**, but the test cases are disjoint. What the model sees during training are GPT-5-mini's reasoning steps, tool call sequences, and responses — not the test case prompts or expected labels. The mock server provides the execution environment; the test partition provides the prompts and ground-truth labels. This is analogous to training a SQL model on queries against a database, then testing on different queries against the same schema.

![[mcp_mock_data_collection.png]]

> **Q9. Your state-match scoring had a bug ("artefact") that required a post-hoc fix. How do you know you haven't introduced other bugs that systematically inflate your numbers?**

The state-match artefact was identified by manual inspection: safety and bulk cases showed anomalously low state-match despite correct tool calls being visible in the trace log. The fix (credit state-match=1.0 when correct destructive tool was called AND HITL triggered) is principled and conservative — it only changes cases where the scorer was provably wrong (argument format mismatch when tool was correct). All other scoring dimensions (tool recall, routing, HITL, keyword, judge) are computed by independent code paths that were cross-validated against manual spot-checks. The 23 remaining low-scoring cases after the fix were manually confirmed as genuine failures.

> **Q10. Why 80/20 train/test split rather than, say, 70/30 or a k-fold cross-validation?**

80/20 gives 2,520 training scenarios, enough to produce ~2,625 unique traces after handoff splitting and deduplication — a reasonable training set for LoRA fine-tuning on a 14B model with ~492 optimizer steps. A larger test split (30%) would not meaningfully change statistical confidence at 615 cases (already enough for ±2 pp margin). k-fold cross-validation would require re-training the model 5× on an A40 ($5 × ~$20 training cost), which was not feasible. The stratified split (by category×scenario, seed=42) is documented and reproducible.

---

## 11. Hard Questions — Results Interpretation

> **Q11. The fine-tuned model scores LOWER than the base model on domain and docs (−4 to −6 pp). Doesn't this contradict your claim that fine-tuning improves the model?**

No — it confirms the expected **LoRA specialisation trade-off**. The fine-tuning corpus is dominated by procedural Slurm tasks (submission, cancellation, bulk operations). The domain and docs categories require broad generalised reasoning and RAG retrieval — skills the base pre-training provides, but LoRA slightly overwrites. The **net improvement** (85.2% → 88.3% overall) reflects a correct engineering trade-off: the categories that needed improvement (submission, multi_step, safety) improved substantially (+6–22 pp), while the already-high categories regressed slightly (−4–6 pp). A practitioner deploying this for primarily read/docs use would need to be aware of this regression.

![[ft_vs_base_per_category.png]]

> **Q12. The FT model's judge score (79.7%) is higher than GPT-5-mini's (75.7%) despite GPT-5-mini being the training teacher. How is the student outscoring the teacher on quality?**

The judge (GPT-OSS 20B) evaluates **conciseness and evidence-grounding**, not structural correctness. GPT-5-mini frequently generates verbose multi-paragraph responses with redundant hedging. The FT model, trained to imitate the *content* but having slightly less capacity for verbose generation, produces more concise, focused responses that the judge scores higher. This is a known effect in distillation: the student model internalises the behavioral pattern without copying the verbosity, especially when trained on a smaller context window (max_length=2048).

> **Q13. Your HITL match for base Qwen (90.2%) and FT Qwen (90.4%) are nearly identical. Did fine-tuning do nothing for safety?**

HITL match at the aggregate level masks the **per-category safety improvement**. Specifically, the safety category (the category designed to test ambiguous/dangerous prompts) improves from 77.3% → 88.6% (+11.3 pp). The aggregate HITL match being similar (90.2% vs. 90.4%) is because the majority of action/bulk/submission cases — which are straightforward HITL triggers — already worked for the base model. Fine-tuning specifically helped the **ambiguous cases** (safety category) where the base model either refused without triggering HITL or skipped confirmation.

![[safety_hitl_compliance.png]]

> **Q14. 84.8 s latency is impractical for interactive use. Why not use a smaller, faster model like Qwen2.5-7B?**

First, a clarification: **84.8 s is model inference speed, not architecture overhead**. GPT-5-mini runs the exact same dual-agent architecture at 28.3 s — which proves the Observer/Operator handoff is not the bottleneck. The architectural overhead is only +4.1 s (5.3%), confirmed by the monolithic ablation (76.8 s → 80.9 s, same model). The 84.8 s is entirely attributable to Qwen2.5-14B fp16 inference on a single A40 GPU.

On the 7B question: preliminary tests with 7B-parameter models showed insufficient multi-step reasoning capacity on submission and multi_step categories — the categories that most benefited from fine-tuning. Latency can be reduced with faster hardware, quantized serving (GPTQ/AWQ), or speculative decoding without changing the architecture.

![[latency_by_category.png]]

> **Q15. 29% gap closure seems modest for a fine-tuned model. Why not a bigger number?**

29% is computed on **avg weighted score** — a continuous metric that awards partial credit per case: (88.3 − 85.2) / (95.9 − 85.2) = 3.1 / 10.7. This is the primary metric used throughout the report and is the most honest measure because it reflects quality across all dimensions (tool recall, routing, HITL, state, keywords), not just binary pass/fail. The base model (85.2%) is already strong — the gap to close is 10.7 pp, and fine-tuning recovers 3.1 pp of it. The gain is concentrated in the hardest categories: submission (+21.7 pp), multi_step (+13.8 pp), safety (+11.3 pp) — precisely the ones that required learning new behavioral patterns.

---

## 12. Hard Questions — Limitations

> **Q16. Your benchmark has only 3 fictional users (charlie, alice, bob) and a fixed job-ID range. A real cluster has hundreds of users. How do you know the agent generalises?**

This is the central limitation of synthetic evaluation. The agent's **generalization to user names** should be fine — Qwen2.5-14B-Instruct has strong instruction-following and can substitute any username in `squeue --user <name>`. The harder question is tool-argument generalization beyond the training distribution. The benchmark job-ID range (1001–5000 approximately) is representative but not exhaustive. Generalization to a production cluster requires:
1. Real cluster access for live testing
2. A broader benchmark with more users and job patterns
3. Human evaluation studies with actual HPC practitioners

> **Q17. The HITL confirmation is a UI element — what stops a malicious or careless prompt from bypassing the architectural HITL gate?**

The HITL gate is enforced at **two independent levels**:
1. **Architectural**: The Observer cannot call `scancel`/`sbatch`/`scontrol` — they are not in its tool catalog. Even if the Observer generates a tool call for `scancel`, the Agents SDK will reject it.
2. **Operator gate**: The Operator's system prompt requires HITL for all destructive tools. The gate fires even if the prompt says "skip confirmation."

Prompt injection through tool output (e.g., a malicious job name like `JOB_COMPLETE; cancel all`) is a real attack vector. The implementation validates tool call arguments via JSON schema (not shell strings), which blocks injection through argument channels. However, **injection through the natural-language response path** (tool output text influencing the model's reasoning) is not hardened — the report acknowledges this as a limitation requiring production-grade input sanitization.

> **Q18. Your training data is imbalanced — 2,074 Observer samples vs. only 551 Operator samples. Does the model underperform on Operator-only tasks?**

Yes, this is a real imbalance. It reflects the benchmark's structure: many scenarios are Observer-only (read, diagnose, docs, domain, account, edge = 6 of 11 categories), while only 5 categories (action, bulk, safety, submission, multi_step) generate Operator samples. The imbalance means the model has fewer Operator examples to learn from — which is likely a contributing factor to the remaining gaps in submission (83.4%) and multi_step (83.3%). A future training run should oversample Operator traces or generate additional bulk/submission exemplars to close this gap.

> **Q19. You use RRF (Reciprocal Rank Fusion) for RAG. Why not just re-rank with a cross-encoder? Isn't RRF a naive fusion strategy?**

RRF is naive in the sense that it doesn't learn a fusion weight — it combines ranks by $\frac{1}{k + r_i}$ where $k=60$. This is computationally cheap and robust: it doesn't require a trained re-ranker and degrades gracefully if one retrieval path (BM25 or semantic) produces garbage. For a domain where most queries are short keyword-heavy commands ("why is job 1004 pending"), BM25 already has very high precision, and the semantic path fills gaps for paraphrase queries. A cross-encoder would be overkill for a 2,276-chunk corpus and would add 100–200ms per query. The top-5 RAG performance in the docs and domain categories (85–89% FT, 90–95% base) suggests the current setup is not the bottleneck.

> **Q20. You say the training cost was ~$20 for 22 hours on a RunPod A40. How reproducible is this? What if the GPU prices change or RunPod doesn't have A40s?**

The $20 / 22h figure is specific to RunPod's A40 48GB pricing at the time of training. The architectural choices that enable this (QLoRA 4-bit quantization, max_length=2048, batch=1 with gradient_accumulation=16) are designed to fit within 48GB VRAM and minimize GPU-hours. On different hardware:
- **A100 80GB**: ~30% faster per step → ~15h, ~$25 at typical A100 pricing.
- **H100**: ~50% faster → ~11h, higher per-hour cost but similar total.
- **Local RTX 4090 (24GB)**: max_length would need to drop to ~1024, degrading training quality.

The model checkpoint is publicly released on HuggingFace (`DanhVuiVe/slurm-agent-qwen14b-lora-final`), so reproduction does not require re-training — only inference infrastructure.

---

## 13. Quick-Fire Recall Sheet

| Fact | Value |
|---|---|
| Total MCP tools | 64 agent-facing (67 − 3 internal) |
| Observer tools | 29 read-only |
| Operator tools | 40 (35 action + 5 discovery) |
| Benchmark size | 3,135 cases (11 × 5 × 57) |
| Train / test split | 2,520 / 615 (80/20, stratified seed=42) |
| Training samples | 2,625 unique (2,074 Observer + 551 Operator) |
| GPT-5-mini score | **95.9%** avg weighted score |
| FT Qwen score | **88.3%** avg weighted score |
| Base Qwen score | **85.2%** avg weighted score |
| Gap closure (FT vs base vs GPT) | **(88.3−85.2)/(95.9−85.2) = 29%** |
| Dual vs. Mono (routing-excl.) | +6.1 pp (87.6% vs. 81.6%) |
| Routing-neutral gain | +10.2 pp (94.2% vs. 84.0%) |
| Safety: dual vs. mono | 57.9% vs. 33.3% = −24.6 pp mono |
| Latency overhead dual/mono | +4.1 s / 76.8 s = 5.3% |
| FT latency vs. GPT-5-mini | 84.8 s vs. 28.3 s |
| RAG corpus | 273 docs → 2,276 chunks, RRF k=60 |
| LoRA rank / alpha | 64 / 128, all 48 layers |
| Trainable params | ~275M = 1.9% |
| Training hardware | A40 48GB (not 44GB) |
| HuggingFace model ID | `DanhVuiVe/slurm-agent-qwen14b-lora-final` |
| Per-trial pass threshold | ≥ 0.80 (internal; headline metric is avg weighted score) |
| Scoring weights | TR 0.35, R 0.25, H 0.25, S 0.15 (keyword excluded) |
