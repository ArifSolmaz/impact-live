"""Facility-site-time matrix and scenario summary (from the scenario cards), LRO illumination seasons computed from
archived Horizons elements (outputs/tables/orbiter_seasons.json), the Danuri disposal plan and the orbiter-latency precedents (impacts separated from soft landings; first documented image and release counted
from the event)."""
import sys, os, json, glob, numpy as np, pandas as pd, yaml, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from ayap1obs import plotting as P, detect as D, montecarlo as MC
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml'))
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); templates = MC.load_templates()
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{root}/outputs/scenarios/S*.json')}
order = [s['id'] for s in cfg['scenarios'] if s['id'] in cards]
# ---- matrix: steady-source SNR-8 limit (above the atmosphere) with the exposure the station would use; 'saturated' if even the
#      shortest exposure fills half the full well with background
rows = []
for s in sites:
    for tname in cfg['site_templates'].get(s['id'], []):
        tp = templates[tname]; band = tp['bands'][0]
        st = MC.Station(s, tname, tp, tp['p_ready']); inst = st.instrument(band)
        row = dict(site=s['id'], station=f"{s['name']} / {tname}", band=band, country=s['country'])
        for sid in order:
            g = cards[sid]['sites'][s['id']]
            if g['available']:
                ext = float(D.extinction_mag(band, g['airmass'], s['alt']))
                bkg = float(D.total_background_sb(band, g['illum'], g['dist_sunlit_arcmin'], g['sun_alt'], 3e-3, ext, 0.0, g['sunlit'], g['incidence']))
                t_e = D.usable_exposure(inst, bkg)
                if t_e is None:
                    row[sid] = 'saturated'
                else:
                    inst.exposure_s = t_e
                    row[sid] = f"{D.limiting_magnitude(inst, bkg, 8.0) - ext:.1f} ({g['moon_alt']:.0f}°)" + ('*' if t_e < tp['exposure_s'] else '')
                    inst.exposure_s = tp['exposure_s']
            elif g['closed']:
                row[sid] = 'closed'
            elif g['visible'] and g['moon_alt'] > 0:
                row[sid] = 'twilight/day' if g['sun_alt'] > -12 else 'low'
            else:
                row[sid] = '-' if not g['visible'] else 'set'
        rows.append(row)
pd.DataFrame(rows).to_csv(f'{root}/outputs/tables/facility_site_time_matrix.csv', index=False)
# ---- scenario summary
def P_(m, strat, o):
    return m['strategies'][strat][o]
summ = []
for sid in order:
    c = cards[sid]; w = c['mc']['wide|broad']; v = c['mc']['v-scaled|broad']
    pl = c['plume']['cases']
    det = [r for r in pl if r['status'].startswith('within')]
    snr = [max(r['observers'][o]['sys0.001']['snr_max'] for o in r['observers']) for r in det] if det else []
    pop = c['population']['by_radius']
    row = dict(id=sid, name=c['name'], cls=c['cls'], lat=c['lat'], lon=c['lon'], impact_utc=c['epoch_utc'], istanbul=c['epoch_istanbul'], physics=c['physics']['label'],
               E_k_GJ=c['energy']['E_k_J'] / 1e9, illum=round(c['moon']['illum_frac'], 2), emission=round(c['geometry']['emission_geocentric'], 1), incidence=round(c['geometry']['incidence'], 1),
               region=c['region'], n_sites=c['n_sites_available'], n_turkish=len(c['turkish_sites_available']),
               light_time_s=f"{c['latency']['light_time_station_range_s'][0]:.3f}-{c['latency']['light_time_station_range_s'][1]:.3f}" if c['latency']['light_time_station_range_s'] else '',
               p_random_plane_0p6=round(c['reachability']['p_random_polar_plane_within']['0.6'], 4), p_random_plane_2p5=round(c['reachability']['p_random_polar_plane_within']['2.5'], 4),
               terrain_p_range=f"{c['terrain']['p_terrain_range'][0]:.2f}-{c['terrain']['p_terrain_range'][1]:.2f}",
               settlements_public_bn_10km=round(pop['10km']['public'] / 1e9, 2), settlements_public_bn_range=f"{pop['25km']['public']/1e9:.2f}-{pop['0km']['public']/1e9:.2f}",
               peakV_med=round(w['peakV']['median'], 1), peakV_10_90=f"{w['peakV']['p10']:.1f}-{w['peakV']['p90']:.1f}", lab_trend_peakV=round(c['lab_trend']['V_peak'], 1))
    for strat, tag in (('A_turkiye_priority', 'A'), ('B_global_science', 'B'), ('C_public_participation', 'C')):
        for o in ('any', 'two_indep', 'dual_validated', 'live', 'turkish'):
            x = P_(w, strat, o); row[f'p{tag}_{o}'] = round(x['p'], 3); row[f'p{tag}_{o}_outer'] = f"{x['outer_p05']:.2f}-{x['outer_p95']:.2f}"
        row[f'p{tag}_any_vscaled'] = round(P_(v, strat, 'any')['p'], 3); row[f'p{tag}_two_indep_vscaled'] = round(P_(v, strat, 'two_indep')['p'], 3)
    vis = c['public']['visual']
    for aid in ('none', 'binoculars', 'telescope20cm'):
        row[f'visual_{aid}_conditional'] = round(vis[aid]['p_conditional'], 4) if vis.get('observable') else 0.0
    row['plume'] = ('cannot determine (all cases outside the scaling domain)' if pl and not det else
                    (f"within-domain cases: max SNR {max(snr):.2f} (1-m, 1 s)" if det else 'not computed (far side)'))
    env = c['crater']['rim_diameter_m']
    row['crater_rim_m'] = f"{env['vertical-component'][0]:.0f}-{env['vertical-component'][2]:.0f} (U sin) / {env['vertical-equivalent'][0]:.0f}-{env['vertical-equivalent'][2]:.0f} (U)"
    summ.append(row)
