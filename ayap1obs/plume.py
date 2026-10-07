"""Ejecta and sunlit-plume model.

1. Ejecta source: Housen & Holsapple (2011, Icarus 211, 856) point-source scaling, implemented with complete named
   parameter sets (their Table 3 as reproduced by Hirata & Ikeya 2021, Table B1, and Cheng et al. 2020, Table 3):
       v(x)/U = C1 [ (x/a) (rho/delta)^nu ]^(-1/mu) (1 - x/(n2 R))^p ,   n1 a <= x <= n2 R
       M(<x)/m = (3k / 4 pi) (rho/delta) [ (x/a)^3 - n1^3 ]
   with the crater radius R from the same paper's gravity- or strength-regime scaling. M(>v) follows by inverting v(x)
   numerically. Speeds above v(n1 a) are OUTSIDE the scaling domain: the model returns NaN ("cannot determine"), not
   zero. The point-source law is for vertical impacts; no validated rule converts it to a 3-degree grazing impact by a
   hollow spacecraft (much of which may ricochet, Schultz & Gault 1990), so two rules bracket the problem
   ('vertical-component': U sin(theta); 'vertical-equivalent': U) and results are exploratory envelopes.
2. Phase-space plume (release 2.1): mass in launch-speed bins over the whole in-domain population down to a declared
   floor (the slowest ejecta leave near the crater rim), launched from their HH2011 launch radius at x/v, numerically
   integrated two-body trajectories (RK4) in lunar gravity, sunlight (point-Sun cylindrical shadow) and visibility
   from an observer (spherical-Moon occultation) at each time, deposition of the visible sunlit mass on nested sky
   grids, separately for dust seen against sunlit ground (which it partly hides: brightness change kappa x ground)
   and against dark ground or sky (additive). Grain size distribution, p Phi, the photometric contrast kappa, the
   seeing, atmospheric extinction of the source and a fast linear camera are applied afterwards; exposures are
   integrated over the window. Results are conditional model estimates; grain sizes, the photometric contrast and the
   oblique-impact rule are unconstrained for a grazing hollow spacecraft.
"""
from __future__ import annotations
import numpy as np
from . import impact as I

MU_MOON = 4.9028e12          # m^3 s^-2
R_MOON_M = 1737.4e3
M_SUN_V = -26.74

# Housen & Holsapple (2011) Table 3 (via Hirata & Ikeya 2021; Cheng et al. 2020): nu = 0.4, n1 = 1.2 for all sets
HH_EJECTA = {
    'sand':         dict(regime='gravity',  mu=0.41, k=0.3,  C1=0.55, H=0.59, n1=1.2, n2=1.3, p=0.3, nu=0.4, Y=0.0,   label='sand (HH2011 C4)'),
    'sand/fly ash': dict(regime='strength', mu=0.40, k=0.3,  C1=0.55, H=0.40, n1=1.2, n2=1.0, p=0.3, nu=0.4, Y=4.0e3, label='sand/fly ash (HH2011 C7, porous, 4 kPa)'),
    'perlite/sand': dict(regime='strength', mu=0.35, k=0.32, C1=0.60, H=0.81, n1=1.2, n2=1.0, p=0.2, nu=0.4, Y=2.0e3, label='perlite/sand (HH2011 C8, highly porous, 2 kPa)'),
}
RHO_REGOLITH = 1500.0        # kg m^-3, bulk target density used with every parameter set

def crater_radius(m, U, delta, params='sand', rho=RHO_REGOLITH, g=I.G_MOON):
    p = HH_EJECTA[params]; mu, nu = p['mu'], p['nu']
    a = I.impactor_radius(m, delta)
    if p['regime'] == 'gravity':
        s = p['H'] * (g * a / U ** 2) ** (-mu / (2 + mu)) * (rho / delta) ** ((2 + mu - 6 * nu) / (3 * (2 + mu)))
    else:
        s = p['H'] * (p['Y'] / (rho * U ** 2)) ** (-mu / 2) * (rho / delta) ** ((1 - 3 * nu) / 3)
    return s * (m / rho) ** (1 / 3)

