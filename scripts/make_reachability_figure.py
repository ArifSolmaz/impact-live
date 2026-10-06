import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
m = np.load(f'{root}/outputs/reachability/reachability_maps.npz'); nside = int(m['nside']); fams = m['families']
fig, axs = plt.subplots(2, 3, figsize=(15, 6.6))
key = 'tol0.6_drift0.0'
for k, om in enumerate([0, 90, 180]):
    i = list(fams).index(om)
    P.lunar_map(axs[0, k], m[f'{key}_flash_tr'][i], nside, f'a{k+1}) node lon. {om} deg (2027-09-01), no plane change; flash geometry + Turkish site', cbar_label='opportunity-hours', vmin=0, features=False)
P.lunar_map(axs[1, 0], m[f'{key}_flash_tr'].mean(axis=0), nside, 'b) family average (24 node longitudes), no plane change', cbar_label='opportunity-hours', vmin=0, features=False)
P.lunar_map(axs[1, 1], m['tol2.5_drift0.0_flash_tr'].mean(axis=0), nside, 'c) family average with a 2.5-deg cross-track budget (~70 m/s)', cbar_label='opportunity-hours', vmin=0, features=False)
P.lunar_map(axs[1, 2], m[f'{key}_flash_cov3'].mean(axis=0), nside, 'd) family average: flash geometry with >= 3 configured sites anywhere', cbar_label='opportunity-hours', vmin=0, features=False)
fig.suptitle('Conditional reachability: hours in the impact domain when a pixel is on the ground track (polar 100-km orbit), dark, Earth-facing, phase 3-65 %, and observable', fontsize=10)
P.evidence_tag(fig, 'CONDITIONAL on declared orbit-plane families - the real AYAP-1 orbit plane is unpublished')
fig.tight_layout(); print(P.savefig(fig, 'fig_reachability'))
