"""Tests of the terrain module (no real LOLA file is needed):
1. LDEM reader: a synthetic PDS3 product written with the official LOLA GDR conventions (global, westernmost
   longitude 0, easternmost 360, pixel-is-area, row 0 at +90 deg, 16-bit LSB integers, SCALING_FACTOR 0.5 m,
   OFFSET 1737400 m) carries bumps at known positions; the reader must return them at the right latitude and at
   longitude in the -180..180 convention (release 1 placed them 180 deg off).
2. Flat-sphere equivalence: with an all-zero DEM, the terrain-aware plume clearance must equal the exact spherical
   clearance for front-side, near-limb and far-side points and finite observer distance, and the spherical clearance
   must agree with R (sec(theta) - 1) (observer at infinity) to within the finite-distance difference.
3. Horizon on a flat sphere equals the curvature dip of the first sample.
Writes outputs/validation/terrain_validation.json and .md; exits non-zero on failure."""
import sys, os, json, tempfile, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
from ayap1obs import terrain as T, geometry as G, ephem as E
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{root}/outputs/validation', exist_ok=True)
results = []
def check(name, ok, detail):
    results.append(dict(test=name, passed=bool(ok), detail=detail)); print(('PASS' if ok else 'FAIL'), name, detail)

# 1. mock LDEM_4
res = 4; lines, samples = 180 * res, 360 * res
lat_c = 90.0 - (np.arange(lines) + 0.5) / res            # pixel centres
lon_c = (np.arange(samples) + 0.5) / res                  # 0..360 east
LAT, LON = np.meshgrid(lat_c, lon_c, indexing='ij')
def bump(lat0, lon0_360, h_m, w_deg=1.5):
    dlon = (LON - lon0_360 + 180) % 360 - 180
    return h_m * np.exp(-((LAT - lat0) ** 2 + (dlon * np.cos(np.radians(lat0))) ** 2) / (2 * w_deg ** 2))
h_m = bump(20.0, 30.0, 3000.0) + bump(-40.0, 200.0, 5000.0)          # +30 E and 200 E (= -160)
raw = np.round(h_m / 0.5).astype('<i2')
tmp = tempfile.mkdtemp()
img = os.path.join(tmp, 'LDEM_4.IMG'); lbl = os.path.join(tmp, 'LDEM_4.LBL')
raw.tofile(img)
open(lbl, 'w').write(f"""PDS_VERSION_ID = PDS3
OBJECT = IMAGE
  LINES = {lines}
  LINE_SAMPLES = {samples}
  SAMPLE_TYPE = LSB_INTEGER
  SAMPLE_BITS = 16
  SCALING_FACTOR = 0.5
  OFFSET = 1737400.0
END_OBJECT = IMAGE
OBJECT = IMAGE_MAP_PROJECTION
  MAP_PROJECTION_TYPE = "SIMPLE CYLINDRICAL"
  MAP_RESOLUTION = {res} <PIX/DEG>
  MAXIMUM_LATITUDE = 90.0 <DEG>
  MINIMUM_LATITUDE = -90.0 <DEG>
  WESTERNMOST_LONGITUDE = 0.0 <DEG>
  EASTERNMOST_LONGITUDE = 360.0 <DEG>
END_OBJECT = IMAGE_MAP_PROJECTION
END
""")
dem = T.LDEM(img, lbl)
for lat0, lon0, h_exp in [(20.0, 30.0, 3.0), (-40.0, -160.0, 5.0)]:
    h = float(dem.height(lat0, lon0))
    check(f'LDEM bump at lat {lat0:+.0f}, lon {lon0:+.0f}', abs(h - h_exp) < 0.05, f'height {h:.3f} km (expected {h_exp} km)')
