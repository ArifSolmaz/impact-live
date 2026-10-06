// Shared helpers: language, formatting, data loading, header/footer, tooltip, table views.
import { STRINGS } from './i18n.js';

const LANGS = ['tr', 'en'];
const listeners = [];
function initialLang() {
  const q = new URLSearchParams(location.search).get('lang');
  if (LANGS.includes(q)) { try { localStorage.setItem('lang', q); } catch (e) { /* storage unavailable */ } return q; }
  try { const s = localStorage.getItem('lang'); if (LANGS.includes(s)) return s; } catch (e) { /* storage unavailable */ }
  return 'tr';
}
export const state = { lang: initialLang() };
export const loc = () => (state.lang === 'tr' ? 'tr-TR' : 'en-GB');

export function t(key, vars) {
  let s = STRINGS[state.lang]?.[key];
  if (s === undefined) s = STRINGS.en[key];
  if (s === undefined) return key;
  if (vars && typeof s === 'string') s = s.replace(/\{(\w+)\}/g, (m, k) => (vars[k] !== undefined ? vars[k] : m));
  return s;
}
export function L(obj) { return obj ? (obj[state.lang] ?? obj.en ?? '') : ''; }

export function applyI18n(root = document) {
  root.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  root.querySelectorAll('[data-i18n-html]').forEach((el) => { el.innerHTML = t(el.dataset.i18nHtml); });
  root.querySelectorAll('[data-i18n-attr]').forEach((el) => {
    el.dataset.i18nAttr.split(';').forEach((pair) => { const [attr, key] = pair.split(':'); if (attr && key) el.setAttribute(attr.trim(), t(key.trim())); });
  });
  document.documentElement.lang = state.lang;
  const title = document.body.dataset.titleKey;
  document.title = (title ? t(title) + ' · ' : '') + t('site.name');
}
export function onLangChange(fn) { listeners.push(fn); }
export function setLang(l) {
  if (!LANGS.includes(l) || l === state.lang) return;
  state.lang = l;
  try { localStorage.setItem('lang', l); } catch (e) { /* storage unavailable */ }
  const u = new URL(location.href); u.searchParams.set('lang', l); history.replaceState(null, '', u);
  applyI18n(); renderChrome(); listeners.forEach((f) => f(l));
}

// ------------------------------------------------------------------ formatting
export const fmt = {
  num(x, d = 0) { return x === null || x === undefined || Number.isNaN(x) ? '–' : new Intl.NumberFormat(loc(), { minimumFractionDigits: d, maximumFractionDigits: d }).format(x); },
  pct(x, d = 0) {
    if (x === null || x === undefined || Number.isNaN(x)) return '–';
    if (x > 0 && x < 0.01 && d === 0) return (state.lang === 'tr' ? '<%1' : '<1%');
    if (x === 0) return (state.lang === 'tr' ? '≈%0' : '≈0%');
    return new Intl.NumberFormat(loc(), { style: 'percent', minimumFractionDigits: d, maximumFractionDigits: d }).format(x);
  },
  pctNum(x) { return new Intl.NumberFormat(loc(), { maximumFractionDigits: 0 }).format(x * 100); },
  date(d, tz = 'Europe/Istanbul', opts = { dateStyle: 'long', timeStyle: 'short' }) {
    return new Intl.DateTimeFormat(loc(), { ...opts, timeZone: tz }).format(typeof d === 'string' ? new Date(d) : d);
  },
  dateOnly(d, tz = 'Europe/Istanbul') { return fmt.date(d, tz, { dateStyle: 'medium' }); },
  time(d, tz = 'Europe/Istanbul') { return fmt.date(d, tz, { hour: '2-digit', minute: '2-digit' }); },
};

