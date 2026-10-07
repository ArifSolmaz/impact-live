"""Event-level Monte Carlo for network detection probabilities, conditional on the spacecraft reaching the stated
terminal state.

Structure (release 2):
* Outer loop (epistemic, n_outer draws): site clear-sky probabilities, station readiness probabilities, station
  calibration factors, Earthshine level, scattered-light coefficient, background-subtraction systematic, terrain
  visibility probability and the visual field factor.
* Inner loop (event draws per outer draw): flash parameters (mass, speed, eta_vis, T0, tau, with the radiative-energy
  consistency cut), ONE impact time offset and ONE impact location offset shared by all stations, correlated weather,
  readiness, per-station pointing error, per-camera exposure phase and per-camera measurement noise.
* Each station: geometry at the photon reception time (linearised in the time offset), recording window, field of
  view (the shared surface offset projected into that station's sky with its own Jacobian, plus pointing error),
  range-corrected flux, extinction, total background, an exposure shortened if the background would exceed half the
  full well (unavailable if even the shortest exposure saturates), and the best-frame counts obtained by integrating
  the light curve over the actual overlap of each exposure with the flash for a random exposure phase. Synchronised
  dual-camera systems share the phase; independent cameras do not.
* Outcomes: detected (observed SNR >= 8 in any camera), obvious (>= 30), dual-camera validation (both cameras of one
  station >= 15 in the same frame), two independent sites (>= 2 detections more than 100 km apart), confirmed (either
  of the last two), live (obvious at a streaming station), rapid replay (detected at a station with a real-time
  pipeline), Turkish detection.
Strategies are evaluated on the same simulated events (common random numbers), so differences between strategies
are paired. Reported: pooled probabilities with Wilson intervals (Monte Carlo precision), the 5-95 % range of the
conditional probability across outer draws (weather/readiness/calibration/background uncertainty), and the
probability by eta_vis bin (the flash-brightness uncertainty, which dominates).
"""
from __future__ import annotations
import numpy as np, yaml, os
from dataclasses import dataclass, field
from scipy.stats import norm
from . import impact as I, detect as D, weather as W

CLUSTER_KM = 100.0
DET_SNR, OBV_SNR, CONF_SNR = 8.0, 30.0, 15.0

def load_templates():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return yaml.safe_load(open(f'{here}/config/instruments.yaml'))['templates']

@dataclass
class Station:
    site: dict
    template: str
    inst: dict
    p_ready: float
    geometry: dict = None          # filled per scenario (see scripts/run_scenarios.py: station_geometry)
    key: str = ''
    def __post_init__(self):
        self.key = f"{self.site['id']}:{self.template}"
    def instrument(self, band):
        t = self.inst
        return D.Instrument(f"{self.key}:{band}", t['aperture_m'], band, t['pixel_scale_arcsec'], tuple(t['fov_arcmin']), t['exposure_s'], t['frame_time_s'],
                            throughput=t['throughput'], obstruction=t.get('obstruction', 0.15), read_noise_e=t['read_noise_e'], seeing_arcsec=t['seeing_arcsec'],
                            full_well_e=float(t.get('full_well_e', t.get('saturation_e', 6e4))), min_exposure_s=float(t.get('min_exposure_s', 1e-3)),
                            dark_e_s=float(t.get('dark_e_s', 0.01)), n_ref=int(t.get('n_ref', 20)))
    def cameras(self):
        """[(band, sync_group)]: two bands on one dual-camera system are synchronised (one group); a dual-camera system
        with one band (e.g. MIDAS) is modelled as two independent cameras."""
        b = list(self.inst['bands'])
        if self.inst.get('dual_camera', False):
            return [(x, 0) for x in b] if len(b) == 2 else [(b[0], 0), (b[0], 1)]
        return [(b[0], 0)]

def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (float((c - h) / d), float((c + h) / d))

def kasten_young(alt_deg):
    a = np.asarray(alt_deg, float); z = 90.0 - a
    with np.errstate(invalid='ignore', divide='ignore'):
        X = 1.0 / (np.cos(np.radians(z)) + 0.50572 * np.maximum(96.07995 - z, 1e-3) ** -1.6364)
    return np.where(a > 0, X, 40.0)

