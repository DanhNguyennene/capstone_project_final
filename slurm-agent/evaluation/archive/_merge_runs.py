"""One-off: merge full 3135-case GPT-5-mini run with 570-case rerun."""
import json

full = json.load(open("evaluation/results/eval_latest_snapshot.json", encoding="utf-8"))
rerun = json.load(open("evaluation/results/eval_all_20260504_105136.json", encoding="utf-8"))

full_ids = {r["test_id"] for r in full["results"]}
rerun_ids = {r["test_id"] for r in rerun["results"]}
overlap = full_ids & rerun_ids
only_rerun = rerun_ids - full_ids

print(f"Full:    {len(full_ids)} unique IDs ({len(full['results'])} rows)")
print(f"Rerun:   {len(rerun_ids)} unique IDs ({len(rerun['results'])} rows)")
print(f"Overlap: {len(overlap)}")
print(f"Only in rerun (new): {len(only_rerun)}")

# Merge: rerun overwrites full for overlapping IDs
merged = {}
for r in full["results"]:
    merged[r["test_id"]] = r
for r in rerun["results"]:
    merged[r["test_id"]] = r

total = len(merged)
passed = sum(1 for r in merged.values() if r.get("passed", False))
full_passed = sum(1 for r in full["results"] if r.get("passed", False))

print(f"\nFull alone: {len(full['results'])} cases, {full_passed} passed, {full_passed/len(full['results']):.4f}")
print(f"Merged:     {total} cases, {passed} passed, {passed/total:.4f}")

out = dict(full)
out["results"] = sorted(merged.values(), key=lambda x: x["test_id"])
out["metrics"] = dict(out.get("metrics", {}))
out["metrics"]["pass_rate"] = round(passed / total, 4)
out["metrics"]["total"] = total
out["metrics"]["passed"] = passed
out["_merge_note"] = f"Merged: {len(full['results'])} full + {len(rerun['results'])} rerun, {len(overlap)} replaced by rerun"

json.dump(out, open("evaluation/results/eval_gpt5mini_merged.json", "w", encoding="utf-8"), indent=2)
print(f"\nSaved -> evaluation/results/eval_gpt5mini_merged.json")
