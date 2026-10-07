"""Facility-site-time matrix (from scenario cards), orbiter follow-up windows figure, scenario summary table."""
import sys, os, json, glob, numpy as np, pandas as pd, yaml, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from ayap1obs import plotting as P, detect as D, montecarlo as MC
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml'))
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); templates = MC.load_templates()
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(f'{root}/outputs/scenarios/S*.json'))}
order = [s['id'] for s in cfg['scenarios'] if s['id'] in cards]
# matrix: rows = site:template, cols = scenarios; cell = limiting magnitude (Rc-equivalent band of the template) if available else blank
rows = []
for s in sites:
    for tname in cfg['site_templates'].get(s['id'], []):
        tp = templates[tname]; band = tp['bands'][0]
        inst = D.Instrument(tname, tp['aperture_m'], band, tp['pixel_scale_arcsec'], tuple(tp['fov_arcmin']), tp['exposure_s'], tp['frame_time_s'], throughput=tp['throughput'], obstruction=0.15, read_noise_e=tp['read_noise_e'], seeing_arcsec=tp['seeing_arcsec'])
        row = dict(site=s['id'], station=f"{s['name']} / {tname}", band=band, country=s['country'])
        for sid in order:
            g = cards[sid]['sites'][s['id']]
            if g['available']:
                ext = float(D.extinction_mag(band, g['airmass'], s['alt']))
                if g['sunlit']:
                    bkg = 3.4 + 2.5 * np.log10(1 / max(np.cos(np.radians(g['incidence'])), 0.05)) - D.LUNAR_COLOR_VS_V[band] + ext
                else:
                    bkg = D.total_background_sb(band, g['illum'], g['dist_sunlit_arcmin'], g['sun_alt'], ext_mag=ext)
                lim = D.limiting_magnitude(inst, bkg, 8.0) - ext   # above-atmosphere limiting magnitude
                row[sid] = f"{lim:.1f} ({g['moon_alt']:.0f}°)"
            elif g['visible'] and g['moon_alt'] > 0:
                row[sid] = 'twilight/day' if g['sun_alt'] > -12 else 'low'
            else:
                row[sid] = '-' if not g['visible'] else 'set'
        rows.append(row)
mat = pd.DataFrame(rows); mat.to_csv(f'{root}/outputs/tables/facility_site_time_matrix.csv', index=False)
# scenario summary
summ = []
for sid in order:
    c = cards[sid]; mB = c['mc']['B_global_science|slow-impact-wide']; mA = c['mc']['A_turkiye_priority|slow-impact-wide']; mC = c['mc']['C_public_participation|slow-impact-wide']; mBv = c['mc']['B_global_science|v3-scaled']
    summ.append(dict(id=sid, name=c['name'], cls=c['cls'], lat=c['lat'], lon=c['lon'], epoch_utc=c['epoch_utc'], istanbul=c['epoch_istanbul'], physics=c['physics']['label'], E_k_GJ=c['energy']['E_k_J'] / 1e9,
                     illum=round(c['moon']['illum_frac'], 2), emission=round(c['geometry']['emission_geocentric'], 1), incidence=round(c['geometry']['incidence'], 1), region=c['region'],
                     n_sites=c['n_sites_available'], n_turkish=len(c['turkish_sites_available']), pop_public_bn=round(c['population']['2'] / 1e9, 2), pop_facility_bn=round(c['population']['3'] / 1e9, 2),
                     peakV_med=round(mB['peakV_median'], 1), peakV_10_90=f"{mB['peakV_p10']:.1f}-{mB['peakV_p90']:.1f}",
                     pA_any=round(mA['p_any'], 2), pB_any=round(mB['p_any'], 2), pC_any=round(mC['p_any'], 2), pB_any_v3=round(mBv['p_any'], 2),
                     pA_conf=round(mA['p_confirmed'], 2), pB_conf=round(mB['p_confirmed'], 2), pC_conf=round(mC['p_confirmed'], 2),
                     pB_obvious=round(mB['p_obvious_any'], 2), pC_live=round(mC['p_live'], 2), pB_rapid=round(mB['p_rapid_replay'], 2), pA_turkish=round(mA['p_turkish'], 2),
                     p_eyepiece=round(mB['p_eyepiece_witness'], 3), p_binocular=round(mB['p_binocular_witness'], 4), p_naked=round(mB['p_naked_eye_witness'], 4),
                     plume_regime=c['plume']['regime'], shadow_h_km=round(c['plume']['shadow_height_km'], 1), crater_m=f"{c['crater']['diameter_m'][0]:.0f}-{c['crater']['diameter_m'][2]:.0f}",
                     terrain_p_vis=c['terrain']['p_visible_statistical'], reach_omega_asc=round(c['reachability']['omega0_ascending'], 1), reach_omega_desc=round(c['reachability']['omega0_descending'], 1),
                     lro_low_sun_days=(c['orbiters']['lro_low_sun_next'][0] if c['orbiters']['lro_low_sun_next'] else None)))
