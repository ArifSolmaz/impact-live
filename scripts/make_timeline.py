"""Launch-to-impact timeline families (modelling choices spanning the published 'first months' / 'first half' / 'Q2 2027'
statements, plus slips) and, for each, the Turkish evening observing sessions near the end of the science phase and the
screening-opportunity probabilities for terminal windows opening then (outputs/tables/timeline_window_probability.csv).
Writes outputs/tables/timeline_families.csv and fig_timeline_families."""
import sys, os, json, numpy as np, yaml, pandas as pd, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
tl = yaml.safe_load(open(f'{root}/config/timeline.yaml')); orb = yaml.safe_load(open(f'{root}/config/orbiters.yaml'))
dom = yaml.safe_load(open(f'{root}/config/domain.yaml'))['domain']
d_start = dt.datetime.strptime(dom['start_utc'], '%Y-%m-%d %H:%M:%S'); d_stop = dt.datetime.strptime(dom['stop_utc'], '%Y-%m-%d %H:%M:%S')
cal = pd.read_csv(f'{root}/outputs/tables/observing_windows_calendar.csv')
cal['start'] = pd.to_datetime(cal.start_utc.str.replace('Z', ''), format='%Y-%m-%dT%H:%M')
ev = cal[cal.session.str.startswith('evening') & cal.illum.between(0.12, 0.5) & (cal.moon_alt_tug > 25)]
twp = pd.read_csv(f'{root}/outputs/tables/timeline_window_probability.csv')
lro_low = [(w['start'], w['end']) for w in json.load(open(f'{root}/outputs/tables/orbiter_seasons.json'))['lro']['low_sun']]   # computed (make_orbiter_seasons.py)
rows = []
for L in tl['launch_families']:
    d0 = dt.datetime.strptime(L['date'], '%Y-%m-%d')
    for key in ['min', 'nominal', 'max']:
        ph = tl['phases']; tr = ph['transfer_days'][key]; loi = ph['loi_and_circularisation_days'][key]; com = ph['commissioning_days'][key]; term = ph['terminal_phase_days'][key]
        t_loi = d0 + dt.timedelta(days=tr); t_sci = t_loi + dt.timedelta(days=loi + com)
        for S in ph['science_months']:
            t_imp = t_sci + dt.timedelta(days=30.44 * S + term)
            inside = d_start <= t_imp < d_stop - dt.timedelta(days=15)
            w = ev[(ev.start >= t_imp - dt.timedelta(days=15)) & (ev.start <= t_imp + dt.timedelta(days=15))]
            best = w.sort_values(['n_sites_available', 'start'], ascending=[False, True], kind='stable').iloc[0] if len(w) else None
            lro = any(dt.datetime.strptime(a, '%Y-%m-%d') <= t_imp <= dt.datetime.strptime(b, '%Y-%m-%d') for a, b in lro_low)
            row = dict(launch=L['id'], launch_date=L['date'], phase_case=key, loi_date=str(t_loi.date()), science_start=str(t_sci.date()), science_months=S,
                       impact_date=str(t_imp.date()), impact_hour_note='date only; the hour is set by the orbital pass',
                       n_evening_sessions_pm15d=(len(w) if inside else None),
                       best_session_istanbul=(best.best_istanbul if best is not None else ('outside the computed domain' if not inside else 'none (low evening crescent)')),
                       in_LRO_low_sun_season=lro)
            if key == 'nominal':
                tw = twp[(twp.launch == L['id']) & (twp.science_months == S) & (twp.family_set == 'main') & (twp.delta == 0.6)]
                for _, r in tw.iterrows():
                    row[f"p30_{r.cls.split('_')[0]}"] = r.p_30d
            rows.append(row)
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/timeline_families.csv', index=False)
# ---- figure
fig, ax = plt.subplots(figsize=(13, 6.6))
y = 0; labels = []
for L in tl['launch_families']:
    d0 = dt.datetime.strptime(L['date'], '%Y-%m-%d'); ph = tl['phases']
    tr = ph['transfer_days']; loi = ph['loi_and_circularisation_days']; com = ph['commissioning_days']
    t_loi = d0 + dt.timedelta(days=tr['nominal']); t_sci = t_loi + dt.timedelta(days=loi['nominal'] + com['nominal'])
    ax.barh(y, (t_loi - d0).days, left=d0, color=P.CAT[0], height=0.6, label='transfer (~2 months)' if y == 0 else None)
    ax.barh(y, (t_sci - t_loi).days, left=t_loi, color=P.CAT[2], height=0.6, label='orbit insertion + circularisation + commissioning' if y == 0 else None)
    for k, S in enumerate(ph['science_months']):
        t_end = t_sci + dt.timedelta(days=30.44 * S); t_prev = t_sci + dt.timedelta(days=30.44 * (ph['science_months'][k - 1] if k else 0))
        ax.barh(y, (t_end - t_prev).days, left=t_prev, color=P.CAT[1], alpha=1 - 0.2 * k, height=0.6, label='orbital science: 3 / 6 / 12 / 18 months' if (y == 0 and k == 0) else None)
        ax.plot(t_end + dt.timedelta(days=ph['terminal_phase_days']['nominal']), y, marker='v', color='k', ms=6)
    ax.plot([d0 + dt.timedelta(days=tr['min']), d0 + dt.timedelta(days=tr['max'])], [y + 0.42, y + 0.42], color=P.TEXT2, lw=1)
    labels.append(f"{L['id']}: {L['date']} ({L['label']})"); y += 1
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8); ax.invert_yaxis()
for a, b in lro_low:
    ax.axvspan(dt.datetime.strptime(a, '%Y-%m-%d'), dt.datetime.strptime(b, '%Y-%m-%d'), color=P.CAT[6], alpha=0.10)
for d in ev.start:
    ax.axvline(d, color=P.CAT[3], lw=0.5, alpha=0.5)
ax.axvspan(dt.datetime(2026, 1, 1), d_start, color='0.85', alpha=0.4); ax.axvspan(d_stop, dt.datetime(2031, 1, 1), color='0.85', alpha=0.4)
ax.plot([], [], color=P.CAT[3], lw=1, label='Turkish evening calendar sessions with illum 0.12-0.5 and Moon > 25 deg at TUG (best hour)')
ax.fill_between([], [], color=P.CAT[6], alpha=0.2, label='approximate LRO low-Sun seasons (orbit plane; not target passes)')
ax.fill_between([], [], color='0.85', alpha=0.6, label='outside the computed domain'); ax.plot([], [], 'kv', label='impact (end of science + ~10-day terminal phase)')
ax.set_xlim(dt.datetime(2027, 1, 1), dt.datetime(2030, 1, 1)); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=3, frameon=False)
ax.set_title("Launch-to-impact families (MODELLING CHOICES: sources say 'first months', 'first half' and 'Q2' 2027; the impact hour is set by the orbital pass)", loc='left', fontsize=9)
P.evidence_tag(fig, 'HYPOTHETICAL SCENARIO FAMILIES - no launch date has been announced (cutoff 2026-10-05)')
fig.tight_layout(); P.savefig(fig, 'fig_timeline_families')
print(df[df.phase_case == 'nominal'].to_string())
