"""Stage-1 full-surface site x epoch x observer screening.  Outputs (outputs/screening/):
  classes.npz      per-epoch, per-pixel bit flags (visible, dark, near-terminator) + epoch tables
  observers.npz    per-site, per-epoch Moon/Sun altitudes and availability flags
  maps_*.csv/npz   aggregated maps
Run time ~1-2 min.  All times UTC.
"""
import sys, os, yaml, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import screening as S, grid as Gd
import warnings; warnings.filterwarnings('ignore')

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/domain.yaml'))
sites = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
out = f'{root}/outputs/screening'; os.makedirs(out, exist_ok=True)
d = cfg['domain']; cr = cfg['criteria']
t0 = Time(d['start_utc'], scale='utc'); t1 = Time(d['stop_utc'], scale='utc')
nstep = int(np.floor((t1 - t0).to_value('hr') / d['coarse_step_hours']))
times = t0 + np.arange(nstep) * d['coarse_step_hours'] / 24.0
print('epochs', nstep)
tic = time.time()
t, jd, moon, sun, M = S.epoch_arrays(times)
illum, elong, dist = S.lunar_phase_arrays(moon, sun)
lat, lon, area, npix = Gd.healpix_grid(d['coarse_nside'])
# bit flags: 1 visible(geocentric, emission<max+1 margin), 2 dark (incidence>=min), 4 near-terminator night (plume), 8 sunlit low sun (incidence 75-90)
flags = np.zeros((nstep, npix), dtype=np.uint8)
emis_u8 = np.zeros((nstep, npix), dtype=np.uint8); inc_u8 = np.zeros((nstep, npix), dtype=np.uint8)
for i in range(nstep):
    em, inc = S.surface_classes(moon[i], sun[i], M[i], lat, lon)
    emis_u8[i] = np.clip(np.round(em), 0, 180).astype(np.uint8); inc_u8[i] = np.clip(np.round(inc), 0, 180).astype(np.uint8)
    f = np.zeros(npix, dtype=np.uint8)
    f |= (em < cr['flash']['max_emission_deg'] + 1.0).astype(np.uint8) * 1
    f |= (inc >= cr['flash']['min_incidence_deg']).astype(np.uint8) * 2
    f |= ((inc >= cr['plume_sunlit']['incidence_min_deg']) & (inc <= cr['plume_sunlit']['incidence_max_deg'])).astype(np.uint8) * 4
    f |= ((inc >= 75) & (inc < 90)).astype(np.uint8) * 8
    flags[i] = f
print('surface classes done %.1fs' % (time.time() - tic))
phase_ok = (illum >= cr['flash']['illum_min']) & (illum <= cr['flash']['illum_max']) & (elong >= cr['flash']['min_elongation_deg'])
# observers
obs = {}
for s in sites:
    sky = S.observer_sky(s['lon'], s['lat'], s['alt'], times, moon, sun)
    avail = (sky['moon_alt'] >= cr['observer']['min_moon_alt_deg']) & (sky['sun_alt'] <= cr['observer']['max_sun_alt_deg'])
    pub = (sky['moon_alt'] >= cr['public']['min_moon_alt_deg']) & (sky['sun_alt'] <= cr['public']['max_sun_alt_deg'])
    months = np.array([x.month for x in times.to_datetime()])
    closed = np.isin(months, s.get('closed_months', []))
    obs[s['id']] = dict(moon_alt=sky['moon_alt'].astype(np.float32), sun_alt=sky['sun_alt'].astype(np.float32),
                        avail=avail & ~closed, public=pub & ~closed)
print('observers done %.1fs' % (time.time() - tic))
np.savez_compressed(f'{out}/classes.npz', flags=flags, emission=emis_u8, incidence=inc_u8, jd_utc=times.utc.jd, illum=illum, elong=elong,
                    dist_km=dist, phase_ok=phase_ok, lat=lat, lon=lon, nside=d['coarse_nside'])
np.savez_compressed(f'{out}/observers.npz', ids=np.array(list(obs.keys())),
                    moon_alt=np.array([v['moon_alt'] for v in obs.values()]), sun_alt=np.array([v['sun_alt'] for v in obs.values()]),
                    avail=np.array([v['avail'] for v in obs.values()]), public=np.array([v['public'] for v in obs.values()]))
# aggregated maps
vis = (flags & 1) > 0; dark = (flags & 2) > 0; term = (flags & 4) > 0
frac_visible = vis.mean(axis=0)
flash_fav = vis & dark & phase_ok[:, None]
frac_flash = flash_fav.mean(axis=0)
plume_fav = vis & term & phase_ok[:, None]
frac_plume = plume_fav.mean(axis=0)
# observer-weighted: number of configured sites available at each epoch; Turkish subset
ids = list(obs.keys()); avail = np.array([obs[k]['avail'] for k in ids])            # S x N
tr_idx = [i for i, s in enumerate(sites) if s['group'] == 'turkiye']
n_avail = avail.sum(axis=0); n_tr = avail[tr_idx].sum(axis=0)
# hours per pixel with flash-favourable geometry AND >=3 sites available / >=1 Turkish site
h_cov3 = (flash_fav & (n_avail >= 3)[:, None]).sum(axis=0) * d['coarse_step_hours']
h_tr = (flash_fav & (n_tr >= 1)[:, None]).sum(axis=0) * d['coarse_step_hours']
h_plume_tr = (plume_fav & (n_tr >= 1)[:, None]).sum(axis=0) * d['coarse_step_hours']
best_n = np.where(flash_fav, n_avail[:, None], 0).max(axis=0)
np.savez_compressed(f'{out}/maps.npz', lat=lat, lon=lon, frac_visible=frac_visible, frac_flash=frac_flash, frac_plume=frac_plume,
                    h_cov3=h_cov3, h_tr=h_tr, h_plume_tr=h_plume_tr, best_n=best_n, n_avail=n_avail, n_tr=n_tr, nside=d['coarse_nside'])
import pandas as pd
pd.DataFrame(dict(pixel=np.arange(npix), lat=lat, lon=lon, region=Gd.region_label(lat, lon), frac_visible=frac_visible, frac_flash=frac_flash,
                  frac_plume=frac_plume, hours_flash_cov3=h_cov3, hours_flash_turkiye=h_tr, hours_plume_turkiye=h_plume_tr, best_n_sites=best_n)).to_csv(f'{out}/pixel_summary.csv', index=False)
print('saved; total %.1fs' % (time.time() - tic))
print('domain hours', nstep, 'fraction of epochs phase_ok %.3f' % phase_ok.mean())
print('max frac_visible %.3f  max frac_flash %.3f  max frac_plume %.4f' % (frac_visible.max(), frac_flash.max(), frac_plume.max()))
print('max hours flash & >=3 sites: %.0f ; max hours flash & Turkish site: %.0f ; plume & TR: %.0f' % (h_cov3.max(), h_tr.max(), h_plume_tr.max()))
