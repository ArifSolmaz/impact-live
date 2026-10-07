"""Ephemeris and lunar-orientation layer.

Sources
-------
* DE421 (Folkner, Williams & Boggs 2009, JPL IOM 343R-08-003): planetary positions and lunar libration
  Euler angles (phi, theta, psi), read with jplephem's legacy reader from the PyPI package 'de421' 2008.1.
* Lunar PA->ME offset for DE421 from NAIF frame kernel moon_080317.tf (angles 67.92", 78.56", 0.30"; axes 3,2,1).
* IAU 2009/2015 Moon orientation series as given in NAIF pck00011.tpc (cross-check only).
* Earth orientation: astropy (ERFA) with the IERS table shipped in the pinned astropy-iers-data package (IERS-A
  'finals2000A' series: measured values, then IERS predictions; no download at run time). For epochs beyond the
  table's last entry astropy holds UT1-UTC at the last tabulated value and uses a 50-year mean polar motion
  (`iers_degraded_accuracy = 'ignore'` turns the error into a warning). The table version, coverage and the values
  used are recorded by `iers_provenance()` (outputs/validation/iers_provenance.json). No accuracy better than the
  following is claimed for 2027-2029 epochs: UTC is kept within 0.9 s of UT1, so the held UT1-UTC value can be wrong by
  up to 0.9 s + |held value| (about 1.05 s for the archived table), i.e. up to ~16 arcsec of Earth rotation
  (0.004 deg in topocentric altitude/azimuth of the Moon); iers_provenance() records the exact bound;
  polar motion errors are below 1 arcsec. This is irrelevant to the 20-deg altitude cuts and hour-scale planning
  here, but sub-arcsecond pointing near an actual event needs current Earth-orientation parameters.

Conventions
-----------
Vectors are ICRF/GCRS cartesian in km unless stated.  Selenographic coordinates are in the Mean Earth/Polar-axis
(ME) frame, latitude north-positive, longitude east-positive, consistent with Horizons' Moon output.
"""
from __future__ import annotations
import os, sys, functools
import numpy as np
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import EarthLocation, ITRS, GCRS, CartesianRepresentation
from astropy.utils import iers
iers.conf.auto_download = False
iers.conf.iers_degraded_accuracy = 'ignore'

KERNEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'kernels')
sys.path.insert(0, KERNEL_DIR)
from jplephem.ephem import Ephemeris  # legacy reader for the .npy packages
import de421 as _de421pkg

R_MOON_KM = 1737.4          # LOLA reference sphere
EMRAT = 81.30056907419062   # DE421 Earth/Moon mass ratio
ARCSEC = np.pi / 180.0 / 3600.0
DEG = np.pi / 180.0

@functools.lru_cache(maxsize=1)
def _eph():
    return Ephemeris(_de421pkg)

def to_time(t):
    if isinstance(t, Time):
        return t
    return Time(t, scale='utc')

def jd_tdb(t):
    """TDB Julian date (float) for an astropy Time or ISO string (UTC)."""
    t = to_time(t)
    return t.tdb.jd

# --- rotation helpers (SPICE convention: rotate the coordinate frame) ---------------------------------
def rotx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])

def roty(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])

def rotz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])

_ROT = {1: rotx, 2: roty, 3: rotz}

# --- bodies -------------------------------------------------------------------------------------------
def moon_geo(jd):
    """Geocentric Moon position, ICRF, km (DE421)."""
    return np.asarray(_eph().position('moon', jd)).ravel()

def sun_geo(jd):
    """Geocentric Sun position, ICRF, km (DE421)."""
    e = _eph()
    emb = np.asarray(e.position('earthmoon', jd)).ravel()
    moon = np.asarray(e.position('moon', jd)).ravel()
    sun = np.asarray(e.position('sun', jd)).ravel()
    earth = emb - moon / (1.0 + EMRAT)
    return sun - earth

def moon_sun(jd):
    """Selenocentric Sun position ICRF km."""
    return sun_geo(jd) - moon_geo(jd)

# --- lunar orientation --------------------------------------------------------------------------------
# DE421 PA -> ME_DE421 (NAIF moon_080317.tf): TKFRAME_31007_ANGLES = (67.92, 78.56, 0.30) arcsec, AXES = (3, 2, 1)
_PA2ME_ANGLES = (67.92 * ARCSEC, 78.56 * ARCSEC, 0.30 * ARCSEC)
_PA2ME_AXES = (3, 2, 1)

