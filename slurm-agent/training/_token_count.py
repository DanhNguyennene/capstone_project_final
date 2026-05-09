"""Count tokens per sample using the actual Qwen2.5 tokenizer + chat template."""
import json, sys, statistics
from transformers import AutoTokenizer

path = sys.argv[1] if len(sys.argv) > 1 else "out/agent_sft_v3_base.jsonl"
rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

print("Loading Qwen2.5-14B-Instruct tokenizer...")
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct", trust_remote_code=True)

lengths = []
for i, row in enumerate(rows):
    text = tok.apply_chat_template(row["messages"], tools=row.get("tools"), tokenize=False, add_generation_prompt=False)
    n = len(tok.encode(text))
    lengths.append((n, row.get("test_id", f"row_{i}"), row.get("role", "?")))

lengths.sort(key=lambda x: x[0], reverse=True)

print(f"\nSamples: {len(lengths)}")
print(f"Min:     {lengths[-1][0]}")
print(f"Median:  {int(statistics.median(t[0] for t in lengths))}")
print(f"Mean:    {int(statistics.mean(t[0] for t in lengths))}")
print(f"P90:     {int(sorted(t[0] for t in lengths)[int(len(lengths)*0.90)])}")
print(f"P95:     {int(sorted(t[0] for t in lengths)[int(len(lengths)*0.95)])}")
print(f"P99:     {int(sorted(t[0] for t in lengths)[int(len(lengths)*0.99)])}")
print(f"Max:     {lengths[0][0]}")

print(f"\nTop 10 longest:")
for n, tid, role in lengths[:10]:
    print(f"  {n:6d} tokens  [{role}]  {tid}")

# Bucket distribution
buckets = [1024, 2048, 3072, 4096, 6144, 8192, 12288, 16384]
print(f"\nBucket distribution:")
for b in buckets:
    count = sum(1 for t in lengths if t[0] <= b)
    print(f"  <= {b:6d}: {count:5d} ({count*100//len(lengths)}%)")