// ------------------------------------------------------------------ data
const cache = new Map();
export function load(name) {
  if (!cache.has(name)) cache.set(name, fetch(`data/${name}`, { cache: name === 'event.json' ? 'no-cache' : 'default' }).then((r) => { if (!r.ok) throw new Error(`${name}: ${r.status}`); return r.json(); }));
  return cache.get(name);
}
export function reload(name) { cache.delete(name); return load(name); }
export function loadImageData(src) {
  return new Promise((resolve, reject) => {
    const img = new Image(); img.decoding = 'async';
    img.onload = () => { const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight; const ctx = c.getContext('2d', { willReadFrequently: true }); ctx.drawImage(img, 0, 0); resolve({ w: c.width, h: c.height, data: ctx.getImageData(0, 0, c.width, c.height).data }); };
    img.onerror = () => reject(new Error('image ' + src)); img.src = src;
  });
}

export function repoUrl(meta) {
  if (meta && meta.repo) return meta.repo;
  const h = location.hostname;
  if (h.endsWith('.github.io')) {
    const user = h.split('.')[0]; const seg = location.pathname.split('/').filter(Boolean)[0];
    return seg && !seg.endsWith('.html') ? `https://github.com/${user}/${seg}` : `https://github.com/${user}/${user}.github.io`;
  }
  return null;
}

// ------------------------------------------------------------------ chrome (header/footer)
const LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><defs><radialGradient id="lg" cx="40%" cy="38%" r="70%"><stop offset="0" stop-color="#e9e6df"/><stop offset="1" stop-color="#8f8b84"/></radialGradient></defs><circle cx="16" cy="16" r="12.5" fill="#1b2130"/><path d="M16 3.5a12.5 12.5 0 0 1 0 25a8.5 12.5 0 0 0 0-25z" fill="url(#lg)"/><circle cx="10.2" cy="13.4" r="2.1" fill="#f5c76a"/><circle cx="10.2" cy="13.4" r="4.2" fill="none" stroke="#f5c76a" stroke-opacity=".45" stroke-width="1"/></svg>';
const PAGES = [['index.html', 'home', 'nav.home'], ['explore.html', 'explore', 'nav.explore'], ['see.html', 'see', 'nav.see'], ['live.html', 'live', 'nav.live'], ['science.html', 'science', 'nav.science']];
let meta = null, eventStatus = 'planning';
export function renderChrome() {
  const page = document.body.dataset.page;
  const header = document.getElementById('site-header');
  if (header) {
    header.className = 'site-header';
    header.innerHTML = `<div class="container">
      <a class="brand" href="index.html">${LOGO}<span><span>${esc(t('site.name'))}</span><small>${esc(t('site.tagline'))}</small></span></a>
      <button class="menu-btn" aria-expanded="false" aria-controls="nav">${esc(t('nav.menu'))}</button>
      <nav class="nav" id="nav" aria-label="main">
        ${PAGES.map(([href, id, key]) => `<a href="${href}"${id === page ? ' aria-current="page"' : ''}>${id === 'live' ? `<span class="live-dot${eventStatus === 'live' ? ' on' : ''}"></span>` : ''}${esc(t(key))}</a>`).join('')}
        <span class="lang" role="group" aria-label="Language / Dil">
          <button type="button" data-lang="tr" aria-pressed="${state.lang === 'tr'}">TR</button><button type="button" data-lang="en" aria-pressed="${state.lang === 'en'}">EN</button>
        </span>
      </nav></div>`;
    header.querySelectorAll('[data-lang]').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));
    const mb = header.querySelector('.menu-btn'), nav = header.querySelector('.nav');
    mb.addEventListener('click', () => { const open = nav.classList.toggle('open'); mb.setAttribute('aria-expanded', String(open)); });
    // keep the language in internal links
    header.querySelectorAll('a[href$=".html"]').forEach((a) => { a.href = `${a.getAttribute('href')}?lang=${state.lang}`; });
  }
  const footer = document.getElementById('site-footer');
  if (footer) {
    footer.className = 'site-footer';
    const repo = repoUrl(meta);
    footer.innerHTML = `<div class="container">
      <div class="disclaimer">${esc(t('footer.disclaimer'))}</div>
      <div>${t('footer.credits_html')}</div>
      <div class="row">${repo ? `<a href="${esc(repo)}">${esc(t('footer.code'))}</a>` : `<span>${esc(t('footer.code'))}</span>`}
        <span class="spacer"></span>${meta ? `<span>${esc(t('footer.author', { author: meta.author, affiliation: L(meta.affiliation) }))}</span><span>${esc(t('footer.cutoff', { date: fmt.dateOnly(meta.evidence_cutoff + 'T12:00:00Z') }))}</span>` : ''}</div>
    </div>`;
  }
  document.querySelectorAll('a[data-keep-lang]').forEach((a) => { const base = a.getAttribute('href').split('?')[0]; a.href = `${base}?lang=${state.lang}`; });
}
export async function initPage() {
  applyI18n(); renderChrome();
  try { meta = await load('meta.json'); } catch (e) { meta = null; }
  try { const ev = await load('event.json'); eventStatus = ev.status; } catch (e) { /* no event file */ }
  renderChrome();
  return meta;
}

