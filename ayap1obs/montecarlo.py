"""Joint Monte Carlo for network detection probabilities (conditional on the spacecraft reaching the stated
terminal state).  Shared uncertainties: luminous efficiency, flash temperature and duration, impact mass,
location error ellipse, timing error, correlated weather, instrument readiness, SNR calibration.

Outcome definitions (per draw):
  detected_i       : station i records the flash with best-frame SNR >= 8 (after calibration scatter)
  obvious_i        : SNR >= 30 (visible in raw frames; 'live feed with identifiable transient')
  confirmed        : >= 2 *independent* detections (distinct sites > 100 km apart, or one dual-camera station
                     plus any other station), OR a single dual-camera station detection with SNR >= 15 in both cameras
                     (counted as weaker 'self-confirmed')
  rapid_replay     : >= 1 detection at a station with a real-time pipeline (processed within ~1 h)
  live_identifiable: >= 1 'obvious' detection at a station that is streaming
  eyepiece_witness : a prepared observer at a 20-cm telescope sees it (threshold model, attention 0.5)
"""
from __future__ import annotations
import numpy as np, yaml, os
from dataclasses import dataclass, field
from . import impact as I, detect as D, weather as W

@dataclass
class Station:
    site: dict
    template: str
    inst: dict
    p_ready: float
    streaming: bool = False
    geometry: dict = None          # filled per scenario: moon_alt, sun_alt, visible, emission, illum, dist_sunlit_arcmin
    def instrument(self, band):
        t = self.inst
        return D.Instrument(f"{self.site['id']}:{self.template}:{band}", t['aperture_m'], band, t['pixel_scale_arcsec'], tuple(t['fov_arcmin']),
                            t['exposure_s'], t['frame_time_s'], throughput=t['throughput'], obstruction=0.15, read_noise_e=t['read_noise_e'],
                            seeing_arcsec=t['seeing_arcsec'], saturation_e=float(t.get('saturation_e', 6e4)))

def load_templates():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return yaml.safe_load(open(f'{here}/config/instruments.yaml'))['templates']

def magnitude_table(bands_exposures, T0_grid, tau_grid):
    """g(T0, tau; band, exposure) such that m_avg = -2.5 log10(eta_vis * E_k / 1 J) + g, for a 1-J reference."""
    tab = {}
    for band, texp in bands_exposures:
        g = np.zeros((len(T0_grid), len(tau_grid)))
        for i, T0 in enumerate(T0_grid):
            for j, tau in enumerate(tau_grid):
                fm = I.FlashModel(E_k=1.0, eta_vis=1.0, T0=T0, Tfloor=min(1200.0, T0 - 100), tau_T=tau, tau_L=tau)
                g[i, j] = fm.exposure_averaged_magnitude(band, texp)
        tab[(band, texp)] = g
    return tab

def interp2(g, T0_grid, tau_grid, T0, tau):
    i = np.clip(np.searchsorted(T0_grid, T0) - 1, 0, len(T0_grid) - 2); j = np.clip(np.searchsorted(tau_grid, tau) - 1, 0, len(tau_grid) - 2)
    fi = (T0 - T0_grid[i]) / (T0_grid[i + 1] - T0_grid[i]); fj = (np.log(tau) - np.log(tau_grid[j])) / (np.log(tau_grid[j + 1]) - np.log(tau_grid[j]))
    return (1 - fi) * (1 - fj) * g[i, j] + fi * (1 - fj) * g[i + 1, j] + (1 - fi) * fj * g[i, j + 1] + fi * fj * g[i + 1, j + 1]

