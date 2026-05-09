"""Deep inconsistency audit — catches issues the basic audit missed.

Checks:
  1. Generic/templated responses (v1-style low-quality)
  2. Hallucination (response mentions entities not in tool output)
  3. HITL compliance (operator must ask for confirmation)
  4. Tool arg vs user request mismatch (e.g., TimeLimit wrong)
  5. Operator used wrong action (e.g., "resume" instead of "down")
  6. lookup_slurm_docs parroting (just echoes keywords)
  7. Empty/stub tool responses  
  8. Ceiling samples with wrong system prompt
  9. Role metadata vs actual behavior mismatch
  10. Duplicate samples
"""
import json, sys, re, hashlib
from collections import Counter, defaultdict
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/agent_sft_v3_base.jsonl")
rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Deep audit of {len(rows)} rows from {path.name}\n")

issues = []
stats = Counter()

# ── 1. Generic/templated responses ──
print("== 1. GENERIC RESPONSE DETECTION ==")
GENERIC_PATTERNS = [
    (r"^(?:The |Here's the |Based on ).*(?:information shows|status showing|data shows)[:\.]?\s*\w+(?:,\s*\w+)*\.?$", "keyword-only response"),
    (r"^(?:Action completed|I've completed|Bulk operation completed|I've submitted|I've executed).*(?:Keywords?:|Relevant:|Details:)", "templated action summary"),
    (r"^Regarding your (?:domain-specific )?query about .+: here's the relevant", "parroted query response"),
    (r"^From the Slurm documentation:.+See the official docs", "docs parrot"),
    (r"^This action affects multiple jobs\. I've executed it after confirmation\. Relevant:", "bulk action template"),
    (r"^I've completed the multi-step operation\. Results:", "multi-step template"),
    (r"^Action completed\. The operation affected:", "action template"),
    (r"^I've submitted the job\. The batch submission returned", "submit template"),
    (r"^Bulk operation completed for the matching targets\. Details:", "bulk template"),
]

generic_count = 0
generic_examples = []
for idx, row in enumerate(rows):
    last = row["messages"][-1]
    if last["role"] != "assistant" or not last.get("content"):
        continue
    content = last["content"].strip()
    for pattern, label in GENERIC_PATTERNS:
        if re.match(pattern, content, re.IGNORECASE | re.DOTALL):
            generic_count += 1
            tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
            if len(generic_examples) < 10:
                generic_examples.append((tid, label, content[:120]))
            stats[f"generic:{label}"] += 1
            break

print(f"  Generic responses: {generic_count}")
for tid, label, text in generic_examples:
    print(f"    [{label}] {tid}: {text}")

# ── 2. Hallucination check ──
print("\n== 2. HALLUCINATION CHECK ==")
# If assistant says "dave" but tool output never mentioned "dave"
hallucination_count = 0
for idx, row in enumerate(rows):
    msgs = row["messages"]
    # Collect all tool output text
    tool_text = ""
    for m in msgs:
        if m["role"] == "tool":
            tool_text += " " + (m.get("content") or "")
    
    last = msgs[-1]
    if last["role"] != "assistant" or not last.get("content"):
        continue
    
    content = last["content"]
    # Check if response mentions specific names/numbers not in any tool output or user message
    user_text = " ".join(m.get("content", "") or "" for m in msgs if m["role"] == "user")
    context_text = tool_text + " " + user_text
    
    # Extract job IDs mentioned in response
    response_ids = set(re.findall(r'\b(\d{4,})\b', content))
    context_ids = set(re.findall(r'\b(\d{4,})\b', context_text))
    hallucinated_ids = response_ids - context_ids
    if hallucinated_ids:
        hallucination_count += 1
        tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
        if hallucination_count <= 5:
            issues.append(f"HALLUCINATION: {tid}: mentions IDs {hallucinated_ids} not in context")

print(f"  Hallucinated IDs: {hallucination_count}")

