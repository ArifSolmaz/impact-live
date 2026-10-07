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
2. Phase-space plume: mass in launch-speed bins (from dM/dv), launch elevations and azimuths, exact two-body
   trajectories in lunar gravity (curvature included), sunlight (point-Sun cylindrical shadow) and visibility from an
   observer (spherical-Moon occultation) at each time, a regolith grain-size distribution and an optical-depth-limited
   projected image; brightness against the station's total background (Earthshine, scattered crescent light, sky).
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

# ------------------------------------------------------------------ trajectories ------------------------------------------
def _kepler_rk4(r, v, dt, nsteps, record_every):
    """Integrate two-body motion for arrays r, v (n,3) in metres; returns positions at recorded steps (k, n, 3) and a
    landed mask history. Particles that return to the surface are frozen there."""
    out = []; landed_hist = []
    landed = np.zeros(len(r), bool)
    def acc(x):
        d = np.linalg.norm(x, axis=1, keepdims=True)
        return -MU_MOON * x / d ** 3
    for s in range(nsteps + 1):
        if s % record_every == 0:
            out.append(r.copy()); landed_hist.append(landed.copy())
        if s == nsteps:
            break
        k1v = acc(r); k1r = v
        k2v = acc(r + 0.5 * dt * k1r); k2r = v + 0.5 * dt * k1v
        k3v = acc(r + 0.5 * dt * k2r); k3r = v + 0.5 * dt * k2v
        k4v = acc(r + dt * k3r); k4r = v + dt * k3v
        rn = r + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r); vn = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        hit = (np.linalg.norm(rn, axis=1) < R_MOON_M) & ~landed
        landed |= hit
        r = np.where(landed[:, None], r, rn); v = np.where(landed[:, None], 0.0, vn)
    return np.array(out), np.array(landed_hist)

def plume_simulation(site_unit, sun_unit, obs_vectors, m_total, U_km_s, angle_deg, impact_azimuth_deg=0.0,
                     model='dense parts + hollow bus', rule='vertical-equivalent', params='sand', grains='regolith',
                     pPhi=0.03, launch_elev=(45.0, 10.0), downrange_factor=1.0, t_max=600.0, dt=1.0, record=2.0,
                     n_speed=48, n_elev=7, n_az=16, cell_km=1.0, half_width_km=60.0):
    """Phase-space plume. site_unit: selenocentric unit vector of the impact point (any inertial frame);
    sun_unit: unit vector towards the Sun; obs_vectors: dict name -> selenocentric observer position (m).
    Returns dict with times, sunlit-visible mass per observer, image cube helper and domain information."""
    n0 = np.asarray(site_unit, float) / np.linalg.norm(site_unit)
    zc = np.array([0, 0, 1.0]) if abs(n0[2]) < 0.9 else np.array([1.0, 0, 0])
    east = np.cross(zc, n0); east /= np.linalg.norm(east); north = np.cross(n0, east)
    U_eff = float(I.effective_speed(U_km_s, angle_deg, rule))
    vmax = domain_vmax_sc(m_total, U_km_s, angle_deg, model, rule, params)
    v_lo = 30.0
    if vmax <= v_lo:
        return dict(ok=False, reason='no ejecta faster than 30 m/s inside the scaling domain', vmax=vmax)
    edges = np.geomspace(v_lo, vmax, n_speed + 1)
    Mabove = ejecta_mass_above_speed_sc(edges, m_total, U_km_s, angle_deg, model, rule, params)
    Mabove = np.nan_to_num(Mabove, nan=0.0)
    dm = np.clip(Mabove[:-1] - Mabove[1:], 0, None); vc = np.sqrt(edges[:-1] * edges[1:])
    el_mu, el_sd = launch_elev
    els = np.radians(np.clip(el_mu + el_sd * np.linspace(-1.5, 1.5, n_elev), 5, 85)); w_el = np.exp(-0.5 * np.linspace(-1.5, 1.5, n_elev) ** 2); w_el /= w_el.sum()
    azs = np.radians(np.arange(n_az) * 360.0 / n_az)
    # downrange weighting (oblique impacts send more mass downrange; 1 = symmetric)
    w_az = 1.0 + (downrange_factor - 1.0) * 0.5 * (1 + np.cos(azs - np.radians(impact_azimuth_deg))); w_az /= w_az.sum()
    V, EL, AZ = np.meshgrid(vc, els, azs, indexing='ij')
    W = dm[:, None, None] * w_el[None, :, None] * w_az[None, None, :]
    V, EL, AZ, W = V.ravel(), EL.ravel(), AZ.ravel(), W.ravel()
    keep = W > 0; V, EL, AZ, W = V[keep], EL[keep], AZ[keep], W[keep]
    dirs = (np.cos(EL) * np.sin(AZ))[:, None] * east + (np.cos(EL) * np.cos(AZ))[:, None] * north + np.sin(EL)[:, None] * n0
    r0 = np.tile(n0 * (R_MOON_M + 1.0), (len(V), 1)); v0 = V[:, None] * dirs
    nsteps = int(round(t_max / dt)); rec = max(1, int(round(record / dt)))
    pos, landed = _kepler_rk4(r0, v0, dt, nsteps, rec)
    times = np.arange(pos.shape[0]) * rec * dt
    s = np.asarray(sun_unit, float) / np.linalg.norm(sun_unit)
    along = pos @ s; perp = np.linalg.norm(pos - along[..., None] * s, axis=-1)
    sunlit = (along >= 0) | (perp >= R_MOON_M)
    sunlit &= ~landed
    res = dict(ok=True, vmax=vmax, times=times, total_mass_fast=float(W.sum()), U_eff=U_eff, observers={})
    sig_per_kg = cross_section_per_mass(grains)
    for name, O in obs_vectors.items():
        O = np.asarray(O, float); dvec = O[None, None, :] - pos
        dd = np.einsum('kni,kni->kn', dvec, dvec); tstar = -np.einsum('kni,kni->kn', pos, dvec) / dd
        C = pos + np.clip(tstar, 0, 1)[..., None] * dvec
        blocked = (tstar > 0) & (tstar < 1) & (np.linalg.norm(C, axis=-1) < R_MOON_M)
        vis = sunlit & ~blocked
        # sky-plane projection centred on the impact point (orthographic; the cloud spans < 0.1 deg)
        los = O - n0 * R_MOON_M; dist = np.linalg.norm(los); los /= dist
        ex = np.cross([0, 0, 1.0], los); ex /= np.linalg.norm(ex); ey = np.cross(los, ex)
        rel = pos - n0 * R_MOON_M
        x_km = (rel @ ex) / 1e3; y_km = (rel @ ey) / 1e3
        M_vis = (vis * W[None, :]).sum(axis=1)
        nb = int(2 * half_width_km / cell_km)
        cube = np.zeros((len(times), nb, nb))
        ix = np.floor((x_km + half_width_km) / cell_km).astype(int); iy = np.floor((y_km + half_width_km) / cell_km).astype(int)
        inside = (ix >= 0) & (ix < nb) & (iy >= 0) & (iy < nb) & vis
        for k in range(len(times)):
            m = inside[k]
            np.add.at(cube[k], (iy[k][m], ix[k][m]), W[m] * sig_per_kg)
        cell_m2 = (cell_km * 1e3) ** 2
        tau = cube / cell_m2
        eff_area = cell_m2 * (1 - np.exp(-tau))                       # optical-depth-limited scattering area per cell
        arcsec_per_km = 206265.0 / (dist / 1e3)
        res['observers'][name] = dict(M_vis=M_vis, eff_area=eff_area, cell_arcsec=cell_km * arcsec_per_km, distance_m=dist,
                                      sigma_total=(cube.sum(axis=(1, 2))), tau_max=tau.max(axis=(1, 2)), pPhi=pPhi)
    return res

