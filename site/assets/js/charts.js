// Small SVG charts: grouped horizontal bars, distribution with method markers, calendar strip.
// Thin marks, hairline grid, legend for >= 2 series, per-mark tooltips, table twin provided by callers.
import { el, tip, hideTip, fmt, loc } from './common.js';

const NS = 'http://www.w3.org/2000/svg';
function s(tag, attrs = {}, ...kids) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) n.setAttribute(k, v);
  kids.flat().forEach((c) => c !== null && c !== undefined && n.append(c.nodeType ? c : document.createTextNode(String(c))));
  return n;
}
function roundedBar(x, y, w, h, r = 4) {           // rounded data end (right), square at the baseline (left)
  r = Math.min(r, h / 2, w); if (w <= 0) return '';
  return `M${x},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x}Z`;
}
export function legend(items) {
  return el('div', { class: 'legend' }, items.map((it) => el('span', { class: 'key' }, el('span', { class: `sw ${it.shape || ''}`, style: `background:${it.shape === 'ring' ? 'transparent' : it.color};color:${it.color}` }), it.label)));
}
function observe(container, draw) { let w = 0; const ro = new ResizeObserver(() => { const nw = container.clientWidth; if (nw && Math.abs(nw - w) > 2) { w = nw; draw(); } }); ro.observe(container); draw(); return ro; }

/** Grouped horizontal bars. categories: [{key,label}], series: [{key,label,color}], value(c,s) in [0,1]. */
export function groupedBars(container, cfg) {
  const holder = el('div', { class: 'chart' }); container.replaceChildren(legend(cfg.series), holder);
  const draw = () => {
    const W = Math.max(300, holder.clientWidth || container.clientWidth || 600);
    const narrow = W < 520; const labelW = narrow ? 0 : Math.min(210, Math.round(W * 0.36)); const right = 46; const bar = 12, gap = 2, groupGap = narrow ? 34 : 20, top = narrow ? 22 : 8;
    const nS = cfg.series.length; const groupH = nS * bar + (nS - 1) * gap;
    const H = top + cfg.categories.length * (groupH + groupGap) + 24 - (narrow ? 14 : 0);
    const x0 = labelW, x1 = W - right, sx = (v) => x0 + v * (x1 - x0);
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': cfg.ariaLabel || '' });
    for (const tv of [0, 0.25, 0.5, 0.75, 1]) {
      svg.append(s('line', { class: tv === 0 ? 'axisline' : 'gridline', x1: sx(tv), x2: sx(tv), y1: top - 4, y2: H - 22 }));
      svg.append(s('g', { class: 'tick' }, s('text', { x: sx(tv), y: H - 6, 'text-anchor': 'middle' }, new Intl.NumberFormat(loc(), { style: 'percent' }).format(tv))));
    }
    cfg.categories.forEach((c, ci) => {
      const gy = top + ci * (groupH + groupGap);
      const lab = narrow ? s('text', { x: 0, y: gy - 7, style: 'fill:var(--text-1)' }) : s('text', { x: 0, y: gy + groupH / 2, 'dominant-baseline': 'middle' });
      lab.textContent = c.label; svg.append(lab);
      cfg.series.forEach((se, si) => {
        const v = cfg.value(c, se); const y = gy + si * (bar + gap);
        const dim = cfg.emphasis && cfg.emphasis !== se.key;
        const path = s('path', { d: roundedBar(x0, y, Math.max(1.5, sx(v) - x0), bar), fill: se.color, class: `mark${dim ? ' dim' : ''}`, tabindex: 0 });
        const show = (e) => tip(e, (t) => { t.append(el('strong', { text: fmt.pct(v) }), el('div', { class: 'tl-row' }, el('span', { class: 'tl-key', style: `background:${se.color}` }), se.label), el('div', {}, c.label)); });
        path.addEventListener('pointermove', show); path.addEventListener('focus', show); path.addEventListener('pointerleave', hideTip); path.addEventListener('blur', hideTip);
        svg.append(path);
        if (!dim) { const tx = s('text', { x: sx(v) + 6, y: y + bar / 2, 'dominant-baseline': 'middle', style: 'fill:var(--text-1);font-weight:600' }); tx.textContent = fmt.pct(v); svg.append(tx); }
      });
    });
    holder.replaceChildren(svg);
  };
  observe(holder, draw);
  return { redraw: draw };
}

