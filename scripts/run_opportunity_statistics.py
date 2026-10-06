"""Per-lunation opportunity statistics for each orbit-plane family: does a reachable, flash-favourable, Turkish-
evening (or any-site) opportunity exist in each lunation?  Then P(>=1 opportunity within the first N months of the
orbital mission, counting only opportunities on or after the assumed start of operations) marginalised over the unknown
node longitude.  Also the far-side/polar/limb alternatives."""
import sys, os, numpy as np, yaml, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import reachability as Rr, ephem as E, grid as Gd
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
fam = yaml.safe_load(open(f'{root}/config/orbit_families.yaml')); sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
cl = np.load(f'{root}/outputs/screening/classes.npz'); ob = np.load(f'{root}/outputs/screening/observers.npz')
flags = cl['flags']; jd = cl['jd_utc']; phase_ok = cl['phase_ok']; lat = cl['lat']; lon = cl['lon']; illum = cl['illum']
vis = (flags & 1) > 0; dark = (flags & 2) > 0; term = (flags & 4) > 0
emis = cl['emission']
central = (np.abs(lat) < 45) & (np.abs(lon) < 60)          # robust region (emission < ~65 deg)
flash_fav = vis & dark & phase_ok[:, None]
avail = ob['avail']; ids = list(ob['ids']); tr = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']
n_avail = avail.sum(axis=0); n_tr = avail[tr].sum(axis=0); tug = avail[ids.index('TUG')]
ut_hour = (jd + 0.5) % 1 * 24
evening_tr = tug & (ut_hour >= 15) & (ut_hour <= 21)       # 18-24 h Istanbul
waxing = np.gradient(illum) > 0
public_phase = (illum >= 0.12) & (illum <= 0.5)
# lunation index: count new moons (illum minima)
newmoon = (illum < 0.01) & (np.gradient(illum) >= 0)
lun = np.cumsum(np.r_[0, np.diff(newmoon.astype(int)) == 1])
t_ref = Time(fam['reference_epoch_utc'], scale='utc').utc.jd
p = E.latlon_to_vec(lat, lon, 1.0)
rows = []; curves = {}
for tol in fam['cross_track_tolerance_deg']:
    for om in np.arange(0, 360, 15):
        sc = Rr.OrbitScenario(f'O{om}', om, t_ref, fam['altitude_km'], fam['inclination_deg'], 0.0, 0.0, tol)
        lam = np.radians(Rr.node_longitude(sc, jd)); i = np.radians(90.0)
        n = np.stack([np.sin(i) * np.sin(lam), -np.sin(i) * np.cos(lam), np.cos(i) * np.ones_like(lam)], axis=1)
        reach = np.zeros(flags.shape, dtype=bool)
        for a in range(0, len(jd), 1500):
            reach[a:a + 1500] = np.degrees(np.abs(np.arcsin(np.clip(n[a:a + 1500] @ p.T, -1, 1)))) <= tol
        # opportunity classes (epoch-level: any pixel satisfying)
        A = (reach & flash_fav & central[None, :]).any(axis=1) & evening_tr & public_phase & waxing & (n_avail >= 3)   # Turkiye evening, central dark, public phase
        B = (reach & flash_fav & central[None, :]).any(axis=1) & (n_avail >= 3)                                      # global science, any time
        C = (reach & flash_fav & central[None, :]).any(axis=1) & (n_tr >= 1)                                          # any Turkish site
        Pm = (reach & vis & term & phase_ok[:, None] & (np.abs(lat) < 60)[None, :]).any(axis=1) & (n_avail >= 3)        # sunlit-plume geometry, global
        for name, arr in [('A_turkiye_evening_public', A), ('B_global_science', B), ('C_any_turkish', C), ('P_plume_global', Pm)]:
            per_lun = pd.Series(arr).groupby(lun).any()
            first = jd[arr][0] if arr.any() else np.nan
            post = arr & (jd >= t_ref)                      # opportunities on or after the assumed start of operations
            first_post = jd[post][0] if post.any() else np.nan
            rows.append(dict(tol=tol, omega0=om, cls=name, n_lunations_with_opp=int(per_lun.sum()), n_lunations=int(per_lun.index.max() + 1),
                             first_opportunity_days_after_ref=float(first - t_ref) if arr.any() else np.nan,
                             first_opportunity_days_after_start=float(first_post - t_ref) if post.any() else np.nan,
                             opp_hours=int(arr.sum()), opp_hours_after_start=int(post.sum())))
        print(f'tol {tol} om {om}: A lunations {rows[-4]["n_lunations_with_opp"]}, first A after {rows[-4]["first_opportunity_days_after_ref"]:.0f} d; B first {rows[-3]["first_opportunity_days_after_ref"]:.0f} d; plume first {rows[-1]["first_opportunity_days_after_ref"]:.0f} d')
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/opportunity_statistics.csv', index=False)
# P(>=1 opportunity within N months) marginalised over omega0
out = []
for tol in fam['cross_track_tolerance_deg']:
    for cls in df.cls.unique():
        d = df[(df.tol == tol) & (df.cls == cls)]
        for N in [3, 4, 6, 9, 12, 18]:
            # primary quantity: first opportunity on or after the assumed start of operations (reference epoch);
            # the variant that also admits opportunities in the pre-start part of the screening domain is kept for transparency
            out.append(dict(tol=tol, cls=cls, months=N, p_at_least_one=float((d.first_opportunity_days_after_start <= 30.44 * N).mean()),
                            p_at_least_one_incl_prestart=float((d.first_opportunity_days_after_ref <= 30.44 * N).mean())))
po = pd.DataFrame(out); po.to_csv(f'{root}/outputs/tables/opportunity_probability_vs_duration.csv', index=False)
print(po.pivot_table(index=['tol', 'cls'], columns='months', values='p_at_least_one').round(2))
