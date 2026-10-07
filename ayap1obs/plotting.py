"""Figure helpers (matplotlib).  Palette follows the project data-viz conventions: fixed categorical order,
single-hue sequential ramps, blue-grey-red diverging; no rainbow maps; every figure carries an evidence tag
('OBSERVED', 'SIMULATION', 'HYPOTHETICAL SCENARIO', 'SYNTHETIC TERRAIN') in its caption/title."""
from __future__ import annotations
import os, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import healpy as hp
import shapefile

# Figures use the Inter typeface shipped in data/fonts (SIL Open Font License), so that they look the same on every
# computer instead of depending on the fonts and matplotlib settings installed locally. matplotlib's bundled
# DejaVu Sans supplies any glyph Inter lacks.
_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'fonts')
for _f in ('Inter-Regular.otf', 'Inter-Italic.otf'):
    if os.path.exists(os.path.join(_FONT_DIR, _f)):
        font_manager.fontManager.addfont(os.path.join(_FONT_DIR, _f))

CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
SEQ_BLUE = LinearSegmentedColormap.from_list('seqblue', ['#f4f8fd', '#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b'])
SEQ_ORANGE = LinearSegmentedColormap.from_list('seqorange', ['#fff5ef', '#fbd4c0', '#f5ab85', '#eb6834', '#b84a1f', '#7a2f12'])
DIV = LinearSegmentedColormap.from_list('div', ['#0d366b', '#3987e5', '#f0efec', '#e34948', '#7a1b1a'])
TEXT = '#0b0b0b'; TEXT2 = '#52514e'; GRID = '#dcdbd6'
plt.rcdefaults()  # ignore any local matplotlibrc or style customisation
plt.rcParams.update({'font.family': ['Inter', 'DejaVu Sans'], 'font.size': 9,'axes.edgecolor': '#9a9994', 'axes.labelcolor': TEXT, 'xtick.color': TEXT2, 'ytick.color': TEXT2,
                     'axes.titlesize': 10, 'figure.dpi': 150, 'savefig.dpi': 200, 'axes.grid': False, 'legend.frameon': False})

FEATURES = {  # reference features (lat, lon E) for orientation only - not targets
    'Tycho': (-43.3, -11.4), 'Copernicus': (9.6, -20.1), 'M. Crisium': (17.0, 59.1), 'M. Imbrium': (32.8, -15.6),
    'Aristarchus': (23.7, -47.4), 'Grimaldi': (-5.5, -68.3), 'M. Orientale': (-19.4, -92.8), 'Tsiolkovskiy': (-20.4, 129.1),
    'Shackleton': (-89.9, 0.0), 'SPA basin': (-53.0, -169.0), 'M. Moscoviense': (27.3, 147.9), 'Hertzsprung': (2.0, -129.2),
}

def healpix_to_raster(values, nside, res_deg=0.5, nest=False):
    lons = np.arange(-180 + res_deg / 2, 180, res_deg); lats = np.arange(90 - res_deg / 2, -90, -res_deg)
    LO, LA = np.meshgrid(lons, lats)
    pix = hp.ang2pix(nside, np.radians(90 - LA), np.radians(LO % 360), nest=nest)
    return values[pix], (-180, 180, -90, 90)

def lunar_map(ax, values, nside, title='', cmap=SEQ_BLUE, vmin=None, vmax=None, cbar_label='', features=True, nearside_box=True, mask=None):
    img, ext = healpix_to_raster(values, nside)
    if mask is not None:
        m, _ = healpix_to_raster(mask.astype(float), nside); img = np.where(m > 0.5, img, np.nan)
    im = ax.imshow(img, extent=ext, origin='upper', cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto', interpolation='nearest')
    ax.set_xticks(np.arange(-180, 181, 60)); ax.set_yticks(np.arange(-90, 91, 30))
    ax.set_xlabel('selenographic longitude (deg E)'); ax.set_ylabel('latitude (deg N)')
    for x in [-90, 90]:
        ax.axvline(x, color=TEXT2, lw=0.8, ls='--')
    if nearside_box:
        ax.text(-178, 84, 'far side', color=TEXT2, fontsize=7, va='top'); ax.text(100, 84, 'far side', color=TEXT2, fontsize=7, va='top')
        ax.text(-40, 84, 'near side (centre 0,0)', color=TEXT2, fontsize=7, va='top', bbox=dict(facecolor='white', alpha=0.75, edgecolor='none', pad=1.5))
    if features:
        for name, (la, lo) in FEATURES.items():
            ax.plot(lo, la, 'k.', ms=3)
            # labels of features near the right edge go to the left of the point so they are not cut off
            ax.text(lo - 2 if lo > 120 else lo + 2, la + 2, name, fontsize=6, color=TEXT, ha='right' if lo > 120 else 'left')
    ax.set_title(title, loc='left')
    cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02); cb.set_label(cbar_label)
    return im

