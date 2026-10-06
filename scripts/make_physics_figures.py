"""Figures: flash brightness sensitivity surfaces (eta_vis x T0) per band; light curves and exposure averaging;
ejecta/plume heights and sunlit-mass; crater scaling validation; instrument limiting magnitudes vs exposure."""
import sys, os, numpy as np, yaml, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
from ayap1obs import impact as I, detect as D, plotting as P, montecarlo as MC
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); templates = MC.load_templates()
dist = 3.80e8
# 1. sensitivity surfaces: peak magnitude vs log eta and T0 for the ballistic case, 4 bands
phys = cfg['physics']['V_BAL']; E_k = I.kinetic_energy(np.mean(phys['mass_kg']), phys['v_km_s'])
etas = np.logspace(-6, -2.5, 36); T0s = np.linspace(1800, 3500, 35)
fig, axs = plt.subplots(1, 4, figsize=(14, 3.6))
for ax, band in zip(axs, ['Rc', 'Ic', 'J', 'Ks']):
    Z = np.zeros((len(T0s), len(etas)))
    for i, T0 in enumerate(T0s):
        for j, eta in enumerate(etas):
            Z[i, j] = I.FlashModel(E_k, eta, T0, 1200, 0.5, 0.5).peak_magnitude(band, dist)
    im = ax.imshow(Z, origin='lower', extent=(np.log10(etas[0]), np.log10(etas[-1]), T0s[0], T0s[-1]), aspect='auto', cmap=P.SEQ_BLUE.reversed(), vmin=4, vmax=18)
    cs = ax.contour(np.log10(etas), T0s, Z, levels=[6, 8, 10, 12, 14, 16], colors='white', linewidths=0.8); ax.clabel(cs, fmt='%d', fontsize=7)
    ax.set_title(f'{band} peak magnitude', loc='left'); ax.set_xlabel('log10 eta_vis (0.40-0.90 um)')
    ax.axvspan(np.log10(5e-4), np.log10(3e-3), color=P.CAT[1], alpha=0.15); ax.text(np.log10(6e-4), 1850, 'natural-flash\nrange (16-72 km/s)', fontsize=6, color=P.CAT[1])
axs[0].set_ylabel('initial temperature T0 (K)')
cb = fig.colorbar(im, ax=axs, fraction=0.02, pad=0.01); cb.set_label('peak Vega magnitude')
fig.suptitle(f'Flash brightness sensitivity, ballistic scenario (E_k = {E_k:.2e} J, 2.0 t at 1.68 km/s), cooling blackbody, tau = 0.5 s, isotropic emission, d = 380 000 km', fontsize=9)
P.evidence_tag(fig, 'MODEL / HYPOTHETICAL SCENARIO - luminous efficiency at < 2.4 km/s is uncalibrated')
P.savefig(fig, 'fig_flash_sensitivity')
# 2. light curves + exposure averaging
fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
t = np.linspace(0, 3, 600)
for k, (T0, tau, lab) in enumerate([(2500, 0.2, 'T0 2500 K, tau 0.2 s'), (2500, 0.8, 'T0 2500 K, tau 0.8 s'), (3500, 0.4, 'T0 3500 K, tau 0.4 s')]):
    fm = I.FlashModel(E_k, 1e-4, T0, 1200, tau, tau)
    for j, band in enumerate(['V', 'Ic', 'Ks']):
        axs[0].plot(t, fm.magnitude(t, band, dist), color=P.CAT[j], lw=1.6, ls=['-', '--', ':'][k], label=f'{band}' if k == 0 else None)
