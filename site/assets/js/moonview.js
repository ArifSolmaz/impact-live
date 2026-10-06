// Orthographic Moon renderer (canvas). Real albedo map + Lommel-Seeliger shading, earthshine,
// optional heat layer, graticule, markers, labels and a flash overlay. North up, lunar east to the right.
import { loadImageData } from './common.js';

const D2R = Math.PI / 180;
let TEXTURE = null;
function texture(src) { if (!TEXTURE) TEXTURE = loadImageData(src); return TEXTURE; }

export class MoonView {
  constructor(canvas, opts = {}) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d');
    this.opts = { texture: 'assets/img/moon_texture.jpg', earthshine: 0.045, grid: true, labels: false, zoom: 1, center: null, heat: null, heatRGB: [57, 135, 229], ...opts };
    this.state = { subEarth: { lat: 0, lon: 0 }, subSolar: { lat: 0, lon: 90 }, markers: [], features: null, flash: null };
    this.base = document.createElement('canvas');
    this.hoverCb = null; this.size = 0;
    this._ro = new ResizeObserver(() => this.render()); this._ro.observe(canvas);
    canvas.addEventListener('pointermove', (e) => this._hover(e));
    canvas.addEventListener('pointerleave', () => this.hoverCb && this.hoverCb(null, null));
  }
  async ready() { this.tex = await texture(this.opts.texture); return this; }
  set(state = {}, opts = {}) { Object.assign(this.state, state); Object.assign(this.opts, opts); this.render(); }
  onHover(cb) { this.hoverCb = cb; }

  _frame() {
    const se = this.state.subEarth; const l0 = se.lon * D2R, p0 = se.lat * D2R;
    const C = [Math.cos(p0) * Math.cos(l0), Math.cos(p0) * Math.sin(l0), Math.sin(p0)];
    const E = [-Math.sin(l0), Math.cos(l0), 0];
    const N = [C[1] * E[2] - C[2] * E[1], C[2] * E[0] - C[0] * E[2], C[0] * E[1] - C[1] * E[0]];
    return { C, E, N };
  }
  /** disk coordinates (x right, y up, z towards Earth) of a selenographic point */
  disk(lat, lon) {
    const { C, E, N } = this._frame(); const la = lat * D2R, lo = lon * D2R;
    const p = [Math.cos(la) * Math.cos(lo), Math.cos(la) * Math.sin(lo), Math.sin(la)];
    return { x: p[0] * E[0] + p[1] * E[1] + p[2] * E[2], y: p[0] * N[0] + p[1] * N[1] + p[2] * N[2], z: p[0] * C[0] + p[1] * C[1] + p[2] * C[2] };
  }
  _view() {
    const k = Math.max(1, this.opts.zoom || 1); let cx = 0, cy = 0;
    if (k > 1 && this.opts.center) { const d = this.disk(this.opts.center.lat, this.opts.center.lon); cx = d.x; cy = d.y; }
    return { k, cx, cy };
  }
  /** CSS-pixel position of a selenographic point */
  project(lat, lon) {
    const d = this.disk(lat, lon); const { k, cx, cy } = this._view(); const W = this.canvas.clientWidth, H = this.canvas.clientHeight;
    const R = Math.min(W, H) / 2;
    return { x: W / 2 + (d.x - cx) * k * R * 0.985, y: H / 2 - (d.y - cy) * k * R * 0.985, visible: d.z > 0, z: d.z };
  }

  render() {
    if (!this.tex) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = this.canvas.clientWidth, H = this.canvas.clientHeight; if (!W || !H) return;
    const PW = Math.round(W * dpr), PH = Math.round(H * dpr);
    if (this.canvas.width !== PW || this.canvas.height !== PH) { this.canvas.width = PW; this.canvas.height = PH; }
    this.base.width = PW; this.base.height = PH;
    const bctx = this.base.getContext('2d'); const img = bctx.createImageData(PW, PH); const out = img.data;
    const { C, E, N } = this._frame(); const ss = this.state.subSolar;
    const sl = ss.lon * D2R, sp = ss.lat * D2R; const S = [Math.cos(sp) * Math.cos(sl), Math.cos(sp) * Math.sin(sl), Math.sin(sp)];
    const tex = this.tex, TW = tex.w, TH = tex.h, TD = tex.data;
    const heat = this.opts.heat, HR = this.opts.heatRGB;
    const es = this.opts.earthshine; const { k, cx, cy } = this._view();
    const R = Math.min(PW, PH) / 2 * 0.985; const ox = PW / 2, oy = PH / 2; const edge = 1.2 / (R * k);
    for (let j = 0; j < PH; j++) {
      const y = cy + (oy - (j + 0.5)) / (R * k);
      for (let i = 0; i < PW; i++) {
        const x = cx + ((i + 0.5) - ox) / (R * k);
        const r2 = x * x + y * y; const o = (j * PW + i) * 4;
        if (r2 >= 1) { out[o + 3] = 0; continue; }
        const z = Math.sqrt(1 - r2);
        const px = x * E[0] + y * N[0] + z * C[0], py = x * E[1] + y * N[1] + z * C[1], pz = x * E[2] + y * N[2] + z * C[2];
        const lat = Math.asin(pz > 1 ? 1 : pz < -1 ? -1 : pz), lon = Math.atan2(py, px);
        // bilinear albedo sample
        let u = (lon / Math.PI * 0.5 + 0.5) * TW - 0.5, v = (0.5 - lat / Math.PI) * TH - 0.5;
        if (u < 0) u += TW; const u0 = Math.floor(u), v0 = Math.max(0, Math.min(TH - 2, Math.floor(v)));
        const fu = u - u0, fv = Math.max(0, Math.min(1, v - v0)); const u1 = (u0 + 1) % TW, uu0 = u0 % TW;
        const a00 = TD[(v0 * TW + uu0) * 4], a10 = TD[(v0 * TW + u1) * 4], a01 = TD[((v0 + 1) * TW + uu0) * 4], a11 = TD[((v0 + 1) * TW + u1) * 4];
        const alb = ((a00 * (1 - fu) + a10 * fu) * (1 - fv) + (a01 * (1 - fu) + a11 * fu) * fv) / 255;
        const mu0 = px * S[0] + py * S[1] + pz * S[2];
        const m0 = mu0 > 0 ? mu0 : 0; let lit = 2 * m0 / (m0 + z + 1e-6); if (lit > 1) lit = 1;
        let s = (mu0 + 0.01) / 0.035; s = s < 0 ? 0 : s > 1 ? 1 : s; s = s * s * (3 - 2 * s);
        let val = alb * 1.25 * (lit * s * 0.92 + es); val = val > 1 ? 1 : Math.pow(val, 0.91);
        let rr = val * 255, gg = val * 251, bb = val * 245;
        if (heat) {
          const hu = Math.min(heat.w - 1, Math.max(0, Math.floor((lon / Math.PI * 0.5 + 0.5) * heat.w)));
          const hv = Math.min(heat.h - 1, Math.max(0, Math.floor((0.5 - lat / Math.PI) * heat.h)));
          const hval = heat.data[(hv * heat.w + hu) * 4] / 255;
          const a = 0.75 * Math.pow(hval, 1.4);
          if (a > 0.03) { rr = rr * (1 - a) + HR[0] * a; gg = gg * (1 - a) + HR[1] * a; bb = bb * (1 - a) + HR[2] * a; }
        }
        const rad = Math.sqrt(r2); const aa = rad > 1 - edge ? Math.max(0, (1 - rad) / edge) : 1;
        out[o] = rr; out[o + 1] = gg; out[o + 2] = bb; out[o + 3] = aa * 255;
      }
    }
    bctx.putImageData(img, 0, 0);
    this.compose();
  }

  compose() {
    const ctx = this.ctx, dpr = this.canvas.width / Math.max(1, this.canvas.clientWidth);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.drawImage(this.base, 0, 0); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (this.opts.grid) this._grid(ctx);
    if (this.opts.labels && this.state.features) this._labels(ctx);
    this._markers(ctx);
    if (this.state.flash) this._flash(ctx, this.state.flash);
  }
  _grid(ctx) {
    ctx.save(); ctx.strokeStyle = 'rgba(160, 190, 255, 0.16)'; ctx.lineWidth = 1;
    const line = (pts) => { let pen = false; ctx.beginPath(); for (const [la, lo] of pts) { const p = this.project(la, lo); if (p.z > 0.02) { pen ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y); pen = true; } else pen = false; } ctx.stroke(); };
    for (let lo = -180; lo < 180; lo += 30) { const pts = []; for (let la = -90; la <= 90; la += 3) pts.push([la, lo]); line(pts); }
    for (let la = -60; la <= 60; la += 30) { const pts = []; for (let lo = -180; lo <= 180; lo += 3) pts.push([la, lo]); line(pts); }
    ctx.restore();
  }
  _text(ctx, txt, x, y, { size = 11, color = 'rgba(235,240,250,0.92)', align = 'center', weight = 500 } = {}) {
    ctx.save(); ctx.font = `${weight} ${size}px system-ui, -apple-system, Segoe UI, sans-serif`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round'; ctx.miterLimit = 2;
    ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(0,0,0,0.75)'; ctx.strokeText(txt, x, y); ctx.fillStyle = color; ctx.fillText(txt, x, y); ctx.restore();
  }
  _labels(ctx) {
    const f = this.state.features;
    for (const m of f.maria.slice(0, 14)) { const p = this.project(m.lat, m.lon); if (p.z > 0.3) this._text(ctx, m.name, p.x, p.y, { size: 10, color: 'rgba(200,215,240,0.75)' }); }
    for (const l of f.landing.filter((x) => x.name.startsWith('Apollo'))) {
      const p = this.project(l.lat, l.lon); if (p.z <= 0.15) continue;
      ctx.save(); ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.beginPath(); ctx.moveTo(p.x, p.y - 4); ctx.lineTo(p.x + 3.5, p.y + 2.5); ctx.lineTo(p.x - 3.5, p.y + 2.5); ctx.closePath(); ctx.fill(); ctx.restore();
      this._text(ctx, l.name.replace('Apollo ', 'A'), p.x + 6, p.y, { size: 9.5, align: 'left', color: 'rgba(255,255,255,0.8)' });
    }
  }
  _markers(ctx) {
    this._hits = [];
    const ms = [...this.state.markers].sort((a, b) => (a.selected ? 1 : 0) - (b.selected ? 1 : 0));
    for (const m of ms) {
      const p = this.project(m.lat, m.lon); if (!p.visible) continue;
      this._hits.push({ m, x: p.x, y: p.y });
      ctx.save();
      if (m.target) {
        ctx.strokeStyle = 'rgba(245,199,106,0.55)'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(p.x, p.y, 13, 0, Math.PI * 2); ctx.stroke();
      } else if (m.selected) {
        ctx.shadowColor = 'rgba(245,199,106,0.9)'; ctx.shadowBlur = 12; ctx.strokeStyle = '#f5c76a'; ctx.lineWidth = 2.2;
        ctx.beginPath(); ctx.arc(p.x, p.y, 9, 0, Math.PI * 2); ctx.stroke(); ctx.shadowBlur = 0;
        ctx.beginPath(); ctx.moveTo(p.x - 15, p.y); ctx.lineTo(p.x - 11, p.y); ctx.moveTo(p.x + 11, p.y); ctx.lineTo(p.x + 15, p.y);
        ctx.moveTo(p.x, p.y - 15); ctx.lineTo(p.x, p.y - 11); ctx.moveTo(p.x, p.y + 11); ctx.lineTo(p.x, p.y + 15); ctx.stroke();
        if (m.label) this._text(ctx, m.label, p.x, p.y - 23, { size: 12.5, weight: 650, color: '#ffe3a6' });
      } else {
        ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.strokeStyle = 'rgba(0,0,0,0.65)'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2); ctx.stroke(); ctx.fill();
        if (m.label) this._text(ctx, m.label, p.x + 7, p.y - 7, { size: 10.5, align: 'left', color: 'rgba(235,240,250,0.85)' });
      }
      ctx.restore();
    }
  }
  _flash(ctx, f) {
    const p = this.project(f.lat, f.lon); if (!p.visible || f.intensity <= 0) return;
    const r = (f.radius || 10) * (0.6 + 0.4 * f.intensity);
    const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 3);
    g.addColorStop(0, `rgba(255,255,255,${Math.min(1, f.intensity)})`); g.addColorStop(0.18, `rgba(255,236,190,${0.85 * f.intensity})`); g.addColorStop(1, 'rgba(255,220,150,0)');
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, r * 3, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  _hover(e) {
    if (!this.hoverCb || !this._hits) return;
    const b = this.canvas.getBoundingClientRect(); const x = e.clientX - b.left, y = e.clientY - b.top;
    let best = null, bd = 14;
    for (const h of this._hits) { const d = Math.hypot(h.x - x, h.y - y); if (d < bd) { bd = d; best = h.m; } }
    this.hoverCb(best, e);
  }
}
