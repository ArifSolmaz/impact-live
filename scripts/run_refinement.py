"""Local refinement around each hypothetical scenario only: 5-min epochs over +-3 h with exact topocentric geometry for
every configured site and the SHARED operational availability (screening.observer_availability: Moon/Sun limits and
seasonal closures), and the spread of geocentric emission/incidence over the HEALPix nside-128 pixels within 1 deg of
the point at the scenario epoch. Reports the observing window (contiguous interval containing the epoch with at least
one station available and the point Earth-facing for it), the station counts, and the TUG window. This refines eleven
selected points; it is not a convergence test of the full-domain opportunity statistics (see
check_reachability_convergence.py). Writes outputs/tables/refined_windows.csv."""
import sys, os, json, yaml, numpy as np, pandas as pd, healpy as hp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import screening as S, ephem as E, grid as Gd
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
rows = []
for scn in cfg['scenarios']:
    t0 = Time(scn['epoch_utc'], scale='utc'); dt_min = np.arange(-180, 181, 5)
    times = t0 + dt_min / 1440.0
    _, _, moon, sun, M = S.epoch_arrays(times)
    lat0, lon0 = np.array([scn['lat']]), np.array([scn['lon']])
    avail = np.zeros((len(sites), len(times)), bool)
    months = np.array([x.month for x in times.to_datetime()])
    crit = yaml.safe_load(open(f'{root}/config/domain.yaml'))['criteria']['observer']
    for k, s in enumerate(sites):
        sky = S.observer_sky(s['lon'], s['lat'], s['alt'], times, moon, sun)
        _, oper = S.observer_availability(sky['moon_alt'], sky['sun_alt'], months, s, crit)
        for i in range(len(times)):
            em, inc = S.surface_classes(moon[i], sun[i], M[i], lat0, lon0, sky['obs_gcrs'][i])
            avail[k, i] = (em[0] < 90) and bool(oper[i])
    n = avail.sum(axis=0); i0 = int(np.where(dt_min == 0)[0][0])
    def window(mask):
        if not mask[i0]:
            return None, None
        a = i0; b = i0
        while a > 0 and mask[a - 1]: a -= 1
        while b < len(mask) - 1 and mask[b + 1]: b += 1
        return int(dt_min[a]), int(dt_min[b])
    wa, wb = window(n >= 1)
    tug = [k for k, s in enumerate(sites) if s['id'] == 'TUG'][0]; ta, tb = window(avail[tug])
    # nside-128 neighbourhood within 1 deg at the scenario epoch (geocentric)
    nside = 128; vec = hp.ang2vec(np.radians(90 - scn['lat']), np.radians(scn['lon'] % 360))
    pix = hp.query_disc(nside, vec, np.radians(1.0)); th, ph = hp.pix2ang(nside, pix)
    la = 90 - np.degrees(th); lo = (np.degrees(ph) + 180) % 360 - 180
    em, inc = S.surface_classes(moon[i0], sun[i0], M[i0], la, lo)
    rows.append(dict(id=scn['id'], epoch_utc=scn['epoch_utc'], n_at_epoch=int(n[i0]), window_start_min=wa, window_end_min=wb,
                     window_length_min=(None if wa is None else wb - wa), n_min_in_window=(None if wa is None else int(n[(dt_min >= wa) & (dt_min <= wb)].min())),
                     n_max_pm3h=int(n.max()), tug_window_start_min=ta, tug_window_end_min=tb, n_pix_1deg=len(pix),
                     emission_range_deg=f'{em.min():.1f}-{em.max():.1f}', incidence_range_deg=f'{inc.min():.1f}-{inc.max():.1f}', neighbourhood_geometry='geocentric, at the scenario epoch'))
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/refined_windows.csv', index=False)
print(df.to_string())
