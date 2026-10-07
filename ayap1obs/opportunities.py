"""Circular-overflight screening opportunities (shared by scripts/run_reachability.py and
scripts/check_reachability_convergence.py).

For one directed orbit plane and a set of orbital phases, every overflight of every HEALPix pixel (the spacecraft on
its circular orbit passes the pixel's along-track position while the pixel is within the cross-track allowance) is
turned into an impact time and classified at that time.

Impact time (re-audit GE-01). An in-plane retrograde burn of dv at time t_b makes the spacecraft descend along an
ellipse that covers a central angle du_d in the flight time t_f (reachability.deorbit_trajectory); the circular orbit
covers n t_f in the same time. To hit the point that the circular orbit overflies at t_c, the burn must therefore be
made where u(t_b) + du_d = u_target, i.e. the impact occurs dt = (du_d - n t_f)/n before t_c (91.5 s for 25 m/s,
14.7 s for 50 m/s at 100 km) and the burn at t_imp - t_f. The target's motion during dt (<= 0.014 deg) and the timing
and phase change of the cross-track manoeuvre are neglected; the descent is two-body to the reference sphere (no
terrain). These are screening opportunities, not burn solutions for a real spacecraft.

Classification (re-audit GE-V2-03). Station Moon and Sun altitudes, the illuminated fraction and the elongation are
computed exactly on the overflight grid, interpolated linearly to each impact time (error <= ~0.02 deg on a 10-min
grid away from culmination) and only then compared with the thresholds; seasonal closures use the calendar month of
the impact time. Classes:
  A: Turkish evening, central near side, public phase (illuminated 12-50 %), waxing, >= 3 sites available
  B: central near side, flash geometry, >= 3 sites;  C: central near side, flash geometry, >= 1 Turkish site
  P: sunlit-plume geometry (emission criterion of the plume class) within 60 deg of the equator, >= 3 sites
"""
from __future__ import annotations
import numpy as np
from astropy.time import Time
from . import reachability as R, screening as S

CLASSES = ['A_turkiye_evening_public', 'B_global_science', 'C_any_turkish', 'P_plume_global']
MAPS = ['flash_cov3', 'flash_tr', 'plume_tr']

def transfer_offset_s(alt_km=100.0, dv_m_s=25.0):
    """(dt, t_f): the impact precedes the circular overflight of the same point by dt seconds; t_f is the burn-to-impact
    flight time (s)."""
    _, _, t_f, du_deg = R.deorbit_trajectory(alt_km, dv_m_s)
    n = 2 * np.pi / R.period_s(alt_km)
    return float((np.radians(du_deg) - n * t_f) / n), float(t_f)

def _month_lookup(jd0, jd1):
    """Month-start JDs (UTC) covering [jd0, jd1] and the calendar month of each interval."""
    d0 = Time(jd0 - 40, format='jd', scale='utc').to_datetime(); d1 = Time(jd1 + 40, format='jd', scale='utc').to_datetime()
    y, m = d0.year, d0.month; starts, months = [], []
    while (y, m) <= (d1.year, d1.month):
        starts.append(Time(f'{y:04d}-{m:02d}-01 00:00:00', scale='utc').jd); months.append(m)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return np.array(starts), np.array(months)