def _tk_matrix(angles, axes):
    """Matrix converting vectors from the *relative* frame (PA) into the *defined* frame (ME), M @ v_PA.
    SPICE TKFRAME semantics: the kernel's matrix [a3]_ax3 [a2]_ax2 [a1]_ax1 maps the defined frame (ME) to the relative
    frame (PA); its inverse is used here.  Both sign conventions were tested against JPL Horizons sub-Earth points
    (scripts/validate_ephemeris.py): this one leaves 0.004 deg rms (explained by Horizons' apparent-direction
    convention), the other 0.04 deg (rejected)."""
    a1, a2, a3 = angles
    x1, x2, x3 = axes
    M_def2rel = _ROT[x3](a3) @ _ROT[x2](a2) @ _ROT[x1](a1)
    return M_def2rel.T

PA2ME = _tk_matrix(_PA2ME_ANGLES, _PA2ME_AXES)

def icrf_to_pa(jd):
    """Matrix converting ICRF vectors to the DE421 principal-axis (PA) frame."""
    phi, theta, psi = np.asarray(_eph().position('librations', jd)).ravel()
    return rotz(psi) @ rotx(theta) @ rotz(phi)

def icrf_to_me(jd, model='de421'):
    """Matrix converting ICRF vectors to the Mean-Earth/Polar-axis frame.
    model='de421' : DE421 librations + PA->ME offset (default, validated against Horizons)
    model='iau'   : pck00011 analytic series (cross-check)"""
    if model == 'de421':
        return PA2ME @ icrf_to_pa(jd)
    elif model == 'iau':
        return _iau_icrf_to_me(jd)
    raise ValueError(model)

# pck00011.tpc Moon (BODY301) constants (NAIF, file dated 2022-12-27; IAU WG 2009/2015 values)
_POLE_RA = (269.9949, 0.0031, 0.0)
_POLE_DEC = (66.5392, 0.0130, 0.0)
_PM = (38.3213, 13.17635815, -1.4e-12)
_NPR = [-3.8787, -0.1204, 0.0700, -0.0172, 0.0, 0.0072, 0.0, 0.0, 0.0, -0.0052, 0.0, 0.0, 0.0043]
_NPD = [1.5419, 0.0239, -0.0278, 0.0068, 0.0, -0.0029, 0.0009, 0.0, 0.0, 0.0008, 0.0, 0.0, -0.0009]
_NPW = [3.5610, 0.1208, -0.0642, 0.0158, 0.0252, -0.0066, -0.0047, -0.0046, 0.0028, 0.0052, 0.0040, 0.0019, -0.0044]
_NPANG = [(125.045, -1935.5364525), (250.089, -3871.0729050), (260.008, 475263.3328725), (176.625, 487269.6299850),
          (357.529, 35999.0509575), (311.589, 964468.4993100), (134.963, 477198.8693250), (276.617, 12006.3007650),
          (34.226, 63863.5132425), (15.134, -5806.6093575), (119.743, 131.8406400), (239.961, 6003.1503825),
          (25.053, 473327.7964200)]

def _iau_icrf_to_me(jd):
    d = jd - 2451545.0
    T = d / 36525.0
    E = np.array([(a + b * T) * DEG for a, b in _NPANG])
    ra = _POLE_RA[0] + _POLE_RA[1] * T + np.sum(np.array(_NPR) * np.sin(E))
    dec = _POLE_DEC[0] + _POLE_DEC[1] * T + np.sum(np.array(_NPD) * np.cos(E))
    w = _PM[0] + _PM[1] * d + _PM[2] * d * d + np.sum(np.array(_NPW) * np.sin(E))
    return rotz(w * DEG) @ rotx((90.0 - dec) * DEG) @ rotz((90.0 + ra) * DEG)

