"""Compare a clean-room pipeline run against the production outputs of the main tree.

Usage: python3 compare_clean_room.py MAIN_ROOT CLEAN_ROOT
Prints a markdown report on stdout.
Deterministic products (geometry, reachability, opportunity statistics, calendars, convergence, refinement,
validation) are expected to be identical; Monte Carlo products differ because the clean-room run uses reduced
sample sizes (NMC, NTRIAL), and are compared against their sampling error.
"""
import sys, os, re, glob, json
import numpy as np, pandas as pd

main, clean = sys.argv[1], sys.argv[2]
out = []
P = out.append

# ------------------------------------------------------------------ deterministic CSV tables
DET = ['opportunity_statistics.csv', 'opportunity_probability_vs_duration.csv', 'reachability_region_summary.csv',
       'observing_windows_calendar.csv', 'timeline_families.csv', 'daily_availability.csv', 'convergence.csv',
       'refined_windows.csv', 'facility_site_time_matrix.csv']
P('### Deterministic tables (expected identical)\n')
P('| file | rows (main / clean) | result |')
P('|---|---|---|')
n_ok = 0
for f in DET:
    a_p, b_p = os.path.join(main, 'outputs/tables', f), os.path.join(clean, 'outputs/tables', f)
    if not os.path.exists(b_p):
        P(f'| {f} | – | **missing in clean run** |'); continue
    a, b = pd.read_csv(a_p), pd.read_csv(b_p)
    res = ''
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        res = f'**shape/columns differ** {a.shape} vs {b.shape}'
    else:
        maxd = 0.0; neq = 0
        for c in a.columns:
            if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
                d = np.nanmax(np.abs(a[c].to_numpy(float) - b[c].to_numpy(float))) if len(a) else 0.0
                both_nan = (a[c].isna() == b[c].isna()).all()
                maxd = max(maxd, 0.0 if np.isnan(d) else d)
                if not both_nan: neq += 1
            else:
                neq += int((a[c].astype(str) != b[c].astype(str)).sum() > 0)
        res = 'identical' if (maxd < 1e-9 and neq == 0) else f'max numeric difference {maxd:.3g}; {neq} non-numeric/NaN-pattern column differences'
        n_ok += res == 'identical'
    P(f'| {f} | {len(a)} / {len(b)} | {res} |')
P(f'\n{n_ok} of {len(DET)} deterministic tables identical.\n')

# ------------------------------------------------------------------ screening and reachability arrays
P('### Screening and reachability arrays\n')
for rel in ['outputs/screening/classes.npz', 'outputs/screening/observers.npz', 'outputs/screening/maps.npz', 'outputs/reachability/reachability_maps.npz']:
    a_p, b_p = os.path.join(main, rel), os.path.join(clean, rel)
    if not (os.path.exists(a_p) and os.path.exists(b_p)):
        P(f'- `{rel}`: missing ({os.path.exists(a_p)}, {os.path.exists(b_p)})'); continue
    A, B = np.load(a_p, allow_pickle=True), np.load(b_p, allow_pickle=True)
    keys = sorted(set(A.files) | set(B.files)); bad = []
    for k in keys:
        if k not in A.files or k not in B.files: bad.append(f'{k} (missing)'); continue
        x, y = A[k], B[k]
        if x.shape != y.shape: bad.append(f'{k} shape {x.shape} vs {y.shape}'); continue
        if x.dtype.kind in 'fc':
            d = np.nanmax(np.abs(x.astype(float) - y.astype(float))) if x.size else 0.0
            if not (np.isnan(x) == np.isnan(y)).all() or d > 1e-9: bad.append(f'{k} max diff {d:.3g}')
        elif not np.array_equal(x, y): bad.append(f'{k} differs')
    P(f'- `{rel}`: {len(keys)} arrays, ' + ('all identical' if not bad else 'differences: ' + '; '.join(bad[:6])))
P('')

