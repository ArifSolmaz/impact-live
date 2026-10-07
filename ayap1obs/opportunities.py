"""Opportunity classes from trajectory-level overflights (shared by scripts/run_reachability.py and
scripts/check_reachability_convergence.py).

For one orbit plane and a set of orbital phases, every overflight of every HEALPix pixel (the spacecraft passes the
pixel's along-track position while the pixel is within the cross-track allowance) is evaluated at its own time:
exact geocentric emission/incidence of the pixel, observer availability (shared function, including seasonal closures),
lunar phase and the Turkish-evening condition (on the overflight grid). Classes:
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

def context(grid, jd_h, cl, ob, sites, cr):
    """Time-dependent global quantities on the overflight grid (interpolated from the hourly screening)."""
    jg = grid['jd_utc']
    interp = lambda a: np.interp(jg, jd_h, a)
    months = np.array([x.month for x in Time(jg, format='jd', scale='utc').to_datetime()])
    ids = list(ob['ids']); avail = np.zeros((len(sites), len(jg)), bool)
    for k, s in enumerate(sites):
        i = ids.index(s['id'])
        _, avail[k] = S.observer_availability(interp(ob['moon_alt'][i]), interp(ob['sun_alt'][i]), months, s, cr['observer'])
    tr = np.array([s['group'] == 'turkiye' for s in sites]); tug = [s['id'] for s in sites].index('TUG')
    illum = interp(cl['illum']); elong = interp(cl['elong'])
    phase_ok = (illum >= cr['flash']['illum_min']) & (illum <= cr['flash']['illum_max']) & (elong >= cr['flash']['min_elongation_deg'])
    ut_hour = ((jg + 0.5) % 1.0) * 24.0
    ctx = dict(n_avail=avail.sum(axis=0), n_tr=avail[tr].sum(axis=0), tug_av=avail[tug], illum=illum, phase_ok=phase_ok,
               waxing=np.gradient(illum) > 0, public_phase=(illum >= 0.12) & (illum <= 0.5))
    ctx['evening_tr'] = ctx['tug_av'] & (ut_hour >= 15) & (ut_hour < 21)          # 18-24 h Istanbul (UTC+3)
    ctx['time_ok'] = phase_ok & (ctx['n_avail'] >= 1)
    return ctx

def node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h0, n_hours, catalogue_tag=None):
    """Hourly occupancy occ[phase, class, delta, hour], per-pixel admissible overflight counts maps[delta, map, pixel]
    (averaged over phases) and, if catalogue_tag is given, a thinned class-B catalogue for the first phase."""
    jg = grid['jd_utc']; npix = len(lat)
    central = (np.abs(lat) < 45) & (np.abs(lon) < 60); lat60 = np.abs(lat) < 60
    occ = np.zeros((len(phases), len(CLASSES), len(deltas), n_hours), bool)
    maps = np.zeros((len(deltas), len(MAPS), npix), np.float32)
    cat = []
    ov = R.overflights(plane, grid, pix, phases, max(deltas), time_mask=ctx['time_ok'])
    for k, o in enumerate(ov):
        gi = np.clip(o['gi'], 0, len(jg) - 1)
        keep = ctx['time_ok'][gi]
        p, t, c, gi = o['pixel'][keep], o['jd_utc'][keep], o['cross_deg'][keep], gi[keep]
        if len(p) == 0:
            continue
        em, inc = R.geocentric_angles_at(grid, pix, p, t)
        flash = (em < cr['flash']['max_emission_deg'] + 1) & (inc >= cr['flash']['min_incidence_deg'])
        plume = (em < cr['plume_sunlit']['max_emission_deg'] + 1) & (inc >= cr['plume_sunlit']['incidence_min_deg']) & (inc <= cr['plume_sunlit']['incidence_max_deg'])
        n3 = ctx['n_avail'][gi] >= 3; ntr1 = ctx['n_tr'][gi] >= 1
        hours = np.clip(np.floor((t - jd_h0) * 24.0).astype(int), 0, n_hours - 1)
        for di, dl in enumerate(deltas):
            ind = np.abs(c) <= dl
            cls = [central[p] & flash & ctx['evening_tr'][gi] & ctx['public_phase'][gi] & ctx['waxing'][gi] & n3, central[p] & flash & n3, central[p] & flash & ntr1, lat60[p] & plume & n3]
            for ci, m in enumerate(cls):
                occ[k, ci, di, hours[ind & m]] = True
            for mi, m in enumerate([flash & n3, flash & ntr1, plume & ntr1]):
                maps[di, mi] += np.bincount(p[ind & m], minlength=npix) / len(phases)
            if catalogue_tag is not None and di == 0 and k == 0:
                sel = np.where(ind & central[p] & flash & n3 & ctx['tug_av'][gi])[0]
                for j in sel[:: max(1, len(sel) // 120)]:
                    cat.append(dict(family=catalogue_tag, phase_deg=float(np.degrees(phases[k])), jd_utc=float(t[j]), pixel=int(p[j]), lat=float(lat[p[j]]), lon=float(lon[p[j]]),
                                    cross_track_deg=float(c[j]), n_sites=int(ctx['n_avail'][gi[j]]), n_tr=int(ctx['n_tr'][gi[j]]), illum=float(ctx['illum'][gi[j]]), plume=bool(plume[j])))
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
