# REPORT REVIEW — FULL TODO CHECKLIST
> Last updated: May 10, 2026  
> Status legend: `[ ]` = not done · `[x]` = done · `[!]` = urgent / examiner will notice

---

## CRITICAL — Must fix before submission

- [ ] **[!] `agent_frameworks_comparison.png` is referenced but MAY be stale**  
  File exists at `report/images/agent_frameworks_comparison.png` — confirm it actually shows LangChain, AutoGen, CrewAI, OpenAI Agents SDK etc. and is not a leftover placeholder image.  
  → Section: `3.RelatedWorks/3.2.Agent-Frameworks.tex` line 26

- [ ] **[!] GPT-5-mini "96.5% action" in per-category table vs "96.5%" in FT column — coincidence, fine, but double-check the GPT-5-mini column hasn't drifted from the real file**  
  Verify GPT-5-mini 615-case numbers from `gpt5mini_test615_tmp.json` match every number in `tab:ft-per-category`.  
  → Section: `6.2.Results.tex` lines 233–247

- [ ] **[!] Summary section still says "97.8% pass rate on GPT-5-mini 3,135-case run"** — this is the full-dataset run, while Chapter 6 now reports the 615-case test split numbers.  
  The two numbers are from different evaluations and should be clearly distinguished. The 97.8% figure (3,135 cases, rescored) needs a sentence making it explicit this is a separate full-dataset run from the 615-case comparison.  
  → Section: `7.1.Summary.tex` "Benchmark Artifact Outcomes" paragraph

- [ ] **[!] `1.2.Goals.tex` and `1.2.Scope-Goals.tex` — both files exist with similar names. Check which one `main.tex` includes; the orphaned one should be removed or the include fixed.**  
  → `report/sections/1.Introduction/`

- [ ] **[!] 1.3.Challenges.tex says "approximately 8 tools each"** but 4.4 Module Specs says Observer sees "approximately 10 tools" and 4.3 was already fixed to "~10 for Observer, ~8 for Operator". The challenge section still uses the old number.  
  → `1.Introduction/1.3.Challenges.tex` — "dual strategy" paragraph

- [ ] **[!] `% TODO: Add training loss curve from wandb`** — commented-out figure in `6.2.Results.tex` line 104. Either add the WandB loss curve image or delete the comment.  
  → Section: `6.2.Results.tex`

---

## Numbers & Consistency Issues

- [ ] **FT model pass rate stated as 91.4% in Ch6 table but "closes 78% of gap"** — verify: (91.4 - 72.8) / (96.6 - 72.8) = 18.6 / 23.8 = **78.2%** ✓ correct.

- [ ] **Ablation table Δ column: HITL shows −8.1 pp (mono 88.9 > split 80.8)** — this is accurate but looks bad. Ensure the explanation in text (monolithic over-prompts on read-only tasks) is present and clear. It is — confirmed present in `6.2.Results.tex` "Safety Enforcement Analysis".

- [ ] **Section 7.1 Summary: "Goal 4 (Dataset, fine-tuning & evaluation)"** — goal numbering in Chapter 1 has Goal 4 as "Curated Benchmark" and Goal 5 as "Domain-Adapted Fine-Tuning", but the summary merges them into "Goal 4". Either align numbering or split into Goal 4 + Goal 5.  
  → `7.1.Summary.tex` "Achievement Against Project Goals"

- [ ] **Chapter 4 intro (4.1) says "Goal 4: Curated Slurm Benchmark Dataset"** and lists no Goal 5, but the section text discusses fine-tuning under Goal 4. Make sure goal numbering is consistent across Ch1, Ch4, Ch7.  
  → `4.1.Introduction.tex` and `1.2.Scope-Goals.tex`

- [ ] **Section 6.2 "docs" category in 3,135-case baseline shows 85.6% pass** but per-category 615-case GPT-5-mini table shows 87.3%. These are different evaluations (full vs test split) — add a sentence noting this difference so examiners don't flag it as inconsistency.  
  → `6.2.Results.tex` lines ~153 and ~234

