"""Orbiter follow-up baseline (re-audit GE-21, GE-V2-05) -> outputs/tables/orbiter_seasons.json.

LRO and Danuri: beta angle from archived JPL Horizons osculating elements (ayap1obs/orbiters.py), daily at 12:00 TDB
from 2027-01-01 to 2029-09-30 (the scenario domain is May 2027 - Feb 2029, plus the season after it); low-Sun seasons
|beta| >= 55 deg and near-noon seasons |beta| <= 15 deg. Only the tracking-based part of each table is used
(config/orbiters.yaml: elements_tracking_until; LRO to 2026-09-02, Danuri to 2026-09-29): every date in the span is an
extrapolation of the observed node trend (central fit and alternatives in config: season_fits), and each season
boundary carries the range given by the alternative fits. The Horizons predictions are not used; their node rates are
listed for comparison (LRO's is 5-25 times slower than observed; Danuri's KARI prediction agrees with the observed
trend, and the beta angles it implies are compared). Checks: a hold-out test of the extrapolation (fits ending
earlier, compared with the later tracking data) and, for LRO, the predicted overflight incidence against LROC-reported
values for the Falcon 9 stage crater (2026-08-11, 19.48 N; 67-71 deg) and the SLIM landing site (2024-01-24, 13.32 S;
14 deg).
Danuri: KASA's press release of 10 February 2025 states that after the extended mission (to the end of 2027) the
orbit will be lowered to near-landing altitude to test landing technology and the spacecraft will be crashed into the
Moon in March 2028 ("2028년 3월, 달에 충돌하도록 할 계획이다"). The baseline therefore treats Danuri as available until
2028-02-29 and not after (seasons after that date are flagged); continued operation is a separate changed-plan
sensitivity. The extrapolation assumes no orbit manoeuvre (KASA plans to lower Danuri's orbit after 2027)."""
import sys, os, json, numpy as np, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import orbiters as O
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml'))
jdT = lambda s: Time(s, scale='tdb').jd
iso = lambda j: Time(j, format='jd', scale='tdb').utc.iso[:10]
isot = lambda j: Time(j, format='jd', scale='tdb').iso[:10]                           # TDB calendar date (table epochs)
jd = jdT('2027-01-01 12:00') + np.arange(0, jdT('2029-09-30') - jdT('2027-01-01') + 1, 1.0)     # daily at 12:00 TDB
TESTS = {'low_sun': lambda b: np.abs(b) >= 55.0, 'near_noon': lambda b: np.abs(b) <= 15.0}

def seasons(beta, alt, key, t_obs, until=None):
    out = []
    central = O.intervals(jd, TESTS[key](beta))
    alts = {fit: O.intervals(jd, TESTS[key](b)) for fit, b in alt.items()}
    for a, b in central:
        starts, ends = [a], [b]
        for fit, wins in alts.items():
            if wins:
                w = min(wins, key=lambda x: abs(0.5 * (x[0] + x[1]) - 0.5 * (a + b)))
                if abs(0.5 * (w[0] + w[1]) - 0.5 * (a + b)) < 90:                      # the same season in the alternative fit
                    starts.append(w[0]); ends.append(w[1])
        rec = dict(start=iso(a), end=iso(b), start_range=[iso(min(starts)), iso(max(starts))], end_range=[iso(min(ends)), iso(max(ends))],
                   clipped_at_span_start=bool(a <= jd[0]), clipped_at_span_end=bool(b >= jd[-1]), extrapolated=bool(b > t_obs))
        if until is not None:
            rec['after_planned_end'] = bool(iso(a) > until)
        out.append(rec)
    return out

