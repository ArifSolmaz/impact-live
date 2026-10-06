"""Figures: full-surface visibility/illumination/coverage maps from the stage-1 screening."""
import sys, os, numpy as np, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
m = np.load(f'{root}/outputs/screening/maps.npz'); nside = int(m['nside'])
cl = np.load(f'{root}/outputs/screening/classes.npz')
nh = len(cl['jd_utc'])
fig, axs = plt.subplots(2, 2, figsize=(13, 7.2))
P.lunar_map(axs[0, 0], m['frac_visible'] * 100, nside, 'a) Fraction of domain hours the point faces Earth (emission < 86 deg, geocentric)', cbar_label='% of hours', vmin=0, vmax=100)
P.lunar_map(axs[0, 1], m['frac_flash'] * 100, nside, 'b) Flash-favourable geometry: dark side, Earth-facing, phase 3-65 %, elongation > 30 deg', cbar_label='% of hours', vmin=0, vmax=35)
P.lunar_map(axs[1, 0], m['h_cov3'], nside, 'c) Hours with flash-favourable geometry and >= 3 configured sites in dark sky, Moon > 20 deg', cbar_label='hours in domain', vmin=0)
P.lunar_map(axs[1, 1], m['h_tr'], nside, 'd) Same, with >= 1 Turkish site available', cbar_label='hours in domain', vmin=0)
fig.suptitle(f'Full-surface screening, impact-epoch domain 2027-08-01 to 2029-03-01 ({nh} hourly epochs), HEALPix nside={nside} (1.8 deg)', fontsize=10)
P.evidence_tag(fig, 'COMPUTED GEOMETRY (DE421; no mission trajectory used) - not a mission prediction')
fig.tight_layout(); print(P.savefig(fig, 'fig_surface_screening'))
# plume map + earth view
fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(width_ratios=[1.6, 1]))
P.lunar_map(axs[0], m['frac_plume'] * 100, nside, 'a) Sunlit-plume geometry: point 0.5-6 deg beyond the terminator (night side), Earth-facing, good phase', cbar_label='% of hours', vmin=0)
P.earth_view(axs[1], m['h_tr'], nside, 0, 0, 'b) Earth view: hours flash-favourable & Turkish site available', cbar_label='hours in domain', vmin=0)
P.evidence_tag(fig, 'COMPUTED GEOMETRY - not a mission prediction')
fig.tight_layout(); print(P.savefig(fig, 'fig_plume_and_earthview'))
# time series of availability
import pandas as pd
from astropy.time import Time
ob = np.load(f'{root}/outputs/screening/observers.npz')
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
jd = cl['jd_utc']; t = Time(jd, format='jd', scale='utc').to_datetime()
avail = ob['avail']; ids = list(ob['ids'])
tr = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']
df = pd.DataFrame(dict(t=t, n_sites=avail.sum(axis=0), n_tr=avail[tr].sum(axis=0), illum=cl['illum'], phase_ok=cl['phase_ok']))
df['day'] = pd.to_datetime(df.t).dt.floor('D')
daily = df.groupby('day').agg(hours_global=('n_sites', lambda x: (x >= 3).sum()), hours_tr=('n_tr', lambda x: (x >= 1).sum()),
                              hours_tr_phase=('n_tr', lambda x: ((x >= 1) & (df.loc[x.index, 'phase_ok'])).sum()), illum=('illum', 'mean'))
fig, ax = plt.subplots(figsize=(13, 3.2))
ax.fill_between(daily.index, daily.hours_tr_phase, color=P.CAT[1], alpha=0.8, label='hours/day: >=1 Turkish site (Moon>20 deg, Sun<-12 deg) AND lunar phase 3-65 %')
ax.plot(daily.index, daily.hours_global, color=P.CAT[0], lw=1.2, label='hours/day: >=3 configured sites available (any phase)')
ax2 = ax.twinx(); ax2.plot(daily.index, daily.illum, color=P.TEXT2, lw=0.6); ax2.set_ylabel('illuminated fraction', color=P.TEXT2); ax2.set_ylim(0, 1)
ax.set_ylabel('hours per day'); ax.legend(loc='upper left', fontsize=7); ax.set_xlim(daily.index.min(), daily.index.max())
ax.set_title('Observer availability over the impact-epoch domain (illuminated fraction shown thin grey on right axis for phase context)', loc='left')
P.evidence_tag(fig, 'COMPUTED GEOMETRY - site list in config/sites.yaml')
fig.tight_layout(); print(P.savefig(fig, 'fig_availability_timeseries'))
daily.to_csv(f'{root}/outputs/tables/daily_availability.csv')
