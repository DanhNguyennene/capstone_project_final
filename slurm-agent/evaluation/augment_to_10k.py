#!/usr/bin/env python3
"""
Scale Evaluation Datasets to 10k
==================================
Augments existing datasets (3135 single-turn + 200 multi-turn + 200 web retrieval)
to ~10,000 total cases via:

1. SCENARIO SWAP: Remap entity references (job IDs, names, nodes) to different scenarios
2. PARAPHRASE: Use qwen2.5:7b to generate natural-language query variations
3. BALANCE: Ensure equal category/scenario distribution in final output

Source datasets:
  - dataset.json (3135 single-turn, 11 categories × 285, 5 scenarios)
  - multi_turn_dataset.json (200 multi-turn conversations)
  - web_retrieval_dataset.json (200 web retrieval cases)

Target: ~10,000 total
  - Single-turn: 11 categories × 700 = 7700
  - Multi-turn: 1150
  - Web retrieval: 1150

Usage:
  python augment_to_10k.py --model qwen2.5:7b
  python augment_to_10k.py --model qwen2.5:7b --target 10000
  python augment_to_10k.py --skip-paraphrase  # fast, no LLM, just swaps
"""

import asyncio
import json
import random
import re
import sys
import argparse
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

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

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY MAPPING TABLES
# ══════════════════════════════════════════════════════════════════════════════

def build_entity_map() -> Dict[str, Dict]:
    """Build a mapping of all entities per scenario for swap operations."""
    entity_map = {}
    for scen in SCENARIOS:
        jobs = MOCK_JOBS[scen]
        nodes = MOCK_NODES[scen]
        entity_map[scen] = {
            "jobs": {j["job_id"]: j for j in jobs},
            "nodes": {n["name"]: n for n in nodes},
            "job_ids": [j["job_id"] for j in jobs],
            "job_names": {j["name"]: j["job_id"] for j in jobs},
            "node_names": [n["name"] for n in nodes],
            "users": list(set(j["user"] for j in jobs)),
            "partitions": list(set(n["partition"] for n in nodes)),
            "by_state": {},
            "by_user": {},
            "by_partition": {},
        }
        # Group jobs by state
        for j in jobs:
            entity_map[scen]["by_state"].setdefault(j["state"], []).append(j)
        # Group jobs by user
        for j in jobs:
            entity_map[scen]["by_user"].setdefault(j["user"], []).append(j)
        # Group nodes by partition
        for n in nodes:
            entity_map[scen]["by_partition"].setdefault(n["partition"], []).append(n)
    return entity_map


ENTITY_MAP = build_entity_map()

# All job IDs across all scenarios (for detection in text)
ALL_JOB_IDS = set()
ALL_JOB_NAMES = set()
ALL_NODE_NAMES = set()
for scen in SCENARIOS:
    for j in MOCK_JOBS[scen]:
        ALL_JOB_IDS.add(j["job_id"])
        ALL_JOB_NAMES.add(j["name"])
    for n in MOCK_NODES[scen]:
        ALL_NODE_NAMES.add(n["name"])


def build_state(scenario: str) -> Dict[str, Any]:
    """Build source/target state dict from scenario."""
    jobs = {}
    for j in MOCK_JOBS[scenario]:
        jobs[j["job_id"]] = {
            "state": j["state"], "user": j["user"],
            "name": j["name"], "partition": j["partition"],
        }
    nodes = {}
    for n in MOCK_NODES[scenario]:
        nodes[n["name"]] = {"state": n["state"], "partition": n["partition"]}
    return {"jobs": jobs, "nodes": nodes}


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO SWAP ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def find_entities_in_text(text: str, scenario: str) -> Dict[str, List[str]]:
    """Find entity references in a text string."""
    found = {"job_ids": [], "job_names": [], "node_names": [], "users": []}
    em = ENTITY_MAP[scenario]

    for jid in em["job_ids"]:
        if jid in text:
            found["job_ids"].append(jid)
    for jname in em["job_names"]:
        if jname in text:
            found["job_names"].append(jname)
    for nname in em["node_names"]:
        if nname in text:
            found["node_names"].append(nname)
    for user in em["users"]:
        if user in text:
            found["users"].append(user)
    return found


