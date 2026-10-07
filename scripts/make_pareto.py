"""Strategy comparison (A: Türkiye-priority, B: global science, C: public participation) across scenarios and
sensitivity dimensions, presented as objective tables and Pareto fronts rather than a single score."""
import sys, os, json, glob, numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P, montecarlo as MC, weather as W
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); sites = {s['id']: s for s in yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']}
templates = MC.load_templates()
COST = {'lunar_impact_system': 1.0, 'midas_video': 0.5, 'fast_camera_large': 3.0, 'nir_large': 4.0, 'fast_camera_possible': 1.5, 'amateur_class': 0.3, 'tug_t100_qhy': 0.8, 'rtt150_fast': 1.5, 'dag_dirac': 3.0, 'dag_visitor_fast': 3.5}
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(f'{root}/outputs/scenarios/S*.json'))}
rows = []
for sid, c in cards.items():
    for strat in cfg['strategies']:
        st_cfg = cfg['strategies'][strat]
        # count stations and cost (available ones only)
        n_st = 0; cost = 0.0; clusters = set(); n_tr = 0
        for s in sites.values():
            if st_cfg['include_groups'] != 'all' and s['group'] not in st_cfg['include_groups']:
                continue
            tl = list(cfg['site_templates'].get(s['id'], []))
            if st_cfg.get('add_amateur_everywhere') and 'amateur_class' not in tl:
                tl.append('amateur_class')
            for t in tl:
                if st_cfg['include_templates'] != 'all' and t not in st_cfg['include_templates']:
                    continue
                if c['sites'][s['id']]['available']:
                    n_st += 1; cost += COST[t]; clusters.add(s['group']); n_tr += (s['group'] == 'turkiye')
        for prior in ['slow-impact-wide', 'v3-scaled']:
            m = c['mc'][f'{strat}|{prior}']
            rows.append(dict(scenario=sid, cls=c['cls'], strategy=strat, prior=prior, stations_available=n_st, turkish_stations=n_tr, geographic_groups=len(clusters), cost_units=cost,
                             p_any=m['p_any'], p_confirmed=m['p_confirmed'], p_two_indep=m['p_two_indep'], p_obvious=m['p_obvious_any'], p_live=m['p_live'], p_rapid=m['p_rapid_replay'],
                             p_turkish=m['p_turkish'], p_eyepiece=m['p_eyepiece_witness'], pop_public_bn=c['population']['2'] / 1e9, pop_turkiye_public_M=c['population']['turkiye_public'] / 1e6,
                             istanbul_hour=int(c['epoch_istanbul'][11:13]), turkish_evening=(18 <= int(c['epoch_istanbul'][11:13]) <= 23)))
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/strategy_objectives.csv', index=False)
w = df[df.prior == 'slow-impact-wide']
print(w.pivot_table(index='scenario', columns='strategy', values=['p_confirmed', 'p_live', 'cost_units']).round(2))
# Pareto fronts: objectives to maximise: p_confirmed, p_live, p_turkish; minimise cost.  Points: (scenario, strategy) pairs.
def pareto(points):
    keep = []
    for i, p in enumerate(points):
        dominated = any(all(q[k] >= p[k] for k in range(len(p))) and any(q[k] > p[k] for k in range(len(p))) for j, q in enumerate(points) if j != i)
        keep.append(not dominated)
    return np.array(keep)
fig, axs = plt.subplots(1, 3, figsize=(14, 4))
col = {'A_turkiye_priority': P.CAT[1], 'B_global_science': P.CAT[0], 'C_public_participation': P.CAT[2]}
mk = {'favourable': 'o', 'intermediate': 's', 'unfavourable': 'x'}
for ax, (xk, yk, xl, yl) in zip(axs, [('cost_units', 'p_confirmed', 'cost (telescope-time units, available stations)', 'P(>= 2 independent confirmations | terminal state)'),
                                      ('p_turkish', 'p_confirmed', 'P(detection by a Turkish station)', 'P(confirmed)'),
                                      ('pop_public_bn', 'p_live', 'urban population under practical direct-viewing sky (bn)', 'P(identifiable transient in a live feed)')]):
    pts = w[[xk, yk]].values.copy()
    if xk == 'cost_units':
        pts[:, 0] = -pts[:, 0]
    pf = pareto(list(map(tuple, pts)))
    labels = {}  # Pareto points at the same position share one label
    for (_, r), ok in zip(w.iterrows(), pf):
        ax.scatter(r[xk], r[yk], color=col[r.strategy], marker=mk[r.cls], s=55 if ok else 25, edgecolor='k' if ok else 'none', linewidth=0.8, alpha=0.95 if ok else 0.6)
        if ok:
            labels.setdefault((round(float(r[xk]), 6), round(float(r[yk]), 6)), {}).setdefault(r.scenario, []).append(r.strategy[0])
    for (x, y), by_s in labels.items():
        ax.text(x, y + 0.012, ', '.join(f"{s}-{'/'.join(v)}" for s, v in by_s.items()), fontsize=6)
    ax.set_xlabel(xl, fontsize=8); ax.set_ylabel(yl, fontsize=8)
