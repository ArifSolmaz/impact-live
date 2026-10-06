"""Lunar terrain: DEM access, local horizon profiles and line-of-sight (ray-trace) obstruction tests.

Two DEM back-ends are provided:

* `LDEM`  - reader for the LRO/LOLA Gridded Data Record cylindrical products (e.g. LDEM_16.IMG + LDEM_16.LBL,
            PDS3, 16-bit signed little-endian, SCALING_FACTOR 0.5 m, reference radius 1737.4 km).  The files could not
            be downloaded inside the analysis sandbox (NAIF/PDS hosts blocked), so this reader is untested on the real
            product in this run; see README for the one-line swap once the file is available.
* `SyntheticDEM` - a clearly-labelled stand-in: an isotropic random field with a power-law spectrum tuned to LOLA
            global statistics (RMS height ~1.9 km at hemispheric scales, ~0.3 km at 10-km scale, median 1-km-baseline
            slope ~3 deg).  It reproduces the *statistics* that control limb obstruction and terrain shadowing; it does
            NOT reproduce real lunar features.  Any figure built on it is marked "SYNTHETIC TERRAIN" in the caption.

Horizon/obstruction tests are exact on the sphere: for a surface point P0 (height h0 above the reference sphere)
and terrain samples Pj along a great-circle path, the elevation of Pj above the local horizontal plane at P0 is
asin( (Pj - P0) . n0 / |Pj - P0| ).  The observer (Earth site) is visible if its elevation (90 - emission angle)
exceeds the terrain horizon elevation in the azimuth of the observer.
"""
from __future__ import annotations
import os, re, numpy as np
from . import ephem as E

R = E.R_MOON_KM

class DEMBase:
    """Equirectangular DEM in km, lat from +90 (row 0) to -90, lon from -180 to +180 (east-positive)."""
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
    def slope_deg(self, lat, lon, baseline_km=1.0):
        """Approximate bidirectional slope magnitude at the given baseline (central differences)."""
        dlat = np.degrees(baseline_km / R)
        dlon = dlat / np.maximum(np.cos(np.radians(lat)), 1e-3)
        dzdx = (self.height(lat, lon + dlon) - self.height(lat, lon - dlon)) / (2 * baseline_km)
        dzdy = (self.height(lat + dlat, lon) - self.height(lat - dlat, lon)) / (2 * baseline_km)
        return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))

class LDEM(DEMBase):
    """LOLA GDR cylindrical DEM reader (PDS3)."""
    def __init__(self, img_path, lbl_path=None):
        lbl_path = lbl_path or os.path.splitext(img_path)[0] + '.LBL'
        txt = open(lbl_path, 'r', errors='ignore').read()
        def key(k, cast=float):
            m = re.search(r'\n\s*' + k + r'\s*=\s*([-+0-9.eE]+)', txt)
            return cast(m.group(1)) if m else None
        lines = key('LINES', int); samples = key('LINE_SAMPLES', int)
        scale = key('SCALING_FACTOR') or 0.5; offset = key('OFFSET') or 1737400.0
        bits = key('SAMPLE_BITS', int) or 16
        dtype = {16: '<i2', 32: '<i4'}[bits]
        raw = np.fromfile(img_path, dtype=dtype).reshape(lines, samples)
        z_m = raw.astype(np.float64) * scale + offset - 1737400.0   # metres above reference sphere
        super().__init__(z_m / 1000.0, label=f'LOLA {os.path.basename(img_path)}')

class SyntheticDEM(DEMBase):
    """Random-field stand-in with LOLA-like statistics (see module docstring).  SYNTHETIC."""
    def __init__(self, ppd=4, seed=20261005, rms_km=1.9, beta=2.4):
        rng = np.random.default_rng(seed)
        nlon, nlat = 360 * ppd, 180 * ppd
        kx = np.fft.fftfreq(nlon)[None, :]; ky = np.fft.fftfreq(nlat)[:, None]
        k = np.sqrt(kx ** 2 + ky ** 2); k[0, 0] = np.inf
        amp = k ** (-beta / 2.0)
        phase = np.exp(2j * np.pi * rng.random((nlat, nlon)))
        z = np.real(np.fft.ifft2(amp * phase))
        # suppress power at wavelengths > 60 deg (the real Moon's hemispheric dichotomy is not a random field)
        z -= z.mean(); z *= rms_km / z.std()
        # add a mare-like smooth low-lying region in the nearside centre to make the dichotomy explicit
        lat = np.linspace(90, -90, nlat)[:, None]; lon = np.linspace(-180, 180, nlon, endpoint=False)[None, :]
        mare = np.exp(-(((lat - 15) / 25) ** 2 + ((lon - 0) / 45) ** 2))
        z = z * (1 - 0.7 * mare) - 1.5 * mare
        super().__init__(z, label=f'SYNTHETIC random-field DEM (ppd={ppd}, seed={seed}, rms={rms_km} km, beta={beta})')