def clusters_of(stations):
    lat = np.array([s.site['lat'] for s in stations]); lon = np.array([s.site['lon'] for s in stations])
    Dm = W.great_circle_km(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    lab = -np.ones(len(stations), int); c = 0
    for i in range(len(stations)):
        if lab[i] < 0:
            lab[(Dm[i] < CLUSTER_KM) & (lab < 0)] = c; c += 1
    return lab

OUTCOMES = ['any', 'two_indep', 'dual_validated', 'confirmed', 'obvious_any', 'live', 'rapid', 'turkish', 'obvious_turkish']

def simulate(scenario, stations, strategies, eta_prior='wide', T0_prior='broad', n_outer=200, n_inner=150, seed=20261005,
             eps_max=0.1, seasonality=True, L_km=500.0, weather_spread=1.0, es_offset_range=(-0.5, 0.5), k_scat_range=(1e-3, 1e-2),
             sys_range=(1e-3, 1e-2), F_vis_range=(1.4, 24.0), attention=0.5, public_site='IST', record_window_min=15.0,
             pointing_sigma_arcsec=15.0, keep_events=False):
    """Run the event-level simulation for one scenario. `stations`: union of all strategies' stations;
    `strategies`: {name: dict(stations=[indices], streaming=set(indices))}. Returns a results dict."""
    rng = np.random.default_rng(seed)
    sc = scenario; N = n_outer * n_inner
    kk = np.repeat(np.arange(n_outer), n_inner)                         # outer index of each event
    # ---------------- epistemic draws (outer)
    usite_idx, usites = W.unique_sites([s.site for s in stations]) if stations else (np.zeros(0, int), [])
    p_site = W.draw_site_probabilities(usites, sc['month'], rng, n_outer, seasonality, weather_spread) if stations else np.zeros((n_outer, 0))
    p_ready = np.empty((n_outer, len(stations)))
    for j, st in enumerate(stations):
        a, b = W.beta_parameters(st.p_ready, 0.15); p_ready[:, j] = rng.beta(a, b, n_outer)
    cal = np.exp(rng.normal(0.0, 0.3, (n_outer, len(stations))))
    es_off = rng.uniform(*es_offset_range, n_outer)
    k_scat = np.exp(rng.uniform(np.log(k_scat_range[0]), np.log(k_scat_range[1]), n_outer))
    sys_f = np.exp(rng.uniform(np.log(sys_range[0]), np.log(sys_range[1]), n_outer))
    p_terr = rng.uniform(sc['p_terrain'][0], sc['p_terrain'][1], n_outer)
    F_vis = np.exp(rng.uniform(np.log(F_vis_range[0]), np.log(F_vis_range[1]), n_outer))
    # ---------------- flash and shared event draws (inner)
    fp = I.sample_flash_parameters(rng, N, sc['v_km_s'], sc['mass_kg'], eta_prior, T0_prior, eps_max)
    eta = 10 ** fp['log_eta']; E_bol = eta * fp['E_k'] / I.W_eval(fp['T0'])
    dt_min = rng.normal(0.0, sc['sigma_t_min'], N)
    d_along = rng.normal(0.0, sc['sigma_along_km'], N); d_cross = rng.normal(0.0, sc['sigma_cross_km'], N)
    terrain_ok = rng.random(N) < p_terr[kk]
    if stations:
        Lc = W.cholesky_factor(W.latent_correlation(usites, L_km))
        u = W.correlated_uniforms(Lc, N, rng)
        clear_u = u < p_site[kk]                                       # N x n_unique
        clear = clear_u[:, usite_idx]
    ready = rng.random((N, len(stations))) < p_ready[kk]
    # ---------------- per-station detection
    nS = len(stations)
    det = np.zeros((N, nS), bool); obv = np.zeros_like(det); selfc = np.zeros_like(det); usable_any = np.zeros_like(det)
    in_fov_all = np.zeros_like(det); avail_all = np.zeros_like(det); snr_best_all = np.zeros((N, nS)); sat_all = np.zeros_like(det)
    for j, st in enumerate(stations):
        g = st.geometry
        if not g.get('candidate', False):
            continue
        moon_alt = g['moon_alt'] + g['d_moon_alt'] * dt_min
        sun_alt = g['sun_alt'] + g['d_sun_alt'] * dt_min
        emission = g['emission'] + g['d_emission'] * dt_min + g['J_em'][0] * d_along + g['J_em'][1] * d_cross
        rec = np.abs(dt_min) <= float(st.inst.get('record_window_min', record_window_min))
        avail = (emission < 90.0) & (moon_alt >= 20.0) & (sun_alt <= -12.0) & (not g.get('closed', False)) & rec
        jx, jy = g['J_sky'][0], g['J_sky'][1]
        dx = jx[0] * d_along + jx[1] * d_cross + rng.normal(0, pointing_sigma_arcsec, N)
        dy = jy[0] * d_along + jy[1] * d_cross + rng.normal(0, pointing_sigma_arcsec, N)
        fw, fh = st.inst['fov_arcmin']
        in_fov = (np.abs(dx) <= 30.0 * fw) & (np.abs(dy) <= 30.0 * fh)
        X = kasten_young(moon_alt)
        dist_m = g['range_km'] * 1e3
        cams = st.cameras(); groups = sorted(set(c[1] for c in cams))
        phase = {gr: rng.uniform(0, st.inst['frame_time_s'], N) for gr in groups}
        snr_cam = []; usable = np.ones(N, bool); sat = np.zeros(N, bool)
        for band, gr in cams:
            inst = st.instrument(band); inst.sys_frac = 0.0
            ext = D.extinction_mag(band, X, st.site.get('alt', 2500.0))
            bkg = D.total_background_sb(band, g['illum'], g['dist_sunlit_arcmin'], sun_alt, k_scat[kk], ext, es_off[kk], g.get('sunlit', False), g.get('incidence', 60.0))
            rate = D.background_e_per_pixel(inst, bkg, 1.0)
            t_e = np.minimum(inst.exposure_s, 0.5 * inst.full_well_e / np.maximum(rate, 1e-30))
            ok_e = t_e >= inst.min_exposure_s
            usable &= ok_e
            t_e = np.maximum(t_e, inst.min_exposure_s)
            # candidate frames: the first three after the phase and three around the band peak
            Tf = inst.frame_time_s; tau = fp['tau']; ph = phase[gr]
            t_pk = I.xpeak_eval(band, fp['T0']) * tau
            k_pk = np.floor((t_pk - (ph - Tf)) / Tf)
            ks = np.stack([np.zeros(N), np.ones(N), 2 * np.ones(N), np.maximum(k_pk - 1, 0), np.maximum(k_pk, 0), np.maximum(k_pk + 1, 0)], axis=1)
            s0 = (ph - Tf)[:, None] + ks * Tf
            a = np.maximum(s0, 0.0); b = np.maximum(s0 + t_e[:, None], 0.0)
            Gb = I.G_eval(band, fp['T0'], b / tau[:, None]); Ga = I.G_eval(band, fp['T0'], a / tau[:, None])
            E_frame = (E_bol / (4 * np.pi * dist_m ** 2))[:, None] * np.clip(Gb - Ga, 0, None) * (10 ** (-0.4 * ext))[:, None]
            counts = D.photons_from_energy(E_frame, band, inst.area, inst.throughput)
            B = D.background_e_per_pixel(inst, bkg, t_e)
            n_pix = D.aperture_pixels(inst)
            S = counts * D.AP_FRAC
            var = S + n_pix * (B[:, None] * (1 + 1.0 / inst.n_ref) + inst.dark_e_s * t_e[:, None] + inst.read_noise_e ** 2) + (sys_f[kk][:, None] * B[:, None] * n_pix) ** 2
            snr_k = S / np.sqrt(var) * cal[kk, j][:, None]
            snr_cam.append(snr_k)
            kb = np.argmax(snr_k, axis=1)
            sat |= (counts[np.arange(N), kb] * D.peak_pixel_fraction(inst) + B) > inst.full_well_e
        snr_cam = np.array(snr_cam)                                     # cams x N x frames
        noise = rng.standard_normal((len(cams), N))
        best = snr_cam.max(axis=2) + noise                              # observed best SNR per camera
        ok = avail & in_fov & clear[:, j] & ready[:, j] & terrain_ok & usable
        det[:, j] = ok & (best.max(axis=0) >= DET_SNR)
        obv[:, j] = ok & (best.max(axis=0) >= OBV_SNR)
        if len(cams) == 2:
            if cams[0][1] == cams[1][1]:                                 # synchronised: both cameras in the same frame
                kj = np.argmax(np.minimum(snr_cam[0], snr_cam[1]), axis=1); ii = np.arange(N)
                joint = np.minimum(snr_cam[0][ii, kj] + noise[0], snr_cam[1][ii, kj] + noise[1])
            else:                                                       # independent cameras, coincident within the flash
                joint = best.min(axis=0)
            selfc[:, j] = ok & (joint >= CONF_SNR)
        usable_any[:, j] = usable; in_fov_all[:, j] = in_fov; avail_all[:, j] = avail; snr_best_all[:, j] = best.max(axis=0); sat_all[:, j] = sat & ok
    # ---------------- network outcomes
    lab = clusters_of(stations) if stations else np.zeros(0, int)
    turk = np.array([s.site['group'] == 'turkiye' for s in stations], bool)
    rt = np.array([bool(s.inst.get('realtime_pipeline', False)) for s in stations], bool)
    log_eta = fp['log_eta']
    bins = np.arange(-6.0, -2.49, 0.5)
    res = dict(n_outer=n_outer, n_inner=n_inner, N=N, eta_prior=eta_prior, T0_prior=T0_prior, eps_max=eps_max, rejected_fraction=fp['rejected_fraction'],
               eta_bins=bins.tolist(), strategies={})
    events = {}
    for name, spec in strategies.items():
        idx = np.array(spec['stations'], int)
        if len(idx) == 0:
            ind = {o: np.zeros(N, bool) for o in OUTCOMES}
        else:
            d = det[:, idx]; ob = obv[:, idx]; sc_ = selfc[:, idx]
            nclu = np.zeros(N, int)
            for c in np.unique(lab[idx]):
                nclu += d[:, lab[idx] == c].any(axis=1)
            stream = np.array([i in spec.get('streaming', set()) for i in idx], bool)
            ind = dict(any=d.any(axis=1), two_indep=nclu >= 2, dual_validated=sc_.any(axis=1))
            ind['confirmed'] = ind['two_indep'] | ind['dual_validated']
            ind['obvious_any'] = ob.any(axis=1); ind['live'] = (ob & stream[None, :]).any(axis=1)
            ind['rapid'] = (d & rt[idx][None, :]).any(axis=1); ind['turkish'] = (d & turk[idx][None, :]).any(axis=1)
            ind['obvious_turkish'] = (ob & turk[idx][None, :]).any(axis=1)
        events[name] = ind
        out = {}
        for o, x in ind.items():
            k = int(x.sum()); pk = x.reshape(n_outer, n_inner).mean(axis=1)
            byeta = [float(x[(log_eta >= lo) & (log_eta < lo + 0.5)].mean()) if np.any((log_eta >= lo) & (log_eta < lo + 0.5)) else None for lo in bins[:-1]]
            # Monte Carlo precision of the pooled probability: events are nested in outer draws, so the standard error is
            # that of the mean of the n_outer outer-draw means (the iid Wilson interval, kept for reference, understates it)
            se = float(pk.std(ddof=1) / np.sqrt(n_outer)) if n_outer > 1 else float('nan')
            out[o] = dict(p=k / N, k=k, mc_se=se, ci95=[max(0.0, k / N - 1.96 * se), min(1.0, k / N + 1.96 * se)], wilson95_iid=wilson(k, N),
                          outer_p05=float(np.percentile(pk, 5)), outer_p50=float(np.percentile(pk, 50)), outer_p95=float(np.percentile(pk, 95)), by_eta=byeta)
        out['n_stations'] = int(len(idx))
        out['station_p_det'] = {stations[i].key: float(det[:, i].mean()) for i in idx}
        out['station_p_fov'] = {stations[i].key: (float(in_fov_all[:, i].mean()) if stations[i].geometry.get('candidate', False) else None) for i in idx}
        out['station_p_saturated'] = {stations[i].key: float(sat_all[:, i].mean()) for i in idx}
        res['strategies'][name] = out
    # paired differences between strategies (common random numbers)
    names = list(strategies)
    res['paired'] = {}
    for o in ('any', 'confirmed', 'two_indep', 'live', 'turkish'):
        for a_ in names:
            for b_ in names:
                if a_ >= b_:
                    continue
                dd = events[b_][o].astype(float) - events[a_][o].astype(float)
                dm = dd.reshape(n_outer, n_inner).mean(axis=1)             # outer-draw means (two-level design)
                m = float(dd.mean()); se = float(dm.std(ddof=1) / np.sqrt(n_outer)) if n_outer > 1 else float('nan')
                res['paired'][f'{o}:{b_}-{a_}'] = dict(diff=m, mc_se=se, ci95=(m - 1.96 * se, m + 1.96 * se))
    # flash brightness (unocculted source-equivalent at the geocentric distance)
    pkV = I.peak_band_magnitude_fast('V', eta, fp['E_k'], fp['T0'], fp['tau'], sc['distance_km'] * 1e3)
    res['peakV'] = dict(median=float(np.median(pkV)), p10=float(np.percentile(pkV, 10)), p90=float(np.percentile(pkV, 90)))
    res['T0_percentiles'] = [float(x) for x in np.percentile(fp['T0'], [5, 50, 95])]
    # conditional visual-threshold model at the public reference site
    res['visual'] = visual_model(sc, stations, public_site, fp, eta, E_bol, kk, es_off, k_scat, F_vis, attention, dt_min, terrain_ok,
                                 clear if stations else None)
    if keep_events:
        res['_events'] = events; res['_log_eta'] = log_eta; res['_pkV'] = pkV; res['_snr'] = snr_best_all; res['_det'] = det
    return res

def visual_model(sc, stations, public_site, fp, eta, E_bol, kk, es_off, k_scat, F_vis, attention, dt_min, terrain_ok, clear):
    """Conditional visual-threshold model at the public reference site: P(a prepared observer notices the flash),
    (a) conditional on the site having the Moon >= 15 deg in a sky darker than Sun -6 deg, the point visible, clear
    weather and no terrain blocking, and (b) including the site's weather and those conditions. Light received in the
    first T_EYE seconds, V band, extincted; Crumey thresholds with field factor F (outer draw)."""
    g = sc.get('public_geometry')
    if g is None:
        return dict(site=public_site, observable=False)
    if not g.get('visible', False):
        return dict(site=public_site, observable=False, note='impact point not visible from the site')
    N = len(eta)
    X = kasten_young(g['moon_alt']); ext = float(D.extinction_mag('V', X, g.get('alt', 100.0)))
    G1 = I.G_eval('V', fp['T0'], (D.T_EYE / fp['tau'])[:, None])[:, 0]
    E = E_bol / (4 * np.pi * (g['range_km'] * 1e3) ** 2) * G1 * 10 ** (-0.4 * ext)
    m_eff = -2.5 * np.log10(np.maximum(E, 1e-300) / D.T_EYE / I.BANDS['V']['width'] / I.BANDS['V']['f0'])
    bkg = D.total_background_sb('V', g['illum'], g['dist_sunlit_arcmin'], g['sun_alt'], k_scat[kk], ext, es_off[kk], g.get('sunlit', False), g.get('incidence', 60.0))
    cond_ok = (g['moon_alt'] >= 15) and (g['sun_alt'] <= -6)
    out = dict(site=public_site, observable=bool(cond_ok), moon_alt=g['moon_alt'], sun_alt=g['sun_alt'])
    for aid in D.AIDS:
        thr = D.visual_threshold_mag(bkg, aid, F_vis[kk])
        p = D.visual_detection_probability(m_eff, thr, attention)
        out[aid] = dict(p_conditional=float(p.mean()) if cond_ok else 0.0,
                        p_with_weather=float((p * (clear[:, g['station_index']] if (clear is not None and g.get('station_index') is not None) else 1.0) * terrain_ok).mean()) if cond_ok else 0.0,
                        threshold_median=float(np.median(thr)))
    return out

def ladder_probabilities(instruments, eta_prior='wide', T0_prior='broad', n=20000, seed=1, mass=(1600, 2400), v_km_s=1.68, distance_m=3.8e8,
                         illum=0.35, dist_sunlit=8.0, sun_alt=-20.0, airmass=1.2, site_alt=2500.0, eps_max=0.1, return_det=False):
    """For the website's instrument ladder: probability that the best frame reaches SNR 8, for a randomly phased
    exposure sequence, with the flash's exposure-integrated counts (not its peak), at a reference geometry, no weather
    or readiness. Also returns the peak V magnitude of each draw so that a 50 % V-equivalent threshold can be fitted."""
    rng = np.random.default_rng(seed)
    fp = I.sample_flash_parameters(rng, n, v_km_s, mass, eta_prior, T0_prior, eps_max)
    eta = 10 ** fp['log_eta']; E_bol = eta * fp['E_k'] / I.W_eval(fp['T0'])
    pkV = I.peak_band_magnitude_fast('V', eta, fp['E_k'], fp['T0'], fp['tau'], distance_m)
    out = {}; dets = {}
    for key, inst, penalty in instruments:
        ext = float(D.extinction_mag(inst.band, airmass, site_alt))
        bkg = float(D.total_background_sb(inst.band, illum, dist_sunlit, sun_alt, 3e-3, ext))
        Tf = inst.frame_time_s; tau = fp['tau']; ph = rng.uniform(0, Tf, n)
        t_pk = I.xpeak_eval(inst.band, fp['T0']) * tau; k_pk = np.floor((t_pk - (ph - Tf)) / Tf)
        ks = np.stack([np.zeros(n), np.ones(n), 2 * np.ones(n), np.maximum(k_pk - 1, 0), np.maximum(k_pk, 0), np.maximum(k_pk + 1, 0)], axis=1)
        s0 = (ph - Tf)[:, None] + ks * Tf; a = np.maximum(s0, 0); b = np.maximum(s0 + inst.exposure_s, 0)
        E_frame = (E_bol / (4 * np.pi * distance_m ** 2))[:, None] * np.clip(I.G_eval(inst.band, fp['T0'], b / tau[:, None]) - I.G_eval(inst.band, fp['T0'], a / tau[:, None]), 0, None) * 10 ** (-0.4 * ext)
        counts = D.photons_from_energy(E_frame, inst.band, inst.area, inst.throughput)
        snr = D.snr_from_counts(inst, counts, bkg).max(axis=1) * penalty
        detp = snr >= 8.0
        out[key] = dict(p=float(detp.mean()), band=inst.band, v50=_v50(pkV, detp), steady_limit=float(D.limiting_magnitude(inst, bkg, 8.0 / penalty) - ext))
        dets[key] = detp
    if return_det:
        return out, pkV, fp, dets
    return out, pkV, fp

def _v50(pkV, det):
    """V peak magnitude at which the detection fraction is 50 % (monotone binned estimate)."""
    edges = np.arange(np.floor(pkV.min()), np.ceil(pkV.max()) + 0.25, 0.25)
    c = np.digitize(pkV, edges)
    fr = np.array([det[c == i].mean() if np.any(c == i) else np.nan for i in range(1, len(edges))])
    mid = 0.5 * (edges[1:] + edges[:-1]); ok = np.isfinite(fr)
    mid, fr = mid[ok], np.maximum.accumulate(fr[ok][::-1])[::-1]          # brighter -> more likely (monotone in m)
    if fr.max() < 0.5:
        return None
    if fr.min() > 0.5:
        return float(mid.max())
    k = np.where(fr >= 0.5)[0].max()
    if k + 1 >= len(mid):
        return float(mid[k])
    f0, f1 = fr[k], fr[k + 1]
    return float(mid[k] + (mid[k + 1] - mid[k]) * (f0 - 0.5) / max(f0 - f1, 1e-9))
