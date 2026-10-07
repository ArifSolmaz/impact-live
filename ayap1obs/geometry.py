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

def surface_geometry(es: EpochState, obs: Observer, lat_deg, lon_deg, height_km=None, t_obs=None):
    """Return dict of arrays for N surface points as seen from `obs` at epoch `es`.

    Keys: visible (bool, spherical test), emission (deg, angle between local normal and direction to observer),
    incidence (deg, solar), sunlit (bool), alt_point, az_point (deg, topocentric, airless, geometric),
    alt_moon, az_moon, sun_alt_obs (deg), earth_alt_local (deg, elevation of the observer above the local
    lunar horizon of the impact point = 90 - emission), sun_alt_local, disk_x, disk_y (position in apparent disk,
    units of apparent lunar radius; x towards celestial east... defined via the sky-plane basis), range_km.
    t_obs: observer time (photon reception) if different from the epoch of the lunar state es (emission); the
    observer's position and horizon are then taken at t_obs while the Moon, its orientation and the Sun are at es.t
    (one-way light time in the geocentric frame; annual aberration and the Earth's barycentric displacement cancel to
    first order there, and the remaining diurnal aberration, < 0.3 arcsec, is neglected).
    """
    lat_deg = np.atleast_1d(np.asarray(lat_deg, float)); lon_deg = np.atleast_1d(np.asarray(lon_deg, float))
    r = E.R_MOON_KM + (0.0 if height_km is None else np.asarray(height_km, float))
    p_me = E.latlon_to_vec(lat_deg, lon_deg, r)                   # N x 3, ME frame
    n_me = p_me / np.linalg.norm(p_me, axis=1, keepdims=True)     # spherical normal (DEM slopes handled in terrain.py)
    p_icrf = p_me @ es.M                                          # (M^T p)^T = p^T M
    n_icrf = n_me @ es.M
    t_o = es.t if t_obs is None else E.to_time(t_obs)
    o = E.observer_gcrs(obs.lon, obs.lat, obs.height_m, t_o)      # observer, geocentric ICRF (at reception)
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
    east, north, up = E.enu_basis_gcrs(obs.lon, obs.lat, t_o)
    alt_pt, az_pt = E.altaz_from_vector(-d_obs, east, north, up)   # direction observer -> point
    alt_moon, az_moon = E.altaz_from_vector((es.r_moon - o)[None, :], east, north, up)
    sun_alt, _ = E.altaz_from_vector((es.r_sun - o)[None, :], east, north, up)
    # position inside the apparent disk: exact gnomonic (tangent-plane) offsets of the observer-to-point direction from
    # the observer-to-centre direction, in units of the apparent lunar radius asin(R/d)
    disk_x, disk_y = disk_coordinates(es, o, pos_geo)
    return dict(visible=cos_e > 0, emission=emission, incidence=incidence, sunlit=cos_i > 0,
                alt_point=alt_pt, az_point=az_pt, alt_moon=float(alt_moon[0]), az_moon=float(az_moon[0]),
                sun_alt_obs=float(sun_alt[0]), earth_alt_local=90.0 - emission, sun_alt_local=90.0 - incidence,
                disk_x=disk_x, disk_y=disk_y, range_km=rng, cos_e=cos_e, cos_i=cos_i)

def sky_basis(es: EpochState, obs_gcrs):
    """Unit vectors (towards the Moon's centre, celestial east, celestial north) as seen from obs_gcrs (ICRF, km)."""
    c = es.r_moon - obs_gcrs; c_hat = c / np.linalg.norm(c)
    ex = np.cross(np.array([0, 0, 1.0]), c_hat); ex /= np.linalg.norm(ex)    # increasing RA (celestial east)
    ey = np.cross(c_hat, ex)                                                  # celestial north
    return c_hat, ex, ey, float(np.linalg.norm(c))

def disk_coordinates(es: EpochState, obs_gcrs, pos_geo):
    """Exact gnomonic offsets (east, north) of points pos_geo (N x 3, geocentric ICRF km) from the Moon's centre as
    seen from obs_gcrs, in units of the apparent lunar radius asin(R/d_centre)."""
    c_hat, ex, ey, dc = sky_basis(es, obs_gcrs)
    d = np.atleast_2d(pos_geo) - obs_gcrs; d /= np.linalg.norm(d, axis=1, keepdims=True)
    w = d @ c_hat
    xi, eta = (d @ ex) / w, (d @ ey) / w
    rad = np.tan(np.arcsin(E.R_MOON_KM / dc))
    return xi / rad, eta / rad

