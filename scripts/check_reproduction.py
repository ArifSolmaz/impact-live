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

One check at a time: a second check started in the same folder is refused, because it would delete the working copy
(.check/run) of the first. Long steps print a "still running" line every 5 minutes; the reachability step alone takes
about half an hour.

Compare two existing trees instead of running:
    python3 scripts/check_reproduction.py --compare REFERENCE_DIR NEW_DIR
Exit status: 0 = PASS, 1 = FAIL, 2 = the pipeline run failed or the input data differ,
             3 = another check is already running in this folder.
"""
import argparse, glob, hashlib, io, json, math, os, re, shlex, shutil, subprocess, sys, tarfile, threading, time
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RTOL, ATOL = 1e-6, 1e-9
Z_MAX, Z3_FRACTION = 5.0, 0.01
Q_TOL = 0.08              # absolute tolerance for the deconvolved outer-draw quantiles (beta-binomial fit of 200 draws)
QUICK = dict(MC_OUTER=40, MC_INNER=50, NTRIAL=20, NSEQ=500)
COPY = ['ayap1obs', 'scripts', 'config', 'data', 'research', 'docs', 'site', 'Makefile', 'requirements.txt', 'CITATION.cff']
SCENARIOS = [f'S{i}' for i in range(1, 12)]
DET_TABLES = ['outputs/tables/opportunity_window_probability.csv', 'outputs/tables/opportunity_probability_vs_duration.csv', 'outputs/tables/opportunity_statistics.csv',
              'outputs/tables/opportunity_convergence.csv', 'outputs/tables/timeline_window_probability.csv', 'outputs/tables/reachability_region_summary.csv',
              'outputs/tables/reachability_convergence.csv', 'outputs/tables/observing_windows_calendar.csv', 'outputs/tables/timeline_families.csv',
              'outputs/tables/daily_availability.csv', 'outputs/tables/convergence.csv', 'outputs/tables/refined_windows.csv', 'outputs/tables/facility_site_time_matrix.csv',
              'outputs/screening/pixel_summary.csv', 'outputs/reachability/catalogue_main.csv', 'outputs/reachability/catalogue_incl88_j2.csv',
              'outputs/tables/plume_convergence.csv']
MC_TABLES = ['outputs/tables/scenario_summary.csv', 'outputs/tables/strategy_objectives.csv', 'outputs/tables/strategy_nondominance.csv']
ARRAYS = ['outputs/screening/maps.npz', 'outputs/screening/observers.npz', 'outputs/screening/classes.npz', 'outputs/reachability/opportunities_main.npz',
          'outputs/reachability/opportunities_incl88_j2.npz', 'outputs/reachability/reachability_maps_main.npz', 'outputs/reachability/reachability_maps_incl88_j2.npz',
          'outputs/scenarios/synthetic_horizons.npz']
UNARCHIVED = {'outputs/screening/classes.npz'}
DET_JSON = ['outputs/validation/ephemeris_validation.json', 'outputs/validation/terrain_validation.json', 'outputs/validation/iers_provenance.json',
            'outputs/tables/peak_magnitude_distribution.json', 'outputs/tables/ejecta_checks.json', 'outputs/tables/orbiter_seasons.json',
            'outputs/validation/lightcurve_accuracy.json', 'outputs/validation/transfer_check.json']
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

STRATS = ['A_turkiye_priority', 'B_global_science', 'C_public_participation']
OUTCOMES = ['any', 'two_indep', 'dual_validated', 'confirmed', 'obvious_any', 'live', 'rapid', 'turkish', 'obvious_turkish']
SITE_MAP = {'any': 'any', 'two': 'two_indep', 'dual': 'dual_validated', 'conf': 'confirmed', 'obvious': 'obvious_any', 'live': 'live', 'rapid': 'rapid', 'turkish': 'turkish'}

def _finite01(x):
    return is_num(x) and math.isfinite(x) and -1e-12 <= x <= 1 + 1e-12

def validate_products(root):
    """Schema, range and cross-product identities of one output tree (re-audit ST-23). Returns a list of problems;
    an empty list means every check passed. Checks: expected scenario ids; every strategy x outcome x prior block with
    0 <= p <= 1, p = k/N, interval = p +- 1.96 mc_se clipped to [0, 1], ordered outer quantiles, eta bins; paired
    differences equal to the difference of the two pooled probabilities and their intervals; the Monte Carlo CSV tables
    equal to the cards; nondominance recomputed from the cards; injection rows, fits and false-alarm products with
    consistent lengths, identities and ranges; website scenario records for exactly the expected ids and equal to the
    cards."""
    P = lambda rel: os.path.join(root, rel); bad = []
    cards = {}
    for sid in SCENARIOS:
        f = P(f'outputs/scenarios/{sid}.json')
        try:
            c = json.load(open(f))
        except Exception as e:
            bad.append(f'{sid}: card unreadable ({type(e).__name__})'); continue
        cards[sid] = c
        if c.get('id') != sid:
            bad.append(f'{sid}: id {c.get("id")!r}')
        ms = c.get('mc_settings', {}); N = ms.get('n_outer', 0) * ms.get('n_inner', 0)
        if not (isinstance(ms.get('n_outer'), int) and isinstance(ms.get('n_inner'), int) and N > 0):
            bad.append(f'{sid}: mc_settings invalid'); continue
        if 'wide|broad' not in c.get('mc', {}) or 'v-scaled|broad' not in c['mc']:
            bad.append(f'{sid}: missing prior blocks'); continue
        for pk, m in c['mc'].items():
            nb = len(m.get('eta_bins', [])) - 1
            for st in STRATS:
                S_ = m.get('strategies', {}).get(st)
                if S_ is None:
                    bad.append(f'{sid}/{pk}: strategy {st} missing'); continue
                for o in OUTCOMES:
                    r = S_.get(o)
                    if not isinstance(r, dict):
                        bad.append(f'{sid}/{pk}/{st}: outcome {o} missing'); continue
                    p_, k_, se = r.get('p'), r.get('k'), r.get('mc_se')
                    if not (_finite01(p_) and isinstance(k_, int) and 0 <= k_ <= N and abs(p_ - k_ / N) < 1e-12):
                        bad.append(f'{sid}/{pk}/{st}/{o}: p/k inconsistent'); continue
                    if not (is_num(se) and math.isfinite(se) and se >= 0):
                        bad.append(f'{sid}/{pk}/{st}/{o}: mc_se invalid'); continue
                    ci = r.get('ci95', [None, None])
                    if not (is_num(ci[0]) and is_num(ci[1]) and abs(ci[0] - max(0.0, p_ - 1.96 * se)) < 1e-9 and abs(ci[1] - min(1.0, p_ + 1.96 * se)) < 1e-9):
                        bad.append(f'{sid}/{pk}/{st}/{o}: ci95 is not p +- 1.96 mc_se')
                    q = [r.get('outer_p05'), r.get('outer_p50'), r.get('outer_p95')]
                    if not (all(_finite01(x) for x in q) and q[0] <= q[1] + 1e-12 <= q[2] + 2e-12):
                        bad.append(f'{sid}/{pk}/{st}/{o}: outer quantiles invalid')
                    if 'outer_raw_p05' in r and not (_finite01(r['outer_raw_p05']) and _finite01(r['outer_raw_p95']) and r['outer_raw_p05'] <= r['outer_raw_p95'] + 1e-12):
                        bad.append(f'{sid}/{pk}/{st}/{o}: raw outer quantiles invalid')
                    be = r.get('by_eta', [])
                    if len(be) != nb or not all(v is None or _finite01(v) for v in be):
                        bad.append(f'{sid}/{pk}/{st}/{o}: by_eta invalid')
            for key, d in m.get('paired', {}).items():
                try:
                    o, ab = key.split(':'); b_, a_ = ab.split('-')
                    want = m['strategies'][b_][o]['p'] - m['strategies'][a_][o]['p']
                except Exception:
                    bad.append(f'{sid}/{pk}: paired key {key} invalid'); continue
                if not (is_num(d.get('diff')) and abs(d['diff'] - want) < 1e-9 and is_num(d.get('mc_se')) and d['mc_se'] >= 0
                        and abs(d['ci95'][0] - (d['diff'] - 1.96 * d['mc_se'])) < 1e-9 and abs(d['ci95'][1] - (d['diff'] + 1.96 * d['mc_se'])) < 1e-9):
                    bad.append(f'{sid}/{pk}: paired {key} inconsistent with the pooled probabilities')
    # Monte Carlo CSV tables against the cards
    try:
        so = pd.read_csv(P('outputs/tables/strategy_objectives.csv'))
        need = {'scenario', 'strategy', 'prior', 'weight_recruited'} | {f'p_{o}' for o in ('any', 'two_indep', 'live', 'turkish')}
        if not need <= set(so.columns):
            bad.append('strategy_objectives.csv: columns missing')
        else:
            exp = {(sid, st, pk) for sid, c in cards.items() for pk in c['mc'] for st in STRATS}
            got = set(zip(so.scenario, so.strategy, so.prior))
            if exp != got:
                bad.append(f'strategy_objectives.csv: {len(exp ^ got)} scenario/strategy/prior rows differ from the cards')
            for _, r in so.iterrows():
                c = cards.get(r.scenario)
                if c is None or r.prior not in c['mc']:
                    continue
                for o in ('any', 'two_indep', 'dual_validated', 'confirmed', 'live', 'turkish'):
                    cr = c['mc'][r.prior]['strategies'][r.strategy][o]
                    for col, key in ((f'p_{o}', 'p'), (f'p_{o}_lo', None), (f'p_{o}_outer05', 'outer_p05'), (f'p_{o}_outer95', 'outer_p95')):
                        if col not in so.columns:
                            continue
                        want = cr['ci95'][0] if key is None else cr[key]
                        if not (is_num(r[col]) and abs(float(r[col]) - want) < 1e-9):
                            bad.append(f'strategy_objectives.csv {r.scenario}/{r.strategy}/{r.prior}: {col} differs from the card'); break
    except Exception as e:
        bad.append(f'strategy_objectives.csv unreadable ({type(e).__name__})'); so = None
    try:
        nd = pd.read_csv(P('outputs/tables/strategy_nondominance.csv'))
        if so is not None and {'scenario', 'strategy', 'nondominated'} <= set(nd.columns):
            w = so[so.prior == 'wide|broad'].set_index(['scenario', 'strategy'])['weight_recruited']
            for sid, c in cards.items():
                m = c['mc']['wide|broad']['strategies']
                for a in STRATS:
                    dom = any(w[(sid, b)] <= w[(sid, a)] and all(m[b][o]['p'] - m[a][o]['p'] >= -1e-12 for o in ('two_indep', 'live', 'turkish'))
                              and (any(m[b][o]['p'] - m[a][o]['p'] > 1e-12 for o in ('two_indep', 'live', 'turkish')) or w[(sid, b)] < w[(sid, a)])
                              for b in STRATS if b != a)
                    row = nd[(nd.scenario == sid) & (nd.strategy == a)]
                    if len(row) != 1 or bool(row.nondominated.iloc[0]) == dom:
                        bad.append(f'strategy_nondominance.csv {sid}/{a}: differs from the descriptive Pareto front of the cards')
        else:
            bad.append('strategy_nondominance.csv: columns missing')
    except Exception as e:
        bad.append(f'strategy_nondominance.csv unreadable ({type(e).__name__})')
    try:
        sm = pd.read_csv(P('outputs/tables/scenario_summary.csv'))
        if set(sm['id']) != set(SCENARIOS):
            bad.append('scenario_summary.csv: scenario ids differ')
        for _, r in sm.iterrows():
            c = cards.get(r['id'])
            if c is not None and 'pA_any' in sm.columns and abs(float(r['pA_any']) - round(c['mc']['wide|broad']['strategies']['A_turkiye_priority']['any']['p'], 3)) > 1e-9:
                bad.append(f'scenario_summary.csv {r["id"]}: pA_any differs from the card')
    except Exception as e:
        bad.append(f'scenario_summary.csv unreadable ({type(e).__name__})')
    # injection-recovery
    try:
        inj = json.load(open(P('outputs/tables/injection_recovery.json')))
        systems = [k for k in inj if not k.startswith('_')]
        if set(systems) != {'nel', 'tug', 'ama', 'afo', 'std'}:
            bad.append(f'injection_recovery.json: systems {sorted(systems)}')
        for k in systems:
            r = inj[k]; ncam = len(r.get('bands', []))
            rows = r.get('rows', [])
            if not rows or any(x['n'] != r['ntrial'] for x in rows) or np.any(np.diff([x['mag'] for x in rows]) <= 0):
                bad.append(f'{k}: injection rows invalid'); continue
            for x in rows:
                for cam in ['cam0'] + (['cam1', 'dual'] if ncam == 2 else []):
                    kk, fr, wi = x.get(f'k_{cam}'), x.get(f'frac_{cam}'), x.get(f'wilson_{cam}')
                    if not (isinstance(kk, int) and 0 <= kk <= x['n'] and abs(fr - kk / x['n']) < 1e-12 and wi[0] - 1e-12 <= fr <= wi[1] + 1e-12):
                        bad.append(f'{k} mag {x["mag"]}: {cam} recovery fraction inconsistent'); break
            for fit, f_ in r.get('fits', {}).items():
                ok = all(is_num(f_.get(q)) and math.isfinite(f_[q]) for q in ('m50', 'width', 'm90')) and f_['width'] > 0
                ok = ok and abs(f_['m90'] - (f_['m50'] - f_['width'] * math.log(9))) < 1e-9
                ok = ok and f_['m50_ci95'][0] <= f_['m50_ci95'][1] and f_['m90_ci95'][0] <= f_['m90_ci95'][1]
                if not ok:
                    bad.append(f'{k}/{fit}: fit invalid (m90 = m50 - w ln 9 and ordered intervals required)')
            fa = r.get('false_alarms', {})
            cr_ = fa.get('candidate_rate_per_box_frame', [])
            if len(cr_) != ncam or len(fa.get('box_frames_with_candidate', [])) != ncam or len(fa.get('per_clip', [])) != fa.get('n_clips', -1):
                bad.append(f'{k}: false-alarm products have the wrong length'); continue
            for j, c_ in enumerate(cr_):
                tot = sum(pc['candidates'][j] for pc in fa['per_clip']); bf = sum(pc['box_frames'] for pc in fa['per_clip'])
                if not (c_['total'] == tot and c_['box_frames'] == bf and abs(c_['rate'] - tot / max(bf, 1)) < 1e-12 and c_['ci95_clip_bootstrap'][0] <= c_['ci95_clip_bootstrap'][1]):
                    bad.append(f'{k}: candidate rate of camera {j} inconsistent with the per-clip counts')
            if ncam == 2:
                d_ = fa.get('dual_coincidence_rate_per_box_frame', {})
                tot = sum(pc['dual_coincident_box_frames'] for pc in fa['per_clip'])
                if not (isinstance(d_, dict) and d_.get('total') == tot and _finite01(d_.get('rate')) and abs(d_['rate'] - tot / max(d_['box_frames'], 1)) < 1e-12):
                    bad.append(f'{k}: dual coincidence rate inconsistent with the per-clip counts')
    except Exception as e:
        bad.append(f'injection_recovery.json unreadable or malformed ({type(e).__name__}: {str(e)[:60]})')
    # website scenario records
    try:
        S = json.load(open(P('site/data/scenarios.json')))
        ids = [x.get('id') for x in S.get('scenarios', [])]
        if sorted(ids, key=lambda z: int(z[1:])) != SCENARIOS:
            bad.append(f'site/data/scenarios.json: scenario ids {ids} (expected S1-S11)')
        for x in S.get('scenarios', []):
            c = cards.get(x.get('id'))
            if c is None:
                continue
            same_epoch = x['epoch_utc'].replace('T', ' ')[:16] == c['epoch_utc'].replace('T', ' ')[:16]   # site: ISO 8601 with 'T'
            if abs(x['lat'] - c['lat']) > 1e-9 or abs(x['lon'] - c['lon']) > 1e-9 or not same_epoch:
                bad.append(f"site {x['id']}: position or epoch differs from the card")
            for k_, st in (('A', 'A_turkiye_priority'), ('B', 'B_global_science'), ('C', 'C_public_participation')):
                for pk, pr in (('wide', 'wide|broad'), ('vs', 'v-scaled|broad')):
                    rec = x['p'][k_][pk]
                    for sk, mk in SITE_MAP.items():
                        cr = c['mc'][pr]['strategies'][st][mk]
                        if abs(rec[sk] - round(cr['p'], 3)) > 1e-9 or abs(rec['range'][sk][0] - round(cr['outer_p05'], 3)) > 1e-9 or abs(rec['range'][sk][1] - round(cr['outer_p95'], 3)) > 1e-9:
                            bad.append(f"site {x['id']} {k_}/{pk}/{sk}: differs from the card"); break
    except Exception as e:
        bad.append(f'site/data/scenarios.json unreadable or malformed ({type(e).__name__})')
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
    # 0b. schema, ranges and cross-product identities of each tree (re-audit ST-23)
    for label, root_ in (('new run', new), ('reference', ref)):
        vb = validate_products(root_)
        rep.add('PASS' if not vb else 'FAIL', f'Product validation ({label}): ids, ranges, p = k/N, intervals, quantiles, paired differences, CSV = cards, '
                f'nondominance, injection identities, website records: {len(vb)} problems')
        for b_ in vb[:8]:
            rep.note(b_)
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
    q_bad, q_n, p_bad, p_n = [], 0, [], 0
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
                elif re.search(r'\.outer_p(05|50|95)$', k) and is_num(a) and is_num(b):
                    q_n += 1
                    if abs(a - b) > Q_TOL:
                        q_bad.append(f'{s}:{k}: {a:.3f} vs {b:.3f}')
                elif re.search(r'\.paired\.[^.]+\.diff$', k) and is_num(a) and is_num(b):
                    sa = A.get(k[:-4] + 'mc_se'); sb = B.get(k[:-4] + 'mc_se')
                    zz = abs(a - b) / max(math.hypot(sa or 0, sb or 0), 1e-6); p_n += 1
                    if zz > Z_MAX:
                        p_bad.append(f'{s}:{k}: {a:.4f} vs {b:.4f} ({zz:.1f} SE)')
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
    rep.add('PASS' if not q_bad else 'FAIL', f'Monte Carlo outer-draw quantiles: {q_n} values within {Q_TOL:g} of the reference')
    for b_ in q_bad[:5]:
        rep.note(b_)
    rep.add('PASS' if not p_bad else 'FAIL', f'Paired strategy differences: {p_n} values within {Z_MAX:g} combined standard errors')
    for b_ in p_bad[:5]:
        rep.note(b_)
    if summ_n:
        rep.add('info', f'Other Monte Carlo values in the cards (station rates, plume and visual sensitivities): {summ_n} values, largest relative difference {summ_rel:.3g}')
    # 5. injection-recovery: every fit (m50, m90, width), every recovery row and the false-alarm products
    fa, fb = p(ref, 'outputs/tables/injection_recovery.json'), p(new, 'outputs/tables/injection_recovery.json')
    if os.path.exists(fa) and os.path.exists(fb):
        bad = []
        try:
            A, B = json.load(open(fa)), json.load(open(fb))
            systems = [k for k in A if not k.startswith('_')]
            for k in systems:
                if k not in B:
                    bad.append(f'{k}: missing'); continue
                if set(A[k]['fits']) != set(B[k]['fits']):
                    bad.append(f'{k}: fit sets differ')
                for fit, fa_ in A[k]['fits'].items():
                    fb_ = B[k]['fits'].get(fit)
                    if fb_ is None:
                        continue
                    for q in ('m50', 'm90'):
                        hw = math.hypot((fa_[q + '_ci95'][1] - fa_[q + '_ci95'][0]) / 2, (fb_[q + '_ci95'][1] - fb_[q + '_ci95'][0]) / 2)
                        if abs(fa_[q] - fb_[q]) > 2 * hw + 1e-9:
                            bad.append(f"{k}/{fit}: {q} {fa_[q]:.2f} vs {fb_[q]:.2f} (tolerance {2 * hw:.2f})")
                    if 'width_ci95' in fa_ and 'width_ci95' in fb_:
                        hw = math.hypot((fa_['width_ci95'][1] - fa_['width_ci95'][0]) / 2, (fb_['width_ci95'][1] - fb_['width_ci95'][0]) / 2)
                        if abs(fa_['width'] - fb_['width']) > 2 * hw + 1e-9:
                            bad.append(f"{k}/{fit}: width {fa_['width']:.3f} vs {fb_['width']:.3f}")
                ra, rb = A[k]['rows'], B[k]['rows']
                if len(ra) != len(rb):
                    bad.append(f'{k}: {len(ra)} vs {len(rb)} recovery rows')
                else:
                    for x, y in zip(ra, rb):
                        for cam in [c for c in ('cam0', 'cam1', 'dual') if f'frac_{c}' in x]:
                            pp = 0.5 * (x[f'frac_{cam}'] + y.get(f'frac_{cam}', -9)); sd = math.sqrt(max(pp * (1 - pp), 0.25 / x['n']) * (1 / x['n'] + 1 / y['n']))
                            if abs(x[f'frac_{cam}'] - y.get(f'frac_{cam}', -9)) > 5 * sd + 1e-9:
                                bad.append(f"{k} mag {x['mag']}: {cam} recovery {x[f'frac_{cam}']:.2f} vs {y.get(f'frac_{cam}')}")
                cA, cB = A[k]['false_alarms']['candidate_rate_per_box_frame'], B[k]['false_alarms']['candidate_rate_per_box_frame']
                if len(cA) != len(cB):
                    bad.append(f'{k}: false-alarm products have different lengths')
                for xa, xb in zip(cA, cB):
                    ia, ib = xa['ci95_clip_bootstrap'], xb['ci95_clip_bootstrap']
                    if ia[1] < ib[0] or ib[1] < ia[0]:
                        bad.append(f"{k}: candidate rate {xa['rate']:.4f} vs {xb['rate']:.4f} (intervals disjoint)")
                da, db = A[k]['false_alarms'].get('dual_coincidence_rate_per_box_frame'), B[k]['false_alarms'].get('dual_coincidence_rate_per_box_frame')
                if (da is None) != (db is None):
                    bad.append(f'{k}: dual coincidence product present in only one tree')
                elif da is not None and (da['ci95_clip_bootstrap'][1] < db['ci95_clip_bootstrap'][0] or db['ci95_clip_bootstrap'][1] < da['ci95_clip_bootstrap'][0]):
                    bad.append(f"{k}: dual coincidence rate {da['rate']:.4f} vs {db['rate']:.4f}")
        except Exception as e:
            bad.append(f'injection_recovery.json malformed ({type(e).__name__}: {str(e)[:60]})'); systems = []
        rep.add('PASS' if not bad else 'FAIL', f'Injection-recovery: fits, recovery rows and false-alarm products of {len(systems)} systems consistent within their uncertainties')
        for b_ in bad[:6]:
            rep.note(b_)
    # 6. website data: deterministic files equal to rounding; scenario records checked against the cards per tree (0b)
    bad, n_val = [], 0
    for f in ('sites.json', 'calendar.json', 'timeline.json', 'heat.json', 'world.json', 'cities.json'):
        fa_, fb_ = p(ref, f'site/data/{f}'), p(new, f'site/data/{f}')
        if not (os.path.exists(fa_) and os.path.exists(fb_)):
            continue
        try:
            A, B = dict(flat(json.load(open(fa_)))), dict(flat(json.load(open(fb_))))
        except Exception as e:
            bad.append(f'{f}: unreadable ({type(e).__name__})'); continue
        if set(A) != set(B):
            bad.append(f'{f}: {len(set(A) ^ set(B))} fields present in only one tree')
        for k, a in A.items():
            if k not in B:
                continue
            b = B[k]; n_val += 1
            if is_num(a) and is_num(b):
                if not close(a, b) and abs(a - b) > 0.0051:                  # values rounded for display may differ by one unit
                    bad.append(f'{f}:{k}: {a} vs {b}')
            elif a != b and not k.endswith(('generated_utc', 'updated_utc')):
                bad.append(f'{f}:{k}: "{str(a)[:30]}" vs "{str(b)[:30]}"')
    rep.add('PASS' if not bad else 'FAIL', f'Website data (deterministic files): {n_val - len(bad)} of {n_val} values equal to display rounding')
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

def lock_check_folder(check):
    """Hold an exclusive lock on .check/lock for the life of this process (released automatically when it exits,
    also after a crash). A second check in the same folder would delete the first one's working copy mid-run."""
    os.makedirs(check, exist_ok=True)
    f = open(os.path.join(check, 'lock'), 'a+')
    try:
        import fcntl
    except ImportError:                      # no advisory locks on this platform: run one check at a time
        return f
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.seek(0)
        who = f.read().strip() or 'another process'
        print(f'Another reproduction check is already running in this folder ({who}).\n'
              'Wait for it to print PASS or FAIL, or stop it first: two checks in one folder delete each other\'s files.')
        sys.exit(3)
    f.seek(0); f.truncate()
    f.write(f'PID {os.getpid()}, started {time.strftime("%Y-%m-%d %H:%M:%S")}\n'); f.flush()
    return f

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
    lock = lock_check_folder(check)  # noqa: F841  (kept open until the process exits)
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
    print('Full log: .check/run.log. Long steps print a "still running" line every 5 minutes.', flush=True)
    t0 = time.time()
    step = dict(name='make all', t=t0)
    finished = threading.Event()
    every = float(os.environ.get('CHECK_HEARTBEAT_S', 300))

    def heartbeat():                 # a line after every 5 quiet minutes of the current step
        last = t0
        while not finished.wait(min(15.0, every / 4)):
            now = time.time()
            if now - max(step['t'], last) >= every:
                print(f'  {time.strftime("%H:%M:%S")}    ... still running {step["name"]} ({(now - step["t"]) / 60:.0f} min)', flush=True)
                last = now
    threading.Thread(target=heartbeat, daemon=True).start()
    with open(os.path.join(check, 'run.log'), 'w') as log:
        py = shlex.quote(sys.executable)
        cmd = ['make', 'all', f'PY={py}'] + [f'{k}={v}' for k, v in sizes.items()]
        proc = subprocess.Popen(cmd, cwd=run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            log.write(line); log.flush()
            if line.startswith((py, sys.executable, 'MC_OUTER=', 'NTRIAL=')):
                m = re.search(r'scripts/\S+\.py', line)
                step.update(name=m.group(0) if m else 'make all', t=time.time())
                print(f'  {time.strftime("%H:%M:%S")}  {line.strip().replace(py, "python").replace(sys.executable, "python")}', flush=True)
        proc.wait()
    finished.set()
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
