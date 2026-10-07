"""Orbiter follow-up helpers (re-audit GE-21, GE-V2-05).

Illumination seasons of LRO and Danuri are computed from archived JPL Horizons osculating elements (Moon-centred,
ecliptic of J2000, daily; queries of 2026-10-07 supplied by the author):
* data/horizons/horizons_lro_elements_2023-2028.txt, LRO (-85), 2023-01-01 to 2028-03-13 TDB: reconstructed to
  2026-03-15, preliminary tracking ("tag-up") solutions to 2026-09-02 and a 558-day prediction after that. The
  prediction is NOT used: its node regresses at 0.004-0.02 deg/day against 0.09-0.12 deg/day (and accelerating) in
  every observed year, the behaviour of a low-fidelity placeholder already noted in the research notes for the earlier
  Horizons forecast.
* data/horizons/horizons_kplo_elements_2023-2027.txt, Danuri (-155), 2023-01-01 to 2027-04-01 TDB: KARI solutions with
  tag-up data through 2026-09-29 and a prediction thereafter (not used, but compared). Danuri's node drifts by only
  about 0.004-0.007 deg/day, so its seasons repeat almost every year.
After the last tracking-based element (config/orbiters.yaml: elements_tracking_until) the node and the inclination
are extrapolated from the observed elements with a polynomial node trend and a linear inclination trend fitted to a
window ending there (config: season_fits; LRO central quadratic over 730 days, Danuri central linear over 300 days);
alternative fits give the range of each season boundary, and a hold-out test (fits ending earlier, compared with the
later tracking data) measures the extrapolation error (scripts/make_orbiter_seasons.py).

The beta angle is the angle between the orbit plane and the Moon-Sun direction:
    beta = asin(n . s),   n = (sin i sin Omega, -sin i cos Omega, cos i) in the ecliptic J2000 frame,
with s from the DE421 Moon-Sun vector rotated from the ICRF to the ecliptic of J2000 (obliquity 84381.448 arcsec, as in
Horizons). For a low-latitude target the overflight solar incidence is ~ arccos(cos(lat) cos(beta)) (Sun near the lunar
equator), so |beta| >= 55 deg marks low-Sun imaging seasons (incidence >= 55 deg, morphology) and |beta| <= 15 deg
near-noon seasons (albedo, poor topography). A season is an orbit-plane condition: it does not guarantee a pass within
pointing limits, operations, a manoeuvre-free orbit or a matched before/after pair.
"""
from __future__ import annotations
import re
import numpy as np
from . import ephem as E

OBLIQUITY_J2000_RAD = np.radians(84381.448 / 3600.0)
CENTRAL_FIT = (2, 730.0)                                   # (polynomial degree of the node trend, fit window in days)
ALTERNATIVE_FITS = [(2, 548.0), (2, 1095.0), (1, 365.0)]
_MON = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9, Oct=10, Nov=11, Dec=12)

def observed_until_jd(path):
    """JD (TDB) after which the Horizons header says the trajectory is a prediction ('... with prediction after
    YYYY-Mon-DD'); inf if the header has no such statement."""
    from astropy.time import Time
    m = re.search(r'prediction after (\d{4})-([A-Za-z]{3})-(\d{2})', open(path, errors='ignore').read(20000))
    if not m:
        return np.inf
    return Time(f'{m.group(1)}-{_MON[m.group(2)]:02d}-{m.group(3)}', scale='tdb').jd

