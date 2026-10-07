"""Reachability figure (release 2.1): circular-overflight screening opportunities of hypothetical orbit planes.
a-c) mean number of screening opportunities per pixel over the domain, averaged over the 72 directed polar planes and 8 phases
(gates evaluated at the impact time of a 25-m/s de-orbit burn);
d) probability of at least one opportunity of each class within 30 days, as a function of the window start date
(uniform prior over planes and phases). Not a mission plan: burn targeting and operations are not modelled."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
z = np.load(f'{root}/outputs/reachability/reachability_maps_main.npz')
maps = z['maps']; nside = int(z['nside']); names = list(z['map_names']); deltas = list(z['deltas'])
fig = plt.figure(figsize=(14, 8.2))
axs = [fig.add_subplot(2, 2, k + 1) for k in range(4)]
def m(name, d):
    return maps[:, deltas.index(d), names.index(name)].mean(axis=0)
P.lunar_map(axs[0], m('flash_tr', 0.6), nside, 'a) Flash-favourable opportunities with a Turkish site,\ncross-track <= 0.6 deg (~17 m/s plane change)', cbar_label='opportunities in domain', vmin=0, features=False)
P.lunar_map(axs[1], m('flash_tr', 2.5), nside, 'b) Same, cross-track <= 2.5 deg\n(~71 m/s plane change)', cbar_label='opportunities in domain', vmin=0, features=False)
P.lunar_map(axs[2], m('plume_tr', 2.5), nside, 'c) Sunlit-plume geometry with a Turkish site, <= 2.5 deg\n(polar HEALPix pixels span up to 90 deg of longitude)', cbar_label='opportunities in domain', vmin=0, features=False)
wp = pd.read_csv(f'{root}/outputs/tables/opportunity_window_probability.csv')
w = wp[(wp.W_days == 30) & (wp.delta == 0.6)]
labels = {'A_turkiye_evening_public': 'A: Turkish evening, public phase', 'B_global_science': 'B: >= 3 sites, flash geometry', 'C_any_turkish': 'C: >= 1 Turkish site', 'P_plume_global': 'P: sunlit-plume geometry'}
ax = axs[3]
for k, (cls, lab) in enumerate(labels.items()):
    s = w[w.cls == cls]
    ax.plot(pd.to_datetime(s.start_utc), s.p, color=P.CAT[k], lw=1.6, label=lab)
ax.set_ylim(-0.02, 1.02); ax.set_ylabel('P(>= 1 opportunity within 30 days)'); ax.set_xlabel('window start (UTC)')
ax.set_title('d) 30-day terminal window, cross-track <= 0.6 deg,\nuniform over 72 directed planes x 8 phases', loc='left')
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False); ax.grid(alpha=0.3)
P.evidence_tag(fig, 'COMPUTED (DE421, hypothetical orbit planes) - circular-overflight screening opportunities, not a mission plan')
fig.tight_layout(); print(P.savefig(fig, 'fig_reachability'))
