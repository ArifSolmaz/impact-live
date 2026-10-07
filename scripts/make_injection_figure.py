"""Injection-recovery figure from outputs/tables/injection_recovery.json (SIMULATION; see run_injection_recovery.py)."""
import sys, os, json, textwrap, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
res = json.load(open(f'{root}/outputs/tables/injection_recovery.json'))
systems = [k for k in res if not k.startswith('_')]
fig, axs = plt.subplots(1, len(systems), figsize=(15, 3.9))
for ax, key in zip(axs, systems):
    r = res[key]; rows = r['rows']
    m = np.array([x['mag'] for x in rows])
    def series(frac_key, ci_key, fit, color, label, marker):
        f = np.array([x[frac_key] for x in rows]); lo = np.array([x[ci_key][0] for x in rows]); hi = np.array([x[ci_key][1] for x in rows])
        ax.errorbar(m, f, yerr=[np.clip(f - lo, 0, None), np.clip(hi - f, 0, None)], fmt=marker, ms=3.5, color=color, ecolor=color, elinewidth=0.8, capsize=0, label=label)
        mm = np.linspace(m.min(), m.max(), 300); ax.plot(mm, 1 / (1 + np.exp((mm - fit['m50']) / fit['width'])), color=color, lw=1.6)
        ax.axvspan(*fit['m50_ci95'], color=color, alpha=0.12, lw=0)
    series('frac_cam0', 'wilson_cam0', r['fits']['cam0'], P.CAT[0], f"one camera ({r['bands'][0]})", 'o')
    if 'dual' in r['fits']:
        series('frac_dual', 'wilson_dual', r['fits']['dual'], P.CAT[2], 'both cameras, same frame', 's')
    al = r['analytic_limits']
    ax.axvline(al['steady_snr8'], color=P.CAT[1], ls='--', lw=1.1, label='analytic steady limit, SNR 8')
    ax.axvline(al['steady_snr5'], color=P.CAT[1], ls=':', lw=1.1, label='analytic steady limit, SNR 5')
    fa = r['false_alarms']; c = fa['candidate_rate_per_box_frame'][0]; lo_c, hi_c = c['ci95_clip_bootstrap']
    txt = (f"blank: {fa['n_clips']} independent clips,\n{c['box_frames']} box-frames ({fa['box_px']} px boxes)\n"
           f"candidates >= 5 sigma: {c['rate']:.4f}/box-frame\n(95% clip bootstrap {lo_c:.4f}-{hi_c:.4f})\n"
           f"per injection window: {fa['expected_false_candidates_per_injection_window']:.2f}")
    if 'dual_coincidence_rate_per_box_frame' in fa and fa['dual_coincidence_rate_per_box_frame']:
        d = fa['dual_coincidence_rate_per_box_frame']
        txt += f"\ndual coincidences: {d['total']}\n(95% upper {d['ci95_clip_bootstrap'][1]:.4f}/box-frame)"
    ax.text(0.02, 0.40, txt, transform=ax.transAxes, fontsize=6.0, ha='left', va='top', color=P.TEXT2)
    f0 = r['fits']['cam0']
    ax.set_title(textwrap.fill(r['label'], 46) + f"\nm50 {f0['m50']:.2f} ({f0['m50_ci95'][0]:.2f}-{f0['m50_ci95'][1]:.2f})", fontsize=7, loc='left')
    ax.set_xlabel(f"injected band-peak magnitude ({r['bands'][0]})"); ax.set_ylim(-0.03, 1.06); ax.set_xlim(m.min() - 0.1, m.max() + 0.1)
axs[0].set_ylabel('recovered fraction'); axs[0].legend(fontsize=5.8, loc='lower left', bbox_to_anchor=(0.0, 0.42))
n = res[systems[0]]['ntrial']
fig.suptitle(f'Injection-recovery on synthetic lunar video (SIMULATION): {n} trials per point, Wilson 95% intervals, logistic fit with bootstrap 95% band on m50. '
             'One detector for injected and blank video (causal 25-frame median reference, sub-pixel registration, 5-sigma matched filter, 40-px boxes)', fontsize=8.2)
P.evidence_tag(fig, 'SIMULATION - synthetic frames with injected flashes; not observed footage and not a calibration of real systems')
fig.tight_layout(rect=(0, 0, 1, 0.92)); print(P.savefig(fig, 'fig_injection_recovery'))
