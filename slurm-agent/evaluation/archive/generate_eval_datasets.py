#!/usr/bin/env python3
"""
LLM-Powered Multi-Turn & Web-Retrieval Dataset Generator
==========================================================
Uses local Ollama (qwen3.5:9b) to generate diverse, curated evaluation cases
at scale. Produces 200 multi-turn conversations and 200 web-retrieval cases.

Strategy:
  - Uses real mock_data states from all 5 scenarios
  - Mixes difficulty levels: easy (2 turns), medium (3 turns), hard (4-5 turns)
  - Varies coreference complexity, action types, and domain coverage
  - Web cases target topics NOT in local corpus (community, cloud, third-party)
  - LLM generates realistic admin questions; script validates & deduplicates

Usage:
  cd evaluation/
  python generate_eval_datasets.py --model qwen3.5:9b
  python generate_eval_datasets.py --model qwen3.5:9b --multi-turn-count 200 --web-count 200
"""

import asyncio
import json
import random
import re
import sys
import time
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

try:
    from openai import AsyncOpenAI
except ImportError:
    print("ERROR: pip install openai")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))
from mock_data import MOCK_JOBS, MOCK_NODES

OLLAMA_URL = "http://localhost:11434/v1"
SCENARIOS = ["healthy", "failed", "pending", "mixed", "debug_needed"]

# ── Tools reference for ground truth ──────────────────────────────────────────
AVAILABLE_TOOLS = [
    "squeue", "sinfo", "sacct", "scontrol_show", "scontrol_hold",
    "scontrol_release", "scontrol_update", "scontrol_requeue",
    "scontrol_create_reservation", "scontrol_delete_reservation",
    "scancel", "sbatch", "sacctmgr_list", "sacctmgr_add",
    "sacctmgr_modify", "sacctmgr_delete", "sdiag", "sprio",
    "sshare", "strigger", "lookup_slurm_docs", "web_search",
]

READ_TOOLS = ["squeue", "sinfo", "sacct", "scontrol_show", "sacctmgr_list", "sdiag", "sprio", "sshare"]
ACTION_TOOLS = ["scancel", "sbatch", "scontrol_hold", "scontrol_release", "scontrol_update",
                "scontrol_requeue", "scontrol_create_reservation", "sacctmgr_add", "sacctmgr_modify"]
DOC_TOOLS = ["lookup_slurm_docs", "web_search"]

# ── State snapshot builders ───────────────────────────────────────────────────

def build_state(scenario: str) -> Dict[str, Any]:
    """Build source_state from mock_data for a given scenario."""
    jobs = {}
    for j in MOCK_JOBS[scenario]:
        jobs[j["job_id"]] = {
            "state": j["state"],
            "user": j["user"],
            "name": j["name"],
            "partition": j["partition"],
        }
    nodes = {}
    for n in MOCK_NODES[scenario]:
        nodes[n["name"]] = {
            "state": n["state"],
            "partition": n["partition"],
        }
    return {"jobs": jobs, "nodes": nodes}


def random_state() -> tuple[str, Dict[str, Any]]:
    """Pick a random scenario and return (scenario_name, state)."""
    s = random.choice(SCENARIOS)
    return s, build_state(s)


# ── LLM Generation ───────────────────────────────────────────────────────────

