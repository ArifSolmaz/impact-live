"""Physics figures (release 2):
fig_flash_sensitivity  peak band magnitude vs eta_vis and T0 (ballistic case) with the radiative-energy consistency limit
fig_lightcurves_limits light curves (true band peaks), exposure dilution, instrument limits vs exposure
fig_ejecta_crater      ejecta mass-speed with the Housen & Holsapple (2011) domain, shadow height, crater consistency check
fig_plume_S2           phase-space plume for scenario S2 (sunlit visible mass, signal-to-noise) and the LCROSS check
fig_public_thresholds  predicted flash brightness vs visual thresholds (V) and phone limits (broad band, separately)
and outputs/tables/peak_magnitude_distribution.json (seeded prior-predictive sample summary)."""
import sys, os, numpy as np, yaml, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
from ayap1obs import impact as I, detect as D, plotting as P, montecarlo as MC, plume as PL, geometry as G, ephem as E
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); templates = MC.load_templates()
dist = 3.80e8
phys = cfg['physics']['V_BAL']; m_bal = float(np.mean(phys['mass_kg'])); E_k = I.kinetic_energy(m_bal, phys['v_km_s'])
# ---------------------------------------------------------------- 1. sensitivity surfaces
etas = np.logspace(-6, -2.5, 71); T0s = np.linspace(1300, 5800, 61)
LE, TT = np.meshgrid(np.log10(etas), T0s)
fig, axs = plt.subplots(1, 4, figsize=(14.5, 3.8))
eps = 10 ** LE / I.W_eval(TT.ravel()).reshape(TT.shape)
for ax, band in zip(axs, ['Rc', 'Ic', 'J', 'Ks']):
    Z = I.peak_band_magnitude_fast(band, 10 ** LE.ravel(), np.full(LE.size, E_k), TT.ravel(), np.full(LE.size, 0.5), dist).reshape(LE.shape)
    im = ax.imshow(Z, origin='lower', extent=(LE.min(), LE.max(), T0s[0], T0s[-1]), aspect='auto', cmap=P.SEQ_BLUE.reversed(), vmin=2, vmax=18)
    cs = ax.contour(np.log10(etas), T0s, Z, levels=[4, 6, 8, 10, 12, 14, 16], colors='white', linewidths=0.8); ax.clabel(cs, fmt='%d', fontsize=7)
    ax.contourf(np.log10(etas), T0s, eps, levels=[0.1, 1e9], colors='none', hatches=['////'])
    ax.contour(np.log10(etas), T0s, eps, levels=[0.1], colors=P.CAT[7], linewidths=1.2)
    ax.set_title(f'{band} peak magnitude', loc='left'); ax.set_xlabel('log10 eta_vis (0.40-0.90 um)')
    ax.axvspan(np.log10(5e-4), np.log10(3e-3), color=P.CAT[1], alpha=0.15)
axs[0].text(np.log10(np.sqrt(5e-4 * 2.9e-3)), 3600, 'natural\nflashes\n16-72\nkm/s', fontsize=6, color='white', ha='center', va='top')
axs[0].text(-5.9, 1700, 'hatched: radiated energy\n> 10 % of E_k (excluded)', fontsize=6, color=P.CAT[7])
axs[0].set_ylabel('initial temperature T0 (K)')
cb = fig.colorbar(im, ax=axs, fraction=0.02, pad=0.01); cb.set_label('peak Vega magnitude (unocculted, 380 000 km)')
fig.suptitle(f'Flash brightness sensitivity, ballistic case (E_k = {E_k:.2e} J: {m_bal/1e3:.1f} t at {phys["v_km_s"]} km/s), cooling blackbody, tau = 0.5 s, isotropic. '
             f'Laboratory-trend extrapolation (Swift et al. 2011): eta ~ {I.lab_trend_eta(phys["v_km_s"]):.0e}, far left of the axis.', fontsize=8.5)
