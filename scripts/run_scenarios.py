"""Scenario pipeline (release 2). For each hypothetical scenario (config/scenarios.yaml):

* times: `epoch_utc` is the impact (emission) time at the lunar surface; each station's geometry uses the lunar state at
  that time and the observer at its own photon reception time (one-way light time, 1.2-1.4 s);
* exact geocentric geometry (observer vector = 0), per-station geometry with time derivatives and Jacobians, the shared
  operational availability (Moon/Sun limits and seasonal closures), exact distance to visible sunlit terrain;
* reachability as a conditional statement (planes containing the point at the epoch, the fraction of random polar
  planes within the cross-track tolerances, timing granularity);
* terrain: no real DEM was obtainable, so only an illustrative synthetic-relief sensitivity range is used;
* flash magnitudes (true band peak, exposure averages), the laboratory-trend extrapolation as a separate case;
* phase-space plume with the Housen & Holsapple (2011) domain respected ('cannot determine' outside it), crater envelope;
* settlement population sums (exact coordinates, agglomeration sensitivity);
* event-level network Monte Carlo for strategies A/B/C on common simulated events, two eta_vis priors and, for S1 and
  S11, two alternative temperature priors;
* orbiter follow-up stated as assumptions and precedents only.
Writes outputs/scenarios/<id>.json and fig_scenario_<id>_coverage."""
import sys, os, json, yaml, numpy as np, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
from astropy.time import Time
import matplotlib.pyplot as plt
from ayap1obs import geometry as G, ephem as E, impact as I, detect as D, terrain as T, montecarlo as MC, population as Pp, plotting as P, reachability as Rr, grid as Gd, screening as S, plume as PL, orbiters as Orb
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml')); fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml'))
dom = yaml.safe_load(open(f'{root}/config/domain.yaml')); CR = dom['criteria']
templates = MC.load_templates()
outdir = f'{root}/outputs/scenarios'
only = sys.argv[1:]
N_OUTER = int(os.environ.get('MC_OUTER', '200')); N_INNER = int(os.environ.get('MC_INNER', '600'))
WEATHER_SENS = {'S1', 'S11'}                                       # spring and winter scenarios (re-audit ST-N04)
WEATHER_VARIANTS = {'flat season': dict(seasonality=False), 'L = 250 km': dict(L_km=250.0), 'L = 1000 km': dict(L_km=1000.0),
                    'prior spread x0.5': dict(weather_spread=0.5), 'prior spread x2': dict(weather_spread=2.0)}
INNER_CONVERGENCE = (150, 600, 2400)                               # S1, fixed outer draws (re-audit ST-01)
ETA_PRIORS = ['wide', 'v-scaled']
T0_SENSITIVITY = {'S1': ['cool', 'narrow'], 'S11': ['cool', 'narrow']}
PUBLIC_SITE = 'IST'
site_by_id = {s['id']: s for s in sites}

class Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        if isinstance(o, set): return sorted(o)
        return super().default(o)

def clean(x):
    """Replace non-finite floats by None so that the JSON is standard."""
    if isinstance(x, dict): return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, (float, np.floating)): return float(x) if np.isfinite(x) else None
    return x

# ---------------------------------------------------------------- stations: one union, strategies index into it
def build_union():
    union, keys, strategies = [], {}, {}
    for strat, st_cfg in cfg['strategies'].items():
        idx, streaming = [], set()
        for s in sites:
            if st_cfg['include_groups'] != 'all' and s['group'] not in st_cfg['include_groups']:
                continue
            tlist = list(cfg['site_templates'].get(s['id'], []))
            if st_cfg.get('add_amateur_everywhere') and 'amateur_class' not in tlist:
                tlist.append('amateur_class')
            for tname in tlist:
                if st_cfg['include_templates'] != 'all' and tname not in st_cfg['include_templates']:
                    continue
                key = f"{s['id']}:{tname}"
                if key not in keys:
                    keys[key] = len(union); t = templates[tname]
                    union.append(MC.Station(s, tname, t, t['p_ready']))
                idx.append(keys[key])
                if key in st_cfg.get('streaming', []):
                    streaming.add(keys[key])
        strategies[strat] = dict(stations=idx, streaming=streaming)
    return union, keys, strategies
UNION, KEYS, STRATEGIES = build_union()

# ---------------------------------------------------------------- illustrative synthetic terrain (computed once)
HZ = T.synthetic_horizon_statistics(n=150, seed=7)
np.savez(f'{outdir}/synthetic_horizons.npz', **{k.split()[0]: v for k, v in HZ.items()})

