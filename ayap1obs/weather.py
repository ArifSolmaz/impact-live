"""Climatological clear-sky priors and spatially correlated weather sampling.

Inputs are long-term *clear-night fractions* per site (config/sites.yaml; literature values where available,
otherwise declared assumptions), modulated by a coarse seasonal pattern per climate class.  They are planning
priors, NOT forecasts: the probability that a specific hour is clear is modelled as
    p_hour = p_night(month) * f_hour,  f_hour = 0.9 (declared: a 'clear night' is not clear every hour),
with a Beta(20 p, 20 (1-p)) uncertainty on p (pseudo-count 20, i.e. roughly +-10 %).
Spatial correlation between sites on the same night: Gaussian copula with rho_ij = exp(-d_ij / L), L = 500 km
(synoptic-scale assumption); sites closer than ~100 km are therefore nearly perfectly correlated and must not be
counted as independent backups.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm, beta as beta_dist

SEASONAL = {   # multiplicative pattern by month (Jan..Dec), normalised to mean 1
    'mediterranean': [0.65, 0.7, 0.8, 0.95, 1.1, 1.3, 1.4, 1.4, 1.25, 1.0, 0.75, 0.65],
    'continental':   [0.8, 0.8, 0.85, 0.9, 1.0, 1.15, 1.25, 1.3, 1.2, 1.05, 0.85, 0.8],
    'desert':        [1.0] * 12,
    'monsoon_asia':  [1.4, 1.4, 1.3, 1.1, 0.7, 0.5, 0.4, 0.4, 0.6, 1.0, 1.3, 1.4],
    'maritime':      [0.95, 0.95, 1.0, 1.0, 1.05, 1.05, 1.05, 1.05, 1.0, 1.0, 0.95, 0.95],
    'south_pacific_subtropical': [0.9, 0.9, 0.95, 1.0, 1.05, 1.1, 1.1, 1.1, 1.05, 1.0, 0.95, 0.9],
}
CLIMATE_BY_GROUP = {'turkiye': 'mediterranean', 'europe': 'mediterranean', 'atlantic': 'maritime', 'africa': 'desert', 'middle_east': 'desert',
                    'caucasus': 'continental', 'central_asia': 'continental', 'asia': 'monsoon_asia', 'east_asia': 'monsoon_asia',
                    'oceania': 'south_pacific_subtropical', 'pacific': 'maritime', 'north_america': 'continental', 'south_america': 'desert'}

def p_clear_hour(site, month, f_hour=0.9):
    s = SEASONAL[CLIMATE_BY_GROUP[site['group']]]
    s = np.array(s) / np.mean(s)
    p = np.clip(site['clear_frac'] * s[month - 1], 0.02, 0.98)
    return p * f_hour

def great_circle_km(lat1, lon1, lat2, lon2):
    la1, lo1, la2, lo2 = map(np.radians, [lat1, lon1, lat2, lon2])
    return 6371.0 * np.arccos(np.clip(np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(lo1 - lo2), -1, 1))

def sample_clear(sites, month, n, rng, L_km=500.0, pseudo=20.0):
    """Boolean array (n x len(sites)) of 'clear at the event hour' draws with spatial correlation."""
    k = len(sites)
    lat = np.array([s['lat'] for s in sites]); lon = np.array([s['lon'] for s in sites])
    D = great_circle_km(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    C = np.exp(-D / L_km); C[np.diag_indices(k)] = 1.0
    z = rng.multivariate_normal(np.zeros(k), C, size=n)
    u = norm.cdf(z)
    p = np.array([p_clear_hour(s, month) for s in sites])
    # one Beta draw per *site* (co-located stations share the same sky): group by (lat, lon)
    keys = [(round(s['lat'], 3), round(s['lon'], 3)) for s in sites]
    uniq = {kk: i for i, kk in enumerate(dict.fromkeys(keys))}
    p_site = np.array([p[[j for j, kk in enumerate(keys) if kk == u_][0]] for u_ in uniq])
    draws = beta_dist.rvs(pseudo * p_site, pseudo * (1 - p_site), size=(n, len(uniq)), random_state=rng)
    p_draw = draws[:, [uniq[kk] for kk in keys]]
    # co-located stations also share the same uniform
    u = u[:, [[j for j, kk in enumerate(keys) if kk == kk2][0] for kk2 in keys]]
    return u < p_draw