P.evidence_tag(fig, 'MODEL / HYPOTHETICAL SCENARIO - no calibrated visible efficiency exists for this speed')
P.savefig(fig, 'fig_flash_sensitivity')
# ---------------------------------------------------------------- 2. light curves, dilution, limits
fig, axs = plt.subplots(1, 3, figsize=(13.5, 3.8))
t = np.linspace(0, 3, 600)
for k, (T0, tau) in enumerate([(2000, 0.2), (3000, 0.8), (4500, 0.4)]):
    fm = I.FlashModel(E_k, 1e-4, T0, float(I.floor_temperature(T0)), tau, tau)
    for j, band in enumerate(['V', 'Ic', 'Ks']):
        axs[0].plot(t, fm.magnitude(t, band, dist), color=P.CAT[j], lw=1.6, ls=['-', '--', ':'][k], label=band if k == 0 else None)
        mpk, tpk = fm.peak_magnitude(band, dist, return_time=True)
        if tpk > 0.02:
            axs[0].plot(tpk, mpk, marker='v', color=P.CAT[j], ms=5)
axs[0].set_ylim(18, 4); axs[0].set_xlabel('time since impact (s)'); axs[0].set_ylabel('apparent magnitude')
axs[0].set_title('a) Light curves, eta_vis 1e-4 (solid 2000 K, 0.2 s; dashed 3000 K,\n0.8 s; dotted 4500 K, 0.4 s); triangles: delayed band peaks', loc='left', fontsize=8); axs[0].legend()
exps = np.logspace(-2.5, 1, 40)
for j, band in enumerate(['Rc', 'Ic', 'Ks']):
    for k, tau in enumerate([0.2, 0.8]):
        fm = I.FlashModel(E_k, 1e-4, 3000, float(I.floor_temperature(3000)), tau, tau)
        axs[1].plot(exps, [fm.exposure_averaged_magnitude(band, e, distance_m=dist) for e in exps], color=P.CAT[j], lw=1.6, ls=['-', '--'][k], label=f'{band}, tau {tau} s')
axs[1].set_xscale('log'); axs[1].set_ylim(18, 4); axs[1].set_xlabel('exposure time (s), starting at the onset'); axs[1].set_ylabel('exposure-averaged magnitude')
axs[1].set_title('b) Dilution of the flash in longer exposures (T0 3000 K)', loc='left', fontsize=8); axs[1].legend(fontsize=7)
illum = 0.35
for j, (tname, lab) in enumerate([('lunar_impact_system', 'NELIOTA-like 1.2 m (Rc)'), ('fast_camera_large', '2.4 m fast camera (Rc)'), ('tug_t100_qhy', 'TUG T100 + QHY174GPS (broad)'),
                                  ('amateur_class', 'amateur 0.35 m (broad)'), ('nir_large', '3.6 m NIR (Ks)'), ('dag_dirac', 'DAG 4 m DIRAC (Ks)')]):
    tp = templates[tname]; band = tp['bands'][0]; lm = []
    for e in exps:
        inst = D.Instrument(tname, tp['aperture_m'], band, tp['pixel_scale_arcsec'], tuple(tp['fov_arcmin']), e, e * 1.1, throughput=tp['throughput'], obstruction=0.15,
                            read_noise_e=tp['read_noise_e'], seeing_arcsec=tp['seeing_arcsec'], full_well_e=float(tp.get('saturation_e', 6e4)))
        ext = float(D.extinction_mag(band, 1.2, 2500.0)); bk = D.total_background_sb(band, illum, 8.0, -20, ext_mag=ext)
        ok = D.background_e_per_pixel(inst, bk, e) <= 0.5 * inst.full_well_e
        lm.append(D.limiting_magnitude(inst, bk, 8.0) - ext if ok else np.nan)
    axs[2].plot(exps, lm, color=P.CAT[j], lw=1.6, label=lab)