def orbiter_block(key, spans, holdout_cuts, until=None):
    cfg = orb[key]; src = cfg['elements_file']
    el = O.read_horizons_elements(f'{root}/{src}', cfg.get('elements_tracking_until'))
    t_obs = el['observed_until_jd']
    fits = cfg['season_fits']; central = tuple(fits['central']); alternatives = [tuple(f) for f in fits['alternatives']]
    beta, extrap = O.beta_angle(el, jd, central)
    alt = {f: O.beta_angle(el, jd, f)[0] for f in alternatives}
    holdouts = []
    for cut in holdout_cuts:
        for f in [central] + alternatives:
            h = O.holdout(el, jdT(cut), f)
            holdouts.append(dict(fit_end=cut, fit=dict(node_degree=f[0], window_days=f[1]), **h))
    ch = [h for h in holdouts if (h['fit']['node_degree'], h['fit']['window_days']) == central]
    shifts = [h['max_abs_boundary_shift_days'] for h in ch if h['max_abs_boundary_shift_days'] is not None]
    rates = O.node_rates(el, [(lab, jdT(a) if isinstance(a, str) else a, jdT(b) if isinstance(b, str) else b) for lab, a, b in spans(t_obs, el)])
    blk = dict(source=src, elements_span_tdb=[isot(el['jd_tdb'][0]), isot(el['jd_tdb'][-1])], tracking_based_until_tdb=isot(t_obs),
               span=['2027-01-01', '2029-09-30'],
               low_sun=seasons(beta, alt, 'low_sun', t_obs, until), near_noon=seasons(beta, alt, 'near_noon', t_obs, until),
               criteria='low Sun: |beta| >= 55 deg (incidence >= 55 deg at low latitude); near noon: |beta| <= 15 deg',
               method=(f'beta angle from the node and inclination of the tracking-based elements (to {isot(t_obs)} TDB) extrapolated with a degree-{central[0]} '
                       f'node trend fitted to the final {central[1]:g} days (linear inclination trend); start_range and end_range span the central fit and '
                       'alternative fits (' + ', '.join(f'degree {f[0]} over {f[1]:g} days' for f in alternatives) + '); season dates are UTC calendar days '
                       'sampled at 12:00 TDB'),
               node_rates_deg_per_day={k: (round(v, 4) if v is not None else None) for k, v in rates.items()},
               holdout=holdouts,
               holdout_summary=dict(central_fit_max_boundary_shift_days=max(shifts) if shifts else None,
                                    central_fit_max_node_error_deg=max(abs(h['node_error_end_deg']) for h in ch),
                                    test_spans_days=[h['span_days'] for h in ch]),
               daily_beta=dict(start_tdb='2027-01-01 12:00', step_days=1, beta_deg=[round(float(x), 3) for x in beta], extrapolated=[bool(x) for x in extrap]),
               note=(f'orbit-plane condition from tracking-based Horizons elements extrapolated beyond {isot(t_obs)} TDB; it assumes no orbit manoeuvre and '
                     'does not guarantee a target pass, operations or a before/after pair'))
    return blk, el, t_obs, central

# ---------------------------------------------------------------- LRO
lro, el_lro, t_lro, c_lro = orbiter_block(
    'lro', lambda t_obs, el: [('2023 (reconstructed)', '2023-01-01', '2024-01-01'), ('2024 (reconstructed)', '2024-01-01', '2025-01-01'),
                              ('2025-01 to 2026-03 (reconstructed)', '2025-01-01', '2026-03-15'), ('2026-03 to 2026-09 (tracking, tag-up)', '2026-03-15', t_obs),
                              ('2026-09 to 2027-06 (Horizons prediction, not used)', t_obs + 1, '2027-06-01'),
                              ('2027-06 to 2028-03 (Horizons prediction, not used)', '2027-06-01', float(el['jd_tdb'][-1]))],
    ('2024-03-02', '2024-09-02', '2025-03-02'))
r = lro['node_rates_deg_per_day']
lro['horizons_prediction_not_used'] = ('the Horizons prediction after %s regresses the node at %.3f to %.3f deg/day against %.3f to %.3f deg/day in the '
                                       'observed spans (accelerating), which marks it as a low-fidelity placeholder' %
                                       (lro['tracking_based_until_tdb'], r['2026-09 to 2027-06 (Horizons prediction, not used)'], r['2027-06 to 2028-03 (Horizons prediction, not used)'],
                                        r['2023 (reconstructed)'], r['2026-03 to 2026-09 (tracking, tag-up)']))
