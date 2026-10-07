"""Reproduction check: re-run the whole pipeline in a clean copy and compare it with the archived outputs.

    make check          full run, production sample sizes (about an hour on two CPU cores)
    make check-quick    reduced Monte Carlo sample sizes (about half an hour)

What it does
  1. Copies the code, configuration and input data (not outputs/, not paper/) into .check/run.
  2. Runs `make all` there, with the same Python interpreter that runs this script.
  3. Compares the new outputs with the archived ones (the outputs/ folder of the committed release; the working
     tree is used when this is not a git checkout) and prints a PASS/FAIL report, also written to .check/report.md.

Pass criteria
  - Deterministic products (geometry, screening, reachability, calendars and other tables, non-random values in the
    scenario cards): equal to within 1e-9 + 1e-6 x |value|, i.e. floating-point rounding.
  - Monte Carlo probabilities in the scenario cards: equal within sampling error, i.e. no value differs by more
    than 5 binomial standard errors and at most 1 % of values differ by more than 3.
  - Ephemeris validation report (comparison with JPL Horizons): identical text.
Figures, the seeded magnitude sample, the injection-recovery curves, the website data and (when a private paper/
folder is present) the manuscript's generated numbers are compared too and reported for information.

Monte Carlo results repeat bit for bit on the same computer. On a different computer the random draws can differ
(the correlated-weather draw factorises a covariance matrix with the local linear-algebra library), so they are
checked statistically.

Compare two existing trees instead of running:
    python3 scripts/check_reproduction.py --compare REFERENCE_DIR NEW_DIR [--nmc-new N]
Exit status: 0 = PASS, 1 = FAIL, 2 = the pipeline run failed.
"""
import argparse, glob, io, json, math, os, re, shutil, subprocess, sys, tarfile, time
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NMC_ARCHIVED, NTRIAL_ARCHIVED = 6000, 10          # sample sizes used for the archived outputs
RTOL, ATOL = 1e-6, 1e-9                           # deterministic tolerance
Z_MAX, Z3_FRACTION = 5.0, 0.01                    # Monte Carlo tolerance
COPY = ['ayap1obs', 'scripts', 'config', 'data', 'research', 'site', 'Makefile', 'requirements.txt']
DET_TABLES = ['outputs/tables/opportunity_statistics.csv', 'outputs/tables/opportunity_probability_vs_duration.csv',
              'outputs/tables/reachability_region_summary.csv', 'outputs/tables/observing_windows_calendar.csv',
              'outputs/tables/timeline_families.csv', 'outputs/tables/daily_availability.csv', 'outputs/tables/convergence.csv',
              'outputs/tables/refined_windows.csv', 'outputs/tables/facility_site_time_matrix.csv',
              'outputs/screening/pixel_summary.csv', 'outputs/reachability/catalogue_tol0.6_drift0.0.csv',
              'outputs/reachability/catalogue_tol2.5_drift0.0.csv']
MC_SUMMARIES_OUTSIDE_MC = {'public.peakV_median'}   # card values outside the 'mc' block that depend on the Monte Carlo sample
ARRAYS = ['outputs/screening/maps.npz', 'outputs/screening/observers.npz', 'outputs/screening/classes.npz',
          'outputs/reachability/reachability_maps.npz']


