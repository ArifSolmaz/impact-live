"""Illustrative clear-sky priors and spatially correlated weather sampling.

Each site has an annual central probability that the line of sight to the Moon is clear enough for flash monitoring
at a random night hour (p_los), derived from the site's quoted statistic (config/sites.yaml: clear_frac with its
definition clear_def) by a definition-dependent factor, and an uncertainty half-range. These are planning
assumptions from mixed sources, NOT a consistent climatology and not forecasts (no per-site hourly cloud dataset
could be used in this study). A qualitative monthly pattern is assigned per site (season); it is guessed, not
fitted, so it is not evidence for differences between scenarios. The 'flat' pattern, L = 250 and 1000 km and prior
spreads x0.5 and x2 are run as sensitivity cases for S1 (spring) and S11 (winter) and exported in those scenario cards
(card key mc_weather_sensitivity, scripts/run_scenarios.py; re-audit ST-N04).

Epistemic structure: in the network Monte Carlo the site probabilities are drawn once per outer iteration from Beta
distributions whose 90 % range matches the half-range; event trials inside an outer iteration share those
probabilities. The spread of the conditional detection probability across outer iterations is the reported
weather/readiness uncertainty; the pooled mean equals the prior-predictive mean.

Spatial correlation: a Gaussian copula with latent-normal correlation rho_ij = exp(-d_ij / L), L = 500 km
(synoptic-scale assumption; 250 and 1000 km are the sensitivity cases above). rho is the correlation of the latent normal
variables, not of the clear/cloudy indicators: two sites 100 km apart (rho = 0.82) with p = 0.5 have an indicator
correlation of (2/pi) asin(0.82) = 0.61, so they are partly redundant but not perfectly correlated. Co-located
stations share the same sky.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm

SEASONAL = {   # qualitative monthly patterns (Jan..Dec), normalised to mean 1 when used; NOT fitted to data
    'flat':          [1.0] * 12,
    'mediterranean': [0.65, 0.7, 0.8, 0.95, 1.1, 1.3, 1.4, 1.4, 1.25, 1.0, 0.75, 0.65],   # dry summer
    'continental':   [0.8, 0.8, 0.85, 0.9, 1.0, 1.15, 1.25, 1.3, 1.2, 1.05, 0.85, 0.8],   # cloudier winter
    'central_asia':  [0.7, 0.7, 0.8, 0.9, 1.05, 1.3, 1.4, 1.4, 1.3, 1.05, 0.75, 0.65],   # very dry summer
    'desert':        [1.0] * 12,
    'maritime':      [0.95, 0.95, 1.0, 1.0, 1.05, 1.05, 1.05, 1.05, 1.0, 1.0, 0.95, 0.95],
    'hawaii':        [0.9, 0.9, 0.95, 1.0, 1.05, 1.1, 1.1, 1.05, 1.05, 1.0, 0.95, 0.9],   # winter storms
    'monsoon_asia':  [1.4, 1.4, 1.3, 1.1, 0.7, 0.5, 0.4, 0.4, 0.6, 1.0, 1.3, 1.4],
    'himalaya':      [1.05, 1.05, 1.05, 1.05, 1.05, 0.95, 0.75, 0.75, 0.95, 1.1, 1.1, 1.1],  # weak monsoon at high altitude
    'japan':         [1.2, 1.15, 1.0, 0.95, 0.9, 0.7, 0.75, 0.9, 0.8, 1.05, 1.15, 1.2],    # rainy season and typhoons
    'sw_monsoon':    [1.05, 1.05, 1.1, 1.15, 1.15, 1.05, 0.75, 0.75, 0.95, 1.1, 1.0, 0.95], # North American monsoon
    'chile_central': [1.1, 1.1, 1.05, 1.0, 0.9, 0.85, 0.85, 0.9, 0.95, 1.05, 1.1, 1.1],  # winter fronts
    'chile_north':   [0.9, 0.9, 1.0, 1.0, 1.0, 1.05, 1.05, 1.05, 1.05, 1.0, 1.0, 0.95], # 'Bolivian winter' in Jan-Feb
    'brazil':        [0.7, 0.75, 0.85, 1.0, 1.15, 1.25, 1.25, 1.2, 1.05, 0.9, 0.8, 0.7],  # wet summer
    'karoo':         [0.9, 0.9, 0.95, 1.0, 1.05, 1.1, 1.1, 1.05, 1.0, 1.0, 0.95, 0.9],    # summer thunderstorms
    'southern_maritime': [1.05, 1.05, 1.0, 1.0, 0.95, 0.95, 0.95, 0.95, 1.0, 1.0, 1.05, 1.05],
}
# conversion of the quoted statistic to a line-of-sight clear probability at a random night hour: (factor, half-range)
DEFINITIONS = {
    'clear nights':              (0.90, 0.10),   # a clear night is not clear every hour
    'usable nights':             (0.85, 0.10),   # usable nights include partly cloudy ones
    'photometric':               (0.90, 0.07),
    'photometric+spectroscopic': (0.90, 0.10),
    'assumed':                   (0.90, 0.15),
}

def site_prior(site):
    """(central annual p_los, half-range) for a site."""
    fac, half = DEFINITIONS[site.get('clear_def', 'assumed')]
    return float(np.clip(site['clear_frac'] * fac, 0.02, 0.98)), half

def pattern(site, seasonality=True):
    key = site.get('season', 'flat') if seasonality else 'flat'
    s = np.array(SEASONAL[key], float)
    return s / s.mean()

def p_clear_month(site, month, seasonality=True):
    p, _ = site_prior(site)
    return float(np.clip(p * pattern(site, seasonality)[month - 1], 0.02, 0.98))

def beta_parameters(mean, half_range):
    """Beta(a, b) with the given mean whose central 90 % range has approximately the given half-width."""
    var = (half_range / 1.645) ** 2
    nu = max(mean * (1 - mean) / var - 1.0, 2.0)
    return mean * nu, (1 - mean) * nu

def great_circle_km(lat1, lon1, lat2, lon2):
    la1, lo1, la2, lo2 = map(np.radians, [lat1, lon1, lat2, lon2])
    return 6371.0 * np.arccos(np.clip(np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(lo1 - lo2), -1, 1))

def unique_sites(sites):
    """Index of each station's sky (co-located stations share one) and the list of unique site dicts."""
    keys = [(round(s['lat'], 3), round(s['lon'], 3)) for s in sites]
    first = {}
    for i, k in enumerate(keys):
        first.setdefault(k, i)
    order = list(dict.fromkeys(keys))
    idx = np.array([order.index(k) for k in keys])
    return idx, [sites[first[k]] for k in order]