# ── 3. HITL compliance (operator must confirm) ──
print("\n== 3. HITL COMPLIANCE ==")
no_confirm = 0
role_field = None
for idx, row in enumerate(rows):
    r = row.get("role", row.get("metadata", {}).get("role", ""))
    if r == "operator":
        msgs = row["messages"]
        # Find the operator system message
        has_operator_section = False
        first_operator_assistant = None
        for i, m in enumerate(msgs):
            if m["role"] == "system" and "operator" in (m.get("content") or "").lower():
                has_operator_section = True
            if has_operator_section and m["role"] == "assistant" and first_operator_assistant is None:
                first_operator_assistant = m
                break
        
        if first_operator_assistant:
            # Operator's first message should either ask for confirmation or have tool_calls
            content = first_operator_assistant.get("content") or ""
            tool_calls = first_operator_assistant.get("tool_calls") or []
            
            # If it immediately calls tools without asking for confirmation
            if tool_calls and not content:
                no_confirm += 1
                tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
                if no_confirm <= 5:
                    tc_names = [tc["function"]["name"] for tc in tool_calls]
                    issues.append(f"NO_HITL: {tid}: operator immediately calls {tc_names} without confirmation")

print(f"  Operator skips confirmation: {no_confirm}")

# ── 4. Wrong tool action ──
print("\n== 4. WRONG TOOL ACTION ==")
wrong_action = 0
for idx, row in enumerate(rows):
    msgs = row["messages"]
    # Find user request
    user_msg = ""
    for m in msgs:
        if m["role"] == "user":
            user_msg = m.get("content", "") or ""
            break
    
    for m in msgs:
        for tc in m.get("tool_calls", []):
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args_str = fn.get("arguments", "{}")
            try:
                args = json.loads(args_str)
            except:
                continue
            
            # Check: user says "down" but tool uses "resume"
            if name == "scontrol_node":
                state = args.get("state", "")
                if "down" in user_msg.lower() and state == "resume":
                    wrong_action += 1
                    tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
                    issues.append(f"WRONG_ACTION: {tid}: user wants down but got state={state}")
                elif "drain" in user_msg.lower() and state == "resume":
                    wrong_action += 1
                    tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
                    issues.append(f"WRONG_ACTION: {tid}: user wants drain but got state={state}")
            
            # Check: TimeLimit mismatch
            if name == "scontrol_update" and "updates" in args:
                updates = args["updates"]
                if "TimeLimit" in updates:
                    # Extract requested hours
                    hours_match = re.search(r'(\d+)\s*hours?', user_msg, re.I)
                    if hours_match:
                        requested = int(hours_match.group(1))
                        tl_match = re.search(r'TimeLimit=(\d+):(\d+):(\d+)', updates)
                        if tl_match:
                            actual_hours = int(tl_match.group(1))
                            if actual_hours != requested:
                                wrong_action += 1
                                tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
                                issues.append(f"WRONG_ACTION: {tid}: user wants {requested}h but TimeLimit={actual_hours}h")

print(f"  Wrong tool actions: {wrong_action}")

# ── 5. Stub/mock tool responses ──
print("\n== 5. STUB TOOL RESPONSES ==")
stub_count = 0
stub_patterns = [
    r"^Relevant information about the requested topic",
    r"^# Slurm Documentation:.*\nRelevant information",
    r"^No job found:",
    r"See `man slurm`",
]
for idx, row in enumerate(rows):
    for m in row["messages"]:
        if m["role"] == "tool":
            content = m.get("content", "") or ""
            for p in stub_patterns:
                if re.search(p, content):
                    stub_count += 1
                    break

print(f"  Stub/mock tool responses: {stub_count}")

# ── 6. Duplicate detection ──
print("\n== 6. DUPLICATES ==")
hashes = defaultdict(list)
for idx, row in enumerate(rows):
    # Hash the messages (excluding metadata)
    msg_str = json.dumps(row["messages"], sort_keys=True)
    h = hashlib.md5(msg_str.encode()).hexdigest()
    tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
    hashes[h].append(tid)

dupes = {h: tids for h, tids in hashes.items() if len(tids) > 1}
print(f"  Duplicate groups: {len(dupes)}")
for h, tids in list(dupes.items())[:5]:
    print(f"    {tids}")

