# Ephemeris validation against JPL Horizons (DE441), tables fetched 2026-10-05

## Geocentric sub-Earth and sub-solar points, 73 epochs at 10-day spacing, 2027-01-01 .. 2028-12-31
Apparent Earth-Moon range residual (local DE421 with light-time+aberration convention minus Horizons delta): max |dr| = 0.004 km, rms = 0.002 km
Geometric sub-Earth point vs Horizons apparent sub-Earth point differs by the aberration shift (~v_obs*tau/d <= 0.006 deg); recomputing the local sub-Earth point from the apparent vector gives: lon rms 0.00020 max 0.00021 deg; lat rms 0.00001 max 0.00001 deg
A direct geometric state-vector check (Horizons VECTORS, 2027-01-01 00:00 TDB) agrees with DE421 to 6 m in position and <1e-9 km/s in velocity.
- model `de421`: residual (local - Horizons) in deg: sub-Earth lon rms 0.00400 max 0.00577; sub-Earth lat rms 0.00027 max 0.00053; sub-solar lon rms 0.00551 max 0.00581; sub-solar lat rms 0.00011 max 0.00017
- model `iau`: residual (local - Horizons) in deg: sub-Earth lon rms 0.00427 max 0.00815; sub-Earth lat rms 0.00112 max 0.00278; sub-solar lon rms 0.00576 max 0.00826; sub-solar lat rms 0.00119 max 0.00212

## Topocentric table horizons_tug_2027-06-10.txt (site: E-lon 30.3356, lat 36.8247, 2.5 km)
| UT | az H | az local | el H | el local | subE lon H | local | subE lat H | local | subS lon H | local |
|---|---|---|---|---|---|---|---|---|---|---|
| 2027-Jun-10 00:00 | 310.3274 | 310.3265 | -28.9629 | -28.9626 | 4.0676 | 4.0658 | 2.7444 | 2.7446 | 113.2117 | 113.2170 |
| 2027-Jun-10 03:00 | 0.5697 | 0.5686 | -44.5815 | -44.5816 | 4.7129 | 4.7113 | 2.7859 | 2.7861 | 111.6830 | 111.6883 |
| 2027-Jun-10 06:00 | 51.5046 | 51.5039 | -29.6295 | -29.6299 | 5.3259 | 5.3244 | 2.7596 | 2.7598 | 110.1543 | 110.1597 |
| 2027-Jun-10 09:00 | 82.2647 | 82.2642 | 1.6201 | 1.6196 | 5.6446 | 5.6434 | 2.7942 | 2.7944 | 108.6258 | 108.6312 |
| 2027-Jun-10 12:00 | 111.3490 | 111.3484 | 35.6245 | 35.6240 | 5.5537 | 5.5526 | 2.9849 | 2.9851 | 107.0974 | 107.1028 |
| 2027-Jun-10 15:00 | 169.3801 | 169.3789 | 58.4452 | 58.4450 | 5.1567 | 5.1557 | 3.3333 | 3.3335 | 105.5691 | 105.5745 |
| 2027-Jun-10 18:00 | 237.2809 | 237.2801 | 42.4245 | 42.4248 | 4.7328 | 4.7319 | 3.7393 | 3.7396 | 104.0409 | 104.0463 |
| 2027-Jun-10 21:00 | 268.6912 | 268.6906 | 8.5000 | 8.5005 | 4.5738 | 4.5731 | 4.0645 | 4.0648 | 102.5128 | 102.5182 |
| 2027-Jun-11 00:00 | 296.0257 | 296.0250 | -25.7277 | -25.7273 | 4.8108 | 4.8102 | 4.2214 | 4.2218 | 100.9848 | 100.9902 |

Worst absolute residual in this table (deg; az scaled by cos el): 0.0018

## Topocentric table horizons_tug_2027-03-15.txt (site: E-lon 30.3356, lat 36.8247, 2.5 km)
| UT | az H | az local | el H | el local | subE lon H | local | subE lat H | local | subS lon H | local |
|---|---|---|---|---|---|---|---|---|---|---|
| 2027-Mar-15 18:00 | 256.9194 | 256.9189 | 64.1104 | 64.1107 | 356.3136 | 356.3138 | -5.2666 | -5.2670 | 85.6148 | 85.6204 |
| 2027-Mar-15 19:00 | 268.0418 | 268.0413 | 52.5302 | 52.5305 | 356.1866 | 356.1868 | -5.1776 | -5.1780 | 85.1074 | 85.1130 |
| 2027-Mar-15 20:00 | 276.2036 | 276.2032 | 40.8847 | 40.8850 | 356.0945 | 356.0947 | -5.0685 | -5.0689 | 84.6000 | 84.6056 |

Worst absolute residual in this table (deg; az scaled by cos el): 0.0004

## PA->ME offset sign test (geocentric table)
- sign +1: sub-Earth lon rms 0.00400 deg, lat rms 0.00027 deg
- sign -1: sub-Earth lon rms 0.03769 deg, lat rms 0.04349 deg

## Documented past event: SMART-1 impact (2006-09-03 05:42:21 UTC, Lacus Excellentiae 34.4 S, 46.2 W) from Maunakea (CFHT)
| UT | az H | az local | el H | el local | subE lon H | local | subE lat H | local | subS lon H | local |
|---|---|---|---|---|---|---|---|---|---|---|
| 2006-09-03 05:00 | 160.0807 | 160.0806 | 38.1912 | 38.1911 | 353.0821 | 353.0847 | 7.3810 | 7.3815 | 55.1066 | 55.1122 |
| 2006-09-03 05:30 | 167.9671 | 167.9671 | 40.1025 | 40.1025 | 352.9787 | 352.9813 | 7.3807 | 7.3812 | 54.8527 | 54.8582 |
| 2006-09-03 06:00 | 176.3135 | 176.3134 | 41.0660 | 41.0660 | 352.8731 | 352.8757 | 7.3726 | 7.3731 | 54.5987 | 54.6043 |

SMART-1 site geometry at impact (local model): emission 56.0 deg, solar incidence 99.3 deg (night side, i.e. 9.3 deg beyond the terminator), Moon altitude at Maunakea 40.6 deg, Sun altitude -16.1 deg, illuminated fraction 0.734: consistent with the published description of a night-side impact in Earthshine observed from Hawaii.
