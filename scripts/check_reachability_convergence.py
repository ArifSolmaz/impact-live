"""Convergence of the opportunity DECISION quantities (audit GE-08, re-audit GE-08): for six directed orbit planes of
the main family (nodes 0, 60, ..., 300 deg: three geometric planes in both traversal directions) the opportunity
classes are recomputed with
  (a) the production settings (10-min overflight grid, 8 phases, HEALPix nside 32, 25 m/s deorbit burn),
  (b) a 5-min grid, (c) 16 phases, (d) nside 64 pixels (0.92 deg, finer than the 1.2-deg full width of the 0.6-deg
      allowance band; nside 32 pixels are 1.83 deg), (e) nodes shifted by +2.5 deg, (f) phases shifted by +22.5 deg, (g) a 50 m/s burn,
and the decision quantities are compared: the window probability P(>= 1 opportunity within 30 days) averaged over all
start days and its minimum, the probability of a first opportunity within 3 and 6 months of the reference epoch, and
the total opportunity-hours per plane. Variants (e) and (f) test grid aliasing: they sample different planes/phases,
so their differences measure sampling sensitivity rather than numerical error. All conditions are evaluated at the
impact times (opportunities.gates_at).
check_convergence.py separately covers only broad regional fractions of the screening.
Writes outputs/tables/reachability_convergence.csv."""
import sys, os, numpy as np, yaml, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import reachability as R, ephem as E, opportunities as OP, grid as Gd
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml')); dom = yaml.safe_load(open(f'{root}/config/domain.yaml'))
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; cr = dom['criteria']
cl = np.load(f'{root}/outputs/screening/classes.npz')
lat32, lon32 = cl['lat'], cl['lon']; jd_h = cl['jd_utc']; n_hours = len(jd_h)
lat64, lon64, _, _ = Gd.healpix_grid(64)
fs = fam['family_sets']['main']; deltas = list(fam['cross_track_tolerance_deg']); dv0 = float(fam['deorbit_dv_m_s'][0])
t_ref = Time(fam['reference_epoch_utc'], scale='utc'); t_ref_tdb = t_ref.tdb.jd; h_ref = int(round((t_ref.utc.jd - jd_h[0]) * 24))
NODES = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
P8 = fam['phases']
VARIANTS = {  # name: (grid step min, n phases, phase offset deg, nside, node offset deg, deorbit dv)
    'production (10 min, 8 phases, nside 32)': (fam['time_step_min'], P8, 0.0, 32, 0.0, dv0),
    'fine time (5 min)': (fam['time_step_min'] / 2, P8, 0.0, 32, 0.0, dv0),
    'fine phase (16 phases)': (fam['time_step_min'], 2 * P8, 0.0, 32, 0.0, dv0),
    'fine space (nside 64)': (fam['time_step_min'], P8, 0.0, 64, 0.0, dv0),
    'shifted nodes (+2.5 deg)': (fam['time_step_min'], P8, 0.0, 32, 2.5, dv0),
    'shifted phases (+22.5 deg)': (fam['time_step_min'], P8, 180.0 / P8, 32, 0.0, dv0),
    'burn 50 m/s': (fam['time_step_min'], P8, 0.0, 32, 0.0, float(fam['deorbit_dv_m_s'][1])),
}
tic = time.time(); occs = {}; grids = {}
for vname, (step, nph, ph_off, nside, node_off, dv) in VARIANTS.items():
    if step not in grids:
        g = R.time_grid(jd_h[0], jd_h[-1] + 1 / 24.0, step); grids[step] = (g, OP.context(g, sites, cr))
    grid, ctx = grids[step]
    lat, lon = (lat32, lon32) if nside == 32 else (lat64, lon64)
    pix = E.latlon_to_vec(lat, lon, 1.0)
    phases = np.radians(np.arange(nph) * 360.0 / nph + ph_off)
    occ = np.zeros((len(NODES), nph, len(OP.CLASSES), len(deltas), n_hours), bool)
    for ni, node in enumerate(NODES):
        plane = R.Plane(node + node_off, t_ref_tdb, fs['inclination_deg'], fam['altitude_km'], 0.0)
        occ[ni], _, _ = OP.node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h[0], n_hours, alt_km=fam['altitude_km'], dv_m_s=dv)
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
df['kind'] = ['numerical' if v.startswith(('fine', 'production')) else ('burn' if 'burn' in v else 'sampling') for v in df.variant]
df.to_csv(f'{root}/outputs/tables/reachability_convergence.csv', index=False)
print(df[['variant', 'cls', 'delta', 'mean_p30', 'd_mean_p30', 'd_min_p30', 'd_p_first_3mo', 'rel_d_opp_hours']].round(3).to_string())
for kind in ('numerical', 'sampling', 'burn'):
    d = df[df.kind == kind]
    print(f'{kind}: max |d mean_p30| {d.d_mean_p30.abs().max():.3f}; max |d min_p30| {d.d_min_p30.abs().max():.3f}; max |d p_first_3mo| {d.d_p_first_3mo.abs().max():.3f}; '
          f'max |rel d opp-hours| {d.rel_d_opp_hours.abs().max():.3f}')