# --- Earth side ---------------------------------------------------------------------------------------
def iers_provenance(epochs=('2027-09-01', '2028-04-01', '2029-03-01')):
    """Version, coverage and the UT1-UTC / polar-motion values actually used for representative epochs."""
    import importlib.metadata as md, hashlib, glob
    t = iers.IERS_Auto.open()
    flag = np.array(t['UT1Flag']); mjd = np.array(t['MJD'].value if hasattr(t['MJD'], 'value') else t['MJD'])
    meas = mjd[flag == 'I']; pred = mjd[flag == 'P']
    import astropy_iers_data as aid
    files = sorted(glob.glob(os.path.join(os.path.dirname(aid.__file__), 'data', 'finals2000A*')))
    out = dict(package='astropy-iers-data', version=md.version('astropy-iers-data'), astropy=md.version('astropy'),
               files={os.path.basename(f): hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in files},
               measured_until=Time(meas.max(), format='mjd').iso[:10] if len(meas) else None,
               predicted_until=Time(pred.max(), format='mjd').iso[:10] if len(pred) else None,
               beyond_table='UT1-UTC held at the last tabulated value; polar motion = 50-year mean (astropy behaviour)', epochs={})
    held = float(u.Quantity(t['UT1_UTC'][-1]).to_value(u.s))
    bound = 0.9 + abs(held)                     # |UT1 - UTC| < 0.9 s by IERS policy, plus the held value itself (re-audit GE-V2-07)
    out.update(ut1_utc_held_s=held, ut1_utc_bound_beyond_table_s=bound, rotation_bound_arcsec=bound * 15.0411,
               bound_note='0.9 s + |held UT1-UTC|; Earth rotation 15.0411 arcsec per second of time')
    for e in epochs:
        tt = Time(e, scale='utc')
        with np.errstate(all='ignore'):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                dut = float(u.Quantity(t.ut1_utc(tt)).to_value(u.s))
                from astropy.coordinates.builtin_frames.utils import get_polar_motion
                xp, yp = (x * u.rad for x in get_polar_motion(tt))   # the values the transformations actually use
        status = 'measured' if len(meas) and tt.mjd <= meas.max() else ('predicted' if len(pred) and tt.mjd <= pred.max() else 'held beyond table')
        out['epochs'][e] = dict(ut1_utc_s=dut, pm_x_arcsec=float(xp.to_value(u.arcsec)), pm_y_arcsec=float(yp.to_value(u.arcsec)), status=status)
    return out

def observer_gcrs(lon_deg, lat_deg, height_m, t):
    """Observer position in GCRS (km) at astropy Time t."""
    loc = EarthLocation.from_geodetic(lon_deg * u.deg, lat_deg * u.deg, height_m * u.m)
    pos, vel = loc.get_gcrs_posvel(to_time(t))
    return pos.xyz.to_value(u.km)

def itrs_to_gcrs_matrix(t):
    """3x3 matrix R such that v_gcrs = R @ v_itrs (directions), at Time t."""
    t = to_time(t)
    eye = np.eye(3)
    itrs = ITRS(CartesianRepresentation(eye[0], eye[1], eye[2], unit=u.km), obstime=t)
    g = itrs.transform_to(GCRS(obstime=t)).cartesian.xyz.to_value(u.km)
    # columns of g are images of basis vectors; normalise to remove any tiny scaling
    R = g / np.linalg.norm(g, axis=0, keepdims=True)
    return R

def enu_basis_gcrs(lon_deg, lat_deg, t):
    """Unit East, North, Up vectors (geodetic) of a site expressed in GCRS at time t."""
    lon, lat = lon_deg * DEG, lat_deg * DEG
    up = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    east = np.array([-np.sin(lon), np.cos(lon), 0.0])
    north = np.cross(up, east)
    R = itrs_to_gcrs_matrix(t)
    return R @ east, R @ north, R @ up

def altaz_from_vector(d, east, north, up):
    """Altitude and azimuth (deg, az from North through East) of direction(s) d (N x 3) in GCRS."""
    d = np.atleast_2d(d)
    dn = d / np.linalg.norm(d, axis=1, keepdims=True)
    alt = np.degrees(np.arcsin(np.clip(dn @ up, -1, 1)))
    az = np.degrees(np.arctan2(dn @ east, dn @ north)) % 360.0
    return alt, az

def latlon_to_vec(lat_deg, lon_deg, r=R_MOON_KM):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    return np.stack([r * np.cos(lat) * np.cos(lon), r * np.cos(lat) * np.sin(lon), r * np.sin(lat)], axis=-1)

def vec_to_latlon(v):
    v = np.atleast_2d(v)
    r = np.linalg.norm(v, axis=1)
    lat = np.degrees(np.arcsin(v[:, 2] / r))
    lon = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
    return lat, lon