sm = pd.DataFrame(summ); sm.to_csv(f'{root}/outputs/tables/scenario_summary.csv', index=False)
print(sm[['id', 'cls', 'n_sites', 'peakV_med', 'pA_any', 'pB_any', 'pC_any', 'pB_two_indep', 'pB_dual_validated', 'pC_live', 'visual_telescope20cm_conditional', 'plume']].to_string())
# ---- orbiter illumination seasons (computed, orbit plane) and the Danuri disposal plan
seas = json.load(open(f'{root}/outputs/tables/orbiter_seasons.json'))
day = lambda x: dt.datetime.strptime(x, '%Y-%m-%d')
fig, ax = plt.subplots(figsize=(13, 3.6)); hatch_label = ['range of a season boundary (alternative node fits)']
for key, col, lab in (('low_sun', P.CAT[0], 'LRO low-Sun season (|beta| >= 55 deg)'), ('near_noon', P.CAT[3], 'LRO near-noon season (|beta| <= 15 deg)')):
    for k, w in enumerate(seas['lro'][key]):
        ax.axvspan(day(w['start']), day(w['end']), ymin=0.47, ymax=0.82, color=col, alpha=0.35, lw=0, label=lab if k == 0 else None)
        for (a, b) in (w['start_range'], w['end_range']):                    # boundary range from the alternative node fits
            if a != b:
                ax.axvspan(day(a), day(b) + dt.timedelta(days=1), ymin=0.47, ymax=0.82, facecolor='none', edgecolor=col, hatch='////', lw=0,
                           label=hatch_label.pop() if hatch_label else None)
dan = seas['danuri']; t_dan = day(dan['available_until']) + dt.timedelta(days=1)
for k, w in enumerate(x for x in dan['low_sun'] if not x.get('after_planned_end')):
    ax.axvspan(day(w['start']), min(day(w['end']), t_dan), ymin=0.06, ymax=0.41, color=P.CAT[2], alpha=0.35, lw=0, label='Danuri low-Sun season (|beta| >= 55 deg)' if k == 0 else None)
    for (a, b) in (w['start_range'], w['end_range']):
        if a != b:
            ax.axvspan(day(a), day(b) + dt.timedelta(days=1), ymin=0.06, ymax=0.41, facecolor='none', edgecolor=P.CAT[2], hatch='////', lw=0)
ax.axvspan(t_dan, dt.datetime(2029, 3, 1), ymin=0.06, ymax=0.41, color=P.TEXT2, alpha=0.12, lw=0, label='Danuri after its planned lunar impact (March 2028, KASA)')
by_epoch = {}
def id_list(sids):                                                           # 'S1, S2, S5, S7-S10'
    n = sorted(int(s[1:]) for s in sids); runs, out = [[n[0]]], []
    for x in n[1:]:
        (runs[-1].append(x) if x == runs[-1][-1] + 1 else runs.append([x]))
    for r in runs:
        out += [f'S{r[0]}-S{r[-1]}'] if len(r) >= 3 else [f'S{x}' for x in r]
    return ', '.join(out)