def read_horizons_elements(path, tracking_until=None):
    """Parse a Horizons 'ELEMENTS' text table (format 10): returns dict of arrays jd_tdb, EC, IN, OM, W, A (deg, km) and
    observed_until_jd, the end of the tracking-based elements: tracking_until (ISO date, TDB) when given, else the date
    after which the header says the trajectory is a prediction, else the end of the table."""
    rows = []; cur = None
    on = False
    for line in open(path, errors='ignore'):
        if line.startswith('$$SOE'):
            on = True; continue
        if line.startswith('$$EOE'):
            break
        if not on:
            continue
        if '= A.D.' in line:
            cur = dict(jd_tdb=float(line.split('=')[0])); rows.append(cur); continue
        toks = line.replace('=', ' = ').split()
        for i, tkn in enumerate(toks):
            if tkn == '=' and i > 0 and i + 1 < len(toks):
                try:
                    cur[toks[i - 1]] = float(toks[i + 1])
                except ValueError:
                    pass
    out = {k: np.array([r[k] for r in rows]) for k in ('jd_tdb', 'EC', 'IN', 'OM', 'W', 'A')}
    out['OM_unwrapped'] = np.degrees(np.unwrap(np.radians(out['OM'])))
    if tracking_until is not None:
        from astropy.time import Time
        t_end = Time(str(tracking_until), scale='tdb').jd
    else:
        t_end = observed_until_jd(path)
    out['observed_until_jd'] = min(t_end, float(out['jd_tdb'][-1]))
    return out

def sun_dir_ecliptic(jd_tdb):
    """Unit vector from the Moon to the Sun in the ecliptic-of-J2000 frame (DE421)."""
    from astropy.time import Time
    from . import screening as S
    t = Time(np.atleast_1d(jd_tdb), format='jd', scale='tdb')
    _, _, moon, sun, _ = S.epoch_arrays(t)
    s = sun - moon; s /= np.linalg.norm(s, axis=1, keepdims=True)
    c, si = np.cos(OBLIQUITY_J2000_RAD), np.sin(OBLIQUITY_J2000_RAD)
    return np.stack([s[:, 0], c * s[:, 1] + si * s[:, 2], -si * s[:, 1] + c * s[:, 2]], axis=1)

def plane_elements(el, jd_tdb, fit=CENTRAL_FIT):
    fit = tuple(fit)
    """Inclination and node (deg) at jd_tdb: interpolated in the tracking-based part of the table, extrapolated after
    it with a polynomial node trend (degree fit[0]) and a linear inclination trend fitted to the final fit[1] days of
    tracking-based elements. Returns (i, Omega, extrapolated flag)."""
    jd = np.atleast_1d(np.asarray(jd_tdb, float)); t = el['jd_tdb']; t_obs = el['observed_until_jd']
    if (jd < t[0]).any():
        raise ValueError('date before the first tabulated element')
    obs = t <= t_obs
    inside = jd <= t_obs
    inc = np.interp(jd, t[obs], el['IN'][obs]); om = np.interp(jd, t[obs], el['OM_unwrapped'][obs])
    if (~inside).any():
        deg, days = fit
        m = obs & (t >= t_obs - days)
        c = np.polyfit(t[m] - t_obs, el['OM_unwrapped'][m], deg); ci = np.polyfit(t[m] - t_obs, el['IN'][m], 1)
        om = np.where(inside, om, np.polyval(c, jd - t_obs)); inc = np.where(inside, inc, np.polyval(ci, jd - t_obs))
    return inc, om % 360.0, ~inside

def beta_from_elements(inc_deg, om_deg, s):
    i, O = np.radians(inc_deg), np.radians(om_deg)
    n = np.stack([np.sin(i) * np.sin(O), -np.sin(i) * np.cos(O), np.cos(i)], axis=1)
    return np.degrees(np.arcsin(np.clip(np.einsum('ij,ij->i', n, s), -1, 1)))

def beta_angle(el, jd_tdb, fit=CENTRAL_FIT):
    inc, om, extrap = plane_elements(el, jd_tdb, tuple(fit))
    return beta_from_elements(inc, om, sun_dir_ecliptic(jd_tdb)), extrap

def node_rates(el, spans):
    """Linear node rate (deg/day) of the tabulated elements in each (label, jd0, jd1) span."""
    t = el['jd_tdb']; out = {}
    for lab, a, b in spans:
        m = (t >= a) & (t <= b)
        out[lab] = float(np.polyfit(t[m] - t[m][0], el['OM_unwrapped'][m], 1)[0]) if m.sum() > 10 else None
    return out

