# Specialist Fine-Tuning Prototype

This folder contains quick LoRA/QLoRA paths for adapting Slurm specialist behavior.

- `build_todo_specialist_sft.py` creates data for the existing runtime `TodoTracker` specialist slot, which expects a JSON array of plan steps.
- `build_specialist_sft.py` creates route/tool-planning data for a future specialist planner, which outputs JSON with tools, route, HITL requirement, and expected state change.

## Build the Runtime Todo Specialist SFT Dataset

```bash
conda activate main
python training/build_todo_specialist_sft.py
```

For a tiny smoke file:

```bash
conda activate main
python training/build_todo_specialist_sft.py --limit 64 --out training/out/todo_specialist_sft_smoke.jsonl
```

## Build the Route/Tool Specialist SFT Dataset

```bash
conda activate main
python training/build_specialist_sft.py
```

This writes `training/out/specialist_sft.jsonl` from `evaluation/dataset.json`. Each row is a chat-style specialist planning sample: user request, compact mock state, expected tools, route, HITL requirement, keywords, and expected state change. This route/tool format is a research prototype and is not the current `TodoTracker` output format.

For a tiny smoke file:

```bash
conda activate main
python training/build_specialist_sft.py --limit 64 --out training/out/specialist_sft_smoke.jsonl
```

## Train a LoRA Adapter

Install training dependencies in a suitable GPU Python environment:

```bash
pip install -r training/requirements-finetune.txt
```

Smoke training example:

```bash
python training/train_specialist_lora.py \
  --data training/out/specialist_sft_smoke.jsonl \
  --base-model google/gemma-2b-it \
  --out training/out/slurm-specialist-gemma2b-lora-smoke \
  --sample-count 64 \
  --max-steps 20
```

Full one-epoch example:

```bash
python training/train_specialist_lora.py \
  --data training/out/specialist_sft.jsonl \
  --base-model google/gemma-2b-it \
  --out training/out/slurm-specialist-gemma2b-lora \
  --epochs 1
```

If Gemma access is unavailable in the local Hugging Face environment, use another small instruct model such as `Qwen/Qwen2.5-1.5B-Instruct` or `Qwen/Qwen2.5-3B-Instruct`.

## Runtime Use

For the TodoTracker-compatible adapter, start the local OpenAI-compatible adapter server:

```bash
conda activate main
python training/serve_specialist_openai.py \
  --adapter training/out/slurm-todo-specialist-qwen05b-lora-quick \
  --model-id slurm-todo-specialist-qwen05b-lora-quick \
  --host 127.0.0.1 \
  --port 8010
```

Then run the app with `OPENAI_BASE_URL=http://127.0.0.1:8010/v1` and choose specialist provider `OpenAI` with model `slurm-todo-specialist-qwen05b-lora-quick`. Keep the main model on Ollama/OpenAI as usual; this adapter is only for the specialist planning call.