/** Distribution (step line + 10 % wash) with vertical method markers. */
export function distribution(container, cfg) {
  const holder = el('div', { class: 'chart' }); container.replaceChildren(legend(cfg.series.map((x) => ({ ...x, shape: 'line' }))), holder);
  const draw = () => {
    const W = Math.max(300, holder.clientWidth || 640); const narrow = W < 560; const H = Math.round(Math.min(360, Math.max(270, W * 0.45)));
    const m = { l: 16, r: 16, t: narrow ? 80 : 58, b: 56 }; const xMin = cfg.xMin, xMax = cfg.xMax;
    const sx = (v) => m.l + (v - xMin) / (xMax - xMin) * (W - m.l - m.r);
    const yMax = Math.max(...cfg.series.flatMap((se) => se.values)) * 1.08; const sy = (v) => H - m.b - v / yMax * (H - m.t - m.b);
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': cfg.ariaLabel || '' });
    svg.append(s('line', { class: 'axisline', x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b }));
    for (let v = Math.ceil(xMin / 2) * 2; v <= xMax; v += 2) {
      svg.append(s('line', { class: 'gridline', x1: sx(v), x2: sx(v), y1: m.t - 6, y2: H - m.b }));
      svg.append(s('g', { class: 'tick' }, s('text', { x: sx(v), y: H - m.b + 16, 'text-anchor': 'middle' }, fmt.num(v))));
    }
    const ends = [s('text', { x: m.l, y: H - m.b + 34, 'text-anchor': 'start', style: 'fill:var(--text-3)' }), s('text', { x: W - m.r, y: H - m.b + 34, 'text-anchor': 'end', style: 'fill:var(--text-3)' })];
    ends[0].textContent = cfg.leftLabel || ''; ends[1].textContent = cfg.rightLabel || ''; svg.append(...ends);
    const axl = s('text', { x: (m.l + W - m.r) / 2, y: H - 4, 'text-anchor': 'middle', style: 'fill:var(--text-3)' }); axl.textContent = cfg.axisLabel || ''; svg.append(axl);
    // series
    cfg.series.forEach((se) => {
      let d = ''; const pts = [];
      se.values.forEach((v, i) => { const xa = cfg.start + i * cfg.step, xb = xa + cfg.step; if (xb < xMin || xa > xMax) return; pts.push([sx(Math.max(xa, xMin)), sy(v)], [sx(Math.min(xb, xMax)), sy(v)]); });
      pts.forEach(([x, y], i) => { d += (i ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1); });
      svg.append(s('path', { d: d + `L${pts[pts.length - 1][0]},${sy(0)}L${pts[0][0]},${sy(0)}Z`, fill: se.color, 'fill-opacity': 0.12, stroke: 'none' }));
      svg.append(s('path', { d, fill: 'none', stroke: se.color, 'stroke-width': 2, 'stroke-linejoin': 'round' }));
    });
    // markers (labels staggered in rows above the plot)
    const rows = narrow ? [-Infinity, -Infinity, -Infinity, -Infinity, -Infinity] : [-Infinity, -Infinity, -Infinity];
    [...cfg.markers].filter((mk) => !narrow || mk.essential).sort((a, b) => a.x - b.x).forEach((mk) => {
      if (mk.x < xMin || mk.x > xMax) return; const x = sx(mk.x);
      svg.append(s('line', { x1: x, x2: x, y1: m.t - 6, y2: H - m.b, stroke: 'var(--text-2)', 'stroke-width': 1, 'stroke-opacity': 0.55 }));
      const est = mk.label.length * (narrow ? 5.8 : 6.3) + 8; let row = rows.findIndex((r) => x - est / 2 > r); if (row < 0) row = rows.indexOf(Math.min(...rows));
      rows[row] = x + est / 2; const ty = 12 + row * 15;
      const tx = s('text', { x, y: ty, 'text-anchor': 'middle', style: 'fill:var(--text-1);font-size:11.5px' }); tx.textContent = mk.label; svg.append(tx);
      svg.append(s('line', { x1: x, x2: x, y1: ty + 4, y2: m.t - 6, stroke: 'var(--text-3)', 'stroke-width': 1, 'stroke-opacity': 0.4 }));
    });
    // crosshair + tooltip
    const cross = s('line', { y1: m.t - 6, y2: H - m.b, stroke: 'var(--text-1)', 'stroke-width': 1, 'stroke-opacity': 0, 'pointer-events': 'none' });
    const hit = s('rect', { x: m.l, y: m.t - 6, width: W - m.l - m.r, height: H - m.t - m.b + 6, fill: 'transparent' });
    hit.addEventListener('pointermove', (e) => {
      const b = svg.getBoundingClientRect(); const px = (e.clientX - b.left) * (W / b.width);
      const v = xMin + (px - m.l) / (W - m.l - m.r) * (xMax - xMin); const i = Math.floor((v - cfg.start) / cfg.step); if (i < 0) return;
      const xc = sx(cfg.start + (i + 0.5) * cfg.step); cross.setAttribute('x1', xc); cross.setAttribute('x2', xc); cross.setAttribute('stroke-opacity', 0.35);
      tip(e, (t) => { t.append(el('div', {}, `${fmt.num(cfg.start + i * cfg.step, 2)} – ${fmt.num(cfg.start + (i + 1) * cfg.step, 2)}`)); cfg.series.forEach((se) => t.append(el('div', { class: 'tl-row' }, el('span', { class: 'tl-key', style: `background:${se.color}` }), el('strong', { text: fmt.pct(se.values[i] ?? 0, 1) }), se.label))); });
    });
    hit.addEventListener('pointerleave', () => { cross.setAttribute('stroke-opacity', 0); hideTip(); });
    svg.append(cross, hit);
    holder.replaceChildren(svg);
  };
  observe(holder, draw);
  return { redraw: draw };
}