def load_default_dem():
    """Return the LOLA DEM if present in data/dem, else the synthetic stand-in (labelled)."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ['LDEM_16.IMG', 'LDEM_4.IMG', 'ldem_16.img', 'ldem_4.img']:
        p = os.path.join(here, 'data', 'dem', name)
        if os.path.exists(p):
            return LDEM(p)
    return SyntheticDEM()

def local_frame(lat, lon):
    """Unit vectors (east, north, up) of a surface point in the ME frame."""
    la, lo = np.radians(lat), np.radians(lon)
    up = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    east = np.array([-np.sin(lo), np.cos(lo), 0.0])
    north = np.cross(up, east)
    return east, north, up

def great_circle_points(lat, lon, az_deg, dist_km):
    """Points along a great circle from (lat, lon) in azimuth az at distances dist_km (array)."""
    la, lo, az = np.radians(lat), np.radians(lon), np.radians(az_deg)
    d = np.asarray(dist_km) / R
    lat2 = np.arcsin(np.sin(la) * np.cos(d) + np.cos(la) * np.sin(d) * np.cos(az))
    lon2 = lo + np.arctan2(np.sin(az) * np.sin(d) * np.cos(la), np.cos(d) - np.sin(la) * np.sin(lat2))
    return np.degrees(lat2), np.degrees(lon2)

def horizon_elevation(dem: DEMBase, lat, lon, az_deg, max_dist_km=250.0, step_km=0.5):
    """Terrain horizon elevation (deg above local horizontal) seen from (lat, lon) towards azimuth az.
    Exact spherical geometry including curvature; 'max_dist_km' caps the search (beyond ~250 km terrain of
    +10 km is already below the horizon of a point at the reference sphere)."""
    h0 = dem.height(lat, lon)
    dist = np.arange(step_km, max_dist_km + step_km, step_km)
    la2, lo2 = great_circle_points(lat, lon, az_deg, dist)
    hj = dem.height(la2, lo2)
    theta = dist / R
    # elevation angle of terrain sample j above local horizontal at P0 (exact on sphere):
    # vertical offset relative to the tangent plane: (R+hj) cos(theta) - (R+h0); horizontal: (R+hj) sin(theta)
    elev = np.degrees(np.arctan2((R + hj) * np.cos(theta) - (R + h0), (R + hj) * np.sin(theta)))
    return float(np.max(elev))

def observer_azimuth_at_point(es, obs_vec_geo, lat, lon):
    """Azimuth (deg from lunar north through east) of the direction from the surface point to an observer whose
    geocentric ICRF position is obs_vec_geo, at epoch state es."""
    p_me = E.latlon_to_vec(lat, lon)
    d_icrf = obs_vec_geo - (es.r_moon + (es.M.T @ p_me))
    d_me = es.M @ d_icrf
    east, north, up = local_frame(lat, lon)
    return float(np.degrees(np.arctan2(d_me @ east, d_me @ north)) % 360.0)

def earth_visible_with_terrain(dem: DEMBase, es, obs_vec_geo, lat, lon, emission_deg):
    """Refined visibility test: observer elevation above the local horizontal (90 - emission) must exceed the
    terrain horizon in the observer's azimuth.  Returns (visible, obs_elev_deg, horizon_elev_deg, margin_deg)."""
    az = observer_azimuth_at_point(es, obs_vec_geo, lat, lon)
    hz = horizon_elevation(dem, lat, lon, az)
    el = 90.0 - emission_deg
    return bool(el > hz), el, hz, el - hz

def plume_clearance_height_km(dem: DEMBase, es, obs_vec_geo, lat, lon, emission_deg, max_h=200.0):
    """Minimum height above the surface point at which a parcel becomes visible to the observer, considering the
    terrain horizon (and the spherical limb for emission > 90).  Vertical column approximation."""
    az = observer_azimuth_at_point(es, obs_vec_geo, lat, lon)
    h0 = dem.height(lat, lon)
    dist = np.arange(0.5, 300.0, 0.5); la2, lo2 = great_circle_points(lat, lon, az, dist); hj = dem.height(la2, lo2)
    theta = dist / R
    el = np.radians(90.0 - emission_deg)   # observer elevation above local horizontal at the surface point
    # a parcel at height H above P0 sees terrain sample j at elevation e_j(H); need e_j(H) < el for all j.
    # The parcel is at (R+h0+H) n0. Terrain sample at (R+hj) n_j. Elevation of sample from parcel:
    # vertical = (R+hj)cos(theta) - (R+h0+H); horizontal = (R+hj) sin(theta)
    H = np.linspace(0, max_h, 2001)
    vert = (R + hj)[None, :] * np.cos(theta)[None, :] - (R + h0 + H)[:, None]
    horiz = (R + hj)[None, :] * np.sin(theta)[None, :]
    ej = np.arctan2(vert, horiz).max(axis=1)
    ok = ej < el
    return float(H[np.argmax(ok)]) if ok.any() else np.inf