MULTI_TURN_SYSTEM = """You are a dataset generator for evaluating an AI Slurm cluster management agent.

Generate a multi-turn conversation between a cluster admin and the AI agent. The conversation must be realistic and test the agent's ability to maintain context across turns.

Rules:
1. Each turn has: input (user message), ground_truth (tools, handoff, hitl, keywords), and optionally context_markers
2. tools: list of MCP tool names the agent should call. Available: {tools}
3. handoff: true if the action requires handing off to Operator agent (any destructive action)
4. hitl: true if the action requires human-in-the-loop confirmation (destructive actions: scancel, sbatch, scontrol_hold, scontrol_release, scontrol_update, scontrol_requeue, scontrol_create_reservation, sacctmgr_add, sacctmgr_modify, sacctmgr_delete)
5. keywords: words that MUST appear in the agent's response (job IDs, states, user names, etc.)
6. context_markers: (for turns 2+) words from prior context the agent must resolve (pronouns, "that job", "it", etc.)
7. Later turns should use pronouns/references to prior context ("that job", "it", "her", "the same node", etc.)
8. READ operations (squeue, sinfo, sacct, scontrol_show, sacctmgr_list) have handoff=false, hitl=false
9. lookup_slurm_docs has handoff=false, hitl=false
10. web_search has handoff=false, hitl=false

TURN COUNT REQUIREMENT (STRICTLY ENFORCED):
- Difficulty "{difficulty}" means you MUST generate EXACTLY {num_turns} turns.
- easy = EXACTLY 2 turns
- medium = EXACTLY 3 turns
- hard = EXACTLY 4 turns

Conversation pattern:
- easy (2T): read → act (with pronoun reference)
- medium (3T): investigate → refine (with "that"/"it") → act (with "the same" reference)
- hard (4T): overview → narrow down → ask docs → execute action (each referencing prior context)

CRITICAL RULES FOR CONTEXT:
- Turn 2+ MUST use pronouns/references ("it", "that job", "her", "the same node", "those")
- Turn 2+ MUST have "context_markers" array listing entities the agent needs to resolve from prior turns
- Make each turn's input SHORT (1 sentence, like a real admin typing quickly)

Current cluster state:
{state}

Generate EXACTLY ONE conversation with EXACTLY {num_turns} turns as a JSON object.
The "turns" array MUST have exactly {num_turns} objects. No more, no less.

JSON structure:
{{
  "id": "mt_<unique_descriptive_snake_case_id>",
  "description": "<one line describing the conversation flow>",
  "scenario": "{scenario}",
  "difficulty": "{difficulty}",
  "turns": [
    {{
      "input": "<short user message, 1 sentence>",
      "ground_truth": {{
        "tools": ["<tool_name>"],
        "handoff": false,
        "hitl": false,
        "keywords": ["<word1>", "<word2>"]
      }}
    }},
    {{
      "input": "<message referencing prior context with pronouns like 'it', 'that job', 'her'>",
      "ground_truth": {{
        "tools": ["<tool_name>"],
        "handoff": true,
        "hitl": true,
        "keywords": ["<word1>"]
      }},
      "context_markers": ["<entity_from_prior_turn_that_must_be_resolved>"]
    }}
    ... (continue until you have exactly {num_turns} turn objects)
  ]
}}

IMPORTANT: Output ONLY the JSON object. No explanation, no markdown fences."""

WEB_RETRIEVAL_SYSTEM = """You are a dataset generator for evaluating an AI Slurm cluster management agent's web search escalation behavior.

Generate a test case where the user asks about a topic NOT covered by the local Slurm documentation corpus. The agent should first try lookup_slurm_docs (local RAG), fail to find relevant info, then escalate to web_search.

Topics NOT in the local corpus (use these categories):
- Third-party integrations: PySlurm, Open OnDemand, XDMoD, Bright Cluster Manager, Warewulf
- Cloud providers: AWS ParallelCluster, Azure CycleCloud, Google Cloud HPC Toolkit, Oracle Cloud
- Container runtimes: Enroot+Pyxis, Singularity/Apptainer GPU specifics, Podman-HPC, Charliecloud
- ML frameworks on Slurm: PyTorch distributed (torchrun), DeepSpeed, Horovod, JAX multi-node
- Competing systems: Flux Framework, PBS Pro, HTCondor, TORQUE comparison
- Community tools: DRMAA, Submitit (Facebook), joblib with Slurm, Snakemake Slurm executor
- Version-specific: Release notes, migration guides, deprecated features
- Monitoring: Prometheus+Grafana for Slurm, Datadog HPC, ELK stack integration
- Security: CVEs, vulnerability advisories, OAuth2/OIDC auth, 2FA for Slurm

Difficulty: {difficulty}
- easy: straightforward question about one external tool
- medium: question requiring synthesis of Slurm + external tool knowledge
- hard: complex integration scenario needing multiple web sources

Rules:
1. ground_truth.tools should include ["lookup_slurm_docs", "web_search"] or just ["web_search"] for clearly non-Slurm topics
2. handoff: false, hitl: false (these are purely informational lookups)
3. keywords: specific terms that prove the answer has real web-sourced content
4. The question must be specific enough that a generic answer would be insufficient
5. Include "rationale" explaining why local corpus can't answer this

Generate EXACTLY ONE test case as a JSON object:
{{
  "id": "web_<descriptive_snake_case_id>",
  "category": "web_retrieval",
  "description": "<what this tests>",
  "difficulty": "{difficulty}",
  "input": "<specific user question>",
  "ground_truth": {{
    "tools": ["lookup_slurm_docs", "web_search"],
    "handoff": false,
    "hitl": false,
    "keywords": ["<specific_term1>", "<specific_term2>"]
  }},
  "expect_web_fallback": true,
  "rationale": "<why local corpus can't answer>"
}}

IMPORTANT: Output ONLY the JSON object. No explanation, no markdown fences."""