/** Calendar strip: one thin bar per observing window. */
export function calendarStrip(container, cfg) {
  const holder = el('div', { class: 'chart' }); const cap = el('div', { class: 'small muted', style: 'margin-top:4px' }, cfg.yLabel || '');
  container.replaceChildren(legend(cfg.series), holder, cap);
  const draw = () => {
    const W = Math.max(300, holder.clientWidth || 800); const H = 190; const m = { l: 26, r: 10, t: 30, b: 32 };
    const t0 = new Date(cfg.start + 'T00:00:00Z').getTime(), t1 = new Date(cfg.end + 'T00:00:00Z').getTime();
    const sx = (t) => m.l + (t - t0) / (t1 - t0) * (W - m.l - m.r); const yMax = 6; const sy = (v) => H - m.b - v / yMax * (H - m.t - m.b);
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': cfg.ariaLabel || '' });
    for (const v of [0, 2, 4, 6]) { svg.append(s('line', { class: v ? 'gridline' : 'axisline', x1: m.l, x2: W - m.r, y1: sy(v), y2: sy(v) })); svg.append(s('g', { class: 'tick' }, s('text', { x: m.l - 6, y: sy(v), 'text-anchor': 'end', 'dominant-baseline': 'middle' }, v))); }
    const mf = new Intl.DateTimeFormat(loc(), { month: 'short', year: 'numeric', timeZone: 'UTC' });
    const d = new Date(t0); d.setUTCDate(1);
    while (d.getTime() <= t1) {
      const x = sx(d.getTime());
      if (d.getUTCMonth() % 3 === 0) { svg.append(s('line', { class: 'gridline', x1: x, x2: x, y1: m.t, y2: H - m.b })); if (W > 520 || d.getUTCMonth() % 6 === 0) svg.append(s('g', { class: 'tick' }, s('text', { x, y: H - m.b + 16, 'text-anchor': 'middle' }, mf.format(d)))); }
      d.setUTCMonth(d.getUTCMonth() + 1);
    }
    const bw = Math.max(2, Math.min(5, (W - m.l - m.r) / 260));
    cfg.windows.forEach((w) => {
      const se = cfg.series.find((x) => x.key === w.session); const x = sx(new Date(w.date + 'T12:00:00Z').getTime());
      const r = s('rect', { x: x - bw / 2, y: sy(w.hours), width: bw, height: sy(0) - sy(w.hours), rx: 1.5, fill: se.color, class: 'mark', tabindex: 0 });
      const show = (e) => tip(e, (t) => cfg.tooltip(t, w, se)); r.addEventListener('pointermove', show); r.addEventListener('focus', show); r.addEventListener('pointerleave', hideTip); r.addEventListener('blur', hideTip);
      svg.append(r);
    });
    const mks = (cfg.marks || []).map((mk) => ({ ...mk, x: sx(new Date(mk.date).getTime()) })).sort((a, b) => a.x - b.x);
    const groups = []; mks.forEach((mk) => { const g = groups[groups.length - 1]; if (g && mk.x - g.x1 < 26) { g.labels.push(mk.label); g.x1 = mk.x; g.xs.push(mk.x); } else groups.push({ x0: mk.x, x1: mk.x, xs: [mk.x], labels: [mk.label] }); });
    groups.forEach((g) => {
      g.xs.forEach((x) => svg.append(s('path', { d: `M${x - 5},${m.t - 14}L${x + 5},${m.t - 14}L${x},${m.t - 6}Z`, fill: '#f5c76a' })));
      const tx = s('text', { x: (g.x0 + g.x1) / 2, y: m.t - 18, 'text-anchor': 'middle', style: 'fill:var(--text-1);font-size:11px;font-weight:600' }); tx.textContent = g.labels.join(' · '); svg.append(tx);
    });
    holder.replaceChildren(svg);
  };
  observe(holder, draw);
  return { redraw: draw };
}
