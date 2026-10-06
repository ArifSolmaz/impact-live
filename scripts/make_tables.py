"""Generate LaTeX tables and the scenario-card appendix from outputs (run after run_scenarios.py and make_pareto.py)."""
import sys, os, json, glob, yaml, numpy as np, pandas as pd, datetime as dt
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
os.makedirs(os.path.join(root, 'paper', 'sections'), exist_ok=True)   # LaTeX tables/macros for the manuscript (manuscript itself not in the public repo)
sys.path.insert(0, root)
from ayap1obs import impact as I, detect as D, montecarlo as MC
templates = MC.load_templates()
cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml')); sites = {s['id']: s for s in yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']}
tl = yaml.safe_load(open(f'{root}/config/timeline.yaml'))
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(f'{root}/outputs/scenarios/S*.json'))}
order = [s['id'] for s in cfg['scenarios'] if s['id'] in cards]
def tex(s):
    return str(s).replace('+-', '$\\pm$').replace('~', '$\\sim$').replace('^', '\\^{}').replace('&', '\\&').replace('%', '\\%').replace('_', '\\_').replace('#', '\\#').replace('ü', '\\"u').replace('Ü', '\\"U').replace('ö', '\\"o').replace('ş', '\\c{s}').replace('ğ', '\\u{g}').replace('ı', '{\\i}').replace('İ', '\\.{I}').replace('ç', '\\c{c}')
# ---------------- scenario summary table (results section) ----------------
sm = pd.read_csv(f'{root}/outputs/tables/scenario_summary.csv')
lines = [r'\begin{landscape}', r'\begin{table}', r'\centering', r'\caption{Scenario summary (all HYPOTHETICAL test points; probabilities conditional on the spacecraft reaching the stated terminal state; wide luminous-efficiency prior unless marked $v^3$). $n$ = configured sites available (Moon $>20^\circ$, Sun $<-12^\circ$, point visible); pop = urban population under practical direct-viewing conditions (Moon $>15^\circ$, Sun $<-6^\circ$, point visible); $V_{\rm pk}$ = median predicted peak $V$ (10--90\%); A/B/C = strategies.}', r'\label{tab:scenarios}', r'\scriptsize',
         r'\setlength{\tabcolsep}{2.6pt}', r'\begin{tabular}{@{}llrrrrrrrrrrrrrrrp{2.9cm}@{}}', r'\toprule',
         r'Id & Class & $e$ & $i$ & illum & $n$ & TR & pop (bn) & $V_{\rm pk}$ & P$_A$(any) & P$_B$(any) & P$_C$(any) & P$_B$(any,$v^3$) & P$_B$(conf) & P$_B$(obv) & P$_C$(live) & P(eyepiece) & plume regime \\', r'\midrule']
for _, r in sm.iterrows():
    lines.append(f"{r.id} & {r.cls} & {r.emission:.0f} & {r.incidence:.0f} & {r.illum:.2f} & {r.n_sites} & {r.n_turkish} & {r.pop_public_bn:.2f} & {r.peakV_med:.1f} ({r.peakV_10_90}) & {r.pA_any:.2f} & {r.pB_any:.2f} & {r.pC_any:.2f} & {r.pB_any_v3:.2f} & {r.pB_conf:.2f} & {r.pB_obvious:.2f} & {r.pC_live:.2f} & {r.p_eyepiece:.3f} & {tex(r.plume_regime)} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}', r'\end{landscape}']
open(f'{root}/paper/sections/tab_scenarios.tex', 'w').write('\n'.join(lines))
# ---------------- strategy objectives table ----------------
so = pd.read_csv(f'{root}/outputs/tables/strategy_objectives.csv'); so = so[so.prior == 'slow-impact-wide']
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Strategy objectives for scenarios S1, S11, S3 and S4 (wide prior). Cost in telescope-time units (Section~\ref{sec:mc}); groups = distinct geographic/climate groups among available stations.}', r'\label{tab:strategies}', r'\footnotesize',
         r'\begin{tabular}{@{}llrrrrrrrrr@{}}', r'\toprule', r'Scen. & Strategy & stations & TR & groups & cost & P(any) & P(conf) & P(obvious) & P(live) & P(rapid) \\', r'\midrule']
