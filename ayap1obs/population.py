"""Settlement populations under coarse geometric viewing criteria (GeoNames 'cities15000' via geonamescache).

What the numbers are: sums of the population fields REPORTED by GeoNames for settlements whose own coordinates satisfy
the geometric criteria (Moon altitude, Sun altitude, impact point on the visible hemisphere) at the impact epoch. They
are not census counts, not a lower bound on people under a suitable sky and not an audience or witness estimate:
weather, obstructions, participation, attention and optical sensitivity are all excluded.

Known problems of the source, handled as a sensitivity rather than solved:
* Overlapping records: GeoNames lists many cities and also their districts (e.g. Istanbul 15.7 M and Esenyurt, Kucukcekmece,
  Bagcilar ... separately), so a plain sum double-counts. `agglomerate` drops a settlement when a settlement at least
  `ratio` times more populous lies within `radius_km`; results are reported for radius 0 (plain sum), 10 and 25 km.
  This is a heuristic: it also removes some genuinely separate satellite towns.
* Census dates differ between records; rural population is absent; the file 'cities15000' contains every settlement
  with population > 15 000 plus capitals/administrative seats below that (45 records < 15 000 in the frozen copy).
The data snapshot is frozen by recording the geonamescache version and the SHA-256 of the file (`snapshot_info`).
Classification uses each settlement's exact coordinates (release 1 used the centre of a 1-degree cell); the 1-degree
grid is retained only for maps, and the change between the two is reported.
"""
from __future__ import annotations
import os, hashlib, json, numpy as np

PUBLIC = dict(moon_min=15.0, sun_max=-6.0)       # 'public practical'
FACILITY = dict(moon_min=20.0, sun_max=-12.0)    # 'facility grade'
RADII_KM = (0.0, 10.0, 25.0)

def _data_file():
    import geonamescache
    return os.path.join(os.path.dirname(geonamescache.__file__), 'data', 'cities15000.json')

def snapshot_info():
    import importlib.metadata as md
    p = _data_file(); h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    lat, lon, pop, cc, name = city_table()
    return dict(source='GeoNames cities15000 (geonamescache package data)', geonamescache_version=md.version('geonamescache'),
                file=os.path.basename(p), sha256=h, n_records=int(len(pop)), n_below_15000=int((pop < 15000).sum()), sum_reported=float(pop.sum()))

_CACHE = None
def city_table():
    global _CACHE
    if _CACHE is None:
        c = json.load(open(_data_file()))
        vals = list(c.values())
        _CACHE = (np.array([v['latitude'] for v in vals], float), np.array([v['longitude'] for v in vals], float),
                  np.array([v['population'] for v in vals], float), np.array([v['countrycode'] for v in vals]), np.array([v['name'] for v in vals]))
    return _CACHE

def agglomerate(lat, lon, pop, radius_km, ratio=2.0):
    """Boolean mask of settlements kept after dropping any settlement within radius_km of one at least `ratio` times
    more populous (greedy, most populous first)."""
    keep = np.ones(len(pop), bool)
    if radius_km <= 0:
        return keep
    order = np.argsort(-pop)
    la, lo = np.radians(lat), np.radians(lon)
    xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=1)
    from scipy.spatial import cKDTree
    tree = cKDTree(xyz); chord = 2 * np.sin(radius_km / 6371.0 / 2)
    dropped = np.zeros(len(pop), bool)
    for i in order:
        if dropped[i]:
            continue
        for j in tree.query_ball_point(xyz[i], chord):
            if j != i and not dropped[j] and pop[j] * ratio <= pop[i]:
                dropped[j] = True
    return ~dropped

_KEEP = {}
def kept_mask(radius_km):
    if radius_km not in _KEEP:
        lat, lon, pop, cc, name = city_table()
        _KEEP[radius_km] = agglomerate(lat, lon, pop, radius_km)
    return _KEEP[radius_km]

