"""Observing calendar for Türkiye, independent of the orbit plane: sessions in which the criterion named 'calendar' in
config/domain.yaml holds at TUG (Moon altitude, Sun altitude, illuminated fraction, elongation).

Method: the hourly screening grid (integer hour offsets from the domain start) is split into contiguous runs of
good hours; each run is one session. Its start and end are refined on a 5-minute grid around the first and last good
hour, and its duration is the refined interval. The best time is the hourly sample with the most configured sites
available. All times are full ISO timestamps in UTC and Europe/Istanbul (UTC+3, no daylight saving), each with its
own date; 'night' is the local date of the evening on which the session starts or the night it ends.
Sessions are geometric planning windows: trajectory feasibility and weather are not included.
"""
import sys, os, numpy as np, yaml, pandas as pd, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import screening as S, ephem as E
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
dom = yaml.safe_load(open(f'{root}/config/domain.yaml')); C = dom['criteria']['calendar']
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; ids = list(ob['ids'])
site = next(s for s in sites if s['id'] == C['site']); k_site = ids.index(C['site']); dag = ids.index('DAG')
start = dt.datetime.strptime(dom['domain']['start_utc'], '%Y-%m-%d %H:%M:%S')
n = len(cl['jd_utc']); hours = [start + dt.timedelta(hours=k) for k in range(n)]      # exact hour labels
illum, elong = cl['illum'], cl['elong']
moon, sun = ob['moon_alt'][k_site], ob['sun_alt'][k_site]
good = (moon >= C['min_moon_alt_deg']) & (sun <= C['max_sun_alt_deg']) & (illum >= C['illum_min']) & (illum <= C['illum_max']) & (elong > C['min_elongation_deg'])
n_sites = ob['avail'].sum(axis=0); tr = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']; n_tr = ob['avail'][tr].sum(axis=0)
waxing = cl['waxing'] if 'waxing' in cl.files else np.gradient(illum) > 0
IST = dt.timedelta(hours=3)

def fine_ok(t0, t1):
    """Criterion on a 5-minute grid between datetimes t0 and t1 (inclusive)."""
    m = int((t1 - t0).total_seconds() // (C['refine_step_minutes'] * 60)) + 1
    tt = [t0 + dt.timedelta(minutes=C['refine_step_minutes'] * j) for j in range(m)]
    times = Time(tt, scale='utc')
    _, _, mo, su, _ = S.epoch_arrays(times)
    sky = S.observer_sky(site['lon'], site['lat'], site['alt'], times, mo, su)
    il, el, _ = S.lunar_phase_arrays(mo, su)
    ok = (sky['moon_alt'] >= C['min_moon_alt_deg']) & (sky['sun_alt'] <= C['max_sun_alt_deg']) & (il >= C['illum_min']) & (il <= C['illum_max']) & (el > C['min_elongation_deg'])
    return tt, ok

runs = []
k = 0
while k < n:
    if good[k]:
        j = k
        while j + 1 < n and good[j + 1]:
            j += 1
        runs.append((k, j)); k = j + 1
    else:
        k += 1
rows = []
for a, b in runs:
    lo = hours[max(a - 1, 0)]; hi = hours[min(b + 1, n - 1)]
    tt, ok = fine_ok(lo, hours[a]); s_ = next((t for t, o in zip(tt, ok) if o), hours[a])
    tt, ok = fine_ok(hours[b], hi); e_ = [t for t, o in zip(tt, ok) if o][-1] if ok.any() else hours[b]
    kb = a + int(np.argmax(n_sites[a:b + 1]))
    best = hours[kb]
    session = 'evening (waxing)' if waxing[kb] else 'morning (waning)'
    night = (s_ + IST).date() if session.startswith('evening') else ((e_ + IST) - dt.timedelta(days=1)).date()
    fmt = lambda t: t.strftime('%Y-%m-%dT%H:%MZ'); fmti = lambda t: (t + IST).strftime('%Y-%m-%dT%H:%M+03:00')
    rows.append(dict(night_istanbul=str(night), session=session, start_utc=fmt(s_), end_utc=fmt(e_), start_istanbul=fmti(s_), end_istanbul=fmti(e_),
                     duration_min=int(round((e_ - s_).total_seconds() / 60)), sampled_hours=int(b - a + 1), best_utc=fmt(best), best_istanbul=fmti(best),
                     illum=round(float(illum[kb]), 3), moon_alt_tug=round(float(moon[kb]), 1), moon_alt_dag=round(float(ob['moon_alt'][dag][kb]), 1),
                     n_sites_available=int(n_sites[kb]), n_turkish=int(n_tr[kb])))
cal = pd.DataFrame(rows)
cal.to_csv(f'{root}/outputs/tables/observing_windows_calendar.csv', index=False)
print(len(cal), 'sessions;', 'criterion:', C)
ev = cal[cal.session.str.startswith('evening')]
print(ev.groupby(ev.night_istanbul.str[:7]).agg(sessions=('night_istanbul', 'count'), max_sites=('n_sites_available', 'max'), mean_minutes=('duration_min', 'mean')).to_string())
