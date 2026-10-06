// Equirectangular Earth map: land, Türkiye, night shading, where the Moon is high in a dark sky, observatories.
import { load } from './common.js';
import { altitudeFromSubpoint } from './astro.js';

export class EarthMap {
  constructor(canvas, { latMin = -58, latMax = 76 } = {}) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.latMin = latMin; this.latMax = latMax;
    this.state = { sun: null, moon: null, siteStatus: {} }; this.hoverCb = null;
    this._ro = new ResizeObserver(() => this.render()); this._ro.observe(canvas);
    canvas.addEventListener('pointermove', (e) => this._hover(e));
    canvas.addEventListener('pointerleave', () => this.hoverCb && this.hoverCb(null, null));
  }
  async ready() { [this.world, this.sites] = await Promise.all([load('world.json'), load('sites.json').then((d) => d.sites)]); return this; }
  set(state) { Object.assign(this.state, state); this.render(); }
  onHover(cb) { this.hoverCb = cb; }
  xy(lat, lon) {
    const W = this.canvas.clientWidth, H = this.canvas.clientHeight;
    return { x: (lon + 180) / 360 * W, y: (this.latMax - lat) / (this.latMax - this.latMin) * H };
  }
  render() {
    if (!this.world) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2); const W = this.canvas.clientWidth, H = this.canvas.clientHeight; if (!W || !H) return;
    this.canvas.width = Math.round(W * dpr); this.canvas.height = Math.round(H * dpr);
    const ctx = this.ctx; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#0a1120'; ctx.fillRect(0, 0, W, H);
    // graticule
    ctx.strokeStyle = 'rgba(140,170,220,0.08)'; ctx.lineWidth = 1; ctx.beginPath();
    for (let lo = -150; lo < 180; lo += 30) { const a = this.xy(this.latMax, lo), b = this.xy(this.latMin, lo); ctx.moveTo(Math.round(a.x) + .5, 0); ctx.lineTo(Math.round(b.x) + .5, H); }
    for (let la = -30; la <= 60; la += 30) { const a = this.xy(la, -180); ctx.moveTo(0, Math.round(a.y) + .5); ctx.lineTo(W, Math.round(a.y) + .5); }
    ctx.stroke();
    // land
    const path = (rings) => { ctx.beginPath(); for (const r of rings) { r.forEach(([lo, la], i) => { const p = this.xy(la, lo); i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y); }); ctx.closePath(); } };
    path(this.world.land); ctx.fillStyle = '#1d2636'; ctx.fill(); ctx.strokeStyle = 'rgba(190,205,230,0.18)'; ctx.lineWidth = 0.6; ctx.stroke();
    path(this.world.turkey); ctx.fillStyle = '#2a3346'; ctx.fill(); ctx.strokeStyle = 'rgba(245,199,106,0.85)'; ctx.lineWidth = 1.1; ctx.stroke();
    // night and Moon visibility layers on a coarse grid, drawn smoothly
    const { sun, moon } = this.state;
    if (sun && moon) {
      const gw = 240, gh = Math.round(gw * H / W); const g = document.createElement('canvas'); g.width = gw; g.height = gh;
      const gctx = g.getContext('2d'); const im = gctx.createImageData(gw, gh); const d = im.data;
      for (let j = 0; j < gh; j++) {
        const lat = this.latMax - (j + 0.5) / gh * (this.latMax - this.latMin);
        for (let i = 0; i < gw; i++) {
          const lon = -180 + (i + 0.5) / gw * 360; const o = (j * gw + i) * 4;
          const sa = altitudeFromSubpoint(lat, lon, sun), ma = altitudeFromSubpoint(lat, lon, moon);
          const night = sa >= 0 ? 0 : sa <= -18 ? 0.6 : 0.6 * (-sa / 18);
          const good = ma >= 20 && sa <= -12, low = !good && ma > 0 && sa < -3;
          const wash = good ? 0.62 : low ? 0.24 : 0;                 // blue wash composited over the black night layer
          const a = wash + night * (1 - wash); const k = a > 0 ? wash / a : 0;
          d[o] = 57 * k; d[o + 1] = 135 * k; d[o + 2] = 229 * k; d[o + 3] = Math.round(a * 255);
        }
      }
      gctx.putImageData(im, 0, 0); ctx.imageSmoothingEnabled = true; ctx.drawImage(g, 0, 0, W, H);
      path(this.world.turkey); ctx.strokeStyle = 'rgba(245,199,106,0.85)'; ctx.lineWidth = 1.1; ctx.stroke();
      // overhead points
      this._glyph(ctx, sun, 'sun'); this._glyph(ctx, moon, 'moon');
    }
    // observatories
    this._hits = [];
    for (const s of this.sites) {
      const p = this.xy(s.lat, s.lon); const st = this.state.siteStatus[s.id];
      const avail = st ? st.available : false;
      ctx.beginPath(); ctx.arc(p.x, p.y, avail ? 4.2 : 3.2, 0, Math.PI * 2);
      if (avail) { ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = '#0a1120'; ctx.stroke(); }
      else { ctx.lineWidth = 1.4; ctx.strokeStyle = 'rgba(190,198,215,0.7)'; ctx.stroke(); }
      this._hits.push({ s, st, x: p.x, y: p.y });
    }
  }
  _glyph(ctx, sp, kind) {
    if (sp.lat > this.latMax || sp.lat < this.latMin) return;
    const p = this.xy(sp.lat, sp.lon); ctx.save();
    if (kind === 'sun') {
      ctx.strokeStyle = '#fab219'; ctx.fillStyle = '#fab219'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(p.x, p.y, 4.5, 0, Math.PI * 2); ctx.fill();
      for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; ctx.beginPath(); ctx.moveTo(p.x + Math.cos(a) * 7, p.y + Math.sin(a) * 7); ctx.lineTo(p.x + Math.cos(a) * 10, p.y + Math.sin(a) * 10); ctx.stroke(); }
    } else {
      ctx.fillStyle = '#e8e4da'; ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#0a1120'; ctx.beginPath(); ctx.arc(p.x - 2.6, p.y - 1, 5.2, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#e8e4da'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();
  }
  _hover(e) {
    if (!this.hoverCb || !this._hits) return;
    const b = this.canvas.getBoundingClientRect(); const x = e.clientX - b.left, y = e.clientY - b.top;
    let best = null, bd = 12;
    for (const h of this._hits) { const dd = Math.hypot(h.x - x, h.y - y); if (dd < bd) { bd = dd; best = h; } }
    this.hoverCb(best, e);
  }
}
