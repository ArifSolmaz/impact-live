"""Numerical convergence and assumption sensitivity of the plume model (re-audit PH-N01, PH-N02, PH-N03) for S2 (dark
site 3 deg beyond the terminator) and S5 (sunlit ground), bus 400 kg/m3, vertical-equivalent rule, sand parameters,
observer TUG. Variants change one numerical setting at a time (fine and coarse cell sizes, number of particles,
integration and record steps, integration window), the declared speed floor and the finite source. Reported: the
largest exposure-integrated SNR (regolith grains, p Phi 0.03, kappa 0.2, subtraction systematic 1e-3 and 1e-2; fine-rich
grains at 1e-3), its time, and the largest visible sunlit mass. Reads geometry and backgrounds from the scenario cards.
Writes outputs/tables/plume_convergence.csv."""
import sys, os, json, time, numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from astropy.time import Time
from ayap1obs import geometry as G, ephem as E, plume as PL
import warnings; warnings.filterwarnings('ignore')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sites = {s['id']: s for s in yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']}
VARIANTS = {'production': {}, 'fine cell 25 m': dict(cell_fine_km=0.025), 'fine cell 100 m': dict(cell_fine_km=0.1),
            'coarse cell 0.25 km': dict(cell_km=0.25), 'coarse cell 1 km': dict(cell_km=1.0),
            'particles x8 (96 x 14 x 32)': dict(n_speed=96, n_elev=14, n_az=32), 'time step x0.5': dict(dt_scale=0.5), 'record step x0.5': dict(rec_scale=0.5),
            'speed floor 0.5 m/s': dict(v_floor=0.5), 'speed floor 2 m/s': dict(v_floor=2.0), 'speed floor 5 m/s': dict(v_floor=5.0),
            'point source at t = 0': dict(finite_source=False), 'window 0.1 s': dict(_t_window=0.1)}
rows = []
for sid in ('S2', 'S5'):
    c = json.load(open(f'{root}/outputs/scenarios/{sid}.json'))
    case = next(x for x in c['plume']['cases'] if x['impactor'] == 'bus 400 kg/m3' and x['rule'] == 'vertical-equivalent')
    ob_card = case['observers']['TUG']; bkg, ext = ob_card['background_sb_V'], ob_card['extinction_mag']
    es = G.epoch_state(c['epoch_utc'])
    site_unit = E.latlon_to_vec(c['lat'], c['lon'], 1.0) @ es.M
    sun_unit = es.r_sun - es.r_moon; sun_unit /= np.linalg.norm(sun_unit)
    tug = sites['TUG']; o_tug = E.observer_gcrs(tug['lon'], tug['lat'], tug['alt'], Time(c['sites']['TUG']['t_reception_utc'], scale='utc'))
    obs = {'TUG': (o_tug - es.r_moon) * 1e3}
    m = float(np.mean(c['physics']['mass_kg'])); v = c['physics']['v_km_s']; ang = c['physics']['angle_deg']
    for vname, kw in VARIANTS.items():
        kw = dict(kw); tw = kw.pop('_t_window', 1.0); kw.setdefault('v_floor', 1.0)
        tic = time.time()
        sim = PL.plume_simulation(site_unit, sun_unit, obs, m, v, ang, model='bus 400 kg/m3', rule='vertical-equivalent', params='sand',
                                  v_lo=max(kw['v_floor'], 0.95 * case['v_needed_m_s']), **kw)
        combos = [dict(grains='regolith', pPhi=0.03, kappa=0.2, sys_frac=1e-3), dict(grains='regolith', pPhi=0.03, kappa=0.2, sys_frac=1e-2),
                  dict(grains='fine-rich', pPhi=0.03, kappa=0.2, sys_frac=1e-3)]
        r = PL.plume_detectability_multi(sim, 'TUG', bkg, combos, ext_mag=ext, t_window=tw)
        k = int(np.argmax(r[0]['snr']))
        rows.append(dict(scenario=sid, variant=vname, snr_regolith_sys1e3=float(r[0]['snr'].max()), t_max_s=float(r[0]['t_start'][k]),
                         snr_regolith_sys1e2=float(r[1]['snr'].max()), snr_fine_rich_sys1e3=float(r[2]['snr'].max()),
                         M_vis_max_kg=float(sim['observers']['TUG']['M_vis'].max()), v_lo_m_s=sim['v_lo'], n_particles=sim['n_particles']))
        print({**rows[-1], 'seconds': round(time.time() - tic, 1)}, flush=True)      # run time in the log only (not deterministic)
df = pd.DataFrame(rows)
base = df[df.variant == 'production'].set_index('scenario')
df['rel_d_snr_regolith'] = [r['snr_regolith_sys1e3'] / max(base.loc[r['scenario'], 'snr_regolith_sys1e3'], 1e-12) - 1 for _, r in df.iterrows()]
df.to_csv(f'{root}/outputs/tables/plume_convergence.csv', index=False)
print(df[['scenario', 'variant', 'snr_regolith_sys1e3', 'snr_regolith_sys1e2', 'snr_fine_rich_sys1e3', 't_max_s', 'M_vis_max_kg', 'rel_d_snr_regolith']].round(3).to_string())