axs[0].set_ylim(18, 4); axs[0].set_xlabel('time since impact (s)'); axs[0].set_ylabel('apparent magnitude'); axs[0].set_title('a) Model light curves, eta_vis = 1e-4\n(solid: 2500 K, tau 0.2 s; dashed: 2500 K, 0.8 s; dotted: 3500 K, 0.4 s)', loc='left', fontsize=8); axs[0].legend()
exps = np.logspace(-2.5, 1, 40)
for j, (band, lab) in enumerate([('Rc', 'Rc'), ('Ic', 'Ic'), ('Ks', 'Ks')]):
    for k, tau in enumerate([0.2, 0.8]):
        fm = I.FlashModel(E_k, 1e-4, 2500, 1200, tau, tau)
        axs[1].plot(exps, [fm.exposure_averaged_magnitude(band, e, distance_m=dist) for e in exps], color=P.CAT[j], lw=1.6, ls=['-', '--'][k], label=f'{band}, tau {tau} s')
axs[1].set_xscale('log'); axs[1].set_ylim(18, 4); axs[1].set_xlabel('exposure time (s)'); axs[1].set_ylabel('exposure-averaged magnitude'); axs[1].set_title('b) Dilution of the flash in longer exposures', loc='left', fontsize=8); axs[1].legend(fontsize=7)
# 3. instrument limits vs exposure
illum = 0.35
for j, (tname, lab) in enumerate([('lunar_impact_system', 'NELIOTA-like 1.2 m (Rc)'), ('fast_camera_large', '2.4 m fast camera (Rc)'), ('tug_t100_qhy', 'TUG T100 + QHY174GPS (broad)'), ('amateur_class', 'amateur 0.35 m (broad)'), ('nir_large', '3.6 m NIR (Ks)'), ('dag_dirac', 'DAG 4 m DIRAC (Ks)')]):
    tp = templates[tname]; band = tp['bands'][0]
    lm = []
    for e in exps:
        inst = D.Instrument(tname, tp['aperture_m'], band, tp['pixel_scale_arcsec'], tuple(tp['fov_arcmin']), e, e * 1.1, throughput=tp['throughput'], obstruction=0.15, read_noise_e=tp['read_noise_e'], seeing_arcsec=tp['seeing_arcsec'])
        ext = float(D.extinction_mag(band, 1.2, 2500.0))
        lm.append(D.limiting_magnitude(inst, D.total_background_sb(band, illum, 8.0, -20, ext_mag=ext), 8.0) - ext)
    axs[2].plot(exps, lm, color=P.CAT[j], lw=1.6, label=lab)
axs[2].set_xscale('log'); axs[2].set_xlabel('exposure time (s)'); axs[2].set_ylabel('8-sigma limiting magnitude (steady source)'); axs[2].set_title('c) Above-atmosphere limits vs exposure (illum 0.35, 8\' from sunlit terrain,\ndark sky, airmass 1.2 at 2500 m)', loc='left', fontsize=8); axs[2].legend(fontsize=6.5)
axs[2].set_ylim(6, 20)
P.evidence_tag(fig, 'MODEL - instrument parameters from config/instruments.yaml; backgrounds are declared assumptions')
fig.tight_layout(); P.savefig(fig, 'fig_lightcurves_limits')
# 4. ejecta/plume + crater validation
fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
v = np.logspace(1, 3.3, 100)
for k, (key, col) in enumerate([('V_BAL', P.CAT[0]), ('V_MOD', P.CAT[1]), ('V_STR', P.CAT[2]), ('V_NSL', P.CAT[3])]):
    ph = cfg['physics'][key]
    axs[0].plot(v, I.ejecta_mass_above_speed(np.mean(ph['mass_kg']), ph['v_km_s'], v, angle_deg=ph['angle_deg']), color=col, lw=1.8, label=ph['label'])
    axs[0].plot(v, I.ejecta_mass_above_speed(np.mean(ph['mass_kg']), ph['v_km_s'], v, angle_deg=90.0), color=col, lw=1.0, ls='--')