def ejecta_velocity(x, m, U, delta, params='sand', rho=RHO_REGOLITH):
    """Launch speed (m/s) of material ejected from distance x (m) from the impact point."""
    p = HH_EJECTA[params]; a = I.impactor_radius(m, delta); R = crater_radius(m, U, delta, params, rho)
    x = np.asarray(x, float)
    with np.errstate(invalid='ignore', divide='ignore'):
        return U * p['C1'] * ((x / a) * (rho / delta) ** p['nu']) ** (-1 / p['mu']) * np.clip(1 - x / (p['n2'] * R), 0, None) ** p['p']

def ejecta_domain(m, U, delta, params='sand', rho=RHO_REGOLITH):
    """(v_max, M_total): the fastest speed inside the scaling domain (at x = n1 a) and the total ejected mass."""
    p = HH_EJECTA[params]; a = I.impactor_radius(m, delta); R = crater_radius(m, U, delta, params, rho)
    vmax = float(ejecta_velocity(p['n1'] * a, m, U, delta, params, rho))
    Mtot = float((3 * p['k'] / (4 * np.pi)) * (rho / delta) * ((p['n2'] * R / a) ** 3 - p['n1'] ** 3) * m)
    return vmax, Mtot

def ejecta_mass_above_speed(v, m, U, delta, params='sand', rho=RHO_REGOLITH):
    """M(>v) in kg. NaN where v exceeds the scaling domain (v > v(n1 a)); the total ejected mass where v is below the
    slowest ejecta. Inverts v(x) by bisection in log x."""
    p = HH_EJECTA[params]; a = I.impactor_radius(m, delta); R = crater_radius(m, U, delta, params, rho)
    v = np.atleast_1d(np.asarray(v, float))
    vmax, Mtot = ejecta_domain(m, U, delta, params, rho)
    lo = np.full(v.shape, np.log(p['n1'] * a)); hi = np.full(v.shape, np.log(p['n2'] * R * (1 - 1e-12)))
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        vm = ejecta_velocity(np.exp(mid), m, U, delta, params, rho)
        go_out = vm > v                      # speed decreases with x: move outwards while still too fast
        lo = np.where(go_out, mid, lo); hi = np.where(go_out, hi, mid)
    x = np.exp(0.5 * (lo + hi))
    M = (3 * p['k'] / (4 * np.pi)) * (rho / delta) * ((x / a) ** 3 - p['n1'] ** 3) * m
    M = np.where(v > vmax, np.nan, M)
    return np.where(v <= 0, Mtot, M)

# spacecraft models: (mass fraction, bulk density) components treated as co-located point sources
IMPACTOR_MODELS = {
    'hollow bus (150 kg/m3)':      [(1.0, 150.0)],
    'bus 400 kg/m3':               [(1.0, 400.0)],
    'dense parts + hollow bus':    [(0.3, 2700.0), (0.7, 150.0)],
}

def ejecta_mass_above_speed_sc(v, m_total, U_km_s, angle_deg, model='dense parts + hollow bus', rule='vertical-equivalent', params='sand'):
    """Sum over spacecraft components of M(>v); NaN where every component is outside its domain at v."""
    U = float(I.effective_speed(U_km_s, angle_deg, rule))
    v = np.atleast_1d(np.asarray(v, float)); tot = np.zeros(v.shape); any_ok = np.zeros(v.shape, bool)
    for frac, delta in IMPACTOR_MODELS[model]:
        M = ejecta_mass_above_speed(v, frac * m_total, U, delta, params)
        ok = np.isfinite(M); tot += np.where(ok, M, 0.0); any_ok |= ok
    return np.where(any_ok, tot, np.nan)

def domain_vmax_sc(m_total, U_km_s, angle_deg, model='dense parts + hollow bus', rule='vertical-equivalent', params='sand'):
    U = float(I.effective_speed(U_km_s, angle_deg, rule))
    return max(ejecta_domain(f * m_total, U, d, params)[0] for f, d in IMPACTOR_MODELS[model])

