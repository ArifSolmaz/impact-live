"""Tests of the terrain module (no real LOLA file is needed):
1. LDEM reader: a synthetic PDS3 product written with the official LOLA GDR conventions (global, westernmost
   longitude 0, easternmost 360, pixel-is-area, row 0 at +90 deg, 16-bit LSB integers, SCALING_FACTOR 0.5 m,
   OFFSET 1737400 m) carries bumps at known positions; the reader must return them at the right latitude and at
   longitude in the -180..180 convention (release 1 placed them 180 deg off).
2. Flat-sphere equivalence: with an all-zero DEM, the terrain-aware plume clearance must equal the exact spherical
   clearance for front-side, near-limb and far-side points and finite observer distance, and the spherical clearance
   must agree with R (sec(theta) - 1) (observer at infinity) to within the finite-distance difference.
3. Horizon on a flat sphere equals the curvature dip of the first sample.
4. Label validation (re-audit GE-V2-06): labels with an unsupported projection type, without pixel-centre registration
   offsets, with west-positive longitudes or with a non-global extent must be rejected.
5. Raised-ridge regression (re-audit GE-13): a 2-km plateau around the tangent point of the line of sight from a parcel
   above a far-side point must raise the clearance above the spherical value (release 2.0 stopped tracing at the first
   ray sample above 12 km and returned the spherical value).
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
LABEL = f"""PDS_VERSION_ID = PDS3
OBJECT = IMAGE
  LINES                 = {lines}
  LINE_SAMPLES          = {samples}
  SAMPLE_TYPE           = LSB_INTEGER
  SAMPLE_BITS           = 16
  SCALING_FACTOR        = 0.5
  OFFSET                = 1737400.
END_OBJECT = IMAGE
OBJECT = IMAGE_MAP_PROJECTION
  MAP_PROJECTION_TYPE          = "SIMPLE CYLINDRICAL"
  MAP_RESOLUTION               = {res} <pix/deg>
  A_AXIS_RADIUS                = 1737.4 <km>
  B_AXIS_RADIUS                = 1737.4 <km>
  C_AXIS_RADIUS                = 1737.4 <km>
  POSITIVE_LONGITUDE_DIRECTION = "EAST"
  CENTER_LATITUDE              = 0 <deg>
  CENTER_LONGITUDE             = 180 <deg>
  MAXIMUM_LATITUDE             = 90 <deg>
  MINIMUM_LATITUDE             = -90 <deg>
  WESTERNMOST_LONGITUDE        = 0 <deg>
  EASTERNMOST_LONGITUDE        = 360 <deg>
  LINE_PROJECTION_OFFSET       = {lines / 2 - 0.5} <pix>
  SAMPLE_PROJECTION_OFFSET     = {samples / 2 - 0.5} <pix>
  COORDINATE_SYSTEM_TYPE       = "BODY-FIXED ROTATING"
  COORDINATE_SYSTEM_NAME       = "MEAN EARTH/POLAR AXIS OF DE421"