axs[2].set_xscale('log'); axs[2].set_xlabel('exposure time (s)'); axs[2].set_ylabel('SNR-8 limit, steady source (aperture sum)')
axs[2].set_title("c) Above-atmosphere limits vs exposure (illum 0.35, 8' from sunlit\nterrain, airmass 1.2; lines end where the background passes half full well)", loc='left', fontsize=8)
axs[2].legend(fontsize=6.5); axs[2].set_ylim(6, 20)
P.evidence_tag(fig, 'MODEL - instrument parameters from config/instruments.yaml; backgrounds are declared assumptions')
fig.tight_layout(); P.savefig(fig, 'fig_lightcurves_limits')
# ---------------------------------------------------------------- 3. ejecta, shadow height, crater consistency
fig, axs = plt.subplots(1, 3, figsize=(14, 3.9))
v = np.logspace(0.5, 3.4, 160)
styles = {'vertical-component': '-', 'vertical-equivalent': '--'}
for k, model in enumerate(PL.IMPACTOR_MODELS):
    for rule, ls in styles.items():
        M = PL.ejecta_mass_above_speed_sc(v, m_bal, phys['v_km_s'], phys['angle_deg'], model, rule, 'sand')
        axs[0].plot(v, M, color=P.CAT[k], lw=1.6, ls=ls)
        ok = np.isfinite(M)
        if ok.any():
            axs[0].plot(v[ok][-1], M[ok][-1], marker='|', color=P.CAT[k], ms=10, mew=1.5)
    axs[0].plot([], [], color=P.CAT[k], lw=1.6, label=model)
axs[0].plot([], [], color=P.TEXT2, ls='-', label="rule 'vertical component' (U sin 3 deg)"); axs[0].plot([], [], color=P.TEXT2, ls='--', label="rule 'vertical equivalent' (U)")
axs[0].set_xscale('log'); axs[0].set_yscale('log'); axs[0].set_xlabel('ejecta speed v (m/s)'); axs[0].set_ylabel('mass ejected faster than v (kg)')
axs[0].set_title('a) Ejecta mass-speed, ballistic case (HH2011, sand);\ncurves stop at the scaling-domain edge (bar): faster = cannot determine', loc='left', fontsize=8)
axs[0].legend(fontsize=5.5, loc='lower left')
th = np.linspace(0, 12, 200); axs[1].plot(th, G.shadow_height_km(90 + th), color=P.CAT[0], lw=2)
axs[1].axvspan(0.5, 6, color=P.CAT[1], alpha=0.12); axs[1].text(3.2, 30, 'plume class\n0.5-6 deg:\n0.066-9.57 km', fontsize=7, color=P.CAT[1], ha='center')
axs[1].set_xlabel('angular distance beyond the terminator (deg)'); axs[1].set_ylabel('height of the shadow edge (km)')
axs[1].set_title('b) Height ejecta must reach to be sunlit (point Sun, sphere;\nthe finite solar disc and terrain broaden the edge)', loc='left', fontsize=8); axs[1].set_ylim(0, 40)
# crater consistency: only cases with published mass, speed and angle; no parameter is fitted to any of them
cases = [('GRAIL (each ~130 kg, 1.6 km/s, ~2 deg)', (130, 130), (1.6, 1.7), (1.5, 2.5), 5.0, False),
         ('LADEE (248 kg, 1.699 km/s, low angle: 1-10 deg assumed)', (248, 248), (1.699, 1.699), (1.0, 10.0), 3.0, True),
         ('Falcon 9 stage (3.9-4.9 t, 2.43 km/s, ~31 deg)', (3900, 4900), (2.43, 2.43), (28, 34), 18.0, False)]
crater_check = []
for k, (lab, mm, vv, aa, d_obs, upper) in enumerate(cases):
    rec = dict(case=lab, observed_m=d_obs, observed_is_upper_limit=upper)
    for j, rule in enumerate(('vertical-component', 'vertical-equivalent')):
        vals = []
        for m_ in mm:
            for v_ in vv:
                for a_ in aa:
                    e = I.crater_rim_diameter_envelope(m_, v_, a_)[rule]; vals += [e[0], e[2]]
        lo, hi = min(vals), max(vals); x = d_obs * (0.93 if j == 0 else 1.07)
        rec[rule] = [lo, hi]
        rec[f'{rule}_consistent'] = bool((lo <= d_obs) if upper else (lo <= d_obs <= hi))
        axs[2].plot([x, x], [lo, hi], color=P.CAT[k], lw=3 if j == 1 else 1.5, alpha=0.85)
    axs[2].plot(d_obs, d_obs, marker='<' if upper else 'o', color=P.CAT[k], ms=6, ls='none', label=lab + (' (observed < 3 m)' if upper else ''))
    crater_check.append(rec)