# ------------------------------------------------------------------ grains and scattering --------------------------------
GRAIN_MODELS = {
    # log-normal mass distribution in grain radius: (median radius m, sigma in dex); regolith: median ~70 um diameter
    # class, 10-20 % finer than 20 um (Lunar Sourcebook) -> median radius 35 um is too coarse for the finest tail; we use
    # the diameter statistics directly as radii x 0.5.
    'regolith':  dict(median=35e-6, dex=0.5, rho=3000.0, label='lunar regolith (median diameter 70 um; ~14 % of mass finer than 20 um)'),
    'fine-rich': dict(median=2.5e-6, dex=0.0, rho=3000.0, label='all mass in 2.5-um grains (the LCROSS brightness-to-mass convention)'),
    'coarse':    dict(median=50e-6, dex=0.4, rho=3000.0, label='coarse regolith (median diameter 100 um)'),
}

def cross_section_per_mass(model='regolith'):
    """Geometric cross-section per unit mass (m^2/kg) = 3/(4 rho_g) <1/a>_mass for a log-normal mass distribution."""
    g = GRAIN_MODELS[model]
    s = g['dex'] * np.log(10)
    return 3.0 / (4 * g['rho']) * np.exp(s ** 2 / 2) / g['median']

def sb_from_cross_section(sigma_m2, area_arcsec2, distance_m, pPhi=0.03, r_au=1.0):
    """Surface brightness (V mag/arcsec^2) of a sunlit cloud element with geometric cross-section sigma (m^2) over a
    projected area (arcsec^2): m = m_sun - 2.5 log10(p Phi sigma / (pi d^2)) + 5 log10(r_au)."""
    with np.errstate(divide='ignore'):
        m = M_SUN_V - 2.5 * np.log10(pPhi * np.asarray(sigma_m2) / (np.pi * distance_m ** 2)) + 5 * np.log10(r_au)
    return m + 2.5 * np.log10(area_arcsec2)

# ------------------------------------------------------------------ camera for the plume -------------------------------------
# A metre-class telescope with a fast linear camera (re-audit PH-N06): the exposure is shortened until the background
# fills at most half the full well (never below the minimum exposure; otherwise the camera is unusable on that
# background) and the short frames are co-added over the integration window with a readout gap per frame.
CAMERA_1M = dict(area_m2=0.785, throughput=0.5, pixel_arcsec=0.5, full_well_e=6.0e4, read_noise_e=5.0, dark_e_s=0.01, n_ref=20,
                 min_exposure_s=1e-3, readout_s=1e-3, seeing_arcsec=1.5, label='1-m telescope, V band, 0.5"/pixel, full well 60 ke-, read noise 5 e-')
SB_OPAQUE_PPHI1 = M_SUN_V + 2.5 * np.log10(np.pi * 206264.806 ** 2)    # V mag/arcsec^2 of an opaque layer with p Phi = 1 (~1.07)

def launch_radius(v, m, U, delta, params='sand', rho=RHO_REGOLITH):
    """Launch distance x (m) of ejecta with speed v from the HH2011 v(x) relation (bisection in log x)."""
    p = HH_EJECTA[params]; a = I.impactor_radius(m, delta); R = crater_radius(m, U, delta, params, rho)
    v = np.atleast_1d(np.asarray(v, float))
    lo = np.full(v.shape, np.log(p['n1'] * a)); hi = np.full(v.shape, np.log(p['n2'] * R * (1 - 1e-9)))
    for _ in range(70):
        mid = 0.5 * (lo + hi); go_out = ejecta_velocity(np.exp(mid), m, U, delta, params, rho) > v
        lo = np.where(go_out, mid, lo); hi = np.where(go_out, hi, mid)
    return np.exp(0.5 * (lo + hi))

def _schedule(t_max, scale, segs):
    """Concatenated uniform steps: segs = [(t_end, step), ...] (steps multiplied by scale)."""
    t = [0.0]
    for t_end, st in segs:
        t_end = min(t_end, t_max)
        while t[-1] < t_end - 1e-9:
            t.append(min(t[-1] + st * scale, t_end))
    return np.array(t)

