# Poster — Slurm Agent Capstone

**Student:** Nguyễn Phúc Thanh Danh — HCMUT · Supervisor: Assoc. Prof. Thoại Nam · Semester 252

---

## Objective
Build an AI agent with a natural language interface for Slurm HPC cluster management — safe, grounded, and requiring no CLI expertise.

---

## ★ Key Numbers

| 91.4% | 78% | ~$20 | 3,135 |
|:---:|:---:|:---:|:---:|
| FT model pass rate | Gap closed to commercial API | Fine-tuning cost | Benchmark cases |

---

## Motivation
- Slurm CLI creates barriers for non-expert users
- No safety layer for destructive operations (cancel, hold, release)
- Open-weight models lack Slurm domain knowledge
- No benchmark existed for evaluating NL-based Slurm agents

## Approach
- **Observer/Operator Split**: Read-only analysis separated from state-changing execution; all destructive actions require human confirmation
- **Grounded RAG**: 273 official Slurm docs → 2,276 chunks, local retrieval reduces hallucination
- **Fine-Tuning**: Qwen2.5-14B + QLoRA distilled from GPT-5-mini traces — no external API needed
- **Benchmark**: 3,135-case dataset across 11 categories, evaluated with LLM-as-judge

## Results

| Model | Pass | Tool | HITL | Judge | Latency |
|---|---|---|---|---|---|
| GPT-5-mini (commercial) | 96.6% | 98.8% | 99.0% | 74.3%† | 28.3s |
| **FT Qwen2.5-14B (ours)** | **91.4%** | **89.2%** | **90.4%** | **79.7%** | **84.8s** |
| Base Qwen2.5-14B | 72.8% | 84.9% | 80.8% | 76.8% | 80.9s |
| Monolithic ablation | 47.2% | — | — | 59.2% | — |

FT model closes **78% of gap** to commercial API. Observer/Operator beats monolithic by **+44.2pp**.

## Contributions
- Observer/Operator safety workflow with HITL confirmation
- Grounded RAG layer over official Slurm documentation
- 3,135-case curated benchmark (11 categories)
- Cost-effective open-weight fine-tuning (~$20, 91.4% pass rate)

## Future Works
- Multi-tenant auth, isolation, and audit logging
- Practitioner user studies
- Expand to more Slurm edge cases and larger models

---

## Images (Final Selection — 3 images)

| # | Panel | File | Placement |
|---|---|---|---|
| 1 | System architecture | `report/images/agent_system_architect.drawio.png` | Middle column, full height — centrepiece |
| 2 | Per-category results | `report/images/evaluation/category_pass_rates.png` | Right column, top — main result visual |
| 3 | HITL UI screenshot | `report/images/UI_confirm_flow.png` | Right column, bottom — shows it actually works |

> **Why these 3:**
> - Architecture diagram explains the whole system without needing much text
> - Category pass rates is the strongest results visual — readable from distance
> - HITL screenshot is the only real demo proof — grabs attention from non-technical viewers
