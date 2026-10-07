"""ayap1obs: observability analysis toolkit for the AYAP-1 terminal lunar impact study.

All geometry uses: JPL DE421 (planetary + lunar libration, via the PyPI 'de421' package, jplephem legacy reader),
IAU/NAIF pck00011 lunar orientation series as a cross-check, astropy for Earth orientation (the IERS table pinned in
astropy-iers-data; beyond the table UT1-UTC is held, which can be wrong by up to ~1 s, i.e. ~15 arcsec of Earth
rotation, for 2028 epochs; see ephem.iers_provenance), and a Moon radius of 1737.4 km.
"""
__version__ = "2.1.0"
