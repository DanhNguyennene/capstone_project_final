# Project + Report Update Checklist

Generated from code/report scan on 2026-04-18.
Scope scanned:
- /mnt/e/workspace/uni/capstone_project/slurm-agent
- /mnt/e/workspace/uni/capstone_project/report

## 1) Highest-Priority Fixes (before final report freeze)

- Replace outdated evaluation narrative (45 tests, old metrics) with current Scenario-Grid framework and current result set.
- Update frontend architecture chapter to reflect current React + Vite application and integrated Eval tab, not only Open WebUI/SvelteKit.
- Update streaming protocol description from marker-based content parsing to structured SSE delta fields.
- Regenerate appendix test tables (currently fixed to old 45-test suite).
- Update repository/documentation section to match current file structure (many docs still describe old files/endpoints).

## 2) Critical Mismatches Found (Report vs Current Code)

### A. Evaluation methodology and numbers are outdated

Current report claims:
- 45 tests, pass threshold 0.7, weighted Tool/Fact/Safety/Completion metrics.
- Aggregate values like 93.3% pass and overall 0.909.

Current code state:
- dataset.json has 367 tests.
- 9 categories: read, diagnose, action, bulk, safety, submission, multi_step, account, edge.
- 5 scenarios: healthy, failed, pending, mixed, debug_needed.
- scenario_eval.py now uses architecture-focused metrics: BAR, SVR, CSR, pass^k.
- Pass threshold is 0.80 with an additional keyword gate.
- Optional LLM judge scores full flow including tools, routing, HITL, thinking, and response.

Files to update:
- report/sections/6.Experiments/6.1.Testing-Approach.tex
- report/sections/6.Experiments/6.2.Results.tex
- report/sections/appendixes/appendix.tex
- report/sections/7.Conclusion/7.1.Summary.tex
- report/sections/7.Conclusion/7.2.Limitations.tex

Evidence:
- slurm-agent/evaluation/dataset.json
- slurm-agent/evaluation/scenario_eval.py
- slurm-agent/evaluation/results/

### B. Frontend architecture chapter no longer matches implementation

Current report claims:
- Frontend is Open WebUI (SvelteKit) through middleware router.

Current code state:
- Active UI is React + Vite in slurm-agent/frontend.
- App includes two views: Chat and Eval.
- EvalPage provides dataset upload, run controls, live status, and per-test drill-down.
- Open WebUI integration code still exists, but should be documented as optional/alternative deployment path, not the only frontend.

Files to update:
- report/sections/5.Implementation/5.3.Frontend.tex
- report/sections/4.Proposed/4.3.Architecture.tex
- report/sections/1.Introduction/1.3.Challenges.tex (if it references only OpenWebUI path)

Evidence:
- slurm-agent/frontend/package.json
- slurm-agent/frontend/src/App.jsx
- slurm-agent/frontend/src/Sidebar.jsx
- slurm-agent/frontend-integration/openwebui_main.py

### C. Streaming protocol description is outdated

Current report claims:
- Uses marker tokens in content such as [TOOL:name], [HANDOFF:agent], [IMG]...[/IMG].

Current code state:
- SSE sends structured delta fields:
  - status_update
  - tool_output
  - reasoning_content / reasoning
  - content
  - chart_artifact
  - todo_update
  - pending_actions
- This is OpenAI-compatible chunk schema with typed deltas.

Files to update:
- report/sections/5.Implementation/5.1.Agent-Backend.tex
- report/sections/1.Introduction/1.3.Challenges.tex

Evidence:
- slurm-agent/agent/main.py
- slurm-agent/agent/flow/multi_agent.py

### D. Visualization pipeline description is outdated in wording

Current report claims:
- Talks about base64 image artifact pipeline and [IMG] markers.

Current code state:
- Primary chart artifact path is Mermaid chart code (chart_artifact), rendered in frontend.
- Chart filtering logic still exists to prevent history pollution.

