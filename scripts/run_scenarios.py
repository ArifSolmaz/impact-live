"""Scenario pipeline: for each hypothetical scenario compute exact geometry per site, backgrounds, plume and
terrain checks, flash-magnitude tables, Earth coverage and population, network Monte Carlo for strategies A/B/C,
orbiter windows, public assessment.  Writes outputs/scenarios/<id>.json and figures."""
import sys, os, json, yaml, numpy as np, pandas as pd, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
from astropy.time import Time
import matplotlib.pyplot as plt
from ayap1obs import geometry as G, ephem as E, impact as I, detect as D, terrain as T, montecarlo as MC, population as Pp, plotting as P, reachability as Rr, grid as Gd, screening as S
import healpy as hp
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml')); fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml'))
templates = MC.load_templates()
outdir = f'{root}/outputs/scenarios'; os.makedirs(outdir, exist_ok=True)
dem = T.load_default_dem()
only = sys.argv[1:]  # optional scenario ids
NMC = int(os.environ.get('NMC', '6000'))

def dist_to_sunlit_arcmin(es, obs_vec, lat, lon, nside=128):
    la, lo, _, _ = Gd.healpix_grid(nside)
    em, inc = S.surface_classes(es.r_moon, es.r_sun, es.M, la, lo, obs_vec)
    sunlit_vis = (inc < 90) & (em < 90)
    if not sunlit_vis.any():
        return 999.0
    p_me = E.latlon_to_vec(la[sunlit_vis], lo[sunlit_vis]); p_pt = E.latlon_to_vec(np.array([lat]), np.array([lon]))
    c = es.r_moon - obs_vec; c_hat = c / np.linalg.norm(c)
    ex = np.cross([0, 0, 1.0], c_hat); ex /= np.linalg.norm(ex); ey = np.cross(c_hat, ex)
    def proj(p):
        v = (p @ es.M)                       # ICRF offsets from Moon centre
        return np.stack([v @ ex, v @ ey], axis=1) / np.linalg.norm(c) * 206265 / 60.0   # arcmin
    d = np.hypot(*(proj(p_me) - proj(p_pt)).T)
    return float(d.min())

def build_stations(strategy, geom):
    st_cfg = cfg['strategies'][strategy]; out = []
    for s in sites:
        if st_cfg['include_groups'] != 'all' and s['group'] not in st_cfg['include_groups']:
            continue
        tlist = list(cfg['site_templates'].get(s['id'], []))
        if st_cfg.get('add_amateur_everywhere') and 'amateur_class' not in tlist:
            tlist.append('amateur_class')
        for tname in tlist:
            if st_cfg['include_templates'] != 'all' and tname not in st_cfg['include_templates']:
                continue
            t = templates[tname]
            st = MC.Station(s, tname, t, t['p_ready'], streaming=(f"{s['id']}:{tname}" in st_cfg.get('streaming', [])), geometry=geom[s['id']])
            out.append(st)
    return out