for sid in ['S1', 'S11', 'S3', 'S4']:
    for _, r in so[so.scenario == sid].iterrows():
        lines.append(f"{sid} & {tex(r.strategy)} & {r.stations_available} & {r.turkish_stations} & {r.geographic_groups} & {r.cost_units:.1f} & {r.p_any:.2f} & {r.p_confirmed:.2f} & {r.p_obvious:.2f} & {r.p_live:.2f} & {r.p_rapid:.2f} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
open(f'{root}/paper/sections/tab_strategies.tex', 'w').write('\n'.join(lines))
# ---------------- opportunity probability table ----------------
po = pd.read_csv(f'{root}/outputs/tables/opportunity_probability_vs_duration.csv')
pv = po.pivot_table(index=['tol', 'cls'], columns='months', values='p_at_least_one')
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Probability, over a uniform prior on the unknown orbit-plane node longitude (24 values), that at least one reachable opportunity of each class occurs within the first $N$ months after the assumed start of orbital operations (2027-09-01); opportunities in the pre-start part of the screening domain are not counted. A = T\"urkiye evening (18--24 h Istanbul), central near side dark, public phase 0.12--0.5, waxing, $\geq$3 sites; B = central near side dark with $\geq$3 sites at any hour; C = any Turkish site; P = sunlit-plume geometry with $\geq$3 sites. $\delta$ = cross-track tolerance (0.6$^\circ$: no plane change; 2.5$^\circ$: $\sim$70 m/s).}', r'\label{tab:opportunity}', r'\footnotesize', r'\begin{tabular}{@{}llrrrrrr@{}}', r'\toprule', r'$\delta$ & class & 3 mo & 4 mo & 6 mo & 9 mo & 12 mo & 18 mo \\', r'\midrule']
for (tol, cls), r in pv.iterrows():
    lines.append(f"{tol} & {tex(cls)} & " + ' & '.join(f'{r[m]:.2f}' for m in [3, 4, 6, 9, 12, 18]) + r' \\')
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
open(f'{root}/paper/sections/tab_opportunity.tex', 'w').write('\n'.join(lines))
# ---------------- reachable opportunity-hours by region (results section) ----------------
rrs = pd.read_csv(f'{root}/outputs/tables/reachability_region_summary.csv')
REG = ['near side central', 'eastern limb region', 'western limb region', 'northern high latitude', 'southern high latitude', 'polar', 'far side']
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Family-averaged reachable opportunity-hours per pixel by region over the domain (mean over pixels in the region). flash\_cov3: flash geometry and $\ge3$ sites; flash\_tr: flash geometry and $\ge1$ Turkish site; plume\_tr: sunlit-plume geometry and $\ge1$ Turkish site.}', r'\label{tab:reach_region}', r'\footnotesize', r'\begin{tabular}{@{}lrrrrrr@{}}', r'\toprule',
         r' & \multicolumn{3}{c}{$\delta=0.6^\circ$ (no plane change)} & \multicolumn{3}{c}{$\delta=2.5^\circ$ ($\sim$70 m/s)} \\', r'Region & flash\_cov3 & flash\_tr & plume\_tr & flash\_cov3 & flash\_tr & plume\_tr \\', r'\midrule']