def pick_equivalent_entity(entity_type: str, entity_value: str,
                           src_scenario: str, dst_scenario: str) -> Optional[str]:
    """Find an equivalent entity in the destination scenario."""
    src_em = ENTITY_MAP[src_scenario]
    dst_em = ENTITY_MAP[dst_scenario]

    if entity_type == "job_id":
        # Match by similar role: same state if possible, else same user, else random
        src_job = src_em["jobs"].get(entity_value)
        if not src_job:
            return random.choice(dst_em["job_ids"]) if dst_em["job_ids"] else None

        # Try same state first
        same_state = dst_em["by_state"].get(src_job["state"], [])
        if same_state:
            return random.choice(same_state)["job_id"]
        # Try same user
        same_user = dst_em["by_user"].get(src_job["user"], [])
        if same_user:
            return random.choice(same_user)["job_id"]
        # Fallback: any job
        return random.choice(dst_em["job_ids"])

    elif entity_type == "job_name":
        # Map job name to its ID, find equivalent job, return its name
        src_jid = src_em["job_names"].get(entity_value)
        if not src_jid:
            # Pick random dst job name
            dst_names = list(dst_em["job_names"].keys())
            return random.choice(dst_names) if dst_names else None
        # Find equivalent job ID in dst
        dst_jid = pick_equivalent_entity("job_id", src_jid, src_scenario, dst_scenario)
        if dst_jid and dst_jid in dst_em["jobs"]:
            return dst_em["jobs"][dst_jid]["name"]
        return random.choice(list(dst_em["job_names"].keys()))

    elif entity_type == "node_name":
        src_nodes = MOCK_NODES[src_scenario]
        src_node = next((n for n in src_nodes if n["name"] == entity_value), None)
        if not src_node:
            return random.choice(dst_em["node_names"]) if dst_em["node_names"] else None
        # Try same partition first
        same_part = dst_em["by_partition"].get(src_node["partition"], [])
        if same_part:
            return random.choice(same_part)["name"]
        return random.choice(dst_em["node_names"])

    return None


def swap_scenario_single_turn(case: Dict, dst_scenario: str) -> Optional[Dict]:
    """
    Swap a single-turn case to a different scenario by remapping entities.
    Returns None if the swap isn't meaningful (same scenario or can't remap).
    """
    src_scenario = case.get("scenario")
    if src_scenario == dst_scenario:
        return None

    new_case = deepcopy(case)
    new_case["scenario"] = dst_scenario
    new_case["source_state"] = build_state(dst_scenario)
    new_case["target_state"] = build_state(dst_scenario)

    # Build replacement map for this case
    replacements = {}  # old_text -> new_text
    input_text = case["input"]
    keywords = case["ground_truth"]["keywords"]

    # Find entities in input
    found = find_entities_in_text(input_text, src_scenario)

    # Also check keywords for entities
    for kw in keywords:
        if kw in ENTITY_MAP[src_scenario]["job_ids"]:
            if kw not in found["job_ids"]:
                found["job_ids"].append(kw)
        elif kw in ENTITY_MAP[src_scenario]["job_names"]:
            if kw not in found["job_names"]:
                found["job_names"].append(kw)
        elif kw in ENTITY_MAP[src_scenario]["node_names"]:
            if kw not in found["node_names"]:
                found["node_names"].append(kw)

    # Map job IDs
    for jid in found["job_ids"]:
        new_jid = pick_equivalent_entity("job_id", jid, src_scenario, dst_scenario)
        if new_jid:
            replacements[jid] = new_jid

    # Map job names
    for jname in found["job_names"]:
        new_jname = pick_equivalent_entity("job_name", jname, src_scenario, dst_scenario)
        if new_jname:
            replacements[jname] = new_jname

    # Map node names
    for nname in found["node_names"]:
        new_nname = pick_equivalent_entity("node_name", nname, src_scenario, dst_scenario)
        if new_nname:
            replacements[nname] = new_nname

    # Apply replacements to input
    new_input = input_text
    for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
        new_input = new_input.replace(old, new)
    new_case["input"] = new_input

    # Apply replacements to keywords
    new_keywords = []
    for kw in keywords:
        if kw in replacements:
            new_keywords.append(replacements[kw])
        else:
            new_keywords.append(kw)
    new_case["ground_truth"]["keywords"] = new_keywords

    # Generate unique ID
    new_case["id"] = f"{case['id']}_swap_{dst_scenario[:3]}"

    return new_case