def context(grid, sites, cr):
    """Continuous time-dependent quantities on the overflight grid, computed exactly at every grid epoch, plus a
    conservative grid-level candidate mask. Thresholds are applied at the impact times by gates_at()."""
    jg = grid['jd_utc']
    t = Time(jg, format='jd', scale='utc')
    Rm = S.itrs_to_gcrs_matrices(t)
    alt_m = np.zeros((len(sites), len(jg)), np.float32); alt_s = np.zeros_like(alt_m)
    for k, s in enumerate(sites):
        sky = S.observer_sky_fast(s['lon'], s['lat'], s['alt'], Rm, grid['moon'], grid['sun'])
        alt_m[k], alt_s[k] = sky['moon_alt'], sky['sun_alt']
    illum, elong, _ = S.lunar_phase_arrays(grid['moon'], grid['sun'])
    m_starts, m_months = _month_lookup(jg[0], jg[-1])
    closed = np.zeros((len(sites), 13), bool)
    for k, s in enumerate(sites):
        closed[k, s.get('closed_months', [])] = True
    ctx = dict(jd=jg, alt_m=alt_m, alt_s=alt_s, illum=illum, elong=elong, m_starts=m_starts, m_months=m_months, closed=closed,
               tr=np.array([s['group'] == 'turkiye' for s in sites]), tug=[s['id'] for s in sites].index('TUG'),
               min_moon=cr['observer']['min_moon_alt_deg'], max_sun=cr['observer']['max_sun_alt_deg'], flash=cr['flash'])
    g = gates_at(ctx, jg)
    ok = g['phase_ok'] & (g['n_avail'] >= 1)
    # candidate mask for the overflight search, dilated by two grid steps: the impact precedes the circular overflight
    # by up to ~1.5 min and the conditions are evaluated exactly at the impact time afterwards
    ctx['time_ok'] = ok | np.roll(ok, 1) | np.roll(ok, -1) | np.roll(ok, 2) | np.roll(ok, -2)
    ctx['n_avail_grid'] = g['n_avail']
    return ctx

def gates_at(ctx, jd, chunk=300000):
    """Observing conditions at arbitrary UTC JDs (re-audit GE-V2-03): continuous quantities are interpolated to each
    time, then thresholded. Returns dict of arrays: n_avail, n_tr, tug_av, evening_tr, illum, phase_ok, public_phase,
    waxing."""
    jd = np.atleast_1d(np.asarray(jd, float)); jg = ctx['jd']; step = jg[1] - jg[0]
    x = (jd - jg[0]) / step; i0 = np.clip(np.floor(x).astype(np.int64), 0, len(jg) - 2); f = (x - i0).astype(np.float32)
    mon = ctx['m_months'][np.clip(np.searchsorted(ctx['m_starts'], jd, side='right') - 1, 0, len(ctx['m_months']) - 1)]
    n_avail = np.zeros(len(jd), np.int16); n_tr = np.zeros(len(jd), np.int16); tug_av = np.zeros(len(jd), bool)
    for a in range(0, len(jd), chunk):
        b = min(a + chunk, len(jd)); ii = i0[a:b]; ff = f[a:b]
        am = ctx['alt_m'][:, ii] * (1 - ff) + ctx['alt_m'][:, ii + 1] * ff
        asun = ctx['alt_s'][:, ii] * (1 - ff) + ctx['alt_s'][:, ii + 1] * ff
        av = (am >= ctx['min_moon']) & (asun <= ctx['max_sun']) & ~ctx['closed'][:, mon[a:b]]
        n_avail[a:b] = av.sum(axis=0); n_tr[a:b] = av[ctx['tr']].sum(axis=0); tug_av[a:b] = av[ctx['tug']]
    il = ctx['illum']; el = ctx['elong']; f64 = f.astype(float)
    illum = il[i0] * (1 - f64) + il[i0 + 1] * f64; elong = el[i0] * (1 - f64) + el[i0 + 1] * f64
    fl = ctx['flash']
    ut_hour = ((jd + 0.5) % 1.0) * 24.0
    return dict(n_avail=n_avail, n_tr=n_tr, tug_av=tug_av, illum=illum,
                phase_ok=(illum >= fl['illum_min']) & (illum <= fl['illum_max']) & (elong >= fl['min_elongation_deg']),
                public_phase=(illum >= 0.12) & (illum <= 0.5), waxing=(il[i0 + 1] - il[i0]) > 0,
                evening_tr=tug_av & (ut_hour >= 15) & (ut_hour < 21))           # 18-24 h Istanbul (UTC+3)