def sky_offset_arcsec(es: EpochState, obs_gcrs, pos_geo, ref_geo):
    """Gnomonic offset (east, north) in arcsec of pos_geo from ref_geo as seen from obs_gcrs."""
    c = ref_geo - obs_gcrs; c_hat = c / np.linalg.norm(c)
    ex = np.cross(np.array([0, 0, 1.0]), c_hat); ex /= np.linalg.norm(ex); ey = np.cross(c_hat, ex)
    d = np.atleast_2d(pos_geo) - obs_gcrs; d /= np.linalg.norm(d, axis=1, keepdims=True)
    w = d @ c_hat
    return np.degrees((d @ ex) / w) * 3600.0, np.degrees((d @ ey) / w) * 3600.0

def surface_point_geo(es: EpochState, lat_deg, lon_deg, height_km=0.0):
    """Geocentric ICRF position (km) of a surface point."""
    p_me = E.latlon_to_vec(np.atleast_1d(lat_deg), np.atleast_1d(lon_deg), E.R_MOON_KM + height_km)
    return es.r_moon + p_me @ es.M

def local_ne_offsets(lat_deg, lon_deg, d_north_km, d_east_km):
    """Selenographic lat/lon of a point displaced d_north/d_east (km) along the surface from (lat, lon)."""
    from .terrain import great_circle_points
    dist = np.hypot(d_north_km, d_east_km); az = np.degrees(np.arctan2(d_east_km, d_north_km))
    return great_circle_points(lat_deg, lon_deg, az, dist)

def light_time_s(t_emit, obs: Observer, lat_deg, lon_deg, n_iter=3):
    """One-way light time (s) from a surface point at emission time t_emit to the observer at reception, solved
    iteratively with the observer at t_emit + tau (geocentric frame)."""
    from astropy.time import TimeDelta
    t0 = E.to_time(t_emit); es0 = epoch_state(t0)
    P = surface_point_geo(es0, lat_deg, lon_deg)[0]; tau = 0.0
    for _ in range(n_iter):
        O = E.observer_gcrs(obs.lon, obs.lat, obs.height_m, t0 + TimeDelta(tau, format='sec'))
        tau = float(np.linalg.norm(P - O) / C_KM_S)
    return tau

def station_geometry(t_utc, obs: Observer, lat_deg, lon_deg, light_time=True, dt_min=5.0, dkm=1.0):
    """Geometry of a surface point for one station: the lunar state (Moon, orientation, Sun) at the impact (emission)
    epoch t_utc and the observer at the photon reception time t_utc + tau (one-way light time solved iteratively).
    Includes time derivatives (per minute of impact-time offset, central differences over +-dt_min, emission and
    reception shifted together) and Jacobians with respect to a surface displacement along local north (along-track
    for a polar orbit) and east (cross-track)."""
    from astropy.time import TimeDelta
    t0 = E.to_time(t_utc)
    def at(t_emit):
        es = epoch_state(t_emit)
        tau = light_time_s(t_emit, obs, lat_deg, lon_deg) if light_time else 0.0
        t_rec = t_emit + TimeDelta(tau, format='sec')
        return es, t_rec, tau, surface_geometry(es, obs, [lat_deg], [lon_deg], t_obs=t_rec)
    es, tr, tau, g = at(t0)
    _, _, _, gm = at(t0 - TimeDelta(dt_min * 60, format='sec')); _, _, _, gp = at(t0 + TimeDelta(dt_min * 60, format='sec'))
    o = E.observer_gcrs(obs.lon, obs.lat, obs.height_m, tr)
    p0 = surface_point_geo(es, lat_deg, lon_deg)[0]
    la_n, lo_n = local_ne_offsets(lat_deg, lon_deg, dkm, 0.0); la_e, lo_e = local_ne_offsets(lat_deg, lon_deg, 0.0, dkm)
    pn = surface_point_geo(es, la_n, lo_n)[0]; pe = surface_point_geo(es, la_e, lo_e)[0]
    xn, yn = sky_offset_arcsec(es, o, pn, p0); xe, ye = sky_offset_arcsec(es, o, pe, p0)
    gn = surface_geometry(es, obs, [float(la_n)], [float(lo_n)], t_obs=tr); ge = surface_geometry(es, obs, [float(la_e)], [float(lo_e)], t_obs=tr)
    return dict(t_impact_utc=t0.utc.iso, t_reception_utc=tr.utc.isot, light_time_s=tau, visible=bool(g['visible'][0]), emission=float(g['emission'][0]),
                d_emission=float(gp['emission'][0] - gm['emission'][0]) / (2 * dt_min),
                J_em=[float(gn['emission'][0] - g['emission'][0]) / dkm, float(ge['emission'][0] - g['emission'][0]) / dkm],
                J_sky=[[float(xn[0]) / dkm, float(xe[0]) / dkm], [float(yn[0]) / dkm, float(ye[0]) / dkm]],
                incidence=float(g['incidence'][0]), sunlit=bool(g['sunlit'][0]),
                moon_alt=float(g['alt_moon']), d_moon_alt=(gp['alt_moon'] - gm['alt_moon']) / (2 * dt_min),
                sun_alt=float(g['sun_alt_obs']), d_sun_alt=(gp['sun_alt_obs'] - gm['sun_alt_obs']) / (2 * dt_min),
                alt_point=float(g['alt_point'][0]), az_point=float(g['az_point'][0]), moon_az=float(g['az_moon']), range_km=float(g['range_km'][0]), illum=es.illum_frac,
                disk_x=float(g['disk_x'][0]), disk_y=float(g['disk_y'][0]))