- [ ] **Training data: section 5.4 says "3,329 total (2,625 unique after dedup)"** but section 6.2 Training Data Summary table says "2,436 passing traces" → "3,329 samples". The 2,436 ≠ 2,625 unique. Clarify: 2,436 original passing traces → role-split → 3,329 samples → 2,625 unique after dedup. Make sure this chain is clearly stated in one place.  
  → `5.4.Fine-Tuning.tex` and `6.2.Results.tex` tab:training-data-summary

- [ ] **Section 5.4 says "3,329 total (2,625 unique)" but tab:ft-hyperparams says "3,329 total (2,436 Observer + 893 Operator)" — 2,436 + 893 = 3,329 ✓ but that's the split, not unique count. Ensure dedup note is not confused with the role split.**

---

## Missing / Incomplete Content

- [ ] **Commented-out placeholder in `1.1.Motivation.tex` lines 10–14** — "Diagram showing complexity of Slurm CLI commands". It is commented out so it won't appear, but consider whether a figure would strengthen the motivation section. Can use the existing `tool_partitioning_comparison.png` or a simple command-list table instead.

- [ ] **Section 3.3 MCP Implementations has a commented-out placeholder** for an "MCP ecosystem diagram" — same as above, commented out so safe, but could add the existing `images/mcp_mock_data_collection.png` figure reference here if a visual would help.

- [ ] **Section 3.2 Agent Frameworks figure `agent_frameworks_comparison.png`** — image exists but caption just says "Comparison of LLM Agent Frameworks" with no detail. If this is a real figure, update the caption to describe what frameworks are shown and what dimensions are compared.  
  → `3.2.Agent-Frameworks.tex` lines 24–28

- [ ] **`% TODO: Add training loss curve from wandb`** in `6.2.Results.tex` — WandB run data is in `slurm-agent/wandb/`. If a loss curve plot exists, add it. If not, delete the comment.

- [ ] **Abstract** — check it mentions the final 91.4% FT result (not an old number).  
  → `report/sections/abstract.tex`

- [ ] **List of Abbreviations** — check MCP, HITL, QLoRA, NF4, RAG, SSE, HPC, RRF are all listed.  
  → `report/sections/list-of-abbreviations.tex`

---

## Cross-Reference Integrity

- [ ] **`\ref{sec:ablation}` used in Ch4 and Ch7** — label is defined in `6.2.Results.tex` as `\label{sec:ablation}`. Verify it compiles without "undefined reference" warnings.

- [ ] **`\ref{sec:fine-tuning}` used in multiple places** — defined in `4.5.LLM-Architecture.tex`. Verify no "undefined reference".

- [ ] **`\ref{sec:state-match-artifact}`** used in text — label defined in `6.2.Results.tex`. Verify.

- [ ] **`\ref{sec:testing-approach}`** used in Ch4 — defined in `6.1.Testing-Approach.tex`. Verify.

- [ ] **`\ref{sec:module-specifications}`** — defined in `4.4.Module-Specifications.tex`. Verify.

- [ ] **`\ref{sec:impl-rag}`** — defined in `5.1.Agent-Backend.tex`. Verify.

---

## Citation Audit

- [ ] Verify `aiplainenglish2024react` is in `ref.bib` and matches the ReAct citation in `2.4.Agent-Architectures.tex`.
- [ ] `\cite{yao2022react}` — used in Ch1, Ch4, Ch5. Verify bib entry is correct.
- [ ] `\cite{dettmers2023qlora}` — used in Ch4, Ch6. Verify entry exists.
- [ ] `\cite{qin2023toolllm}` — used in Ch1, Ch3. Verify entry.
- [ ] `\cite{reimers2019sentence}` — used in Ch5 RAG section. Verify.
- [ ] `\cite{cormack2009reciprocal}` — RRF citation in Ch5. Verify.
- [ ] `\cite{doosthosseini2024chatai}`, `\cite{langchainparsl2025}`, `\cite{fujitsu2025acb}` — Ch3. Verify all exist in bib.
- [ ] `\cite{patil2023gorilla}`, `\cite{zeng2023agenttuning}` — Ch3. Verify.
- [ ] Check for any `\cite{}` with empty keys or broken entries — run `biber main` and check `.blg` for warnings.