def sky_at_points(es, lat, lon, site_lat, site_lon, height_m=0.0):
    """Moon altitude, Sun altitude (deg, geometric, airless) and visibility of the lunar surface point (spherical test)
    from Earth points (lat, lon) at the epoch state es."""
    from astropy.coordinates import EarthLocation
    from astropy import units as u
    from . import ephem as E
    loc = EarthLocation.from_geodetic(np.asarray(lon) * u.deg, np.asarray(lat) * u.deg, height_m * u.m)
    pos, _ = loc.get_gcrs_posvel(es.t); o = pos.xyz.to_value(u.km).T
    Rm = E.itrs_to_gcrs_matrix(es.t)
    # geodetic vertical (WGS84 normal) for altitude
    la, lo = np.radians(lat), np.radians(lon)
    up = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=1) @ Rm.T
    d_moon = es.r_moon[None, :] - o; d_moon /= np.linalg.norm(d_moon, axis=1, keepdims=True)
    d_sun = es.r_sun[None, :] - o; d_sun /= np.linalg.norm(d_sun, axis=1, keepdims=True)
    moon_alt = np.degrees(np.arcsin(np.clip(np.einsum('ij,ij->i', d_moon, up), -1, 1)))
    sun_alt = np.degrees(np.arcsin(np.clip(np.einsum('ij,ij->i', d_sun, up), -1, 1)))
    p_me = E.latlon_to_vec(site_lat, site_lon); p_icrf = es.M.T @ np.ravel(p_me); n = p_icrf / np.linalg.norm(p_icrf)
    d = o - (es.r_moon + p_icrf)[None, :]; d /= np.linalg.norm(d, axis=1, keepdims=True)
    return moon_alt, sun_alt, d @ n > 0

def classify(moon_alt, sun_alt, vis):
    """0 Moon down; 1 Moon up; 2 public practical (Moon > 15, Sun < -6, point visible); 3 facility grade (Moon > 20, Sun < -12)."""
    cls = np.zeros(np.shape(moon_alt), int)
    cls[moon_alt > 0] = 1
    cls[(moon_alt > PUBLIC['moon_min']) & (sun_alt < PUBLIC['sun_max']) & vis] = 2
    cls[(moon_alt > FACILITY['moon_min']) & (sun_alt < FACILITY['sun_max']) & vis] = 3
    return cls

def coverage_at_epoch(epoch_time, site_lat, site_lon, grid_step=1.0):
    """1-degree Earth grid (for maps only): Moon altitude, Sun altitude and point visibility at cell centres."""
    from . import geometry as G
    es = G.epoch_state(epoch_time)
    lats = np.arange(-90 + grid_step / 2, 90, grid_step); lons = np.arange(-180 + grid_step / 2, 180, grid_step)
    LO, LA = np.meshgrid(lons, lats)
    m, s, v = sky_at_points(es, LA.ravel(), LO.ravel(), site_lat, site_lon)
    return dict(lat=lats, lon=lons, moon_alt=m.reshape(LO.shape), sun_alt=s.reshape(LO.shape), visible=v.reshape(LO.shape), es=es)

def classify_coverage(cov):
    return classify(cov['moon_alt'], cov['sun_alt'], cov['visible'])

def settlement_sums(epoch_time, site_lat, site_lon, cov=None):
    """Reported-population sums by class at exact settlement coordinates, for each agglomeration radius, plus the
    release-1 style 1-degree-cell classification for comparison. All values in persons (reported)."""
    from . import geometry as G
    lat, lon, pop, cc, name = city_table()
    es = G.epoch_state(epoch_time) if cov is None else cov['es']
    m, s, v = sky_at_points(es, lat, lon, site_lat, site_lon)
    c = classify(m, s, v)
    tr = cc == 'TR'
    out = dict(definition='sum of GeoNames-reported settlement populations whose coordinates meet the criteria; not a census, lower bound or audience estimate',
               by_radius={})
    for r in RADII_KM:
        k = kept_mask(r)
        out['by_radius'][f'{r:g}km'] = dict(moon_up=float(pop[k & (c >= 1)].sum()), public=float(pop[k & (c >= 2)].sum()), facility=float(pop[k & (c >= 3)].sum()),
                                           turkiye_total=float(pop[k & tr].sum()), turkiye_public=float(pop[k & tr & (c >= 2)].sum()),
                                           turkiye_facility=float(pop[k & tr & (c >= 3)].sum()), n_settlements=int(k.sum()), all_settlements=float(pop[k].sum()))
    if cov is not None:                 # legacy comparison: class of the containing 1-degree cell, no agglomeration
        step = cov['lat'][1] - cov['lat'][0]
        i = np.clip(((lat + 90) / step).astype(int), 0, len(cov['lat']) - 1); j = np.clip(((lon + 180) / step).astype(int), 0, len(cov['lon']) - 1)
        cg = classify_coverage(cov)[i, j]
        out['grid_cell_legacy'] = dict(public=float(pop[cg >= 2].sum()), facility=float(pop[cg >= 3].sum()), turkiye_public=float(pop[tr & (cg >= 2)].sum()))
        out['n_reclassified_vs_grid'] = int((cg != c).sum())
        out['pop_reclassified_vs_grid'] = float(pop[cg != c].sum())
    return out