for sid in order:
    by_epoch.setdefault(cards[sid]['epoch_utc'], []).append(sid)
for k, (e, sids) in enumerate(by_epoch.items()):
    t = dt.datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
    ax.axvline(t, color=P.CAT[7], lw=1, label='scenario impact times' if k == 0 else None)
    ax.text(t, 0.915, ' ' + id_list(sids), transform=ax.get_xaxis_transform(), fontsize=6.5, va='center', ha='left', color=P.CAT[7])   # label strip above the bands
ax.axvline(dt.datetime(2027, 12, 31), color=P.TEXT2, lw=1.2, ls='--', label='LRO fuel statement "until 2027" (NASA, 2024); no approved end date found')
ax.set_ylim(0, 1); ax.set_yticks([0.235, 0.645]); ax.set_yticklabels(['Danuri/KPLO', 'LRO']); ax.set_xlim(dt.datetime(2027, 3, 1), dt.datetime(2029, 3, 1))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2)
hs = seas['lro']['holdout_summary']
ax.set_title(f"Orbiter follow-up: orbit-plane illumination seasons from tracking-based JPL Horizons elements (LRO to {seas['lro']['tracking_based_until_tdb']}, "
             f"Danuri to {dan['tracking_based_until_tdb']}), extrapolated\n(LRO hold-out test: boundaries within {hs['central_fit_max_boundary_shift_days']:.0f} days over 1.5-2.5 years; "
             "assumes no orbit manoeuvre; a season does not guarantee a sunlit pass over a target) and the scenario impact times", loc='left', fontsize=8.2)
P.evidence_tag(fig, 'COMPUTED GEOMETRY from archived JPL Horizons elements; orbiter availability in 2028 is not assured')
fig.tight_layout(); P.savefig(fig, 'fig_orbiter_windows')
# ---- latency precedents
lat = pd.read_csv(f'{root}/research/orbiter_latency.csv')
lat = lat[lat.days_event_to_first_image.notna()].copy()
grp = {'planned impact': 0, 'uncontrolled impact': 1, 'soft landing (context)': 2, 'natural impact (context)': 3}
lat['g'] = lat.event_class.map(grp); lat = lat.sort_values(['g', 'days_event_to_first_image'], kind='stable')
fig, ax = plt.subplots(figsize=(10, 5.6))
y = np.arange(len(lat))
lab = (lat.event.str.replace(' end-of-mission impacts', '').str.replace(' end-of-mission impact', '').str.replace(' (context)', '').str.replace(r'\s*\(Blue Ghost M1 launch, 15 Jan 2025\)', ' (2025-010D)', regex=True)
       .str.replace(r'\s*\(natural, context\)', ' (natural)', regex=True).str[:44])
cols = [P.CAT[grp[c]] for c in lat.event_class]
ax.barh(y, lat.days_event_to_first_image, color=cols, height=0.38)
ax.scatter(lat.days_event_to_release, y + 0.3, marker='|', color='k', s=60, label='first public release (days after the event)')
for yy, (_, r) in zip(y, lat.iterrows()):
    if r.first_image_bound == '<=':
        ax.text(r.days_event_to_first_image * 0.92, yy - 0.05, 'upper bound', fontsize=6, va='center', ha='right', color='white')
    if np.isfinite(r.get('days_event_to_confirmation', np.nan)):
        ax.scatter(r.days_event_to_confirmation, yy + 0.3, marker='*', color=P.CAT[7], s=40, label='identification released (Vikram, day 87)')
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=6.5); ax.set_xscale('log'); ax.set_xlabel('days after the event'); ax.invert_yaxis()
from matplotlib.patches import Patch
h, l = ax.get_legend_handles_labels()
ax.legend(handles=[Patch(color=P.CAT[v], label=k + ': first documented post-event NAC image') for k, v in grp.items()] + h, fontsize=6.5,
          loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False)
ax.set_title('OBSERVED precedents for LROC imaging (research/orbiter_latency.csv): a small, selected sample, not a forecast', loc='left', fontsize=8.5)
P.evidence_tag(fig, 'OBSERVED (LROC posts, NASA releases); day counts assume 12:00 UTC where times are unknown')
fig.tight_layout(); P.savefig(fig, 'fig_orbiter_latency')
print('ok')