from matplotlib.lines import Line2D
h = [Line2D([], [], color=col[k], marker='o', ls='', label=k) for k in col] + [Line2D([], [], color='k', marker=mk[k], ls='', label=k, mfc='none') for k in mk] + [Line2D([], [], color='k', marker='o', ls='', mfc='w', label='Pareto-efficient (large, outlined)')]
axs[2].legend(handles=h, fontsize=6.5, loc='upper left')
fig.suptitle('Strategy A/B/C objectives across hypothetical scenarios (wide luminous-efficiency prior; probabilities conditional on reaching the terminal state)', fontsize=9)
P.evidence_tag(fig, 'MODEL (Monte Carlo) on HYPOTHETICAL SCENARIOS')
fig.tight_layout(); P.savefig(fig, 'fig_pareto')
# sensitivity figure: P(confirmed, B) vs eta quartile for S1, S10; vs month (weather) via S1/S11/S4; vs FOV (DAG DIRAC coverage)
fig, axs = plt.subplots(1, 3, figsize=(13, 3.5))
for sid, lab, c_ in [('S1', 'S1 ballistic 1.68 km/s', P.CAT[0]), ('S10', 'S10 strong deceleration 0.8 km/s', P.CAT[1]), ('S2', 'S2 near terminator (scattered light)', P.CAT[2])]:
    if sid in cards:
        m = cards[sid]['mc']['B_global_science|slow-impact-wide']; e = m['eta_quartile_edges_log10']; x = [(e[i] + e[i + 1]) / 2 for i in range(4)]
        axs[0].plot(x, m['p_conf_by_eta_quartile'], marker='o', color=c_, label=lab)
axs[0].set_xlabel('log10 eta_vis (quartile centres of the wide prior)'); axs[0].set_ylabel('P(confirmed | eta quartile), strategy B'); axs[0].legend(fontsize=7); axs[0].set_ylim(0, 1)
labs = []; vals = []
for sid in ['S11', 'S1', 'S4', 'S3']:
    if sid in cards:
        c = cards[sid]; labs.append(f"{sid}\n{c['epoch_utc'][:7]}\n{c['n_sites_available']} sites"); vals.append([c['mc'][f'{s}|slow-impact-wide']['p_confirmed'] for s in cfg['strategies']])
vals = np.array(vals); xx = np.arange(len(labs))
for k, s in enumerate(cfg['strategies']):
    axs[1].bar(xx + (k - 1) * 0.26, vals[:, k], 0.25, color=col[s], label=s)
axs[1].set_xticks(xx); axs[1].set_xticklabels(labs, fontsize=7); axs[1].set_ylabel('P(confirmed)'); axs[1].legend(fontsize=7); axs[1].set_title('season / site availability (climatological weather included)', fontsize=8, loc='left')
# FOV coverage vs ellipse size
from ayap1obs.montecarlo import fov_coverage
sig = np.logspace(0, 2, 25)
for k, (fov, lab) in enumerate([((0.55, 0.55), "DAG DIRAC 33''"), ((4, 4), "4' fast camera"), ((8, 6), "8'x6' visitor CMOS"), ((17, 14.4), "NELIOTA 17'x14'")]):
    axs[2].plot(sig, [fov_coverage(fov, s, s / 4, 15.0) for s in sig], color=P.CAT[k], lw=1.8, label=lab)
axs[2].set_xscale('log'); axs[2].set_xlabel('along-track 1-sigma position uncertainty (km)'); axs[2].set_ylabel('probability the impact falls in the field'); axs[2].legend(fontsize=7); axs[2].set_title("field of view vs uncertainty ellipse (pointing error 15'' 1-sigma)", fontsize=8, loc='left')
P.evidence_tag(fig, 'MODEL sensitivity (Monte Carlo and analytic)')
fig.tight_layout(); P.savefig(fig, 'fig_sensitivity')
print('ok')
