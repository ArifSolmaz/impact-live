"""Independent exact-time check of the opportunity catalogue (re-audit GE-V2-03): for every row of
outputs/reachability/catalogue_main.csv the station availability is recomputed at the stored impact UTC with astropy
(get_body, AltAz; no refraction) instead of the pipeline's DE421 station geometry interpolated from the 10-min grid:
Moon altitude >= 20 deg, Sun altitude <= -12 deg, configured seasonal closures. The numbers of available sites,
Turkish sites and TUG availability are compared with the catalogue. Differences can only arise for a station within a
small margin of a threshold (the two geometry codes differ by thousandths of a degree); their margins are reported.
Writes outputs/validation/catalogue_gate_check.json (`make gatecheck`; about 10 minutes; not part of `make all`)."""
import sys, os, json, numpy as np, pandas as pd, yaml
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_body
import astropy, astropy.units as u
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = yaml.safe_load(open(f'{root}/config/domain.yaml'))['criteria']['observer']
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
cat = pd.read_csv(f'{root}/outputs/reachability/catalogue_main.csv')
t = Time(cat.jd_utc_impact.values, format='jd', scale='utc')
months = np.array([d.month for d in t.to_datetime()])
n_av = np.zeros(len(cat), int); n_tr = np.zeros(len(cat), int); tug = np.zeros(len(cat), bool); margin = np.full(len(cat), np.inf)
for s in sites:
    loc = EarthLocation.from_geodetic(s['lon'] * u.deg, s['lat'] * u.deg, s['alt'] * u.m)
    fr = AltAz(obstime=t, location=loc)
    am = get_body('moon', t, loc).transform_to(fr).alt.deg; asun = get_body('sun', t, loc).transform_to(fr).alt.deg
    av = (am >= cfg['min_moon_alt_deg']) & (asun <= cfg['max_sun_alt_deg']) & ~np.isin(months, s.get('closed_months', []))
    margin = np.minimum(margin, np.minimum(np.abs(am - cfg['min_moon_alt_deg']), np.abs(asun - cfg['max_sun_alt_deg'])))
    n_av += av; n_tr += av & (s['country'] == 'TR')
    if s['id'] == 'TUG':
        tug = av
d_av = n_av - cat.n_sites.values; d_tr = n_tr - cat.n_tr.values; d_tug = tug != cat.tug_available.values.astype(bool)
bad = (d_av != 0) | (d_tr != 0) | d_tug
out = dict(rows=int(len(cat)), astropy=astropy.__version__, criteria=dict(min_moon_alt_deg=cfg['min_moon_alt_deg'], max_sun_alt_deg=cfg['max_sun_alt_deg']),
           total_count_mismatches=int((d_av != 0).sum()), max_abs_total_count_difference=int(np.abs(d_av).max()),
           turkish_count_mismatches=int((d_tr != 0).sum()), tug_mismatches=int(d_tug.sum()),
           rows_with_fewer_than_3_sites_but_stored_3_or_more=int(((n_av < 3) & (cat.n_sites.values >= 3)).sum()),
           max_threshold_margin_of_mismatched_rows_deg=(float(margin[bad].max()) if bad.any() else None),
           note='release 2.0 (nearest-grid-time gates): 921 of 4450 rows differed (re-audit GE-V2-03)')
json.dump(out, open(f'{root}/outputs/validation/catalogue_gate_check.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
