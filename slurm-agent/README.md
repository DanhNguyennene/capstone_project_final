# Slurm Agent — AI-Powered HPC Cluster Management

> An intelligent agent system for Slurm cluster management using LLMs + Model Context Protocol (MCP).

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
│   │
│   └── chart-generators/         # Mermaid chart generation
│       ├── chart_system_health.py
│       ├── chart_cluster_topology.py
│       ├── chart_resource_map.py
│       ├── chart_pending_analysis.py
│       └── chart_job_lifecycle.py
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