# ── 7. Response length vs tool output analysis ──
print("\n== 7. RESPONSE QUALITY (length ratio) ==")
very_short = 0
short_examples = []
for idx, row in enumerate(rows):
    msgs = row["messages"]
    last = msgs[-1]
    if last["role"] != "assistant":
        continue
    content = last.get("content") or ""
    if not content.strip():
        continue
    
    # Get total tool output length
    tool_len = sum(len(m.get("content", "") or "") for m in msgs if m["role"] == "tool")
    resp_len = len(content.strip())
    
    # If tool gave substantial output but response is suspiciously short
    if tool_len > 200 and resp_len < 50:
        very_short += 1
        tid = row.get("test_id", row.get("metadata", {}).get("id", f"row_{idx}"))
        if len(short_examples) < 10:
            short_examples.append((tid, tool_len, resp_len, content.strip()[:80]))

print(f"  Suspiciously short responses (vs tool output): {very_short}")
for tid, tl, rl, txt in short_examples:
    print(f"    {tid}: tool={tl}chars, resp={rl}chars: {txt}")

# ── 8. Observer calling transfer_to_operator without it in tools ──
print("\n== 8. TRANSFER TOOL AVAILABILITY ==")
transfer_missing = 0
for idx, row in enumerate(rows):
    r = row.get("role", row.get("metadata", {}).get("role", ""))
    if r != "observer":
        continue
    tools = row.get("tools") or []
    declared_names = set()
    for t in tools:
        fn = t.get("function", {})
        declared_names.add(fn.get("name", ""))
    
    for m in row["messages"]:
        for tc in m.get("tool_calls", []):
            name = tc.get("function", {}).get("name", "")
            if name == "transfer_to_operator" and "transfer_to_operator" not in declared_names:
                transfer_missing += 1
                break

print(f"  transfer_to_operator called but not in tools: {transfer_missing}")

# ── 9. Ceiling samples sanity check ──
print("\n== 9. CEILING SAMPLE CHECK ==")
ceiling_count = 0
ceiling_wrong_sys = 0
for idx, row in enumerate(rows):
    msgs = row["messages"]
    if msgs[0]["role"] == "system" and "specialist planner" in (msgs[0].get("content") or ""):
        ceiling_count += 1
        # Ceiling samples should have JSON-only responses
        last = msgs[-1]
        if last["role"] == "assistant":
            content = last.get("content") or ""
            try:
                parsed = json.loads(content)
                if not isinstance(parsed, dict):
                    ceiling_wrong_sys += 1
            except json.JSONDecodeError:
                ceiling_wrong_sys += 1

print(f"  Ceiling samples: {ceiling_count}")
print(f"  Non-JSON ceiling responses: {ceiling_wrong_sys}")

# ── 10. Category distribution ──
print("\n== 10. CATEGORY DISTRIBUTION ==")
cats = Counter()
roles = Counter()
for row in rows:
    meta = row.get("metadata", {})
    cats[meta.get("category", row.get("category", "?"))] += 1
    roles[row.get("role", meta.get("role", "?"))] += 1

print(f"  Categories: {dict(cats.most_common())}")
print(f"  Roles: {dict(roles.most_common())}")

# ── Summary ──
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
total_issues = generic_count + hallucination_count + wrong_action + len(dupes)
print(f"  Total samples:           {len(rows)}")
print(f"  Generic responses:       {generic_count}")
print(f"  Hallucinated IDs:        {hallucination_count}")
print(f"  Skipped HITL:            {no_confirm}")
print(f"  Wrong tool actions:      {wrong_action}")
print(f"  Stub tool responses:     {stub_count}")
print(f"  Duplicates:              {len(dupes)}")
print(f"  Short vs tool output:    {very_short}")
print(f"  transfer_to_operator gap:{transfer_missing}")
print(f"  Bad ceiling responses:   {ceiling_wrong_sys}")

if generic_count > 0 or wrong_action > 0:
    print(f"\n  ⚠ WARNING: Found {generic_count + wrong_action} potential quality issues")
else:
    print(f"\n  ✓ No major inconsistencies found")

# Print all issues
if issues:
    print(f"\n{'='*60}")
    print(f"DETAILED ISSUES ({len(issues)}):")
    print(f"{'='*60}")
    for iss in issues:
        print(f"  {iss}")