def _deposit(grid, x, y, w, half, cell):
    """Cloud-in-cell deposit of weights w at positions (x, y) km on a square grid of half-width half and cell size cell."""
    nb = grid.shape[0]
    fx = (x + half) / cell - 0.5; fy = (y + half) / cell - 0.5
    i0 = np.floor(fx).astype(int); j0 = np.floor(fy).astype(int); ax = fx - i0; ay = fy - j0
    for di, wx in ((0, 1 - ax), (1, ax)):
        for dj, wy in ((0, 1 - ay), (1, ay)):
            ii = i0 + di; jj = j0 + dj
            ok = (ii >= 0) & (ii < nb) & (jj >= 0) & (jj < nb)
            np.add.at(grid, (jj[ok], ii[ok]), (w * wx * wy)[ok])

def plume_simulation(site_unit, sun_unit, obs_vectors, m_total, U_km_s, angle_deg, impact_azimuth_deg=0.0,
                     model='dense parts + hollow bus', rule='vertical-equivalent', params='sand', launch_elev=(45.0, 10.0),
                     downrange_factor=1.0, v_lo=None, v_floor=1.0, finite_source=True, t_max=600.0, dt_scale=1.0, rec_scale=1.0,
                     n_speed=48, n_elev=7, n_az=16, cell_fine_km=0.05, half_fine_km=2.0, cell_km=0.5, half_width_km=40.0):
    """Phase-space ejecta plume (release 2.1; re-audit PH-N01, PH-N03).

    Population: every in-domain launch speed from v_lo (default v_floor = 1 m/s; for a site in darkness the caller
    passes the speed needed to reach sunlight, below which ejecta cannot be lit) to the domain maximum, per spacecraft
    component. Finite source: ejecta of speed v leave from their HH2011 launch radius x(v) at time x/v (excavation
    flow), at the launch azimuth. Two-body RK4 integration with steps of 0.05 s (< 10 s), 0.25 s (< 60 s) and 1 s
    (x dt_scale); particles are frozen when they return to the surface. At every record time (0.25 / 1 / 4 s x
    rec_scale) the sunlit particles visible from each observer are projected on the sky plane and their MASS is
    deposited (cloud-in-cell) on a fine grid near the impact point and a coarse grid outside, separately for parcels
    seen against sunlit ground (contrast class: the dust hides ground of similar brightness) and against dark ground or
    sky (additive class). Optical depth, grains, p Phi and the camera are applied by plume_detectability()."""
    n0 = np.asarray(site_unit, float) / np.linalg.norm(site_unit)
    zc = np.array([0, 0, 1.0]) if abs(n0[2]) < 0.9 else np.array([1.0, 0, 0])
    east = np.cross(zc, n0); east /= np.linalg.norm(east); north = np.cross(n0, east)
    U_eff = float(I.effective_speed(U_km_s, angle_deg, rule))
    vmax = domain_vmax_sc(m_total, U_km_s, angle_deg, model, rule, params)
    vlo = max(float(v_floor), float(v_lo or 0.0))
    M_domain = float(sum(ejecta_domain(f * m_total, U_eff, d, params)[1] for f, d in IMPACTOR_MODELS[model]))
    if vmax <= vlo:
        return dict(ok=False, reason=f'no in-domain ejecta faster than {vlo:.1f} m/s', vmax=vmax, v_lo=vlo, M_domain_kg=M_domain)
    el_mu, el_sd = launch_elev
    zs = np.linspace(-1.5, 1.5, n_elev)
    els = np.radians(np.clip(el_mu + el_sd * zs, 5, 85)); w_el = np.exp(-0.5 * zs ** 2); w_el /= w_el.sum()
    azs = np.radians((np.arange(n_az) + 0.5) * 360.0 / n_az)
    w_az = 1.0 + (downrange_factor - 1.0) * 0.5 * (1 + np.cos(azs - np.radians(impact_azimuth_deg))); w_az /= w_az.sum()
    V, EL, AZ, W, X0, T0 = [], [], [], [], [], []
    for frac, delta in IMPACTOR_MODELS[model]:
        vmax_c = ejecta_domain(frac * m_total, U_eff, delta, params)[0]
        if vmax_c <= vlo:
            continue
        edges = np.geomspace(vlo, vmax_c, n_speed + 1)
        Mab = np.nan_to_num(ejecta_mass_above_speed(edges, frac * m_total, U_eff, delta, params), nan=0.0)
        dm = np.clip(Mab[:-1] - Mab[1:], 0, None); vc = np.sqrt(edges[:-1] * edges[1:])
        xc = launch_radius(vc, frac * m_total, U_eff, delta, params) if finite_source else np.zeros_like(vc)
        v_, e_, a_ = np.meshgrid(vc, els, azs, indexing='ij'); x_ = np.broadcast_to(xc[:, None, None], v_.shape)
        w_ = dm[:, None, None] * w_el[None, :, None] * w_az[None, None, :]
        V.append(v_.ravel()); EL.append(e_.ravel()); AZ.append(a_.ravel()); W.append(w_.ravel()); X0.append(x_.ravel())
        T0.append((x_ / v_).ravel() if finite_source else np.zeros(v_.size))
    V, EL, AZ, W, X0, T0 = (np.concatenate(z) for z in (V, EL, AZ, W, X0, T0))
    keep = W > 0; V, EL, AZ, W, X0, T0 = V[keep], EL[keep], AZ[keep], W[keep], X0[keep], T0[keep]
    hor = np.cos(AZ)[:, None] * north + np.sin(AZ)[:, None] * east
    dirs = np.cos(EL)[:, None] * hor + np.sin(EL)[:, None] * n0
    r = n0 * (R_MOON_M + 1.0) + X0[:, None] * hor; r0 = r.copy(); v = V[:, None] * dirs
    landed = np.zeros(len(V), bool)
    s_sun = np.asarray(sun_unit, float) / np.linalg.norm(sun_unit)
    t_steps = _schedule(t_max, dt_scale, [(10.0, 0.05), (60.0, 0.25), (t_max, 1.0)])
    t_rec = _schedule(t_max, rec_scale, [(10.0, 0.25), (60.0, 1.0), (t_max, 4.0)])
    nf = int(round(2 * half_fine_km / cell_fine_km)); nc = int(round(2 * half_width_km / cell_km))
    obs = {}
    for name, O in obs_vectors.items():
        O = np.asarray(O, float); los = O - n0 * R_MOON_M; dist = float(np.linalg.norm(los)); los /= dist
        ex = np.cross([0, 0, 1.0], los); ex /= np.linalg.norm(ex); ey = np.cross(los, ex)
        obs[name] = dict(O=O, ex=ex, ey=ey, dist=dist, fine_add=np.zeros((len(t_rec), nf, nf), np.float32), fine_con=np.zeros((len(t_rec), nf, nf), np.float32),
                         coarse_add=np.zeros((len(t_rec), nc, nc), np.float32), coarse_con=np.zeros((len(t_rec), nc, nc), np.float32),
                         M_vis=np.zeros(len(t_rec)), M_con=np.zeros(len(t_rec)))
    def acc(x):
        d = np.linalg.norm(x, axis=1, keepdims=True)
        return -MU_MOON * x / d ** 3
    def record(kr, t):
        active = (T0 <= t) & ~landed
        sunlit = active & (((r @ s_sun) >= 0) | (np.linalg.norm(r - (r @ s_sun)[:, None] * s_sun, axis=1) >= R_MOON_M))
        for ob in obs.values():
            dvec = ob['O'][None, :] - r; dd = np.einsum('ni,ni->n', dvec, dvec)
            tstar = -np.einsum('ni,ni->n', r, dvec) / dd; C = r + np.clip(tstar, 0, 1)[:, None] * dvec
            blocked = (tstar > 0) & (tstar < 1) & (np.linalg.norm(C, axis=1) < R_MOON_M - 0.5)
            vis = sunlit & ~blocked
            if not vis.any():
                continue
            P = r[vis]; u = -dvec[vis] / np.sqrt(dd[vis])[:, None]          # from the observer through the parcel, onwards
            pu = np.einsum('ni,ni->n', P, u); disc = pu ** 2 - np.einsum('ni,ni->n', P, P) + R_MOON_M ** 2
            th = -pu - np.sqrt(np.maximum(disc, 0)); th = np.where(th > 0, th, -pu + np.sqrt(np.maximum(disc, 0)))
            Hh = P + th[:, None] * u
            con = (disc >= 0) & (th > 0) & ((Hh @ s_sun) > 0)              # behind the parcel: sunlit ground
            rel = P - n0 * R_MOON_M; x_km = (rel @ ob['ex']) / 1e3; y_km = (rel @ ob['ey']) / 1e3
            w = W[vis]; fine = (np.abs(x_km) < half_fine_km) & (np.abs(y_km) < half_fine_km)
            for cls, msk in (('con', con), ('add', ~con)):
                _deposit(ob[f'fine_{cls}'][kr], x_km[msk & fine], y_km[msk & fine], w[msk & fine], half_fine_km, cell_fine_km)
                _deposit(ob[f'coarse_{cls}'][kr], x_km[msk & ~fine], y_km[msk & ~fine], w[msk & ~fine], half_width_km, cell_km)
            ob['M_vis'][kr] = float(w.sum()); ob['M_con'][kr] = float(w[con].sum())
    kr = 0
    for k in range(len(t_steps) - 1):
        t, t1 = t_steps[k], t_steps[k + 1]
        while kr < len(t_rec) and t_rec[kr] <= t + 1e-9:
            record(kr, t_rec[kr]); kr += 1
        dt = t1 - t
        mov = (T0 <= t) & ~landed
        if mov.any():
            rr, vv = r[mov], v[mov]
            k1v = acc(rr); k1r = vv
            k2v = acc(rr + 0.5 * dt * k1r); k2r = vv + 0.5 * dt * k1v
            k3v = acc(rr + 0.5 * dt * k2r); k3r = vv + 0.5 * dt * k2v
            k4v = acc(rr + dt * k3r); k4r = vv + dt * k3v
            rn = rr + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r); vn = vv + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            hit = np.linalg.norm(rn, axis=1) < R_MOON_M
            idx = np.where(mov)[0]
            r[idx[~hit]] = rn[~hit]; v[idx[~hit]] = vn[~hit]; landed[idx[hit]] = True
        # particles launched during this step start from their launch point at their launch time (sub-step neglected)
    while kr < len(t_rec):
        record(kr, t_rec[kr]); kr += 1
    res = dict(ok=True, vmax=vmax, v_lo=vlo, times=t_rec, M_selected_kg=float(W.sum()), M_domain_kg=M_domain, U_eff=U_eff, n_particles=int(len(W)),
               grids=dict(cell_fine_km=cell_fine_km, half_fine_km=half_fine_km, cell_km=cell_km, half_width_km=half_width_km), observers={})
    for name, ob in obs.items():
        res['observers'][name] = dict(distance_m=ob['dist'], arcsec_per_km=206264.806 / (ob['dist'] / 1e3), fine_add=ob['fine_add'], fine_con=ob['fine_con'],
                                      coarse_add=ob['coarse_add'], coarse_con=ob['coarse_con'], M_vis=ob['M_vis'], M_con=ob['M_con'])
    return res