def p_random_polar_plane(lat, delta_deg):
    """Fraction of polar planes (uniform node) that pass within delta of a point at latitude lat at a given epoch."""
    c = np.cos(np.radians(lat)); sd = np.sin(np.radians(delta_deg))
    return 1.0 if c <= sd else float(2 * np.arcsin(sd / c) / np.pi)

PLUME_V_FLOOR = 1.0          # m/s: slowest ejecta modelled (they rise 0.3 m and land within ~0.6 m of the rim)
PLUME_GRAINS = ('regolith', 'coarse', 'fine-rich'); PLUME_PPHI = (0.01, 0.03, 0.1); PLUME_KAPPA = (0.2, 0.5, 1.0)

def plume_cases(es, lat, lon, m, v, angle, observers, bkg, ext, h_need_km):
    """Phase-space plume (release 2.1) for the bracketing rules, impactor models and HH2011 parameter sets. Population:
    all in-domain ejecta from PLUME_V_FLOOR upwards; for a site whose ground is dark the slowest speed is the vertical
    launch speed to the height where parcels become sunlit and visible (slower ejecta can never be lit), declared in
    each case. Default reporting: regolith grains, p Phi 0.03, dust/ground contrast kappa 0.2 (dust seen against sunlit
    ground), subtraction systematic 1e-3 and 1e-2; sensitivities: grains, p Phi, kappa."""
    site_unit = E.latlon_to_vec(lat, lon, 1.0) @ es.M
    sun_unit = (es.r_sun - es.r_moon); sun_unit /= np.linalg.norm(sun_unit)
    h = max(h_need_km, 0.0) * 1e3 if np.isfinite(h_need_km) else np.inf
    v_need = float(np.sqrt(2 * PL.MU_MOON * h / (PL.R_MOON_M * (PL.R_MOON_M + h)))) if np.isfinite(h) else np.inf
    v_lo = max(PLUME_V_FLOOR, 0.95 * v_need) if np.isfinite(v_need) else np.inf
    rows = []
    for rule in ('vertical-component', 'vertical-equivalent'):
        for model in PL.IMPACTOR_MODELS:
            plist = ['sand', 'sand/fly ash', 'perlite/sand'] if (rule == 'vertical-equivalent' and model == 'dense parts + hollow bus') else ['sand']
            for params in plist:
                vmax = PL.domain_vmax_sc(m, v, angle, model, rule, params)
                row = dict(rule=rule, impactor=model, params=params, U_eff_m_s=float(I.effective_speed(v, angle, rule)), vmax_domain_m_s=vmax,
                           v_needed_m_s=v_need, observers={})
                if not np.isfinite(v_need):
                    row['status'] = 'plume cannot rise into view (no finite clearance height)'; rows.append(row); continue
                if v_need > vmax:
                    row['status'] = f'cannot determine: reaching sunlight/visibility needs > {v_need:.0f} m/s (vertical launch), above the scaling-domain maximum {vmax:.0f} m/s'
                    rows.append(row); continue
                res = PL.plume_simulation(site_unit, sun_unit, observers, m, v, angle, model=model, rule=rule, params=params, v_lo=v_lo, v_floor=PLUME_V_FLOOR)
                if not res['ok']:
                    row['status'] = 'cannot determine: ' + res['reason']; rows.append(row); continue
                row['status'] = 'within-domain estimate (ejecta faster than the domain maximum are not modelled)'
                row.update(v_lo_m_s=res['v_lo'], M_selected_kg=res['M_selected_kg'], M_domain_kg=res['M_domain_kg'],
                           population=f"in-domain ejecta from {res['v_lo']:.1f} m/s to {res['vmax']:.0f} m/s ({res['M_selected_kg']:.3g} of {res['M_domain_kg']:.3g} kg in the domain)")
                row['M_fast_total_kg'] = res['M_selected_kg']
                for name, ob in res['observers'].items():
                    out = {}
                    combos = [dict(grains='regolith', pPhi=0.03, kappa=PLUME_KAPPA[0], sys_frac=1e-3), dict(grains='regolith', pPhi=0.03, kappa=PLUME_KAPPA[0], sys_frac=1e-2)]
                    combos += [dict(grains=g_, pPhi=0.03, kappa=PLUME_KAPPA[0], sys_frac=1e-3) for g_ in PLUME_GRAINS]
                    combos += [dict(grains='regolith', pPhi=q, kappa=PLUME_KAPPA[0], sys_frac=1e-3) for q in PLUME_PPHI]
                    combos += [dict(grains='regolith', pPhi=0.03, kappa=q, sys_frac=1e-3) for q in PLUME_KAPPA]
                    combos += [dict(grains='fine-rich', pPhi=PLUME_PPHI[-1], kappa=PLUME_KAPPA[-1], sys_frac=1e-3)]      # optimistic corner of the declared ranges
                    rs = PL.plume_detectability_multi(res, name, bkg[name], combos, ext_mag=ext[name])
                    for sys_f, d in zip((1e-3, 1e-2), rs[:2]):
                        k = int(np.argmax(d['snr']))
                        out[f'sys{sys_f:g}'] = dict(snr_max=float(d['snr'][k]), t_snr_max_s=float(d['t_start'][k]), contrast_max=float(d['contrast'].max()))
                    d = rs[0]
                    out['camera'] = dict(t_exposure_s=d['t_exposure_s'], n_frames=d['n_frames'], usable=d['usable'])
                    out['grains_sys0.001'] = {g_: float(r_['snr'].max()) for g_, r_ in zip(PLUME_GRAINS, rs[2:5])}
                    out['pphi_sys0.001'] = {f'{q:g}': float(r_['snr'].max()) for q, r_ in zip(PLUME_PPHI, rs[5:8])}
                    out['M_vis_max_kg'] = float(ob['M_vis'].max()); out['t_M_vis_max_s'] = float(res['times'][int(np.argmax(ob['M_vis']))])
                    out['M_contrast_class_max_kg'] = float(ob['M_con'].max())
                    if out['M_contrast_class_max_kg'] > 0:
                        out['kappa_sys0.001'] = {f'{q:g}': float(r_['snr'].max()) for q, r_ in zip(PLUME_KAPPA, rs[8:11])}
                    out['optimistic_corner_sys0.001'] = dict(snr_max=float(rs[11]['snr'].max()), assumptions=f'fine-rich grains, p Phi {PLUME_PPHI[-1]:g}, kappa {PLUME_KAPPA[-1]:g}')
                    out['tau_max'] = d['tau_max']; out['background_sb_V'] = float(bkg[name]); out['extinction_mag'] = float(ext[name])
                    row['observers'][name] = out
                rows.append(row)
    return rows

