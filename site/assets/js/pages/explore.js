import { initPage, load, t, L, fmt, el, onLangChange, tip, hideTip, tableToggle, classBadge, loadImageData, state } from '../common.js';
import { MoonView } from '../moonview.js';
import { EarthMap } from '../earthmap.js';
import { subPoints } from '../astro.js';
import { groupedBars, calendarStrip } from '../charts.js';

await initPage();
const [SC, SITES, HEAT, FEAT, CAL] = await Promise.all([load('scenarios.json'), load('sites.json'), load('heat.json'), load('moon_features.json'), load('calendar.json')]);
const scen = SC.scenarios; const siteById = Object.fromEntries(SITES.sites.map((s) => [s.id, s]));
const css = getComputedStyle(document.documentElement); const C = (v) => css.getPropertyValue(v).trim();
const SERIES = [{ key: 'A', color: C('--series-1') }, { key: 'B', color: C('--series-2') }, { key: 'C', color: C('--series-3') }];
const METRICS = ['any', 'two', 'live', 'rapid'];
const st = { id: (location.hash || '#S1').slice(1), net: 'B', prior: 'wide', heat: '', labels: false };
if (!scen.find((s) => s.id === st.id)) st.id = 'S1';
const cur = () => scen.find((s) => s.id === st.id);
// impact point beyond the limb as seen from the Earth's centre (far side or occulted)
const occulted = (s) => s.geometry.emission >= 90;
// calendar sessions carry full ISO timestamps (UTC and Istanbul) and the local night
const iso = (z) => new Date(z.replace('Z', ':00Z'));

// ---------------------------------------------------------------- views
const moon = new MoonView(document.getElementById('moon'), { grid: true }); await moon.ready();
const earth = new EarthMap(document.getElementById('earth')); await earth.ready();
const heatImg = {};
moon.onHover((m, e) => { if (!m) return hideTip(); const s = scen.find((x) => x.id === m.id); tip(e, (tt) => { tt.append(el('strong', { text: s.id }), el('div', {}, L(s.name))); }); });
earth.onHover((h, e) => {
  if (!h) return hideTip(); const g = h.st || {};
  tip(e, (tt) => {
    tt.append(el('strong', { text: h.s.name }), el('div', {}, L(h.s.country_name)));
    if (g.moon_alt !== undefined) tt.append(el('div', {}, `${t(g.available ? 'ex.site_tip_avail' : 'ex.site_tip_unavail')} · ${t('ex.site_tip_alt', { alt: fmt.num(g.moon_alt, 0) })} · ${t('ex.site_tip_sun', { alt: fmt.num(g.sun_alt, 0) })}`));
    tt.append(el('div', { class: 'small' }, L(h.s.tier_label)));
  });
});

