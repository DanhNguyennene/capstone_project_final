#!/usr/bin/env python3
"""Side-by-side comparison of three models on the same eval dataset.

Pass any number of (label, path-to-results.json) pairs. The results file may be
either the single-turn `scenario_eval` snapshot (with `metrics` + `results`)
or the multi-turn `multi_turn_eval` snapshot (with `summary` + `results`).

Headline metrics + per-category pass rate + per-category overlap with the
training split (from evaluation/regen_test_ids.py).

Usage:
    python evaluation/compare_models.py \
        --st gpt5mini=evaluation/results/eval_all_20260504_rescored.json \
        --st ft=evaluation/results/<ft_run>.json \
        --st qwen=evaluation/results/<qwen_base_run>.json \
        --mt gpt5mini=evaluation/results/multi_turn_20260505_012523.json \
        --mt ft=evaluation/results/<ft_mt>.json \
        --mt qwen=evaluation/results/<qwen_mt>.json
"""
from __future__ import annotations
import argparse, json, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stratified_split(seed: int = 42, ratio: float = 0.2):
    data = json.loads((ROOT / "evaluation" / "dataset.json").read_text())
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in data:
        buckets[(r.get("category", "?"), r.get("scenario", "?"))].append(r)
    train, test = [], []
    for key in sorted(buckets):
        b = buckets[key][:]
        rng.shuffle(b)
        n_test = max(1, round(len(b) * ratio)) if len(b) >= 2 else 0
        test.extend(b[:n_test])
        train.extend(b[n_test:])
    return ({r["id"] for r in train}, {r["id"] for r in test},
            {r["id"]: r.get("category", "?") for r in data})


def load_pairs(args_list: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for spec in args_list or []:
        if "=" not in spec:
            raise SystemExit(f"--st/--mt expects label=path, got: {spec}")
        label, path = spec.split("=", 1)
        p = Path(path)
        if not p.is_absolute():
            p = (ROOT / path).resolve()
        out[label] = json.loads(p.read_text(encoding="utf-8"))
    return out


def fmt_pct(x: float | None) -> str:
    return f"{x*100:5.1f}%" if isinstance(x, (int, float)) else "  n/a"


def report_single_turn(loaded: dict[str, dict], train_ids: set, test_ids: set,
                        cat_by_id: dict[str, str]) -> None:
    if not loaded:
        return
    print("=" * 78)
    print("SINGLE-TURN  (scenario_eval)")
    print("=" * 78)

    # Headline metrics
    rows = []
    for label, snap in loaded.items():
        m = snap.get("metrics", {})
        results = snap.get("results", [])
        n = len(results)
        n_failed = sum(1 for r in results if not r.get("passed"))
        rows.append((label, n, m.get("BAR"), m.get("SVR"), m.get("CSR"),
                     m.get("pass_rate", (n - n_failed) / n if n else None),
                     m.get("avg_tool_recall"), m.get("avg_judge_score"),
                     m.get("avg_latency_s")))
    hdr = f"{'model':<10} {'N':>5} {'BAR':>7} {'SVR':>7} {'CSR':>7} {'pass':>7} {'recall':>7} {'judge':>7} {'lat(s)':>7}"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print(f"{r[0]:<10} {r[1]:>5} " + " ".join(fmt_pct(x) if i < 5 else f"{x:>7.2f}" if isinstance(x, (int, float)) else "    n/a"
                                                   for i, x in enumerate(r[2:])))

    # Per-category pass rate
    print("\nPer-category pass rate:")
    cats = sorted({cat_by_id.get(r.get("test_id"), "?")
                   for snap in loaded.values() for r in snap.get("results", [])})
    hdr = f"{'category':<14} " + " ".join(f"{lbl:>10}" for lbl in loaded)
    print(hdr); print("-" * len(hdr))
    for c in cats:
        cells = []
        for snap in loaded.values():
            results = [r for r in snap.get("results", []) if cat_by_id.get(r.get("test_id")) == c]
            if not results:
                cells.append("    n/a"); continue
            pr = sum(1 for r in results if r.get("passed")) / len(results)
            cells.append(f"{pr*100:5.1f}% ({len(results):>3})")
        print(f"{c:<14} " + " ".join(f"{x:>10}" for x in cells))

    # Held-out vs leaked split
    print("\nPass rate on TRAIN-only ids vs TEST-only (615) ids:")
    hdr = f"{'model':<10} {'train pass':>14} {'test pass':>14}"
    print(hdr); print("-" * len(hdr))
    for label, snap in loaded.items():
        results = snap.get("results", [])
        tr = [r for r in results if r.get("test_id") in train_ids]
        te = [r for r in results if r.get("test_id") in test_ids]
        tr_pr = sum(1 for r in tr if r.get("passed")) / len(tr) if tr else None
        te_pr = sum(1 for r in te if r.get("passed")) / len(te) if te else None
        print(f"{label:<10} {fmt_pct(tr_pr) + ' (' + str(len(tr)) + ')':>14} "
              f"{fmt_pct(te_pr) + ' (' + str(len(te)) + ')':>14}")
    print()


def report_multi_turn(loaded: dict[str, dict]) -> None:
    if not loaded:
        return
    print("=" * 78)
    print("MULTI-TURN  (multi_turn_eval)")
    print("=" * 78)
    hdr = f"{'model':<10} {'conv':>5} {'turns':>6} {'conv_pass':>10} {'turn_pass':>10} {'ctx_ret':>9} {'lat(s)':>8}"
    print(hdr); print("-" * len(hdr))
    for label, snap in loaded.items():
        s = snap.get("summary") or snap.get("metrics") or {}
        results = snap.get("results", [])
        n_conv = len(results)
        n_turn = sum(len(r.get("turns", [])) for r in results)
        conv_pass = s.get("conversation_pass_rate")
        if conv_pass is None and results:
            conv_pass = sum(1 for r in results if r.get("all_turns_passed")) / n_conv
        turn_pass = s.get("turn_pass_rate")
        if turn_pass is None and results:
            tot = sum(1 for r in results for t in r.get("turns", []) if t.get("passed"))
            turn_pass = tot / n_turn if n_turn else None
        ctx = s.get("avg_context_retention")
        if ctx is None and results:
            xs = [r.get("avg_context_retention") for r in results if isinstance(r.get("avg_context_retention"), (int, float))]
            ctx = sum(xs) / len(xs) if xs else None
        lat = s.get("avg_latency_s")
        if lat is None and results:
            xs = [r.get("total_latency_s") for r in results if isinstance(r.get("total_latency_s"), (int, float))]
            lat = sum(xs) / len(xs) if xs else None
        print(f"{label:<10} {n_conv:>5} {n_turn:>6} {fmt_pct(conv_pass):>10} {fmt_pct(turn_pass):>10} "
              f"{fmt_pct(ctx):>9} {(f'{lat:>7.1f}' if isinstance(lat,(int,float)) else '    n/a'):>8}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--st", action="append", help="single-turn label=path")
    ap.add_argument("--mt", action="append", help="multi-turn label=path")
    args = ap.parse_args()

    train_ids, test_ids, cat_by_id = stratified_split()
    report_single_turn(load_pairs(args.st or []), train_ids, test_ids, cat_by_id)
    report_multi_turn(load_pairs(args.mt or []))


if __name__ == "__main__":
    main()