axs[0].plot([], [], color=P.TEXT2, lw=1.8, label='solid: vertical velocity component (nominal)'); axs[0].plot([], [], color=P.TEXT2, lw=1.0, ls='--', label='dashed: full impact speed (upper bound)')
axs[0].set_xscale('log'); axs[0].set_yscale('log'); axs[0].set_xlabel('ejecta speed v (m/s)'); axs[0].set_ylabel('mass ejected faster than v (kg)'); axs[0].set_title('a) Ejecta mass-velocity (Housen & Holsapple 2011 scaling)', loc='left', fontsize=8); axs[0].legend(fontsize=5.5)
ax2 = axs[0].twiny(); ax2.set_xscale('log'); ax2.set_xlim(axs[0].get_xlim()); hts = [0.1, 1, 10, 100]; ax2.set_xticks([float(I.speed_for_height(h * 1e3)) for h in hts]); ax2.set_xticklabels([f'{h} km' for h in hts]); ax2.set_xlabel('max height (45 deg launch)')
th = np.linspace(0, 20, 200); axs[1].plot(th, I.G_MOON * 0 + 1737.4 * (1 / np.cos(np.radians(th)) - 1), color=P.CAT[0], lw=2)
axs[1].set_xlabel('angular distance beyond the terminator (deg)'); axs[1].set_ylabel('height of the shadow edge (km)'); axs[1].set_title('b) Height a plume must reach to be sunlit (spherical Moon)', loc='left', fontsize=8); axs[1].set_ylim(0, 110)
for h, lab in [(2.4, '3 deg'), (26.8, '10 deg')]:
    axs[1].axhline(h, color=P.TEXT2, lw=0.6, ls=':')
obs = [('GRAIL (130 kg, 1.7, ~2 deg)', 130, 1.7, 2, 5.0), ('LADEE (248 kg, 1.7, shallow)', 248, 1.7, 3, 2.5), ('Luna 25 (~1.75 t, ~1.7)', 1750, 1.7, 5, 10), ('CE5-T1 R/B (~4 t, 2.6)', 4000, 2.6, 30, 17), ('Falcon 9 (4-4.9 t, 2.43, 31 deg)', 4500, 2.43, 31, 18), ('Apollo S-IVB (14 t, 2.55)', 14000, 2.55, 70, 37.5)]
for k, (lab, m, vv, a, dobs) in enumerate(obs):
    lo, md, hi = I.crater_diameter_range(m, vv, a)
    axs[2].errorbar(dobs, md, yerr=[[md - lo], [hi - md]], fmt='o', color=P.CAT[k % 8], ms=5, capsize=3, label=lab)
axs[2].plot([1, 60], [1, 60], color=P.TEXT2, lw=0.8, ls='--'); axs[2].set_xscale('log'); axs[2].set_yscale('log'); axs[2].set_xlabel('observed crater diameter (m, LROC)'); axs[2].set_ylabel('pi-scaling prediction (m)'); axs[2].set_title('c) Crater scaling check against artificial impacts', loc='left', fontsize=8); axs[2].legend(fontsize=6)
lo, md, hi = I.crater_diameter_range(2000, 1.68, 3); axs[2].axhspan(lo, hi, color=P.CAT[0], alpha=0.12); axs[2].text(1.2, md, 'AYAP-1 ballistic\nscenario range', fontsize=6, color=P.CAT[0])
P.evidence_tag(fig, 'MODEL; panel c compares model to OBSERVED LROC crater sizes (research/precedents.csv)')
fig.tight_layout(); P.savefig(fig, 'fig_ejecta_crater')
# 5. human/phone thresholds vs predicted peak V distribution (illuminated fraction of scenario S1)
ILLUM_PUB = 0.39
fig, ax = plt.subplots(figsize=(7, 3.4))
m = np.linspace(-2, 20, 400)
for k, (aid, lab) in enumerate([('none', 'naked eye'), ('binoculars', '7x50 binoculars'), ('telescope20cm', '20-cm telescope eyepiece')]):
    ax.axvline(D.naked_eye_threshold_mag(0.3, ILLUM_PUB, aid), color=P.CAT[k], lw=1.5, ls='--'); ax.text(D.naked_eye_threshold_mag(0.3, ILLUM_PUB, aid) + 0.1, 0.9 - 0.1 * k, lab, color=P.CAT[k], fontsize=7)
