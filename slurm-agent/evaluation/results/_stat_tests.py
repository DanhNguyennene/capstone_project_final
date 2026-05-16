"""
Statistical significance tests for all model pairs.
Uses paired Wilcoxon signed-rank (non-parametric) + paired t-test on continuous overall scores.
Also includes effect size (Cohen's d) and McNemar on binary pass/fail.
"""
import json, math, itertools
from collections import defaultdict

# ---------- load all 4 models ----------
FILES = {
    "GPT-5-mini":  "gpt5mini_test615.json",
    "FT Qwen":     "qwen14b_lora_final_test615_tmp.json",
    "Base Qwen":   "base_qwen14b_test615.json",
    "Monolithic":  "base_qwen14b_monolithic_test615.json",
}

models = {}
for label, fname in FILES.items():
    data = json.load(open(fname, encoding="utf-8"))
    models[label] = {r["test_id"]: r["overall"] for r in data["results"]}
    print(f"{label}: n={len(models[label])}, mean={sum(models[label].values())/len(models[label])*100:.1f}%")

# common test ids across ALL 4
common = sorted(set.intersection(*(set(m.keys()) for m in models.values())))
print(f"\nCommon test IDs across all 4 models: {len(common)}")

# ---------- helper: stats without scipy ----------
def mean(xs):
    return sum(xs) / len(xs)

def stdev(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

def cohens_d(a, b):
    """Paired Cohen's d = mean(diff) / stdev(diff)"""
    diffs = [x - y for x, y in zip(a, b)]
    sd = stdev(diffs)
    return mean(diffs) / sd if sd > 0 else float("inf")

def paired_t(a, b):
    """Paired t-test statistic and approximate two-sided p-value."""
    diffs = [x - y for x, y in zip(a, b)]
    n = len(diffs)
    d_bar = mean(diffs)
    sd = stdev(diffs)
    if sd == 0:
        return float("inf"), 0.0
    t_stat = d_bar / (sd / math.sqrt(n))
    # approximate p from t using large-sample normal (n=615 >> 30)
    # For |t| > 5, p < 1e-6 essentially
    df = n - 1
    # Use normal approximation for p-value (valid for df > 100)
    import statistics
    z = abs(t_stat)
    # Approximate using complementary error function
    p = math.erfc(z / math.sqrt(2))  # two-sided
    return t_stat, p

def wilcoxon_signed_rank(a, b):
    """
    Manual Wilcoxon signed-rank test (two-sided).
    Returns (W_statistic, z_approx, p_approx).
    For n > 25, uses normal approximation.
    """
    diffs = [(x - y) for x, y in zip(a, b)]
    # Remove zeros
    nonzero = [(abs(d), 1 if d > 0 else -1) for d in diffs if d != 0]
    n = len(nonzero)
    if n == 0:
        return 0, 0.0, 1.0

    # Rank by absolute value
    nonzero.sort(key=lambda x: x[0])

    # Handle ties: assign average ranks
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and nonzero[j][0] == nonzero[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0  # 1-indexed average
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # W+ = sum of ranks for positive diffs
    w_plus = sum(r for r, (_, sign) in zip(ranks, nonzero) if sign > 0)
    w_minus = sum(r for r, (_, sign) in zip(ranks, nonzero) if sign < 0)
    W = min(w_plus, w_minus)

    # Normal approximation (valid for n > 25)
    mu = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    z = (W - mu) / sigma if sigma > 0 else 0
    p = math.erfc(abs(z) / math.sqrt(2))  # two-sided
    return W, z, p

def mcnemar(a_scores, b_scores, threshold=0.80):
    """McNemar's test. Returns (b, c, chi2, chi2_cc)."""
    bb = cc = 0
    for sa, sb in zip(a_scores, b_scores):
        ap = sa >= threshold
        bp = sb >= threshold
        if ap and not bp: bb += 1
        elif not ap and bp: cc += 1
    if bb + cc == 0:
        return bb, cc, 0, 0
    chi2 = (bb - cc) ** 2 / (bb + cc)
    chi2_cc = (abs(bb - cc) - 1) ** 2 / (bb + cc)
    return bb, cc, chi2, chi2_cc

# ---------- pairwise comparisons ----------
labels = list(FILES.keys())
print("\n" + "=" * 80)
print("PAIRWISE STATISTICAL TESTS (on continuous overall scores, n={})".format(len(common)))
print("=" * 80)

for a_label, b_label in itertools.combinations(labels, 2):
    a_scores = [models[a_label][tid] for tid in common]
    b_scores = [models[b_label][tid] for tid in common]

    diff = mean(a_scores) - mean(b_scores)
    d = cohens_d(a_scores, b_scores)
    t_stat, t_p = paired_t(a_scores, b_scores)
    W, z, w_p = wilcoxon_signed_rank(a_scores, b_scores)
    b_disc, c_disc, chi2, chi2_cc = mcnemar(a_scores, b_scores)

    print(f"\n--- {a_label} vs {b_label} ---")
    print(f"  Mean diff:     {diff*100:+.2f} pp  ({mean(a_scores)*100:.1f}% vs {mean(b_scores)*100:.1f}%)")
    print(f"  Cohen's d:     {d:.3f}  ({'large' if abs(d)>=0.8 else 'medium' if abs(d)>=0.5 else 'small' if abs(d)>=0.2 else 'negligible'})")
    print(f"  Paired t-test: t={t_stat:.2f}, p≈{t_p:.2e}  {'***' if t_p<0.001 else '**' if t_p<0.01 else '*' if t_p<0.05 else 'ns'}")
    print(f"  Wilcoxon:      W={W:.0f}, z={z:.2f}, p≈{w_p:.2e}  {'***' if w_p<0.001 else '**' if w_p<0.01 else '*' if w_p<0.05 else 'ns'}")
    print(f"  McNemar (≥.80): b={b_disc}, c={c_disc}, χ²={chi2:.1f} (Yates: {chi2_cc:.1f})  {'***' if chi2>10.83 else '**' if chi2>6.63 else '*' if chi2>3.84 else 'ns'}")

# ---------- summary table ----------
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(f"{'Comparison':<30} {'Δ (pp)':>8} {'Cohen d':>9} {'t':>8} {'p (t)':>10} {'p (W)':>10} {'McN χ²':>8} {'Sig':>5}")
print("-" * 95)
for a_label, b_label in itertools.combinations(labels, 2):
    a_scores = [models[a_label][tid] for tid in common]
    b_scores = [models[b_label][tid] for tid in common]
    diff = mean(a_scores) - mean(b_scores)
    d = cohens_d(a_scores, b_scores)
    t_stat, t_p = paired_t(a_scores, b_scores)
    W, z, w_p = wilcoxon_signed_rank(a_scores, b_scores)
    _, _, chi2, _ = mcnemar(a_scores, b_scores)
    sig = "***" if t_p < 0.001 else "**" if t_p < 0.01 else "*" if t_p < 0.05 else "ns"
    tag = f"{a_label} vs {b_label}"
    print(f"{tag:<30} {diff*100:>+7.2f} {d:>9.3f} {t_stat:>8.2f} {t_p:>10.2e} {w_p:>10.2e} {chi2:>8.1f} {sig:>5}")
