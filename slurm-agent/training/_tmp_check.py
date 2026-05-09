import json, re

rows = [json.loads(l) for l in open("out/agent_sft_v3_base.jsonl", encoding="utf-8") if l.strip()]

# Check template pollution match
print("=== TEMPLATE POLLUTION MATCH ===")
pattern = r"(?:Job|Jobs) (?:has|have) been (?:successfully )?(?:cancelled|submitted|held|released|requeued)"
for idx, row in enumerate(rows):
    last = row["messages"][-1]
    if last["role"] == "assistant" and last.get("content"):
        if re.search(pattern, last["content"], re.IGNORECASE):
            tid = row.get("test_id", f"row_{idx}")
            print(f"  {tid} [{row['role']}]:")
            print(f"  {last['content'][:300]}")

# Check observer system prompt for RULES/safety
print()
print("=== SYSTEM PROMPT CHECK ===")
for row in rows:
    if row.get("role") == "observer":
        sys_content = row["messages"][0]["content"]
        for kw in ["RULE", "Rule", "rule", "guardrail", "dangerous", "destructive",
                    "safety", "Safety", "NEVER", "forbidden", "confirm"]:
            if kw in sys_content:
                idx = sys_content.index(kw)
                print(f'  Observer has "{kw}" at pos {idx}: ...{sys_content[max(0,idx-20):idx+40]}...')
        break

# Check operator system prompt for confirm
print()
for row in rows:
    if row.get("role") == "operator":
        sys_content = row["messages"][0]["content"]
        for kw in ["confirm", "Confirm", "approval", "Approval", "HITL", "human",
                    "approve", "Approve"]:
            if kw in sys_content:
                idx = sys_content.index(kw)
                print(f'  Operator has "{kw}" at pos {idx}: ...{sys_content[max(0,idx-20):idx+40]}...')
        break

# Response diversity excluding expected patterns
print()
print("=== DIVERSITY EXCLUDING HANDOFFS ===")
responses = []
for row in rows:
    last = row["messages"][-1]
    c = last.get("content", "") or ""
    if c.strip() and not c.startswith("Handing off to operator"):
        responses.append(c[:50])
unique = len(set(responses))
print(f"  Non-handoff responses: {len(responses)}")
print(f"  Unique openings: {unique} ({unique*100//max(1,len(responses))}%)")
