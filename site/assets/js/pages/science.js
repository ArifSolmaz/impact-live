import { initPage, load, t, L, fmt, el, onLangChange, repoUrl } from '../common.js';

const meta = await initPage();
const [SC, MAG] = await Promise.all([load('scenarios.json'), load('magnitudes.json')]);
const S1 = SC.scenarios.find((s) => s.id === 'S1'); const OPP = SC.opportunity || {};
const FIGS = ['fig_surface_screening', 'fig_reachability', 'fig_availability_timeseries', 'fig_flash_sensitivity', 'fig_lightcurves_limits', 'fig_public_thresholds', 'fig_ejecta_crater',
  'fig_plume_S2', 'fig_plume_and_earthview', 'fig_timeline_families', 'fig_orbiter_windows', 'fig_pareto', 'fig_injection_recovery', 'fig_sensitivity', 'fig_scenario_S1_coverage'];
const repo = repoUrl(meta);

function findings() {
  const p = S1.p;
  const plumeSnr = Math.max(0, ...SC.scenarios.map((s) => s.plume.snr_max || 0));
  const plumeFine = Math.max(0, ...SC.scenarios.map((s) => s.plume.snr_fine || 0));
  const items = [
    t('sci.f1', { med: fmt.num(MAG.pct.wide.p50, 1) }),
    t('sci.f2', { a: fmt.pct(p.A.wide.any), b: fmt.pct(p.B.wide.any), twoA: fmt.pct(p.A.wide.two), twoB: fmt.pct(p.B.wide.two) }),
    t('sci.f3', { eye: fmt.pct(S1.visual.eyepiece.p) }),
    t('sci.f4', { a: fmt.pct(OPP.A_w30), b: fmt.pct(OPP.B_w30) }),
    t('sci.f5', { snr: fmt.num(plumeSnr, 1), fine: fmt.num(plumeFine, 0) }),
    t('sci.f6', { min: fmt.num(Math.min(S1.crater.vc[0], S1.crater.ve[0])), max: fmt.num(Math.max(S1.crater.vc[1], S1.crater.ve[1])) }),
  ];
  document.getElementById('findings').replaceChildren(...items.map((x) => el('li', {}, x)));
}
function methods() {
  document.getElementById('methods').replaceChildren(...[1, 2, 3, 4, 5, 6].map((i) => el('div', { class: 'card' }, el('div', { class: 'kicker' }, String(i).padStart(2, '0')), el('h3', {}, t(`m.${i}_t`)), el('p', { class: 'secondary small', style: 'margin:0' }, t(`m.${i}_d`, { outer: fmt.num(SC.mc.n_outer), inner: fmt.num(SC.mc.n_inner), n: fmt.num(SC.mc.n_outer * SC.mc.n_inner) })))));
}
function gallery() {
  const lb = document.getElementById('lightbox'), img = document.getElementById('lb-img');
  document.getElementById('gallery').replaceChildren(...FIGS.map((f) => {
    const src = `assets/figures/${f}.jpg`; const cap = t(`fig.${f}`);
    const b = el('button', { type: 'button', 'aria-label': cap }, el('img', { src, alt: cap, loading: 'lazy' }));
    b.addEventListener('click', () => { img.src = src; img.alt = cap; lb.classList.add('open'); document.getElementById('lb-close').focus(); });
    return el('figure', {}, b, el('figcaption', {}, el('b', {}, cap), repo ? el('a', { href: `${repo}/blob/main/outputs/figures/${f}.pdf` }, 'PDF') : ''));
  }));
}
document.getElementById('lb-close').addEventListener('click', () => document.getElementById('lightbox').classList.remove('open'));
document.getElementById('lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') e.currentTarget.classList.remove('open'); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.getElementById('lightbox').classList.remove('open'); });

function data() {
  const links = [['outputs/scenarios', 'scenarios (JSON)'], ['outputs/tables', 'tables (CSV/JSON)'], ['outputs/figures', 'figures (PNG/PDF)'], ['research', 'research notes'], ['scripts', 'pipeline scripts'], ['site/data', 'site data']];
  document.getElementById('data-links').replaceChildren(...links.map(([p, label]) => el('li', {}, repo ? el('a', { href: `${repo}/tree/main/${p}` }, p) : el('code', {}, p), ` — ${label}`)));
  const clone = repo ? `git clone ${repo}.git\ncd ${repo.split('/').pop()}` : 'cd impact-live';
  document.getElementById('repro').textContent = `${clone}\npython3 -m venv .venv && source .venv/bin/activate\npip install -r requirements.txt\nmake all          # ~2 h; or: make all MC_OUTER=40 MC_INNER=50 NTRIAL=20\nmake site         # refresh this website's data\npython3 -m http.server -d site 8000`;
  const year = '2026';
  document.getElementById('cite').textContent = `${meta ? meta.author : ''} (${year}). ${t('site.name')}: ${state_title()} (v${meta ? meta.version : '1.0.0'}). ${repo || 'GitHub'}`;
  document.getElementById('manuscript').textContent = meta ? L(meta.manuscript) : '';
}
function state_title() { return document.documentElement.lang === 'tr' ? 'gözlenebilirlik çalışması — kod, veri ve etkileşimli site' : 'observability study — code, data and interactive site'; }
function all() { findings(); methods(); gallery(); data(); }
all(); onLangChange(all);