function chips() {
  document.getElementById('chips').replaceChildren(...scen.map((s) => {
    const b = el('button', { class: 'chip', type: 'button', 'aria-pressed': String(s.id === st.id), title: L(s.name) }, el('span', { class: `badge ${s.cls}`, style: 'padding:0;border:0;background:none' }, el('span', { class: 'dot' })), s.id);
    b.addEventListener('click', () => { st.id = s.id; history.replaceState(null, '', `#${s.id}`); update(); });
    return b;
  }));
}
function head() {
  const s = cur();
  document.getElementById('scenario-head').replaceChildren(
    el('div', { class: 'row' }, el('strong', { style: 'font-size:1.15rem' }, `${s.id} · ${L(s.name)}`), classBadge(s.cls), el('span', { class: 'badge demo' }, t('common.hypothetical'))),
    el('p', { class: 'secondary', style: 'margin:10px 0 0' }, L(s.why)));
}
async function views() {
  const s = cur();
  const same = scen.filter((x) => x.epoch_utc === s.epoch_utc && x.id !== 'S10');   // test points evaluated at the same moment
  const markers = same.map((x) => ({ id: x.id, lat: x.lat, lon: x.lon, label: x.id === 'S1' && (st.id === 'S10' || st.id === 'S1') && scen.find((y) => y.id === 'S10') ? 'S1 / S10' : x.id, selected: x.id === s.id || (s.id === 'S10' && x.id === 'S1') }));
  let heat = null;
  if (st.heat) { heatImg[st.heat] = heatImg[st.heat] || await loadImageData(`data/${HEAT[st.heat].file}`); heat = heatImg[st.heat]; }
  moon.set({ subEarth: { lat: s.moon.subearth_lat, lon: s.moon.subearth_lon }, subSolar: { lat: s.moon.subsolar_lat, lon: s.moon.subsolar_lon }, markers, features: FEAT }, { heat, labels: st.labels });
  document.getElementById('moon-sub').textContent = t('ex.moon_sub', { date: fmt.date(s.epoch_utc), pct: fmt.pctNum(s.moon.illum), age: fmt.num(s.moon.age_days, 1) });
  document.getElementById('farside').classList.toggle('hidden', moon.disk(s.lat, s.lon).z > 0);
  const hl = document.getElementById('heat-legend'); hl.classList.toggle('hidden', !st.heat);
  if (st.heat) hl.textContent = t(st.heat === 'h_tr' ? 'ex.heat_legend_tr' : 'ex.heat_legend_plume', { lo: fmt.num(HEAT[st.heat].lo_hours, 0), max: fmt.num(HEAT[st.heat].max_hours, 0),
    start: fmt.dateOnly(HEAT.interval[0] + 'T12:00:00Z', 'UTC'), stop: fmt.dateOnly(HEAT.interval[1] + 'T12:00:00Z', 'UTC') });
  document.querySelectorAll('#heat-tabs button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.heat === st.heat)));
  const sp = subPoints(new Date(s.epoch_utc));
  earth.set({ sun: sp.sun, moon: sp.moon, siteStatus: s.site_geom });
  document.getElementById('earth-occ').classList.toggle('hidden', !occulted(s));
}
document.querySelectorAll('#heat-tabs button').forEach((b) => b.addEventListener('click', () => { st.heat = b.dataset.heat; views(); }));
document.getElementById('labels').addEventListener('change', (e) => { st.labels = e.target.checked; views(); });

// ---------------------------------------------------------------- odds
let barChart = null, oddsTable = null;
function netTabs() {
  document.getElementById('net-tabs').replaceChildren(...SERIES.map((se) => {
    const b = el('button', { role: 'tab', 'aria-selected': String(se.key === st.net) }, t(`strat.${se.key}`));
    b.addEventListener('click', () => { st.net = se.key; odds(); }); return b;
  }));
  document.querySelectorAll('#prior-tabs button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.prior === st.prior)));
}
document.querySelectorAll('#prior-tabs button').forEach((b) => b.addEventListener('click', () => { st.prior = b.dataset.prior; odds(); }));
function odds() {
  const s = cur(); netTabs();
  document.getElementById('net-desc').textContent = t(`strat.${st.net}_d`);
  const p = s.p[st.net][st.prior];
  document.getElementById('odds-stats').replaceChildren(...METRICS.map((k) => el('div', { class: 'stat' }, el('div', { class: 'label' }, t(`metric.${k}`)), el('div', { class: 'value' }, fmt.pct(p[k])),
    el('div', { class: 'sub' }, `${t(`metric.${k}_d`)} · ${t('metric.range', { lo: fmt.pct(p.range[k][0]), hi: fmt.pct(p.range[k][1]) })}`))));
  const series = SERIES.map((se) => ({ ...se, label: t(`strat.${se.key}`) }));
  const cats = METRICS.map((k) => ({ key: k, label: t(`metric.${k}`) }));
  barChart = groupedBars(document.getElementById('odds-chart'), { categories: cats, series, emphasis: st.net, value: (c, se) => s.p[se.key][st.prior][c.key] ?? 0, ariaLabel: t('ex.odds_chart_title') });
  if (!oddsTable) oddsTable = tableToggle(document.getElementById('odds-table'), () => ({ head: ['', ...SERIES.map((se) => t(`strat.${se.key}`))], rows: METRICS.map((k) => [t(`metric.${k}`), ...SERIES.map((se) => fmt.pct(cur().p[se.key][st.prior][k]))]) }));
  else oddsTable.refresh();
}

// ---------------------------------------------------------------- details and stations
function details() {
  const s = cur(); const g = s.site_geom; const dd = [];
  const add = (k, v) => dd.push(el('dt', {}, t(k)), el('dd', {}, v));
  add('ex.d_time', `${fmt.date(s.epoch_utc)} ${t('common.ist')} · ${fmt.time(s.epoch_utc, 'UTC')} UTC`);
  if (s.moon.light_time_range_s) add('ex.d_light', t('ex.v_light', { a: fmt.num(s.moon.light_time_range_s[0], 3), b: fmt.num(s.moon.light_time_range_s[1], 3) }));
  add('ex.d_region', `${L(s.region)} (${fmt.num(s.lat, 1)}°, ${fmt.num(s.lon, 1)}°)`);
  add('ex.d_moon', t('ex.v_moon', { pct: fmt.pctNum(s.moon.illum), age: fmt.num(s.moon.age_days, 1) }));
  add('ex.d_alt', `${fmt.num(g.TUG.moon_alt, 0)}° / ${fmt.num(g.DAG.moon_alt, 0)}°`);
  add('ex.d_sites', t('ex.v_sites', { n: s.n_sites, tr: s.turkish_sites.length }));
  if (s.closed_sites && s.closed_sites.length) add('ex.d_closed', s.closed_sites.join(', '));
  add('ex.d_pop', t('ex.v_bn', { n: fmt.num(s.settlements_bn.public, 2), lo: fmt.num(s.settlements_bn.public_range[0], 2), hi: fmt.num(s.settlements_bn.public_range[1], 2) }));
  add('ex.d_physics', L(s.physics.label));
  add('ex.d_energy', t('ex.v_energy', { gj: fmt.num(s.energy_GJ, 2), tnt: fmt.num(s.tnt_kg, 0) }));
  const pk = { med: fmt.num(s.source_equiv_V.median, 1), p10: fmt.num(s.source_equiv_V.p10, 1), p90: fmt.num(s.source_equiv_V.p90, 1) };
  add('ex.d_flash', occulted(s) ? t('ex.v_flash_occ', pk) : t(s.geometry.sunlit ? 'ex.v_flash_sunlit' : 'ex.v_flash', pk));
  add('ex.d_witness', occulted(s) || !s.visual.observable ? t('ex.v_witness_occ') : t('ex.v_witness', { p: fmt.pct(s.visual.eyepiece.p, 1), pw: fmt.pct(s.visual.eyepiece.p_weather, 1) }));
  const pl = s.plume;
  add('ex.d_plume', pl.code === 'cannot' ? t('ex.v_plume_cannot', { h: fmt.num(pl.h_km, pl.h_km < 10 ? 1 : 0) }) : pl.code === 'weak' ? t('ex.v_plume_weak', { snr: fmt.num(pl.snr_max, 2) })
    : pl.code === 'possible' ? t('ex.v_plume_possible', { snr: fmt.num(pl.snr_max, 1) }) : t('ex.v_plume_none'));
  add('ex.d_crater', t('ex.v_crater', { a: fmt.num(s.crater.vc[0]), b: fmt.num(s.crater.vc[1]), c: fmt.num(s.crater.ve[0]), d: fmt.num(s.crater.ve[1]) }));
  if (!occulted(s)) {
    const lo = fmt.pct(s.terrain[0]), hi = fmt.pct(s.terrain[1]);
    add('ex.d_terrain', t('ex.v_terrain', { range: lo === hi ? lo : `${lo}–${hi}` }));
  }
  add('ex.d_reach', t('ex.v_reach', { p06: fmt.pct(s.reach.p06, 1), p25: fmt.pct(s.reach.p25, 1), per: fmt.num(s.reach.period_min, 0) }));
  add('ex.d_lro', t('ex.v_lro', { p: fmt.pct(s.lro.p_operational) }));
  document.getElementById('details').replaceChildren(...dd);
  document.getElementById('stations-title').textContent = t('ex.stations_title');
  const rows = s.top_stations.length ? s.top_stations.map((x) => el('div', { class: 'lrow' },
    el('div', { class: 'lname' }, L(x.name), el('small', {}, siteById[x.id] ? L(siteById[x.id].country_name) : '')),
    el('div', { class: 'meter', role: 'img', 'aria-label': fmt.pct(x.p) }, el('span', { style: `width:${Math.max(1.5, x.p * 100)}%` })),
    el('div', { class: 'lval' }, fmt.pct(x.p)))) : [el('p', { class: 'muted' }, t('ex.stations_none'))];
  document.getElementById('stations').replaceChildren(...rows);
}

// ---------------------------------------------------------------- calendar
let calTable = null;
function calendar() {
  const cr = CAL.criteria;
  document.getElementById('cal-lead').textContent = t('ex.cal_lead', { site: cr.site, alt: cr.moon_alt_min, sun: fmt.num(cr.sun_alt_max, 0), imin: fmt.num(cr.illum_min * 100, 0), imax: fmt.num(cr.illum_max * 100, 0), el: cr.elongation_min, step: cr.refine_step_min });
  const series = [{ key: 'evening', label: t('ex.cal_evening'), color: C('--series-1') }, { key: 'morning', label: t('ex.cal_morning'), color: C('--series-2') }];
  const groups = {}; scen.forEach((s) => { const d = s.epoch_utc; (groups[d] = groups[d] || []).push(s.id); });
  const marks = Object.entries(groups).filter(([, ids]) => !ids.includes('S9') || ids.length > 1).map(([d, ids]) => ({ date: d, label: ids.sort((a, b) => +a.slice(1) - +b.slice(1))[0] }));
  const wins = CAL.windows.map((w) => ({ ...w, date: w.night, hours: w.minutes / 60 }));
  const ist = (z) => fmt.date(iso(z), 'Europe/Istanbul', { dateStyle: 'medium', timeStyle: 'short' });
  const istT = (z) => fmt.date(iso(z), 'Europe/Istanbul', { timeStyle: 'short' });
  calendarStrip(document.getElementById('calendar'), {
    windows: wins, start: CAL.domain.start, end: CAL.domain.stop, series, marks, yLabel: t('ex.cal_y'), ariaLabel: t('ex.cal_title'),
    tooltip: (tt, w, se) => {
      tt.append(el('strong', { text: `${ist(w.start_utc)} – ${istT(w.end_utc)}` }), el('div', { class: 'tl-row' }, el('span', { class: 'tl-key', style: `background:${se.color}` }), se.label));
      tt.append(el('div', {}, `${t('ex.cal_best')}: ${ist(w.best_utc)}`), el('div', {}, `${fmt.pct(w.illum)} · TUG ${fmt.num(w.alt_tug, 0)}° · ${w.n_sites} ${t('ex.cal_sites')}`));
    },
  });
  if (!calTable) calTable = tableToggle(document.getElementById('calendar-table'), () => ({ head: [t('ex.cal_date'), t('ex.cal_session'), t('ex.cal_window'), t('ex.cal_best'), t('ex.d_sites')],
    rows: CAL.windows.map((w) => [fmt.dateOnly(w.night + 'T12:00:00Z', 'UTC'), t(w.session === 'evening' ? 'ex.cal_evening' : 'ex.cal_morning'), `${ist(w.start_utc)} – ${istT(w.end_utc)}`, ist(w.best_utc), String(w.n_sites)]) }));
  else calTable.refresh();
}

function update() { chips(); head(); views(); odds(); details(); }
update(); calendar();
onLangChange(() => { update(); calendar(); });
window.addEventListener('hashchange', () => { const id = location.hash.slice(1); if (scen.find((s) => s.id === id)) { st.id = id; update(); } });
