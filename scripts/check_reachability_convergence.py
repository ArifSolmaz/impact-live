"""Convergence of the reachability DECISION quantities (audit GE-08): for a subset of six orbit planes of the main
family, the opportunity classes are recomputed with (a) the production settings (10-min overflight grid, 8 phases),
(b) a 5-min grid and (c) 16 phases, and the decision quantities are compared: the window probability
P(>= 1 opportunity within 30 days) averaged over all start days and its minimum, the probability of a first
opportunity within 3 and 6 months of the reference epoch, and the total opportunity-hours per plane.
check_convergence.py separately covers only broad regional fractions of the screening.
Writes outputs/tables/reachability_convergence.csv."""
import sys, os, numpy as np, yaml, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import reachability as R, ephem as E, opportunities as OP
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml')); dom = yaml.safe_load(open(f'{root}/config/domain.yaml'))
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; cr = dom['criteria']
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
lat, lon = cl['lat'], cl['lon']; pix = E.latlon_to_vec(lat, lon, 1.0); jd_h = cl['jd_utc']; n_hours = len(jd_h)
fs = fam['family_sets']['main']; deltas = list(fam['cross_track_tolerance_deg'])
t_ref = Time(fam['reference_epoch_utc'], scale='utc'); t_ref_tdb = t_ref.tdb.jd; h_ref = int(round((t_ref.utc.jd - jd_h[0]) * 24))
NODES = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0]
VARIANTS = {'production (10 min, 8 phases)': (fam['time_step_min'], fam['phases']), 'fine time (5 min, 8 phases)': (fam['time_step_min'] / 2, fam['phases']),
            'fine phase (10 min, 16 phases)': (fam['time_step_min'], 2 * fam['phases'])}
tic = time.time(); occs = {}
for vname, (step, nph) in VARIANTS.items():
    grid = R.time_grid(jd_h[0], jd_h[-1] + 1 / 24.0, step); ctx = OP.context(grid, jd_h, cl, ob, sites, cr)
    phases = np.radians(np.arange(nph) * 360.0 / nph)
    occ = np.zeros((len(NODES), nph, len(OP.CLASSES), len(deltas), n_hours), bool)
    for ni, node in enumerate(NODES):
        plane = R.Plane(node, t_ref_tdb, fs['inclination_deg'], fam['altitude_km'], 0.0)
        occ[ni], _, _ = OP.node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h[0], n_hours)
    occs[vname] = occ
    print(f'{vname} done ({time.time() - tic:.0f}s)', flush=True)
rows = []
for vname, occ in occs.items():
    for ci, cls in enumerate(OP.CLASSES):
        for di, dl in enumerate(deltas):
            oc = occ[:, :, ci, di, :].reshape(-1, n_hours)
            _, p30 = OP.window_prob(oc, 30); fa = OP.first_after(oc, h_ref)
            per_node = occ[:, :, ci, di, :].any(axis=1).sum(axis=1)          # opportunity-hours per plane (any phase)
            rows.append(dict(variant=vname, cls=cls, delta=dl, mean_p30=float(p30.mean()), min_p30=float(p30.min()), p_first_3mo=float(np.mean(fa <= 91.3)),
                             p_first_6mo=float(np.mean(fa <= 182.6)), opp_hours_per_plane=float(per_node.mean())))
df = pd.DataFrame(rows)
base = df[df.variant.str.startswith('production')].set_index(['cls', 'delta'])
for q in ('mean_p30', 'min_p30', 'p_first_3mo', 'p_first_6mo'):
    df[f'd_{q}'] = [r[q] - base.loc[(r['cls'], r['delta'])][q] for _, r in df.iterrows()]
df['rel_d_opp_hours'] = [(r['opp_hours_per_plane'] - base.loc[(r['cls'], r['delta'])]['opp_hours_per_plane']) / max(base.loc[(r['cls'], r['delta'])]['opp_hours_per_plane'], 1e-9) for _, r in df.iterrows()]
df.to_csv(f'{root}/outputs/tables/reachability_convergence.csv', index=False)
print(df[['variant', 'cls', 'delta', 'mean_p30', 'd_mean_p30', 'd_min_p30', 'd_p_first_3mo', 'rel_d_opp_hours']].round(3).to_string())
print(f'max |d mean_p30| {df.d_mean_p30.abs().max():.3f}; max |d p_first_3mo| {df.d_p_first_3mo.abs().max():.3f}; max |rel d opp-hours| {df.rel_d_opp_hours.abs().max():.3f}')
