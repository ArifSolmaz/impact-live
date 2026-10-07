"""Strategy comparison (A: Türkiye-priority, B: global science, C: public participation), release 2.

* strategy_objectives.csv: per scenario, strategy and prior, the Monte Carlo outcome probabilities with 95 % Monte Carlo
  intervals (from the spread of the outer-draw means) and the 5-95 % range over the epistemic outer draws, and ILLUSTRATIVE relative
  resource weights (dimensionless constants per instrument template, summed over all stations a strategy recruits and,
  separately, over those available at the epoch; no hours, staffing, setup or money are modelled).
* strategy_nondominance.csv: joint nondominance WITHIN each scenario (strategies compared on the same simulated events)
  across four objectives: maximise P(two independent sites), P(live), P(Turkish detection); minimise the recruited
  weight. A strategy is dominated if another is at least as good in every objective and better in one, where 'better'
  in a probability requires the paired 95 % interval of the difference to exclude zero. Strategies are descriptive
  options, not optimisation results.
* fig_pareto: outcome probabilities by scenario and strategy with the outer 5-95 % ranges; fig_sensitivity: flash-efficiency,
  season, temperature-prior and field-of-view sensitivities."""
import sys, os, json, glob, numpy as np, pandas as pd, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from ayap1obs import plotting as P, montecarlo as MC
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml'))
WEIGHT = {'lunar_impact_system': 1.0, 'midas_video': 0.5, 'fast_camera_large': 3.0, 'nir_large': 4.0, 'fast_camera_possible': 1.5, 'amateur_class': 0.3,
          'tug_t100_qhy': 0.8, 'rtt150_fast': 1.5, 'dag_dirac': 3.0, 'dag_visitor_fast': 3.5}       # illustrative, elicited by the authors
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{root}/outputs/scenarios/S*.json')}
order = sorted(cards, key=lambda s: int(s[1:]))
STRATS = list(cfg['strategies']); OUTS = ['any', 'two_indep', 'dual_validated', 'confirmed', 'obvious_any', 'live', 'rapid', 'turkish']
rows = []
for sid in order:
    c = cards[sid]
    for strat in STRATS:
        keys = c['strategies'][strat]['stations']
        w_all = sum(WEIGHT[k.split(':')[1]] for k in keys)
        w_av = sum(WEIGHT[k.split(':')[1]] for k in keys if c['sites'][k.split(':')[0]]['available'])
        for prior_key, m in c['mc'].items():
            s = m['strategies'][strat]
            row = dict(scenario=sid, cls=c['cls'], strategy=strat, prior=prior_key, n_stations=len(keys), n_available=sum(c['sites'][k.split(':')[0]]['available'] for k in keys),
                       weight_recruited=w_all, weight_available=w_av, istanbul_hour=int(c['epoch_istanbul'][11:13]))
            for o in OUTS:
                row[f'p_{o}'] = s[o]['p']; row[f'p_{o}_lo'] = s[o]['ci95'][0]; row[f'p_{o}_hi'] = s[o]['ci95'][1]
                row[f'p_{o}_outer05'] = s[o]['outer_p05']; row[f'p_{o}_outer95'] = s[o]['outer_p95']
            rows.append(row)
