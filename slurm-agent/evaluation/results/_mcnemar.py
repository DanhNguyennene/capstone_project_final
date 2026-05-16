import json

ft = json.load(open('qwen14b_lora_final_test615_tmp.json', encoding='utf-8'))
base = json.load(open('base_qwen14b_test615.json', encoding='utf-8'))

print(f"FT: {ft['model']}, n={len(ft['results'])}")
print(f"Base: {base['model']}, n={len(base['results'])}")
print(f"FT metrics: BAR={ft['metrics']['BAR']}, SVR={ft['metrics']['SVR']}")
print(f"Base metrics: BAR={base['metrics']['BAR']}, SVR={base['metrics']['SVR']}")

ft_map = {r['test_id']: r for r in ft['results']}
base_map = {r['test_id']: r for r in base['results']}

common = sorted(set(ft_map.keys()) & set(base_map.keys()))
print(f"Common test_ids: {len(common)}")

# McNemar using 'passed' field directly
a = b = c = d = 0
for tid in common:
    fp = ft_map[tid]['passed']
    bp = base_map[tid]['passed']
    if fp and bp: a += 1
    elif fp and not bp: b += 1
    elif not fp and bp: c += 1
    else: d += 1

print(f"\n=== McNemar 2x2 table (using 'passed' field) ===")
print(f"a={a} (both pass), b={b} (FT pass/Base fail), c={c} (FT fail/Base pass), d={d} (both fail)")
print(f"FT pass rate: {(a+b)/len(common)*100:.1f}%")
print(f"Base pass rate: {(a+c)/len(common)*100:.1f}%")

if b + c > 0:
    chi2 = (b - c)**2 / (b + c)
    chi2_cc = (abs(b - c) - 1)**2 / (b + c)
    print(f"\nMcNemar chi2 (no correction) = {chi2:.2f}")
    print(f"McNemar chi2 (Yates correction) = {chi2_cc:.2f}")
    print(f"b+c = {b+c}")
    print(f"df=1, p < 0.05 if chi2 > 3.84")
    print(f"df=1, p < 0.01 if chi2 > 6.63")
    print(f"df=1, p < 0.005 if chi2 > 7.88")
    print(f"df=1, p < 0.001 if chi2 > 10.83")

# Also with overall >= 0.80 threshold
a2 = b2 = c2 = d2 = 0
for tid in common:
    fp = ft_map[tid]['overall'] >= 0.80
    bp = base_map[tid]['overall'] >= 0.80
    if fp and bp: a2 += 1
    elif fp and not bp: b2 += 1
    elif not fp and bp: c2 += 1
    else: d2 += 1

print(f"\n=== McNemar 2x2 table (overall >= 0.80) ===")
print(f"a={a2} (both pass), b={b2} (FT pass/Base fail), c={c2} (FT fail/Base pass), d={d2} (both fail)")
print(f"FT pass rate: {(a2+b2)/len(common)*100:.1f}%")
print(f"Base pass rate: {(a2+c2)/len(common)*100:.1f}%")

if b2 + c2 > 0:
    chi2_2 = (b2 - c2)**2 / (b2 + c2)
    chi2_cc2 = (abs(b2 - c2) - 1)**2 / (b2 + c2)
    print(f"\nMcNemar chi2 (no correction) = {chi2_2:.2f}")
    print(f"McNemar chi2 (Yates correction) = {chi2_cc2:.2f}")
    print(f"b+c = {b2+c2}")

# Also check monolithic
try:
    mono = json.load(open('base_qwen14b_monolithic_test615.json', encoding='utf-8'))
    mono_map = {r['test_id']: r for r in mono['results']}
    common_m = sorted(set(ft_map.keys()) & set(mono_map.keys()))
    print(f"\n=== McNemar: FT vs Monolithic (n={len(common_m)}) ===")
    am = bm = cm = dm = 0
    for tid in common_m:
        fp = ft_map[tid]['passed']
        mp = mono_map[tid]['passed']
        if fp and mp: am += 1
        elif fp and not mp: bm += 1
        elif not fp and mp: cm += 1
        else: dm += 1
    print(f"a={am}, b={bm} (FT pass/Mono fail), c={cm} (FT fail/Mono pass), d={dm}")
    if bm + cm > 0:
        chi2_m = (bm - cm)**2 / (bm + cm)
        chi2_m_cc = (abs(bm - cm) - 1)**2 / (bm + cm)
        print(f"McNemar chi2 = {chi2_m:.2f} (Yates: {chi2_m_cc:.2f})")
except Exception as e:
    print(f"Monolithic comparison skipped: {e}")
