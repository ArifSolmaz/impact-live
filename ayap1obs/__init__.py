"""ayap1obs: observability analysis toolkit for the AYAP-1 terminal lunar impact study.

All geometry uses: JPL DE421 (planetary + lunar libration, via the PyPI 'de421' package, jplephem legacy reader),
IAU/NAIF pck00011 lunar orientation series as a cross-check, astropy for Earth orientation (IERS-B bundled,
UT1-UTC and polar motion neglected beyond table range: < 1 arcsec effect), and a Moon radius of 1737.4 km.
"""
__version__ = "0.1.0"