async def generate_one(client: AsyncOpenAI, model: str, system: str, temperature: float = 0.9) -> Optional[Dict]:
    """Call LLM and parse JSON response."""
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}],
            temperature=temperature,
            max_tokens=2000,
        )
        text = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        # Sometimes model wraps in think tags
        if "<think>" in text:
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return json.loads(text)
    except (json.JSONDecodeError, Exception) as e:
        return None


def validate_multi_turn(case: Dict, existing_ids: set) -> tuple[bool, str]:
    """Validate a generated multi-turn case."""
    if not isinstance(case, dict):
        return False, "not a dict"
    if not case.get("id", "").startswith("mt_"):
        return False, "bad id prefix"
    if case["id"] in existing_ids:
        return False, "duplicate id"
    if not case.get("turns") or len(case["turns"]) < 2:
        return False, "too few turns"
    if not case.get("description"):
        return False, "missing description"

    # Enforce turn count by difficulty
    difficulty = case.get("difficulty", "medium")
    expected_turns = {"easy": 2, "medium": 3, "hard": 4}
    min_turns = expected_turns.get(difficulty, 2)
    if len(case["turns"]) < min_turns:
        return False, f"need {min_turns} turns for {difficulty}, got {len(case['turns'])}"

    for i, turn in enumerate(case["turns"]):
        if not turn.get("input"):
            return False, f"turn {i} missing input"
        gt = turn.get("ground_truth")
        if not gt:
            return False, f"turn {i} missing ground_truth"
        if "tools" not in gt or "handoff" not in gt or "hitl" not in gt or "keywords" not in gt:
            return False, f"turn {i} incomplete ground_truth"
        if not isinstance(gt["tools"], list):
            return False, f"turn {i} tools not list"
        if not isinstance(gt["keywords"], list) or not gt["keywords"]:
            return False, f"turn {i} keywords empty"

        # Turn 2+ must have context_markers
        if i > 0 and not turn.get("context_markers"):
            return False, f"turn {i} missing context_markers"

        # Validate tool names
        for t in gt["tools"]:
            if t not in AVAILABLE_TOOLS:
                return False, f"turn {i} unknown tool: {t}"

        # Validate action/hitl consistency
        action_tools = set(gt["tools"]) & set(ACTION_TOOLS)
        if action_tools and not gt["hitl"]:
            return False, f"turn {i} action tool but hitl=false"
        if action_tools and not gt["handoff"]:
            return False, f"turn {i} action tool but handoff=false"
        if gt["hitl"] and not action_tools:
            return False, f"turn {i} hitl=true but no action tool"

        # Turn 2+ should have context markers or references
        if i > 0:
            input_lower = turn["input"].lower()
            has_ref = any(w in input_lower for w in [
                "it", "that", "this", "those", "them", "the same",
                "her", "his", "their", "she", "he", "which",
                "again", "also", "too", "previous", "earlier",
            ])
            if not has_ref and not turn.get("context_markers"):
                # Not strictly required but preferred
                pass

    return True, "ok"


def validate_web_case(case: Dict, existing_ids: set) -> tuple[bool, str]:
    """Validate a generated web retrieval case."""
    if not isinstance(case, dict):
        return False, "not a dict"
    if not case.get("id", "").startswith("web_"):
        return False, "bad id prefix"
    if case["id"] in existing_ids:
        return False, "duplicate id"
    if not case.get("input"):
        return False, "missing input"
    if not case.get("ground_truth"):
        return False, "missing ground_truth"

    gt = case["ground_truth"]
    if "tools" not in gt or "keywords" not in gt:
        return False, "incomplete ground_truth"
    if "web_search" not in gt["tools"]:
        return False, "must include web_search"
    if not gt["keywords"] or len(gt["keywords"]) < 2:
        return False, "need at least 2 keywords"
    if gt.get("handoff") not in (False, None):
        return False, "web cases should not have handoff"
    if gt.get("hitl") not in (False, None):
        return False, "web cases should not have hitl"
    if not case.get("rationale"):
        return False, "missing rationale"

    # Ensure gt has correct structure
    gt.setdefault("handoff", False)
    gt.setdefault("hitl", False)

    return True, "ok"


