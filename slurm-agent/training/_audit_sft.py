"""Deep quality audit of SFT v3 data — check for weird tokens, template pollution,
response quality, tool arg correctness, and Qwen chat template compatibility."""
import json, sys, re, collections
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/agent_sft_v3_base.jsonl")
rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Auditing {len(rows)} rows from {path.name}\n")

issues = []

# ── 1. Weird/broken tokens ──
print("== 1. WEIRD TOKEN SCAN ==")
WEIRD_PATTERNS = [
    (r"\\u[0-9a-fA-F]{4}", "unicode escape in text"),
    (r"\\n\\n", "literal \\n in text (should be real newline)"),
    (r"\x00", "null byte"),
    (r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>", "Qwen special token in content"),
    (r"<\|tool_call\|>|<\|tool_response\|>", "Qwen tool token in content"),
    (r"\{%.*%\}|\{\{.*\}\}", "Jinja template syntax"),
    (r"(?:^|\s)None(?:\s|$|,|\.|!)", "Python None literal (should be null/empty)"),
    (r"<\|START_OF_TURN\|>|<\|END_OF_TURN\|>", "Gemma turn tokens"),
    (r"\[INST\]|\[/INST\]", "Llama inst tokens"),
    (r"<<SYS>>|<</SYS>>", "Llama sys tokens"),
]

weird_counts = collections.Counter()
for idx, row in enumerate(rows):
    for m in row["messages"]:
        content = m.get("content") or ""
        for tc in m.get("tool_calls", []):
            content += " " + tc.get("function", {}).get("arguments", "")
        for pattern, label in WEIRD_PATTERNS:
            if re.search(pattern, content):
                weird_counts[label] += 1
                if weird_counts[label] <= 2:
                    tid = row.get("test_id", f"row_{idx}")
                    issues.append(f"WEIRD: {tid}: {label}")

if weird_counts:
    for label, cnt in weird_counts.most_common():
        print(f"  {label}: {cnt}")
else:
    print("  No weird tokens found")

# ── 2. Template pollution (v1/v2 garbage) ──
print("\n== 2. TEMPLATE POLLUTION ==")
POLLUTION_PATTERNS = [
    r"Here(?:'s| is) (?:the|a) summary of",
    r"I(?:'ve| have) (?:successfully |already )?(?:cancelled|submitted|updated|drained|released|requeued)",
    r"(?:Job|Jobs) (?:has|have) been (?:successfully )?(?:cancelled|submitted|held|released|requeued)",
    r"The following jobs? (?:has|have) been",
    r"Action completed successfully",
    r"✅ Done\.",
    r"I'll help you with that",
    r"Sure,? (?:I can|let me|I'll)",
    r"Based on (?:the|my) (?:analysis|review|examination)",
]
pollution_counts = collections.Counter()
for idx, row in enumerate(rows):
    last_msg = row["messages"][-1]
    if last_msg["role"] == "assistant" and last_msg.get("content"):
        resp = last_msg["content"]
        for pattern in POLLUTION_PATTERNS:
            if re.search(pattern, resp, re.IGNORECASE):
                pollution_counts[pattern] += 1

if pollution_counts:
    for pattern, cnt in pollution_counts.most_common():
        print(f"  [{cnt:3d}x] {pattern}")
else:
    print("  No template pollution found")

# ── 3. Response quality ──
print("\n== 3. RESPONSE QUALITY ==")
short_responses = []
empty_responses = []
very_long = []
for idx, row in enumerate(rows):
    last_msg = row["messages"][-1]
    content = last_msg.get("content", "") or ""
    tid = row.get("test_id", f"row_{idx}")
    if not content.strip():
        empty_responses.append(tid)
    elif len(content.strip()) < 20:
        short_responses.append((tid, content.strip()))
    elif len(content) > 3000:
        very_long.append((tid, len(content)))

print(f"  Empty responses:  {len(empty_responses)}")
if empty_responses[:5]:
    for tid in empty_responses[:5]:
        print(f"    {tid}")
print(f"  Short (<20 char): {len(short_responses)}")
for tid, resp in short_responses[:5]:
    print(f"    {tid}: '{resp}'")
print(f"  Very long (>3k):  {len(very_long)}")
for tid, l in very_long[:5]:
    print(f"    {tid}: {l} chars")

# ── 4. Tool arg validity ──
print("\n== 4. TOOL ARG VALIDITY ==")
bad_args = []
empty_args = 0
total_calls = 0
for idx, row in enumerate(rows):
    tid = row.get("test_id", f"row_{idx}")
    for m in row["messages"]:
        for tc in m.get("tool_calls", []):
            total_calls += 1
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args_str = fn.get("arguments", "")
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError:
                bad_args.append((tid, name, f"invalid JSON: {args_str[:60]}"))
                continue
            if not isinstance(args, dict):
                bad_args.append((tid, name, f"args is {type(args).__name__}, not dict"))
                continue
            if not args:
                empty_args += 1
            # Check for double-encoded JSON
            for k, v in args.items():
                if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
                    try:
                        json.loads(v)
                        bad_args.append((tid, name, f"double-encoded JSON in arg '{k}'"))
                    except Exception:
                        pass

print(f"  Total tool calls: {total_calls}")
print(f"  Empty args: {empty_args}")
print(f"  Bad args:   {len(bad_args)}")
for tid, name, reason in bad_args[:10]:
    print(f"    {tid}: {name} -> {reason}")

# ── 5. Tool call/response pairing ──
print("\n== 5. TOOL CALL/RESPONSE PAIRING ==")
mismatched = 0
for idx, row in enumerate(rows):
    tid = row.get("test_id", f"row_{idx}")
    msgs = row["messages"]
    all_call_ids = set()
    all_resp_ids = set()
    for m in msgs:
        for tc in m.get("tool_calls", []):
            all_call_ids.add(tc["id"])
        if m.get("tool_call_id"):
            all_resp_ids.add(m["tool_call_id"])
    orphan_calls = all_call_ids - all_resp_ids
    orphan_resps = all_resp_ids - all_call_ids
    if orphan_calls or orphan_resps:
        mismatched += 1
        if mismatched <= 5:
            print(f"  {tid}: orphan_calls={orphan_calls} orphan_resps={orphan_resps}")
print(f"  Mismatched rows: {mismatched}")

# ── 6. Conversation flow validity ──
print("\n== 6. CONVERSATION FLOW ==")
flow_issues = 0
for idx, row in enumerate(rows):
    tid = row.get("test_id", f"row_{idx}")
    msgs = row["messages"]
    
    # system must be first
    if msgs[0]["role"] != "system":
        flow_issues += 1
        issues.append(f"FLOW: {tid}: first msg is {msgs[0]['role']}")
    
    # Must end with assistant
    if msgs[-1]["role"] != "assistant":
        flow_issues += 1
        issues.append(f"FLOW: {tid}: last msg is {msgs[-1]['role']}")
    
    # tool response must follow assistant with tool_calls
    for i, m in enumerate(msgs):
        if m["role"] == "tool" and i > 0:
            prev = msgs[i-1]
            # Previous should be assistant+tool_calls or another tool response
            if prev["role"] not in ("assistant", "tool"):
                flow_issues += 1
                if flow_issues <= 5:
                    issues.append(f"FLOW: {tid}: tool response after {prev['role']} at pos {i}")

print(f"  Flow issues: {flow_issues}")

# ── 7. System prompt matches real agent ──
print("\n== 7. SYSTEM PROMPT VERIFICATION ==")
observer_sys = None
operator_sys = None
for row in rows:
    role = row.get("role", "")
    sys_content = row["messages"][0]["content"]
    if role == "observer" and observer_sys is None:
        observer_sys = sys_content
    elif role == "operator" and operator_sys is None:
        operator_sys = sys_content
    if observer_sys and operator_sys:
        break

# Check observer prompt has key sections
obs_checks = [
    ("RULES section", "RULES" in observer_sys),
    ("tool routing table", "squeue" in observer_sys),
    ("transfer_to_operator mention", "transfer_to_operator" in observer_sys),
    ("safety guardrails", "safety" in observer_sys.lower() or "dangerous" in observer_sys.lower()),
    ("lookup_slurm_docs mention", "lookup_slurm_docs" in observer_sys),
    ("reasonable length", 5000 < len(observer_sys) < 20000),
]
print(f"  Observer system prompt ({len(observer_sys)} chars):")
for check, passed in obs_checks:
    status = "OK" if passed else "MISSING"
    print(f"    [{status}] {check}")

op_checks = [
    ("action executor role", "executor" in operator_sys.lower() or "action" in operator_sys.lower()),
    ("handoff mention", "handoff" in operator_sys.lower()),
    ("confirmation/HITL", "confirm" in operator_sys.lower() or "approval" in operator_sys.lower()),
    ("reasonable length", 2000 < len(operator_sys) < 15000),
]
print(f"  Operator system prompt ({len(operator_sys)} chars):")
for check, passed in op_checks:
    status = "OK" if passed else "MISSING"
    print(f"    [{status}] {check}")

# ── 8. Qwen chat template compatibility ──
print("\n== 8. QWEN TEMPLATE COMPAT ==")
qwen_issues = 0
for idx, row in enumerate(rows):
    tid = row.get("test_id", f"row_{idx}")
    msgs = row["messages"]
    for i, m in enumerate(msgs):
        # assistant with tool_calls: content must be None or empty
        if m["role"] == "assistant" and m.get("tool_calls"):
            c = m.get("content")
            if c is not None and c.strip():
                qwen_issues += 1
                if qwen_issues <= 3:
                    print(f"  {tid}: assistant msg[{i}] has content AND tool_calls")
        # tool_calls must have id, type, function.name, function.arguments
        for tc in m.get("tool_calls", []):
            if not tc.get("id") or not tc.get("function", {}).get("name"):
                qwen_issues += 1
                if qwen_issues <= 3:
                    print(f"  {tid}: malformed tool_call: {tc}")
        # tool response must have tool_call_id and content
        if m["role"] == "tool":
            if not m.get("tool_call_id"):
                qwen_issues += 1
                if qwen_issues <= 3:
                    print(f"  {tid}: tool msg[{i}] missing tool_call_id")
            if m.get("content") is None:
                qwen_issues += 1
                if qwen_issues <= 3:
                    print(f"  {tid}: tool msg[{i}] has None content")
print(f"  Qwen compat issues: {qwen_issues}")

# ── 9. Real trace vs synthetic check ──
print("\n== 9. REAL TRACE INDICATORS ==")
# Real traces should have varied responses, not cookie-cutter templates
responses = [row["messages"][-1].get("content", "") for row in rows if row["messages"][-1]["role"] == "assistant"]
# Check response diversity (unique first 50 chars)
unique_starts = len(set(r[:50] for r in responses if r))
print(f"  Total responses: {len(responses)}")
print(f"  Unique openings: {unique_starts} ({unique_starts*100//max(1,len(responses))}%)")

# Check for copy-paste responses
response_counter = collections.Counter(r[:100] for r in responses if r)
dupes = [(prefix, cnt) for prefix, cnt in response_counter.most_common(10) if cnt > 5]
if dupes:
    print(f"  Repeated response patterns (>5x):")
    for prefix, cnt in dupes:
        print(f"    [{cnt:3d}x] {prefix[:70]}...")
else:
    print("  No heavily repeated response patterns")

# ── SUMMARY ──
print(f"\n{'='*60}")
print(f"  AUDIT SUMMARY")
print(f"{'='*60}")
total_issues = len(issues) + mismatched + flow_issues + qwen_issues + len(bad_args) + len(empty_responses)
print(f"  Rows:              {len(rows)}")
print(f"  Weird tokens:      {sum(weird_counts.values())}")
print(f"  Template pollution: {sum(pollution_counts.values())}")
print(f"  Empty responses:   {len(empty_responses)}")
print(f"  Bad tool args:     {len(bad_args)}")
print(f"  Mismatched IDs:    {mismatched}")
print(f"  Flow issues:       {flow_issues}")
print(f"  Qwen compat:       {qwen_issues}")
print(f"  Response diversity: {unique_starts*100//max(1,len(responses))}%")

blockers = len(bad_args) + mismatched + flow_issues + qwen_issues + len(empty_responses)
if blockers == 0:
    print(f"\n  VERDICT: DATA IS CLEAN - READY FOR TRAINING")
else:
    print(f"\n  VERDICT: {blockers} BLOCKERS FOUND - FIX BEFORE TRAINING")