def swap_scenario_multi_turn(case: Dict, dst_scenario: str) -> Optional[Dict]:
    """Swap a multi-turn case to a different scenario."""
    src_scenario = case.get("scenario")
    if src_scenario == dst_scenario:
        return None

    new_case = deepcopy(case)
    new_case["scenario"] = dst_scenario
    new_case["source_state"] = build_state(dst_scenario)
    new_case["target_state"] = build_state(dst_scenario)

    # Collect all entities across all turns
    all_text = " ".join(t["input"] for t in case["turns"])
    all_kw = []
    for t in case["turns"]:
        all_kw.extend(t["ground_truth"]["keywords"])
        all_kw.extend(t.get("context_markers", []))

    found = find_entities_in_text(all_text + " " + " ".join(all_kw), src_scenario)

    # Build consistent replacement map
    replacements = {}
    for jid in found["job_ids"]:
        new_jid = pick_equivalent_entity("job_id", jid, src_scenario, dst_scenario)
        if new_jid:
            replacements[jid] = new_jid
    for jname in found["job_names"]:
        new_jname = pick_equivalent_entity("job_name", jname, src_scenario, dst_scenario)
        if new_jname:
            replacements[jname] = new_jname
    for nname in found["node_names"]:
        new_nname = pick_equivalent_entity("node_name", nname, src_scenario, dst_scenario)
        if new_nname:
            replacements[nname] = new_nname

    # Apply to all turns
    for turn in new_case["turns"]:
        new_input = turn["input"]
        for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
            new_input = new_input.replace(old, new)
        turn["input"] = new_input

        # Keywords
        new_kw = []
        for kw in turn["ground_truth"]["keywords"]:
            new_kw.append(replacements.get(kw, kw))
        turn["ground_truth"]["keywords"] = new_kw

        # Context markers
        if "context_markers" in turn:
            new_cm = []
            for cm in turn["context_markers"]:
                new_cm.append(replacements.get(cm, cm))
            turn["context_markers"] = new_cm

    new_case["id"] = f"{case['id']}_swap_{dst_scenario[:3]}"
    return new_case


# ══════════════════════════════════════════════════════════════════════════════
# PARAPHRASE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

PARAPHRASE_SYSTEM = """You are a paraphrasing assistant for HPC/Slurm queries. Rewrite the user message in a different natural way.
Rules:
- Keep the SAME meaning and intent
- Keep all specific names, IDs, numbers, node names, usernames, and technical terms EXACTLY
- Change sentence structure, word choice, or style (casual/formal/shorter/longer)
- Do NOT add new information or change what is being asked
- Output ONLY the rewritten text, nothing else
- Do NOT wrap in quotes"""


