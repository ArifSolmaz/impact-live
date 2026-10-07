# Terrain module tests

No real LOLA product could be downloaded in the analysis environment; the reader is tested on a synthetic file
written with the official LOLA GDR conventions. Flat-sphere tests check the line-of-sight clearance.

| test | result | detail |
|---|---|---|
| LDEM bump at lat +20, lon +30 | PASS | height 2.980 km (expected 3.0 km) |
| LDEM bump at lat -40, lon -160 | PASS | height 4.972 km (expected 5.0 km) |
| LDEM no bump 180 deg away | PASS | height at lon -150: 0.000 km |
| LDEM latitude orientation | PASS | height at lat -20, lon 30: 0.000 km |
| LDEM rejects unsupported projection | PASS | only global 0-360 / -90..90 products are supported (got W -180.0, E 360.0, lat - |
| flat DEM = sphere (emission 23.4) | PASS | terrain 0.00 km, sphere 0.00 km |
| sphere vs R(sec-1) (emission 23.4) | PASS | 0.00 vs 0.00 km |
| flat DEM = sphere (emission 77.1) | PASS | terrain 0.00 km, sphere 0.00 km |
| sphere vs R(sec-1) (emission 77.1) | PASS | 0.00 vs 0.00 km |
| flat DEM = sphere (emission 102.1) | PASS | terrain 39.59 km, sphere 39.59 km |
| sphere vs R(sec-1) (emission 102.1) | PASS | 39.59 vs 39.55 km |
| flat DEM = sphere (emission 107.1) | PASS | terrain 80.45 km, sphere 80.45 km |
| sphere vs R(sec-1) (emission 107.1) | PASS | 80.45 vs 80.34 km |
| flat DEM = sphere (emission 117.1) | PASS | terrain 214.15 km, sphere 214.15 km |
| sphere vs R(sec-1) (emission 117.1) | PASS | 214.15 vs 213.64 km |
| flat DEM = sphere (emission 132.0) | PASS | terrain 602.77 km, sphere 602.77 km |
| sphere vs R(sec-1) (emission 132.0) | PASS | 602.77 vs 600.26 km |
| flat DEM = sphere (emission 156.8) | PASS | terrain 2699.20 km, sphere 2699.20 km |
| sphere vs R(sec-1) (emission 156.8) | PASS | 2699.20 vs 2670.13 km |
| flat-sphere horizon = first-sample curvature dip | PASS | -0.00824 deg |

| point lon | emission (deg) | sphere clearance (km) | flat-DEM clearance (km) | R(sec-1), observer at infinity (km) |
|---|---|---|---|---|
| -30 | 23.43 | 0.00 | 0.00 | 0.00 |
| 70 | 77.15 | 0.00 | 0.00 | 0.00 |
| 95 | 102.11 | 39.59 | 39.59 | 39.55 |
| 100 | 107.10 | 80.45 | 80.45 | 80.34 |
| 110 | 117.06 | 214.15 | 214.15 | 213.64 |
| 125 | 131.99 | 602.77 | 602.77 | 600.26 |
| 150 | 156.78 | 2699.20 | 2699.20 | 2670.13 |