env = I.crater_rim_diameter_envelope(m_bal, phys['v_km_s'], phys['angle_deg'])
axs[2].axhspan(env['all'][0], env['all'][2], color=P.CAT[0], alpha=0.10); axs[2].text(1.15, env['all'][2] * 0.8, 'AYAP-1 ballistic\ncase envelope', fontsize=6, color=P.CAT[0])
axs[2].plot([1, 80], [1, 80], color=P.TEXT2, lw=0.8, ls='--'); axs[2].set_xscale('log'); axs[2].set_yscale('log'); axs[2].set_xlim(1, 80); axs[2].set_ylim(0.8, 120)
axs[2].set_xlabel('observed crater diameter (m, LROC)'); axs[2].set_ylabel('model rim-diameter envelope (m)')
axs[2].set_title('c) Consistency check, no tuning (thin: vertical-component rule;\nthick: vertical-equivalent; parameter sets x densities 150-1000)', loc='left', fontsize=8)
axs[2].legend(fontsize=5.5, loc='upper left')
P.evidence_tag(fig, 'MODEL; panel c compares with OBSERVED LROC crater sizes (research/precedents.csv); not a validation of either oblique-impact rule')
fig.tight_layout(); P.savefig(fig, 'fig_ejecta_crater')
# ---------------------------------------------------------------- 4. plume for S2 and the LCROSS check
s2 = next(s for s in cfg['scenarios'] if s['id'] == 'S2'); es = G.epoch_state(s2['epoch_utc'])
site_unit = E.latlon_to_vec(s2['lat'], s2['lon'], 1.0) @ es.M; sun_unit = (es.r_sun - es.r_moon) / np.linalg.norm(es.r_sun - es.r_moon)
o_tug = E.observer_gcrs(30.3356, 36.8242, 2500.0, es.t); obsv = {'TUG': (o_tug - es.r_moon) * 1e3}
card2 = json.load(open(f'{root}/outputs/scenarios/S2.json'))
bkg_tug = card2['plume']['cases'][-1]['observers'].get('TUG', {}).get('background_sb_V', 13.5) if card2['plume']['cases'] else 13.5
fig, axs = plt.subplots(1, 3, figsize=(14, 3.9))
runs = [('bus 400 kg/m3', 'sand'), ('dense parts + hollow bus', 'sand'), ('dense parts + hollow bus', 'perlite/sand')]
for k, (model, params) in enumerate(runs):
    r = PL.plume_simulation(site_unit, sun_unit, obsv, m_bal, phys['v_km_s'], phys['angle_deg'], model=model, rule='vertical-equivalent', params=params)
    if not r['ok']:
        continue
    ob = r['observers']['TUG']
    axs[0].plot(r['times'], ob['M_vis'], color=P.CAT[k], lw=1.6, label=f'{model}, {params}')
    for sys_f, ls in ((1e-3, '-'), (1e-2, ':')):
        snr, con, pk = PL.plume_detectability(ob, bkg_tug, sys_frac=sys_f)
        axs[1].plot(r['times'], snr, color=P.CAT[k], lw=1.4, ls=ls)
axs[0].set_xlabel('time after impact (s)'); axs[0].set_ylabel('sunlit ejecta mass visible from TUG (kg)')
axs[0].set_title("a) S2 (3.3 deg beyond the terminator, shadow edge 2.9 km):\nsunlit visible mass, rule 'vertical equivalent' (the other rule: cannot determine)", loc='left', fontsize=8)
axs[0].legend(fontsize=6)
axs[1].axhline(5, color=P.TEXT2, lw=0.8, ls='--'); axs[1].text(5, 5.3, 'SNR 5', fontsize=6, color=P.TEXT2)
axs[1].set_xlabel('time after impact (s)'); axs[1].set_ylabel('best-aperture SNR, 1-m telescope, 1-s V frame'); axs[1].set_ylim(0, 6)
axs[1].set_title('b) Plume signal-to-noise against the total background\n(solid: subtraction systematic 1e-3; dotted: 1e-2)', loc='left', fontsize=8)
labs, vals, lcross = [], [], []
for model in ['hollow Centaur', 'Centaur as 400 kg/m3', 'dense parts + hollow']:
    for params in ['sand', 'sand/fly ash', 'perlite/sand']:
        r_ = PL.lcross_check(model, params); lcross.append(r_)
        labs.append(f'{model}\n{params}'); vals.append(r_['M_illuminated_kg'])