// ------------------------------------------------------------------ small DOM helpers
export function esc(s) { return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
export function el(tag, attrs = {}, ...children) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v; else if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? '' : v);
  }
  children.flat().forEach((c) => { if (c !== null && c !== undefined) n.append(c.nodeType ? c : document.createTextNode(String(c))); });
  return n;
}

// tooltip (values lead, labels follow; built with textContent)
let tipEl = null;
export function tip(evt, build) {
  if (!tipEl) { tipEl = el('div', { class: 'tooltip', role: 'status' }); document.body.append(tipEl); }
  tipEl.replaceChildren(); build(tipEl);
  const pad = 14, r = tipEl.getBoundingClientRect();
  let x = (evt.clientX ?? 0) + pad, y = (evt.clientY ?? 0) + pad;
  if (evt.target && evt.clientX === undefined) { const b = evt.target.getBoundingClientRect(); x = b.right + pad; y = b.top; }
  if (x + r.width > innerWidth - 8) x = Math.max(8, (evt.clientX ?? x) - r.width - pad);
  if (y + r.height > innerHeight - 8) y = Math.max(8, innerHeight - r.height - 8);
  tipEl.style.left = `${x}px`; tipEl.style.top = `${y}px`; tipEl.classList.add('show');
}
export function hideTip() { if (tipEl) tipEl.classList.remove('show'); }

// accessible table twin for a chart
export function tableToggle(container, getRows) {
  const btn = el('button', { class: 'btn small table-toggle', type: 'button', 'aria-expanded': 'false' }, t('common.table_show'));
  const holder = el('div', { class: 'hidden' });
  btn.addEventListener('click', () => {
    const open = holder.classList.toggle('hidden') === false;
    btn.setAttribute('aria-expanded', String(open)); btn.textContent = t(open ? 'common.table_hide' : 'common.table_show');
    if (open) render();
  });
  function render() {
    const { head, rows } = getRows();
    const table = el('table', { class: 'data-table' });
    const thead = el('thead', {}, el('tr', {}, head.map((h, i) => el('th', { class: i ? 'num' : '' }, h))));
    const tbody = el('tbody', {}, rows.map((r) => el('tr', {}, r.map((c, i) => el('td', { class: i ? 'num' : '' }, c)))));
    table.append(thead, tbody); holder.replaceChildren(table);
  }
  container.append(btn, holder);
  return { refresh() { if (!holder.classList.contains('hidden')) render(); btn.textContent = t(holder.classList.contains('hidden') ? 'common.table_show' : 'common.table_hide'); } };
}

export function classBadge(cls) {
  return el('span', { class: `badge ${cls}` }, el('span', { class: 'dot', 'aria-hidden': 'true' }), t(`class.${cls}`));
}
export function storageGet(key, fallback) { try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch (e) { return fallback; } }
export function storageSet(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* ignore */ } }