sm = pd.DataFrame(summ); sm.to_csv(f'{root}/outputs/tables/scenario_summary.csv', index=False)
print(sm[['id', 'cls', 'n_sites', 'pop_public_bn', 'peakV_med', 'pA_any', 'pB_any', 'pC_any', 'pB_conf', 'pB_obvious', 'pC_live', 'p_eyepiece', 'plume_regime']].to_string())
# orbiter windows figure
fig, ax = plt.subplots(figsize=(13, 3.2))
for k, (a, b) in enumerate(orb['lro']['low_sun_windows']):
    ax.axvspan(dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d'), ymin=0.55, ymax=0.95, color=P.CAT[0], alpha=0.35, label='LRO low-Sun imaging window (incidence >= 55 deg at low latitude; derived, +-3 wk)' if k == 0 else None)
for k, (a, b) in enumerate(orb['lro']['near_noon_windows']):
    ax.axvspan(dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d'), ymin=0.55, ymax=0.95, color=P.CAT[3], alpha=0.35, label='LRO near-noon window (albedo ratios; poor topography)' if k == 0 else None)
for k, (a, b) in enumerate(orb['danuri']['low_sun_windows']):
    ax.axvspan(dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d'), ymin=0.1, ymax=0.5, color=P.CAT[2], alpha=0.35, label='Danuri low-Sun window (derived; mission extension to 2027 only)' if k == 0 else None)
by_epoch = {}
for sid in order:  # scenarios sharing an epoch get one combined label
    by_epoch.setdefault(cards[sid]['epoch_utc'], []).append(sid)
for k, (e, sids) in enumerate(by_epoch.items()):
    t = dt.datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
    ax.axvline(t, color=P.CAT[7], lw=1, label='scenario epochs' if k == 0 else None)
    ax.text(t, 0.97, ' ' + ', '.join(sorted(sids, key=lambda s: int(s[1:]))), rotation=90, fontsize=6, va='top', ha='left', color=P.CAT[7])
ax.axvline(dt.datetime(2027, 12, 31), color=P.TEXT2, lw=1.2, ls='--', label='LRO fuel statement: "until 2027" (NASA, 2024); FY2027 budget risk; no approved end date found')
ax.set_yticks([0.3, 0.75]); ax.set_yticklabels(['Danuri/KPLO', 'LRO']); ax.set_xlim(dt.datetime(2027, 3, 1), dt.datetime(2029, 3, 1)); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2); ax.set_title('Orbiter follow-up: illumination windows (derived from the 331-day LRO beta cycle; research/orbiters.md) and scenario epochs', loc='left', fontsize=9)
P.evidence_tag(fig, 'DERIVED from Horizons orbital elements and LROC-reported incidence angles; windows uncertain by +-3 weeks; orbiter availability in 2028 is NOT assured')
fig.tight_layout(); P.savefig(fig, 'fig_orbiter_windows')
# latency precedent figure
lat = pd.read_csv(f'{root}/research/orbiter_latency.csv')
lat = lat[lat.days_event_to_first_image.notna()]
fig, ax = plt.subplots(figsize=(9, 3.6))
lab = lat.event.str.replace(' end-of-mission impact', '').str.replace(' (context)', '').str[:40]
y = np.arange(len(lat))
ax.barh(y, lat.days_event_to_first_image, color=P.CAT[0], height=0.35, label='impact -> first LRO NAC image (days)')
ax.barh(y + 0.38, lat.days_event_to_release, color=P.CAT[1], height=0.35, label='impact -> public release (days)')
ax.set_yticks(y + 0.19); ax.set_yticklabels(lab, fontsize=6.5); ax.set_xscale('log'); ax.set_xlabel('days'); ax.legend(fontsize=7); ax.invert_yaxis()
ax.set_title('OBSERVED precedent latencies for LROC imaging of impact sites and landings (research/orbiter_latency.csv)', loc='left', fontsize=8)
P.evidence_tag(fig, 'OBSERVED (LROC posts, NASA releases); day counts assume 12:00 UTC where times unknown')
fig.tight_layout(); P.savefig(fig, 'fig_orbiter_latency')
print('ok')
