"""Lunar terrain: DEM access, local horizons, line-of-sight clearance, and an illustrative synthetic-terrain experiment.

* `LDEM` reads the LRO/LOLA Gridded Data Record cylindrical products (PDS3 IMG + LBL, e.g. LDEM_4/LDEM_16). The label's
  map-projection keywords are parsed: the global products run from westernmost longitude 0 deg to easternmost 360 deg
  (pixel-is-area, centre longitude 180), so the array is rolled by half its columns into the -180..180 convention used
  here (release 1 read it without the roll, i.e. 180 deg off in longitude). Only global 0-360 / -90..90 products are
  supported; anything else raises. The reader is tested on a synthetic file written with the official conventions
  (tests in scripts/validate_terrain.py); no real LOLA file could be downloaded in the analysis environment, so it has
  not been run on the real product here.
* Without a real DEM, site-specific terrain tests are not made. Instead `synthetic_horizon_statistics` generates
  local Gaussian random terrain patches in a tangent plane (kilometre units, the same at every latitude) for three
  declared relief levels and returns the distribution of the terrain horizon elevation seen from a point; this is an
  illustrative sensitivity experiment, not a calibrated lunar prior and not a bound (real terrain can raise or lower
  the horizon).
* Horizon/obstruction geometry is exact on the sphere, and `plume_clearance_height_km` first enforces the spherical-limb
  clearance for the actual observer direction and then traces the whole line of sight over the terrain.
"""
from __future__ import annotations
import os, re, numpy as np
from . import ephem as E

R = E.R_MOON_KM

class DEMBase:
    """Equirectangular DEM in km, lat from +90 (row 0) to -90, lon from -180 to +180 (east-positive), pixel-is-area."""
    def __init__(self, z, label=''):
        self.z = np.asarray(z, dtype=np.float32)
        self.nlat, self.nlon = self.z.shape
        self.label = label
    def height(self, lat, lon):
        """Bilinear height (km) at lat/lon arrays (deg)."""
        lat = np.asarray(lat, float); lon = (np.asarray(lon, float) + 180.0) % 360.0 - 180.0
        fy = (90.0 - lat) / 180.0 * self.nlat - 0.5
        fx = (lon + 180.0) / 360.0 * self.nlon - 0.5
        y0 = np.floor(fy).astype(int); x0 = np.floor(fx).astype(int)
        wy = fy - y0; wx = fx - x0
        y0c = np.clip(y0, 0, self.nlat - 1); y1c = np.clip(y0 + 1, 0, self.nlat - 1)
        x0c = x0 % self.nlon; x1c = (x0 + 1) % self.nlon
        z = self.z
        return ((1 - wy) * ((1 - wx) * z[y0c, x0c] + wx * z[y0c, x1c]) + wy * ((1 - wx) * z[y1c, x0c] + wx * z[y1c, x1c]))

def parse_pds3_label(txt):
    """Numeric keywords of a PDS3 label (values with units such as <DEG> are accepted)."""
    out = {}
    for m in re.finditer(r'^\s*([A-Z_^]+)\s*=\s*"?([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)"?\s*(?:<[^>]*>)?\s*$', txt, re.M):
        out[m.group(1)] = float(m.group(2))
    for m in re.finditer(r'^\s*([A-Z_]+)\s*=\s*"?([A-Z_]+)"?\s*$', txt, re.M):
        out.setdefault(m.group(1), m.group(2))
    return out