Files to update:
- report/sections/5.Implementation/5.1.Agent-Backend.tex
- report/sections/5.Implementation/5.3.Frontend.tex

Evidence:
- slurm-agent/agent/main.py
- slurm-agent/frontend/src/components/MermaidDiagram.jsx (and related frontend rendering)
- slurm-agent/evaluation/eval_ui.html

### E. Model configuration narrative is stale/over-simplified

Current report claims:
- Main agent uses qwen3.5:9b, sub-agents use gpt-oss:20b as fixed setup.

Current code state:
- Model provider is configurable via environment (ollama, copilot, github-models).
- DEFAULT_MODEL is environment-driven.
- reasoning_model and tool_model default to same model unless overridden.

Files to update:
- report/sections/6.Experiments/6.1.Testing-Approach.tex
- report/sections/5.Implementation/5.1.Agent-Backend.tex

Evidence:
- slurm-agent/agent/flow/model.py
- slurm-agent/agent/flow/multi_agent.py

## 3) New Components Missing from Report (should be added)

- Evaluation web backend and real-time runner:
  - endpoints for run, stop, run-single, clear-results
  - background run persistence and reconnect stream behavior
  - state snapshot restore logic
- Deterministic mock reset before each test case (stateful MCP baseline restore).
- Integrated Eval tab in main frontend application (not only standalone eval page).

Files to cite/add in implementation chapter:
- slurm-agent/evaluation/eval_server.py
- slurm-agent/evaluation/scenario_eval.py
- slurm-agent/mcp-server/slurm_mcp_sse.py
- slurm-agent/frontend/src/EvalPage.jsx

## 4) Project Documentation Drift (outside thesis text)

### A. Root project README is outdated

Observed problems:
- Lists files that do not exist now (for example evaluation/evaluate_agent.py, evaluation/run_evaluation.py).
- Still advertises old 45-test metric snapshot.

Update needed in:
- slurm-agent/README.md

### B. Legacy docs conflict with current architecture

Observed problems:
- docs/agent-readme.md describes older main_clean.py and tool stack.
- docs/OPENAI_FEATURES.md describes old client abstractions not aligned with current runtime path.
- docs/TEST_CASES.md describes hard-test categories that do not match current dataset/scenario_eval pipeline.

Update or archive-marker needed in:
- slurm-agent/docs/agent-readme.md
- slurm-agent/docs/OPENAI_FEATURES.md
- slurm-agent/docs/TEST_CASES.md

Recommendation:
- Add a docs index stating which docs are current vs legacy.

## 5) Report Build Quality Issues (formatting, not factual)

Detected from main.log:
- Many Overfull and Underfull box warnings.
- No immediate missing-file error detected in scanned warnings.

Update pass needed in:
- report/sections/5.Implementation/5.1.Agent-Backend.tex
- report/sections/6.Experiments/6.1.Testing-Approach.tex
- report/sections/6.Experiments/6.2.Results.tex
- report/sections/appendixes/appendix.tex

Goal:
- Improve table widths, long token wrapping, and figure/table placement.

## 6) Recommended Update Order (best-effort minimal churn)

1. Freeze one canonical evaluation run to report (choose one results JSON under slurm-agent/evaluation/results).
2. Rewrite Chapter 6 and Appendix to match 367-test framework and current metrics.
3. Rewrite Frontend section to describe dual mode:
   - primary React frontend
   - optional Open WebUI integration
4. Rewrite streaming and chart artifact subsections in backend implementation.
5. Align Summary/Limitations/Future Work claims with actual implemented stack.
6. Refresh project README and mark legacy docs explicitly.
7. Final LaTeX formatting cleanup pass (warnings reduction).

## 7) Suggested Acceptance Checklist

- All numeric claims in report are traceable to a current results file.
- No section claims a component that is no longer primary implementation.
- Appendix test inventory matches current dataset generation pipeline.
- Frontend chapter explicitly distinguishes active UI and optional integration path.
- README project tree matches real files.
- Legacy docs are either updated or clearly tagged as legacy.