checks = []
for name, t, lat, rep in [('Falcon 9 stage crater', '2026-08-11 12:39', 19.4759, [67.0, 71.0]), ('SLIM landing site', '2024-01-24 12:00', -13.316, [14.0, 14.0])]:
    b, ex = O.beta_angle(el_lro, np.array([Time(t, scale='utc').tdb.jd]), c_lro)
    inc = float(O.overflight_incidence_deg(lat, b[0]))
    checks.append(dict(case=name, utc=t, lat=lat, beta_deg=round(float(b[0]), 3), predicted_incidence_deg=round(inc, 2), lroc_reported_incidence_deg=rep,
                       within_3_deg=bool(rep[0] - 3 <= inc <= rep[1] + 3), elements='tracking-based' if not ex[0] else 'extrapolated'))
lro['checks'] = checks

# ---------------------------------------------------------------- Danuri
dcfg = orb['danuri']
dan, el_dan, t_dan, c_dan = orbiter_block(
    'danuri', lambda t_obs, el: [('2023-2024 (100-km circular orbit)', '2023-01-01', '2025-01-01'), ('2025-03 to 2025-09 (~60-km orbit)', '2025-03-01', '2025-09-01'),
                                 ('2025-12 to 2026-09 (~55-60 x 205 km orbit, tracking)', '2025-12-01', t_obs),
                                 ('2026-09 to 2027-04 (KARI prediction, not used)', t_obs + 1, float(el['jd_tdb'][-1]))],
    ('2026-03-29', '2026-06-29'), until=dcfg['available_until'])
# the KARI prediction as a check: beta angles implied by the predicted elements versus the extrapolation
w = el_dan['jd_tdb'] > t_dan; jw = el_dan['jd_tdb'][w]
b_pred = O.beta_from_elements(el_dan['IN'][w], el_dan['OM_unwrapped'][w], O.sun_dir_ecliptic(jw))
b_ext, _ = O.beta_angle(el_dan, jw, c_dan)
dan['prediction_check'] = dict(span_tdb=[isot(jw[0]), isot(jw[-1])], max_abs_beta_difference_deg=round(float(np.abs(b_pred - b_ext).max()), 2),
                               note='KARI prediction in the Horizons record (not used for the seasons) versus the extrapolation of the tracking-based elements')
dan.update(planned_impact='2028-03', available_until=dcfg['available_until'], baseline='not available after its planned March 2028 lunar impact',
           source_plan='KASA press release, 10 February 2025 (planned lunar impact in March 2028 after low-altitude landing-technology tests)',
           sensitivity='continued operation after March 2028 (changed plan) with the same assumed availability',
           research_notes_estimate_low_sun=dcfg['research_notes_estimate_low_sun'])
out = dict(lro=lro, danuri=dan)
json.dump(out, open(f'{root}/outputs/tables/orbiter_seasons.json', 'w'), indent=1)
for name, blk, cen in (('LRO', lro, c_lro), ('Danuri', dan, c_dan)):
    print(f"{name}: tracking to {blk['tracking_based_until_tdb']}; node rates {blk['node_rates_deg_per_day']}")
    for k in ('low_sun', 'near_noon'):
        print('  ', k)
        for s_ in blk[k]:
            print(f"     {s_['start']} .. {s_['end']}   start range {s_['start_range'][0]}..{s_['start_range'][1]}, end range {s_['end_range'][0]}..{s_['end_range'][1]}"
                  + ('  (after the planned end)' if s_.get('after_planned_end') else ''))
    print('   hold-out (central fit):', [(h['fit_end'], round(h['node_error_end_deg'], 2), h['max_abs_boundary_shift_days']) for h in blk['holdout']
                                         if (h['fit']['node_degree'], h['fit']['window_days']) == cen])
print('Danuri prediction check:', dan['prediction_check'])
for c in checks:
    print(f"check {c['case']}: incidence {c['predicted_incidence_deg']:.1f} deg vs LROC {c['lroc_reported_incidence_deg']} -> {'OK' if c['within_3_deg'] else 'MISMATCH'} ({c['elements']})")
