// "Is the Moon up where I am?" widget: geolocation or city search + time -> Moon/Sun altitude and a verdict.
import { t, fmt, el, load, state, storageGet, storageSet, onLangChange, esc } from './common.js';
import { altaz, illumination } from './astro.js';

const pad = (n) => String(n).padStart(2, '0');
const toLocalInput = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
function timeLine(d) {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone; const parts = [fmt.date(d, tz)];
  if (tz !== 'Europe/Istanbul') parts.push(`${fmt.time(d, 'Europe/Istanbul')} ${t('common.ist')}`);
  parts.push(`${fmt.time(d, 'UTC')} UTC`); return parts.join(' · ');
}
const fromLocalInput = (v) => { const d = new Date(v); return Number.isNaN(d.getTime()) ? null : d; };

export async function mountLocationWidget(root, { presets = [] } = {}) {
  const cities = (await load('cities.json')).cities;
  let place = storageGet('impact-live-place', null);
  if (!place) { const ist = cities.find((c) => c[1] === 'TR'); if (ist) place = { name: `${ist[0]}, ${ist[1]}`, lat: ist[2], lon: ist[3] }; }
  let when = presets.find((p) => p.default)?.date || new Date();
  let custom = false;   // true once the user picks a time; until then a new default (announced time, demo) replaces it

  const status = el('div', { class: 'small muted', 'aria-live': 'polite' });
  const btnGeo = el('button', { class: 'btn small', type: 'button' });
  const listId = 'citylist-' + Math.random().toString(36).slice(2, 7);
  const search = el('input', { type: 'search', list: listId, autocomplete: 'off' });
  const datalist = el('datalist', { id: listId }, cities.map((c) => el('option', { value: `${c[0]}, ${c[1]}` })));
  const time = el('input', { type: 'datetime-local', value: toLocalInput(when) });
  const presetRow = el('div', { class: 'row' });
  const out = el('div', { class: 'loc-result' });
  root.replaceChildren(
    el('div', { class: 'grid two' },
      el('label', { class: 'field' }, el('span', { 'data-k': 'see.loc_place' }), el('div', { class: 'row' }, search, btnGeo), datalist),
      el('label', { class: 'field' }, el('span', { 'data-k': 'see.loc_time' }), time)),
    presetRow, status, out, el('p', { class: 'small muted', style: 'margin:12px 0 0', 'data-k': 'see.loc_note' }));

  function labels() {
    root.querySelectorAll('[data-k]').forEach((n) => { n.textContent = t(n.dataset.k); });
    btnGeo.textContent = t('see.loc_use'); search.placeholder = t('see.loc_search');
    presetRow.replaceChildren(...presets.map((p) => el('button', { class: 'btn small', type: 'button', 'aria-pressed': String(Math.abs(when.getTime() - p.date.getTime()) < 60000), onclick: () => { when = p.date; custom = !p.default; time.value = toLocalInput(when); labels(); } }, t(p.key))));
    if (place) search.value = place.name;
    compute();
  }
  btnGeo.addEventListener('click', () => {
    if (!navigator.geolocation) { status.textContent = t('see.loc_err'); return; }
    status.textContent = t('common.loading');
    navigator.geolocation.getCurrentPosition((pos) => {
      place = { name: `${pos.coords.latitude.toFixed(2)}°, ${pos.coords.longitude.toFixed(2)}°`, lat: pos.coords.latitude, lon: pos.coords.longitude };
      status.textContent = ''; search.value = place.name; storageSet('impact-live-place', place); compute();
    }, () => { status.textContent = t('see.loc_err'); }, { timeout: 10000, maximumAge: 600000 });
  });
  search.addEventListener('change', () => {
    const v = search.value.trim().toLocaleLowerCase(state.lang === 'tr' ? 'tr-TR' : 'en-GB');
    const c = cities.find((x) => `${x[0]}, ${x[1]}`.toLocaleLowerCase(state.lang === 'tr' ? 'tr-TR' : 'en-GB') === v) || cities.find((x) => x[0].toLocaleLowerCase('tr-TR').startsWith(v.split(',')[0]));
    if (c) { place = { name: `${c[0]}, ${c[1]}`, lat: c[2], lon: c[3] }; storageSet('impact-live-place', place); search.value = place.name; compute(); }
  });
  time.addEventListener('change', () => { const d = fromLocalInput(time.value); if (d) { when = d; custom = true; labels(); } });

  function compute() {
    if (!place) { out.replaceChildren(el('p', { class: 'muted' }, t('see.loc_choose'))); return; }
    const m = altaz('moon', when, place.lat, place.lon), sun = altaz('sun', when, place.lat, place.lon), ill = illumination(when);
    let verdict = 'see.v_good', cls = 'yes';
    if (m.alt <= 0) { verdict = 'see.v_below'; cls = 'no'; } else if (sun.alt > -0.83) { verdict = 'see.v_day'; cls = 'no'; } else if (sun.alt > -12) { verdict = 'see.v_twilight'; cls = 'no'; } else if (m.alt < 20) { verdict = 'see.v_low'; cls = 'no'; }
    const dirs = t('see.dir'); const dir = dirs[Math.round(((m.az % 360) + 360) % 360 / 45) % 8];
    out.replaceChildren(dome(m, dirs),
      el('div', {},
        el('div', { class: 'verdict' }, el('span', { class: `result-pill ${cls}` }, t(verdict))),
        el('dl', { class: 'kv' },
          el('dt', {}, t('see.loc_place')), el('dd', {}, place.name),
          el('dt', {}, t('see.loc_time')), el('dd', {}, timeLine(when)),
          el('dt', {}, t('see.loc_moon_alt')), el('dd', {}, `${fmt.num(m.alt, 1)}°`),
          el('dt', {}, t('see.loc_moon_az')), el('dd', {}, `${fmt.num(m.az, 0)}° (${dir})`),
          el('dt', {}, t('see.loc_sun_alt')), el('dd', {}, `${fmt.num(sun.alt, 1)}°`),
          el('dt', {}, t('see.loc_phase')), el('dd', {}, fmt.pct(ill)))));
  }
  function dome(m, dirs) {
    const NS = 'http://www.w3.org/2000/svg'; const S = 150, R = 54, c = S / 2;
    const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${S} ${S}`); svg.setAttribute('width', S); svg.setAttribute('role', 'img');
    const r = Math.max(0, Math.min(1, (90 - m.alt) / 90)) * R; const a = (m.az - 90) * Math.PI / 180; const below = m.alt <= 0;
    svg.innerHTML = `<circle cx="${c}" cy="${c}" r="${R}" fill="#0f1a2e" stroke="#3a4252"/><circle cx="${c}" cy="${c}" r="${R * 70 / 90}" fill="none" stroke="#232a38"/>`
      + [[0, 'N'], [90, 'E'], [180, 'S'], [270, 'W']].map(([az], i) => { const aa = (az - 90) * Math.PI / 180; return `<text x="${c + Math.cos(aa) * (R + 9)}" y="${c + Math.sin(aa) * (R + 9) + 4}" text-anchor="middle" font-size="10" fill="#8a90a0">${esc(dirs[i * 2])}</text>`; }).join('')
      + `<circle cx="${c + Math.cos(a) * (below ? R : r)}" cy="${c + Math.sin(a) * (below ? R : r)}" r="7" fill="${below ? 'none' : '#e8e4da'}" stroke="#e8e4da" stroke-dasharray="${below ? '2 2' : 'none'}"/>`;
    return svg;
  }
  onLangChange(labels);
  labels();
  return { setPresets(p) {
    presets = p;
    if (!custom) { const d = p.find((x) => x.default)?.date; if (d) { when = d; time.value = toLocalInput(when); } }
    labels();
  } };
}
