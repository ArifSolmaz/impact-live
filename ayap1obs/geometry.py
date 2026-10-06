"""Topocentric geometry for lunar surface points.

For an observer (lon, lat, height) and epoch, and N lunar surface points (selenographic ME lat/lon, optional
height above the 1737.4 km sphere), compute: visibility (spherical outward-normal test), emission angle,
solar incidence angle, altitude/azimuth of the impact point and of the Moon's centre, observer solar altitude
(twilight class), lunar phase angle / illuminated fraction / elongation, libration (sub-Earth point), sub-solar
point, distance and light time, and the point's position inside the apparent lunar disk.

All angles in degrees.  Vectorised over surface points; loops over epochs.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from astropy.time import Time
from . import ephem as E

C_KM_S = 299792.458

@dataclass
class EpochState:
    t: Time
    jd: float
    r_moon: np.ndarray      # geocentric Moon, ICRF km
    r_sun: np.ndarray       # geocentric Sun, ICRF km
    M: np.ndarray           # ICRF -> ME rotation
    subsolar_lon: float
    subsolar_lat: float
    subearth_lon: float     # geocentric libration (sub-Earth point)
    subearth_lat: float
    phase_angle: float      # Sun-Moon-Earth angle (deg)
    illum_frac: float
    elongation: float       # Sun-Earth-Moon angle (deg)
    distance_km: float
    light_time_s: float

def epoch_state(t) -> EpochState:
    t = E.to_time(t)
    jd = E.jd_tdb(t)
    rm = E.moon_geo(jd); rs = E.sun_geo(jd)
    M = E.icrf_to_me(jd)
    lat_s, lon_s = E.vec_to_latlon(M @ (rs - rm))
    lat_e, lon_e = E.vec_to_latlon(M @ (-rm))
    d = np.linalg.norm(rm)
    cos_phase = np.dot(-rm, rs - rm) / (d * np.linalg.norm(rs - rm))
    phase = np.degrees(np.arccos(np.clip(cos_phase, -1, 1)))
    elong = np.degrees(np.arccos(np.clip(np.dot(rm, rs) / (d * np.linalg.norm(rs)), -1, 1)))
    return EpochState(t, jd, rm, rs, M, float(lon_s[0]), float(lat_s[0]), float(lon_e[0]), float(lat_e[0]),
                      float(phase), float(0.5 * (1 + cos_phase)), float(elong), float(d), float(d / C_KM_S))

@dataclass
class Observer:
    name: str
    lon: float   # deg E
    lat: float   # deg N
    height_m: float = 0.0

def surface_geometry(es: EpochState, obs: Observer, lat_deg, lon_deg, height_km=None):
    """Return dict of arrays for N surface points as seen from `obs` at epoch `es`.

    Keys: visible (bool, spherical test), emission (deg, angle between local normal and direction to observer),
    incidence (deg, solar), sunlit (bool), alt_point, az_point (deg, topocentric, airless, geometric),
    alt_moon, az_moon, sun_alt_obs (deg), earth_alt_local (deg, elevation of the observer above the local
    lunar horizon of the impact point = 90 - emission), sun_alt_local, disk_x, disk_y (position in apparent disk,
    units of apparent lunar radius; x towards celestial east... defined via the sky-plane basis), range_km.
    """
    lat_deg = np.atleast_1d(np.asarray(lat_deg, float)); lon_deg = np.atleast_1d(np.asarray(lon_deg, float))
    r = E.R_MOON_KM + (0.0 if height_km is None else np.asarray(height_km, float))
    p_me = E.latlon_to_vec(lat_deg, lon_deg, r)                   # N x 3, ME frame
    n_me = p_me / np.linalg.norm(p_me, axis=1, keepdims=True)     # spherical normal (DEM slopes handled in terrain.py)
    p_icrf = p_me @ es.M                                          # (M^T p)^T = p^T M
    n_icrf = n_me @ es.M
    o = E.observer_gcrs(obs.lon, obs.lat, obs.height_m, es.t)     # observer, geocentric ICRF
    pos_geo = es.r_moon + p_icrf                                  # surface point, geocentric
    d_obs = o - pos_geo                                           # surface point -> observer
    rng = np.linalg.norm(d_obs, axis=1)
    d_hat = d_obs / rng[:, None]
    s_vec = es.r_sun - pos_geo
    s_hat = s_vec / np.linalg.norm(s_vec, axis=1, keepdims=True)
    cos_e = np.einsum('ij,ij->i', n_icrf, d_hat)
    cos_i = np.einsum('ij,ij->i', n_icrf, s_hat)
    emission = np.degrees(np.arccos(np.clip(cos_e, -1, 1)))
    incidence = np.degrees(np.arccos(np.clip(cos_i, -1, 1)))
    east, north, up = E.enu_basis_gcrs(obs.lon, obs.lat, es.t)
    alt_pt, az_pt = E.altaz_from_vector(-d_obs, east, north, up)   # direction observer -> point
    alt_moon, az_moon = E.altaz_from_vector((es.r_moon - o)[None, :], east, north, up)
    sun_alt, _ = E.altaz_from_vector((es.r_sun - o)[None, :], east, north, up)
    # position inside apparent disk: sky-plane basis at the Moon's centre
    c = es.r_moon - o; c_hat = c / np.linalg.norm(c)
    zc = np.array([0, 0, 1.0])
    ex = np.cross(zc, c_hat); ex /= np.linalg.norm(ex)            # towards increasing RA (celestial east)
    ey = np.cross(c_hat, ex)                                      # towards celestial north
    rel = p_icrf                                                  # offset of point from Moon centre
    ang_rad = E.R_MOON_KM / np.linalg.norm(c)
    disk_x = (rel @ ex) / np.linalg.norm(c) / ang_rad
    disk_y = (rel @ ey) / np.linalg.norm(c) / ang_rad
    return dict(visible=cos_e > 0, emission=emission, incidence=incidence, sunlit=cos_i > 0,
                alt_point=alt_pt, az_point=az_pt, alt_moon=float(alt_moon[0]), az_moon=float(az_moon[0]),
                sun_alt_obs=float(sun_alt[0]), earth_alt_local=90.0 - emission, sun_alt_local=90.0 - incidence,
                disk_x=disk_x, disk_y=disk_y, range_km=rng, cos_e=cos_e, cos_i=cos_i)

def twilight_class(sun_alt):
    """0: day (>-0.833), 1: civil, 2: nautical, 3: astronomical twilight, 4: night (< -18)."""
    s = np.asarray(sun_alt)
    return np.select([s > -0.833, s > -6, s > -12, s > -18], [0, 1, 2, 3], default=4)

def airmass(alt_deg):
    """Kasten & Young (1989) airmass; inf below horizon."""
    a = np.asarray(alt_deg, float)
    z = 90.0 - a
    with np.errstate(divide='ignore', invalid='ignore'):
        X = 1.0 / (np.cos(np.radians(z)) + 0.50572 * (96.07995 - z) ** -1.6364)
    return np.where(a > 0, X, np.inf)

def shadow_height_km(incidence_deg):
    """Height above a spherical Moon at which a vertical column over a night-side point first reaches sunlight
    (geometric terminator shadow, no terrain).  incidence > 90 means night side."""
    inc = np.radians(np.asarray(incidence_deg, float))
    theta = inc - np.pi / 2            # angular distance beyond the terminator
    h = np.where(theta > 0, E.R_MOON_KM * (1.0 / np.cos(np.minimum(theta, np.radians(89.9))) - 1.0), 0.0)
    return h

def limb_clearance_height_km(emission_deg):
    """Height a parcel directly above a point must reach to clear the spherical limb as seen from the observer
    (point with emission angle > 90 is behind the limb).  Returns 0 for visible points."""
    e = np.radians(np.asarray(emission_deg, float))
    theta = e - np.pi / 2
    return np.where(theta > 0, E.R_MOON_KM * (1.0 / np.cos(np.minimum(theta, np.radians(89.9))) - 1.0), 0.0)