for k, (mode, lab) in enumerate([('standalone', 'phone video, standalone'), ('afocal', 'phone video through 20 cm')]):
    lim = D.limiting_magnitude(D.phone_instrument(mode), D.total_background_sb('broad', ILLUM_PUB, 10, -20), 8 / D.phone_processing_penalty(mode))
    ax.axvline(lim, color=P.CAT[3 + k], lw=1.5, ls=':'); ax.text(lim + 0.1, 0.55 - 0.1 * k, lab, color=P.CAT[3 + k], fontsize=7)
# predicted peak V distribution (wide prior, ballistic)
rng = np.random.default_rng(1); n = 20000
log_eta = I.luminous_efficiency_prior(1.68, rng, n, 'slow-impact-wide'); T0 = rng.uniform(1800, 3500, n); tau = np.exp(rng.uniform(np.log(0.1), np.log(2), n))
mass = rng.uniform(1600, 2400, n); Ek = I.kinetic_energy(mass, 1.68)
# offset table for V peak
# peak offset depends on T0 and tau (the visible-band energy is normalised over the whole event)
T0g = np.linspace(1800, 3500, 18); taug = np.array([0.1, 0.2, 0.4, 0.8, 1.5, 2.0])
offs = np.array([[I.FlashModel(1, 1, t, 1200, ta, ta).peak_magnitude('V', dist) for ta in taug] for t in T0g])
from scipy.interpolate import RegularGridInterpolator
fo = RegularGridInterpolator((T0g, np.log(taug)), offs)
peak = -2.5 * np.log10(10 ** log_eta * Ek) + fo(np.stack([T0, np.log(tau)], axis=1))
log_eta2 = I.luminous_efficiency_prior(1.68, rng, n, 'v3-scaled'); peak2 = -2.5 * np.log10(10 ** log_eta2 * Ek) + fo(np.stack([T0, np.log(tau)], axis=1))
ax.hist(peak, bins=60, range=(-2, 20), density=True, color=P.CAT[0], alpha=0.5, label='predicted peak V, ballistic, wide eta prior (1e-6..3e-3)')
ax.hist(peak2, bins=60, range=(-2, 20), density=True, color=P.CAT[1], alpha=0.4, label='v^3-scaled eta prior')
ax.set_xlabel('peak V magnitude (brighter to the left)'); ax.set_ylabel('probability density'); ax.invert_xaxis(); ax.legend(fontsize=7, loc='upper left'); ax.set_title('Predicted flash brightness vs human and phone thresholds (0.3-s flash, 39 % illuminated Moon as in S1)', loc='left', fontsize=8)
P.evidence_tag(fig, 'MODEL / HYPOTHETICAL SCENARIO')
fig.tight_layout(); P.savefig(fig, 'fig_public_thresholds')
json.dump(dict(peakV_wide=dict(p5=float(np.percentile(peak, 5)), p50=float(np.percentile(peak, 50)), p95=float(np.percentile(peak, 95)), p_brighter_than_eyepiece=float(np.mean(peak < D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'telescope20cm'))), p_brighter_than_binoculars=float(np.mean(peak < D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'binoculars'))), p_brighter_than_naked_eye=float(np.mean(peak < D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'none')))),
               peakV_v3=dict(p5=float(np.percentile(peak2, 5)), p50=float(np.percentile(peak2, 50)), p95=float(np.percentile(peak2, 95)), p_brighter_than_eyepiece=float(np.mean(peak2 < D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'telescope20cm'))))),
          open(f'{root}/outputs/tables/peak_magnitude_distribution.json', 'w'), indent=1)
print('done')