def node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h0, n_hours, catalogue_tag=None,
                   alt_km=100.0, dv_m_s=25.0):
    """Hourly occupancy occ[phase, class, delta, hour] by impact time, per-pixel admissible opportunity counts
    maps[delta, map, pixel] (averaged over phases) and, if catalogue_tag is given, a thinned class-B catalogue for the
    first phase with circular-overflight, burn and impact times."""
    npix = len(lat)
    central = (np.abs(lat) < 45) & (np.abs(lon) < 60); lat60 = np.abs(lat) < 60
    occ = np.zeros((len(phases), len(CLASSES), len(deltas), n_hours), bool)
    maps = np.zeros((len(deltas), len(MAPS), npix), np.float32)
    cat = []
    dt_s, t_f = transfer_offset_s(alt_km, dv_m_s)
    ov = R.overflights(plane, grid, pix, phases, max(deltas), time_mask=ctx['time_ok'])
    for k, o in enumerate(ov):
        if len(o['pixel']) == 0:
            continue
        t_imp = o['jd_utc'] - dt_s / 86400.0
        g = gates_at(ctx, t_imp)
        keep = g['phase_ok'] & (g['n_avail'] >= 1)
        p, t, c, tc = o['pixel'][keep], t_imp[keep], o['cross_deg'][keep], o['jd_utc'][keep]
        g = {key: v[keep] for key, v in g.items()}
        if len(p) == 0:
            continue
        em, inc = R.geocentric_angles_at(grid, pix, p, t)
        flash = (em < cr['flash']['max_emission_deg'] + 1) & (inc >= cr['flash']['min_incidence_deg'])
        plume = (em < cr['plume_sunlit']['max_emission_deg'] + 1) & (inc >= cr['plume_sunlit']['incidence_min_deg']) & (inc <= cr['plume_sunlit']['incidence_max_deg'])
        n3 = g['n_avail'] >= 3; ntr1 = g['n_tr'] >= 1
        hours = np.floor((t - jd_h0) * 24.0).astype(int)
        inside = (hours >= 0) & (hours < n_hours)
        for di, dl in enumerate(deltas):
            ind = (np.abs(c) <= dl) & inside
            cls = [central[p] & flash & g['evening_tr'] & g['public_phase'] & g['waxing'] & n3, central[p] & flash & n3, central[p] & flash & ntr1, lat60[p] & plume & n3]
            for ci, m in enumerate(cls):
                occ[k, ci, di, hours[ind & m]] = True
            for mi, m in enumerate([flash & n3, flash & ntr1, plume & ntr1]):
                maps[di, mi] += np.bincount(p[ind & m], minlength=npix) / len(phases)
            if catalogue_tag is not None and di == 0 and k == 0:
                sel = np.where(ind & central[p] & flash & n3 & g['tug_av'])[0]
                for j in sel[:: max(1, len(sel) // 120)]:
                    cat.append(dict(family=catalogue_tag, phase_deg=float(np.degrees(phases[k])), jd_utc_overflight=float(tc[j]),
                                    jd_utc_impact=float(t[j]), jd_utc_burn=float(t[j] - t_f / 86400.0), deorbit_dv_m_s=dv_m_s,
                                    pixel=int(p[j]), lat=float(lat[p[j]]), lon=float(lon[p[j]]), cross_track_deg=float(c[j]),
                                    n_sites=int(g['n_avail'][j]), n_tr=int(g['n_tr'][j]), tug_available=bool(g['tug_av'][j]),
                                    illum=float(g['illum'][j]), plume=bool(plume[j])))
    return occ, maps, cat

def window_prob(occ_c, W_days, step_h=24):
    """occ_c: combinations x hours. Returns (start hour indices, P(>= 1 opportunity in [h, h + W)))."""
    cs = np.concatenate([np.zeros((occ_c.shape[0], 1), np.int32), np.cumsum(occ_c, axis=1, dtype=np.int32)], axis=1)
    W = int(W_days * 24); starts = np.arange(0, occ_c.shape[1] - W + 1, step_h)
    return starts, ((cs[:, starts + W] - cs[:, starts]) > 0).mean(axis=0)

def first_after(occ_c, h0):
    sub = occ_c[:, h0:]
    has = sub.any(axis=1)
    return np.where(has, sub.argmax(axis=1), np.nan) / 24.0
