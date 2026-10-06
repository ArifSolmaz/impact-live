import { initPage, load, t, L, fmt, el, onLangChange, tableToggle, storageGet, storageSet } from '../common.js';
import { distribution } from '../charts.js';
import { MoonView } from '../moonview.js';
import { mountLocationWidget } from '../location.js';

await initPage();
const [MAG, SC, EV] = await Promise.all([load('magnitudes.json'), load('scenarios.json'), load('event.json')]);
const S1 = SC.scenarios.find((s) => s.id === 'S1');
const css = getComputedStyle(document.documentElement); const C = (v) => css.getPropertyValue(v).trim();
const methods = [...MAG.methods].sort((a, b) => a.v_equiv - b.v_equiv);

// ---------------------------------------------------------------- distribution + ladder
let ladderTable = null;
function ladder() {
  const pw = MAG.pct.wide;
  distribution(document.getElementById('dist'), {
    start: MAG.bins.start, step: MAG.bins.step, xMin: 0, xMax: 21,
    series: [{ label: t('see.hist_wide'), color: C('--series-1'), values: MAG.hist.wide }, { label: t('see.hist_v3'), color: C('--series-2'), values: MAG.hist.v3 }],
    markers: methods.filter((m) => m.key !== 'phone').map((m) => ({ x: m.v_equiv, label: t(`see.mk.${m.key}`), essential: ['naked', 'binoculars', 'eyepiece', 'neliota', 'nir'].includes(m.key) })),
    leftLabel: t('see.axis_bright'), rightLabel: t('see.axis_faint'), axisLabel: `${t('see.axis_mag')} · ${t('see.median', { m: fmt.num(pw.p50, 1) })}`, ariaLabel: t('see.hist_title'),
  });
  document.getElementById('ladder').replaceChildren(...methods.map((m) => el('div', { class: 'lrow' },
    el('div', { class: 'lname' }, L(m.label), el('small', {}, `${t('see.limit')} ${fmt.num(m.limit, 1)} ${t('unit.mag')}${m.band !== 'V' ? ` (${t('band.' + m.band)})` : ''}`)),
    el('div', { class: 'meter', role: 'img', 'aria-label': fmt.pct(m.p_bright_enough) }, el('span', { style: `width:${Math.max(1, m.p_bright_enough * 100)}%` })),
    el('div', { class: 'lval' }, fmt.pct(m.p_bright_enough)))));
  if (!ladderTable) ladderTable = tableToggle(document.getElementById('ladder-table'), () => ({ head: [t('see.sim_method'), t('see.limit'), t('see.v_equiv'), t('see.p_bright')], rows: methods.map((m) => [L(m.label), `${fmt.num(m.limit, 2)} ${m.band}`, fmt.num(m.v_equiv, 2), fmt.pct(m.p_bright_enough, 1)]) }));
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
  const m = methods.find((x) => x.key === sel.value); const mag = magAt(+range.value / 100); const visible = mag < m.v_equiv;
  const margin = m.v_equiv - mag; const peak = visible ? Math.min(1, 0.3 + 0.18 * margin) : 0;
  const msg = document.getElementById('sim-msg');
  document.getElementById('sim-result').replaceChildren(el('span', { class: `result-pill ${visible ? 'yes' : 'no'}` }, t(visible ? 'see.sim_yes' : 'see.sim_no', { mag: fmt.num(mag, 1), lim: fmt.num(m.v_equiv, 1) })));
  cancelAnimationFrame(anim); const t0 = performance.now(); msg.classList.add('hidden');
  const step = (now) => {
    const dt = (now - t0) / 1000; const inten = dt < 0.06 ? peak * dt / 0.06 : peak * Math.exp(-(dt - 0.06) / 0.45);
    sim.state.flash = { lat: S1.lat, lon: S1.lon, intensity: inten, radius: 4 + 3 * (ZOOM[m.key] || 1) / 3 }; sim.compose();
    if (dt < 2.2) anim = requestAnimationFrame(step); else { sim.state.flash = null; sim.compose(); if (!visible) { msg.textContent = t('see.sim_no', { mag: fmt.num(mag, 1), lim: fmt.num(m.v_equiv, 1) }); msg.classList.remove('hidden'); } }
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