END_OBJECT = IMAGE_MAP_PROJECTION
END
"""                                            # keywords as in the official LDEM_4.LBL (PDS copy checked 2026-10-07)
open(lbl, 'w').write(LABEL)
dem = T.LDEM(img, lbl)
for lat0, lon0, h_exp in [(20.0, 30.0, 3.0), (-40.0, -160.0, 5.0)]:
    h = float(dem.height(lat0, lon0))
    check(f'LDEM bump at lat {lat0:+.0f}, lon {lon0:+.0f}', abs(h - h_exp) < 0.05, f'height {h:.3f} km (expected {h_exp} km)')
h_wrong = float(dem.height(20.0, 30.0 - 180.0))
check('LDEM no bump 180 deg away', abs(h_wrong) < 0.05, f'height at lon -150: {h_wrong:.3f} km')
check('LDEM latitude orientation', abs(float(dem.height(-20.0, 30.0))) < 0.05, f'height at lat -20, lon 30: {float(dem.height(-20.0, 30.0)):.3f} km')
# 4. label validation: each altered label must be rejected
BAD = {'unsupported projection type': ('"SIMPLE CYLINDRICAL"', '"POLAR STEREOGRAPHIC"'),
       'missing line registration offset': (f'  LINE_PROJECTION_OFFSET       = {lines / 2 - 0.5} <pix>\n', ''),
       'shifted sample registration': (f'SAMPLE_PROJECTION_OFFSET     = {samples / 2 - 0.5}', f'SAMPLE_PROJECTION_OFFSET     = {samples / 2}'),
       'west-positive longitudes': ('POSITIVE_LONGITUDE_DIRECTION = "EAST"', 'POSITIVE_LONGITUDE_DIRECTION = "WEST"'),
       'non-global extent': ('WESTERNMOST_LONGITUDE        = 0 <deg>', 'WESTERNMOST_LONGITUDE        = -180 <deg>'),
       'other body frame': ('"MEAN EARTH/POLAR AXIS OF DE421"', '"PRINCIPAL AXIS"')}
for k, (name, (a, b)) in enumerate(BAD.items()):
    assert a in LABEL, name
    img_b = os.path.join(tmp, f'BAD{k}.IMG'); lbl_b = os.path.join(tmp, f'BAD{k}.LBL')
    open(lbl_b, 'w').write(LABEL.replace(a, b)); os.link(img, img_b)
    try:
        T.LDEM(img_b, lbl_b); check(f'LDEM rejects label: {name}', False, 'accepted')
    except (NotImplementedError, ValueError) as e:
        check(f'LDEM rejects label: {name}', True, str(e)[:90])

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
# 5. raised-ridge regression: 2-km plateau around the tangent point of the sight line from a parcel above 0 N / 100 E
class PlateauDEM(T.DEMBase):
    def __init__(self, lat0, lon0, h_km, radius_deg):
        self.z = np.array([[0.0, h_km]], np.float32); self.nlat, self.nlon = self.z.shape; self.label = 'plateau'
        self.p0 = E.latlon_to_vec(lat0, lon0, 1.0); self.h = h_km; self.rad = np.radians(radius_deg)
    def height(self, lat, lon):
        p = E.latlon_to_vec(np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(lon, float)), 1.0)
        out = np.where(np.arccos(np.clip(p @ self.p0, -1, 1)) <= self.rad, self.h, 0.0)
        return out if np.ndim(lat) else float(out[0])
ridge_rows = []
for obs_name, obs_vec in [('geocentre', np.zeros(3)), ('TUG', obs)]:
    lat, lon = 0.0, 100.0
    H_s = T.sphere_clearance_height_km(es, obs_vec, lat, lon)
    n0 = E.latlon_to_vec(lat, lon, 1.0); O_me = es.M @ (obs_vec - es.r_moon)
    Q = n0 * (T.R + H_s); d = O_me - Q; d /= np.linalg.norm(d); P_ca = Q + max(0.0, -float(Q @ d)) * d
    lat_t = float(np.degrees(np.arcsin(P_ca[2] / np.linalg.norm(P_ca)))); lon_t = float(np.degrees(np.arctan2(P_ca[1], P_ca[0])))
    ridge = PlateauDEM(lat_t, lon_t, 2.0, 1.5)
    H_r = T.plume_clearance_height_km(ridge, es, obs_vec, lat, lon, step_km=0.25)
    ridge_rows.append(dict(observer=obs_name, sphere_km=H_s, ridge_km=H_r, tangent_lat=lat_t, tangent_lon=lon_t))
    check(f'2-km ridge at the tangent raises the clearance ({obs_name})', np.isfinite(H_r) and H_r >= H_s + 1.9,
          f'sphere {H_s:.2f} km, with ridge {H_r:.2f} km; tangent near {lat_t:.2f} N / {lon_t:.2f} E')
ok = all(r['passed'] for r in results)
json.dump(dict(passed=ok, tests=results, clearance_table=rows, ridge_regression=ridge_rows), open(f'{root}/outputs/validation/terrain_validation.json', 'w'), indent=1, default=float)
with open(f'{root}/outputs/validation/terrain_validation.md', 'w') as f:
    f.write('# Terrain module tests\n\nNo real LOLA product could be downloaded in the analysis environment; the reader is tested on a synthetic file\n'
            'written with the official LOLA GDR label conventions; altered labels must be rejected. Flat-sphere and raised-ridge tests check the\n'
            'line-of-sight clearance.\n\n| test | result | detail |\n|---|---|---|\n')
    for r in results:
        f.write(f"| {r['test']} | {'PASS' if r['passed'] else 'FAIL'} | {r['detail']} |\n")
    f.write('\n| point lon | emission (deg) | sphere clearance (km) | flat-DEM clearance (km) | R(sec-1), observer at infinity (km) |\n|---|---|---|---|---|\n')
    for r in rows:
        f.write(f"| {r['lon']:.0f} | {r['emission']:.2f} | {r['sphere_km']:.2f} | {r['terrain_flat_km']:.2f} | {r['infinite_observer_km']:.2f} |\n")
print('ALL PASSED' if ok else 'FAILURES'); sys.exit(0 if ok else 1)
