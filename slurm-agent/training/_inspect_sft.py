"""One-shot script to deeply inspect SFT v3 base data quality."""
import json, sys, collections, textwrap
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/agent_sft_v3_base.jsonl")
rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

print(f"=== FILE: {path.name}  ({len(rows)} rows) ===\n")

# ── 1. Structure check ──
print("── 1. ROW STRUCTURE ──")
r0 = rows[0]
print(f"  Keys: {sorted(r0.keys())}")
for k in sorted(r0.keys()):
    if k not in ("messages", "tools"):
        print(f"  {k}: {r0[k]}")
print()

# ── 2. System prompt check ──
print("── 2. SYSTEM PROMPTS ──")
sys_prompts = set()
for r in rows:
    msgs = r["messages"]
    if msgs and msgs[0]["role"] == "system":
        sys_prompts.add(msgs[0]["content"][:80])
for sp in sorted(sys_prompts):
    count = sum(1 for r in rows if r["messages"][0].get("content","")[:80] == sp)
    print(f"  [{count:4d}x] {sp}...")
print()

# ── 3. Tool schema check ──
print("── 3. TOOL SCHEMAS ──")
all_declared = set()
for r in rows:
    for t in r.get("tools", []):
        all_declared.add(t["function"]["name"])
print(f"  Declared tools: {sorted(all_declared)}")

all_called = collections.Counter()
for r in rows:
    for m in r["messages"]:
        for tc in m.get("tool_calls", []):
            all_called[tc["function"]["name"]] += 1
print(f"  Called tools:   {sorted(all_called.keys())}")
undeclared = set(all_called.keys()) - all_declared
if undeclared:
    print(f"  !! UNDECLARED tools called: {undeclared}")
else:
    print(f"  All called tools are declared in schemas")
print(f"\n  Tool call counts:")
for name, cnt in all_called.most_common():
    flag = " *** NOT IN SCHEMA" if name in undeclared else ""
    print(f"    {name:35s} {cnt:4d}{flag}")
print()

# ── 4. Message structure checks ──
print("── 4. MESSAGE STRUCTURE ──")
issues = []
for idx, r in enumerate(rows):
    msgs = r["messages"]
    tid = r.get("test_id", f"row_{idx}")
    
    # Check: starts with system
    if not msgs or msgs[0]["role"] != "system":
        issues.append((tid, "missing system message"))
    
    # Check: has user message
    if not any(m["role"] == "user" for m in msgs):
        issues.append((tid, "no user message"))
    
    # Check: ends with assistant
    if msgs[-1]["role"] != "assistant":
        issues.append((tid, f"last msg is {msgs[-1]['role']}, not assistant"))
    
    # Check: assistant with tool_calls has content=None or empty
    for i, m in enumerate(msgs):
        if m["role"] == "assistant" and m.get("tool_calls"):
            if m.get("content") and m["content"].strip():
                issues.append((tid, f"msg[{i}] assistant has both content AND tool_calls"))
    
    # Check: every tool_call has a matching tool response
    for i, m in enumerate(msgs):
        if m["role"] == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                tc_id = tc["id"]
                found = any(m2.get("tool_call_id") == tc_id for m2 in msgs[i+1:])
                if not found:
                    issues.append((tid, f"tool_call {tc_id} has no tool response"))
    
    # Check: tool response without preceding tool_call
    for i, m in enumerate(msgs):
        if m["role"] == "tool":
            tc_id = m.get("tool_call_id", "")
            found = any(
                tc["id"] == tc_id 
                for m2 in msgs[:i] if m2.get("tool_calls")
                for tc in m2["tool_calls"]
            )
            if not found:
                issues.append((tid, f"orphan tool response {tc_id}"))
    
    # Check: empty final response
    if msgs[-1]["role"] == "assistant":
        content = msgs[-1].get("content", "")
        if not content or not content.strip():
            issues.append((tid, "empty final assistant response"))

