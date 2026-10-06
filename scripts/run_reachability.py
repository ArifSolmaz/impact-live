"""Conditional reachability: for each orbit-plane family, which (pixel, epoch) pairs that are flash/plume-favourable
and observable are also on the ground track (within the cross-track tolerance).  Produces per-family maps and the
family-averaged map, plus a catalogue of reachable favourable opportunities with Turkish coverage."""
import sys, os, numpy as np, yaml, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import reachability as Rr, grid as Gd, ephem as E
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml'))
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
flags = cl['flags']; jd = cl['jd_utc']; phase_ok = cl['phase_ok']; lat = cl['lat']; lon = cl['lon']; nside = int(cl['nside'])
vis = (flags & 1) > 0; dark = (flags & 2) > 0; term = (flags & 4) > 0
flash_fav = vis & dark & phase_ok[:, None]; plume_fav = vis & term & phase_ok[:, None]
avail = ob['avail']; tr = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']
n_avail = avail.sum(axis=0); n_tr = avail[tr].sum(axis=0)
tug = list(ob['ids']).index('TUG'); tug_avail = avail[tug]
t_ref = Time(fam['reference_epoch_utc'], scale='utc').utc.jd
p = E.latlon_to_vec(lat, lon, 1.0)                              # unit vectors P x 3
out = f'{root}/outputs/reachability'; os.makedirs(out, exist_ok=True)
results = {}
tic = time.time()
for tol in fam['cross_track_tolerance_deg']:
    for drift in fam['node_drift_deg_day']:
        maps_flash_cov3 = []; maps_flash_tr = []; maps_plume_tr = []; maps_reach = []
        catalogue = []
        for om in fam['node_longitudes_deg']:
            sc = Rr.OrbitScenario(f'O{om}', om, t_ref, fam['altitude_km'], fam['inclination_deg'], drift, 0.0, tol)
            lam = np.radians(Rr.node_longitude(sc, jd))
            i = np.radians(sc.inclination_deg)
            n = np.stack([np.sin(i) * np.sin(lam), -np.sin(i) * np.cos(lam), np.cos(i) * np.ones_like(lam)], axis=1)   # N x 3
            reach = np.zeros(flags.shape, dtype=bool)
            for a in range(0, len(jd), 1500):
                ct = np.degrees(np.abs(np.arcsin(np.clip(n[a:a + 1500] @ p.T, -1, 1))))
                reach[a:a + 1500] = ct <= tol
            r_flash3 = reach & flash_fav & (n_avail >= 3)[:, None]
            r_flash_tr = reach & flash_fav & (n_tr >= 1)[:, None]
            r_plume_tr = reach & plume_fav & (n_tr >= 1)[:, None]
            maps_reach.append(reach.mean(axis=0)); maps_flash_cov3.append(r_flash3.sum(axis=0)); maps_flash_tr.append(r_flash_tr.sum(axis=0)); maps_plume_tr.append(r_plume_tr.sum(axis=0))
            # catalogue: epochs x pixels with flash geometry, reachable, TUG available and >= 3 sites
            ii, pp = np.where(reach & flash_fav & tug_avail[:, None] & (n_avail >= 3)[:, None])
            for k in range(0, len(ii), max(1, len(ii) // 4000)):   # thin to keep the table manageable
                e, px = ii[k], pp[k]
                catalogue.append(dict(family=f'tol{tol}_drift{drift}_om{om}', jd=jd[e], pixel=px, lat=lat[px], lon=lon[px], n_sites=n_avail[e], n_tr=n_tr[e],
                                      illum=cl['illum'][e], plume=bool(plume_fav[e, px])))
        key = f'tol{tol}_drift{drift}'
        results[key] = dict(reach=np.array(maps_reach), flash_cov3=np.array(maps_flash_cov3), flash_tr=np.array(maps_flash_tr), plume_tr=np.array(maps_plume_tr))
        pd.DataFrame(catalogue).to_csv(f'{out}/catalogue_{key}.csv', index=False)
        print(key, 'done %.0fs' % (time.time() - tic), 'catalogue rows', len(catalogue))
np.savez_compressed(f'{out}/reachability_maps.npz', lat=lat, lon=lon, nside=nside, families=np.array(fam['node_longitudes_deg']),
                    **{f'{k}_{q}': v[q] for k, v in results.items() for q in v})
# summary table per region
import healpy as hp
reg = Gd.region_label(lat, lon)
rows = []
for key, v in results.items():
    for q in ['flash_cov3', 'flash_tr', 'plume_tr']:
        fm = v[q].mean(axis=0)   # family-averaged opportunity-hours per pixel
        for r in np.unique(reg):
            m = reg == r
            rows.append(dict(family_set=key, quantity=q, region=r, mean_hours=fm[m].mean(), max_hours=fm[m].max(), frac_pixels_nonzero=(fm[m] > 0).mean()))
pd.DataFrame(rows).to_csv(f'{root}/outputs/tables/reachability_region_summary.csv', index=False)
print(pd.DataFrame(rows).pivot_table(index=['family_set', 'region'], columns='quantity', values='mean_hours').round(2))