# ------------------------------------------------------------------------------------------------ helpers
def close(a, b):
    """Elementwise 'equal to rounding' for float arrays (NaN equals NaN, inf equals inf)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    with np.errstate(invalid='ignore'):
        return (a == b) | (np.abs(a - b) <= ATOL + RTOL * np.maximum(np.abs(a), np.abs(b))) | (np.isnan(a) & np.isnan(b))


def rel_diff(a, b):
    """Largest difference relative to the scale of the values (finite values only)."""
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    ok = np.isfinite(a) & np.isfinite(b)
    if not ok.any():
        return 0.0
    a, b = a[ok], b[ok]; scale = max(np.abs(a).max(), np.abs(b).max())
    return float(np.abs(a - b).max() / scale) if scale > 0 else 0.0


def flat(x, pre=''):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f'{pre}.{k}' if pre else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f'{pre}[{i}]')
    else:
        yield pre, x


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Report:
    def __init__(self):
        self.lines, self.fail = [], False

    def add(self, status, text):
        if status == 'FAIL':
            self.fail = True
        line = f'[{status}] {text}'
        self.lines.append(line); print(line, flush=True)

    def note(self, text):
        self.lines.append(f'       {text}'); print(f'       {text}', flush=True)


# ------------------------------------------------------------------------------------------------ comparison
def compare(ref, new, nmc_ref=NMC_ARCHIVED, nmc_new=NMC_ARCHIVED, rep=None):
    rep = rep or Report()
    p = lambda root, rel: os.path.join(root, rel)

    # 1. deterministic tables
    bad, n_ok, worst = [], 0, 0.0
    for f in DET_TABLES:
        if not os.path.exists(p(ref, f)):
            continue
        if not os.path.exists(p(new, f)):
            bad.append(f'{f}: missing in the new run'); continue
        a, b = pd.read_csv(p(ref, f)), pd.read_csv(p(new, f))
        if a.shape != b.shape or list(a.columns) != list(b.columns):
            bad.append(f'{f}: shape/columns {a.shape} vs {b.shape}'); continue
        problems = []
        for c in a.columns:
            if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
                ok = close(a[c], b[c])
                if not ok.all():
                    problems.append(f'{c}: {int((~ok).sum())} values')
                worst = max(worst, rel_diff(a[c], b[c]))
            else:
                n = int((a[c].astype(str) != b[c].astype(str)).sum())
                if n:
                    i = int(np.argmax((a[c].astype(str) != b[c].astype(str)).to_numpy()))
                    problems.append(f'{c}: {n} text cells, e.g. "{a[c].iloc[i]}" vs "{b[c].iloc[i]}"')
        if problems:
            bad.append(f'{f}: ' + '; '.join(problems[:3]))
        else:
            n_ok += 1
    rep.add('PASS' if not bad else 'FAIL', f'Deterministic tables: {n_ok} of {n_ok + len(bad)} equal to rounding (largest relative difference {worst:.1e})')
    for b in bad:
        rep.note(b)

    # 2. arrays
    bad, n_ok, n_arr, worst = [], 0, 0, 0.0
    for f in ARRAYS:
        if not (os.path.exists(p(ref, f)) and os.path.exists(p(new, f))):
            continue
        A, B = np.load(p(ref, f), allow_pickle=False), np.load(p(new, f), allow_pickle=False)
        for k in sorted(set(A.files) | set(B.files)):
            n_arr += 1
            if k not in A.files or k not in B.files:
                bad.append(f'{f}:{k} missing'); continue
            x, y = A[k], B[k]
            if x.shape != y.shape:
                bad.append(f'{f}:{k} shape {x.shape} vs {y.shape}'); continue
            if x.dtype.kind in 'fc':
                ok = close(x, y); worst = max(worst, rel_diff(x, y))
                if not ok.all():
                    bad.append(f'{f}:{k} {int((~ok).sum())} of {x.size} values differ'); continue
            elif x.size and np.mean(x != y) > 1e-5:   # integer/boolean classes: allow isolated threshold flips
                bad.append(f'{f}:{k} {int((x != y).sum())} of {x.size} values differ'); continue
            n_ok += 1
    rep.add('PASS' if not bad else 'FAIL', f'Arrays (screening, reachability): {n_ok} of {n_arr} equal to rounding (largest relative difference {worst:.1e})')
    for b in bad[:8]:
        rep.note(b)

    # 3. scenario cards: deterministic values and Monte Carlo probabilities
    det_bad, det_n, det_worst, txt_bad = [], 0, 0.0, []
    z, ad, n_mc, n_same, worst = [], [], 0, 0, []
    summ_n, summ_rel = 0, 0.0   # other Monte Carlo summaries (medians, means)
    cards = sorted(glob.glob(p(ref, 'outputs/scenarios/S*.json')), key=lambda s: int(re.findall(r'S(\d+)', s)[-1]))
    for fa in cards:
        name = os.path.basename(fa); fb = p(new, f'outputs/scenarios/{name}')
        if not os.path.exists(fb):
            det_bad.append(f'{name} missing in the new run'); continue
        A, B = dict(flat(json.load(open(fa)))), dict(flat(json.load(open(fb))))
        for k, a in A.items():
            if k not in B:
                det_bad.append(f'{name}:{k} missing'); continue
            b = B[k]
            if k.startswith('mc.') or k in MC_SUMMARIES_OUTSIDE_MC:
                leaf = k.split('.')[-1]
                prob = bool(re.match(r'p_', leaf)) or '.station_p_det.' in k or '.station_fov_cov.' in k
                if prob and is_num(a) and is_num(b) and 0 <= a <= 1 and 0 <= b <= 1:
                    q = 4 if '_by_eta_quartile' in k else 1   # quartile subsets hold a quarter of the draws
                    n_mc += 1; n_same += a == b; ad.append(abs(a - b))
                    pm = min(max((a + b) / 2, 1 / nmc_new), 1 - 1 / nmc_new)
                    se = math.sqrt(pm * (1 - pm) * (q / nmc_ref + q / nmc_new)); zz = abs(a - b) / se
                    z.append(zz); worst.append((zz, f'{name}:{k}', a, b))
                elif is_num(a) and is_num(b) and math.isfinite(a) and math.isfinite(b):
                    summ_n += 1; summ_rel = max(summ_rel, abs(a - b) / max(abs(a), abs(b), 1e-12))
                continue
            if is_num(a) and is_num(b):
                det_n += 1
                if not close(a, b):
                    det_bad.append(f'{name}:{k}: {a} vs {b}')
                det_worst = max(det_worst, rel_diff(a, b))
            elif a != b:
                txt_bad.append(f'{name}:{k}: "{str(a)[:40]}" vs "{str(b)[:40]}"')
    rep.add('PASS' if not det_bad and not txt_bad else 'FAIL',
            f'Scenario cards, deterministic values: {det_n - len(det_bad)} of {det_n} equal to rounding (largest relative difference {det_worst:.1e}); {len(txt_bad)} text differences')
    for b in (det_bad + txt_bad)[:8]:
        rep.note(b)
    if z:
        z = np.array(z); ad = np.array(ad); f3 = float(np.mean(z > 3))
        ok = z.max() <= Z_MAX and f3 <= Z3_FRACTION
        rep.add('PASS' if ok else 'FAIL',
                f'Monte Carlo probabilities (NMC {nmc_ref} vs {nmc_new}): {n_mc} values, {100 * n_same / n_mc:.0f} % identical; largest difference {ad.max():.3f}; '
                f'largest {z.max():.1f} standard errors (limit {Z_MAX:g}); {100 * f3:.2f} % beyond 3 (limit {100 * Z3_FRACTION:g} %)')
        if not ok:
            for zz, k, a, b in sorted(worst, reverse=True)[:5]:
                rep.note(f'{k}: {a:.4f} vs {b:.4f} ({zz:.1f} SE)')
    else:
        rep.add('FAIL', 'Monte Carlo probabilities: no scenario cards to compare')

    if summ_n:
        rep.add('info', f'Other Monte Carlo summaries in the scenario cards (medians, means, quantiles): {summ_n} values, largest relative difference {summ_rel:.3g}')

    # 4. ephemeris validation report
    va, vb = p(ref, 'outputs/validation/ephemeris_validation.md'), p(new, 'outputs/validation/ephemeris_validation.md')
    if os.path.exists(va) and os.path.exists(vb):
        same = open(va).read() == open(vb).read()
        rep.add('PASS' if same else 'FAIL', 'Ephemeris validation against JPL Horizons: report ' + ('identical' if same else 'differs'))
    else:
        rep.add('FAIL', 'Ephemeris validation report missing')

    # 5. information only
    rep.lines.append(''); print()
    for f, label in [('outputs/tables/peak_magnitude_distribution.json', 'Seeded flash-magnitude sample'),
                     ('outputs/tables/injection_recovery.json', 'Injection-recovery curves')]:
        if os.path.exists(p(ref, f)) and os.path.exists(p(new, f)):
            A, B = dict(flat(json.load(open(p(ref, f))))), dict(flat(json.load(open(p(new, f)))))
            d = [abs(A[k] - B[k]) for k in A if k in B and is_num(A[k]) and is_num(B[k])]
            rep.add('info', f'{label}: {sum(x == 0 for x in d)} of {len(d)} values identical, largest difference {max(d) if d else 0:.3g}')
    ma, mb = p(ref, 'paper/sections/numbers.tex'), p(new, 'paper/sections/numbers.tex')
    if os.path.exists(ma) and os.path.exists(mb):
        rx = re.compile(r'\\newcommand\{\\N([A-Za-z]+)\}\{(.*)\}\s*$')
        get = lambda fn: {m.group(1): m.group(2) for m in (rx.match(l.strip()) for l in open(fn)) if m}
        A, B = get(ma), get(mb); same = sum(A[k] == B.get(k) for k in A)
        num = lambda s: float(s) if re.fullmatch(r'-?\d+(\.\d+)?', s) else None
        d = [abs(num(A[k]) - num(B[k])) for k in A if k in B and A[k] != B[k] and num(A[k]) is not None and num(B.get(k, 'x')) is not None]
        rep.add('info', f'Numbers quoted in the manuscript: {same} of {len(A)} identical' + (f', largest numeric difference {max(d):.3g}' if d else ''))
    sa = sorted(glob.glob(p(ref, 'site/data/*.json')))
    n_same = n_cmp = 0; dmax = 0.0
    for fa in sa:
        fb = p(new, 'site/data/' + os.path.basename(fa))
        if os.path.basename(fa) in ('event.json', 'meta.json') or not os.path.exists(fb):
            continue
        n_cmp += 1; A, B = dict(flat(json.load(open(fa)))), dict(flat(json.load(open(fb))))
        if A == B:
            n_same += 1; continue
        dmax = max([dmax] + [abs(A[k] - B[k]) for k in A if k in B and is_num(A[k]) and is_num(B[k])])
    if n_cmp:
        rep.add('info', f'Website data files: {n_same} of {n_cmp} identical' + (f'; largest numeric difference {dmax:.3g} (Monte Carlo values)' if n_same < n_cmp else ''))
    try:
        from PIL import Image
        figs = sorted(glob.glob(p(new, 'outputs/figures/*.png'))); same = 0; diff = []
        for fb in figs:
            fa = p(ref, 'outputs/figures/' + os.path.basename(fb))
            if not os.path.exists(fa):
                continue
            x, y = np.asarray(Image.open(fa).convert('RGBA')), np.asarray(Image.open(fb).convert('RGBA'))
            if x.shape == y.shape and np.array_equal(x, y):
                same += 1
            else:
                diff.append(os.path.basename(fb))
        rep.add('info', f'Figures: {same} of {same + len(diff)} pixel-identical' + (f'; differing: {", ".join(diff[:6])}' + (' ...' if len(diff) > 6 else '') if diff else ''))
    except ImportError:
        pass
    rep.lines.append(''); print()
    rep.add('FAIL' if rep.fail else 'PASS', 'RESULT: ' + ('the run does NOT reproduce the archived outputs' if rep.fail else 'the run reproduces the archived outputs'))
    return rep


# ------------------------------------------------------------------------------------------------ run
def reference_tree(check_dir):
    """Archived outputs: the committed release when this is a git checkout, else the working tree."""
    try:
        sha = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
        tracked = subprocess.run(['git', '-C', ROOT, 'ls-files', 'outputs'], capture_output=True, text=True, check=True).stdout.strip()
        if tracked:
            ref = os.path.join(check_dir, 'ref'); shutil.rmtree(ref, ignore_errors=True); os.makedirs(ref)
            tar = subprocess.run(['git', '-C', ROOT, 'archive', '--format=tar', 'HEAD', 'outputs', 'site/data'], capture_output=True, check=True).stdout
            tarfile.open(fileobj=io.BytesIO(tar)).extractall(ref)
            if os.path.exists(os.path.join(ROOT, 'paper/sections/numbers.tex')):   # private manuscript, not in git
                shutil.copytree(os.path.join(ROOT, 'paper/sections'), os.path.join(ref, 'paper/sections'))
            return ref, f'committed release (git {sha})'
    except (OSError, subprocess.CalledProcessError):
        pass
    return ROOT, 'outputs in this folder (not a git checkout)'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--quick', action='store_true', help='reduced sample sizes (NMC 400, NTRIAL 2)')
    ap.add_argument('--nmc', type=int, default=None); ap.add_argument('--ntrial', type=int, default=None)
    ap.add_argument('--compare', nargs=2, metavar=('REFERENCE', 'NEW'), help='compare two existing trees, no run')
    ap.add_argument('--nmc-new', type=int, default=NMC_ARCHIVED, help='with --compare: Monte Carlo sample size of NEW')
    a = ap.parse_args()
    if a.compare:
        rep = compare(a.compare[0], a.compare[1], nmc_new=a.nmc_new)
        sys.exit(1 if rep.fail else 0)
    nmc = a.nmc or (400 if a.quick else NMC_ARCHIVED); ntrial = a.ntrial or (2 if a.quick else NTRIAL_ARCHIVED)
    check = os.path.join(ROOT, '.check'); run = os.path.join(check, 'run')
    shutil.rmtree(run, ignore_errors=True); os.makedirs(run)
    for item in COPY:
        src = os.path.join(ROOT, item)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(run, item), ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        elif os.path.exists(src):
            shutil.copy2(src, run)
    ref, ref_label = reference_tree(check)
    print(f'Reproduction check: re-running the pipeline in .check/run with NMC={nmc}, NTRIAL={ntrial}')
    print(f'Python {sys.version.split()[0]} ({sys.executable}); numpy {np.__version__}; reference: {ref_label}')
    print('Full log: .check/run.log', flush=True)
    t0 = time.time()
    with open(os.path.join(check, 'run.log'), 'w') as log:
        proc = subprocess.Popen(['make', 'all', f'NMC={nmc}', f'NTRIAL={ntrial}', f'PY={sys.executable}'], cwd=run,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            log.write(line)
            if line.startswith(sys.executable) or line.startswith('NMC=') or line.startswith('NTRIAL='):
                print(f'  {time.strftime("%H:%M:%S")}  {line.strip().replace(sys.executable, "python")}', flush=True)
        proc.wait()
    if proc.returncode != 0:
        print(f'\nThe pipeline stopped with an error after {(time.time() - t0) / 60:.0f} min; see .check/run.log')
        sys.exit(2)
    print(f'\nPipeline finished in {(time.time() - t0) / 60:.0f} min. Comparing with the archived outputs:\n', flush=True)
    rep = compare(ref, run, nmc_new=nmc)
    head = [f'# Reproduction check, {time.strftime("%Y-%m-%d %H:%M")}', '',
            f'- Python {sys.version.split()[0]}, numpy {np.__version__}, platform {sys.platform}',
            f'- NMC={nmc}, NTRIAL={ntrial}; reference: {ref_label}', '', '```']
    open(os.path.join(check, 'report.md'), 'w').write('\n'.join(head + rep.lines + ['```', '']))
    print('\nReport saved to .check/report.md')
    sys.exit(1 if rep.fail else 0)


if __name__ == '__main__':
    main()