y = np.arange(len(vals)); axs[2].barh(y, vals, color=[P.CAT[0]] * 3 + [P.CAT[1]] * 3 + [P.CAT[2]] * 3, height=0.6)
axs[2].axvspan(2240 - 400, 2240 + 400, color=P.CAT[7], alpha=0.15); axs[2].axvline(2240, color=P.CAT[7], lw=1.2)
axs[2].set_yticks(y); axs[2].set_yticklabels(labs, fontsize=5.5); axs[2].invert_yaxis(); axs[2].set_xlabel('illuminated ejecta mass at 20 s (kg)')
axs[2].set_title('c) LCROSS like-for-like check (observed 2240 +/- 400 kg,\nStrycker et al. 2013): a calibration of the bulk density, not a validation', loc='left', fontsize=8)
P.evidence_tag(fig, 'MODEL / HYPOTHETICAL SCENARIO - within the HH2011 scaling domain only')
fig.tight_layout(); P.savefig(fig, 'fig_plume_S2')
# ---------------------------------------------------------------- 5. public thresholds (S1 geometry at Istanbul)
c1 = json.load(open(f'{root}/outputs/scenarios/S1.json')); g = c1['sites']['IST']; ILLUM_PUB = c1['moon']['illum_frac']
rng = np.random.default_rng(1); n = 40000
fp = {k: I.sample_flash_parameters(rng, n, phys['v_km_s'], phys['mass_kg'], k, 'broad', 0.1) for k in ('wide', 'v-scaled')}
X = MC.kasten_young(g['moon_alt']); ext = float(D.extinction_mag('V', X, 100.0))
def eye_mag(f):
    eta = 10 ** f['log_eta']; E_bol = eta * f['E_k'] / I.W_eval(f['T0'])
    G1 = I.G_eval('V', f['T0'], (D.T_EYE / f['tau'])[:, None])[:, 0]
    Ein = E_bol / (4 * np.pi * (g['range_km'] * 1e3) ** 2) * G1 * 10 ** (-0.4 * ext)
    return -2.5 * np.log10(Ein / D.T_EYE / I.BANDS['V']['width'] / I.BANDS['V']['f0'])
def phone_mag(f):     # broad-band magnitude of the light in the first 1/30-s video frame (exposure starting at the onset)
    eta = 10 ** f['log_eta']; E_bol = eta * f['E_k'] / I.W_eval(f['T0'])
    G1 = I.G_eval('broad', f['T0'], ((1 / 30) / f['tau'])[:, None])[:, 0]
    Ein = E_bol / (4 * np.pi * (g['range_km'] * 1e3) ** 2) * G1 * 10 ** (-0.4 * float(D.extinction_mag('broad', X, 100.0)))
    return -2.5 * np.log10(Ein / (1 / 30) / I.BANDS['broad']['width'] / I.BANDS['broad']['f0'])
bkg_V = float(D.total_background_sb('V', ILLUM_PUB, g['dist_sunlit_arcmin'], g['sun_alt'], 3e-3, ext))
bkg_b = float(D.total_background_sb('broad', ILLUM_PUB, g['dist_sunlit_arcmin'], g['sun_alt'], 3e-3, 0.0))
fig, axs = plt.subplots(1, 2, figsize=(13, 3.8))
mv = {k: eye_mag(f) for k, f in fp.items()}; mb = {k: phone_mag(f) for k, f in fp.items()}
for k, (key, lab) in enumerate((('wide', 'wide eta prior'), ('v-scaled', 'v-scaled eta prior'))):
    axs[0].hist(mv[key], bins=70, range=(-2, 22), density=True, color=P.CAT[k], alpha=0.45, label=lab)
    axs[1].hist(mb[key], bins=70, range=(-2, 22), density=True, color=P.CAT[k], alpha=0.45, label=lab)
