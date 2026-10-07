"""Validate the local DE421 + lunar-orientation implementation against JPL Horizons (DE441) tables fetched on
2026-10-05/06 (data/horizons/*.txt; the processed tables are archived, the raw API responses were not).

Every number written to the report is computed here; thresholds are asserted and the script exits non-zero on a
regression. Quantities are reported separately for geometric position, orientation and observables:
* range: the light-time-corrected (astrometric) Earth-Moon range |r_moon,bary(t - tau) - r_earth,bary(t)| with
  barycentric light time iterated, against Horizons 'delta' (stellar aberration does not change a range, so this
  checks the light-time convention, not aberration);
* sub-Earth point: (a) geometric (Moon and orientation at t), (b) astrometric (retarded relative vector, orientation
  at t - tau), (c) apparent (b plus stellar aberration from the Earth's barycentric velocity);
* sub-solar point: (a) geometric at t, (b) like-for-like apparent: at the emission time t - tau, Sun retarded by
  its light time to the Moon and aberrated by the Moon's barycentric velocity, orientation at t - tau;
* topocentric azimuth/elevation at TUG and Maunakea (geometric local model vs Horizons apparent airless values).
The 2027-2028 tables do not cover January-February 2029 (Horizons could not be re-queried from the analysis
environment); for that part of the domain only the internal DE421-versus-IAU orientation consistency is reported.
Also writes outputs/validation/iers_provenance.json (Earth-orientation table, coverage and values used)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ayap1obs import ephem as E
from astropy.time import Time
import warnings; warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs('outputs/validation', exist_ok=True)
C = 299792.458
AU = 149597870.7
THRESH = dict(range_km=0.05, subearth_best_deg=0.001, subsolar_like_deg=0.002, topo_deg=0.01)

def parse(fn, cols):
    rows = []
    for line in open(fn):
        if line.startswith('#') or not line.strip():
            continue
        p = line.split(); rows.append((f'{p[0]} {p[1]}', dict(zip(cols, [float(x) for x in p[2:]]))))
    return rows

def tdate(s):
    mon = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
    return Time(f"{s[:4]}-{mon[s[5:8]]:02d}-{s[9:11]} {s[12:]}", scale='utc')

def bary(jd):
    """Barycentric Earth, Moon, Sun positions (km) and Earth, Moon velocities (km/s)."""
    e = E._eph()
    emb, vemb = (np.asarray(x).ravel() for x in e.position_and_velocity('earthmoon', jd))
    mg, vmg = (np.asarray(x).ravel() for x in e.position_and_velocity('moon', jd))
    sun = np.asarray(e.position('sun', jd)).ravel()
    rE = emb - mg / (1 + E.EMRAT); vE = (vemb - vmg / (1 + E.EMRAT)) / 86400.0
    return rE, rE + mg, sun, vE, vE + vmg / 86400.0

def aberrate(u, v):
    """First-order stellar aberration of unit direction u for an observer moving with velocity v (km/s)."""
    b = v / C; up = u + b - (u @ b) * u
    return up / np.linalg.norm(up)

def lonlat(v):
    la, lo = E.vec_to_latlon(v)
    return lo[0] % 360.0, la[0]

def dlon(a, b):
    return (a - b + 180.0) % 360.0 - 180.0

checks = {}; out = ['# Ephemeris validation against JPL Horizons (DE441)', '',
                    'Processed Horizons tables fetched 2026-10-05/06 are in data/horizons (headers list centre, site and columns; the raw API '
                    'responses and request metadata were not archived). All residuals below are computed by this script.', '']
rows = parse('data/horizons/horizons_geocentric_2027-2028.txt', ['illu', 'angdiam', 'olon', 'olat', 'slon', 'slat', 'delta', 'deldot'])
R = {k: [] for k in ('range', 'se_geom', 'se_astr', 'se_app', 'ss_geom', 'ss_like', 'se_iau')}
for date, v in rows:
    t = tdate(date); jd = E.jd_tdb(t)
    rE, rM, rS, vE, vM = bary(jd)
    tau = np.linalg.norm(rM - rE) / C
    for _ in range(4):
        _, rM_r, _, _, _ = bary(jd - tau / 86400.0); tau = np.linalg.norm(rM_r - rE) / C
    _, rM_r, _, _, vM_r = bary(jd - tau / 86400.0)
    A = rM_r - rE
    R['range'].append(np.linalg.norm(A) - v['delta'] * AU)
    M_t = E.icrf_to_me(jd); M_e = E.icrf_to_me(jd - tau / 86400.0)
    lo, la = lonlat(M_t @ (-(rM - rE))); R['se_geom'].append([dlon(lo, v['olon']), la - v['olat']])
    lo, la = lonlat(M_e @ (-A)); R['se_astr'].append([dlon(lo, v['olon']), la - v['olat']])
    u_app = aberrate(A / np.linalg.norm(A), vE); lo, la = lonlat(M_e @ (-u_app)); R['se_app'].append([dlon(lo, v['olon']), la - v['olat']])
    lo, la = lonlat(M_t @ (rS - rM)); R['ss_geom'].append([dlon(lo, v['slon']), la - v['slat']])
    # like-for-like sub-solar: emission time t_e = t - tau; Sun retarded by its light time to the Moon; aberration by v_moon
    jd_e = jd - tau / 86400.0; ts = np.linalg.norm(rS - rM_r) / C
    for _ in range(3):
        rS_r = np.asarray(E._eph().position('sun', jd_e - ts / 86400.0)).ravel(); ts = np.linalg.norm(rS_r - rM_r) / C
    us = aberrate((rS_r - rM_r) / np.linalg.norm(rS_r - rM_r), vM_r); lo, la = lonlat(M_e @ us); R['ss_like'].append([dlon(lo, v['slon']), la - v['slat']])
    lo, la = lonlat(E.icrf_to_me(jd, 'iau') @ (-(rM - rE))); R['se_iau'].append([dlon(lo, v['olon']), la - v['olat']])
def stats(a):
    a = np.atleast_2d(np.array(a))
    return dict(lon_rms=float(np.sqrt(np.mean(a[:, 0] ** 2))), lon_max=float(np.abs(a[:, 0]).max()), lat_rms=float(np.sqrt(np.mean(a[:, 1] ** 2))), lat_max=float(np.abs(a[:, 1]).max()))
rr = np.array(R['range'])
checks['range_km'] = dict(rms=float(np.sqrt(np.mean(rr ** 2))), max=float(np.abs(rr).max()), n=len(rr))
for k in ('se_geom', 'se_astr', 'se_app', 'ss_geom', 'ss_like', 'se_iau'):
    checks[k] = stats(R[k])
out.append(f'## Geocentric table: {len(rows)} epochs at 10-day spacing, 2027-01-01 .. 2028-12-31')
out.append(f"- astrometric (light-time-corrected) range minus Horizons delta: rms {checks['range_km']['rms']:.4f} km, max {checks['range_km']['max']:.4f} km")
lab = dict(se_geom='sub-Earth, geometric (orientation and Moon at t)', se_astr='sub-Earth, astrometric (retarded vector, orientation at t - tau)',
           se_app='sub-Earth, apparent (astrometric + stellar aberration)', ss_geom='sub-solar, geometric at t', ss_like='sub-solar, apparent like-for-like (see header)',
           se_iau='sub-Earth, geometric, IAU (pck00011) orientation instead of DE421')
for k in ('se_geom', 'se_astr', 'se_app', 'ss_geom', 'ss_like', 'se_iau'):
    s = checks[k]
    out.append(f"- {lab[k]}: lon rms {s['lon_rms']:.5f} max {s['lon_max']:.5f} deg; lat rms {s['lat_rms']:.5f} max {s['lat_max']:.5f} deg")
best = min(('se_astr', 'se_app'), key=lambda k: checks[k]['lon_rms'])
checks['subearth_best'] = best
out.append(f"Best-matching sub-Earth convention: {lab[best]}. An angular residual of 0.006 deg corresponds to ~180 m of arc on the lunar surface, so the "
           f"geometric screening (which uses geometric vectors) is accurate to ~0.01 deg, not to metres.")
# PA->ME sign test
for sign in (+1, -1):
    M_alt = E._tk_matrix(tuple(sign * a for a in E._PA2ME_ANGLES), E._PA2ME_AXES); r = []
    for date, v in rows:
        jd = E.jd_tdb(tdate(date)); lo, la = lonlat((M_alt @ E.icrf_to_pa(jd)) @ (-E.moon_geo(jd))); r.append([dlon(lo, v['olon']), la - v['olat']])
    checks[f'pa2me_sign_{sign:+d}'] = stats(r)
out.append(f"- PA->ME offset sign test (geometric sub-Earth): sign +1 lon rms {checks['pa2me_sign_+1']['lon_rms']:.5f} deg; sign -1 lon rms {checks['pa2me_sign_-1']['lon_rms']:.5f} deg (the +1 convention is used)")
# topocentric tables (geometric local alt/az vs Horizons apparent airless az/el)
def topo(fn, cols, lon, lat, h_m):
    rows_t = parse(fn, cols); worst = 0.0; lines = []
    for date, v in rows_t:
        t = tdate(date); jd = E.jd_tdb(t); obs = E.observer_gcrs(lon, lat, h_m, t); east, north, up = E.enu_basis_gcrs(lon, lat, t)
        alt, az = E.altaz_from_vector(E.moon_geo(jd) - obs, east, north, up)
        d = max(abs(alt[0] - v['el']), abs(dlon(az[0], v['az'])) * np.cos(np.radians(v['el'])))
        worst = max(worst, d); lines.append(f"| {date} | {v['az']:.4f} | {az[0]:.4f} | {v['el']:.4f} | {alt[0]:.4f} |")
    return worst, lines
for fn, cols, site in [('data/horizons/horizons_tug_2027-06-10.txt', ['az', 'el', 'illu', 'angdiam', 'olon', 'olat', 'slon', 'slat', 'delta', 'deldot', 'sto'], (30.3356, 36.8247, 2500.0)),
                       ('data/horizons/horizons_tug_2027-03-15.txt', ['az', 'el', 'olon', 'olat', 'slon', 'slat'], (30.3356, 36.8247, 2500.0)),
                       ('data/horizons/horizons_smart1_maunakea.txt', ['az', 'el', 'illu', 'olon', 'olat', 'slon', 'slat'], (-155.47, 19.83, 4200.0))]:
    w, lines = topo(fn, cols, *site); checks[f'topo_{os.path.basename(fn)}'] = w
    out += ['', f'## Topocentric table {os.path.basename(fn)} (geometric local model vs Horizons apparent, airless)', '| UT | az H | az local | el H | el local |', '|---|---|---|---|---|'] + lines
    out.append(f'Worst residual (deg; azimuth scaled by cos el): {w:.4f}')
# 2029 part of the domain: internal orientation consistency only
r29 = []
for d in np.arange(0, 59, 2):
    t = Time('2029-01-01 00:00:00', scale='utc') + d; jd = E.jd_tdb(t); rm = E.moon_geo(jd)
    a = lonlat(E.icrf_to_me(jd) @ (-rm)); b = lonlat(E.icrf_to_me(jd, 'iau') @ (-rm)); r29.append([dlon(a[0], b[0]), a[1] - b[1]])
checks['de421_vs_iau_2029'] = stats(r29)
out += ['', '## January-February 2029 (no Horizons table)', f"DE421 versus IAU orientation, sub-Earth point: lon rms {checks['de421_vs_iau_2029']['lon_rms']:.5f} deg, lat rms {checks['de421_vs_iau_2029']['lat_rms']:.5f} deg "
        '(internal consistency of two orientation models, not an independent validation of DE421).']
# SMART-1 geometry (documented past event)
from ayap1obs import geometry as G
es = G.epoch_state('2006-09-03 05:42:21'); g = G.surface_geometry(es, G.Observer('MK', -155.47, 19.83, 4200), [-34.4], [-46.2])
out += ['', f"SMART-1 (2006-09-03 05:42:21 UTC, 34.4 S 46.2 W) from Maunakea: emission {g['emission'][0]:.1f} deg, incidence {g['incidence'][0]:.1f} deg ({g['incidence'][0]-90:.1f} deg beyond the terminator), "
        f"Moon altitude {g['alt_moon']:.1f} deg, Sun altitude {g['sun_alt_obs']:.1f} deg, illuminated fraction {es.illum_frac:.3f} (a night-side impact in Earthshine seen from Hawaii, as published)."]
# assertions
fails = []
if checks['range_km']['max'] > THRESH['range_km']: fails.append('range')
if checks[best]['lon_max'] > THRESH['subearth_best_deg'] or checks[best]['lat_max'] > THRESH['subearth_best_deg']: fails.append('sub-Earth like-for-like')
if checks['ss_like']['lon_max'] > THRESH['subsolar_like_deg'] or checks['ss_like']['lat_max'] > THRESH['subsolar_like_deg']: fails.append('sub-solar like-for-like')
if max(v for k, v in checks.items() if k.startswith('topo_')) > THRESH['topo_deg']: fails.append('topocentric')
checks['thresholds'] = THRESH; checks['failures'] = fails
out += ['', f"Thresholds: {THRESH}. Result: {'PASS' if not fails else 'FAIL: ' + ', '.join(fails)}"]
json.dump(checks, open('outputs/validation/ephemeris_validation.json', 'w'), indent=1)
open('outputs/validation/ephemeris_validation.md', 'w').write('\n'.join(out) + '\n')
json.dump(E.iers_provenance(), open('outputs/validation/iers_provenance.json', 'w'), indent=1)
print('\n'.join(out))
# the terrain-module tests are part of validation (no separate Makefile target)
import runpy
try:
    runpy.run_path(os.path.join('scripts', 'validate_terrain.py'), run_name='__main__')
except SystemExit as e:
    if e.code:
        fails.append('terrain tests')
sys.exit(1 if fails else 0)