async def paraphrase_one(client: AsyncOpenAI, model: str, text: str,
                         semaphore: asyncio.Semaphore) -> str:
    """Paraphrase a single input string with concurrency control."""
    async with semaphore:
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": PARAPHRASE_SYSTEM},
                    {"role": "user", "content": text},
                ],
                temperature=0.9,
                max_tokens=250,
            )
            result = resp.choices[0].message.content.strip()
            # Strip thinking tags
            if "<think>" in result:
                result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()
            # Strip quotes
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            if result.startswith("'") and result.endswith("'"):
                result = result[1:-1]
            return result if result and len(result) > 5 else text
        except Exception as e:
            return text


async def paraphrase_single_turn(client: AsyncOpenAI, model: str,
                                 case: Dict, variant_id: int,
                                 semaphore: asyncio.Semaphore) -> Dict:
    """Create a paraphrased variant of a single-turn case."""
    new_case = deepcopy(case)
    new_case["input"] = await paraphrase_one(client, model, case["input"], semaphore)
    new_case["id"] = f"{case['id']}_p{variant_id}"
    return new_case


async def paraphrase_multi_turn(client: AsyncOpenAI, model: str,
                                case: Dict, variant_id: int,
                                semaphore: asyncio.Semaphore) -> Dict:
    """Create a paraphrased variant of a multi-turn conversation."""
    new_case = deepcopy(case)
    tasks = [paraphrase_one(client, model, t["input"], semaphore) for t in new_case["turns"]]
    results = await asyncio.gather(*tasks)
    for turn, new_input in zip(new_case["turns"], results):
        turn["input"] = new_input
    new_case["id"] = f"{case['id']}_p{variant_id}"
    return new_case


async def paraphrase_web_case(client: AsyncOpenAI, model: str,
                              case: Dict, variant_id: int,
                              semaphore: asyncio.Semaphore) -> Dict:
    """Create a paraphrased variant of a web retrieval case."""
    new_case = deepcopy(case)
    new_case["input"] = await paraphrase_one(client, model, case["input"], semaphore)
    new_case["id"] = f"{case['id']}_p{variant_id}"
    return new_case


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

ACTION_TOOLS = {
    'scancel', 'sbatch', 'scontrol_hold', 'scontrol_release', 'scontrol_update',
    'scontrol_requeue', 'scontrol_create_reservation', 'sacctmgr_add',
    'sacctmgr_modify', 'scontrol_suspend', 'scontrol_shutdown',
    'scontrol_reconfigure', 'scontrol_delete_reservation',
    'scontrol_update_reservation', 'scontrol_setdebug',
    'strigger_set', 'strigger_clear', 'salloc', 'srun',
}


def validate_single_turn(case: Dict) -> List[str]:
    """Validate a single-turn case, return list of errors."""
    errors = []
    gt = case.get("ground_truth", {})
    # Empty tools is valid (ambiguous intent cases in source dataset)
    if not case.get("input"):
        errors.append("empty input")
    if not case.get("scenario"):
        errors.append("missing scenario")
    if case.get("scenario") not in SCENARIOS:
        errors.append("invalid scenario")
    return errors


def validate_multi_turn(case: Dict) -> List[str]:
    """Validate a multi-turn case."""
    errors = []
    if not case.get("turns") or len(case["turns"]) < 2:
        errors.append("too few turns")
    for i, t in enumerate(case.get("turns", [])):
        gt = t.get("ground_truth", {})
        if not gt.get("tools"):
            errors.append(f"turn {i}: empty tools")
        if not gt.get("keywords"):
            errors.append(f"turn {i}: empty keywords")
        if not t.get("input"):
            errors.append(f"turn {i}: empty input")
    return errors


def validate_web(case: Dict) -> List[str]:
    """Validate a web retrieval case."""
    errors = []
    gt = case.get("ground_truth", {})
    if "web_search" not in gt.get("tools", []):
        errors.append("missing web_search tool")
    if not case.get("input"):
        errors.append("empty input")
    if not gt.get("keywords"):
        errors.append("empty keywords")
    return errors


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

