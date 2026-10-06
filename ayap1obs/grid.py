"""Area-aware lunar surface grids (HEALPix) with hierarchical refinement."""
from __future__ import annotations
import numpy as np
import healpy as hp

def healpix_grid(nside=32):
    """Equal-area HEALPix pixel centres: returns (lat_deg, lon_deg_east, pixel_area_km2, npix)."""
    npix = hp.nside2npix(nside)
    theta, phi = hp.pix2ang(nside, np.arange(npix))
    lat = 90.0 - np.degrees(theta)
    lon = (np.degrees(phi) + 180.0) % 360.0 - 180.0
    area = 4 * np.pi * 1737.4 ** 2 / npix
    return lat, lon, area, npix

def pixel_of(nside, lat_deg, lon_deg):
    return hp.ang2pix(nside, np.radians(90.0 - np.asarray(lat_deg)), np.radians(np.asarray(lon_deg) % 360.0))

def refine(nside_coarse, pix_ids, nside_fine):
    """Children pixels (NESTED numbering) of coarse pixels, returned in RING numbering."""
    pix_nest = hp.ring2nest(nside_coarse, np.asarray(pix_ids))
    f = (nside_fine // nside_coarse) ** 2
    children = (pix_nest[:, None] * f + np.arange(f)[None, :]).ravel()
    return hp.nest2ring(nside_fine, children)

def resolution_deg(nside):
    return np.degrees(hp.nside2resol(nside))

def region_label(lat, lon):
    """Coarse geographic classes used for reporting (near side centre, limbs, high latitudes, poles, far side)."""
    lat = np.asarray(lat); lon = np.asarray(lon)
    near = np.abs(lon) <= 90
    out = np.full(lat.shape, 'far side', dtype=object)
    out[near & (np.abs(lat) < 45) & (np.abs(lon) < 45)] = 'near side central'
    out[near & (np.abs(lat) < 45) & (lon >= 45)] = 'eastern limb region'
    out[near & (np.abs(lat) < 45) & (lon <= -45)] = 'western limb region'
    out[near & (lat >= 45) & (lat < 80)] = 'northern high latitude'
    out[near & (lat <= -45) & (lat > -80)] = 'southern high latitude'
    out[np.abs(lat) >= 80] = 'polar'
    return out