---

## Formatting / LaTeX Issues

- [ ] **Overfull hboxes** — recompile and check log for `Overfull \hbox` warnings. Common culprits: long URLs in text, `\texttt{...}` with long identifiers, table cells.
- [ ] **Figure/table floating** — after all recent adds, check no figure overflows into wrong section. Compile and visually verify Ch5 UI figures (7 total now) don't push Agent API section to wrong page.
- [ ] **List of Figures** — after adding 4 new UI figures + judge score chart, verify the LOF is complete and captions are not truncated.
- [ ] **List of Tables** — verify all new tables appear.
- [ ] **Page count** — check total page count is within thesis submission limit (if one exists).
- [ ] **Equation numbering** — two equations in Ch6 scoring (one in 4.4, one in 6.1, one in 5.1 RAG). Ensure none are unnumbered when they should be or duplicated.
- [ ] **`\allowbreak{}` in `/v1/chat/completions`** — verify it renders correctly and doesn't add unwanted space.

---

## Content Quality

- [ ] **Abstract** — re-read after all changes. Must mention: MCP, Observer/Operator, HITL, fine-tuning, 91.4% pass rate, 615-case benchmark.
- [ ] **Chapter 7.1 Summary "Safety remains a hard problem"** — currently says "mismatch rates in safety-related categories show stronger guarantees are still required before production use". This is borderline self-critical. Consider reframing: "safety-category performance at 93.0% demonstrates reliable HITL activation; production deployment would additionally require role-aware authentication and audit logging."
- [ ] **Section 7.3 Future Work Priority 1** says "weakest performance in multi_step, safety, and submission" — but latest results show safety=93.0% which is strong. Update to reflect actual weakest: submission (84.2%), docs (85.5%), multi_step (87.7%).
- [ ] **Section 1.4 Thesis Structure Ch5 description** says "supporting evaluation infrastructure" — fine-tuning is also in Ch5. Consider adding "and the fine-tuning training pipeline" to the description.
- [ ] **Section 3.2 "Relevance to Slurm Agent"** bullet list — mentions "ReAct pattern informs the agent's approach". Now that we cite `aiplainenglish2024react`, ensure the citation also appears in this section or in 2.4 where ReAct is first discussed.

---

## Git / Final Steps

- [ ] `git add` and `git commit` all pending changes (5.3.Frontend.tex, 6.2.Results.tex, 7.1.Summary.tex, 7.2.Limitations.tex, 4.3.Architecture.tex, 5.1.Agent-Backend.tex, README.md, generate_ablation_charts.py, docs/images/)
- [ ] Run `.\compile.ps1` one final time after all fixes and check for zero errors / zero undefined references in the log.
- [ ] Check `.blg` file for biber/bibtex warnings.
- [ ] Check `main.log` for `Overfull \hbox` and `LaTeX Warning: Reference ... undefined`.
- [ ] Export final PDF and do a visual page-by-page check.

---

## Nice-to-Have (if time permits)

- [ ] Add WandB training loss curve to `6.2.Results.tex` (uncomment the figure block and provide the image).
- [ ] Replace the commented-out Slurm CLI complexity figure in `1.1.Motivation.tex` with a real simple table or diagram.
- [ ] Add a sentence in `6.2.Results.tex` explicitly cross-referencing the judge score chart (`fig:judge-score-comparison`) from the narrative text near line 221.
- [ ] Consider adding `\label{eq:overall-score}` to the scoring equation in `6.1.Testing-Approach.tex` and cross-referencing it from `4.4.Module-Specifications.tex` where the same formula appears (currently duplicated without cross-ref).