def latent_correlation(sites, L_km=500.0):
    lat = np.array([s['lat'] for s in sites]); lon = np.array([s['lon'] for s in sites])
    Dm = great_circle_km(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    C = np.exp(-Dm / L_km); np.fill_diagonal(C, 1.0)
    return C

def cholesky_factor(C):
    """Cholesky factor (unique for a positive-definite matrix, so samples agree across linear-algebra libraries up to
    rounding); a tiny diagonal jitter is added if needed."""
    jit = 0.0
    for _ in range(8):
        try:
            return np.linalg.cholesky(C + jit * np.eye(len(C)))
        except np.linalg.LinAlgError:
            jit = 1e-10 if jit == 0 else jit * 10
    raise np.linalg.LinAlgError('correlation matrix not positive definite')

def correlated_uniforms(Lc, n, rng):
    """n x k uniforms with latent-normal correlation C = Lc Lc^T."""
    z = rng.standard_normal((n, Lc.shape[0])) @ Lc.T
    return norm.cdf(z)

def draw_site_probabilities(usites, month, rng, n_outer, seasonality=True, spread=1.0):
    """n_outer x n_sites draws of the event-hour clear probability (epistemic uncertainty), from Beta distributions
    centred on the site's monthly central value."""
    out = np.empty((n_outer, len(usites)))
    for j, s in enumerate(usites):
        m = p_clear_month(s, month, seasonality); _, half = site_prior(s)
        a, b = beta_parameters(m, half * spread)
        out[:, j] = rng.beta(a, b, n_outer)
    return out

def indicator_correlation(p1, p2, rho):
    """Correlation of two clear/cloudy indicators with marginal probabilities p1, p2 under a Gaussian copula with
    latent correlation rho."""
    from scipy.stats import multivariate_normal
    z1, z2 = norm.ppf(p1), norm.ppf(p2)
    p11 = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]]).cdf([z1, z2])
    return (p11 - p1 * p2) / np.sqrt(p1 * (1 - p1) * p2 * (1 - p2)), p11
