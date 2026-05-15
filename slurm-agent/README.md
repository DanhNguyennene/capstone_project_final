# Slurm Agent — AI-Powered HPC Cluster Management

> An intelligent dual-agent system for Slurm HPC cluster management using LLMs, the Model Context Protocol (MCP), and a domain-fine-tuned open-weight model.

[![Model](https://img.shields.io/badge/🤗%20Model-DanhVuiVe%2Fslurm--agent--qwen14b--lora--final-blue)](https://huggingface.co/DanhVuiVe/slurm-agent-qwen14b-lora-final)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Overview

The Slurm Agent translates natural-language requests into grounded Slurm scheduler interactions. It combines:

- **Observer/Operator dual-agent architecture** — read-only inspection is separated from state-changing operations at the framework level
- **Human-in-the-Loop (HITL) confirmation** — all destructive tool calls (cancel, hold, drain, modify) require explicit user approval before execution
- **MCP tool layer** — 67 typed Slurm tools with parameter validation and dual real/mock execution modes
- **Domain fine-tuned model** — Qwen2.5-14B-Instruct + QLoRA adapter trained on GPT-5-mini distilled traces, achieving **91.4% pass rate** on a 615-case held-out benchmark
- **Hybrid RAG** — local Slurm documentation retrieval (BM25 + semantic, RRF fusion) with web search fallback

---

## Fine-Tuned Model

The domain-adapted model is publicly available on Hugging Face:

**[DanhVuiVe/slurm-agent-qwen14b-lora-final](https://huggingface.co/DanhVuiVe/slurm-agent-qwen14b-lora-final)**

| Property | Value |
|---|---|
| Base model | Qwen2.5-14B-Instruct |
| Adapter type | QLoRA (r=64, α=128) |
| Target layers | All 48 transformer layers |
| Trainable params | ~480M (3.2%) |
| Training data | 3,329 samples (GPT-5-mini distillation) |
| Training hardware | 1× NVIDIA A40 48 GB |
| Training time | ~22 hours |

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-14B-Instruct", load_in_4bit=True)
model = PeftModel.from_pretrained(base, "DanhVuiVe/slurm-agent-qwen14b-lora-final")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct")
```

---

## Benchmark Results

All three configurations evaluated on an identical 615-case held-out test split (stratified 80/20, seed=42):

| Metric | GPT-5-mini | **Qwen2.5-14B (FT)** | Qwen2.5-14B (Base) | Monolithic (Base) |
|---|---|---|---|---|
| Pass rate | 96.6% | **91.4%** | 72.8% | 69.8%† |
| Tool recall | 98.8% | **89.2%** | 84.9% | 77.5% |
| Routing match | 99.0% | **90.1%** | 83.6% | 63.3% |
| HITL match | 99.0% | **90.4%** | 80.8% | 88.9% |
| Judge score | 75.2% | **79.7%** | 76.8% | 75.2% |
| Latency | 28.3 s | 84.8 s | 80.9 s | 76.8 s |

The fine-tuned model closes **78% of the gap** between the base model and the commercial API baseline while running entirely on local infrastructure.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Interface Layer  (React + Vite)                │
│  → submits prompts, relays confirm/cancel       │
├─────────────────────────────────────────────────┤
│  Agent Layer  (OpenAI Agents SDK)               │
│  ┌──────────────┐      ┌──────────────────────┐ │
│  │   Observer   │─────▶│      Operator        │ │
│  │ (read-only)  │handoff│ (state-changing)    │ │
│  │ ~10 tools    │◀─────│ ~8 tools + HITL gate │ │
│  └──────────────┘      └──────────────────────┘ │
├─────────────────────────────────────────────────┤
│  Protocol Layer  (MCP Server, 67 tools)         │
│  → real mode: Slurm CLI subprocess              │
│  → mock mode: in-memory resettable state        │
├─────────────────────────────────────────────────┤
│  Infrastructure                                 │
│  Slurm cluster · LLM endpoint · SQLite · Docs  │
└─────────────────────────────────────────────────┘
```

The Observer handles all read-only operations (queue inspection, diagnosis, documentation, web search). When a state-changing operation is required, it hands off to the Operator via the SDK `handoff()` mechanism. The Operator executes destructive tools only after the user confirms the pending action.

---

## Screenshots

All screenshots are from a live session using the fine-tuned `DanhVuiVe/slurm-agent-qwen14b-lora-final` adapter.

### HITL Safety Flow

| Before | During | After |
|---|---|---|
| ![Read query](docs/images/UI_before_HITL.jpg) | ![Confirmation gate](docs/images/UI_during_HITL.jpg) | ![Post-execution](docs/images/UI_after_HITL.jpg) |
| Read-only query: `squeue` returns active jobs | Destructive `scancel` intercepted — user must confirm | Confirmed: jobs cancelled, follow-up `squeue` verifies CANCELLED state |

### Web Search Integration

| Tool execution | Final response |
|---|---|
| ![Web search calls](docs/images/UI_before_WEB.jpg) | ![CUDA OOM answer](docs/images/UI_after_WEB.jpg) |
| Observer calls `web_search` + `web_fetch` for CUDA OOM error | Structured troubleshooting guide from retrieved sources |

### Documentation Lookup (RAG)

| Retrieval phase | Final response |
|---|---|
| ![Docs retrieval](docs/images/UI_before_RAG.jpg) | ![Partition guide](docs/images/UI_after_RAG.jpg) |
| Observer calls `lookup_slurm_docs`, extracts partition config snippets | Grounded partition-selection guide from local corpus |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/DanhNguyennene/capstone_project_final
cd capstone_project_final/slurm-agent
pip install -r agent/requirements.txt
pip install -r mcp-server/requirements.txt
```

### 2. Configure environment

```bash
cp config/agent.env.example .env
# Set OPENAI_API_KEY or point OPENAI_BASE_URL to local model server
```

### 3. Start MCP server

```bash
# Mock mode (for development/evaluation)
python mcp-server/slurm_mcp_sse.py --mock

# Real mode (requires Slurm on PATH)
python mcp-server/slurm_mcp_sse.py
```

### 4. Start agent backend

```bash
cd agent
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Run with fine-tuned model

```bash
# Serve the fine-tuned model locally (requires A40 or equivalent)
python evaluation/serve_ft_model.py --port 9000

# Point the agent at it
export OPENAI_BASE_URL=http://localhost:9000/v1
export OPENAI_API_KEY=dummy
export SLURM_AGENT_MODEL=slurm-agent
```

---

## Evaluation

```bash
# Run full 615-case benchmark (fine-tuned model)
bash run_ft_eval.sh

# Run ablation (monolithic vs Observer/Operator)
bash run_ablation_monolithic.sh

# Inspect results
python evaluation/eval_ui.html  # open in browser
```

---

## Project Structure

```
slurm-agent/
├── agent/                  # FastAPI backend + OpenAI Agents SDK orchestration
│   ├── main.py             # /v1/chat/completions endpoint
│   └── flow/               # Observer, Operator, instructions, tools
├── mcp-server/             # 67 typed Slurm MCP tools (real + mock)
├── evaluation/             # Benchmark dataset, eval harness, scoring
│   ├── dataset.json        # 3,135 test cases (11 categories × 5 scenarios)
│   └── results/            # Evaluation result JSON files
├── training/               # QLoRA fine-tuning scripts
├── frontend/               # React + Vite UI
├── docs/                   # Documentation + screenshots
│   └── images/             # UI screenshots
└── config/                 # Environment templates + deployment
```

---

## Citation

```bibtex
@misc{slurmagent2026,
  title  = {Slurm Agent: An AI-Powered HPC Cluster Management System with Observer/Operator Architecture},
  author = {Danh Nguyen},
  year   = {2026},
  url    = {https://github.com/DanhNguyennene/capstone_project_final}
}
```


## Project Structure

```
slurm-agent/
│
├── agent/                        # Agent Backend (core AI logic)
│   ├── main.py                   # FastAPI service — OpenAI-compatible API
│   ├── openwebui_pipe.py         # Open WebUI pipeline adapter
│   ├── validate.py               # Validation utilities
│   ├── mock_mcp_server.py        # Mock MCP server for local testing
│   ├── test_sequential.py        # Sequential conversation tests
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Agent container
│   ├── docker-compose.yaml       # Agent + MCP orchestration
│   ├── run.sh                    # Quick start script
│   │
│   ├── flow/                     # Multi-agent orchestration
│   │   ├── multi_agent.py        # ★ Main agent system (Main + Analysis + Action sub-agents)
│   │   ├── react_agent.py        # ReAct agent implementation
│   │   ├── workflows.py          # Workflow patterns
│   │   └── multi_agent_old.py    # Previous iteration (reference)
│   │
│   ├── utils/                    # Shared utilities
│   │   ├── mcp_client.py         # MCP protocol client
│   │   └── openai_client.py      # OpenAI SDK helpers
│   │
│   └── rag/                      # Retrieval-Augmented Generation
│       └── rag.py                # RAG pipeline for Slurm docs
│
├── mcp-server/                   # MCP Server (Slurm tool definitions)
│   ├── __init__.py               # ★ MCP server with all tool definitions
│   ├── mock_data.py              # Mock Slurm cluster data (5 scenarios)
│   ├── requirements.txt          # Server dependencies
│   ├── start.sh                  # Server start script
│   │
│   ├── analysis-scripts/         # Predefined Slurm analysis tools
│   │   ├── scripts.json          # Script registry
│   │   ├── analyze_my_jobs.sh
│   │   ├── analyze_failed_jobs.sh
│   │   ├── analyze_gpu_resources.sh
│   │   ├── analyze_cluster_status.sh
│   │   ├── analyze_pending_jobs.sh
│   │   ├── analyze_my_efficiency.sh
│   │   └── analyze_my_usage.sh
│
├── evaluation/                   # Testing & Evaluation
│   ├── evaluate_agent.py         # ★ 45-test automated evaluation suite
│   ├── test_scoring.py           # Scoring: Tool F1, Fact, Safety, Completion
│   ├── evaluation_framework.py   # Framework utilities
│   ├── run_evaluation.py         # Evaluation runner
│   ├── test_agent.py             # Agent unit tests
│   ├── test_mcp_direct.py        # Direct MCP tool tests
│   │
│   ├── results/                  # Evaluation outputs
│   │   ├── agent_evaluation_full.json
│   │   ├── agent_evaluation_web_search.json
│   │   ├── agent_evaluation_tables*.tex
│   │   └── score_history.jsonl
│   │
│   └── test-results/             # MCP-level test results
│       ├── mcp_test_results.json
│       └── mcp_test_table.tex
│
├── frontend-integration/         # Open WebUI ↔ Agent bridge
│   ├── openwebui_main.py         # FastAPI middleware router
│   └── openwebui_config.py       # Configuration
│
├── config/                       # Configuration & deployment
│   ├── agent.env.example         # Agent environment template
│   ├── docker-compose.yaml       # Full stack orchestration
│   ├── Dockerfile.root           # Root container
│   ├── pyproject.toml            # Python project config
│   ├── Makefile                  # Build commands
│   ├── setup_tool_server.sh      # Slurm test env setup
│   ├── tool_server.py            # Tool server utility
│   └── process_controller.py     # Process management
│
├── docs/                         # Documentation
│   ├── agent-readme.md           # Agent detailed docs
│   ├── ARCHITECTURE.py           # Architecture overview (executable)
│   ├── STRUCTURED_AGENT.md       # Agent design rationale
│   ├── TEST_CASES.md             # Test case descriptions
│   ├── OPENAI_FEATURES.md        # OpenAI SDK features used
│   ├── BUILDER_USAGE.md          # Builder pattern docs
│   └── agent_output_example.txt  # Sample agent output
│
└── archive/                      # Previous agent versions
    ├── agent.py                  # v1 single agent
    ├── agent_v2.py               # v2 with improvements
    ├── agent_v2_openai.py        # v2 OpenAI SDK port
    ├── tools.py                  # v1 tool definitions
    ├── tools_openai.py           # OpenAI-format tools
    └── openai_adapter.py         # Adapter layer
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  Presentation: Open WebUI (SvelteKit)       │
├─────────────────────────────────────────────┤
│  Middleware: FastAPI Router (session mgmt)   │
├─────────────────────────────────────────────┤
│  Agent Layer: ReAct Main Agent              │
│    ├── Analysis Sub-Agent (read-only)       │
│    └── Action Sub-Agent (state changes)     │
├─────────────────────────────────────────────┤
│  Protocol: MCP Server (Slurm tools)         │
├─────────────────────────────────────────────┤
│  Infrastructure: Slurm · LLM · SQLite       │
└─────────────────────────────────────────────┘
```

## Key Results

| Metric | Score |
|--------|-------|
| Pass Rate | 93.3% (42/45) |
| Tool Accuracy | 0.940 |
| Fact Accuracy | 0.873 |
| Safety Score | 0.956 |
| Overall | 0.909 |