h_wrong = float(dem.height(20.0, 30.0 - 180.0))
check('LDEM no bump 180 deg away', abs(h_wrong) < 0.05, f'height at lon -150: {h_wrong:.3f} km')
check('LDEM latitude orientation', abs(float(dem.height(-20.0, 30.0))) < 0.05, f'height at lat -20, lon 30: {float(dem.height(-20.0, 30.0)):.3f} km')
try:
    open(lbl.replace('LDEM_4', 'BAD'), 'w').write(open(lbl).read().replace('WESTERNMOST_LONGITUDE = 0.0', 'WESTERNMOST_LONGITUDE = -180.0'))
    os.link(img, img.replace('LDEM_4', 'BAD')); T.LDEM(img.replace('LDEM_4', 'BAD'), lbl.replace('LDEM_4', 'BAD'))
    check('LDEM rejects unsupported projection', False, 'no error raised')
except NotImplementedError as e:
    check('LDEM rejects unsupported projection', True, str(e)[:80])

# 2. flat-sphere equivalence of the plume clearance
flat = T.DEMBase(np.zeros((180, 360)), 'flat')
es = G.epoch_state('2028-04-01 18:00:00')
obs = E.observer_gcrs(30.335, 36.825, 2500.0, es.t)
rows = []
for lon in [-30.0, 70.0, 95.0, 100.0, 110.0, 125.0, 150.0]:
    lat = 0.0
    pos = G.surface_point_geo(es, lat, lon)[0]; n_icrf = E.latlon_to_vec(lat, lon, 1.0) @ es.M
    d = obs - pos; em = float(np.degrees(np.arccos(np.clip(n_icrf @ d / np.linalg.norm(d), -1, 1))))
    H_s = T.sphere_clearance_height_km(es, obs, lat, lon)
    H_t = T.plume_clearance_height_km(flat, es, obs, lat, lon, step_km=0.5)
    H_inf = float(G.limb_clearance_height_km(em))
    rows.append(dict(lon=lon, emission=em, sphere_km=H_s, terrain_flat_km=H_t, infinite_observer_km=H_inf))
    if np.isfinite(H_s):
        check(f'flat DEM = sphere (emission {em:.1f})', abs(H_t - H_s) <= 0.3, f'terrain {H_t:.2f} km, sphere {H_s:.2f} km')
        rel = abs(H_s - H_inf) / max(H_inf, 1.0)
        check(f'sphere vs R(sec-1) (emission {em:.1f})', rel < 0.02 or abs(H_s - H_inf) < 0.5, f'{H_s:.2f} vs {H_inf:.2f} km')
    else:
        check(f'flat DEM = sphere (emission {em:.1f})', not np.isfinite(H_t), 'both not cleared below the cap')
# 3. horizon on a flat sphere
hz = T.horizon_elevation(flat, 0.0, 0.0, 90.0, step_km=0.5)
check('flat-sphere horizon = first-sample curvature dip', abs(hz - (-np.degrees(0.5 / T.R / 2))) < 1e-3, f'{hz:.5f} deg')
ok = all(r['passed'] for r in results)
json.dump(dict(passed=ok, tests=results, clearance_table=rows), open(f'{root}/outputs/validation/terrain_validation.json', 'w'), indent=1, default=float)
with open(f'{root}/outputs/validation/terrain_validation.md', 'w') as f:
    f.write('# Terrain module tests\n\nNo real LOLA product could be downloaded in the analysis environment; the reader is tested on a synthetic file\n'
            'written with the official LOLA GDR conventions. Flat-sphere tests check the line-of-sight clearance.\n\n| test | result | detail |\n|---|---|---|\n')
    for r in results:
        f.write(f"| {r['test']} | {'PASS' if r['passed'] else 'FAIL'} | {r['detail']} |\n")
    f.write('\n| point lon | emission (deg) | sphere clearance (km) | flat-DEM clearance (km) | R(sec-1), observer at infinity (km) |\n|---|---|---|---|---|\n')
    for r in rows:
        f.write(f"| {r['lon']:.0f} | {r['emission']:.2f} | {r['sphere_km']:.2f} | {r['terrain_flat_km']:.2f} | {r['infinite_observer_km']:.2f} |\n")
print('ALL PASSED' if ok else 'FAILURES'); sys.exit(0 if ok else 1)