df = pd.DataFrame(rows); df.to_csv(f'{root}/outputs/tables/strategy_objectives.csv', index=False)
# ---- joint nondominance within each scenario (wide|broad), significance from the paired differences
nd_rows = []
for sid in order:
    m = cards[sid]['mc']['wide|broad']; pr = m['paired']
    def better(o, a, b):
        """True if strategy a is significantly better than b in outcome o (paired 95 % CI excludes zero)."""
        k1, k2 = f'{o}:{a}-{b}', f'{o}:{b}-{a}'
        if k1 in pr: return pr[k1]['ci95'][0] > 0
        if k2 in pr: return pr[k2]['ci95'][1] < 0
        return False
    def not_worse(o, a, b):
        return not better(o, b, a)
    sub = df[(df.scenario == sid) & (df.prior == 'wide|broad')].set_index('strategy')
    for a in STRATS:
        dominated_by = []
        for b in STRATS:
            if a == b:
                continue
            objs_ok = all(not_worse(o, b, a) for o in ('two_indep', 'live', 'turkish')) and sub.loc[b, 'weight_recruited'] <= sub.loc[a, 'weight_recruited']
            strictly = any(better(o, b, a) for o in ('two_indep', 'live', 'turkish')) or sub.loc[b, 'weight_recruited'] < sub.loc[a, 'weight_recruited']
            if objs_ok and strictly:
                dominated_by.append(b)
        nd_rows.append(dict(scenario=sid, strategy=a, nondominated=not dominated_by, dominated_by=';'.join(dominated_by)))
nd = pd.DataFrame(nd_rows); nd.to_csv(f'{root}/outputs/tables/strategy_nondominance.csv', index=False)
print(nd.pivot_table(index='scenario', columns='strategy', values='nondominated', aggfunc='first').reindex(order).to_string())
# ---- figure: outcome probabilities by scenario
col = {'A_turkiye_priority': P.CAT[1], 'B_global_science': P.CAT[0], 'C_public_participation': P.CAT[2]}
w = df[df.prior == 'wide|broad']
fig, axs = plt.subplots(3, 1, figsize=(13, 9.5), sharex=True)
xx = np.arange(len(order))
for ax, (o, lab) in zip(axs, [('two_indep', 'P(detections at >= 2 sites > 100 km apart)'), ('live', 'P(obvious, SNR >= 30, at a streaming station)'), ('turkish', 'P(detection by a Turkish station)')]):
    for k, s in enumerate(STRATS):
        d = w[w.strategy == s].set_index('scenario').reindex(order)
        ax.bar(xx + (k - 1) * 0.27, d[f'p_{o}'], 0.26, color=col[s], label=s if o == 'two_indep' else None)
        ax.errorbar(xx + (k - 1) * 0.27, d[f'p_{o}'], yerr=[d[f'p_{o}'] - d[f'p_{o}_outer05'], d[f'p_{o}_outer95'] - d[f'p_{o}']], fmt='none', ecolor=P.TEXT2, elinewidth=0.8)
    ax.set_ylabel(lab, fontsize=8); ax.set_ylim(0, 1); ax.grid(axis='y', alpha=0.3)
axs[0].legend(fontsize=7, ncol=3, loc='upper right')
axs[2].set_xticks(xx); axs[2].set_xticklabels([f"{s}\n{cards[s]['cls']}" for s in order], fontsize=7)
hw = max(1.96 * cards[s_]['mc']['wide|broad']['strategies'][st_][o_]['mc_se'] for s_ in order for st_ in STRATS for o_ in ('two_indep', 'live', 'turkish')
         if cards[s_]['mc']['wide|broad']['strategies'][st_][o_]['mc_se'] is not None)
fig.suptitle('Strategy outcomes by hypothetical scenario (wide eta prior; conditional on the terminal state; error bars: 5-95 % range of the conditional\n'
             f'probability over the weather, readiness, calibration and background draws; 95 % Monte Carlo intervals of the bar heights are within +/-{np.ceil(hw * 100) / 100:.2f})', fontsize=8.5)
P.evidence_tag(fig, 'MODEL (Monte Carlo) on HYPOTHETICAL SCENARIOS - strategies are descriptive options, not optimised networks')
fig.tight_layout(rect=(0, 0, 1, 0.95)); P.savefig(fig, 'fig_pareto')
# ---- sensitivity figure
fig, axs = plt.subplots(1, 4, figsize=(15, 3.7))
bins = np.array(cards['S1']['mc']['wide|broad']['eta_bins']); xc = 0.5 * (bins[1:] + bins[:-1])
for sid, lab, c_ in [('S1', 'S1 ballistic 1.68 km/s', P.CAT[0]), ('S10', 'S10 strong deceleration 0.8 km/s', P.CAT[1]), ('S2', 'S2 near terminator', P.CAT[2])]:
    be = cards[sid]['mc']['wide|broad']['strategies']['B_global_science']['two_indep']['by_eta']
    axs[0].plot(xc, [np.nan if v is None else v for v in be], marker='o', color=c_, label=lab)
