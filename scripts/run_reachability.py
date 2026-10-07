"""Circular-overflight screening opportunities and orbit-plane compatibility (see ayap1obs/reachability.py and
ayap1obs/opportunities.py).

For every orbit-plane family (directed planes: nodes over [0, 360)) and orbital phase, enumerate the overflights of
every HEALPix pixel over the screening domain, convert each into an impact time for the production deorbit burn
(25 m/s: impact 91.5 s before the circular overflight), evaluate the observing conditions at that time and record:
  * hourly occupancy of the four opportunity classes for every (plane, phase, allowance) -> opportunities_<set>.npz
  * per-pixel counts of admissible overflights with flash geometry (>= 3 sites; >= 1 Turkish site) and with sunlit-plume
    geometry and a Turkish site, averaged over phases -> reachability_maps_<set>.npz
  * the orbit-plane compatibility envelope (fraction of time within delta of the plane), for comparison
  * a thinned catalogue of class-B opportunities with TUG available (circular-overflight, burn and impact times)
    -> catalogue_<set>.csv
  * a numerical check of the burn-to-impact mapping for the catalogue entries -> outputs/validation/transfer_check.json
These are screening opportunities of hypothetical planes, not a mission plan: burn targeting, navigation errors,
the cross-track manoeuvre and operations are not modelled (the burn-to-impact arc itself is 27-47 min).
"""
import sys, os, json, numpy as np, yaml, pandas as pd, time
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
ctx = OP.context(grid, sites, cr)
print(f"exact station geometry on the grid ({time.time() - tic:.0f}s)")
dv_ref = float(fam['deorbit_dv_m_s'][0]); dt_imp, t_flight = OP.transfer_offset_s(fam['altitude_km'], dv_ref)
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
        occ[ni], maps[ni], cat = OP.node_occupancy(plane, grid, ctx, pix, lat, lon, phases, deltas, cr, jd_h[0], n_hours, catalogue_tag=f'{set_name}_node{node:g}',
                                                   alt_km=fam['altitude_km'], dv_m_s=dv_ref)
        catalogue += cat
        for di, dl in enumerate(deltas):
            env[ni, di] = R.compatibility_fraction(plane, env_grid, pix, dl)
        print(f'{set_name} node {node:5.1f} done ({time.time() - tic:.0f}s)', flush=True)
    np.savez_compressed(f'{out}/opportunities_{set_name}.npz', occ=np.packbits(occ, axis=-1), n_hours=n_hours, jd0=jd_h[0], nodes=nodes, phases_deg=np.degrees(phases),
                        deltas=np.array(deltas), classes=np.array(OP.CLASSES), inclination=fs['inclination_deg'], drift_deg_day=drift,
                        deorbit_dv_m_s=dv_ref, impact_before_overflight_s=dt_imp, burn_to_impact_s=t_flight, hours_by='impact time')
    np.savez_compressed(f'{out}/reachability_maps_{set_name}.npz', lat=lat, lon=lon, nside=int(cl['nside']), nodes=nodes, deltas=np.array(deltas), map_names=np.array(OP.MAPS),
                        maps=maps, envelope=env)
    pd.DataFrame(catalogue).to_csv(f'{out}/catalogue_{set_name}.csv', index=False)
    # numerical check of the burn-to-impact mapping (two-body RK4 from the burn state) for the catalogue entries
    cdf = pd.DataFrame(catalogue)
    if len(cdf):
        sub = cdf.iloc[:: max(1, len(cdf) // 60)]
        miss = []
        for fam_tag, grp in sub.groupby('family'):
            node = float(fam_tag.split('node')[1])
            plane = R.Plane(node, t_ref_tdb, fs['inclination_deg'], fam['altitude_km'], drift)
            jb = Time(grp.jd_utc_burn.values, format='jd', scale='utc').tdb.jd
            jd_imp, p_imp = R.propagate_descent(plane, np.radians(grp.phase_deg.values), jb, dv_ref)
            # intended point: the circular-orbit ground point at the overflight time (ME frame at that time)
            jo = Time(grp.jd_utc_overflight.values, format='jd', scale='utc').tdb.jd
            n_i, e_i, f_i = plane.vectors_icrf(jo)
            u = np.radians(grp.phase_deg.values) + plane.mean_motion * (jo - plane.t_ref_jd) * 86400.0
            r_c = np.cos(u)[:, None] * e_i + np.sin(u)[:, None] * f_i
            p_c = np.einsum('nij,nj->ni', np.array([E.icrf_to_me(j) for j in jo]), r_c)
            ang = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', p_imp, p_c), -1, 1)))
            dti = (jd_imp - Time(grp.jd_utc_impact.values, format='jd', scale='utc').tdb.jd) * 86400.0
            miss += [dict(family=fam_tag, miss_deg=float(a_), miss_km=float(np.radians(a_) * R.R_MOON), impact_time_error_s=float(d_)) for a_, d_ in zip(ang, dti)]
        chk_path = f'{root}/outputs/validation/transfer_check.json'
        chk = json.load(open(chk_path)) if os.path.exists(chk_path) and set_name != only_sets[0] else {}
        m_ = pd.DataFrame(miss)
        chk[set_name] = dict(deorbit_dv_m_s=dv_ref, impact_before_overflight_s=dt_imp, burn_to_impact_s=t_flight, n_checked=len(m_),
                             max_miss_km=float(m_.miss_km.max()), median_miss_km=float(m_.miss_km.median()), max_abs_impact_time_error_s=float(m_.impact_time_error_s.abs().max()),
                             note='RK4 two-body descent from the burn state compared with the circular-orbit ground point at the overflight time; '
                                  'the residual is the target motion during the 15-92 s offset, which the mapping neglects')
        json.dump(chk, open(chk_path, 'w'), indent=1)
        print(f"{set_name}: burn-to-impact check on {len(m_)} entries: max miss {m_.miss_km.max():.2f} km, max impact-time error {m_.impact_time_error_s.abs().max():.1f} s")
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
