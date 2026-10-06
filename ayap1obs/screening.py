"""Vectorised site x epoch x observer screening.

Stage 1 (coarse): HEALPix nside=32 (1.8 deg, ~55 km pixels), hourly epochs over the impact-search domain.
Stage 2 (refined): nside=128 (0.46 deg, ~14 km) around candidate regions, 5-min epochs around candidate windows.
Observer-dependent visibility of a surface point differs from geocentric visibility only by the parallax of
the observer (<= 1 deg of emission angle): the coarse stage uses geocentric emission angles with a 1-deg margin
and the refined stage recomputes exact topocentric geometry per observer (geometry.surface_geometry).
"""
from __future__ import annotations
import numpy as np
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import EarthLocation, ITRS, GCRS, CartesianRepresentation
from . import ephem as E
from . import grid as Gd

def epoch_arrays(times):
    """Vectorised Moon/Sun geocentric vectors and ICRF->ME matrices for an astropy Time array."""
    t = E.to_time(times)
    jd = np.atleast_1d(t.tdb.jd)
    e = E._eph()
    moon = np.asarray(e.position('moon', jd))            # 3 x N
    emb = np.asarray(e.position('earthmoon', jd)); sun = np.asarray(e.position('sun', jd))
    earth = emb - moon / (1.0 + E.EMRAT)
    sun_geo = sun - earth
    phi, theta, psi = np.asarray(e.position('librations', jd))
    # batched rotation matrices ICRF->PA then PA->ME
    cp, sp = np.cos(phi), np.sin(phi); ct, st = np.cos(theta), np.sin(theta); cs, ss = np.cos(psi), np.sin(psi)
    Rz_phi = np.array([[cp, sp, 0 * cp], [-sp, cp, 0 * cp], [0 * cp, 0 * cp, 1 + 0 * cp]])       # 3x3xN
    Rx_th = np.array([[1 + 0 * ct, 0 * ct, 0 * ct], [0 * ct, ct, st], [0 * ct, -st, ct]])
    Rz_psi = np.array([[cs, ss, 0 * cs], [-ss, cs, 0 * cs], [0 * cs, 0 * cs, 1 + 0 * cs]])
    M = np.einsum('ijn,jkn,kln->iln', Rz_psi, Rx_th, Rz_phi)
    M = np.einsum('ij,jkn->ikn', E.PA2ME, M)
    return t, jd, moon.T, sun_geo.T, np.moveaxis(M, 2, 0)      # (N,3), (N,3), (N,3,3)

def observer_sky(obs_lon, obs_lat, obs_h_m, times, moon, sun):
    """Moon and Sun altitudes/azimuths (deg) for an observer over a Time array; moon/sun are geocentric (N,3)."""
    t = E.to_time(times)
    loc = EarthLocation.from_geodetic(obs_lon * u.deg, obs_lat * u.deg, obs_h_m * u.m)
    pos, _ = loc.get_gcrs_posvel(t)
    o = pos.xyz.to_value(u.km).T                                  # N x 3
    n = len(o)
    lon, lat = np.radians(obs_lon), np.radians(obs_lat)
    up = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    east = np.array([-np.sin(lon), np.cos(lon), 0.0]); north = np.cross(up, east)
    def rot(v):
        itrs = ITRS(CartesianRepresentation(np.repeat(v[0], n) * u.km, np.repeat(v[1], n) * u.km, np.repeat(v[2], n) * u.km), obstime=t)
        g = itrs.transform_to(GCRS(obstime=t)).cartesian.xyz.to_value(u.km).T
        return g / np.linalg.norm(g, axis=1, keepdims=True)
    E_, N_, U_ = rot(east), rot(north), rot(up)
    def altaz(target):
        d = target - o; d /= np.linalg.norm(d, axis=1, keepdims=True)
        alt = np.degrees(np.arcsin(np.clip(np.einsum('ij,ij->i', d, U_), -1, 1)))
        az = np.degrees(np.arctan2(np.einsum('ij,ij->i', d, E_), np.einsum('ij,ij->i', d, N_))) % 360
        return alt, az
    alt_m, az_m = altaz(moon); alt_s, az_s = altaz(sun)
    return dict(moon_alt=alt_m, moon_az=az_m, sun_alt=alt_s, sun_az=az_s, obs_gcrs=o)

def surface_classes(moon, sun, M, lat, lon, obs_gcrs=None):
    """For one epoch: emission (geocentric or topocentric if obs_gcrs given) and incidence angles for all pixels."""
    p_me = E.latlon_to_vec(lat, lon)              # P x 3
    n_icrf = (p_me / E.R_MOON_KM) @ M             # normals in ICRF (M^T n)^T
    pos = moon[None, :] + p_me @ M
    origin = np.zeros(3) if obs_gcrs is None else obs_gcrs
    d = origin[None, :] - pos; d /= np.linalg.norm(d, axis=1, keepdims=True)
    s = sun[None, :] - pos; s /= np.linalg.norm(s, axis=1, keepdims=True)
    cos_e = np.einsum('ij,ij->i', n_icrf, d); cos_i = np.einsum('ij,ij->i', n_icrf, s)
    return np.degrees(np.arccos(np.clip(cos_e, -1, 1))), np.degrees(np.arccos(np.clip(cos_i, -1, 1)))

def lunar_phase_arrays(moon, sun):
    d = np.linalg.norm(moon, axis=1)
    ms = sun - moon
    cos_phase = np.einsum('ij,ij->i', -moon, ms) / (d * np.linalg.norm(ms, axis=1))
    illum = 0.5 * (1 + cos_phase)
    elong = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', moon, sun) / (d * np.linalg.norm(sun, axis=1)), -1, 1)))
    return illum, elong, d
