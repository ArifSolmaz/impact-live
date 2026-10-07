import { initPage, load, t, L, fmt, el, onLangChange, tableToggle, storageGet, storageSet } from '../common.js';
import { distribution } from '../charts.js';
import { MoonView } from '../moonview.js';
import { mountLocationWidget } from '../location.js';

await initPage();
const [MAG, SC, EV] = await Promise.all([load('magnitudes.json'), load('scenarios.json'), load('event.json')]);
const S1 = SC.scenarios.find((s) => s.id === 'S1');
const css = getComputedStyle(document.documentElement); const C = (v) => css.getPropertyValue(v).trim();
// order: methods that never reach half their maximum chance first, then by the brightness at which they do
const halfKey = (m) => m.half ?? (m.beyond ? 99 : -99);
const halfText = (m) => (m.half === null || m.half === undefined) ? t(m.beyond ? 'see.beyond' : 'see.never') : t('see.half_at', { m: fmt.num(m.half, 1) });
const methods = [...MAG.methods].sort((a, b) => halfKey(a) - halfKey(b));
const binOf = (mag) => Math.max(0, Math.min(MAG.bins.count - 1, Math.floor((mag - MAG.bins.start) / MAG.bins.step)));

// ---------------------------------------------------------------- distribution + ladder
let ladderTable = null;
function ladder() {
  const pw = MAG.pct.wide;
  distribution(document.getElementById('dist'), {
    start: MAG.bins.start, step: MAG.bins.step, xMin: 0, xMax: 21,
    series: [{ label: t('see.hist_wide'), color: C('--series-1'), values: MAG.hist.wide }, { label: t('see.hist_vs'), color: C('--series-2'), values: MAG.hist.vs }],
    markers: methods.filter((m) => m.half !== null && m.half <= 21).map((m) => ({ x: m.half, label: t(`see.mk.${m.key}`), essential: ['binoculars', 'eyepiece', 'neliota', 'fast_large'].includes(m.key) })),
    leftLabel: t('see.axis_bright'), rightLabel: t('see.axis_faint'), axisLabel: `${t('see.axis_mag')} · ${t('see.median', { m: fmt.num(pw.p50, 1) })}`, ariaLabel: t('see.hist_title'),
  });
  document.getElementById('ladder').replaceChildren(...methods.map((m) => el('div', { class: 'lrow' },
    el('div', { class: 'lname' }, L(m.label), el('small', {}, `${halfText(m)}${m.band !== 'V' ? ` · ${t('band.' + m.band)}` : ''}`)),
    el('div', { class: 'meter', role: 'img', 'aria-label': fmt.pct(m.p) }, el('span', { style: `width:${Math.max(1, m.p * 100)}%` })),
    el('div', { class: 'lval' }, fmt.pct(m.p, m.p < 0.01 ? 1 : 0)))));
  if (!ladderTable) ladderTable = tableToggle(document.getElementById('ladder-table'), () => ({ head: [t('see.sim_method'), t('see.v_equiv'), t('see.p_bright'), t('see.limit')],
    rows: methods.map((m) => [L(m.label), m.band, fmt.pct(m.p, 1), (m.half === null || m.half === undefined) ? t(m.beyond ? 'see.beyond' : 'see.never') : fmt.num(m.half, 2)]) }));
  else ladderTable.refresh();
}