if issues:
    print(f"  Found {len(issues)} issues:")
    for tid, issue in issues[:30]:
        print(f"    {tid}: {issue}")
    if len(issues) > 30:
        print(f"    ... and {len(issues)-30} more")
else:
    print(f"  All {len(rows)} rows have valid message structure")
print()

# ── 5. Role distribution ──
print("── 5. ROLE / CATEGORY DISTRIBUTION ──")
roles = collections.Counter(r.get("role","?") for r in rows)
cats = collections.Counter(r.get("category","?") for r in rows)
sources = collections.Counter(r.get("source","?") for r in rows)
print(f"  Roles:      {dict(roles)}")
print(f"  Sources:    {dict(sources)}")
print(f"  Categories: {dict(cats)}")
print()

# ── 6. Spot-check samples ──
def show_sample(label, row):
    print(f"\n  --- {label}: {row.get('test_id','?')} (cat={row.get('category','?')}, role={row.get('role','?')}) ---")
    for i, m in enumerate(row["messages"]):
        role = m["role"]
        content = m.get("content", "")
        tc = m.get("tool_calls", [])
        tcid = m.get("tool_call_id", "")
        if role == "system":
            print(f"    [{i}] system: ({len(content)} chars)")
        elif role == "user":
            print(f"    [{i}] user: {content[:120]}")
        elif role == "assistant" and tc:
            print(f"    [{i}] assistant: tool_calls={len(tc)}")
            for t in tc:
                fn = t["function"]
                args = fn.get("arguments","")
                print(f"         -> {fn['name']}({args[:100]})")
        elif role == "tool":
            print(f"    [{i}] tool[{tcid[:20]}]: {(content or '')[:100]}")
        elif role == "assistant":
            print(f"    [{i}] assistant: {(content or '')[:150]}")

print("── 6. SPOT-CHECK SAMPLES ──")

# Find one of each interesting type
observer_with_tools = next((r for r in rows if r.get("role")=="observer" and any(m.get("tool_calls") for m in r["messages"])), None)
operator_sample = next((r for r in rows if r.get("role")=="operator"), None)
no_tool_sample = next((r for r in rows if not any(m.get("tool_calls") for m in r["messages"])), None)
docs_sample = next((r for r in rows if r.get("category")=="docs"), None)
safety_sample = next((r for r in rows if r.get("category")=="safety"), None)
multi_step = next((r for r in rows if r.get("category")=="multi_step"), None)

if observer_with_tools: show_sample("OBSERVER+TOOLS", observer_with_tools)
if operator_sample: show_sample("OPERATOR", operator_sample)
if no_tool_sample: show_sample("NO-TOOL (clarification)", no_tool_sample)
if docs_sample: show_sample("DOCS/LOOKUP", docs_sample)
if safety_sample: show_sample("SAFETY", safety_sample)
if multi_step: show_sample("MULTI-STEP", multi_step)

# ── 7. Token length distribution ──
print("\n\n── 7. TOKEN LENGTH ESTIMATES ──")
lengths = []
for r in rows:
    total_chars = sum(len(json.dumps(m)) for m in r["messages"])
    lengths.append(total_chars)
lengths.sort()
print(f"  Min chars:    {lengths[0]}")
print(f"  Median chars: {lengths[len(lengths)//2]}")
print(f"  P95 chars:    {lengths[int(len(lengths)*0.95)]}")
print(f"  P99 chars:    {lengths[int(len(lengths)*0.99)]}")
print(f"  Max chars:    {lengths[-1]}")
# Rough token estimate (4 chars per token)
print(f"  Est tokens (median): ~{lengths[len(lengths)//2]//4}")
print(f"  Est tokens (p95):    ~{lengths[int(len(lengths)*0.95)]//4}")
print(f"  Est tokens (max):    ~{lengths[-1]//4}")

print("\n\n=== INSPECTION COMPLETE ===")