def holdout(el, cut_jd, fit=CENTRAL_FIT):
    """Extrapolation test: fit the node and inclination trends to tracking-based elements before cut_jd only, predict
    them to the end of the tracking-based table and compare. Returns the node error at the end, the largest |beta|
    error and the shifts (days) of season boundaries (|beta| >= 55 and <= 15 deg) that fall inside the test span."""
    t = el['jd_tdb']; t_obs = el['observed_until_jd']
    w = (t > cut_jd) & (t <= t_obs)
    jd = t[w]; s = sun_dir_ecliptic(jd)
    deg, days = tuple(fit)
    m = (t <= cut_jd) & (t >= cut_jd - days)
    om_p = np.polyval(np.polyfit(t[m] - cut_jd, el['OM_unwrapped'][m], deg), jd - cut_jd)
    in_p = np.polyval(np.polyfit(t[m] - cut_jd, el['IN'][m], 1), jd - cut_jd)
    b_true = beta_from_elements(el['IN'][w], el['OM_unwrapped'][w], s); b_pred = beta_from_elements(in_p, om_p, s)
    shifts = []
    for test in (lambda b: np.abs(b) >= 55.0, lambda b: np.abs(b) <= 15.0):
        A, B = intervals(jd, test(b_true)), intervals(jd, test(b_pred))
        for a in A:
            if not B:
                continue
            bb = min(B, key=lambda x: abs(x[0] - a[0]))
            if a[0] > jd[0] + 1 and bb[0] > jd[0] + 1:
                shifts.append(bb[0] - a[0])
            if a[1] < jd[-1] - 1 and bb[1] < jd[-1] - 1:
                shifts.append(bb[1] - a[1])
    return dict(span_days=float(jd[-1] - cut_jd), node_error_end_deg=float(om_p[-1] - el['OM_unwrapped'][w][-1]),
                max_abs_beta_error_deg=float(np.abs(b_pred - b_true).max()), boundary_shifts_days=[round(float(x), 1) for x in shifts],
                max_abs_boundary_shift_days=float(max(np.abs(shifts))) if shifts else None)

def intervals(jd, mask):
    """[start, end] JD pairs of contiguous True runs."""
    out = []; k = 0; n = len(mask)
    while k < n:
        if mask[k]:
            j = k
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((float(jd[k]), float(jd[j]))); k = j + 1
        else:
            k += 1
    return out

def overflight_incidence_deg(lat_deg, beta_deg):
    return np.degrees(np.arccos(np.clip(np.cos(np.radians(lat_deg)) * np.cos(np.radians(beta_deg)), -1, 1)))

SEASON_NOTE = ('orbit-plane illumination season: beta angle from JPL Horizons tracking-based LRO elements, extrapolated beyond 2026-09-02 '
               '(quadratic node trend; start_range and end_range from alternative fits); assumes no orbit manoeuvre and does not guarantee '
               'a sunlit pass over this point')

def season_status(t0, wins):
    """Next season (list of dicts from orbiter_seasons.json) ending on or after the datetime t0: its central dates and
    ranges, the days until it starts, whether t0 is inside it (central fit) and whether t0 falls within the uncertainty
    range of a boundary."""
    import datetime as dt
    day = lambda s: dt.datetime.strptime(s, '%Y-%m-%d')
    for w in wins:
        a_, b_ = day(w['start']), day(w['end'])
        if b_ >= t0:
            r = w.get('start_range', [w['start']] * 2) + w.get('end_range', [w['end']] * 2)
            near = day(r[0]) <= t0 <= day(r[1]) + dt.timedelta(days=1) or day(r[2]) <= t0 <= day(r[3]) + dt.timedelta(days=1)
            return dict(next_season=[w['start'], w['end']], start_range=w.get('start_range'), end_range=w.get('end_range'),
                        days_until=max(0, (a_ - t0).days), inside=bool(a_ <= t0 <= b_), boundary_uncertain=bool(near),
                        extrapolated=bool(w['extrapolated']))
    return None
