"""Reproduction check (release 2): re-run the whole pipeline in a clean copy and compare it with the archived outputs.

    make check          full run with the archived sample sizes (about two hours on two CPU cores)
    make check-quick    reduced Monte Carlo and injection sizes (about one hour)

What it does
  0. Verifies the input data against data/DATA_MANIFEST.sha256 (stops if a data file differs or is missing).
  1. Copies the code, configuration and input data (not outputs/, not paper/) into .check/run.
  2. Runs `make all` there with the same Python interpreter.
  3. Checks that every REQUIRED product exists in both trees (outputs/screening/classes.npz is deliberately not archived
     in git: it must exist in the new run but is compared only when the reference has it), then compares:
     - deterministic tables, arrays, validation results and the seeded magnitude sample: equal to within
       1e-9 + 1e-6 x |value| (floating-point rounding; boolean/integer arrays may differ in < 1e-5 of the entries);
     - scenario cards: non-Monte-Carlo values to rounding; outcome probabilities statistically, with a standard error
       that includes the spread over the epistemic outer draws (no value beyond 5 standard errors, at most 1 % beyond 3);
     - injection-recovery: m50 of each system within twice the combined bootstrap half-widths, false-alarm rates
       consistent within their Poisson intervals;
     - website data: every file present and the scenario probabilities equal to the new scenario cards.
  Figures are compared pixel by pixel for information only (fonts and libraries change pixels, not science).
Monte Carlo results repeat bit for bit on the same computer; on another computer the draws can differ slightly.

Compare two existing trees instead of running:
    python3 scripts/check_reproduction.py --compare REFERENCE_DIR NEW_DIR
Exit status: 0 = PASS, 1 = FAIL, 2 = the pipeline run failed or the input data differ.
"""
import argparse, glob, hashlib, io, json, math, os, re, shlex, shutil, subprocess, sys, tarfile, time
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RTOL, ATOL = 1e-6, 1e-9
Z_MAX, Z3_FRACTION = 5.0, 0.01
QUICK = dict(MC_OUTER=40, MC_INNER=50, NTRIAL=20, NSEQ=500)
COPY = ['ayap1obs', 'scripts', 'config', 'data', 'research', 'docs', 'site', 'Makefile', 'requirements.txt', 'CITATION.cff']
SCENARIOS = [f'S{i}' for i in range(1, 12)]
DET_TABLES = ['outputs/tables/opportunity_window_probability.csv', 'outputs/tables/opportunity_probability_vs_duration.csv', 'outputs/tables/opportunity_statistics.csv',
              'outputs/tables/opportunity_convergence.csv', 'outputs/tables/timeline_window_probability.csv', 'outputs/tables/reachability_region_summary.csv',
              'outputs/tables/reachability_convergence.csv', 'outputs/tables/observing_windows_calendar.csv', 'outputs/tables/timeline_families.csv',
              'outputs/tables/daily_availability.csv', 'outputs/tables/convergence.csv', 'outputs/tables/refined_windows.csv', 'outputs/tables/facility_site_time_matrix.csv',
              'outputs/screening/pixel_summary.csv', 'outputs/reachability/catalogue_main.csv', 'outputs/reachability/catalogue_incl88_j2.csv']
MC_TABLES = ['outputs/tables/scenario_summary.csv', 'outputs/tables/strategy_objectives.csv', 'outputs/tables/strategy_nondominance.csv']
ARRAYS = ['outputs/screening/maps.npz', 'outputs/screening/observers.npz', 'outputs/screening/classes.npz', 'outputs/reachability/opportunities_main.npz',
          'outputs/reachability/opportunities_incl88_j2.npz', 'outputs/reachability/reachability_maps_main.npz', 'outputs/reachability/reachability_maps_incl88_j2.npz',
          'outputs/scenarios/synthetic_horizons.npz']
UNARCHIVED = {'outputs/screening/classes.npz'}
DET_JSON = ['outputs/validation/ephemeris_validation.json', 'outputs/validation/terrain_validation.json', 'outputs/validation/iers_provenance.json',
            'outputs/tables/peak_magnitude_distribution.json', 'outputs/tables/ejecta_checks.json']
