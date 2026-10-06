"""Grid and time-step convergence of the Stage-1 screening: regional means of the Earth-facing fraction and of the
flash-favourable fraction at HEALPix nside 32 vs 64 (on a 6-hourly subsample of epochs), and hourly vs 6-hourly
sampling at nside 32.  Writes outputs/tables/convergence.csv."""
import sys, os, numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import screening as S, grid as Gd
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cr = yaml.safe_load(open(f'{root}/config/domain.yaml'))['criteria']
cl = np.load(f'{root}/outputs/screening/classes.npz')
jd_all = cl['jd_utc']; phase_ok_all = cl['phase_ok']
sub = np.arange(0, len(jd_all), 6)
t = Time(jd_all[sub], format='jd', scale='utc')
_, _, moon, sun, M = S.epoch_arrays(t)
rows = []
res = {}
for nside in (32, 64):
    lat, lon, area, npix = Gd.healpix_grid(nside)
    vis = np.zeros(npix); fl = np.zeros(npix)
    for i in range(len(sub)):
        em, inc = S.surface_classes(moon[i], sun[i], M[i], lat, lon)
        v = em < cr['flash']['max_emission_deg'] + 1.0
        vis += v; fl += v & (inc >= cr['flash']['min_incidence_deg']) & phase_ok_all[sub[i]]
    res[nside] = (Gd.region_label(lat, lon), vis / len(sub), fl / len(sub))
# hourly nside-32 values from the full screening
flags = cl['flags']; vis_h = ((flags & 1) > 0).mean(axis=0); fl_h = (((flags & 1) > 0) & ((flags & 2) > 0) & phase_ok_all[:, None]).mean(axis=0)
reg32 = res[32][0]
for r in sorted(set(reg32)):
    m32 = res[32][0] == r; m64 = res[64][0] == r
    rows.append(dict(region=r, vis_n32_6h=res[32][1][m32].mean(), vis_n64_6h=res[64][1][m64].mean(), vis_n32_1h=vis_h[m32].mean(),
                     flash_n32_6h=res[32][2][m32].mean(), flash_n64_6h=res[64][2][m64].mean(), flash_n32_1h=fl_h[m32].mean()))
df = pd.DataFrame(rows)
df['d_vis_grid'] = df.vis_n64_6h - df.vis_n32_6h; df['d_flash_grid'] = df.flash_n64_6h - df.flash_n32_6h
df['d_vis_time'] = df.vis_n32_1h - df.vis_n32_6h; df['d_flash_time'] = df.flash_n32_1h - df.flash_n32_6h
df.to_csv(f'{root}/outputs/tables/convergence.csv', index=False)
print(df.round(4).to_string())
print('max |grid difference| (absolute fraction): vis %.4f flash %.4f; max |time-step difference|: vis %.4f flash %.4f' % (
    df.d_vis_grid.abs().max(), df.d_flash_grid.abs().max(), df.d_vis_time.abs().max(), df.d_flash_time.abs().max()))