thr = {}
for k, (aid, lab) in enumerate((('none', 'naked eye'), ('binoculars', '7x50 binoculars'), ('telescope20cm', '20-cm telescope eyepiece'))):
    lo, md, hi = (float(D.visual_threshold_mag(bkg_V, aid, F)) for F in (24.0, np.sqrt(1.4 * 24), 1.4)); thr[aid] = (lo, md, hi)
    axs[0].axvspan(lo, hi, color=P.CAT[3 + k], alpha=0.12); axs[0].axvline(md, color=P.CAT[3 + k], lw=1.4, ls='--')
    axs[0].text(md, 0.97, lab, color=P.CAT[3 + k], fontsize=7, rotation=90, va='top', ha='right', transform=axs[0].get_xaxis_transform(),
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1.0))
for k, (mode, lab) in enumerate((('standalone', 'phone video, standalone'), ('afocal', 'phone video through 20 cm'))):
    lim = D.limiting_magnitude(D.phone_instrument(mode), bkg_b, 8 / D.phone_processing_penalty(mode))
    axs[1].axvline(lim, color=P.CAT[3 + k], lw=1.4, ls=':'); axs[1].text(lim, 0.97, lab, color=P.CAT[3 + k], fontsize=7, rotation=90, va='top', ha='right', transform=axs[1].get_xaxis_transform(),
                                                                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1.0))
for ax in axs:
    ax.invert_xaxis(); ax.set_ylabel('probability density'); ax.legend(fontsize=7, loc='upper left'); ax.set_ylim(0, ax.get_ylim()[1] * 1.35)
axs[0].set_xlabel('V magnitude of the light in the first 0.1 s (brighter to the right)')
axs[0].set_title(f'a) Visual-threshold model, S1 at Istanbul (Moon {g["moon_alt"]:.0f} deg, {ILLUM_PUB*100:.0f} % lit);\nbands: field factor 1.4-24; conditional on a clear, unobstructed, attentive view', loc='left', fontsize=8)
axs[1].set_xlabel('broad-band (0.40-0.70 um) magnitude in the first 1/30-s frame')
axs[1].set_title('b) Phone video limits (SNR 8 after the declared processing penalty), broad band:\nnot V magnitudes; not comparable with panel a without colour terms', loc='left', fontsize=8)
P.evidence_tag(fig, 'MODEL / HYPOTHETICAL SCENARIO - visual thresholds are exploratory, not calibrated for lunar flashes')
fig.tight_layout(); P.savefig(fig, 'fig_public_thresholds')
summ = {}
for key in fp:
    pk = I.peak_band_magnitude_fast('V', 10 ** fp[key]['log_eta'], fp[key]['E_k'], fp[key]['T0'], fp[key]['tau'], dist)
    summ[f'peakV_{key}'] = dict(p5=float(np.percentile(pk, 5)), p50=float(np.percentile(pk, 50)), p95=float(np.percentile(pk, 95)),
                                eye_V_p50=float(np.percentile(mv[key], 50)), rejected_fraction=float(fp[key]['rejected_fraction']),
                                **{f'p_brighter_than_{a}_median_threshold': float(np.mean(mv[key] < thr[a][1])) for a in thr})
summ['note'] = 'seeded prior-predictive sample (n=40000), ballistic case, broad T0 prior, radiative-energy cut 0.1; peak V unocculted at 380 000 km; eye magnitudes: first 0.1 s at the S1 Istanbul geometry, extincted'
summ['visual_thresholds_V'] = {a: dict(F24=v[0], F_geo=v[1], F1p4=v[2]) for a, v in thr.items()}
json.dump(summ, open(f'{root}/outputs/tables/peak_magnitude_distribution.json', 'w'), indent=1)
env_bal = I.crater_rim_diameter_envelope(m_bal, phys['v_km_s'], phys['angle_deg'])
json.dump(dict(lcross=lcross, crater_consistency=crater_check, ballistic_envelope_m={k: list(v) for k, v in env_bal.items()},
               note='LCROSS: like-for-like illuminated ejecta mass at 20 s (Strycker et al. 2013 observed 2240 +/- 400 kg); crater: '
                    'out-of-sample consistency of the rim-diameter envelopes with LROC-observed craters (no parameter fitted)'),
          open(f'{root}/outputs/tables/ejecta_checks.json', 'w'), indent=1)
print('done')