SITE = ['scenarios.json', 'sites.json', 'magnitudes.json', 'calendar.json', 'timeline.json', 'heat.json', 'world.json', 'cities.json']
FIGURES = ['fig_surface_screening', 'fig_reachability', 'fig_availability_timeseries', 'fig_flash_sensitivity', 'fig_lightcurves_limits', 'fig_public_thresholds',
           'fig_ejecta_crater', 'fig_plume_S2', 'fig_plume_and_earthview', 'fig_timeline_families', 'fig_orbiter_windows', 'fig_orbiter_latency', 'fig_pareto',
           'fig_injection_recovery', 'fig_sensitivity'] + [f'fig_scenario_{s}_coverage' for s in SCENARIOS]
REQUIRED = (DET_TABLES + MC_TABLES + ARRAYS + DET_JSON + ['outputs/tables/injection_recovery.json', 'outputs/validation/ephemeris_validation.md']
            + [f'outputs/scenarios/{s}.json' for s in SCENARIOS] + [f'site/data/{f}' for f in SITE] + [f'outputs/figures/{f}.png' for f in FIGURES])

def close(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    with np.errstate(invalid='ignore'):
        return (a == b) | (np.abs(a - b) <= ATOL + RTOL * np.maximum(np.abs(a), np.abs(b))) | (np.isnan(a) & np.isnan(b))

def rel_diff(a, b):
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel(); ok = np.isfinite(a) & np.isfinite(b)
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
        line = f'[{status}] {text}'; self.lines.append(line); print(line, flush=True)
    def note(self, text):
        self.lines.append(f'       {text}'); print(f'       {text}', flush=True)

def verify_data(root):
    man = os.path.join(root, 'data', 'DATA_MANIFEST.sha256')
    if not os.path.exists(man):
        return ['data/DATA_MANIFEST.sha256 missing']
    bad = []
    for line in open(man):
        h, p = line.strip().split('  ', 1)
        fp = os.path.join(root, p)
        if not os.path.exists(fp):
            bad.append(f'{p}: missing'); continue
        if hashlib.sha256(open(fp, 'rb').read()).hexdigest() != h:
            bad.append(f'{p}: checksum differs')
    return bad

def compare(ref, new, rep=None):
    rep = rep or Report(); p = lambda root, rel: os.path.join(root, rel)
    # 0. required products
    miss_new = [f for f in REQUIRED if not os.path.exists(p(new, f))]
    miss_ref = [f for f in REQUIRED if not os.path.exists(p(ref, f)) and f not in UNARCHIVED]
    rep.add('PASS' if not (miss_new or miss_ref) else 'FAIL', f'Required products: {len(REQUIRED) - len(miss_new)} of {len(REQUIRED)} present in the new run, '
            f'{len(REQUIRED) - len(miss_ref)} of {len(REQUIRED)} in the reference ({len(UNARCHIVED)} deliberately unarchived)')
    for f in miss_new[:6]:
        rep.note(f'missing in the new run: {f}')
    for f in miss_ref[:6]:
        rep.note(f'missing in the reference: {f}')
    # 1. deterministic tables
    bad, n_ok, worst = [], 0, 0.0
    for f in DET_TABLES:
        if not (os.path.exists(p(ref, f)) and os.path.exists(p(new, f))):
            continue
        a, b = pd.read_csv(p(ref, f)), pd.read_csv(p(new, f))
        if a.shape != b.shape or list(a.columns) != list(b.columns):
            bad.append(f'{f}: shape/columns {a.shape} vs {b.shape}'); continue
        probs = []
        for c in a.columns:
            if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
                ok = close(a[c], b[c]); worst = max(worst, rel_diff(a[c], b[c]))
                if not ok.all():
                    probs.append(f'{c}: {int((~ok).sum())} values')
            else:
                n = int((a[c].astype(str) != b[c].astype(str)).sum())
                if n:
                    probs.append(f'{c}: {n} text cells')
        if probs:
            bad.append(f'{f}: ' + '; '.join(probs[:3]))
        else:
            n_ok += 1
    rep.add('PASS' if not bad else 'FAIL', f'Deterministic tables: {n_ok} of {n_ok + len(bad)} equal to rounding (largest relative difference {worst:.1e})')
    for b_ in bad:
        rep.note(b_)
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
            elif x.dtype.kind in 'USO':
                if not np.array_equal(x, y):
                    bad.append(f'{f}:{k} text differs'); continue
            elif x.size and np.mean(np.unpackbits(np.bitwise_xor(x, y).astype(np.uint8)) if x.dtype == np.uint8 and k == 'occ' else (x != y)) > 1e-5:
                bad.append(f'{f}:{k} differs in more than 1e-5 of the entries'); continue
            n_ok += 1
    rep.add('PASS' if not bad else 'FAIL', f'Arrays (screening, reachability, terrain experiment): {n_ok} of {n_arr} equal to rounding (largest relative difference {worst:.1e})')
    for b_ in bad[:8]:
        rep.note(b_)
    # 3. deterministic JSON products
    bad, n_val = [], 0
    for f in DET_JSON:
        if not (os.path.exists(p(ref, f)) and os.path.exists(p(new, f))):
            continue
        A, B = dict(flat(json.load(open(p(ref, f))))), dict(flat(json.load(open(p(new, f)))))
        for k, a in A.items():
            b = B.get(k, '__missing__'); n_val += 1
            if b == '__missing__':
                bad.append(f'{f}:{k} missing')
            elif is_num(a) and is_num(b):
                if not close(a, b):
                    bad.append(f'{f}:{k}: {a} vs {b}')
            elif a != b and not k.endswith(('platform', 'machine')):
                bad.append(f'{f}:{k}: "{str(a)[:30]}" vs "{str(b)[:30]}"')
    rep.add('PASS' if not bad else 'FAIL', f'Validation results and seeded magnitude sample: {n_val - len(bad)} of {n_val} values equal to rounding')
    for b_ in bad[:6]:
        rep.note(b_)
    # 4. scenario cards
    det_bad, det_n, z, ad, n_mc, n_same, worst, summ_n, summ_rel = [], 0, [], [], 0, 0, [], 0, 0.0
    for s in SCENARIOS:
        fa, fb = p(ref, f'outputs/scenarios/{s}.json'), p(new, f'outputs/scenarios/{s}.json')
        if not (os.path.exists(fa) and os.path.exists(fb)):
            continue
        ca, cb = json.load(open(fa)), json.load(open(fb))
        Na = ca['mc_settings']['n_outer'] * ca['mc_settings']['n_inner']; Nb = cb['mc_settings']['n_outer'] * cb['mc_settings']['n_inner']
        A, B = dict(flat(ca)), dict(flat(cb))
        for k, a in A.items():
            if k not in B:
                det_bad.append(f'{s}:{k} missing'); continue
            b = B[k]
            mc_key = k.startswith(('mc.', 'mc_settings.', 'public.visual'))
            if mc_key:
                m = re.match(r'(mc\.[^.]+\.strategies\.[^.]+\.[a-z_]+)\.p$', k)
                if m and is_num(a) and is_num(b):
                    base = m.group(1)
                    def se(D, N, n_out):
                        pp = min(max(D[base + '.p'], 1 / N), 1 - 1 / N)
                        floor = math.sqrt(pp * (1 - pp) / N)                       # iid floor (also covers p = 0 or 1)
                        if is_num(D.get(base + '.mc_se')) and math.isfinite(D[base + '.mc_se']):
                            return max(D[base + '.mc_se'], floor)               # standard error of the mean of outer-draw means
                        sd_o = max(D[base + '.outer_p95'] - D[base + '.outer_p05'], 0) / 3.29
                        return math.sqrt(floor ** 2 + sd_o ** 2 / n_out)
                    s_ = math.hypot(se(A, Na, ca['mc_settings']['n_outer']), se(B, Nb, cb['mc_settings']['n_outer']))
                    zz = abs(a - b) / max(s_, 1e-12); n_mc += 1; n_same += a == b; ad.append(abs(a - b)); z.append(zz); worst.append((zz, f'{s}:{k}', a, b))
                elif is_num(a) and is_num(b) and math.isfinite(a) and math.isfinite(b):
                    summ_n += 1; summ_rel = max(summ_rel, abs(a - b) / max(abs(a), abs(b), 1e-12))
                continue
            if is_num(a) and is_num(b):
                det_n += 1
                if not close(a, b):
                    det_bad.append(f'{s}:{k}: {a} vs {b}')
            elif a != b:
                det_bad.append(f'{s}:{k}: "{str(a)[:40]}" vs "{str(b)[:40]}"')
    rep.add('PASS' if not det_bad else 'FAIL', f'Scenario cards, non-Monte-Carlo values: {det_n} numbers compared, {len(det_bad)} differences')
    for b_ in det_bad[:8]:
        rep.note(b_)
    if z:
        z = np.array(z); f3 = float(np.mean(z > 3)); ok = z.max() <= Z_MAX and f3 <= Z3_FRACTION
        rep.add('PASS' if ok else 'FAIL', f'Monte Carlo outcome probabilities: {n_mc} values, {100 * n_same / n_mc:.0f} % identical; largest difference {max(ad):.3f}; '
                f'largest {z.max():.1f} standard errors (limit {Z_MAX:g}); {100 * f3:.2f} % beyond 3 (limit {100 * Z3_FRACTION:g} %)')
        if not ok:
            for zz, k, a, b in sorted(worst, reverse=True)[:5]:
                rep.note(f'{k}: {a:.4f} vs {b:.4f} ({zz:.1f} SE)')
    else:
        rep.add('FAIL', 'Monte Carlo outcome probabilities: no scenario cards to compare')
    if summ_n:
        rep.add('info', f'Other Monte Carlo values in the cards (station rates, percentiles, paired differences): {summ_n} values, largest relative difference {summ_rel:.3g}')
    # 5. injection-recovery
    fa, fb = p(ref, 'outputs/tables/injection_recovery.json'), p(new, 'outputs/tables/injection_recovery.json')
    if os.path.exists(fa) and os.path.exists(fb):
        A, B = json.load(open(fa)), json.load(open(fb)); bad = []
        for k in A:
            if k.startswith('_'):
                continue
            if k not in B:
                bad.append(f'{k}: missing'); continue
            for fit in A[k]['fits']:
                fa_, fb_ = A[k]['fits'][fit], B[k]['fits'].get(fit)
                if fb_ is None:
                    bad.append(f'{k}/{fit}: missing'); continue
                hw = math.hypot((fa_['m50_ci95'][1] - fa_['m50_ci95'][0]) / 2, (fb_['m50_ci95'][1] - fb_['m50_ci95'][0]) / 2)
                if abs(fa_['m50'] - fb_['m50']) > 2 * hw + 1e-9:
                    bad.append(f"{k}/{fit}: m50 {fa_['m50']:.2f} vs {fb_['m50']:.2f} (tolerance {2 * hw:.2f})")
            for i, (ra, rb) in enumerate(zip(A[k]['false_alarms']['candidate_rate_per_frame'], B[k]['false_alarms']['candidate_rate_per_frame'])):
                if ra['ci95'][1] < rb['ci95'][0] or rb['ci95'][1] < ra['ci95'][0]:
                    bad.append(f"{k}: false-alarm rate {ra['rate']:.4f} vs {rb['rate']:.4f} (Poisson intervals disjoint)")
        rep.add('PASS' if not bad else 'FAIL', f'Injection-recovery: m50 and false-alarm rates of {len([k for k in A if not k.startswith("_")])} systems consistent within their uncertainties')
        for b_ in bad[:6]:
            rep.note(b_)
    # 6. website data
    bad = []
    sc = p(new, 'site/data/scenarios.json')
    if os.path.exists(sc):
        S = json.load(open(sc))
        for s in S['scenarios']:
            c = json.load(open(p(new, f"outputs/scenarios/{s['id']}.json")))
            for k, strat in (('A', 'A_turkiye_priority'), ('B', 'B_global_science'), ('C', 'C_public_participation')):
                for mk, mm in (('any', 'any'), ('two', 'two_indep'), ('live', 'live')):
                    v = round(c['mc']['wide|broad']['strategies'][strat][mm]['p'], 3)
                    if abs(s['p'][k]['wide'][mk] - v) > 1e-9:
                        bad.append(f"{s['id']} {k} {mk}: site {s['p'][k]['wide'][mk]} vs card {v}")
    rep.add('PASS' if (os.path.exists(sc) and not bad) else 'FAIL', 'Website data: scenario probabilities equal to the new scenario cards')
    for b_ in bad[:5]:
        rep.note(b_)
    # 7. information only: figures
    try:
        from PIL import Image
        same, diff = 0, []
        for f in FIGURES:
            fa, fb = p(ref, f'outputs/figures/{f}.png'), p(new, f'outputs/figures/{f}.png')
            if not (os.path.exists(fa) and os.path.exists(fb)):
                continue
            x, y = np.asarray(Image.open(fa).convert('RGBA')), np.asarray(Image.open(fb).convert('RGBA'))
            if x.shape == y.shape and np.array_equal(x, y):
                same += 1
            else:
                diff.append(f)
        rep.add('info', f'Figures (visual check only): {same} of {same + len(diff)} pixel-identical' + (f'; differing: {", ".join(diff[:6])}' if diff else ''))
    except ImportError:
        pass
    rep.lines.append(''); print()
    rep.add('FAIL' if rep.fail else 'PASS', 'RESULT: ' + ('the run does NOT reproduce the archived outputs' if rep.fail else 'the run reproduces the archived outputs'))
    return rep

def reference_tree(check_dir):
    """Archived outputs: the committed release when this is a git checkout, else the working tree."""
    try:
        sha = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
        tracked = subprocess.run(['git', '-C', ROOT, 'ls-files', 'outputs'], capture_output=True, text=True, check=True).stdout.strip()
        if tracked:
            ref = os.path.join(check_dir, 'ref'); shutil.rmtree(ref, ignore_errors=True); os.makedirs(ref)
            tar = subprocess.run(['git', '-C', ROOT, 'archive', '--format=tar', 'HEAD', 'outputs', 'site/data'], capture_output=True, check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
                try:
                    tf.extractall(ref, filter='data')
                except TypeError:
                    tf.extractall(ref)
            return ref, f'committed release (git {sha})'
    except (OSError, subprocess.CalledProcessError):
        pass
    return ROOT, 'outputs in this folder (not a git checkout)'

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--quick', action='store_true', help=f'reduced sizes {QUICK}')
    ap.add_argument('--compare', nargs=2, metavar=('REFERENCE', 'NEW'), help='compare two existing trees, no run')
    a = ap.parse_args()
    if a.compare:
        rep = compare(a.compare[0], a.compare[1]); sys.exit(1 if rep.fail else 0)
    bad = verify_data(ROOT)
    if bad:
        print('Input data do not match data/DATA_MANIFEST.sha256:'); [print('  ' + b) for b in bad[:10]]; sys.exit(2)
    sizes = QUICK if a.quick else {}
    check = os.path.join(ROOT, '.check'); run = os.path.join(check, 'run')
    shutil.rmtree(run, ignore_errors=True); os.makedirs(run)
    for item in COPY:
        src = os.path.join(ROOT, item)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(run, item), ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        elif os.path.exists(src):
            shutil.copy2(src, run)
    ref, ref_label = reference_tree(check)
    print(f'Reproduction check: re-running the pipeline in .check/run {sizes or "(archived sample sizes)"}')
    print(f'Python {sys.version.split()[0]} ({sys.executable}); numpy {np.__version__}; reference: {ref_label}')
    print('Full log: .check/run.log', flush=True)
    t0 = time.time()
    with open(os.path.join(check, 'run.log'), 'w') as log:
        py = shlex.quote(sys.executable)
        cmd = ['make', 'all', f'PY={py}'] + [f'{k}={v}' for k, v in sizes.items()]
        proc = subprocess.Popen(cmd, cwd=run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            log.write(line)
            if line.startswith((py, sys.executable, 'MC_OUTER=', 'NTRIAL=')):
                print(f'  {time.strftime("%H:%M:%S")}  {line.strip().replace(py, "python").replace(sys.executable, "python")}', flush=True)
        proc.wait()
    if proc.returncode != 0:
        print(f'\nThe pipeline stopped with an error after {(time.time() - t0) / 60:.0f} min; see .check/run.log'); sys.exit(2)
    print(f'\nPipeline finished in {(time.time() - t0) / 60:.0f} min. Comparing with the archived outputs:\n', flush=True)
    rep = compare(ref, run)
    head = [f'# Reproduction check, {time.strftime("%Y-%m-%d %H:%M")}', '', f'- Python {sys.version.split()[0]}, numpy {np.__version__}, platform {sys.platform}',
            f'- sizes: {sizes or "archived"}; reference: {ref_label}', '', '```']
    open(os.path.join(check, 'report.md'), 'w').write('\n'.join(head + rep.lines + ['```', '']))
    print('\nReport saved to .check/report.md'); sys.exit(1 if rep.fail else 0)

if __name__ == '__main__':
    main()