// ---------------------------------------------------------------- simulator
const sim = new MoonView(document.getElementById('sim-moon'), { grid: false, earthshine: 0.1 }); await sim.ready();
const ZOOM = { phone: 1, naked: 1, binoculars: 1.25, phone_scope: 2, eyepiece: 2, amateur: 2.2, neliota: 2.6, fast_large: 3, nir: 3 };
const termLon = S1.moon.subsolar_lon - 90;   // sunrise terminator of the waxing Moon
const frame = (k) => (k > 1 ? { lat: S1.lat, lon: S1.lon + (termLon - S1.lon) * 0.45 } : null);
const sel = document.getElementById('sim-method'); const range = document.getElementById('sim-bright');
const cdf = (() => { const h = MAG.hist.wide; const out = []; let acc = 0; h.forEach((v, i) => { acc += v; out.push([MAG.bins.start + (i + 1) * MAG.bins.step, acc]); }); return out; })();
const magAt = (q) => { for (let i = 0; i < cdf.length; i++) if (cdf[i][1] >= q) { const [x1, y1] = cdf[i]; const [x0, y0] = i ? cdf[i - 1] : [MAG.bins.start, 0]; return x0 + (q - y0) / Math.max(1e-9, y1 - y0) * (x1 - x0); } return cdf[cdf.length - 1][0]; };
function simOptions() {
  const v = sel.value; sel.replaceChildren(...methods.map((m) => el('option', { value: m.key }, L(m.label))));
  sel.value = v || 'eyepiece';
}
function simView() {
  const key = sel.value; const k = ZOOM[key] || 1;
  sim.set({ subEarth: { lat: S1.moon.subearth_lat, lon: S1.moon.subearth_lon }, subSolar: { lat: S1.moon.subsolar_lat, lon: S1.moon.subsolar_lon }, markers: [{ lat: S1.lat, lon: S1.lon, target: true }], flash: null }, { zoom: k, center: frame(k) });
  const q = +range.value / 100; document.getElementById('sim-bright-hint').textContent = `${fmt.num(magAt(q), 1)} ${t('unit.mag')} · ${t('see.sim_bright_hint', { pct: fmt.pctNum(q) })}`;
  document.getElementById('sim-result').replaceChildren(); document.getElementById('sim-msg').classList.add('hidden');
}
let anim = null;
function play() {
  const m = methods.find((x) => x.key === sel.value); const mag = magAt(+range.value / 100);
  const p = m.curve[binOf(mag)];
  const msg = document.getElementById('sim-msg');
  document.getElementById('sim-result').replaceChildren(el('span', { class: `result-pill ${p >= 0.5 ? 'yes' : (p < 0.05 ? 'no' : 'maybe')}` }, t('see.sim_p', { mag: fmt.num(mag, 1), p: fmt.pct(p, p < 0.01 ? 1 : 0) })));
  cancelAnimationFrame(anim); const t0 = performance.now(); msg.classList.add('hidden');
  const peak = Math.min(1, 0.15 + 0.85 * p);       // schematic: brighter spot for a higher chance; not a photometric rendering
  const step = (now) => {
    const dt = (now - t0) / 1000; const inten = dt < 0.06 ? peak * dt / 0.06 : peak * Math.exp(-(dt - 0.06) / 0.45);
    sim.state.flash = { lat: S1.lat, lon: S1.lon, intensity: inten, radius: 4 + 3 * (ZOOM[m.key] || 1) / 3 }; sim.compose();
    if (dt < 2.2) anim = requestAnimationFrame(step); else { sim.state.flash = null; sim.compose(); }
  };
  anim = requestAnimationFrame(step);
}
sel.addEventListener('change', simView); range.addEventListener('input', simView); document.getElementById('sim-play').addEventListener('click', play);

// ---------------------------------------------------------------- location
const presets = [{ key: 'see.loc_now', date: new Date(), default: true }, { key: 'see.loc_s1', date: new Date(S1.epoch_utc) }];
if (EV.impact_utc) presets.push({ key: 'see.loc_event', date: new Date(EV.impact_utc) });
await mountLocationWidget(document.getElementById('loc'), { presets });

// ---------------------------------------------------------------- observer kit
function kit() {
  const done = storageGet('impact-live-kit', {});
  document.getElementById('kit').replaceChildren(...[1, 2, 3, 4, 5, 6, 7, 8].map((i) => {
    const cb = el('input', { type: 'checkbox', checked: done[i] ? true : null });
    cb.addEventListener('change', () => { done[i] = cb.checked; storageSet('impact-live-kit', done); });
    return el('li', {}, el('label', {}, cb, el('span', {}, el('div', { class: 'ck-title' }, t(`kit.${i}_t`)), el('div', { class: 'ck-detail' }, t(`kit.${i}_d`)))));
  }));
}

function all() { ladder(); simOptions(); simView(); kit(); }
all();
onLangChange(all);
