"""Population with practical direct-viewing conditions (cities >= 15 000 from GeoNames via geonamescache).
Coverage: ~3.9 billion people live in these ~34 000 cities (about half of humanity); rural population is not
represented, so absolute numbers are lower bounds for 'people under a suitable sky' and the comparison between
scenarios is the robust output."""
from __future__ import annotations
import numpy as np
import geonamescache
from . import screening as S

def city_table():
    gc = geonamescache.GeonamesCache()
    c = gc.get_cities()
    lat = np.array([v['latitude'] for v in c.values()]); lon = np.array([v['longitude'] for v in c.values()])
    pop = np.array([v['population'] for v in c.values()], float); cc = np.array([v['countrycode'] for v in c.values()])
    name = np.array([v['name'] for v in c.values()])
    return lat, lon, pop, cc, name

def coverage_at_epoch(epoch_time, site_lat, site_lon, grid_step=1.0):
    """Earth 1-deg grid classes at an epoch for a lunar surface point: returns dict with grids of Moon altitude,
    Sun altitude, and point visibility (exact topocentric), plus the class map."""
    from . import geometry as G
    es = G.epoch_state(epoch_time)
    lats = np.arange(-89.5, 90, grid_step); lons = np.arange(-179.5, 180, grid_step)
    LO, LA = np.meshgrid(lons, lats)
    moon_alt = np.zeros_like(LO); sun_alt = np.zeros_like(LO); vis = np.zeros_like(LO, dtype=bool)
    # vectorised over the grid: observer positions in GCRS for all grid points at one epoch
    from astropy.coordinates import EarthLocation
    from astropy import units as u
    from ayap1obs import ephem as E
    loc = EarthLocation.from_geodetic(LO.ravel() * u.deg, LA.ravel() * u.deg, 0 * u.m)
    pos, _ = loc.get_gcrs_posvel(es.t); o = pos.xyz.to_value(u.km).T
    R = E.itrs_to_gcrs_matrix(es.t)
    la, lo = np.radians(LA.ravel()), np.radians(LO.ravel())
    up = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=1) @ R.T
    d_moon = es.r_moon[None, :] - o; d_moon /= np.linalg.norm(d_moon, axis=1, keepdims=True)
    d_sun = es.r_sun[None, :] - o; d_sun /= np.linalg.norm(d_sun, axis=1, keepdims=True)
    moon_alt = np.degrees(np.arcsin(np.einsum('ij,ij->i', d_moon, up))).reshape(LO.shape)
    sun_alt = np.degrees(np.arcsin(np.einsum('ij,ij->i', d_sun, up))).reshape(LO.shape)
    p_me = E.latlon_to_vec(site_lat, site_lon); p_icrf = es.M.T @ p_me; n = p_icrf / np.linalg.norm(p_icrf)
    pos_pt = es.r_moon + p_icrf
    d = o - pos_pt[None, :]; d /= np.linalg.norm(d, axis=1, keepdims=True)
    vis = (d @ n > 0).reshape(LO.shape)
    return dict(lat=lats, lon=lons, moon_alt=moon_alt, sun_alt=sun_alt, visible=vis)

def classify_coverage(cov):
    """0 none; 1 Moon up (any), 2 public practical (Moon>15, Sun<-6, point visible), 3 facility grade (Moon>20, Sun<-12, visible)"""
    m, s, v = cov['moon_alt'], cov['sun_alt'], cov['visible']
    cls = np.zeros(m.shape, dtype=int)
    cls[(m > 0)] = 1
    cls[(m > 15) & (s < -6) & v] = 2
    cls[(m > 20) & (s < -12) & v] = 3
    return cls

def population_by_class(cov, cls):
    lat, lon, pop, cc, name = city_table()
    i = np.clip(((lat + 90) / (cov['lat'][1] - cov['lat'][0])).astype(int), 0, len(cov['lat']) - 1)
    j = np.clip(((lon + 180) / (cov['lon'][1] - cov['lon'][0])).astype(int), 0, len(cov['lon']) - 1)
    c = cls[i, j]
    out = {k: float(pop[c >= k].sum()) for k in [1, 2, 3]}
    out['total_cities'] = float(pop.sum())
    out['turkiye_total'] = float(pop[cc == 'TR'].sum())
    out['turkiye_public'] = float(pop[(cc == 'TR') & (c >= 2)].sum())
    out['turkiye_facility'] = float(pop[(cc == 'TR') & (c >= 3)].sum())
    return out
