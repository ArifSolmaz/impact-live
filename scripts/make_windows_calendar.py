"""Catalogue of observing windows over the impact-epoch domain, independent of the orbit plane:
for each night, the Turkish evening (waxing) and morning (waning) windows with phase 5-60 %, Moon > 20 deg at TUG,
Sun < -12 deg, and the number of configured sites simultaneously available.  Times in UTC and Europe/Istanbul (UTC+3)."""
import sys, os, numpy as np, yaml, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; ids = list(ob['ids'])
jd = cl['jd_utc']; illum = cl['illum']; elong = cl['elong']
avail = ob['avail']; n_sites = avail.sum(axis=0); tr = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']; n_tr = avail[tr].sum(axis=0)
tug = ids.index('TUG'); dag = ids.index('DAG')
waxing = np.gradient(illum) > 0
t = Time(jd, format='jd', scale='utc')
dt = t.to_datetime()
rows = []
good = avail[tug] & (illum >= 0.05) & (illum <= 0.60) & (elong > 30)
days = pd.to_datetime(dt).floor('D')
df = pd.DataFrame(dict(jd=jd, tt=pd.to_datetime(dt), day=days, illum=illum, waxing=waxing, good=good, n_sites=n_sites, n_tr=n_tr,
                       tug_alt=ob['moon_alt'][tug], dag_alt=ob['moon_alt'][dag], sun_tug=ob['sun_alt'][tug], ut_hour=(jd + 0.5) % 1 * 24))
for (day, wax), g in df[df.good].groupby(['day', 'waxing']):
    best = g.loc[g.n_sites.idxmax()]
    rows.append(dict(date_utc=str(day.date()), session='evening (waxing)' if wax else 'morning (waning)',
                     window_start_utc=g.tt.min().strftime('%H:%M'), window_end_utc=g.tt.max().strftime('%H:%M'), hours=len(g),
                     best_hour_utc=best.tt.strftime('%Y-%m-%d %H:%M'), best_hour_istanbul=(best.tt + pd.Timedelta(hours=3)).strftime('%H:%M'),
                     illum=round(best.illum, 3), moon_alt_tug=round(best.tug_alt, 1), moon_alt_dag=round(best.dag_alt, 1),
                     n_sites_available=int(best.n_sites), n_turkish=int(best.n_tr)))
cal = pd.DataFrame(rows)
cal.to_csv(f'{root}/outputs/tables/observing_windows_calendar.csv', index=False)
print(len(cal), 'window-nights')
ev = cal[cal.session.str.startswith('evening')]
print('evening windows per month:'); print(ev.groupby(ev.date_utc.str[:7]).agg(nights=('date_utc', 'count'), max_sites=('n_sites_available', 'max'), mean_hours=('hours', 'mean')).to_string())
# best evening nights overall (public-friendly: 19:00-23:00 Istanbul, illum 0.15-0.45, Moon > 30 deg)
pub = ev[(ev.illum.between(0.15, 0.45)) & (ev.moon_alt_tug > 30)]
print(pub.sort_values('n_sites_available', ascending=False).head(25).to_string())