def earth_view(ax, values, nside, subearth_lon=0.0, subearth_lat=0.0, title='', cmap=SEQ_BLUE, vmin=None, vmax=None, cbar_label='', n=600, features=True, mask=None, terminator_lon=None):
    """Orthographic view of the near side as seen from Earth (celestial north up, IAU east to the right? no:
    lunar east (+lon) appears on the sky's west side, i.e. to the RIGHT when north is up for a northern observer)."""
    x = np.linspace(-1, 1, n); X, Y = np.meshgrid(x, -x)
    rho = np.hypot(X, Y); inside = rho <= 1
    c = np.arcsin(np.clip(rho, 0, 1))
    la0, lo0 = np.radians(subearth_lat), np.radians(subearth_lon)
    with np.errstate(invalid='ignore', divide='ignore'):
        lat = np.arcsin(np.cos(c) * np.sin(la0) + Y * np.sin(c) * np.cos(la0) / np.where(rho == 0, 1, rho))
        lon = lo0 + np.arctan2(X * np.sin(c), rho * np.cos(c) * np.cos(la0) - Y * np.sin(c) * np.sin(la0))
    pix = hp.ang2pix(nside, np.radians(90 - np.degrees(lat)), lon % (2 * np.pi))
    img = np.where(inside, values[pix], np.nan)
    if mask is not None:
        img = np.where(inside & (mask[pix] > 0.5), img, np.nan)
    im = ax.imshow(img, extent=(-1, 1, -1, 1), cmap=cmap, vmin=vmin, vmax=vmax, interpolation='nearest')
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, color=TEXT2, lw=0.8))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect('equal'); ax.set_title(title, loc='left')
    # graticule
    for lo in range(-90, 91, 30):
        la = np.radians(np.linspace(-90, 90, 181)); lor = np.radians(lo)
        xg = np.cos(la) * np.sin(lor - lo0); yg = np.cos(la0) * np.sin(la) - np.sin(la0) * np.cos(la) * np.cos(lor - lo0)
        vis = np.sin(la0) * np.sin(la) + np.cos(la0) * np.cos(la) * np.cos(lor - lo0) > 0
        ax.plot(np.where(vis, xg, np.nan), np.where(vis, yg, np.nan), color='white', lw=0.3, alpha=0.6)
    for la_ in range(-60, 61, 30):
        lo_ = np.radians(np.linspace(-180, 180, 361)); lar = np.radians(la_)
        xg = np.cos(lar) * np.sin(lo_ - lo0); yg = np.cos(la0) * np.sin(lar) - np.sin(la0) * np.cos(lar) * np.cos(lo_ - lo0)
        vis = np.sin(la0) * np.sin(lar) + np.cos(la0) * np.cos(lar) * np.cos(lo_ - lo0) > 0
        ax.plot(np.where(vis, xg, np.nan), np.where(vis, yg, np.nan), color='white', lw=0.3, alpha=0.6)
    if features:
        for name, (la, lo) in FEATURES.items():
            lar, lor = np.radians(la), np.radians(lo)
            if np.sin(la0) * np.sin(lar) + np.cos(la0) * np.cos(lar) * np.cos(lor - lo0) > 0.05:
                xg = np.cos(lar) * np.sin(lor - lo0); yg = np.cos(la0) * np.sin(lar) - np.sin(la0) * np.cos(lar) * np.cos(lor - lo0)
                ax.plot(xg, yg, 'k.', ms=3); ax.text(xg + 0.03, yg + 0.03, name, fontsize=6)
    ax.text(0, -1.08, 'view from Earth, celestial north up; lunar east (+lon) on the right', ha='center', fontsize=6, color=TEXT2)
    if cbar_label:
        cb = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02); cb.set_label(cbar_label)
    return im

_COAST = None
def coastlines(ax, res='110m', color=TEXT2, lw=0.5):
    global _COAST
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fn = f'{here}/data/coast/ne_{res}_coastline.shp'
    r = shapefile.Reader(fn)
    for sh in r.shapes():
        pts = np.array(sh.points)
        parts = list(sh.parts) + [len(pts)]
        for a, b in zip(parts[:-1], parts[1:]):
            seg = pts[a:b]
            # break at dateline jumps
            jumps = np.where(np.abs(np.diff(seg[:, 0])) > 180)[0]
            for s in np.split(np.arange(len(seg)), jumps + 1):
                if len(s) > 1:
                    ax.plot(seg[s, 0], seg[s, 1], color=color, lw=lw)

def country_outline(ax, name='Turkey', color=TEXT, lw=0.8):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = shapefile.Reader(f'{here}/data/coast/ne_50m_admin_0_countries.shp')
    flds = [f[0] for f in r.fields[1:]]
    iname = flds.index('NAME')
    for sr in r.iterShapeRecords():
        if sr.record[iname] in (name, 'Türkiye', 'Turkiye'):
            pts = np.array(sr.shape.points); parts = list(sr.shape.parts) + [len(pts)]
            for a, b in zip(parts[:-1], parts[1:]):
                ax.plot(pts[a:b, 0], pts[a:b, 1], color=color, lw=lw)

def evidence_tag(fig, tag):
    fig.text(0.995, 0.005, tag, ha='right', va='bottom', fontsize=7, color=TEXT2, style='italic', gid='evidence-tag')

def _place_evidence_tags(fig):
    """Move evidence tags just below the lowest element of the figure, right-aligned with it, so they never cover axis labels."""
    tags = [t for t in fig.texts if t.get_gid() == 'evidence-tag']
    if not tags:
        return
    for t in tags: t.set_visible(False)
    fig.canvas.draw(); bb = fig.get_tightbbox(fig.canvas.get_renderer())  # inches
    for t in tags:
        t.set_visible(True); t.set_va('top')
        t.set_position((bb.x1 / fig.get_figwidth(), (bb.y0 - 0.04) / fig.get_figheight()))

def savefig(fig, name, outdir=None):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = outdir or f'{here}/outputs/figures'
    os.makedirs(outdir, exist_ok=True)
    _place_evidence_tags(fig)
    # no creation date in the PDF, so repeated runs give byte-identical files
    fig.savefig(f'{outdir}/{name}.png', bbox_inches='tight'); fig.savefig(f'{outdir}/{name}.pdf', bbox_inches='tight', metadata={'CreationDate': None})
    plt.close(fig)
    return f'{outdir}/{name}.png'