for scn in cfg['scenarios']:
    if only and scn['id'] not in only:
        continue
    tic = time.time()
    phys = cfg['physics'][scn['physics']]
    es = G.epoch_state(scn['epoch_utc'])
    card = dict(id=scn['id'], name=scn['name'], cls=scn['class'], hypothetical=True, note='HYPOTHETICAL TEST POINT - not an official AYAP-1 target',
                lat=scn['lat'], lon=scn['lon'], epoch_utc=scn['epoch_utc'], epoch_istanbul=(Time(scn['epoch_utc']).to_datetime() + dt.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M (UTC+3)'),
                physics=phys, rationale=scn['rationale'], region=str(Gd.region_label(np.array([scn['lat']]), np.array([scn['lon']]))[0]),
                moon=dict(subsolar_lon=es.subsolar_lon, subsolar_lat=es.subsolar_lat, subearth_lon=es.subearth_lon, subearth_lat=es.subearth_lat,
                          phase_angle=es.phase_angle, illum_frac=es.illum_frac, elongation=es.elongation, distance_km=es.distance_km, light_time_s=es.light_time_s,
                          moon_age_days=float(((es.elongation if es.subsolar_lon > 0 else 360 - es.elongation) / 360) * 29.53)))
    # reachability condition
    t_ref = Time(fam['reference_epoch_utc']).utc.jd; jd = Time(scn['epoch_utc']).utc.jd
    om_asc = (scn['lon'] + Rr.OMEGA_MOON_DEG_DAY * (jd - t_ref)) % 360; om_desc = (om_asc + 180) % 360
    card['reachability'] = dict(status='conditional', condition=f"orbit node longitude at {fam['reference_epoch_utc']} must be {om_asc:.1f} deg (ascending pass) or {om_desc:.1f} deg (descending) within +-{fam['cross_track_tolerance_deg'][0]} deg (no plane change) or +-{fam['cross_track_tolerance_deg'][1]} deg (~70 m/s plane change); otherwise the nearest passes over this site occur ~13.7 days earlier/later with different phase and local time",
                                omega0_ascending=om_asc, omega0_descending=om_desc, polar_note='polar sites (|lat|>85) are crossed on every orbit' if abs(scn['lat']) > 85 else '')
    # per-site geometry
    geom = {}
    for s in sites:
        obs = G.Observer(s['id'], s['lon'], s['lat'], s['alt'])
        g = G.surface_geometry(es, obs, [scn['lat']], [scn['lon']])
        obs_vec = E.observer_gcrs(s['lon'], s['lat'], s['alt'], es.t)
        dsun = dist_to_sunlit_arcmin(es, obs_vec, scn['lat'], scn['lon']) if g['visible'][0] and g['alt_moon'] > 0 else np.nan
        geom[s['id']] = dict(visible=bool(g['visible'][0]), emission=float(g['emission'][0]), incidence=float(g['incidence'][0]), sunlit=bool(g['sunlit'][0]),
                             moon_alt=float(g['alt_moon']), moon_az=float(g['az_moon']), sun_alt=float(g['sun_alt_obs']), alt_point=float(g['alt_point'][0]),
                             airmass=float(G.airmass(g['alt_moon'])), illum=es.illum_frac, dist_sunlit_arcmin=float(dsun) if np.isfinite(dsun) else 999.0,
                             disk_x=float(g['disk_x'][0]), disk_y=float(g['disk_y'][0]), range_km=float(g['range_km'][0]),
                             twilight=int(G.twilight_class(g['sun_alt_obs'])), available=bool(g['visible'][0] and g['alt_moon'] >= 20 and g['sun_alt_obs'] <= -12),
                             local_time=(Time(scn['epoch_utc']).to_datetime() + dt.timedelta(hours=round(s['lon'] / 15))).strftime('%H:%M') + ' (approx. local solar zone)')
    card['sites'] = geom
    avail_ids = [k for k, v in geom.items() if v['available']]
    card['n_sites_available'] = len(avail_ids); card['sites_available'] = avail_ids
    card['turkish_sites_available'] = [k for k in avail_ids if next(s for s in sites if s['id'] == k)['group'] == 'turkiye']
    # geocentric geometry + terrain
    g0 = G.surface_geometry(es, G.Observer('geocentre', 0, 0, -6371000.0), [scn['lat']], [scn['lon']])   # trick: height -R -> geocentre
    em0 = float(g0['emission'][0]); inc0 = float(g0['incidence'][0])
    card['geometry'] = dict(emission_geocentric=em0, incidence=inc0, sunlit=bool(inc0 < 90), earth_elev_local=90 - em0, sun_elev_local=90 - inc0,
                            shadow_height_km=float(G.shadow_height_km(inc0)), limb_clearance_km=float(G.limb_clearance_height_km(em0)))
    vis_t = T.earth_visible_with_terrain(dem, es, np.zeros(3), scn['lat'], scn['lon'], em0)
    H_pl = T.plume_clearance_height_km(dem, es, np.zeros(3), scn['lat'], scn['lon'], em0)
    # statistical terrain: P(Earth above local horizon) from random synthetic-DEM sites with the same emission angle
    rng = np.random.default_rng(7); hz = np.array([T.horizon_elevation(dem, la, lo, az) for la, lo, az in zip(rng.uniform(-70, 70, 150), rng.uniform(-180, 180, 150), rng.uniform(0, 360, 150))])
    rough = 1.6 if abs(scn['lat']) > 75 else (1.0 if scn.get('terrain_class', 'highland') == 'highland' else 0.6)
    if abs(scn['lat']) <= 75 and abs(scn['lon']) < 60 and -30 < scn['lat'] < 45 and scn['lon'] < 30:
        rough = 0.6   # western/central near-side maria (hypothetical sites S1, S2, S4, S10, S11 lie on mare terrain)
    p_terr = float(np.mean(hz * rough < (90 - em0)))
    card['terrain'] = dict(dem=dem.label, local_horizon_elev_deg=vis_t[2], earth_elev_deg=vis_t[1], visible_with_terrain=vis_t[0], plume_clearance_km=H_pl, roughness_factor=rough,
                           p_visible_statistical=p_terr, note='SYNTHETIC DEM horizon statistics scaled by a terrain-class roughness factor (mare 0.6, highland 1.0, polar 1.6); replace with LDEM_16 ray tracing for site-specific results')
    # flash magnitude table
    E_k = I.kinetic_energy(np.mean(phys['mass_kg']), phys['v_km_s'])
    card['energy'] = dict(E_k_J=E_k, mass_mean_kg=float(np.mean(phys['mass_kg'])), v_km_s=phys['v_km_s'], angle_deg=phys['angle_deg'], tnt_equiv_kg=E_k / 4.184e6)
    tab = []
    for eta in [1e-5, 1e-4, 1e-3]:
        for T0 in [2000, 2500, 3000]:
            fm = I.FlashModel(E_k, eta, T0, 1200, 0.5, 0.5)
            tab.append(dict(eta_vis=eta, T0=T0, **{f'{b}_peak': round(fm.peak_magnitude(b, es.distance_km * 1e3), 2) for b in I.BANDS},
                            **{f'{b}_avg33ms': round(fm.exposure_averaged_magnitude(b, 0.033, distance_m=es.distance_km * 1e3), 2) for b in ['Rc', 'Ic']},
                            **{f'{b}_avg2s': round(fm.exposure_averaged_magnitude(b, 2.0, distance_m=es.distance_km * 1e3), 2) for b in ['Ks']}))
    card['flash_magnitudes'] = tab
    # plume
    h_shadow = card['geometry']['shadow_height_km']
    v_need = float(I.speed_for_height(max(h_shadow, H_pl if np.isfinite(H_pl) else 0) * 1e3 + 500.0))
    M_sun = float(I.ejecta_mass_above_speed(np.mean(phys['mass_kg']), phys['v_km_s'], v_need, angle_deg=phys['angle_deg']))   # nominal: vertical component
    M_up = float(I.ejecta_mass_above_speed(np.mean(phys['mass_kg']), phys['v_km_s'], v_need, angle_deg=90.0))                # upper bound: full speed
    dist_m = es.distance_km * 1e3
    plume = dict(shadow_height_km=h_shadow, clearance_height_km=H_pl if np.isfinite(H_pl) else None, ejecta_speed_needed_m_s=v_need,
                 ejecta_mass_sunlit_kg=M_sun, ejecta_mass_sunlit_upper_kg=M_up, flight_time_s=float(I.ballistic_flight_time(v_need)),
                 plume_V_mag_10um=float(I.plume_magnitude(M_sun, 1e-5, distance_m=dist_m)), plume_V_mag_1um=float(I.plume_magnitude(M_sun, 1e-6, distance_m=dist_m)),
                 plume_V_mag_10um_upper=float(I.plume_magnitude(M_up, 1e-5, distance_m=dist_m)))
    ang_rad_arcsec = 206265 * 5.0 / es.distance_km   # 5-km plume radius
    area = np.pi * ang_rad_arcsec ** 2
    plume['plume_sb_10um_mag_arcsec2'] = float(I.surface_brightness(plume['plume_V_mag_10um'], area))
    plume['plume_sb_10um_upper_mag_arcsec2'] = float(I.surface_brightness(plume['plume_V_mag_10um_upper'], area))
    plume['background_sb_V'] = float(D.earthshine_sb_V(es.illum_frac)) if inc0 > 90 else 3.4 + 2.5 * np.log10(max(np.cos(np.radians(inc0)), 0.05) ** -1)
    plume['contrast_10um'] = float(10 ** (-0.4 * (plume['plume_sb_10um_mag_arcsec2'] - plume['background_sb_V'])))
    plume['contrast_10um_upper'] = float(10 ** (-0.4 * (plume['plume_sb_10um_upper_mag_arcsec2'] - plume['background_sb_V'])))
    plume['regime'] = 'sunlit plume over dark ground' if (inc0 > 90 and h_shadow < 30) else ('plume over sunlit ground (low contrast, LCROSS-like)' if inc0 < 90 else 'plume stays in shadow (needs > 30 km)')
    if inc0 > 90 and h_shadow >= 30:
        # only Earthshine (~10 mag fainter than sunlight) illuminates the cloud: integrated magnitude ~ +21, undetectable
        plume.update(ejecta_mass_sunlit_kg=0.0, ejecta_mass_sunlit_upper_kg=0.0, plume_V_mag_10um=None, plume_V_mag_1um=None, plume_V_mag_10um_upper=None,
                     plume_sb_10um_mag_arcsec2=None, plume_sb_10um_upper_mag_arcsec2=None, contrast_10um=None, contrast_10um_upper=None,
                     earthshine_lit_plume_V_mag=float(I.plume_magnitude(I.ejecta_mass_above_speed(np.mean(phys['mass_kg']), phys['v_km_s'], 100.0, angle_deg=90.0), 1e-5, distance_m=dist_m) + 9.7))
    card['plume'] = plume
    # crater
    dmin, dmed, dmax = I.crater_diameter_range(np.mean(phys['mass_kg']), phys['v_km_s'], phys['angle_deg'])
    card['crater'] = dict(diameter_m=[dmin, dmed, dmax], angular_size_arcsec=206265 * dmed / 1e3 / es.distance_km, lroc_nac_pixels=dmed / orb['lro']['nac_resolution_m'],
                          note='pi-scaling with 15-deg angle floor; elongated/irregular for grazing impacts')
    # latencies
    card['latency'] = dict(light_time_s=es.light_time_s, telemetry_note='direct-to-Earth S/X-band: last frames before loss of signal arrive ~1.3 s after emission + ground processing (assumed 5-60 s); no relay -> no post-impact telemetry',
                           broadcast_s=[10, 60], rapid_replay_min=[5, 60], confirmed_detection_h=[1, 24])
    # Earth coverage & population
    cov = Pp.coverage_at_epoch(scn['epoch_utc'], scn['lat'], scn['lon']); cls = Pp.classify_coverage(cov); pop = Pp.population_by_class(cov, cls)
    card['population'] = pop
    # orbiter windows
    t_imp = Time(scn['epoch_utc']).to_datetime()
    def next_window(wins):
        for a, b in wins:
            a_, b_ = dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d')
            if b_ >= t_imp:
                return (max(a_, t_imp) - t_imp).days, a, b
        return None
    nw = next_window(orb['lro']['low_sun_windows'])
    card['orbiters'] = dict(lro_low_sun_next=nw, lro_first_image_days=orb['lro']['latency_first_image_days'], lro_release_days=orb['lro']['latency_release_days'],
                            p_lro_operational=orb['lro']['p_operational_2028'], danuri_low_sun_next=next_window(orb['danuri']['low_sun_windows']), p_danuri=orb['danuri']['p_operational_2028'],
                            high_latitude_note='incidence >= 60 deg year-round at |lat| >= 60' if abs(scn['lat']) >= 60 else '')
    # Monte Carlo per strategy
    mc_sc = dict(mass_kg=phys['mass_kg'], v_km_s=phys['v_km_s'], sigma_along_km=phys['sigma_along_km'], sigma_cross_km=phys['sigma_cross_km'], illum_for_eye=es.illum_frac, sunlit_site=bool(inc0 < 90), p_terrain=p_terr)
    month = t_imp.month
    card['mc'] = {}
    for strat in cfg['strategies']:
        stations = build_stations(strat, geom)
        for prior in ['slow-impact-wide', 'v3-scaled']:
            r = MC.run(mc_sc, stations, n=NMC, eta_prior=prior, month=month)
            r['n_stations'] = len(stations)
            card['mc'][f'{strat}|{prior}'] = r
    # public assessment
    peakV_med = card['mc']['B_global_science|slow-impact-wide']['peakV_median']
    card['public'] = dict(peakV_median=peakV_med, naked_eye_threshold=float(D.naked_eye_threshold_mag(0.3, es.illum_frac, 'none')),
                          binocular_threshold=float(D.naked_eye_threshold_mag(0.3, es.illum_frac, 'binoculars')), eyepiece20cm_threshold=float(D.naked_eye_threshold_mag(0.3, es.illum_frac, 'telescope20cm')),
                          phone_standalone_limit=float(D.limiting_magnitude(D.phone_instrument('standalone'), D.total_background_sb('broad', es.illum_frac, 10, -20), 8 / D.phone_processing_penalty('standalone'))),
                          phone_afocal20cm_limit=float(D.limiting_magnitude(D.phone_instrument('afocal'), D.total_background_sb('broad', es.illum_frac, 10, -20), 8 / D.phone_processing_penalty('afocal'))))
    json.dump(card, open(f'{outdir}/{scn["id"]}.json', 'w'), indent=1, default=float)
    # figure: Earth coverage + disk view
    fig = plt.figure(figsize=(13, 4.8)); ax1 = fig.add_axes([0.04, 0.1, 0.6, 0.8]); ax2 = fig.add_axes([0.67, 0.1, 0.31, 0.8])
    cmap = plt.matplotlib.colors.ListedColormap(['#f4f4f2', '#cde2fb', '#5598e7', '#0d366b'])
    ax1.imshow(cls, extent=(-180, 180, -90, 90), origin='lower', cmap=cmap, vmin=-0.5, vmax=3.5, interpolation='nearest', aspect='auto')
    P.coastlines(ax1, '110m'); P.country_outline(ax1, 'Turkey', color='#e34948', lw=1.0)
    for s in sites:
        g = geom[s['id']]; ax1.plot(s['lon'], s['lat'], marker='o' if g['available'] else 'x', ms=4, color='#eb6834' if g['available'] else '#9a9994', mec='k', mew=0.3)
    ax1.set_xlim(-180, 180); ax1.set_ylim(-90, 90); ax1.set_xlabel('longitude'); ax1.set_ylabel('latitude')
    from matplotlib.patches import Patch
    ax1.legend(handles=[Patch(color='#f4f4f2', label='Moon below horizon (online only)'), Patch(color='#cde2fb', label='Moon up (daylight/twilight or point hidden)'),
                        Patch(color='#5598e7', label='public practical: Moon>15 deg, Sun<-6 deg, point visible'), Patch(color='#0d366b', label='facility grade: Moon>20 deg, Sun<-12 deg')],
               loc='upper center', bbox_to_anchor=(0.5, -0.12), fontsize=6.5, ncol=2)
    ax1.set_title(f"{scn['id']}: Earth coverage at {scn['epoch_utc']} UTC ({card['epoch_istanbul']}) - dots: configured sites (orange = available)", loc='left')
    # disk view with sunlit mask and point
    la, lo, _, _ = Gd.healpix_grid(64); em, inc = S.surface_classes(es.r_moon, es.r_sun, es.M, la, lo)
    vals = np.where(inc < 90, 1.0, 0.0)
    P.earth_view(ax2, vals, 64, es.subearth_lon, es.subearth_lat, title=f"Moon at {scn['epoch_utc'][:16]} UTC: illuminated {es.illum_frac*100:.0f} %", cmap=plt.matplotlib.colors.ListedColormap(['#2b2b2b', '#f0e6c8']), vmin=0, vmax=1, features=True)
    la0, lo0 = np.radians(es.subearth_lat), np.radians(es.subearth_lon); lar, lor = np.radians(scn['lat']), np.radians(scn['lon'])
    if np.sin(la0) * np.sin(lar) + np.cos(la0) * np.cos(lar) * np.cos(lor - lo0) > 0:
        xg = np.cos(lar) * np.sin(lor - lo0); yg = np.cos(la0) * np.sin(lar) - np.sin(la0) * np.cos(lar) * np.cos(lor - lo0)
        ax2.plot(xg, yg, marker='*', ms=14, color='#e34948', mec='k'); ax2.text(xg + 0.05, yg - 0.08, 'hypothetical\nimpact point', color='#e34948', fontsize=7)
    else:
        ax2.text(0, 0, 'impact point on far side\n(not visible)', ha='center', color='#e34948', fontsize=8)
    P.evidence_tag(fig, 'HYPOTHETICAL SCENARIO - computed geometry (DE421); not an AYAP-1 prediction')
    P.savefig(fig, f'fig_scenario_{scn["id"]}_coverage')
    mcB = card['mc']['B_global_science|slow-impact-wide']; mcA = card['mc']['A_turkiye_priority|slow-impact-wide']; mcC = card['mc']['C_public_participation|slow-impact-wide']
    print(f"{scn['id']} done {time.time()-tic:.0f}s | avail {len(avail_ids)} sites (TR {len(card['turkish_sites_available'])}) | em {em0:.1f} inc {inc0:.1f} | pop public {pop[2]/1e9:.2f} bn | "
          f"P(any) A {mcA['p_any']:.2f} B {mcB['p_any']:.2f} C {mcC['p_any']:.2f} | P(conf) B {mcB['p_confirmed']:.2f} | P(obvious) B {mcB['p_obvious_any']:.2f} | peakV med {mcB['peakV_median']:.1f} ({mcB['peakV_p10']:.1f}-{mcB['peakV_p90']:.1f}) | eyepiece {mcB['p_eyepiece_witness']:.3f}")