t_ref = Time(fam['reference_epoch_utc'], scale='utc')
main_fs = fam['family_sets']['main']; main_nodes = np.arange(main_fs['node_start'], main_fs['node_stop'], main_fs['node_step'], dtype=float)
for si, scn in enumerate(cfg['scenarios']):
    if only and scn['id'] not in only:
        continue
    tic = time.time()
    phys = cfg['physics'][scn['physics']]
    lat, lon = float(scn['lat']), float(scn['lon'])
    t_imp = Time(scn['epoch_utc'], scale='utc'); es = G.epoch_state(t_imp); month = t_imp.to_datetime().month
    em0, inc0 = (float(x[0]) for x in G.geocentric_surface_geometry(es, lat, lon))
    m_mean = float(np.mean(phys['mass_kg'])); v = float(phys['v_km_s']); angle = float(phys['angle_deg'])
    card = dict(id=scn['id'], name=scn['name'], cls=scn['class'], hypothetical=True, note='HYPOTHETICAL TEST POINT - not an official AYAP-1 target',
                lat=lat, lon=lon, epoch_utc=scn['epoch_utc'],
                epoch_definition='epoch_utc is the impact (emission) time at the lunar surface; photons reach each station 1.2-1.4 s later (per-site reception times below)',
                impact_utc=t_imp.utc.isot, impact_tdb=t_imp.tdb.isot,
                epoch_istanbul=(t_imp.to_datetime() + dt.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M (UTC+3)'),
                physics=phys, rationale=scn['rationale'], region=str(Gd.region_label(np.array([lat]), np.array([lon]))[0]),
                moon=dict(subsolar_lon=es.subsolar_lon, subsolar_lat=es.subsolar_lat, subearth_lon=es.subearth_lon, subearth_lat=es.subearth_lat,
                          phase_angle=es.phase_angle, illum_frac=es.illum_frac, elongation=es.elongation, distance_km=es.distance_km, light_time_geocentric_s=es.light_time_s))
    # waxing: the illuminated fraction increases over the next hour
    card['moon']['waxing'] = bool(G.epoch_state(Time(t_imp.utc.jd + 1 / 24, format='jd', scale='utc')).illum_frac > es.illum_frac)
    card['geometry'] = dict(observer='geocentre (zero vector)', emission_geocentric=em0, incidence=inc0, sunlit=bool(inc0 < 90), earth_elev_local=90 - em0, sun_elev_local=90 - inc0,
                            shadow_height_km=float(G.shadow_height_km(inc0)), limb_clearance_km=float(T.sphere_clearance_height_km(es, np.zeros(3), lat, lon)),
                            plume_emission_ok=bool(em0 < CR['plume_sunlit']['max_emission_deg'] + 1))
    # ---- reachability (conditional)
    planes = Rr.planes_through_point(t_imp.utc.jd, lat, lon, 90.0, t_ref.utc.jd)
    node = planes[0]['node_ref_deg'] % 180.0 if planes else np.nan
    dn = np.abs(((main_nodes - node) + 90.0) % 180.0 - 90.0)
    card['reachability'] = dict(status='conditional', planes=planes, required_node_mod180_deg=float(node), nearest_family_node_deg=float(main_nodes[np.argmin(dn)]),
                                offset_from_family_grid_deg=float(dn.min()),
                                p_random_polar_plane_within={f'{d:g}': p_random_polar_plane(lat, d) for d in fam['cross_track_tolerance_deg']},
                                plane_change_dv_m_s={f'{d:g}': float(Rr.plane_change_dv(d)) for d in fam['cross_track_tolerance_deg']},
                                orbital_period_min=float(Rr.period_s(fam['altitude_km']) / 60.0),
                                note=('the impact is possible at this epoch only if the orbit plane is within the cross-track tolerance of the required node AND the orbital phase '
                                      'puts the spacecraft over the point; given the plane, passes over the latitude recur every orbital period. '
                                      + ('Near the pole the point lies within a few degrees of many polar planes, so it is reachable on every orbit only for that subset of planes.' if abs(lat) > 80 else '')))
    # ---- per-site geometry (lunar state at impact, observer at reception), shared operational availability
    geom = {}
    sig_t = phys['sigma_t_min']; sig_pos = max(phys['sigma_along_km'], phys['sigma_cross_km'])
    for s in sites:
        obs = G.Observer(s['id'], s['lon'], s['lat'], s['alt'])
        g = G.station_geometry(t_imp, obs, lat, lon)
        sky_ok, oper = S.observer_availability(g['moon_alt'], g['sun_alt'], month, s, CR['observer'])
        closed = month in s.get('closed_months', [])
        o_rec = E.observer_gcrs(s['lon'], s['lat'], s['alt'], Time(g['t_reception_utc'], scale='utc'))
        dsun = G.dist_to_sunlit_arcmin(es, o_rec, lat, lon) if (g['visible'] and g['moon_alt'] > 0) else 999.0
        slack_em = 4 * (abs(g['d_emission']) * sig_t + (abs(g['J_em'][0]) + abs(g['J_em'][1])) * sig_pos)
        candidate = (g['emission'] - slack_em < 90) and (g['moon_alt'] + 4 * abs(g['d_moon_alt']) * sig_t >= CR['observer']['min_moon_alt_deg']) and \
                    (g['sun_alt'] - 4 * abs(g['d_sun_alt']) * sig_t <= CR['observer']['max_sun_alt_deg']) and not closed
        lmst = (t_imp.to_datetime() + dt.timedelta(hours=s['lon'] / 15.0)).strftime('%H:%M')
        g.update(sky_ok=bool(sky_ok), operational=bool(oper), closed=bool(closed), available=bool(oper and g['visible']), candidate=bool(candidate),
                 dist_sunlit_arcmin=float(dsun), airmass=float(G.airmass(g['moon_alt'])), twilight=int(G.twilight_class(g['sun_alt'])),
                 local_time=((t_imp.to_datetime() + dt.timedelta(hours=3)).strftime('%H:%M') + ' Istanbul (UTC+3)') if s['group'] == 'turkiye' else (lmst + ' local mean solar time'))
        geom[s['id']] = g
    card['sites'] = geom
    avail_ids = [k for k, g in geom.items() if g['available']]
    card['n_sites_available'] = len(avail_ids); card['sites_available'] = avail_ids
    card['turkish_sites_available'] = [k for k in avail_ids if site_by_id[k]['group'] == 'turkiye']
    card['sites_closed'] = [k for k, g in geom.items() if g['closed']]
    # ---- terrain (illustrative synthetic sensitivity only)
    p_vis = {k: T.p_visible_given_emission(hz, em0) for k, hz in HZ.items()} if em0 < 90 else {k: 0.0 for k in HZ}
    p_lo, p_hi = min(p_vis.values()), max(p_vis.values())
    card['terrain'] = dict(dem='none: no LOLA product could be obtained in the analysis environment, so no site-specific terrain test is made',
                           synthetic_relief_p_visible=p_vis, p_terrain_range=[p_lo, p_hi],
                           synthetic_relief_levels={k: v for k, v in T.RELIEF.items()},
                           note='illustrative sensitivity: Earth above the horizon of 150 synthetic Gaussian-relief patches per declared relief level at the geocentric emission angle; not a validated lunar prior and not a bound (real terrain can raise or lower the horizon)')
    # ---- flash magnitudes
    E_k = I.kinetic_energy(m_mean, v); dist_m = es.distance_km * 1e3
    card['energy'] = dict(E_k_J=E_k, mass_mean_kg=m_mean, v_km_s=v, angle_deg=angle, tnt_equiv_kg=E_k / 4.184e6)
    tab = []
    for eta in [1e-6, 1e-5, 1e-4, 1e-3]:
        for T0 in [2000.0, 3000.0, 4500.0]:
            fm = I.FlashModel(E_k, eta, T0, float(I.floor_temperature(T0)), 0.5, 0.5)
            eps = fm.radiative_efficiency()
            row = dict(eta_vis=eta, T0=T0, tau_s=0.5, radiative_efficiency=eps, energy_consistent=bool(eps <= 0.1))
            for b in ['V', 'Rc', 'Ic', 'Ks']:
                mpk, tpk = fm.peak_magnitude(b, dist_m, return_time=True); row[f'{b}_peak'] = round(mpk, 2); row[f'{b}_t_peak_s'] = round(tpk, 3)
            row['Rc_avg_first_23ms'] = round(fm.exposure_averaged_magnitude('Rc', 0.023, distance_m=dist_m), 2)
            row['Ic_avg_first_23ms'] = round(fm.exposure_averaged_magnitude('Ic', 0.023, distance_m=dist_m), 2)
            row['Ks_avg_first_2s'] = round(fm.exposure_averaged_magnitude('Ks', 2.0, distance_m=dist_m), 2)
            tab.append(row)
    card['flash_magnitudes'] = tab
    card['flash_magnitude_note'] = 'unocculted source-equivalent magnitudes at the geocentric distance (not apparent magnitudes if the point is occulted or behind the limb)'
    eta_lab = float(I.lab_trend_eta(v)); fm_lab = I.FlashModel(E_k, eta_lab, 3000.0, float(I.floor_temperature(3000.0)), 0.5, 0.5)
    card['lab_trend'] = dict(eta_vis=eta_lab, V_peak=fm_lab.peak_magnitude('V', dist_m), Rc_peak=fm_lab.peak_magnitude('Rc', dist_m),
                             note='Swift et al. (2011) laboratory fit eta = 1.5e-3 exp(-(9.3/v)^2) for Pyrex into regolith simulant at 2.4-5.75 km/s, extrapolated below its tested range; T0 3000 K, tau 0.5 s. Under this case the flash is far below every detection limit.')
    # ---- plume (phase-space model; HH2011 domain respected)
    h_shadow = float(G.shadow_height_km(inc0)); H_clear = card['geometry']['limb_clearance_km']
    h_need = max(h_shadow, H_clear) if np.isfinite(H_clear) else np.inf
    tug = site_by_id['TUG']; g_tug = geom['TUG']
    o_tug = E.observer_gcrs(tug['lon'], tug['lat'], tug['alt'], Time(g_tug['t_reception_utc'], scale='utc'))
    observers = {'geocentre': -es.r_moon * 1e3, 'TUG': (o_tug - es.r_moon) * 1e3}
    dsun_geo = G.dist_to_sunlit_arcmin(es, np.zeros(3), lat, lon) if em0 < 90 else 999.0
    ext_tug = float(D.extinction_mag('V', MC.kasten_young(max(g_tug['moon_alt'], 1.0)), tug['alt']))
    bkg = {'geocentre': float(D.total_background_sb('V', es.illum_frac, dsun_geo, -18.0, 3e-3, 0.2, 0.0, inc0 < 90, inc0)),
           'TUG': float(D.total_background_sb('V', es.illum_frac, g_tug['dist_sunlit_arcmin'], g_tug['sun_alt'], 3e-3, ext_tug, 0.0, inc0 < 90, inc0))}
    run_plume = em0 < 120.0
    card['plume'] = dict(shadow_height_km=h_shadow, clearance_height_km=H_clear if np.isfinite(H_clear) else None, height_needed_km=h_need if np.isfinite(h_need) else None,
                         emission_criterion_ok=card['geometry']['plume_emission_ok'],
                         regime=('plume over sunlit ground (low contrast, LCROSS-like)' if inc0 < 90 else
                                 ('sunlit plume over dark ground possible' if h_shadow < 30 else 'sunlight only far above the surface')),
                         instrument=PL.CAMERA_1M['label'] + '; 1-s integration windows; seeing 1.5 arcsec; source and background extincted; background-subtraction systematic 1e-3 and 1e-2 of the background',
                         defaults='regolith grains, p Phi 0.03, dust/sunlit-ground contrast kappa 0.2',
                         cases=plume_cases(es, lat, lon, m_mean, v, angle, observers, bkg, {'geocentre': 0.0, 'TUG': ext_tug}, h_need) if run_plume else [],
                         note=('Housen & Holsapple (2011) point-source scaling with its domain [n1 a, n2 R]; two oblique-impact rules bracket a grazing impact by a hollow spacecraft, '
                               'for which no validated rule exists; impactor bulk density is a calibration choice (the LCROSS like-for-like check favours ~400 kg/m3), not a validation.'))
    # ---- crater
    env = I.crater_rim_diameter_envelope(m_mean, v, angle)
    card['crater'] = dict(rim_diameter_m=env, angular_size_arcsec=206265 * env['all'][1] / 1e3 / es.distance_km, lroc_nac_pixels_median=env['all'][1] / orb['lro']['nac_resolution_m'],
                          note='envelope over the Holsapple (LPI) and Housen & Holsapple (2011) parameter sets, bulk densities 150/400/1000 kg/m3 and the two oblique-impact rules; neither rule is validated for a hollow spacecraft at grazing incidence')
    # ---- latency
    lts = [g['light_time_s'] for g in geom.values() if g['visible']]
    card['latency'] = dict(light_time_geocentric_s=es.light_time_s, light_time_station_range_s=[min(lts), max(lts)] if lts else None,
                           telemetry_note='direct-to-Earth S/X-band: the last frames before loss of signal arrive ~1.3 s after emission, plus ground processing (assumed 5-60 s); no relay, so no post-impact telemetry',
                           broadcast_note='broadcast (encoding/streaming) latency is separate from the light time: assumed 10-60 s',
                           rapid_replay_min=[5, 60], confirmed_detection_h=[1, 24])
    # ---- settlement population sums
    cov = Pp.coverage_at_epoch(t_imp, lat, lon); cls_map = Pp.classify_coverage(cov)
    card['population'] = Pp.settlement_sums(t_imp, lat, lon, cov)
    # ---- orbiters: assumptions, computed LRO illumination seasons and the Danuri disposal plan
    lro = orb['lro']; dan = orb['danuri']
    seas = json.load(open(f'{root}/outputs/tables/orbiter_seasons.json'))
    season_status = lambda wins: Orb.season_status(t_imp.to_datetime(), wins)
    dan_ok = t_imp.to_datetime() <= dt.datetime.strptime(dan['available_until'], '%Y-%m-%d')
    card['orbiters'] = dict(lro=dict(p_operational_assumed=lro['p_operational_2028'], p_operational_sensitivity=lro['p_operational_sensitivity'],
                                     p_note='assumed probability that LRO is still operating in 2028 (scenario input, not measured; not a probability of imaging the crater)',
                                     latency_summary=lro['latency_precedents']['summary'],
                                     latency_note='heuristic from a small, selected precedent sample (impacts only; first documented image, release counted from the event); not a calibrated forecast for this site',
                                     low_sun_season=season_status(seas['lro']['low_sun']), near_noon_season=season_status(seas['lro']['near_noon']),
                                     season_note=Orb.SEASON_NOTE),
                            danuri=dict(planned_impact=dan['planned_impact'], available_in_baseline=bool(dan_ok),
                                        p_operational_assumed=dan['p_operational_before_planned_end'] if dan_ok else dan['p_operational_after_planned_end'],
                                        p_continued_operation_sensitivity=None if dan_ok else dan['continued_operation_sensitivity'],
                                        note='KASA plans a lunar impact in March 2028 (press release 10 Feb 2025); after it, Danuri follow-up exists only in the changed-plan sensitivity'),
                            high_latitude_note='at |lat| >= 60 deg the incidence stays high most of the year, but the lunar sub-solar latitude and terrain still decide whether the site is lit' if abs(lat) >= 60 else '')
    # ---- event-level Monte Carlo
    for st in UNION:
        st.geometry = geom[st.site['id']]
    pub_key = f'{PUBLIC_SITE}:amateur_class'
    pub = dict(geom[PUBLIC_SITE]); pub.update(station_index=KEYS.get(pub_key), alt=site_by_id[PUBLIC_SITE]['alt'])
    sc_mc = dict(month=month, mass_kg=phys['mass_kg'], v_km_s=v, sigma_t_min=phys['sigma_t_min'], sigma_along_km=phys['sigma_along_km'], sigma_cross_km=phys['sigma_cross_km'],
                 p_terrain=(p_lo, p_hi), distance_km=es.distance_km, public_geometry=pub)
    card['mc'] = {}
    seed = 20261005 + 1000 * si
    for ep in ETA_PRIORS:
        card['mc'][f'{ep}|broad'] = MC.simulate(sc_mc, UNION, STRATEGIES, eta_prior=ep, T0_prior='broad', n_outer=N_OUTER, n_inner=N_INNER, seed=seed, public_site=PUBLIC_SITE)
    for T0p in T0_SENSITIVITY.get(scn['id'], []):
        card['mc'][f'wide|{T0p}'] = MC.simulate(sc_mc, UNION, STRATEGIES, eta_prior='wide', T0_prior=T0p, n_outer=N_OUTER, n_inner=N_INNER, seed=seed, public_site=PUBLIC_SITE)
    pick = lambda r, outs: {st: {o: {k: r['strategies'][st][o][k] for k in ('p', 'mc_se', 'ci95', 'outer_p05', 'outer_p95', 'outer_raw_p05', 'outer_raw_p95')}
                                 for o in outs} for st in STRATEGIES}
    if scn['id'] in WEATHER_SENS:                                       # weather-model sensitivities, wide|broad
        card['mc_weather_sensitivity'] = {v: pick(MC.simulate(sc_mc, UNION, STRATEGIES, eta_prior='wide', T0_prior='broad', n_outer=N_OUTER, n_inner=N_INNER,
                                                              seed=seed, public_site=PUBLIC_SITE, **kw), ('any', 'two_indep', 'confirmed'))
                                          for v, kw in WEATHER_VARIANTS.items()}
    if scn['id'] == 'S1':                                               # convergence of the outer ranges in the inner sample size
        card['mc_inner_convergence'] = {str(ni): pick(MC.simulate(sc_mc, UNION, STRATEGIES, eta_prior='wide', T0_prior='broad', n_outer=N_OUTER, n_inner=ni,
                                                                  seed=seed, public_site=PUBLIC_SITE), ('any', 'two_indep'))
                                        for ni in INNER_CONVERGENCE}
    card['strategies'] = {k: dict(description=cfg['strategies'][k]['description'], stations=[UNION[i].key for i in v_['stations']],
                                  streaming=[UNION[i].key for i in sorted(v_['streaming'])]) for k, v_ in STRATEGIES.items()}
    card['mc_settings'] = dict(n_outer=N_OUTER, n_inner=N_INNER, seed=seed, detection_snr=MC.DET_SNR, obvious_snr=MC.OBV_SNR, dual_camera_snr=MC.CONF_SNR, cluster_km=MC.CLUSTER_KM)
    # ---- public view
    g_pub = geom[PUBLIC_SITE]
    bk_phone = float(D.total_background_sb('broad', es.illum_frac, g_pub['dist_sunlit_arcmin'], g_pub['sun_alt'], 3e-3, 0.0))
    card['public'] = dict(site=PUBLIC_SITE, visual=card['mc']['wide|broad']['visual'],
                          phone_standalone_limit_broad=float(D.limiting_magnitude(D.phone_instrument('standalone'), bk_phone, 8 / D.phone_processing_penalty('standalone'))),
                          phone_afocal20cm_limit_broad=float(D.limiting_magnitude(D.phone_instrument('afocal'), bk_phone, 8 / D.phone_processing_penalty('afocal'))),
                          phone_note='steady-source limits in the unfiltered (broad) CMOS band, not V magnitudes; flash detection also depends on the frame rate and processing')
    json.dump(clean(card), open(f'{outdir}/{scn["id"]}.json', 'w'), indent=1, cls=Enc)
    # ---- figure: Earth coverage + Moon as seen from the geocentre (celestial north up)
    fig = plt.figure(figsize=(13, 4.8)); ax1 = fig.add_axes([0.04, 0.1, 0.6, 0.8]); ax2 = fig.add_axes([0.67, 0.1, 0.31, 0.8])
    cmap = plt.matplotlib.colors.ListedColormap(['#f4f4f2', '#cde2fb', '#5598e7', '#0d366b'])
    ax1.imshow(cls_map, extent=(-180, 180, -90, 90), origin='lower', cmap=cmap, vmin=-0.5, vmax=3.5, interpolation='nearest', aspect='auto')
    P.coastlines(ax1, '110m'); P.country_outline(ax1, 'Turkey', color='#e34948', lw=1.0)
    for s in sites:
        g = geom[s['id']]; ax1.plot(s['lon'], s['lat'], marker='o' if g['available'] else 'x', ms=4, color='#eb6834' if g['available'] else '#9a9994', mec='k', mew=0.3)
    ax1.set_xlim(-180, 180); ax1.set_ylim(-90, 90); ax1.set_xlabel('longitude'); ax1.set_ylabel('latitude')
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax1.legend(handles=[Patch(color='#f4f4f2', label='Moon below horizon'), Patch(color='#cde2fb', label='Moon up (daylight/twilight or point hidden)'),
                        Patch(color='#5598e7', label='public practical: Moon>15 deg, Sun<-6 deg, point visible'), Patch(color='#0d366b', label='facility grade: Moon>20 deg, Sun<-12 deg'),
                        Line2D([], [], ls='none', marker='o', ms=4, color='#eb6834', mec='k', mew=0.3, label='configured site, available (incl. closures)'),
                        Line2D([], [], ls='none', marker='x', ms=4, color='#9a9994', mec='k', mew=0.3, label='configured site, not available')],
               loc='upper center', bbox_to_anchor=(0.5, -0.12), fontsize=6.5, ncol=3)
    ax1.set_title(f"{scn['id']}: Earth coverage at the impact time {scn['epoch_utc'][:16]} UTC ({card['epoch_istanbul'].replace(' (UTC+3)', ' in Türkiye, UTC+3')})", loc='left')
    la, lo, _, _ = Gd.healpix_grid(64); em, inc = S.surface_classes(es.r_moon, es.r_sun, es.M, la, lo)
    P.earth_view(ax2, np.where(inc < 90, 1.0, 0.0), 64, title=f"Moon from Earth's centre: illuminated {es.illum_frac*100:.0f} %",
                 cmap=plt.matplotlib.colors.ListedColormap(['#2b2b2b', '#f0e6c8']), vmin=0, vmax=1, features=True, es=es)
    basis = P.disk_basis(es); xg, yg, vis = P.disk_xy(lat, lon, basis)
    if vis:
        ax2.plot(xg, yg, marker='*', ms=14, color='#e34948', mec='k')
        ax2.text(xg - 0.06 if xg > 0.4 else xg + 0.05, yg - 0.08, 'hypothetical\nimpact point', color='#e34948', fontsize=7, ha='right' if xg > 0.4 else 'left')
    else:
        ax2.text(0, 0, 'impact point on the far side\n(not visible)', ha='center', color='#e34948', fontsize=8)
    P.evidence_tag(fig, 'HYPOTHETICAL SCENARIO - computed geometry (DE421); not an AYAP-1 prediction')
    P.savefig(fig, f'fig_scenario_{scn["id"]}_coverage')
    mw = card['mc']['wide|broad']['strategies']
    print(f"{scn['id']} done {time.time()-tic:.0f}s | avail {len(avail_ids)} (TR {len(card['turkish_sites_available'])}) | em {em0:.1f} inc {inc0:.1f} | "
          f"P(any) A {mw['A_turkiye_priority']['any']['p']:.3f} B {mw['B_global_science']['any']['p']:.3f} C {mw['C_public_participation']['any']['p']:.3f} | "
          f"P(conf) B {mw['B_global_science']['confirmed']['p']:.3f} | peakV {card['mc']['wide|broad']['peakV']['median']:.1f} | plume cases {len(card['plume']['cases'])}", flush=True)