class LDEM(DEMBase):
    """LOLA GDR cylindrical DEM reader (PDS3, global 0-360 products)."""
    def __init__(self, img_path, lbl_path=None):
        lbl_path = lbl_path or os.path.splitext(img_path)[0] + '.LBL'
        L = parse_pds3_label(open(lbl_path, 'r', errors='ignore').read())
        lines, samples = int(L['LINES']), int(L['LINE_SAMPLES'])
        bits = int(L.get('SAMPLE_BITS', 16)); stype = str(L.get('SAMPLE_TYPE', 'LSB_INTEGER'))
        endian = '<' if stype.startswith('LSB') else '>'
        dtype = {16: endian + 'i2', 32: endian + 'i4'}[bits]
        west, east = L.get('WESTERNMOST_LONGITUDE', 0.0), L.get('EASTERNMOST_LONGITUDE', 360.0)
        lat_max, lat_min = L.get('MAXIMUM_LATITUDE', 90.0), L.get('MINIMUM_LATITUDE', -90.0)
        if not (abs(west) < 1e-6 and abs(east - 360.0) < 1e-6 and abs(lat_max - 90) < 1e-6 and abs(lat_min + 90) < 1e-6):
            raise NotImplementedError(f'only global 0-360 / -90..90 products are supported (got W {west}, E {east}, lat {lat_min}..{lat_max})')
        res = L.get('MAP_RESOLUTION')
        if res is not None and abs(samples - 360.0 * res) > 0.5:
            raise ValueError('LINE_SAMPLES inconsistent with MAP_RESOLUTION')
        raw = np.fromfile(img_path, dtype=dtype).reshape(lines, samples).astype(np.float64)
        if 'MISSING_CONSTANT' in L:
            raw[raw == L['MISSING_CONSTANT']] = np.nan
        scale = L.get('SCALING_FACTOR', 0.5); offset = L.get('OFFSET', 1737400.0)
        z_m = raw * scale + offset - 1737400.0                         # metres above the 1737.4 km sphere
        z_m = np.roll(z_m, -samples // 2, axis=1)                      # columns 0..360 -> -180..180
        super().__init__(z_m / 1000.0, label=f'LOLA {os.path.basename(img_path)}')

def load_real_dem():
    """The LOLA DEM if present in data/dem, else None (no synthetic substitute is used for site-specific tests)."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ['LDEM_16.IMG', 'LDEM_4.IMG', 'ldem_16.img', 'ldem_4.img']:
        p = os.path.join(here, 'data', 'dem', name)
        if os.path.exists(p):
            return LDEM(p)
    return None

def local_frame(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    up = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    east = np.array([-np.sin(lo), np.cos(lo), 0.0])
    return east, np.cross(up, east), up

def great_circle_points(lat, lon, az_deg, dist_km):
    """Points along a great circle from (lat, lon) in azimuth az at distances dist_km (array)."""
    la, lo, az = np.radians(lat), np.radians(lon), np.radians(az_deg)
    d = np.asarray(dist_km) / R
    lat2 = np.arcsin(np.sin(la) * np.cos(d) + np.cos(la) * np.sin(d) * np.cos(az))
    lon2 = lo + np.arctan2(np.sin(az) * np.sin(d) * np.cos(la), np.cos(d) - np.sin(la) * np.sin(lat2))
    return np.degrees(lat2), np.degrees(lon2)

def horizon_elevation(dem: DEMBase, lat, lon, az_deg, max_dist_km=250.0, step_km=0.5):
    """Terrain horizon elevation (deg above the local horizontal) seen from (lat, lon) towards azimuth az (exact on
    the sphere: vertical offset (R+hj) cos(theta) - (R+h0), horizontal (R+hj) sin(theta))."""
    h0 = dem.height(lat, lon)
    dist = np.arange(step_km, max_dist_km + step_km, step_km)
    la2, lo2 = great_circle_points(lat, lon, az_deg, dist)
    hj = dem.height(la2, lo2); theta = dist / R
    return float(np.max(np.degrees(np.arctan2((R + hj) * np.cos(theta) - (R + h0), (R + hj) * np.sin(theta)))))

def observer_azimuth_at_point(es, obs_vec_geo, lat, lon):
    """Azimuth (deg from lunar north through east) of the direction from the surface point to an observer."""
    p_me = E.latlon_to_vec(lat, lon)
    d_me = es.M @ (obs_vec_geo - (es.r_moon + (es.M.T @ p_me)))
    east, north, up = local_frame(lat, lon)
    return float(np.degrees(np.arctan2(d_me @ east, d_me @ north)) % 360.0)

def earth_visible_with_terrain(dem: DEMBase, es, obs_vec_geo, lat, lon, emission_deg):
    az = observer_azimuth_at_point(es, obs_vec_geo, lat, lon)
    hz = horizon_elevation(dem, lat, lon, az); el = 90.0 - emission_deg
    return bool(el > hz), el, hz, el - hz

def sphere_clearance_height_km(es, obs_vec_geo, lat, lon, h_max=5000.0):
    """Minimum height above a surface point at which a parcel on the local vertical is visible from the observer,
    for a spherical Moon (exact, finite observer distance). 0 if the point itself is visible; inf if no height up
    to h_max clears the limb."""
    n0_me = E.latlon_to_vec(lat, lon, 1.0); n0 = es.M.T @ n0_me
    O = obs_vec_geo - es.r_moon                                       # observer, selenocentric (km)
    def blocked(H):
        Q = n0 * (R + H); d = O - Q
        t = -(Q @ d) / (d @ d)
        return 0 < t < 1 and np.linalg.norm(Q + t * d) < R
    if not blocked(1e-6):
        return 0.0
    if blocked(h_max):
        return np.inf
    lo, hi = 0.0, h_max
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if blocked(mid) else (lo, mid)
    return hi

def plume_clearance_height_km(dem, es, obs_vec_geo, lat, lon, max_h=None, step_km=0.25):
    """Minimum height above a surface point at which a parcel on the local vertical is visible from the observer:
    the spherical-limb clearance (exact) and, if a DEM is given, terrain along the entire line of sight (the ray is
    traced until it is higher than any terrain, 12 km). Returns inf if not cleared below max_h (default: the
    spherical clearance + 50 km)."""
    H_s = sphere_clearance_height_km(es, obs_vec_geo, lat, lon)
    if not np.isfinite(H_s) or dem is None:
        return H_s
    max_h = (H_s + 50.0) if max_h is None else max_h
    n0_me = E.latlon_to_vec(lat, lon, 1.0); O_me = es.M @ (obs_vec_geo - es.r_moon)
    h0 = float(dem.height(lat, lon))
    def clear(H):
        Q = n0_me * (R + h0 + H); d = O_me - Q; d /= np.linalg.norm(d)
        s = np.arange(step_km, 4000.0, step_km)
        P = Q[None, :] + s[:, None] * d[None, :]
        r = np.linalg.norm(P, axis=1); h_ray = r - R
        beyond = np.where(h_ray > 12.0)[0]
        upto = beyond[0] if len(beyond) else len(s)
        if upto == 0:
            return True
        la = np.degrees(np.arcsin(P[:upto, 2] / r[:upto])); lo = np.degrees(np.arctan2(P[:upto, 1], P[:upto, 0]))
        return bool(np.all(h_ray[:upto] > dem.height(la, lo)))
    for H in np.arange(H_s, max_h + 1e-9, 0.25):
        if clear(H):
            return float(H)
    return np.inf

# ------------------------------------------------------------------ illustrative synthetic terrain -----------------------
RELIEF = {   # RMS height over a 300-km patch (km) and spectral slope of the 2-D power spectrum (declared, illustrative)
    'low (mare-like)':      dict(rms_km=0.3, beta=3.6),
    'medium':               dict(rms_km=1.0, beta=3.6),
    'high (highland/polar)': dict(rms_km=2.0, beta=3.6),
}

def local_patch(rng, size_km=300.0, step_km=0.5, rms_km=1.0, beta=3.6):
    """Isotropic Gaussian random terrain on a tangent plane (km), power spectrum ~ k^-beta, RMS rms_km."""
    n = int(size_km / step_km)
    k = np.sqrt(np.fft.fftfreq(n, step_km)[None, :] ** 2 + np.fft.fftfreq(n, step_km)[:, None] ** 2); k[0, 0] = np.inf
    z = np.real(np.fft.ifft2(k ** (-beta / 2) * np.exp(2j * np.pi * rng.random((n, n)))))
    z -= z.mean(); z *= rms_km / z.std()
    return z

def synthetic_horizon_statistics(n=150, seed=7, size_km=300.0, step_km=0.5):
    """Horizon elevation (deg) seen from the centre of n synthetic patches towards a random azimuth, per relief level,
    including the Moon's curvature (drop d^2 / 2R). Returns {relief: array of n horizon elevations}."""
    rng = np.random.default_rng(seed)
    out = {}
    for name, p in RELIEF.items():
        hz = []
        for _ in range(n):
            z = local_patch(rng, size_km, step_km, p['rms_km'], p['beta'])
            c = z.shape[0] // 2; az = rng.uniform(0, 2 * np.pi)
            d = np.arange(step_km, size_km / 2 - step_km, step_km)
            iy = np.clip(np.round(c + d * np.cos(az) / step_km).astype(int), 0, z.shape[0] - 1); ix = np.clip(np.round(c + d * np.sin(az) / step_km).astype(int), 0, z.shape[1] - 1)
            rise = z[iy, ix] - z[c, c] - d ** 2 / (2 * R)
            hz.append(float(np.degrees(np.arctan2(rise, d)).max()))
        out[name] = np.array(hz)
    return out

def p_visible_given_emission(hz, emission_deg):
    """Fraction of synthetic horizons below the Earth's elevation (90 - emission) at the point."""
    return float(np.mean(np.asarray(hz) < 90.0 - emission_deg))
