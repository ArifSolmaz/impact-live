import { initPage, load, t, L, fmt, el, onLangChange } from '../common.js';
import { MoonView } from '../moonview.js';
import { moonGeometry } from '../astro.js';

const meta = await initPage();
const [sc, ev, mags] = await Promise.all([load('scenarios.json'), load('event.json'), load('magnitudes.json')]);
const S1 = sc.scenarios.find((x) => x.id === 'S1');
const naked = mags.methods.find((m) => m.key === 'naked');

// hero Moon
const mv = new MoonView(document.getElementById('hero-moon'), { grid: false });
await mv.ready();
let mode = 'now'; const now = new Date();
function showMoon() {
  const cap = document.getElementById('moon-caption');
  if (mode === 'now') {
    const g = moonGeometry(now);
    mv.set({ subEarth: g.subEarth, subSolar: g.subSolar, markers: [] });
    cap.textContent = t('home.moon_caption_now', { pct: fmt.pctNum(g.illum), date: fmt.date(now, undefined, { dateStyle: 'medium', timeStyle: 'short' }) });
  } else {
    mv.set({ subEarth: { lat: S1.moon.subearth_lat, lon: S1.moon.subearth_lon }, subSolar: { lat: S1.moon.subsolar_lat, lon: S1.moon.subsolar_lon }, markers: [{ lat: S1.lat, lon: S1.lon, label: 'S1', selected: true }] });
    cap.textContent = t('home.moon_caption_s1', { date: fmt.date(S1.epoch_utc) });
  }
  document.getElementById('tab-now').setAttribute('aria-selected', String(mode === 'now'));
  document.getElementById('tab-s1').setAttribute('aria-selected', String(mode === 's1'));
}
document.getElementById('tab-now').addEventListener('click', () => { mode = 'now'; showMoon(); });
document.getElementById('tab-s1').addEventListener('click', () => { mode = 's1'; showMoon(); });

function status() {
  const badge = el('span', { class: `badge ${ev.status}` }, el('span', { class: 'dot', 'aria-hidden': 'true' }), t(`live.status.${ev.status}`));
  document.getElementById('status-badge').replaceChildren(badge);
  document.getElementById('status-title').textContent = t(`home.status_${ev.status}`);
  const body = document.getElementById('status-body'); body.replaceChildren(L(ev.mission_status) + ' ');
  if (ev.status !== 'planning' && ev.impact_utc) body.append(el('strong', {}, `${fmt.date(ev.impact_utc)} ${t('common.ist')}. `));
  body.append(el('a', { href: `live.html?lang=${document.documentElement.lang}` }, t('home.status_link')));
}

function stats() {
  const p = S1.p; const tiles = [
    [t('stat.peak_label'), `≈ ${fmt.num(S1.peakV.median, 0)} ${t('unit.mag')}`, t('stat.peak_sub', { thr: fmt.num(naked.limit, 0) })],
    [t('stat.net_label'), fmt.pct(p.B.wide.any), t('stat.net_sub', { a: fmt.pct(p.A.wide.any), c: fmt.pct(p.C.wide.any) })],
    [t('stat.light_label'), `${fmt.num(S1.moon.light_time_s, 1)} s`, t('stat.light_sub')],
    [t('stat.crater_label'), `${fmt.num(S1.crater_m[0])}–${fmt.num(S1.crater_m[2])} m`, t('stat.crater_sub')],
  ];
  document.getElementById('stats').replaceChildren(...tiles.map(([l, v, s]) => el('div', { class: 'stat' }, el('div', { class: 'label' }, l), el('div', { class: 'value' }, v), el('div', { class: 'sub' }, s))));
}
showMoon(); status(); stats();
onLangChange(() => { showMoon(); status(); stats(); });