# ------------------------------------------------------------------ catalogues
for f in sorted(glob.glob(os.path.join(main, 'outputs/reachability/catalogue_*.csv'))):
    g = os.path.join(clean, 'outputs/reachability', os.path.basename(f))
    if os.path.exists(g):
        a, b = pd.read_csv(f), pd.read_csv(g)
        same = a.shape == b.shape and all(np.allclose(a[c], b[c], equal_nan=True) if pd.api.types.is_numeric_dtype(a[c]) else (a[c].astype(str) == b[c].astype(str)).all() for c in a.columns)
        P(f'- `{os.path.basename(f)}`: {len(a)} rows, ' + ('identical' if same else '**differs**'))
P('')

# ------------------------------------------------------------------ prior-predictive peak-magnitude distribution (seeded)
pa_, pb_ = [json.load(open(os.path.join(r, 'outputs/tables/peak_magnitude_distribution.json'))) for r in (main, clean)]
def flat(d, pre=''):
    for k, v in d.items():
        if isinstance(v, dict): yield from flat(v, pre + k + '.')
        else: yield pre + k, v
fa, fb = dict(flat(pa_)), dict(flat(pb_))
mx = max((abs(float(fa[k]) - float(fb[k])) for k in fa if k in fb and isinstance(fa[k], (int, float))), default=0.0)
P(f'- `peak_magnitude_distribution.json` (seeded prior-predictive sample): {len(fa)} values, max difference {mx:.3g}\n')

# ------------------------------------------------------------------ validation report
va, vb = [open(os.path.join(r, 'outputs/validation/ephemeris_validation.md')).read() for r in (main, clean)]
P('### Ephemeris validation report\n')
P('- `ephemeris_validation.md`: ' + ('identical' if va == vb else 'differs (see diff)') + '\n')

# ------------------------------------------------------------------ numbers.tex macros
def macros(fn):
    d = {}
    for line in open(fn):
        m = re.match(r'\\newcommand\{\\N([A-Za-z]+)\}\{(.*)\}\s*$', line.strip())
        if m: d[m.group(1)] = m.group(2)
    return d
ma, mb = macros(os.path.join(main, 'paper/sections/numbers.tex')), macros(os.path.join(clean, 'paper/sections/numbers.tex'))
same = [k for k in ma if k in mb and ma[k] == mb[k]]
diff = [k for k in ma if k in mb and ma[k] != mb[k]]
only = sorted(set(ma) ^ set(mb))
P('### Text macros (`paper/sections/numbers.tex`)\n')
P(f'- {len(ma)} macros in the production run, {len(mb)} in the clean run; {len(same)} identical, {len(diff)} different, {len(only)} present in only one run.')
num = lambda s: float(s) if re.fullmatch(r'-?\d+(\.\d+)?', s) else None
pd_ = [(k, num(ma[k]), num(mb[k])) for k in diff if num(ma[k]) is not None and num(mb[k]) is not None]
prob = [(k, a, b) for k, a, b in pd_ if 0 <= a <= 1 and 0 <= b <= 1 and ('.' in ma[k])]
if prob:
    dd = np.array([abs(a - b) for _, a, b in prob])
    P(f'- {len(prob)} differing probability-valued macros (Monte Carlo): median |difference| {np.median(dd):.3f}, 95th percentile {np.percentile(dd, 95):.3f}, maximum {dd.max():.3f} ({prob[int(dd.argmax())][0]}).')
    # expected binomial error of the difference between n=6000 and n=400 estimates at p
    z = np.array([abs(a - b) / max(np.sqrt(max(a * (1 - a), 1e-4) * (1 / 6000 + 1 / 400)), 1e-3) for _, a, b in prob])
    P(f'- Normalised by the binomial standard error of the difference (n = 6000 vs 400): median {np.median(z):.2f}, fraction above 3: {np.mean(z > 3):.3f}. (Draws are not independent across macros, and the prior over luminous efficiency is shared, so this is an indicative check.)')
other = [k for k in diff if (k, num(ma[k]), num(mb[k])) not in prob]
if other:
    P('- Other differing macros (first 40): ' + ', '.join(f'`{k}` {ma[k]} → {mb[k]}' for k in other[:40]))
if only:
    P('- Macros present in only one run: ' + ', '.join(only[:30]))
P('')
print('\n'.join(out))