def fov_coverage(fov_arcmin, sigma_along_km, sigma_cross_km, pointing_err_arcsec=15.0, distance_km=384400.0, n=4000, rng=None):
    """Probability that the true impact point lies inside the field when the field is centred on the nominal point."""
    rng = rng or np.random.default_rng(0)
    arcsec_per_km = 206265.0 / distance_km
    x = rng.normal(0, sigma_along_km * arcsec_per_km, n) + rng.normal(0, pointing_err_arcsec, n)
    y = rng.normal(0, sigma_cross_km * arcsec_per_km, n) + rng.normal(0, pointing_err_arcsec, n)
    return float(np.mean((np.abs(x) < fov_arcmin[0] * 30) & (np.abs(y) < fov_arcmin[1] * 30)))

def run(scenario, stations, n=20000, seed=20261005, eta_prior='slow-impact-wide', month=1):
    rng = np.random.default_rng(seed)
    sc = scenario
    # physics draws
    mass = rng.uniform(sc['mass_kg'][0], sc['mass_kg'][1], n)
    v = sc['v_km_s'] * rng.normal(1.0, 0.03, n)
    E_k = I.kinetic_energy(mass, v)
    log_eta = I.luminous_efficiency_prior(sc['v_km_s'], rng, n, eta_prior)
    T0 = rng.uniform(1800, 3500, n); tau = np.exp(rng.uniform(np.log(0.1), np.log(2.0), n))
    T0_grid = np.array([1800, 2200, 2600, 3000, 3500.0]); tau_grid = np.array([0.1, 0.2, 0.4, 0.8, 1.5, 2.0])
    be = sorted({(b, st.inst['exposure_s']) for st in stations for b in st.inst['bands']} | {('V', 0.001)})
    tab = magnitude_table(be, T0_grid, tau_grid)
    peakV = -2.5 * np.log10(10 ** log_eta * E_k) + interp2(tab[('V', 0.001)], T0_grid, tau_grid, T0, tau)
    # weather, readiness
    clear = W.sample_clear([st.site for st in stations], month, n, rng)
    terrain_ok = rng.random(n) < sc.get('p_terrain', 1.0)      # shared: local terrain hides the flash from every observer or none
    ready = rng.random((n, len(stations))) < np.array([st.p_ready for st in stations])[None, :]
    cal = np.exp(rng.normal(0, 0.3, (n, len(stations))))      # SNR calibration scatter (declared)
    det = np.zeros((n, len(stations)), bool); obv = np.zeros_like(det); snr_all = np.zeros((n, len(stations)))
    cov = np.zeros(len(stations))
    for k, st in enumerate(stations):
        g_ = st.geometry
        if not g_['visible'] or g_['moon_alt'] < 20 or g_['sun_alt'] > -12:   # same facility-grade criterion as 'available'
            continue
        cov[k] = fov_coverage(st.inst['fov_arcmin'], sc['sigma_along_km'], sc['sigma_cross_km'], rng=rng)
        snr_best = np.zeros(n)
        for b in st.inst['bands']:
            inst = st.instrument(b)
            ext = float(D.extinction_mag(b, g_.get('airmass', 1.0), st.site.get('alt', 2500.0)))
            if g_.get('sunlit', False):
                # sunlit terrain: Lambert-like surface brightness 3.4 mag/arcsec^2 at normal incidence (full-Moon mean), dimmer by 1/cos(i)
                bkg = 3.4 + 2.5 * np.log10(1.0 / max(np.cos(np.radians(g_.get('incidence', 60.0))), 0.05)) - D.LUNAR_COLOR_VS_V[b] + ext
            else:
                bkg = D.total_background_sb(b, g_['illum'], g_['dist_sunlit_arcmin'], g_['sun_alt'], ext_mag=ext)
            m_avg = -2.5 * np.log10(10 ** log_eta * E_k) + interp2(tab[(b, st.inst['exposure_s'])], T0_grid, tau_grid, T0, tau) + ext
            # duty-cycle miss: flash shorter than the dead gap can fall entirely in the gap
            gap = inst.frame_time_s - inst.exposure_s
            p_miss = np.clip((gap - tau) / inst.frame_time_s, 0, 1)
            snr = np.array([D.frame_snr(inst, m, bkg)[0] for m in m_avg]) * (rng.random(n) > p_miss)
            snr_best = np.maximum(snr_best, snr)
        snr_best *= cal[:, k]
        in_fov = rng.random(n) < cov[k]
        ok = clear[:, k] & ready[:, k] & in_fov & terrain_ok
        snr_all[:, k] = np.where(ok, snr_best, 0)
        det[:, k] = ok & (snr_best >= 8); obv[:, k] = ok & (snr_best >= 30)
    # independence: cluster stations within 100 km
    lat = np.array([st.site['lat'] for st in stations]); lon = np.array([st.site['lon'] for st in stations])
    Dm = W.great_circle_km(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    clusters = -np.ones(len(stations), int); c = 0
    for i in range(len(stations)):
        if clusters[i] < 0:
            clusters[np.where(Dm[i] < 100)[0]] = c; c += 1
    n_indep = np.zeros(n, int)
    for cl in range(c):
        n_indep += det[:, clusters == cl].any(axis=1)
    dual = np.array([st.inst.get('dual_camera', False) for st in stations])
    self_conf = (det & dual[None, :] & (snr_all >= 15)).any(axis=1)
    confirmed = (n_indep >= 2) | (self_conf & (det.sum(axis=1) >= 1) & (n_indep >= 1) & ((n_indep >= 2) | self_conf))
    rt = np.array([st.inst.get('realtime_pipeline', False) for st in stations]); stream = np.array([st.streaming for st in stations])
    tr = np.array([st.site['group'] == 'turkiye' for st in stations])
    pen = 6.0 if sc.get('sunlit_site', False) else 0.0     # flash against sunlit terrain: thresholds ~6 mag brighter (declared)
    pw = D.witness_probability(peakV + pen, tau, sc['illum_for_eye'], 'telescope20cm', attention=0.5)
    pw_eye = D.witness_probability(peakV + pen, tau, sc['illum_for_eye'], 'none', attention=0.5)
    pw_bin = D.witness_probability(peakV + pen, tau, sc['illum_for_eye'], 'binoculars', attention=0.5)
    out = dict(
        p_any=float(det.any(axis=1).mean()), p_confirmed=float(confirmed.mean()), p_two_indep=float((n_indep >= 2).mean()),
        p_obvious_any=float(obv.any(axis=1).mean()), p_live=float((obv & stream[None, :]).any(axis=1).mean()),
        p_rapid_replay=float((det & rt[None, :]).any(axis=1).mean()), p_turkish=float((det & tr[None, :]).any(axis=1).mean()),
        p_obvious_turkish=float((obv & tr[None, :]).any(axis=1).mean()),
        p_eyepiece_witness=float(np.mean(pw)), p_naked_eye_witness=float(np.mean(pw_eye)), p_binocular_witness=float(np.mean(pw_bin)), mean_n_det=float(det.sum(axis=1).mean()),
        station_p_det={st.site['id'] + ':' + st.template: float(det[:, k].mean()) for k, st in enumerate(stations)},
        station_fov_cov={st.site['id'] + ':' + st.template: float(cov[k]) for k, st in enumerate(stations)},
        peakV_median=float(np.median(peakV)), peakV_p10=float(np.percentile(peakV, 10)), peakV_p90=float(np.percentile(peakV, 90)),
    )
    # sensitivity: by eta decile
    q = np.percentile(log_eta, [0, 25, 50, 75, 100])
    out['p_any_by_eta_quartile'] = [float(det.any(axis=1)[(log_eta >= q[i]) & (log_eta <= q[i + 1])].mean()) for i in range(4)]
    out['p_conf_by_eta_quartile'] = [float(confirmed[(log_eta >= q[i]) & (log_eta <= q[i + 1])].mean()) for i in range(4)]
    out['eta_quartile_edges_log10'] = [float(x) for x in q]
    return out
