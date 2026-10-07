"""Plot the injection-recovery completeness curves from outputs/tables/injection_recovery.json (SIMULATION)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
results = json.load(open(f'{root}/outputs/tables/injection_recovery.json'))
# recompute the analytic limits with the current detection model (single source of truth for the systems:
# the definitions section of run_injection_recovery.py)
_src = open(f'{root}/scripts/run_injection_recovery.py').read()
_ns = {'__file__': f'{root}/scripts/run_injection_recovery.py', '__name__': 'defs'}
exec(compile(_src[:_src.index('systems = [')], 'run_injection_recovery_defs', 'exec'), _ns)
for name in results:
    inst, _ = _ns['make_system'](name)
    results[name]['analytic_8sigma_limit'] = float(_ns['D'].limiting_magnitude(inst, _ns['D'].total_background_sb(inst.band, _ns['ILLUM'], 8.0, -20), 8.0))
json.dump(results, open(f'{root}/outputs/tables/injection_recovery.json', 'w'), indent=1)
fig, axs = plt.subplots(1, len(results), figsize=(14, 3.6))
for ax, (name, r) in zip(axs, results.items()):
    m = np.array(r['mags']); c = np.array(r['completeness']); n = r.get('ntrial', 10)
    err = np.sqrt(np.clip(c * (1 - c), 0.02, None) / n)
    ax.fill_between(m, np.clip(c - err, 0, 1), np.clip(c + err, 0, 1), color=P.CAT[0], alpha=0.15, lw=0)
    ax.plot(m, c, color=P.CAT[0], lw=2, marker='o', ms=4, label='recovered fraction')
    ax.axvline(r['analytic_8sigma_limit'], color=P.CAT[1], ls='--', lw=1.2, label='analytic 8-sigma limit')
    ax.set_title(name, fontsize=7.5, loc='left'); ax.set_xlabel(f"injected peak magnitude ({r['band']})"); ax.set_ylim(-0.02, 1.08); ax.set_xlim(m.min(), m.max())
    ax.text(0.03, 0.30, f"single-camera false alarms\nper frame (5-sigma, whole field):\n{r['false_alarm_per_frame']:.2f}" + ("\n(dual-camera coincidence\nrequired for recovery)" if r.get('dual') else ''), transform=ax.transAxes, fontsize=6.2, ha='left', va='top')
axs[0].set_ylabel('recovery completeness'); axs[0].legend(fontsize=6.5, loc='center left')
fig.suptitle('Injection-recovery on synthetic lunar video (SIMULATION; illuminated fraction 0.35, flash durations 0.1-1 s, 5-sigma matched filter; shaded: binomial 1-sigma)', fontsize=9)
P.evidence_tag(fig, 'SIMULATION - synthetic frames with injected flashes; not observed footage')
fig.tight_layout(); print(P.savefig(fig, 'fig_injection_recovery'))
