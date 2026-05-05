import json
from collections import Counter
from pathlib import Path

data_path = Path(r"C:\uni\capstone_project\slurm-agent\training\out\agent_sft.jsonl")
data = [json.loads(l) for l in data_path.open(encoding="utf-8")]

print(f"Total samples: {len(data)}")
print(f"Avg messages/sample: {sum(len(d['messages']) for d in data)/len(data):.1f}")
lens = [len(json.dumps(d)) for d in data]
print(f"Avg chars: {sum(lens)/len(lens):.0f}, Max: {max(lens)}, Min: {min(lens)}")

# Role distribution
roles = Counter()
tc_count = 0
for d in data:
    for m in d["messages"]:
        roles[m["role"]] += 1
        if m.get("tool_calls"):
            tc_count += 1
print(f"\nRole distribution: {dict(roles)}")
print(f"Messages with tool_calls: {tc_count}")

# Check first sample
print(f"\n--- First sample ---")
for m in data[0]["messages"]:
    content = (m.get("content") or "")[:80]
    tc = f" [tool_calls: {len(m['tool_calls'])}]" if m.get("tool_calls") else ""
    print(f"  {m['role']}: {content}{tc}")

# Check a few random samples for quality issues
import random
random.seed(42)
issues = []
for i, d in enumerate(data):
    msgs = d["messages"]
    # Issue: no system prompt
    if msgs[0]["role"] != "system":
        issues.append(f"Sample {i}: no system prompt")
    # Issue: empty assistant content with no tool_calls
    for j, m in enumerate(msgs):
        if m["role"] == "assistant" and not m.get("content") and not m.get("tool_calls"):
            issues.append(f"Sample {i}, msg {j}: empty assistant (no content, no tool_calls)")
    # Issue: very short conversations (only system + user + assistant)
    if len(msgs) < 4:
        issues.append(f"Sample {i}: too short ({len(msgs)} messages)")

print(f"\n--- Quality issues: {len(issues)} ---")
for issue in issues[:20]:
    print(f"  {issue}")

# Token length estimation
avg_tokens_est = sum(len(json.dumps(d).split()) for d in data) / len(data)
print(f"\nEstimated avg tokens/sample: ~{avg_tokens_est:.0f}")
print(f"Estimated total tokens: ~{avg_tokens_est * len(data):.0f}")