def plume_detectability(obs_res, bkg_sb, inst_area_m2=0.785, throughput=0.5, t_exp=1.0, seeing_arcsec=1.5, sys_frac=0.01, band='V'):
    """Best-aperture signal-to-noise and contrast of the plume against a background of bkg_sb (V mag/arcsec^2),
    per recorded time. The image is smoothed by the seeing, the aperture is the set of cells above 20 % of the peak
    (at least 3x3 cells), the noise includes photon noise of plume and background and a background-subtraction
    systematic of sys_frac x background (coherent over the aperture)."""
    from scipy.ndimage import gaussian_filter
    eff = obs_res['eff_area']; cell_as = obs_res['cell_arcsec']; d = obs_res['distance_m']
    area_as = cell_as ** 2
    sb_cells = sb_from_cross_section(np.maximum(eff, 1e-30), area_as, d, obs_res['pPhi'])        # mag/arcsec^2 per cell
    f_cells = 10 ** (-0.4 * sb_cells)                                                           # flux per arcsec^2 (rel. to 0 mag)
    sig_px = seeing_arcsec / 2.355 / cell_as
    out_snr = []; out_con = []; out_peak = []
    from .detect import photons_from_mag
    for k in range(eff.shape[0]):
        img = gaussian_filter(f_cells[k], sig_px) if sig_px > 0.3 else f_cells[k]
        pk = img.max()
        if pk <= 0:
            out_snr.append(0.0); out_con.append(0.0); out_peak.append(np.inf); continue
        ap = img >= 0.2 * pk
        if ap.sum() < 9:
            iy, ix = np.unravel_index(np.argmax(img), img.shape); ap = np.zeros_like(ap); ap[max(iy - 1, 0):iy + 2, max(ix - 1, 0):ix + 2] = True
        S_flux = img[ap].sum() * area_as                                                         # 0-mag units
        B_flux = 10 ** (-0.4 * bkg_sb) * area_as * ap.sum()
        S_e = photons_from_mag(-2.5 * np.log10(S_flux), band, inst_area_m2, throughput, t_exp)
        B_e = photons_from_mag(-2.5 * np.log10(B_flux), band, inst_area_m2, throughput, t_exp)
        noise = np.sqrt(S_e + B_e + (sys_frac * B_e) ** 2)
        out_snr.append(float(S_e / noise)); out_con.append(float(S_flux / B_flux)); out_peak.append(float(-2.5 * np.log10(pk)))
    return np.array(out_snr), np.array(out_con), np.array(out_peak)

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
