"""Verify mock_tool_outputs_5x64.json: scenario × arg-variant × tool coverage."""
import json
from pathlib import Path

d = json.load(open("mock_tool_outputs_5x64.json"))
scenarios = list(d.keys())
base_keys = set(d[scenarios[0]].keys())

# ── 1. Key consistency ───────────────────────────────────────────────────────
print("=== Key consistency across scenarios ===")
all_same = True
for sc in scenarios[1:]:
    diff = base_keys.symmetric_difference(d[sc].keys())
    if diff:
        print(f"  {sc}: MISMATCH {diff}")
        all_same = False
if all_same:
    print(f"  All {len(scenarios)} scenarios have identical {len(base_keys)} keys  OK")

# ── 2. Per-key status per scenario ───────────────────────────────────────────
print()
W = 46
hdr = f"{'KEY':<{W}}" + "".join(f"{sc[:11]:<12}" for sc in scenarios)
print(hdr)
print("-" * len(hdr))

problems = []
for key in sorted(base_keys):
    row = f"{key:<{W}}"
    for sc in scenarios:
        val = d[sc].get(key, "MISSING")
        if not val or val.startswith("ERROR"):
            tag = "ERR"
            problems.append((sc, key, val[:60]))
        elif val.startswith("(no "):
            tag = "N/A"   # expected: no job of that type in this scenario
        else:
            tag = "OK"
        row += f"{tag:<12}"
    print(row)

# ── 3. Summary ───────────────────────────────────────────────────────────────
print()
total = len(scenarios) * len(base_keys)
na_count = sum(
    1 for sc in scenarios for key in base_keys
    if d[sc].get(key, "").startswith("(no ")
)
err_count = len(problems)
print(f"Total cells : {total}")
print(f"OK          : {total - na_count - err_count}")
print(f"N/A         : {na_count}  (expected — e.g. no pending job in 'failed' scenario)")
print(f"ERR         : {err_count}")
if problems:
    print("Problems:")
    for sc, key, val in problems:
        print(f"  [{sc}] {key}: {val}")