for reg in REG:
    vals = [float(rrs[(rrs.family_set == fs) & (rrs.quantity == q) & (rrs.region == reg)].mean_hours.values[0]) for fs in ['tol0.6_drift0.0', 'tol2.5_drift0.0'] for q in ['flash_cov3', 'flash_tr', 'plume_tr']]
    lines.append(f'{reg} & ' + ' & '.join(f'{v:.1f}' for v in vals) + r' \\')
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
open(f'{root}/paper/sections/tab_reach.tex', 'w').write('\n'.join(lines))
# ---------------- timeline table ----------------
tf = pd.read_csv(f'{root}/outputs/tables/timeline_families.csv'); tf = tf[tf.phase_case == 'nominal']
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Launch-to-impact timeline families (nominal phase durations; SCENARIO ASSUMPTIONS). Windows = T\"urkiye evening observing windows (illum 0.12--0.5, Moon $>25^\circ$ at TUG) within $\pm$15 days of the impact date; LRO = impact date inside a derived LRO low-Sun window.}', r'\label{tab:timeline}', r'\footnotesize', r'\begin{tabular}{@{}llllrlll@{}}', r'\toprule', r'Launch & date & LOI & science start & months & impact date & windows ($\pm$15 d) & LRO \\', r'\midrule']
for _, r in tf.iterrows():
    lines.append(f"{r.launch} & {r.launch_date} & {r.loi_date} & {r.science_start} & {r.science_months} & {r.impact_date} & {tex(r.n_evening_windows_pm15d)} & {'yes' if r.in_LRO_low_sun_window else 'no'} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
open(f'{root}/paper/sections/tab_timeline.tex', 'w').write('\n'.join(lines))
# ---------------- scenario cards appendix ----------------
scn_cfg = {s['id']: s for s in cfg['scenarios']}
def flash_mags(E_k, eta, dist_m, T0=2500.0, tau=0.5):
    fm = I.FlashModel(E_k, eta, T0, 1200.0, tau, tau)
    return {b: fm.peak_magnitude(b, dist_m) for b in ['V', 'Rc', 'Ic', 'Ks']}
L = [r'\section{Scenario cards}', r'\label{app:scenarios}',
     r"All coordinates are hypothetical test points chosen by the screening (latitude north-positive, longitude east-positive, ME frame); none is an official AYAP-1 target. Impact times are the screening epochs; the actual minute on a pass is set by the orbital phase. Reachability is conditional on the orbit plane (Section~\ref{sec:reach}). Probabilities are conditional on reaching the stated terminal state; ``wide'' denotes the log-uniform $\eta_{\rm vis}$ prior and ``$v^3$'' the velocity-scaled prior.", '']
for sid in order:
    c = cards[sid]; sc = scn_cfg[sid]
    mB = c['mc']['B_global_science|slow-impact-wide']; mA = c['mc']['A_turkiye_priority|slow-impact-wide']; mC = c['mc']['C_public_participation|slow-impact-wide']; mBv = c['mc']['B_global_science|v3-scaled']
    avail = c['sites_available']; tr = c['turkish_sites_available']
    dist_m = c['moon']['distance_km'] * 1e3; Ek = c['energy']['E_k_J']
    f0, f1, f2 = (flash_mags(Ek, e, dist_m) for e in (1e-5, 1e-4, 1e-3))
    lro = c['orbiters']['lro_low_sun_next']; pl = c['plume']
    if pl.get('plume_V_mag_10um') is not None:
        plume_txt = (f"; ejecta faster than {pl['ejecta_speed_needed_m_s']:.0f} m/s reach sunlight: {pl['ejecta_mass_sunlit_kg']:.0f} kg (nominal, vertical velocity component) to {pl['ejecta_mass_sunlit_upper_kg']:.0f} kg (upper bound, full speed); "
                     f"integrated $V$ {pl['plume_V_mag_10um']:.1f} to {pl['plume_V_mag_10um_upper']:.1f} (10 $\\mu$m grains); surface brightness {pl['plume_sb_10um_mag_arcsec2']:.1f} to {pl['plume_sb_10um_upper_mag_arcsec2']:.1f} against a background of {pl['background_sb_V']:.1f} mag/arcsec$^2$ (contrast {pl['contrast_10um']:.2f} to {pl['contrast_10um_upper']:.2f})")
    else:
        plume_txt = f"; only Earthshine illuminates the cloud, integrated $V\\approx${pl.get('earthshine_lit_plume_V_mag', float('nan')):.0f} (undetectable)"
    L += [r'\subsection*{' + tex(f"{sid}: {sc['name']}") + '}',
          r'\begin{tabularx}{\textwidth}{@{}p{3.6cm}X@{}}', r'\toprule',
          f"Class & {c['cls']} \\\\",
          f"Coordinates (hypothetical) & lat {c['lat']:+.1f}$^\\circ$, lon {c['lon']:+.1f}$^\\circ$E; region: {tex(c['region'])}; rationale: {tex(sc['rationale'])} \\\\",
          f"Impact epoch & {c['epoch_utc']} UTC = {tex(c['epoch_istanbul'])}; light time {c['moon']['light_time_s']:.2f} s; Earth--Moon distance {c['moon']['distance_km']:.0f} km; Moon age {c['moon']['moon_age_days']:.1f} d \\\\",
          f"Linked mission assumptions & impact within an orbital mission that started by {tl['launch_families'][0]['date'][:7]}--{tl['launch_families'][2]['date'][:7]} (families L1--L3), i.e.\\ a 3--12 month science phase; physics {tex(c['physics']['label'])} ({tex(c['physics']['status'])}) \\\\",
          f"Reachability & conditional: {tex(c['reachability']['condition'])} {tex(c['reachability'].get('polar_note',''))} \\\\",
          f"Impact conditions & $E_k$ = {Ek/1e9:.2f} GJ ({c['energy']['tnt_equiv_kg']:.0f} kg TNT), mass {c['energy']['mass_mean_kg']:.0f} kg (range {c['physics']['mass_kg'][0]}--{c['physics']['mass_kg'][1]}), $v$ = {c['energy']['v_km_s']} km/s at {c['energy']['angle_deg']}$^\\circ$; emission (geocentric) {c['geometry']['emission_geocentric']:.1f}$^\\circ$, solar incidence {c['geometry']['incidence']:.1f}$^\\circ$ ({'sunlit' if c['geometry']['sunlit'] else 'dark'}); illuminated fraction {c['moon']['illum_frac']:.2f}, sub-Earth point ({c['moon']['subearth_lon']:+.1f}, {c['moon']['subearth_lat']:+.1f}); shadow height {c['geometry']['shadow_height_km']:.1f} km \\\\",
          f"Terrain (synthetic DEM statistics) & P(Earth above local horizon) = {c['terrain']['p_visible_statistical']:.2f} (roughness factor {c['terrain']['roughness_factor']}); plume clearance {c['terrain']['plume_clearance_km']:.1f} km \\\\",
          f"Visible facilities & {len(avail)} configured sites available ({len(tr)} Turkish): {tex(', '.join(avail)) if avail else 'none'} \\\\",
          f"Predicted flash (peak $V/R_c/I_c/K_s$) & $\\eta_{{\\rm vis}}=10^{{-5}}$: {f0['V']:.1f}/{f0['Rc']:.1f}/{f0['Ic']:.1f}/{f0['Ks']:.1f}; $10^{{-4}}$: {f1['V']:.1f}/{f1['Rc']:.1f}/{f1['Ic']:.1f}/{f1['Ks']:.1f}; $10^{{-3}}$: {f2['V']:.1f}/{f2['Rc']:.1f}/{f2['Ic']:.1f}/{f2['Ks']:.1f} ($T_0$ = 2500 K, $\\tau$ = 0.5 s); Monte Carlo median peak $V$ {mB['peakV_median']:.1f} (10--90\\%: {mB['peakV_p10']:.1f}--{mB['peakV_p90']:.1f}) \\\\",
          f"Instrument requirements & fast ($\\le$50 ms) visible or $\\ge$1-s near-infrared imaging with GPS timing; field covering the ellipse ($\\sigma$ along/cross {c['physics']['sigma_along_km']}/{c['physics']['sigma_cross_km']} km = {206265*c['physics']['sigma_along_km']/c['moon']['distance_km']:.1f}$''$/{206265*c['physics']['sigma_cross_km']/c['moon']['distance_km']:.1f}$''$); linear $\\ge$16-bit data; non-sidereal tracking; timing uncertainty $\\pm${c['physics']['sigma_t_min']} min requires continuous recording \\\\",
          f"Network probabilities (wide prior) & P(any): A {mA['p_any']:.2f}, B {mB['p_any']:.2f}, C {mC['p_any']:.2f}; P(two independent confirmations): A {mA['p_two_indep']:.2f}, B {mB['p_two_indep']:.2f}, C {mC['p_two_indep']:.2f}; P(obvious in raw frames, B) {mB['p_obvious_any']:.2f}; P(live identifiable, C) {mC['p_live']:.2f}; P(rapid replay, B) {mB['p_rapid_replay']:.2f}; P(Turkish detection, A) {mA['p_turkish']:.2f}; $v^3$ prior: P(any, B) {mBv['p_any']:.2f}, P(conf, B) {mBv['p_confirmed']:.2f} \\\\",
          f"Public viewing assessment & urban population with practical direct view {c['population']['2']/1e9:.2f} bn (T\\\"urkiye {c['population']['turkiye_public']/1e6:.0f} M); P(naked eye) {mB['p_naked_eye_witness']:.4f}, P(binoculars) {mB['p_binocular_witness']:.4f}, P(20-cm eyepiece) {mB['p_eyepiece_witness']:.3f}; phone standalone limit {c['public']['phone_standalone_limit']:.1f} mag, phone afocal on 20 cm {c['public']['phone_afocal20cm_limit']:.1f} mag (analytic) \\\\",
          f"Plume & {tex(pl['regime'])}; shadow height {pl['shadow_height_km']:.1f} km" + plume_txt + " \\\\",
          f"Crater and orbital follow-up & rim diameter {c['crater']['diameter_m'][0]:.0f}--{c['crater']['diameter_m'][2]:.0f} m (median {c['crater']['diameter_m'][1]:.0f} m), {c['crater']['lroc_nac_pixels']:.0f} NAC pixels, {c['crater']['angular_size_arcsec']:.4f}$''$ from Earth; LRO first image 0.4--27 d after impact (well-located precedents) with P(LRO operating) = {c['orbiters']['p_lro_operational']}; " + (f"impact falls inside the derived low-Sun window {lro[1]} to {lro[2]}" if (lro and lro[0] == 0) else (f"next derived low-Sun window starts in {lro[0]} d ({lro[1]} to {lro[2]})" if lro else "next low-Sun window beyond the derived table")) + f"; Danuri P = {c['orbiters']['p_danuri']}; public release 12--34 d after impact (precedents) \\\\",
          r'\bottomrule', r'\end{tabularx}', '']
open(f'{root}/paper/sections/B_scenarios.tex', 'w').write('\n'.join(L))

# ---------------- Table 8: model flash magnitudes ----------------
Ek_bal = I.kinetic_energy(2000.0, 1.68); d38 = 3.8e8
lines = [r'\begin{table}[t]', r'\centering', r'\caption{Model flash magnitudes for the ballistic scenario at 380\,000 km ($T_0=2500$ K, $\tau=0.5$ s, isotropic; generated by \texttt{make\_tables.py}). ``33 ms'' and ``2 s'' are exposure-averaged magnitudes for those exposures starting at impact; ``fluence'' is the time-integrated band fluence expressed as the magnitude of a source of the same fluence lasting 1 s.}', r'\label{tab:magtable}', r'\footnotesize', r'\setlength{\tabcolsep}{4pt}', r'\begin{tabular}{@{}lrrrrrrrrrrr@{}}', r'\toprule',
         r'$\eta_{\rm vis}$ & $V$ peak & $R_c$ peak & $R_c$ 33 ms & $R_c$ fluence & $I_c$ peak & $I_c$ 33 ms & $J$ peak & $H$ peak & $K_s$ peak & $K_s$ 2 s & $K_s$ fluence \\', r'\midrule']
for e, lab in [(1e-3, '$10^{-3}$'), (1e-4, '$10^{-4}$'), (1e-5, '$10^{-5}$'), (1e-6, '$10^{-6}$')]:
    fm = I.FlashModel(Ek_bal, e, 2500, 1200, 0.5, 0.5)
    vals = [fm.peak_magnitude('V', d38), fm.peak_magnitude('Rc', d38), fm.exposure_averaged_magnitude('Rc', 0.033, distance_m=d38), fm.fluence('Rc', d38)[1], fm.peak_magnitude('Ic', d38), fm.exposure_averaged_magnitude('Ic', 0.033, distance_m=d38), fm.peak_magnitude('J', d38), fm.peak_magnitude('H', d38), fm.peak_magnitude('Ks', d38), fm.exposure_averaged_magnitude('Ks', 2.0, distance_m=d38), fm.fluence('Ks', d38)[1]]
    lines.append(lab + ' & ' + ' & '.join(f'{v:.1f}' for v in vals) + r' \\')
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
open(f'{root}/paper/sections/tab_magtable.tex', 'w').write('\n'.join(lines))

# ---------------- numbers.tex: every volatile number quoted in the text ----------------
W = {'S1': 'One', 'S2': 'Two', 'S3': 'Three', 'S4': 'Four', 'S5': 'Five', 'S6': 'Six', 'S7': 'Seven', 'S8': 'Eight', 'S9': 'Nine', 'S10': 'Ten', 'S11': 'Eleven'}
NUM = ['% Auto-generated by scripts/make_tables.py from outputs/ -- do not edit by hand.']
def nm(name, val, fmt='{:.2f}'):
    NUM.append(f'\\newcommand{{\\N{name}}}{{{val if isinstance(val, str) else fmt.format(val)}}}')
metrics = {'any': 'p_any', 'two': 'p_two_indep', 'conf': 'p_confirmed', 'obv': 'p_obvious_any', 'live': 'p_live', 'rapid': 'p_rapid_replay', 'tr': 'p_turkish'}
SL = {'A_turkiye_priority': 'A', 'B_global_science': 'B', 'C_public_participation': 'C'}
for sid in order:
    c = cards[sid]; w = W[sid]
    for strat, S in SL.items():
        for prior, suf in [('slow-impact-wide', ''), ('v3-scaled', 'V')]:
            m = c['mc'][f'{strat}|{prior}']
            for k, key in metrics.items():
                nm(f'{k}{S}{w}{suf}', m[key])
    mB = c['mc']['B_global_science|slow-impact-wide']
    nm(f'eye{w}', mB['p_eyepiece_witness']); nm(f'bin{w}', mB['p_binocular_witness'], '{:.3f}'); nm(f'naked{w}', mB['p_naked_eye_witness'], '{:.3f}')
    nm(f'nsites{w}', int(c['n_sites_available']), '{:d}'); nm(f'ntr{w}', len(c['turkish_sites_available']), '{:d}')
    nm(f'pop{w}', c['population']['2'] / 1e9); nm(f'pkmed{w}', mB['peakV_median'], '{:.1f}'); nm(f'pklo{w}', mB['peakV_p10'], '{:.1f}'); nm(f'pkhi{w}', mB['peakV_p90'], '{:.1f}')
    nm(f'Ek{w}', c['energy']['E_k_J'] / 1e9); nm(f'illum{w}', c['moon']['illum_frac']); nm(f'age{w}', c['moon']['moon_age_days'], '{:.1f}')
c1 = cards['S1']; mB1 = c1['mc']['B_global_science|slow-impact-wide']; mC1 = c1['mc']['C_public_participation|slow-impact-wide']
nm('altTUGOne', c1['sites']['TUG']['moon_alt'], '{:.0f}'); nm('altDAGOne', c1['sites']['DAG']['moon_alt'], '{:.0f}')
nm('diracCovOne', mB1['station_fov_cov']['DAG:dag_dirac']); nm('diracPOne', mB1['station_p_det']['DAG:dag_dirac'])
FR = {'SAAO:fast_camera_large': 'the Sutherland fast camera', 'KRY:lunar_impact_system': 'NELIOTA', 'KOT:fast_camera_possible': 'a visitor camera at Kottamia', 'TUG:rtt150_fast': 'a fast camera on RTT150',
      'MAID:fast_camera_possible': 'a visitor camera at Maidanak', 'TUG:tug_t100_qhy': 'TUG T100 with its GPS camera', 'SAO:fast_camera_large': 'the Zelenchukskaya station', 'DAG:dag_visitor_fast': 'a visitor camera on DAG',
      'BYU:fast_camera_possible': 'a visitor camera at Byurakan', 'SEV:midas_video': 'MIDAS', 'ORM:fast_camera_large': 'a La Palma fast camera'}
top = [(k, v) for k, v in sorted(mB1['station_p_det'].items(), key=lambda x: -x[1]) if k != 'DAG:dag_dirac' and v > 0][:8]
nm('stationsOne', ', '.join(f"{FR.get(k, k.replace('_', ' '))} ({v:.2f})" for k, v in top[:-1]) + f", and {FR.get(top[-1][0], top[-1][0])} ({top[-1][1]:.2f})")
q = mB1['eta_quartile_edges_log10']; pa = mB1['p_any_by_eta_quartile']; pc = mB1['p_conf_by_eta_quartile']
nm('qOneEdge', q[1], '{:.1f}'); nm('qThreeEdge', q[2], '{:.1f}'); nm('qanyOne', pa[0]); nm('qanyTwo', pa[1]); nm('qanyHi', f'{min(pa[2:]):.2f}--{max(pa[2:]):.2f}'); nm('qconfLo', pc[0]); nm('qconfHi', max(pc[2:]))
for lab, m in [('B', mB1), ('C', mC1)]:
    p = np.array(list(m['station_p_det'].values())); naive = 1 - np.prod(1 - p)
    nm(f'naive{lab}', naive); nm(f'over{lab}', naive - m['p_any'])
# strategy statistics
so = pd.read_csv(f'{root}/outputs/tables/strategy_objectives.csv'); so = so[so.prior == 'slow-impact-wide']
cr = []
for sid in order:
    b = so[(so.scenario == sid) & (so.strategy == 'B_global_science')]; cc = so[(so.scenario == sid) & (so.strategy == 'C_public_participation')]
    if len(b) and len(cc) and cc.cost_units.values[0] > 0:
        cr.append(b.cost_units.values[0] / cc.cost_units.values[0])
nm('costRatio', f'{min(cr):.1f}--{max(cr):.1f}')
a2 = so[so.strategy == 'A_turkiye_priority'].set_index('scenario').p_two_indep
nm('twoAmax', a2.max()); nm('twoAmaxScen', str(a2.idxmax()))
cge = [sid for sid in order if so[(so.scenario == sid) & (so.strategy == 'C_public_participation')].p_confirmed.values[0] >= so[(so.scenario == sid) & (so.strategy == 'B_global_science')].p_confirmed.values[0] and so[(so.scenario == sid) & (so.strategy == 'B_global_science')].p_confirmed.values[0] > 0]
nm('CgeB', (', '.join(cge[:-1]) + ' and ' + cge[-1]) if len(cge) > 1 else (cge[0] if cge else 'no scenario'))
nm('CgeBNote', ('equal or higher in ' + ((', '.join(cge[:-1]) + ' and ' + cge[-1]) if len(cge) > 1 else cge[0])) if cge else 'lower in every scenario')
dconf = [so[(so.scenario == sid) & (so.strategy == 'B_global_science')].p_confirmed.values[0] - so[(so.scenario == sid) & (so.strategy == 'B_global_science')].p_two_indep.values[0] for sid in order if sid != 'S9']
nm('confMinusTwo', f'{min(dconf):.2f}--{max(dconf):.2f}')
# instrument limits (same conditions as Fig. 6c: illum 0.35, 8 arcmin from sunlit terrain, Sun -20 deg, obstruction 0.15)
LIMN = {'lunar_impact_system': 'Nel', 'fast_camera_large': 'Fast', 'tug_t100_qhy': 'Thund', 'amateur_class': 'Am', 'nir_large': 'Nir', 'dag_dirac': 'Dirac', 'rtt150_fast': 'Rtt', 'dag_visitor_fast': 'Dagv', 'fast_camera_possible': 'Fposs', 'midas_video': 'Midas'}
for tname, tag in LIMN.items():
    tp = templates[tname]; band = tp['bands'][0]
    inst = D.Instrument(tname, tp['aperture_m'], band, tp['pixel_scale_arcsec'], tuple(tp['fov_arcmin']), tp['exposure_s'], tp['frame_time_s'], throughput=tp['throughput'], obstruction=0.15, read_noise_e=tp['read_noise_e'], seeing_arcsec=tp['seeing_arcsec'])
    ext = float(D.extinction_mag(band, 1.2, 2500.0))
    nm(f'lim{tag}', D.limiting_magnitude(inst, D.total_background_sb(band, 0.35, 8.0, -20, ext_mag=ext), 8.0) - ext, '{:.1f}')
    nm(f'sat{tag}', D.bright_limit(inst, float(tp.get('saturation_e', 6e4))) - ext, '{:.1f}')
# flash-model numbers
for T0, tag in [(3500, 'Hot'), (2500, 'Mid'), (1800, 'Cool')]:
    fm = I.FlashModel(Ek_bal, 1e-4, T0, 1200, 0.5, 0.5); nm(f'kv{tag}', fm.peak_magnitude('V', d38) - fm.peak_magnitude('Ks', d38), '{:.1f}')
fm = I.FlashModel(Ek_bal, 1e-4, 2500, 1200, 0.5, 0.5)
for b in ['V', 'Rc', 'Ic', 'J', 'H', 'Ks']:
    nm(f'pk{b}', fm.peak_magnitude(b, d38), '{:.1f}')
nm('ksSix', I.FlashModel(Ek_bal, 1e-6, 2500, 1200, 0.5, 0.5).peak_magnitude('Ks', d38), '{:.1f}')
nm('dilTen', fm.exposure_averaged_magnitude('Ks', 10.0, distance_m=d38) - fm.peak_magnitude('Ks', d38), '{:.1f}')
fs = I.FlashModel(I.kinetic_energy(285, 2.0), 1e-4, 2500, 1200, 0.5, 0.5)
nm('smartAvg', fs.exposure_averaged_magnitude('Ks', 10.0, distance_m=d38), '{:.1f}'); nm('smartPk', fs.peak_magnitude('Ks', d38), '{:.1f}')
pk = json.load(open(f'{root}/outputs/tables/peak_magnitude_distribution.json'))
nm('pkWideMed', pk['peakV_wide']['p50'], '{:.1f}'); nm('pkWideLo', pk['peakV_wide']['p5'], '{:.1f}'); nm('pkWideHi', pk['peakV_wide']['p95'], '{:.1f}')
nm('pkVMed', pk['peakV_v3']['p50'], '{:.1f}'); nm('pkVLo', pk['peakV_v3']['p5'], '{:.1f}'); nm('pkVHi', pk['peakV_v3']['p95'], '{:.1f}')
nm('fracEyeWide', 100 * pk['peakV_wide']['p_brighter_than_eyepiece'], '{:.0f}'); nm('fracBinWide', 100 * pk['peakV_wide']['p_brighter_than_binoculars'], '{:.1f}'); nm('fracNakedWide', 100 * pk['peakV_wide']['p_brighter_than_naked_eye'], '{:.0f}')
nm('fracEyeV', 100 * pk['peakV_v3']['p_brighter_than_eyepiece'], '{:.0f}')
# public thresholds (S1)
pb = c1['public']
nm('thrNaked', pb['naked_eye_threshold'], '{:.1f}'); nm('thrBin', pb['binocular_threshold'], '{:.1f}'); nm('thrEye', pb['eyepiece20cm_threshold'], '{:.1f}')
nm('phoneStand', pb['phone_standalone_limit'], '{:.1f}'); nm('phoneAf', pb['phone_afocal20cm_limit'], '{:.1f}')
# injection-recovery
inj = json.load(open(f'{root}/outputs/tables/injection_recovery.json'))
INJ = {'NELIOTA': 'Nel', 'Amateur': 'Am', 'Phone afocal': 'Af', 'Phone standalone': 'Ph'}
for name, r in inj.items():
    tag = next(v for k, v in INJ.items() if name.startswith(k))
    m = np.array(r['mags']); cpl = np.array(r['completeness'])
    full = m[0]
    for mm, cc in zip(m, cpl):
        if cc >= 0.9: full = mm
        else: break
    idx = np.where(cpl < 0.5)[0]; j = idx[idx > 0][0] if len(idx[idx > 0]) else len(m) - 1
    k_ = max(j - 1, 0); half = m[k_] + (m[j] - m[k_]) * (cpl[k_] - 0.5) / max(cpl[k_] - cpl[j], 1e-9)
    nm(f'inj{tag}Half', half, '{:.1f}'); nm(f'inj{tag}Full', full, '{:.1f}'); nm(f'inj{tag}An', r['analytic_8sigma_limit'], '{:.1f}'); nm(f'inj{tag}Fa', 100 * r['false_alarm_per_frame'], '{:.0f}')
    nm(f'inj{tag}Ntr', int(r.get('ntrial', 10)), '{:d}')
fa = inj[next(k for k in inj if k.startswith('NELIOTA'))]['false_alarm_per_frame']
p_box = fa * 49.0 / (240.0 ** 2)
nm('faBox', f'{p_box:.0e}'.replace('e-0', '\\times10^{-').replace('e-', '\\times10^{-') + '}')
nm('faWinSingle', 3600 * p_box, '{:.1f}'); nm('faWinCoinc', f'{3600 * p_box ** 2:.0e}'.replace('e-0', '\\times10^{-').replace('e-', '\\times10^{-') + '}')
# plume numbers
p1 = cards['S1']['plume']; p2 = cards['S2']['plume']; p5 = cards['S5']['plume']; p8 = cards['S8']['plume']
nm('shOne', p1['shadow_height_km'], '{:.0f}'); nm('esPlumeOne', p1['earthshine_lit_plume_V_mag'], '{:.1f}')
nm('shTwo', p2['shadow_height_km'], '{:.1f}'); nm('vneedTwo', p2['ejecta_speed_needed_m_s'], '{:.0f}'); nm('tflTwo', p2['flight_time_s'], '{:.0f}')
nm('mNomTwo', p2['ejecta_mass_sunlit_kg'] / 1e3, '{:.1f}'); nm('mUpTwo', p2['ejecta_mass_sunlit_upper_kg'] / 1e3, '{:.1f}')
nm('vNomTwo', p2['plume_V_mag_10um'], '{:.1f}'); nm('vUpTwo', p2['plume_V_mag_10um_upper'], '{:.1f}')
nm('sbNomTwo', p2['plume_sb_10um_mag_arcsec2'], '{:.1f}'); nm('sbUpTwo', p2['plume_sb_10um_upper_mag_arcsec2'], '{:.1f}'); nm('bgTwo', p2['background_sb_V'], '{:.1f}')
nm('cNomTwo', p2['contrast_10um'], '{:.1f}'); nm('cUpTwo', p2['contrast_10um_upper'], '{:.1f}')
nm('vTenTwo', p2['plume_V_mag_10um'] + 2.5, '{:.1f}'); nm('cTenTwo', p2['contrast_10um'] / 10, '{:.2f}')
nm('cFive', p5['contrast_10um_upper'], '{:.3f}'); nm('shEight', p8['shadow_height_km'], '{:.1f}'); nm('emEight', cards['S8']['geometry']['emission_geocentric'], '{:.0f}')
# craters
cb = I.crater_diameter_range(2000, 1.68, 3); nm('crBalLo', cb[0], '{:.0f}'); nm('crBalMed', cb[1], '{:.0f}'); nm('crBalHi', cb[2], '{:.0f}')
br = [I.crater_diameter_range(np.mean(cfg['physics'][k]['mass_kg']), cfg['physics'][k]['v_km_s'], cfg['physics'][k]['angle_deg']) for k in ['V_MOD', 'V_STR', 'V_NSL']]
nm('crBrLo', min(x[0] for x in br), '{:.0f}'); nm('crBrHi', max(x[2] for x in br), '{:.0f}')

# SMART-1 conditional bound on eta_vis (declared 2006 camera parameters; see impact.smart1_saturation_eta)
def sci(x):
    m, e = f'{x:.1e}'.split('e'); return f'{m}\\times10^{{{int(e)}}}'
for T0, tag in [(1800, 'Cool'), (2500, 'Mid'), (3500, 'Hot')]:
    lo, hi = I.smart1_saturation_eta(T0, 0.5, overexposure=(1.0, 1.0)); nm(f'smSatLo{tag}', sci(lo)); nm(f'smSatHi{tag}', sci(hi))
    lo10, hi10 = I.smart1_saturation_eta(T0, 0.5, overexposure=(10.0, 10.0)); nm(f'smOverLo{tag}', sci(lo10))
nm('qHalfEdge', f'{q[2]:.1f}')

# convergence and Stage-2 refinement
cv = pd.read_csv(f'{root}/outputs/tables/convergence.csv')
nm('convGridVis', cv.d_vis_grid.abs().max(), '{:.3f}'); nm('convGridFlash', cv.d_flash_grid.abs().max(), '{:.3f}')
nm('convTime', max(cv.d_vis_time.abs().max(), cv.d_flash_time.abs().max()), '{:.4f}')
rel = (cv.d_vis_grid.abs() / cv.vis_n32_6h.where(cv.vis_n32_6h > 0.1)).max(); nm('convRel', 100 * rel, '{:.1f}')
rw = pd.read_csv(f'{root}/outputs/tables/refined_windows.csv').set_index('id')
r1 = rw.loc['S1']; t1 = pd.Timestamp(r1.epoch_utc)
fmt = lambda m: (t1 + pd.Timedelta(minutes=float(m))).strftime('%H:%M'); fmti = lambda m: (t1 + pd.Timedelta(minutes=float(m) + 180)).strftime('%H:%M')
nm('refTugStartOne', fmt(r1.tug_window_start_min)); nm('refTugEndOne', fmt(r1.tug_window_end_min))
nm('refTugStartIstOne', fmti(r1.tug_window_start_min)); nm('refTugEndIstOne', fmti(r1.tug_window_end_min))
nm('refNminOne', int(r1.n_min_in_window), '{:d}'); nm('refNmaxOne', int(r1.n_max_pm3h), '{:d}')
sp = [float(x.split('-')[1]) - float(x.split('-')[0]) for x in rw.emission_range_deg] + [float(x.split('-')[1]) - float(x.split('-')[0]) for x in rw.incidence_range_deg]
nm('refSpread', max(sp), '{:.1f}')
r4 = rw.loc['S4']; nm('refTugLenFour', float(r4.tug_window_end_min - r4.tug_window_start_min), '{:.0f}')
# opportunity statistics (post-start convention; scripts/run_opportunity_statistics.py) and plane-change gain
A_, P_ = 'A_turkiye_evening_public', 'P_plume_global'
def popp(tol, cls, N, col='p_at_least_one'):
    return float(po[(po.tol == tol) & (po.cls == cls) & (po.months == N)][col].values[0])
def nfull(tol, cls, col='p_at_least_one'):
    for N in [3, 4, 6, 9, 12, 18]:
        if popp(tol, cls, N, col) >= 0.995: return f'{N}'
    return 'more than 18'
nm('oppAThree', popp(0.6, A_, 3)); nm('oppAThreeR', popp(0.6, A_, 3), '{:.1f}'); nm('oppAFour', popp(0.6, A_, 4)); nm('oppAFourPC', popp(2.5, A_, 4))
nm('oppANfull', nfull(0.6, A_)); nm('oppANfullPC', nfull(2.5, A_))
nm('oppPThree', popp(0.6, P_, 3)); nm('oppPThreePC', popp(2.5, P_, 3)); nm('oppPSix', popp(0.6, P_, 6)); nm('oppPTwelve', popp(0.6, P_, 12))
nm('oppPThreeAll', popp(0.6, P_, 3, 'p_at_least_one_incl_prestart')); nm('oppPThreePCAll', popp(2.5, P_, 3, 'p_at_least_one_incl_prestart'))
nm('oppPNfull', nfull(0.6, P_)); nm('oppPNfullPC', nfull(2.5, P_))
ost = pd.read_csv(f'{root}/outputs/tables/opportunity_statistics.csv')
sel = lambda tol, cls: ost[(ost.tol == tol) & (ost.cls == cls)]
a6, p6, p25 = sel(0.6, A_), sel(0.6, P_), sel(2.5, P_)
nm('oppALunLo', int(a6.n_lunations_with_opp.min()), '{:d}'); nm('oppALunHi', int(a6.n_lunations_with_opp.max()), '{:d}'); nm('oppALunMean', a6.n_lunations_with_opp.mean(), '{:.1f}')
nm('oppALunMeanPC', sel(2.5, A_).n_lunations_with_opp.mean(), '{:.1f}')
nm('nLun', int(a6.n_lunations.max()), '{:d}'); nm('oppAPct', 100 * a6.n_lunations_with_opp.mean() / a6.n_lunations.max(), '{:.0f}')
b6 = sel(0.6, 'B_global_science'); nm('oppBLunLo', int(b6.n_lunations_with_opp.min()), '{:d}'); nm('oppBLunHi', int(b6.n_lunations_with_opp.max()), '{:d}'); nm('oppBThree', popp(0.6, 'B_global_science', 3))
nm('oppPLunLo', int(p6.n_lunations_with_opp.min()), '{:d}'); nm('oppPLunHi', int(p6.n_lunations_with_opp.max()), '{:d}')
nm('plumeGain', p25.n_lunations_with_opp.mean() / p6.n_lunations_with_opp.mean(), '{:.1f}')
nm('oppPLunLoPC', int(p25.n_lunations_with_opp.min()), '{:d}'); nm('oppPLunHiPC', int(p25.n_lunations_with_opp.max()), '{:d}')
nm('oppPreDays', -min(0.0, ost.first_opportunity_days_after_ref.min()), '{:.0f}')
aall = ost[ost.cls == A_]; a_first = aall.first_opportunity_days_after_ref.min()
nm('oppAFirst', a_first, '{:.0f}')
nm('oppAPreNote', f'class~A is unaffected because its earliest opportunity in any family is {a_first:.0f} days after the start' if a_first >= 0
   else f'class~A changes by at most {max(abs(popp(t, A_, 3) - popp(t, A_, 3, "p_at_least_one_incl_prestart")) for t in (0.6, 2.5)):.2f}')
rr = pd.read_csv(f'{root}/outputs/tables/reachability_region_summary.csv')
hrs = lambda fs: float(rr[(rr.family_set == fs) & (rr.quantity == 'flash_cov3') & (rr.region == 'near side central')].mean_hours.values[0])
nm('reachGain', hrs('tol2.5_drift0.0') / hrs('tol0.6_drift0.0'), '{:.1f}')
nm('reachHrsNoPC', hrs('tol0.6_drift0.0'), '{:.0f}'); nm('reachHrsPC', hrs('tol2.5_drift0.0'), '{:.0f}')
# scenario-to-scenario changes quoted in the text (wide prior; at-least-one and two-independent metrics; all three strategies)
def mcv(sid, strat, key): return cards[sid]['mc'][f'{strat}|slow-impact-wide'][key]
def drop(s_ref, s_alt, keys=('p_any', 'p_two_indep')):
    d = [mcv(s_ref, st, k) - mcv(s_alt, st, k) for st in SL for k in keys]
    return f'{min(d):.2f}--{max(d):.2f}'
nm('dropBr', drop('S1', 'S10')); nm('dropJan', drop('S1', 'S11')); nm('dropPlume', drop('S1', 'S2', ('p_any',)))
gap = [mcv(sid, 'B_global_science', 'p_confirmed') - mcv(sid, 'C_public_participation', 'p_confirmed') for sid in order if sid != 'S9']
nm('gapCB', max(gap))
darknp = [sid for sid in order if cards[sid]['geometry']['incidence'] > 90 and cards[sid]['region'] != 'polar' and cards[sid]['n_sites_available'] > 0]
rat = [mcv(sid, st, 'p_confirmed') / mcv(sid, 'A_turkiye_priority', 'p_confirmed') for sid in darknp for st in ('B_global_science', 'C_public_participation') if mcv(sid, 'A_turkiye_priority', 'p_confirmed') > 0]
nm('confRatio', f'{min(rat):.1f}--{max(rat):.1f}')
from ayap1obs import weather as Wt
pcl = [Wt.p_clear_hour(sites['TUG'], mo) for mo in range(1, 13)]; nm('cloudTug', f'{1 - max(pcl):.2f}--{1 - min(pcl):.2f}')
nm('gapNaked', pk['peakV_wide']['p50'] - pb['naked_eye_threshold'], '{:.0f}')
# DIRAC field coverage for larger along-track uncertainties (same cross-track sigma and 15" pointing error as the Monte Carlo)
rng_cov = np.random.default_rng(20261005); dfov = templates['dag_dirac']['fov_arcmin']; scr = cfg['physics']['V_BAL']['sigma_cross_km']
nm('diracCovFifty', MC.fov_coverage(dfov, 50.0, scr, n=200000, rng=rng_cov)); nm('diracCovHundred', MC.fov_coverage(dfov, 100.0, scr, n=200000, rng=rng_cov))
open(f'{root}/paper/sections/numbers.tex', 'w').write('\n'.join(NUM) + '\n')
print('tables written;', len(NUM) - 1, 'number macros')
