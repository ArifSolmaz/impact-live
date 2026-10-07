"""Trajectory-level impact opportunities and orbit-plane compatibility (see ayap1obs/reachability.py and
ayap1obs/opportunities.py).

For every orbit-plane family and orbital phase, enumerate the overflights of every HEALPix pixel over the screening
domain, evaluate the observing conditions at each overflight time and record:
  * hourly occupancy of the four opportunity classes for every (plane, phase, allowance) -> opportunities_<set>.npz
  * per-pixel counts of admissible flash-favourable overflights (>= 3 sites; >= 1 Turkish site) and of plume-favourable
    overflights with a Turkish site, averaged over phases -> reachability_maps_<set>.npz
  * the orbit-plane compatibility envelope (fraction of time within delta of the plane), for comparison
  * a thinned catalogue of class-B opportunities with TUG available -> catalogue_<set>.csv
These are geometric overflight opportunities of hypothetical planes, not a mission plan: burn targeting, navigation
errors and operations are not modelled (the burn-to-impact arc itself is 27-47 min, reachability.deorbit_trajectory).
"""
import sys, os, numpy as np, yaml, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import reachability as R, grid as Gd, ephem as E, opportunities as OP
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml')); dom = yaml.safe_load(open(f'{root}/config/domain.yaml'))
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']; cr = dom['criteria']
only_sets = sys.argv[1:] or list(fam['family_sets'])
out = f'{root}/outputs/reachability'
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
lat, lon = cl['lat'], cl['lon']; npix = len(lat); pix = E.latlon_to_vec(lat, lon, 1.0)
jd_h = cl['jd_utc']; n_hours = len(jd_h)
tic = time.time()
grid = R.time_grid(jd_h[0], jd_h[-1] + 1 / 24.0, fam['time_step_min'])
print(f"grid {len(grid['jd_utc'])} steps ({time.time() - tic:.0f}s)")
ctx = OP.context(grid, jd_h, cl, ob, sites, cr)
t_ref_tdb = Time(fam['reference_epoch_utc'], scale='utc').tdb.jd
phases = np.radians(np.arange(fam['phases']) * 360.0 / fam['phases'])
deltas = list(fam['cross_track_tolerance_deg'])
env_grid = {k: v[::6] for k, v in grid.items() if k != 'step_min'}; env_grid['step_min'] = grid['step_min'] * 6
for set_name in only_sets:
    fs = fam['family_sets'][set_name]
    nodes = np.arange(fs['node_start'], fs['node_stop'], fs['node_step'], dtype=float)
    drift = R.j2_nodal_rate_deg_day(fs['inclination_deg'], fam['altitude_km']) if fs['drift'] == 'j2' else float(fs['drift'])
    occ = np.zeros((len(nodes), len(phases), len(OP.CLASSES), len(deltas), n_hours), bool)
    maps = np.zeros((len(nodes), len(deltas), len(OP.MAPS), npix), np.float32)
    env = np.zeros((len(nodes), len(deltas), npix), np.float32)
    catalogue = []
    for ni, node in enumerate(nodes):
        plane = R.Plane(node, t_ref_tdb, fs['inclination_deg'], fam['altitude_km'], drift)
        occ[ni], maps[ni], cat = OP.node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h[0], n_hours, catalogue_tag=f'{set_name}_node{node:g}')
        catalogue += cat
        for di, dl in enumerate(deltas):
            env[ni, di] = R.compatibility_fraction(plane, env_grid, pix, dl)
        print(f'{set_name} node {node:5.1f} done ({time.time() - tic:.0f}s)', flush=True)
    np.savez_compressed(f'{out}/opportunities_{set_name}.npz', occ=np.packbits(occ, axis=-1), n_hours=n_hours, jd0=jd_h[0], nodes=nodes, phases_deg=np.degrees(phases),
                        deltas=np.array(deltas), classes=np.array(OP.CLASSES), inclination=fs['inclination_deg'], drift_deg_day=drift)
    np.savez_compressed(f'{out}/reachability_maps_{set_name}.npz', lat=lat, lon=lon, nside=int(cl['nside']), nodes=nodes, deltas=np.array(deltas), map_names=np.array(OP.MAPS),
                        maps=maps, envelope=env)
    pd.DataFrame(catalogue).to_csv(f'{out}/catalogue_{set_name}.csv', index=False)
    if set_name == 'main':
        reg = Gd.region_label(lat, lon); rows = []
        for di, dl in enumerate(deltas):
            for mi, q in enumerate(OP.MAPS):
                fm = maps[:, di, mi].mean(axis=0)
                for r in np.unique(reg):
                    m = reg == r
                    rows.append(dict(delta=dl, quantity=q, region=r, mean_opportunities=float(fm[m].mean()), max_opportunities=float(fm[m].max()), frac_pixels_nonzero=float((fm[m] > 0).mean()),
                                     mean_envelope_hours=float(env[:, di].mean(axis=0)[m].mean() * n_hours)))
        pd.DataFrame(rows).to_csv(f'{root}/outputs/tables/reachability_region_summary.csv', index=False)
        print(pd.DataFrame(rows).pivot_table(index=['delta', 'region'], columns='quantity', values='mean_opportunities').round(2))
print(f'total {time.time() - tic:.0f}s')
