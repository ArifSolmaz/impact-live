import { initPage, load, reload, t, L, fmt, el, onLangChange, state } from '../common.js';
import { MoonView } from '../moonview.js';
import { moonGeometry } from '../astro.js';
import { mountLocationWidget } from '../location.js';

await initPage();
const SC = await load('scenarios.json');
const S1 = SC.scenarios.find((s) => s.id === 'S1');
let EV = await load('event.json');
let demo = new URLSearchParams(location.search).get('demo') === '1';
const DEMO = { status: 'announced', impact_utc: S1.epoch_utc, impact_uncertainty_min: S1.physics.sigma_t_min, target: { lat: S1.lat, lon: S1.lon, name: { tr: 'Varsayımsal nokta S1', en: 'Hypothetical point S1' } }, streams: [], watch_events: [], updates: [], results: null, mission_status: null };
const E = () => (demo ? { ...EV, ...DEMO } : EV);

const moon = new MoonView(document.getElementById('moon'), { grid: true }); await moon.ready();
let loc = null, timer = null;

function header() {
  const e = E();
  document.getElementById('status-badge').replaceChildren(el('span', { class: `badge ${demo ? 'demo' : e.status}` }, el('span', { class: 'dot', 'aria-hidden': 'true' }), demo ? 'DEMO' : t(`live.status.${e.status}`)));
  document.getElementById('updated').textContent = EV.updated_utc ? t('live.updated', { date: fmt.date(EV.updated_utc) }) : '';
  document.getElementById('demo-banner').classList.toggle('hidden', !demo);
  const hasTime = !!e.impact_utc;
  document.getElementById('planning').classList.toggle('hidden', hasTime);
  document.getElementById('countdown-card').classList.toggle('hidden', !hasTime);
  document.getElementById('demo-exit').classList.toggle('hidden', !demo);
  if (hasTime) {
    const d = new Date(e.impact_utc); const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    document.getElementById('times').replaceChildren(
      el('dt', {}, t('common.ist')), el('dd', {}, fmt.date(d, 'Europe/Istanbul', { dateStyle: 'full', timeStyle: 'short' })),
      el('dt', {}, 'UTC'), el('dd', {}, fmt.date(d, 'UTC', { dateStyle: 'medium', timeStyle: 'short' })),
      el('dt', {}, t('common.local')), el('dd', {}, `${fmt.date(d, tz, { dateStyle: 'medium', timeStyle: 'short' })} (${tz})`));
    document.getElementById('uncertainty').textContent = e.impact_uncertainty_min ? t('live.uncertainty', { min: fmt.num(e.impact_uncertainty_min) }) : '';
  }
  const rc = document.getElementById('results-card'); rc.classList.toggle('hidden', !(e.status === 'completed' && e.results));
  if (e.results) document.getElementById('results').replaceChildren(el('p', {}, L(e.results.summary)), ...(e.results.links || []).map((l) => el('p', {}, el('a', { href: l.url, rel: 'noopener' }, L(l.label) || l.url))));
}
function countdown() {
  const e = E(); if (!e.impact_utc) return;
  const box = document.getElementById('countdown'); let ms = new Date(e.impact_utc).getTime() - Date.now();
  if (ms <= 0) { box.replaceChildren(el('p', { class: 'secondary' }, t('live.cd_past'))); return; }
  const units = [['live.cd_days', 86400000], ['live.cd_hours', 3600000], ['live.cd_min', 60000], ['live.cd_sec', 1000]];
  box.replaceChildren(...units.map(([k, u]) => { const v = Math.floor(ms / u); ms -= v * u; return el('div', { class: 'unit' }, el('div', { class: 'num' }, String(v).padStart(k === 'live.cd_days' ? 1 : 2, '0')), el('div', { class: 'lab' }, t(k))); }));
}
function moonView() {
  const e = E(); const d = e.impact_utc ? new Date(e.impact_utc) : new Date(); const g = moonGeometry(d);
  const markers = e.target ? [{ lat: e.target.lat, lon: e.target.lon, label: L(e.target.name) || '', selected: true }] : [];
  moon.set({ subEarth: g.subEarth, subSolar: g.subSolar, markers });
  document.getElementById('target-sub').textContent = e.target ? `${L(e.target.name)} · ${fmt.num(e.target.lat, 1)}°, ${fmt.num(e.target.lon, 1)}° · ${fmt.pct(g.illum)}` : t(e.impact_utc ? 'live.target_unknown' : 'live.target_none');
}
function lists() {
  const e = E();
  const streams = (e.streams || []);
  const sBox = document.getElementById('streams');
  if (!streams.length) sBox.replaceChildren(el('p', { class: 'muted' }, t('live.streams_none')));
  else {
    const first = streams[0]; const yt = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/.exec(first.url || '');
    sBox.replaceChildren(...(yt && e.status === 'live' ? [el('div', { class: 'embed' }, el('iframe', { src: `https://www.youtube-nocookie.com/embed/${yt[1]}`, title: first.name || 'stream', allow: 'autoplay; encrypted-media; picture-in-picture', allowfullscreen: true, loading: 'lazy' }))] : []),
      el('ul', { class: 'clean' }, streams.map((s) => el('li', {}, el('a', { href: s.url, rel: 'noopener' }, s.name || s.url), s.lang ? ` (${s.lang.toUpperCase()})` : ''))));
  }
  const w = e.watch_events || []; const wBox = document.getElementById('watch');
  wBox.replaceChildren(w.length ? el('ul', { class: 'clean' }, w.map((x) => el('li', {}, x.url ? el('a', { href: x.url, rel: 'noopener' }, L(x.name)) : el('b', {}, L(x.name)), x.place ? ` — ${x.place}` : ''))) : el('p', { class: 'muted' }, t('live.watch_none')));
  const u = [...(e.updates || [])].sort((a, b) => (a.time_utc < b.time_utc ? 1 : -1));
  document.getElementById('updates').replaceChildren(...(u.length ? u.map((x) => el('li', {}, el('time', { datetime: x.time_utc }, `${fmt.date(x.time_utc)} ${t('common.ist')}`), L(x))) : [el('li', { class: 'muted' }, t('live.updates_none'))]));
}
function timeline() {
  const e = E(); const T0 = e.impact_utc ? new Date(e.impact_utc).getTime() : null; const now = Date.now();
  const H = 3600000, D = 24 * H; const bounds = [-Infinity, -D, -H, 0, 5 * 60000, H, D, 35 * D, Infinity];
  let cur = -1; if (T0 !== null) { const dt = now - T0; for (let i = 0; i < 8; i++) if (dt >= bounds[i] && dt < bounds[i + 1]) cur = i; }
  document.getElementById('timeline').replaceChildren(...[1, 2, 3, 4, 5, 6, 7, 8].map((i) => el('li', { class: cur < 0 ? '' : i - 1 < cur ? 'done' : i - 1 === cur ? 'now' : '' },
    el('div', { class: 'when' }, t(`tl.${i}_w`)), el('div', { class: 'what' }, t(`tl.${i}_t`)), el('div', { class: 'detail' }, t(`tl.${i}_d`)))));
}
async function locWidget() {
  const e = E(); const presets = [];
  if (e.impact_utc) presets.push({ key: 'see.loc_event', date: new Date(e.impact_utc), default: true });
  presets.push({ key: 'see.loc_now', date: new Date(), default: !e.impact_utc });
  if (!loc) loc = await mountLocationWidget(document.getElementById('loc'), { presets }); else loc.setPresets(presets);
}
function all() { header(); countdown(); moonView(); lists(); timeline(); locWidget(); }
document.getElementById('demo-btn').addEventListener('click', () => { demo = true; const u = new URL(location.href); u.searchParams.set('demo', '1'); history.replaceState(null, '', u); all(); });
document.getElementById('demo-exit').addEventListener('click', () => { demo = false; const u = new URL(location.href); u.searchParams.delete('demo'); history.replaceState(null, '', u); all(); });
all();
timer = setInterval(countdown, 1000);
setInterval(async () => { if (!demo && EV.status === 'live') { try { EV = await reload('event.json'); all(); } catch (err) { /* keep last state */ } } else timeline(); }, 60000);
onLangChange(all);
