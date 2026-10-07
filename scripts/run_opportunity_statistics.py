"""Opportunity statistics from the trajectory-level overflight analysis (outputs/reachability/opportunities_<set>.npz).

All probabilities are fractions of sampled (orbit-plane, orbital-phase) combinations under a uniform prior on both,
i.e. conditional statements about an unknown plane and phase, not mission forecasts. Products:
  opportunity_window_probability.csv   P(>= 1 admissible opportunity of a class within [T1, T1 + W]) for every start
                                       day T1 in the domain and W = 7-90 days (the terminal-window statistic)
  opportunity_probability_vs_duration.csv   the fixed-start statistic: first opportunity within N months after the
                                       reference epoch (kept for comparison with release 1)
  opportunity_statistics.csv           per (plane, phase): lunations with an opportunity, first opportunity, totals
  timeline_window_probability.csv      for each launch family / science duration: P for terminal windows that open
                                       at the end of the science phase
  opportunity_convergence.csv          the same statistics from subsets of planes and phases (convergence check)
"""
import sys, os, numpy as np, yaml, pandas as pd, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import opportunities as OP
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml')); tl = yaml.safe_load(open(f'{root}/config/timeline.yaml'))
cl = np.load(f'{root}/outputs/screening/classes.npz'); illum_h = cl['illum']; jd_h = cl['jd_utc']
newmoon = (illum_h < 0.01) & (np.gradient(illum_h) >= 0)
lun = np.cumsum(np.r_[0, np.diff(newmoon.astype(int)) == 1])
t_ref_jd = Time(fam['reference_epoch_utc'], scale='utc').utc.jd
WINDOWS = fam['terminal_windows_days']

def load(set_name):
    z = np.load(f'{root}/outputs/reachability/opportunities_{set_name}.npz')
    occ = np.unpackbits(z['occ'], axis=-1, count=int(z['n_hours'])).astype(bool)
    return occ, z

window_prob, first_after = OP.window_prob, OP.first_after

occ, z = load('main')
classes = list(z['classes']); deltas = list(z['deltas']); nodes = z['nodes']; nph = occ.shape[1]
h_ref = int(round((t_ref_jd - jd_h[0]) * 24))
rows_w, rows_d, rows_s, rows_c = [], [], [], []
for ci, cls in enumerate(classes):
    for di, dl in enumerate(deltas):
        occ_c = occ[:, :, ci, di, :].reshape(-1, occ.shape[-1])
        for W in WINDOWS:
            starts, p = window_prob(occ_c, W)
            for h, pp in zip(starts, p):
                rows_w.append(dict(cls=cls, delta=dl, start_utc=Time(jd_h[h], format='jd').utc.iso[:10], W_days=W, p=float(pp)))
        fa = first_after(occ_c, h_ref)
        for N in [3, 4, 6, 9, 12, 18]:
            rows_d.append(dict(cls=cls, delta=dl, months=N, p_at_least_one=float(np.mean(fa <= 30.44 * N)), n_combinations=int(occ_c.shape[0])))
        for comb in range(occ_c.shape[0]):
            per_lun = pd.Series(occ_c[comb]).groupby(lun).any()
            rows_s.append(dict(cls=cls, delta=dl, node=float(nodes[comb // nph]), phase_deg=float(z['phases_deg'][comb % nph]), n_lunations_with_opp=int(per_lun.sum()),
                               n_lunations=int(per_lun.index.max() + 1), first_after_ref_days=float(fa[comb]), opportunity_hours=int(occ_c[comb].sum())))
        # convergence: subsets of planes (every 2nd node) and phases (every 2nd phase)
        for lab, nsel, psel in [('all', slice(None), slice(None)), ('nodes/2', slice(None, None, 2), slice(None)), ('phases/2', slice(None), slice(None, None, 2)), ('both/2', slice(None, None, 2), slice(None, None, 2))]:
            oc = occ[nsel, psel, ci, di, :].reshape(-1, occ.shape[-1])
            _, p30 = window_prob(oc, 30); fa_s = first_after(oc, h_ref)
            rows_c.append(dict(cls=cls, delta=dl, subset=lab, n_combinations=int(oc.shape[0]), mean_p30=float(p30.mean()), min_p30=float(p30.min()),
                               p_first_3mo=float(np.mean(fa_s <= 91.3)), p_first_6mo=float(np.mean(fa_s <= 182.6))))
pd.DataFrame(rows_w).to_csv(f'{root}/outputs/tables/opportunity_window_probability.csv', index=False)
pd.DataFrame(rows_d).to_csv(f'{root}/outputs/tables/opportunity_probability_vs_duration.csv', index=False)
pd.DataFrame(rows_s).to_csv(f'{root}/outputs/tables/opportunity_statistics.csv', index=False)
conv = pd.DataFrame(rows_c)
# differences of each subset from the full set
full = conv[conv.subset == 'all'].set_index(['cls', 'delta'])
conv['d_mean_p30'] = [r.mean_p30 - full.loc[(r.cls, r.delta)].mean_p30 for r in conv.itertuples()]
conv['d_p_first_3mo'] = [r.p_first_3mo - full.loc[(r.cls, r.delta)].p_first_3mo for r in conv.itertuples()]
conv.to_csv(f'{root}/outputs/tables/opportunity_convergence.csv', index=False)
# ---- launch families: terminal windows opening at the end of the science phase (nominal phase durations)
rows_t = []
sets = {'main': occ}
if os.path.exists(f'{root}/outputs/reachability/opportunities_incl88_j2.npz'):
    sets['incl88_j2'] = load('incl88_j2')[0]
for L in tl['launch_families']:
    d0 = dt.datetime.strptime(L['date'], '%Y-%m-%d'); ph = tl['phases']
    t_sci = d0 + dt.timedelta(days=ph['transfer_days']['nominal'] + ph['loi_and_circularisation_days']['nominal'] + ph['commissioning_days']['nominal'])
    for S_m in ph['science_months']:
        t_open = t_sci + dt.timedelta(days=30.44 * S_m)
        h0 = int(round((Time(t_open).utc.jd - jd_h[0]) * 24))
        for set_name, oc_all in sets.items():
            for ci, cls in enumerate(classes):
                for di, dl in enumerate(deltas):
                    oc = oc_all[:, :, ci, di, :].reshape(-1, oc_all.shape[-1])
                    row = dict(launch=L['id'], science_months=S_m, window_opens=str(t_open.date()), family_set=set_name, cls=cls, delta=dl)
                    for W in [14, 30, 60]:
                        W_h = W * 24
                        row[f'p_{W}d'] = float(oc[:, h0:h0 + W_h].any(axis=1).mean()) if (h0 >= 0 and h0 + W_h <= oc.shape[1]) else None
                    rows_t.append(row)
pd.DataFrame(rows_t).to_csv(f'{root}/outputs/tables/timeline_window_probability.csv', index=False)
po = pd.DataFrame(rows_d)
print(po.pivot_table(index=['delta', 'cls'], columns='months', values='p_at_least_one').round(2))
wp = pd.DataFrame(rows_w)
print(wp[wp.W_days == 30].groupby(['delta', 'cls']).p.describe()[['mean', 'min', '50%', 'max']].round(2))
print(conv[['cls', 'delta', 'subset', 'mean_p30', 'd_mean_p30', 'd_p_first_3mo']].round(3).to_string())