axs[0].set_xlabel('log10 eta_vis (bins of the wide prior)'); axs[0].set_ylabel('P(two sites | eta bin), strategy B'); axs[0].legend(fontsize=6.5); axs[0].set_ylim(0, 1)
axs[0].set_title('a) The flash efficiency dominates', loc='left', fontsize=8)
labs = []; vals = []
for sid in ['S11', 'S1', 'S4', 'S3']:
    c = cards[sid]; labs.append(f"{sid}\n{c['epoch_utc'][:7]}\n{c['n_sites_available']} sites"); vals.append([c['mc']['wide|broad']['strategies'][s]['two_indep']['p'] for s in STRATS])
vals = np.array(vals); x4 = np.arange(len(labs))
for k, s in enumerate(STRATS):
    axs[1].bar(x4 + (k - 1) * 0.26, vals[:, k], 0.25, color=col[s], label=s)
axs[1].set_xticks(x4); axs[1].set_xticklabels(labs, fontsize=6.5); axs[1].set_ylabel('P(two sites)'); axs[1].legend(fontsize=6, loc='upper left'); axs[1].set_ylim(0, 0.75); axs[1].set_title('b) Season and site availability (seasonal weather)', fontsize=8, loc='left')
for k, sid in enumerate(['S1', 'S11']):
    pk = [p for p in ('wide|broad', 'wide|cool', 'wide|narrow') if p in cards[sid]['mc']]
    for j, p in enumerate(pk):
        s = cards[sid]['mc'][p]['strategies']['B_global_science']['two_indep']
        axs[2].errorbar(k * 4 + j, s['p'], yerr=[[s['p'] - s['outer_p05']], [s['outer_p95'] - s['p']]], fmt='o', color=P.CAT[j], label=p.split('|')[1] + ' T0 prior' if k == 0 else None)
axs[2].set_xticks([1, 5]); axs[2].set_xticklabels(['S1', 'S11']); axs[2].set_ylim(0, 1); axs[2].set_ylabel('P(two sites), strategy B'); axs[2].legend(fontsize=6.5)
axs[2].set_title('c) Flash temperature prior (broad 1300-5800 K,\ncool 1300-2500 K, release-1 1800-3500 K)', fontsize=8, loc='left')
tpl = {}
for strat in ('B_global_science', 'C_public_participation'):
    for k, v in cards['S1']['mc']['wide|broad']['strategies'][strat]['station_p_fov'].items():
        if v is not None and cards['S1']['sites'][k.split(':')[0]]['candidate']:
            tpl.setdefault(k.split(':')[1], {})[k] = v
names = sorted(tpl, key=lambda t: np.mean(list(tpl[t].values())))
axs[3].barh(np.arange(len(names)), [np.mean(list(tpl[t].values())) for t in names], color=P.CAT[4])
axs[3].set_yticks(np.arange(len(names))); axs[3].set_yticklabels(names, fontsize=6.5); axs[3].set_xlim(0, 1.0)
axs[3].set_xlabel('P(impact inside the field), S1 (stations that can observe)'); axs[3].set_title("d) Field of view vs the shared impact-position\nuncertainty (12 x 2 km 1-sigma, pointing 15'')", fontsize=8, loc='left')
P.evidence_tag(fig, 'MODEL sensitivity (Monte Carlo) on HYPOTHETICAL SCENARIOS')
fig.tight_layout(); P.savefig(fig, 'fig_sensitivity')
print(w.pivot_table(index='scenario', columns='strategy', values=['p_two_indep', 'p_live', 'weight_recruited']).reindex(order).round(3).to_string())
