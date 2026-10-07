"""Orbit-plane compatibility and circular-overflight screening opportunities from a ~100-km near-polar circular orbit.

The AYAP-1 orbit plane, orbital phase, terminal-burn plan and propellant budget are not published, so everything here
is conditional on declared families of planes and phases.

Orbit model. A circular orbit of radius a = R + h whose plane is fixed in the ICRF (optionally drifting about the
lunar spin axis at a stated rate). A family is defined by its inclination i and ascending-node longitude Omega in the
Mean-Earth (ME) frame at the reference epoch; the ICRF plane is obtained with the full DE421 ICRF->ME rotation at that
epoch, and the plane is carried to any other epoch with the same full rotation. The spacecraft's argument of latitude
is u(t) = u0 + n (t - t_ref), with the phase u0 unknown and marginalised. A plane with node Omega and the plane with
node Omega + 180 deg (same inclination 90 deg) are the same geometric plane traversed in opposite directions; phase
cannot reverse the direction of motion, so release 2.1 samples nodes over [0, 360) (re-audit GE-V2-02).

Two products:
* Orbit-plane compatibility (an envelope): a surface point is compatible at time t if it lies within the cross-track
  allowance delta of the instantaneous plane. delta = 0.6 deg needs a ~17 m/s plane change and 2.5 deg ~71 m/s
  (dv = 2 v sin(delta/2), v = 1.633 km/s); 0.6 deg is therefore a plane-change allowance, not 'no plane change'.
  This ignores where the spacecraft is and is not a reachability statement.
* Circular-overflight screening opportunities: for each phase u0 the spacecraft passes over (or closest to) a given
  point once per orbit; an opportunity is such an overflight with the cross-track angle within delta. The impact time
  follows from an in-plane retrograde burn (deorbit_trajectory): the descent ellipse covers 84-147 deg of central angle
  for 50-25 m/s, so the burn is made (du_d - n t_f)/n + t_f before the circular overflight and the impact occurs
  (du_d - n t_f)/n before it (opportunities.transfer_offset_s; re-audit GE-01). propagate_descent() checks this mapping
  by numerical two-body integration. Opportunities are screening products for hypothetical planes, not burn solutions.
Limitations: two-body circular motion; no gravity-field evolution, third-body perturbations or orbit maintenance
(100-km near-polar orbits decay within months without maintenance: Ramanan & Adimurthy 2005; Genova 2026, NTRS
20260002233); the cross-track manoeuvre's timing and phase change are not modelled; the descent ends on the reference
sphere (no terrain: the flight-path angle at impact is ~3 deg below the local horizontal, so 1 km of terrain moves the
impact point ~19 km along track).
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from . import ephem as E

MU_MOON = 4902.800066     # km^3/s^2
R_MOON = 1737.4

def circular_speed(alt_km=100.0):
    return float(np.sqrt(MU_MOON / (R_MOON + alt_km)))             # 1.633 km/s at 100 km (orbital, not ground speed)

def ground_track_speed(alt_km=100.0):
    return circular_speed(alt_km) * R_MOON / (R_MOON + alt_km)     # 1.545 km/s along the surface (before lunar rotation)

def plane_change_dv(di_deg, v=None):
    v = circular_speed() if v is None else v
    return 2 * v * np.sin(np.radians(di_deg) / 2) * 1000.0           # m/s

def period_s(alt_km=100.0):
    a = R_MOON + alt_km
    return float(2 * np.pi * np.sqrt(a ** 3 / MU_MOON))

def j2_nodal_rate_deg_day(inclination_deg, alt_km=100.0, J2=2.0330e-4):
    """Secular nodal rate from the lunar J2 (deg/day); ~ -0.04 deg/day at 88 deg, 0 at 90 deg."""
    a = R_MOON + alt_km; n = np.sqrt(MU_MOON / a ** 3)
    return float(np.degrees(-1.5 * n * J2 * (R_MOON / a) ** 2 * np.cos(np.radians(inclination_deg))) * 86400)

@dataclass
class Plane:
    """An orbit plane fixed in the ICRF (plus optional drift about the lunar pole axis at t_ref)."""
    node_deg: float           # ascending-node longitude in the ME frame at t_ref
    t_ref_jd: float           # reference epoch (TDB JD)
    inclination_deg: float = 90.0
    altitude_km: float = 100.0
    drift_deg_day: float = 0.0
    def __post_init__(self):
        i, O = np.radians(self.inclination_deg), np.radians(self.node_deg)
        M = E.icrf_to_me(self.t_ref_jd)
        n_me = np.array([np.sin(i) * np.sin(O), -np.sin(i) * np.cos(O), np.cos(i)])
        e_me = np.array([np.cos(O), np.sin(O), 0.0])
        self.n_icrf = M.T @ n_me; self.e_icrf = M.T @ e_me
        self.f_icrf = np.cross(self.n_icrf, self.e_icrf)
        self.k_icrf = M.T @ np.array([0, 0, 1.0])                   # lunar pole at t_ref (drift axis)
        self.mean_motion = 2 * np.pi / period_s(self.altitude_km)   # rad/s
    def vectors_icrf(self, jd):
        """Plane normal, node and in-plane quadrature unit vectors in the ICRF at epochs jd (arrays (N,3))."""
        jd = np.atleast_1d(jd)
        if self.drift_deg_day == 0.0:
            return [np.tile(v, (len(jd), 1)) for v in (self.n_icrf, self.e_icrf, self.f_icrf)]
        ang = np.radians(self.drift_deg_day * (jd - self.t_ref_jd))
        k = self.k_icrf; out = []
        for v in (self.n_icrf, self.e_icrf, self.f_icrf):           # Rodrigues rotation about k
            c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
            out.append(v * c + np.cross(k, v)[None, :] * s + k[None, :] * (k @ v) * (1 - c))
        return out

def time_grid(jd_start, jd_stop, step_min):
    """TDB JDs and batched Moon/Sun/ICRF->ME matrices on a regular grid (uses screening.epoch_arrays)."""
    from astropy.time import Time
    from . import screening as S
    n = int(np.floor((jd_stop - jd_start) * 1440.0 / step_min)) + 1
    t = Time(jd_start + np.arange(n) * step_min / 1440.0, format='jd', scale='utc')
    _, jd_tdb, moon, sun, M = S.epoch_arrays(t)
    return dict(jd_utc=t.utc.jd, jd_tdb=jd_tdb, moon=moon, sun=sun, M=M, step_min=step_min)

def plane_in_me(plane: Plane, grid):
    """n, e, f of the plane expressed in the ME frame at every grid epoch (N,3 each)."""
    n_i, e_i, f_i = plane.vectors_icrf(grid['jd_tdb'])
    M = grid['M']
    return [np.einsum('nij,nj->ni', M, v) for v in (n_i, e_i, f_i)]

def compatibility_fraction(plane: Plane, grid, pix_me, delta_deg, chunk=200):
    """Fraction of grid epochs at which each pixel lies within delta of the plane (orbit-plane compatibility
    envelope; not a reachability statement)."""
    n_me, _, _ = plane_in_me(plane, grid); s = np.sin(np.radians(delta_deg))
    cnt = np.zeros(len(pix_me))
    for a in range(0, len(n_me), chunk):
        cnt += (np.abs(n_me[a:a + chunk] @ pix_me.T) <= s).sum(axis=0)
    return cnt / len(n_me)

def overflights(plane: Plane, grid, pix_me, phases_rad, delta_max_deg, chunk=144, time_mask=None, pixel_mask=None):
    """Overflight opportunities: for each phase u0, every time the spacecraft's argument of latitude equals the
    in-plane angle of a pixel while the pixel is within delta_max of the plane. Returns a list (one per phase) of
    dicts with arrays pixel, jd_utc (overflight time), cross_deg (signed cross-track angle at that time), gi (index
    of the grid step that contains the overflight). Optional time_mask (per grid step) and pixel_mask restrict the
    output to useful candidates (the overflight times themselves are unaffected)."""
    n_me, e_me, f_me = plane_in_me(plane, grid)
    jd_u = grid['jd_utc']; jd_t = grid['jd_tdb']; dtd = grid['step_min'] / 1440.0
    s_lim = np.sin(np.radians(delta_max_deg + 0.3))
    omega = plane.mean_motion * 86400.0                                # rad/day
    step_ang = omega * dtd
    out = [dict(pixel=[], jd_utc=[], cross_deg=[]) for _ in phases_rad]
    for a in range(0, len(jd_u) - 1, chunk):
        b = min(a + chunk, len(jd_u) - 1)
        S = n_me[a:b] @ pix_me.T                                        # (T, P)
        cand = np.abs(S) <= s_lim
        if time_mask is not None:
            cand &= (time_mask[a:b] | time_mask[a + 1:b + 1])[:, None]
        if pixel_mask is not None:
            cand &= pixel_mask[None, :]
        ti, pi = np.nonzero(cand)
        if len(ti) == 0:
            continue
        ti_g = ti + a
        pe = np.einsum('ij,ij->i', pix_me[pi], e_me[ti_g]); pf = np.einsum('ij,ij->i', pix_me[pi], f_me[ti_g])
        u_p = np.arctan2(pf, pe)
        for k, u0 in enumerate(phases_rad):
            u_sc = u0 + omega * (jd_t[ti_g] - plane.t_ref_jd)
            du = (u_sc - u_p + np.pi) % (2 * np.pi) - np.pi              # wrapped to (-pi, pi]
            hit = (du <= 0) & (du > -step_ang)
            if not hit.any():
                continue
            frac = -du[hit] / step_ang                                  # position of the crossing inside the step
            t_cross = jd_u[ti_g[hit]] + frac * dtd
            n_int = n_me[ti_g[hit]] * (1 - frac)[:, None] + n_me[ti_g[hit] + 1] * frac[:, None]
            n_int /= np.linalg.norm(n_int, axis=1, keepdims=True)
            cr = np.degrees(np.arcsin(np.clip(np.einsum('ij,ij->i', pix_me[pi[hit]], n_int), -1, 1)))
            keep = np.abs(cr) <= delta_max_deg
            out[k]['pixel'].append(pi[hit][keep].astype(np.int32)); out[k]['jd_utc'].append(t_cross[keep]); out[k]['cross_deg'].append(cr[keep].astype(np.float32))
            out[k].setdefault('gi', []).append((ti_g[hit][keep] + np.round(frac[keep]).astype(int)).astype(np.int32))
    for d in out:
        for key in ('pixel', 'jd_utc', 'cross_deg', 'gi'):
            d[key] = np.concatenate(d[key]) if d.get(key) else np.zeros(0, dtype=np.int32 if key in ('pixel', 'gi') else float)
    return out

def interp_rows(grid_jd, arr, jd):
    """Linear interpolation of arr (N, ...) sampled at grid_jd to times jd."""
    x = (jd - grid_jd[0]) / (grid_jd[1] - grid_jd[0])
    i = np.clip(np.floor(x).astype(int), 0, len(grid_jd) - 2); f = (x - i)
    f = f.reshape(f.shape + (1,) * (arr.ndim - 1))
    return arr[i] * (1 - f) + arr[i + 1] * f

def geocentric_angles_at(grid, pix_me, pixel, jd_utc):
    """Geocentric emission and solar incidence (deg) of pixels at arbitrary times (interpolated ephemeris)."""
    moon = interp_rows(grid['jd_utc'], grid['moon'], jd_utc); sun = interp_rows(grid['jd_utc'], grid['sun'], jd_utc)
    M = interp_rows(grid['jd_utc'], grid['M'], jd_utc)
    p = pix_me[pixel]
    n_icrf = np.einsum('nji,nj->ni', M, p)                            # M^T p
    pos = moon + n_icrf * R_MOON
    d = -pos; d /= np.linalg.norm(d, axis=1, keepdims=True)
    s = sun - pos; s /= np.linalg.norm(s, axis=1, keepdims=True)
    em = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', n_icrf, d), -1, 1)))
    inc = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', n_icrf, s), -1, 1)))
    return em, inc

def deorbit_trajectory(altitude_km=100.0, dv_retro_m_s=25.0):
    """Two-body descent after an in-plane retrograde burn from a circular orbit: returns (impact speed km/s,
    flight-path angle below horizontal at impact deg, flight time s, central angle travelled from the burn deg)."""
    a0 = R_MOON + altitude_km
    v0 = np.sqrt(MU_MOON / a0) - dv_retro_m_s / 1000.0
    eps = v0 ** 2 / 2 - MU_MOON / a0; h = a0 * v0; a = -MU_MOON / (2 * eps)
    e = np.sqrt(max(0.0, 1 - h ** 2 / (MU_MOON * a)))
    if a * (1 - e) > R_MOON:
        return None
    v_imp = np.sqrt(2 * (eps + MU_MOON / R_MOON))
    gamma = np.degrees(np.arccos(np.clip(h / (R_MOON * v_imp), -1, 1)))
    nu_imp = np.arccos(np.clip((a * (1 - e ** 2) / R_MOON - 1) / e, -1, 1))   # true anomaly at impact (descending: 2pi - nu)
    def M_of(nu):
        E_ = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(nu / 2))
        return E_ - e * np.sin(E_)
    n = np.sqrt(MU_MOON / a ** 3)
    t = (M_of(np.pi) - M_of(nu_imp)) / n                               # apolune (burn) to impact
    return float(v_imp), float(gamma), float(abs(t)), float(np.degrees(np.pi - nu_imp))

def planes_through_point(jd_utc_epoch, lat_deg, lon_deg, inclination_deg=90.0, jd_ref_utc=None):
    """Node longitudes (ME, at the reference epoch) of the two planes of the given inclination that contain the point
    at the epoch (ascending and descending passes), using the full ICRF->ME rotation at both epochs."""
    from astropy.time import Time
    jd_t = Time(jd_utc_epoch, format='jd', scale='utc').tdb.jd
    p = E.latlon_to_vec(np.array([lat_deg]), np.array([lon_deg]), 1.0)[0]
    i = np.radians(inclination_deg)
    # node longitude O (ME at the epoch) such that p . n(O) = 0: sin i (px sin O - py cos O) + pz cos i = 0
    A, B, C = np.sin(i) * p[0], -np.sin(i) * p[1], np.cos(i) * p[2]
    r = np.hypot(A, B)
    if abs(C) > r:
        return []
    phi = np.arctan2(B, A); base = np.arcsin(-C / r)
    sols = [(base - phi), (np.pi - base - phi)]
    out = []
    M_t = E.icrf_to_me(jd_t)
    jd_ref_t = Time(jd_ref_utc, format='jd', scale='utc').tdb.jd if jd_ref_utc else jd_t
    M_ref = E.icrf_to_me(jd_ref_t)
    for O in sols:
        n_me_t = np.array([np.sin(i) * np.sin(O), -np.sin(i) * np.cos(O), np.cos(i)])
        e_me_t = np.array([np.cos(O), np.sin(O), 0.0])
        n_ref = M_ref @ (M_t.T @ n_me_t); e_ref = M_ref @ (M_t.T @ e_me_t)
        # node longitude at t_ref: direction of z x n (ascending node) in the ME frame at t_ref
        node = np.cross([0, 0, 1.0], n_ref); node /= np.linalg.norm(node)
        incl_ref = np.degrees(np.arccos(np.clip(n_ref[2], -1, 1)))
        f_me_t = np.cross(n_me_t, e_me_t)
        u_site = np.arctan2(p @ f_me_t, p @ e_me_t)
        northbound = np.cos(u_site) * f_me_t[2] > 0                      # d(position)/du has a positive z component
        out.append(dict(node_ref_deg=float(np.degrees(np.arctan2(node[1], node[0])) % 360), inclination_ref_deg=float(incl_ref),
                        pass_type='northbound' if northbound else 'southbound'))
    return out

def propagate_descent(plane: Plane, phase_rad, jd_burn_tdb, dv_m_s, step_s=1.0, t_max_s=4000.0):
    """Numerical check of the burn-to-impact mapping (re-audit GE-01): state on the circular orbit at the burn epoch,
    in-plane retrograde burn of dv, RK4 two-body integration in the ICRF until the reference sphere is reached.
    Vectorised over arrays of phases and burn epochs. Returns (impact TDB JD, impact unit vectors in the ME frame)."""
    phase_rad = np.atleast_1d(phase_rad).astype(float); jd_b = np.atleast_1d(jd_burn_tdb).astype(float)
    a = R_MOON + plane.altitude_km; n = plane.mean_motion
    n_i, e_i, f_i = plane.vectors_icrf(jd_b)
    u = phase_rad + n * (jd_b - plane.t_ref_jd) * 86400.0
    r = a * (np.cos(u)[:, None] * e_i + np.sin(u)[:, None] * f_i)
    v = a * n * (-np.sin(u)[:, None] * e_i + np.cos(u)[:, None] * f_i)
    v *= (1 - dv_m_s / 1000.0 / np.linalg.norm(v, axis=1))[:, None]
    def acc(x):
        d = np.linalg.norm(x, axis=1, keepdims=True)
        return -MU_MOON * x / d ** 3
    t = np.zeros(len(u)); done = np.zeros(len(u), bool); t_imp = np.full(len(u), np.nan); r_imp = np.zeros_like(r)
    for _ in range(int(t_max_s / step_s)):
        k1v = acc(r); k1r = v
        k2v = acc(r + 0.5 * step_s * k1r); k2r = v + 0.5 * step_s * k1v
        k3v = acc(r + 0.5 * step_s * k2r); k3r = v + 0.5 * step_s * k2v
        k4v = acc(r + step_s * k3r); k4r = v + step_s * k3v
        r_new = r + step_s / 6 * (k1r + 2 * k2r + 2 * k3r + k4r); v_new = v + step_s / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        d0 = np.linalg.norm(r, axis=1); d1 = np.linalg.norm(r_new, axis=1)
        hit = ~done & (d1 <= R_MOON)
        if hit.any():
            fr = ((d0[hit] - R_MOON) / (d0[hit] - d1[hit]))[:, None]
            r_imp[hit] = r[hit] * (1 - fr) + r_new[hit] * fr; t_imp[hit] = t[hit] + fr[:, 0] * step_s; done |= hit
        r, v = np.where(done[:, None], r, r_new), np.where(done[:, None], v, v_new); t = t + step_s
        if done.all():
            break
    jd_imp = jd_b + t_imp / 86400.0
    M = np.array([E.icrf_to_me(j) for j in jd_imp])
    p = np.einsum('nij,nj->ni', M, r_imp / np.linalg.norm(r_imp, axis=1, keepdims=True))
    return jd_imp, p