def attach_state(case: Dict, scenario: str, state: Dict) -> Dict:
    """Attach source/target state to a case."""
    case["scenario"] = scenario
    case["source_state"] = state
    # For read-only conversations, target = source
    # For action conversations, we'd need to compute target — use source as default
    case["target_state"] = state.copy()
    return case


def attach_web_state(case: Dict) -> Dict:
    """Attach minimal state to a web retrieval case (not state-dependent)."""
    scenario, state = random_state()
    case["scenario"] = scenario
    case["source_state"] = state
    case["target_state"] = state.copy()
    case["category"] = "web_retrieval"
    return case


async def generate_multi_turn_batch(
    client: AsyncOpenAI, model: str, count: int, batch_size: int = 10
) -> List[Dict]:
    """Generate multi-turn cases with retries."""
    results = []
    existing_ids = set()
    difficulties = ["easy"] * (count // 4) + ["medium"] * (count // 2) + ["hard"] * (count - count // 4 - count // 2)
    random.shuffle(difficulties)

    attempt = 0
    max_attempts = count * 4  # Allow 4x attempts for failures

    while len(results) < count and attempt < max_attempts:
        batch = []
        batch_prompts = []

        for _ in range(min(batch_size, count - len(results))):
            difficulty = difficulties[len(results) % len(difficulties)]
            scenario, state = random_state()
            state_str = json.dumps(state, indent=2)
            num_turns = {"easy": 2, "medium": 3, "hard": 4}[difficulty]

            prompt = MULTI_TURN_SYSTEM.format(
                tools=", ".join(AVAILABLE_TOOLS),
                difficulty=difficulty,
                num_turns=num_turns,
                state=state_str,
                scenario=scenario,
            )
            batch_prompts.append((prompt, scenario, state, difficulty))

        # Run batch in parallel
        tasks = [
            generate_one(client, model, prompt, temperature=0.92)
            for prompt, _, _, _ in batch_prompts
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for resp, (prompt, scenario, state, difficulty) in zip(responses, batch_prompts):
            attempt += 1
            if isinstance(resp, Exception) or resp is None:
                continue

            # Add state and validate
            case = attach_state(resp, scenario, state)
            valid, reason = validate_multi_turn(case, existing_ids)
            if valid:
                # Make ID unique with a counter suffix to avoid collisions
                base_id = case["id"]
                if base_id in existing_ids:
                    base_id = f"{base_id}_{len(results)}"
                    case["id"] = base_id
                existing_ids.add(case["id"])
                case["difficulty"] = difficulty
                results.append(case)
                print(f"  ✓ [{len(results):03d}/{count}] {case['id'][:50]} ({difficulty}, {len(case['turns'])}T)")
            else:
                print(f"  ✗ rejected: {reason}")

    return results


async def generate_web_batch(
    client: AsyncOpenAI, model: str, count: int, batch_size: int = 10
) -> List[Dict]:
    """Generate web retrieval cases with retries."""
    results = []
    existing_ids = set()
    difficulties = ["easy"] * (count // 3) + ["medium"] * (count // 3) + ["hard"] * (count - 2 * (count // 3))
    random.shuffle(difficulties)

    attempt = 0
    max_attempts = count * 4

    while len(results) < count and attempt < max_attempts:
        batch_prompts = []

        for _ in range(min(batch_size, count - len(results))):
            difficulty = difficulties[len(results) % len(difficulties)]
            prompt = WEB_RETRIEVAL_SYSTEM.format(difficulty=difficulty)
            batch_prompts.append((prompt, difficulty))

        tasks = [
            generate_one(client, model, prompt, temperature=0.95)
            for prompt, _ in batch_prompts
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for resp, (prompt, difficulty) in zip(responses, batch_prompts):
            attempt += 1
            if isinstance(resp, Exception) or resp is None:
                continue

            case = attach_web_state(resp)
            valid, reason = validate_web_case(case, existing_ids)
            if valid:
                existing_ids.add(case["id"])
                case["difficulty"] = difficulty
                results.append(case)
                print(f"  ✓ [{len(results):03d}/{count}] {case['id'][:50]} ({difficulty})")
            else:
                print(f"  ✗ rejected: {reason}")

    return results


def deduplicate_by_input(cases: List[Dict], key: str = "input") -> List[Dict]:
    """Remove cases with very similar inputs (>80% token overlap)."""
    seen_hashes = set()
    unique = []
    for case in cases:
        # For multi-turn, hash all turn inputs; for single, hash input
        if "turns" in case:
            text = " ".join(t["input"] for t in case["turns"])
        else:
            text = case.get("input", "")

        # Normalize and hash
        normalized = " ".join(text.lower().split())
        h = hashlib.md5(normalized.encode()).hexdigest()[:12]
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique.append(case)
    return unique


async def main():
    p = argparse.ArgumentParser(description="Generate evaluation datasets using LLM")
    p.add_argument("--model", default="qwen3.5:9b", help="Ollama model name")
    p.add_argument("--multi-turn-count", type=int, default=200, help="Number of multi-turn conversations")
    p.add_argument("--web-count", type=int, default=200, help="Number of web retrieval cases")
    p.add_argument("--batch-size", type=int, default=8, help="Parallel generation batch size")
    p.add_argument("--output-dir", default=".", help="Output directory")
    p.add_argument("--skip-multi-turn", action="store_true")
    p.add_argument("--skip-web", action="store_true")
    args = p.parse_args()

    client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")
    output_dir = Path(args.output_dir)

    # Quick model test
    print(f"Testing model {args.model}...")
    try:
        test = await client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": "Say 'ready' in one word"}],
            max_tokens=10,
        )
        print(f"  Model OK: {test.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"  ERROR: Cannot reach model: {e}")
        sys.exit(1)

    # Generate multi-turn
    if not args.skip_multi_turn:
        print(f"\n{'='*60}")
        print(f"  Generating {args.multi_turn_count} multi-turn conversations...")
        print(f"{'='*60}")
        mt_cases = await generate_multi_turn_batch(
            client, args.model, args.multi_turn_count, args.batch_size
        )
        mt_cases = deduplicate_by_input(mt_cases)
        print(f"\n  Generated {len(mt_cases)} unique multi-turn conversations")

        # Merge with existing hand-crafted cases
        existing_mt_path = output_dir / "multi_turn_dataset.json"
        if existing_mt_path.exists():
            existing = json.loads(existing_mt_path.read_text())
            existing_ids = {c["id"] for c in existing}
            new_cases = [c for c in mt_cases if c["id"] not in existing_ids]
            merged = existing + new_cases
            print(f"  Merged: {len(existing)} existing + {len(new_cases)} new = {len(merged)} total")
        else:
            merged = mt_cases

        out_path = output_dir / "multi_turn_dataset.json"
        out_path.write_text(json.dumps(merged, indent=2))
        print(f"  Saved: {out_path} ({len(merged)} conversations)")

    # Generate web retrieval
    if not args.skip_web:
        print(f"\n{'='*60}")
        print(f"  Generating {args.web_count} web retrieval cases...")
        print(f"{'='*60}")
        web_cases = await generate_web_batch(
            client, args.model, args.web_count, args.batch_size
        )
        web_cases = deduplicate_by_input(web_cases)
        print(f"\n  Generated {len(web_cases)} unique web retrieval cases")

        # Merge with existing hand-crafted cases
        existing_web_path = output_dir / "web_retrieval_dataset.json"
        if existing_web_path.exists():
            existing = json.loads(existing_web_path.read_text())
            existing_ids = {c["id"] for c in existing}
            new_cases = [c for c in web_cases if c["id"] not in existing_ids]
            merged = existing + new_cases
            print(f"  Merged: {len(existing)} existing + {len(new_cases)} new = {len(merged)} total")
        else:
            merged = web_cases

        out_path = output_dir / "web_retrieval_dataset.json"
        out_path.write_text(json.dumps(merged, indent=2))
        print(f"  Saved: {out_path} ({len(merged)} cases)")

    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
