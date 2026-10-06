"""Launch-to-impact timeline families and candidate observing windows."""
import sys, os, numpy as np, yaml, pandas as pd, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
tl = yaml.safe_load(open(f'{root}/config/timeline.yaml')); orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml'))
cal = pd.read_csv(f'{root}/outputs/tables/observing_windows_calendar.csv')
ev = cal[cal.session.str.startswith('evening') & cal.illum.between(0.12, 0.5) & (cal.moon_alt_tug > 25)]
rows = []
for L in tl['launch_families']:
    d0 = dt.datetime.strptime(L['date'], '%Y-%m-%d')
    for key in ['min', 'nominal', 'max']:
        tr = tl['phases']['transfer_days'][key]; loi = tl['phases']['loi_and_circularisation_days'][key]; com = tl['phases']['commissioning_days'][key]; term = tl['phases']['terminal_phase_days'][key]
        t_loi = d0 + dt.timedelta(days=tr); t_sci = t_loi + dt.timedelta(days=loi + com)
        for S in tl['phases']['science_months']:
            t_imp = t_sci + dt.timedelta(days=30.44 * S + term)
            # candidate Turkish-evening windows within +-15 d of the end-of-mission date
            w = ev[(pd.to_datetime(ev.date_utc) >= t_imp - dt.timedelta(days=15)) & (pd.to_datetime(ev.date_utc) <= t_imp + dt.timedelta(days=15))]
            # LRO low-sun window status at impact
            lro = any(dt.datetime.strptime(a, '%Y-%m-%d') <= t_imp <= dt.datetime.strptime(b, '%Y-%m-%d') for a, b in orb['lro']['low_sun_windows'])
            beyond = t_imp > dt.datetime(2029, 2, 15)
            rows.append(dict(launch=L['id'], launch_date=L['date'], phase_case=key, loi_date=t_loi.date(), science_start=t_sci.date(), science_months=S, impact_date=t_imp.date(),
                             impact_istanbul_note='date only; hour set by the pass', n_evening_windows_pm15d=('beyond computed domain' if beyond else len(w)), best_window=(w.sort_values('n_sites_available', ascending=False).iloc[0].best_hour_utc + ' UTC' if len(w) else ('n/a (beyond domain)' if beyond else 'none (summer: low evening crescent)')),
                             in_LRO_low_sun_window=lro))
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/timeline_families.csv', index=False)
# figure
fig, ax = plt.subplots(figsize=(13, 5.2))
y = 0; labels = []
for L in tl['launch_families']:
    d0 = dt.datetime.strptime(L['date'], '%Y-%m-%d')
    tr = tl['phases']['transfer_days']; loi = tl['phases']['loi_and_circularisation_days']; com = tl['phases']['commissioning_days']
    t_loi = d0 + dt.timedelta(days=tr['nominal']); t_sci = t_loi + dt.timedelta(days=loi['nominal'] + com['nominal'])
    ax.barh(y, (t_loi - d0).days, left=d0, color=P.CAT[0], height=0.6, label='transfer (~2 months, multi-burn)' if y == 0 else None)
    ax.barh(y, (t_sci - t_loi).days, left=t_loi, color=P.CAT[2], height=0.6, label='LOI + circularisation + commissioning' if y == 0 else None)
    for k, S in enumerate(tl['phases']['science_months']):
        t_end = t_sci + dt.timedelta(days=30.44 * S); t_prev = t_sci + dt.timedelta(days=30.44 * (tl['phases']['science_months'][k - 1] if k else 0))
        ax.barh(y, (t_end - t_prev).days, left=t_prev, color=P.CAT[1], alpha=1 - 0.2 * k, height=0.6, label='orbital science: 3 / 6 / 12 / 18 months' if (y == 0 and k == 0) else None)
        ax.plot(t_end + dt.timedelta(days=tl['phases']['terminal_phase_days']['nominal']), y, marker='v', color='k', ms=6)
    # transfer uncertainty bar
    ax.plot([d0 + dt.timedelta(days=tr['min']), d0 + dt.timedelta(days=tr['max'])], [y + 0.42, y + 0.42], color=P.TEXT2, lw=1)
    labels.append(f"{L['id']}: launch {L['date']} ({L['label']})"); y += 1
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8); ax.invert_yaxis()
for a, b in orb['lro']['low_sun_windows']:
    ax.axvspan(dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d'), color=P.CAT[6], alpha=0.12)
for d in pd.to_datetime(ev.date_utc):
    ax.axvline(d, color=P.CAT[3], lw=0.5, alpha=0.5)
ax.plot([], [], color=P.CAT[3], lw=1, label='Türkiye evening windows (illum 0.12-0.5, Moon > 25 deg at TUG)'); ax.fill_between([], [], color=P.CAT[6], alpha=0.2, label='estimated LRO low-Sun imaging windows (+-3 weeks)')
ax.plot([], [], 'kv', label='impact (end of science + ~10-day terminal phase)')
ax.set_xlim(dt.datetime(2027, 3, 1), dt.datetime(2030, 1, 1)); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.legend(fontsize=7, loc='lower right'); ax.set_title('Launch-to-impact timeline families (SCENARIO ASSUMPTIONS anchored on published statements; impact hour set by the orbital pass)', loc='left', fontsize=9)
P.evidence_tag(fig, 'HYPOTHETICAL SCENARIO FAMILIES - no launch date or contract has been published (cutoff 2026-10-05)')
fig.tight_layout(); P.savefig(fig, 'fig_timeline_families')
print(df[(df.phase_case == 'nominal')].to_string())