def _eff_area(mass_maps, sigma_per_kg, cell_km):
    """Optical-depth-limited scattering area (m^2) per cell from deposited mass (kg) at the deposit resolution."""
    a = (cell_km * 1e3) ** 2
    return a * (1 - np.exp(-np.asarray(mass_maps, float) * sigma_per_kg / a))

def _to_coarse(sim, ob, eff_fine):
    """Add fine-grid effective areas (computed at fine resolution) into the coarse grid cells they fall in."""
    g = sim['grids']; nf = eff_fine.shape[-1]; nc = ob['coarse_add'].shape[-1]
    f = int(round(g['cell_km'] / g['cell_fine_km']))
    blk = eff_fine.reshape(eff_fine.shape[:-2] + (nf // f, f, nf // f, f)).sum(axis=(-3, -1))
    off = int(round((g['half_width_km'] - g['half_fine_km']) / g['cell_km']))
    out = np.zeros(eff_fine.shape[:-2] + (nc, nc))
    out[..., off:off + nf // f, off:off + nf // f] = blk
    return out

def plume_detectability_multi(sim, obs_name, bkg_sb, combos, ext_mag=0.0, cam=CAMERA_1M, t_window=1.0, band='V'):
    """Exposure-integrated detectability of the plume for several assumption combinations at once (re-audit PH-N03,
    PH-N06). combos: list of dict(grains, pPhi, kappa, sys_frac). Integration windows start at every record time and
    average the deposited mass maps recorded within [t, t + t_window] (records are 0.25 s apart early on, so the first
    minute is genuinely exposure-integrated; later the evolution is slower than the record spacing). Mass maps ->
    effective scattering area with the optical depth at the deposit resolution (fine grid near the impact point,
    coarse outside) -> excess surface brightness: additive class p Phi A / (pi d^2) x sunlight; contrast class (dust
    over sunlit ground) kappa x pPhi_ground x A, pPhi_ground from the extinction-corrected background brightness and
    kappa the unknown dust/ground photometric contrast. The source is extincted like the background, smoothed by the
    seeing and summed in the aperture of cells above 20 % of the peak |excess| (at least the seeing disk). Camera: the
    exposure is shortened so that the background fills at most half the full well (>= min_exposure, else unusable) and
    the frames are co-added over the window with a readout gap; noise = source and background shot noise, read and
    dark noise per frame, the mean of n_ref reference frames, and a subtraction systematic sys_frac x background."""
    from scipy.ndimage import gaussian_filter
    from .detect import photons_from_mag
    ob = sim['observers'][obs_name]; g = sim['grids']; t = sim['times']; d = ob['distance_m']
    starts = t[t <= max(t[-1] - t_window, 0.0) + 1e-9]
    idx = [np.where((t >= t0 - 1e-9) & (t <= t0 + t_window + 1e-9))[0] for t0 in starts]
    def window_mean(maps):
        return np.array([maps[i].mean(axis=0) for i in idx])
    cell_as = g['cell_km'] * ob['arcsec_per_km']; area_as = cell_as ** 2
    pphi_ground = 10 ** (-0.4 * (bkg_sb - ext_mag - SB_OPAQUE_PPHI1))
    f0 = 10 ** (-0.4 * M_SUN_V) / (np.pi * d ** 2) / area_as * 10 ** (-0.4 * ext_mag)
    sig_px = cam['seeing_arcsec'] / 2.355 / cell_as
    pix_per_cell = (cell_as / cam['pixel_arcsec']) ** 2
    rate_pix = photons_from_mag(bkg_sb, band, cam['area_m2'], cam['throughput'], 1.0) * cam['pixel_arcsec'] ** 2
    t_e = min(t_window, 0.5 * cam['full_well_e'] / max(rate_pix, 1e-30)); usable = t_e >= cam['min_exposure_s']
    t_e = max(t_e, cam['min_exposure_s']); n_fr = max(int(np.floor(t_window / (t_e + cam['readout_s']))), 1)
    seeing_cells = max(np.pi * (1.5 * cam['seeing_arcsec'] / cell_as) ** 2, 1.0)
    filt = {}
    for gr in sorted({c['grains'] for c in combos}):
        sig = cross_section_per_mass(gr)
        A = {}
        for cls in ('add', 'con'):
            eff = window_mean(_eff_area(ob[f'coarse_{cls}'], sig, g['cell_km'])) + _to_coarse(sim, ob, window_mean(_eff_area(ob[f'fine_{cls}'], sig, g['cell_fine_km'])))
            A[cls] = np.array([gaussian_filter(e, sig_px) if sig_px > 0.3 else e for e in eff])
        filt[gr] = (A, max(np.max(ob['fine_add'] + ob['fine_con']) * sig / (g['cell_fine_km'] * 1e3) ** 2,
                           np.max(ob['coarse_add'] + ob['coarse_con']) * sig / (g['cell_km'] * 1e3) ** 2))
    yy, xx = np.ogrid[:ob['coarse_add'].shape[1], :ob['coarse_add'].shape[2]]
    out = []
    for c in combos:
        A, tau_max = filt[c['grains']]
        img_all = f0 * (c['pPhi'] * A['add'] + c['kappa'] * pphi_ground * A['con'])
        snr = np.zeros(len(starts)); con = np.zeros(len(starts))
        for k in range(len(starts)):
            img = img_all[k]; pk = np.abs(img).max()
            if pk <= 0:
                continue
            ap = np.abs(img) >= 0.2 * pk
            if ap.sum() < seeing_cells:
                iy, ix = np.unravel_index(np.argmax(np.abs(img)), img.shape)
                ap = (yy - iy) ** 2 + (xx - ix) ** 2 <= seeing_cells / np.pi
            S_flux = abs(img[ap].sum()) * area_as
            n_pix = ap.sum() * pix_per_cell
            S_e = photons_from_mag(-2.5 * np.log10(max(S_flux, 1e-300)), band, cam['area_m2'], cam['throughput'], n_fr * t_e)
            B_e = rate_pix * n_fr * t_e * n_pix
            frame = n_pix * n_fr * (cam['read_noise_e'] ** 2 + cam['dark_e_s'] * t_e)
            var = S_e + B_e + frame + (B_e + frame) / cam['n_ref'] + (c['sys_frac'] * B_e) ** 2
            snr[k] = S_e / np.sqrt(var); con[k] = S_flux / (10 ** (-0.4 * bkg_sb) * area_as * ap.sum())
        out.append(dict(t_start=starts, snr=snr, contrast=con, t_exposure_s=t_e, n_frames=n_fr, usable=bool(usable), pphi_ground=float(pphi_ground), tau_max=float(tau_max)))
    return out

def plume_detectability(sim, obs_name, bkg_sb, ext_mag=0.0, grains='regolith', pPhi=0.03, kappa=0.2, sys_frac=0.01, cam=CAMERA_1M, t_window=1.0, band='V'):
    """Single-combination wrapper of plume_detectability_multi."""
    return plume_detectability_multi(sim, obs_name, bkg_sb, [dict(grains=grains, pPhi=pPhi, kappa=kappa, sys_frac=sys_frac)], ext_mag, cam, t_window, band)[0]

def lcross_check(model='hollow Centaur', params='sand', t_check=20.0, h_sun_m=830.0, launch_elev=(45.0, 10.0)):
    """Like-for-like comparison with LCROSS (Strycker et al. 2013: total illuminated plume mass 2240 +/- 400 kg at 20 s
    after impact; sunlight horizon ~830 m): ejecta mass above the sunlight horizon at t_check for the Centaur
    (2271.61 kg at 2.507 km/s, 85.9 deg from horizontal; Marshall et al. 2012), flat-ground ballistic heights."""
    m, U = 2271.61, 2506.885
    deltas = {'hollow Centaur': [(1.0, 40.0)], 'Centaur as 400 kg/m3': [(1.0, 400.0)], 'dense parts + hollow': [(0.3, 2700.0), (0.7, 40.0)]}[model]
    els = np.radians(np.clip(launch_elev[0] + launch_elev[1] * np.linspace(-1.5, 1.5, 7), 5, 85)); w = np.exp(-0.5 * np.linspace(-1.5, 1.5, 7) ** 2); w /= w.sum()
    total = 0.0; vmaxs = []
    for frac, delta in deltas:
        vmax, Mtot = ejecta_domain(frac * m, U * np.sin(np.radians(85.917)), delta, params)
        vmaxs.append(vmax)
        for el, we in zip(els, w):
            vz_need = (h_sun_m + 0.5 * I.G_MOON * t_check ** 2) / t_check      # above h_sun at t_check (flat ground)
            v_need = vz_need / np.sin(el)
            M = ejecta_mass_above_speed(np.array([v_need]), frac * m, U * np.sin(np.radians(85.917)), delta, params)[0]
            total += we * (0.0 if not np.isfinite(M) else M)
    return dict(model=model, params=params, M_illuminated_kg=float(total), observed_kg=2240.0, observed_sigma_kg=400.0, vmax_domain=vmaxs)