def dist_to_sunlit_arcmin(es: EpochState, obs_gcrs, lat_deg, lon_deg, nside=256, cap_deg=60.0):
    """Angular distance (arcmin) from the impact point to the nearest sunlit terrain visible from the observer, with
    exact gnomonic projection from the observer position (HEALPix nside 256, ~7 km; points within cap_deg of the
    impact point are searched). 0 if the point itself is sunlit; 999 if no visible sunlit terrain lies in the cap."""
    import healpy as hp
    v0 = E.latlon_to_vec(lat_deg, lon_deg, 1.0)
    ip = hp.query_disc(nside, np.ravel(v0), np.radians(cap_deg))
    th, ph = hp.pix2ang(nside, ip); la = 90.0 - np.degrees(th); lo = np.degrees(ph)
    pos = surface_point_geo(es, la, lo); n = E.latlon_to_vec(la, lo, 1.0) @ es.M
    p0 = surface_point_geo(es, lat_deg, lon_deg)[0]; n0 = np.ravel(v0) @ es.M
    if n0 @ (es.r_sun - p0) > 0:
        return 0.0
    lit = np.einsum('ij,ij->i', n, es.r_sun - pos) > 0
    vis = np.einsum('ij,ij->i', n, np.asarray(obs_gcrs) - pos) > 0
    sel = lit & vis
    if not sel.any():
        return 999.0
    x, y = sky_offset_arcsec(es, np.asarray(obs_gcrs), pos[sel], p0)
    return float(np.hypot(x, y).min() / 60.0)

def geocentric_surface_geometry(es: EpochState, lat_deg, lon_deg):
    """Emission and incidence angles of surface points seen from the Earth's centre (observer vector = 0)."""
    p_me = E.latlon_to_vec(np.atleast_1d(lat_deg), np.atleast_1d(lon_deg)); n = p_me / E.R_MOON_KM
    pos = es.r_moon + p_me @ es.M; n_icrf = n @ es.M
    d = -pos; d /= np.linalg.norm(d, axis=1, keepdims=True)
    s = es.r_sun - pos; s /= np.linalg.norm(s, axis=1, keepdims=True)
    return (np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', n_icrf, d), -1, 1))), np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', n_icrf, s), -1, 1))))

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
    """Height above a spherical Moon at which a vertical column over a night-side point first reaches sunlight:
    h = R (sec theta - 1) with theta = incidence - 90 deg (point Sun, reference sphere, no terrain; the finite solar
    disc and terrain broaden the transition). 0.5-6 deg beyond the terminator gives 0.066-9.57 km. Incidence > 90 is
    the night side."""
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