async def main():
    p = argparse.ArgumentParser(description="Scale evaluation datasets to 10k")
    p.add_argument("--model", default="qwen2.5:7b", help="Ollama model for paraphrasing")
    p.add_argument("--target", type=int, default=10000, help="Total target case count")
    p.add_argument("--concurrency", type=int, default=16, help="Max parallel LLM requests")
    p.add_argument("--skip-paraphrase", action="store_true", help="Skip LLM (swap-only mode)")
    p.add_argument("--output-dir", default=".", help="Output directory")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    args = p.parse_args()

    random.seed(args.seed)
    output_dir = Path(args.output_dir)

    # ── Load source data ────────────────────────────────────────────────────
    print("Loading source datasets...")
    st_data = json.loads((output_dir / "dataset.json").read_text())
    mt_data = json.loads((output_dir / "multi_turn_dataset.json").read_text())
    web_data = json.loads((output_dir / "web_retrieval_dataset.json").read_text())
    print(f"  Single-turn: {len(st_data)}")
    print(f"  Multi-turn:  {len(mt_data)}")
    print(f"  Web:         {len(web_data)}")
    print(f"  Total source: {len(st_data) + len(mt_data) + len(web_data)}")

    # ── Compute targets (balanced) ──────────────────────────────────────────
    # 13 total categories: 11 single-turn + multi_turn + web_retrieval
    # Single-turn gets 77% of budget, multi-turn and web get 11.5% each
    st_target = int(args.target * 0.77)  # 7700
    mt_target = int(args.target * 0.115)  # 1150
    web_target = args.target - st_target - mt_target  # 1150

    # Balance single-turn across categories
    st_categories = sorted(set(c["category"] for c in st_data))
    st_per_cat = st_target // len(st_categories)  # 700 per category

    print(f"\n  Targets:")
    print(f"    Single-turn: {st_target} ({st_per_cat} × {len(st_categories)} categories)")
    print(f"    Multi-turn:  {mt_target}")
    print(f"    Web:         {web_target}")
    print(f"    Total:       {st_target + mt_target + web_target}")

    # ── Setup LLM client ────────────────────────────────────────────────────
    client = None
    semaphore = asyncio.Semaphore(args.concurrency)

    if not args.skip_paraphrase:
        client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")
        print(f"\nTesting model {args.model}...")
        try:
            test = await client.chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": "Say 'ready'"}],
                max_tokens=10,
            )
            resp = test.choices[0].message.content.strip()
            if "<think>" in resp:
                resp = re.sub(r"<think>.*?</think>", "", resp, flags=re.DOTALL).strip()
            print(f"  Model OK: {resp[:20]}")
        except Exception as e:
            print(f"  WARNING: Model unavailable ({e}), falling back to swap-only")
            args.skip_paraphrase = True

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 1: Augment single-turn data
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  Phase 1: Augmenting single-turn ({len(st_data)} → {st_target})")
    print(f"{'='*60}")

    # Group by category
    by_category: Dict[str, List[Dict]] = {}
    for case in st_data:
        by_category.setdefault(case["category"], []).append(case)

    augmented_st = []
    para_queue_st = []  # (category_index, case) — cases that need paraphrasing

    for cat_idx, cat in enumerate(st_categories):
        cat_cases = by_category[cat]
        needed = st_per_cat

        # Start with originals
        pool = list(cat_cases)

        # Phase 1a: Scenario swap — generates variants with different states
        swapped = []
        for case in cat_cases:
            src_scen = case["scenario"]
            other_scens = [s for s in SCENARIOS if s != src_scen]
            dst = random.choice(other_scens)
            swapped_case = swap_scenario_single_turn(case, dst)
            if swapped_case:
                swapped.append(swapped_case)
        pool.extend(swapped)

        # If we already have enough, just trim
        if len(pool) >= needed:
            random.shuffle(pool)
            pool = pool[:needed]
        else:
            # Queue paraphrases for the gap
            gap = needed - len(pool)
            sources = []
            while len(sources) < gap:
                sources.extend(pool)
            for j, src in enumerate(sources[:gap]):
                para_queue_st.append((cat_idx, src, j))

        augmented_st.append((cat, pool, needed))
        print(f"  {cat}: {len(cat_cases)} orig + {len(swapped)} swapped = {len(pool)} "
              f"(need {needed}, gap={max(0, needed - len(pool))})")

    # Phase 1b: Paraphrase ALL augmented cases (swapped ones) to ensure unique inputs
    # Also paraphrase to fill gaps
    if not args.skip_paraphrase:
        # First: paraphrase all swapped cases in-place to differentiate them
        all_swapped_indices = []
        for cat_idx, (cat, pool, needed) in enumerate(augmented_st):
            for i, case in enumerate(pool):
                if "_swap_" in case.get("id", ""):
                    all_swapped_indices.append((cat_idx, i))

        print(f"\n  Phase 1b: Paraphrasing {len(all_swapped_indices)} swapped + "
              f"{len(para_queue_st)} gap-fill cases...")

        # Paraphrase swapped cases (in-place)
        batch_size = 64
        for batch_start in range(0, len(all_swapped_indices), batch_size):
            batch = all_swapped_indices[batch_start:batch_start + batch_size]
            tasks = []
            for (cat_idx, pool_idx) in batch:
                cat, pool, needed = augmented_st[cat_idx]
                case = pool[pool_idx]
                tasks.append(paraphrase_one(client, args.model, case["input"], semaphore))

            results = await asyncio.gather(*tasks)
            for (cat_idx, pool_idx), new_input in zip(batch, results):
                cat, pool, needed = augmented_st[cat_idx]
                pool[pool_idx]["input"] = new_input

            done = min(batch_start + batch_size, len(all_swapped_indices))
            print(f"    Swapped paraphrased: {done}/{len(all_swapped_indices)}", end="\r")

        if all_swapped_indices:
            print(f"    Swapped paraphrased: {len(all_swapped_indices)}/{len(all_swapped_indices)}")

        # Paraphrase gap-fill cases
        if para_queue_st:
            completed = 0
            for batch_start in range(0, len(para_queue_st), batch_size):
                batch = para_queue_st[batch_start:batch_start + batch_size]
                tasks = [
                    paraphrase_single_turn(client, args.model, src, vid, semaphore)
                    for (_, src, vid) in batch
                ]
                results = await asyncio.gather(*tasks)

                for (cat_idx, _, _), result in zip(batch, results):
                    cat, pool, needed = augmented_st[cat_idx]
                    pool.append(result)
                    augmented_st[cat_idx] = (cat, pool, needed)

                completed += len(batch)
                print(f"    Gap-fill paraphrased: {completed}/{len(para_queue_st)}", end="\r")
            print(f"    Gap-fill paraphrased: {completed}/{len(para_queue_st)}")
    elif args.skip_paraphrase:
        print(f"\n  Phase 1b: Skipped (--skip-paraphrase)")

    # Collect all single-turn (trim each category to target)
    final_st = []
    for cat, pool, needed in augmented_st:
        random.shuffle(pool)
        final_st.extend(pool[:needed])

    # Balance scenarios within each category
    print(f"\n  Balancing scenarios...")
    st_scen_dist = {}
    for c in final_st:
        st_scen_dist[c["scenario"]] = st_scen_dist.get(c["scenario"], 0) + 1
    print(f"    Scenario dist: {st_scen_dist}")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 2: Augment multi-turn data
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  Phase 2: Augmenting multi-turn ({len(mt_data)} → {mt_target})")
    print(f"{'='*60}")

    # Start with originals
    mt_pool = list(mt_data)
    mt_seen_ids: Set[str] = {c["id"] for c in mt_pool}

    # Phase 2a: Scenario swap
    mt_swapped = []
    for case in mt_data:
        src_scen = case["scenario"]
        other_scens = [s for s in SCENARIOS if s != src_scen]
        for dst in random.sample(other_scens, min(2, len(other_scens))):
            swapped = swap_scenario_multi_turn(case, dst)
            if swapped and swapped["id"] not in mt_seen_ids:
                mt_seen_ids.add(swapped["id"])
                mt_swapped.append(swapped)

    mt_pool.extend(mt_swapped)
    print(f"  Scenario swap: +{len(mt_swapped)} → {len(mt_pool)} total")

    # Phase 2b: Paraphrase
    if not args.skip_paraphrase and len(mt_pool) < mt_target:
        gap = mt_target - len(mt_pool)
        print(f"  Paraphrasing {gap} multi-turn variants...")

        sources = []
        while len(sources) < gap:
            sources.extend(mt_pool)
        sources = sources[:gap]

        batch_size = 16
        mt_paraphrased = []
        for batch_start in range(0, len(sources), batch_size):
            batch = sources[batch_start:batch_start + batch_size]
            tasks = [
                paraphrase_multi_turn(client, args.model, src, batch_start + j, semaphore)
                for j, src in enumerate(batch)
            ]
            results = await asyncio.gather(*tasks)
            for r in results:
                if r["id"] not in mt_seen_ids:
                    mt_seen_ids.add(r["id"])
                    mt_paraphrased.append(r)
            print(f"    {min(batch_start + batch_size, len(sources))}/{gap}", end="\r")
        print(f"    Paraphrased {len(mt_paraphrased)} multi-turn variants")
        mt_pool.extend(mt_paraphrased)

    final_mt = mt_pool[:mt_target]
    # Balance difficulty
    mt_diff_dist = {}
    for c in final_mt:
        mt_diff_dist[c.get("difficulty", "?")] = mt_diff_dist.get(c.get("difficulty", "?"), 0) + 1
    print(f"  Final: {len(final_mt)} | difficulty: {mt_diff_dist}")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 3: Augment web retrieval data
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  Phase 3: Augmenting web retrieval ({len(web_data)} → {web_target})")
    print(f"{'='*60}")

    web_pool = list(web_data)
    web_seen_ids: Set[str] = {c["id"] for c in web_pool}

    # Phase 3a: Scenario swap (just swap state context, query stays same)
    web_swapped = []
    for case in web_data:
        src_scen = case["scenario"]
        other_scens = [s for s in SCENARIOS if s != src_scen]
        for dst in random.sample(other_scens, min(2, len(other_scens))):
            new_case = deepcopy(case)
            new_case["scenario"] = dst
            new_case["source_state"] = build_state(dst)
            new_case["target_state"] = build_state(dst)
            new_case["id"] = f"{case['id']}_swap_{dst[:3]}"
            if new_case["id"] not in web_seen_ids:
                web_seen_ids.add(new_case["id"])
                web_swapped.append(new_case)

    web_pool.extend(web_swapped)
    print(f"  Scenario swap: +{len(web_swapped)} → {len(web_pool)} total")

    # Phase 3b: Paraphrase
    if not args.skip_paraphrase and len(web_pool) < web_target:
        gap = web_target - len(web_pool)
        print(f"  Paraphrasing {gap} web variants...")

        sources = []
        while len(sources) < gap:
            sources.extend(web_pool)
        sources = sources[:gap]

        batch_size = 32
        web_paraphrased = []
        for batch_start in range(0, len(sources), batch_size):
            batch = sources[batch_start:batch_start + batch_size]
            tasks = [
                paraphrase_web_case(client, args.model, src, batch_start + j, semaphore)
                for j, src in enumerate(batch)
            ]
            results = await asyncio.gather(*tasks)
            for r in results:
                if r["id"] not in web_seen_ids:
                    web_seen_ids.add(r["id"])
                    web_paraphrased.append(r)
            print(f"    {min(batch_start + batch_size, len(sources))}/{gap}", end="\r")
        print(f"    Paraphrased {len(web_paraphrased)} web variants")
        web_pool.extend(web_paraphrased)

    final_web = web_pool[:web_target]
    web_cat_dist = {}
    for c in final_web:
        desc = c.get("description", "")
        cat = desc.split(":")[0] if ":" in desc else "other"
        web_cat_dist[cat] = web_cat_dist.get(cat, 0) + 1
    print(f"  Final: {len(final_web)} | categories: {web_cat_dist}")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 4: Validation
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  Phase 4: Validation")
    print(f"{'='*60}")

    st_errors = 0
    for c in final_st:
        errs = validate_single_turn(c)
        if errs:
            st_errors += 1

    mt_errors = 0
    for c in final_mt:
        errs = validate_multi_turn(c)
        if errs:
            mt_errors += 1

    web_errors = 0
    for c in final_web:
        errs = validate_web(c)
        if errs:
            web_errors += 1

    print(f"  Single-turn: {len(final_st)} cases, {st_errors} invalid")
    print(f"  Multi-turn:  {len(final_mt)} cases, {mt_errors} invalid")
    print(f"  Web:         {len(final_web)} cases, {web_errors} invalid")

    # Remove invalid cases
    if st_errors or mt_errors or web_errors:
        final_st = [c for c in final_st if not validate_single_turn(c)]
        final_mt = [c for c in final_mt if not validate_multi_turn(c)]
        final_web = [c for c in final_web if not validate_web(c)]
        print(f"  After cleanup: {len(final_st)} + {len(final_mt)} + {len(final_web)}")

    # Check uniqueness
    all_ids = [c["id"] for c in final_st] + [c["id"] for c in final_mt] + [c["id"] for c in final_web]
    dupes = len(all_ids) - len(set(all_ids))
    print(f"  Duplicate IDs: {dupes}")

    # Check input uniqueness
    st_inputs = set(c["input"] for c in final_st)
    mt_inputs = set(" | ".join(t["input"] for t in c["turns"]) for c in final_mt)
    web_inputs = set(c["input"] for c in final_web)
    print(f"  Unique inputs: st={len(st_inputs)}/{len(final_st)}, "
          f"mt={len(mt_inputs)}/{len(final_mt)}, web={len(web_inputs)}/{len(final_web)}")

    # ══════════════════════════════════════════════════════════════════════════
    # PHASE 5: Save
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  Phase 5: Saving")
    print(f"{'='*60}")

    total = len(final_st) + len(final_mt) + len(final_web)
    print(f"\n  TOTAL: {total} cases")

    # Final stats
    st_cat_final = {}
    for c in final_st:
        st_cat_final[c["category"]] = st_cat_final.get(c["category"], 0) + 1
    print(f"\n  Single-turn by category:")
    for cat in sorted(st_cat_final):
        print(f"    {cat}: {st_cat_final[cat]}")

    st_scen_final = {}
    for c in final_st:
        st_scen_final[c["scenario"]] = st_scen_final.get(c["scenario"], 0) + 1
    print(f"\n  Single-turn by scenario: {st_scen_final}")

    # Save
    st_path = output_dir / "dataset_10k.json"
    st_path.write_text(json.dumps(final_st, indent=2))
    print(f"\n  Saved: {st_path} ({len(final_st)} cases)")

    mt_path = output_dir / "multi_turn_dataset_10k.json"
    mt_path.write_text(json.dumps(final_mt, indent=2))
    print(f"  Saved: {mt_path} ({len(final_mt)} cases)")

    web_path = output_dir / "web_retrieval_dataset_10k.json"
    web_path.write_text(json.dumps(final_web, indent=2))
    print(f"  Saved: {web_path} ({len(final_web)} cases)")

    print(f"\n{'='*60}")
    print(f"  DONE! {len(final_st)} + {len(final_mt)} + {len(final_web)} = {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
