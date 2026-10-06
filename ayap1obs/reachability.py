"""Dynamic reachability of impact sites from a 100-km polar circular lunar orbit (scenario families).

The AYAP-1 orbit plane orientation (node longitude at a reference epoch), nodal drift, the terminal-burn
propellant budget and the operational constraints are NOT published.  This module therefore evaluates
reachability as a *conditional* property under declared scenario families:

* node longitude at reference epoch: Omega0 in [0, 360) deg (uniform family, or sampled on a grid)
* nodal drift relative to the inertial frame: dOmega/dt (deg/day), default 0 (small for polar orbits), with
  the Moon's sidereal rotation (13.1763 deg/day) moving the ground track westward in the ME frame
* inclination: 90 deg nominal (88-92 explored)
* cross-track tolerance: max plane change the terminal manoeuvre can buy (deg), from the Delta-v budget via
  dv = 2 v sin(di/2) with v = 1.633 km/s (100 km circular speed)
* along-track freedom: the de-orbit burn can be timed anywhere in the orbit, so any latitude on the current
  ground track is reachable; the arrival time at that latitude is then fixed by the orbital phase.

Reachability of a (site, epoch) pair = the site lies within the cross-track tolerance of the ground track at
that epoch.  Opportunities for a site are the epochs when this holds (roughly twice per sidereal month,
ascending and descending passes, each lasting a few consecutive orbits).
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

MU_MOON = 4902.800066     # km^3/s^2
R_MOON = 1737.4
OMEGA_MOON_DEG_DAY = 13.17635815   # sidereal rotation rate (pck00011 W rate)

@dataclass
class OrbitScenario:
    name: str
    omega0_deg: float          # node longitude in the ME frame at t_ref (deg E)
    t_ref_jd: float            # reference epoch (JD, UTC)
    altitude_km: float = 100.0
    inclination_deg: float = 90.0
    node_drift_deg_day: float = 0.0   # inertial nodal drift (deg/day), positive eastward
    u0_deg: float = 0.0        # argument of latitude at t_ref (deg)
    cross_track_tol_deg: float = 0.6  # half-width of reachable band around the track (deg)
    @property
    def period_s(self):
        a = R_MOON + self.altitude_km
        return 2 * np.pi * np.sqrt(a ** 3 / MU_MOON)
    @property
    def speed_km_s(self):
        return np.sqrt(MU_MOON / (R_MOON + self.altitude_km))

def plane_change_dv(di_deg, v=1.633):
    return 2 * v * np.sin(np.radians(di_deg) / 2) * 1000.0   # m/s

def node_longitude(sc: OrbitScenario, jd):
    """Node longitude (deg E, ME frame) at epoch(s) jd."""
    dt = np.asarray(jd) - sc.t_ref_jd
    return (sc.omega0_deg - OMEGA_MOON_DEG_DAY * dt + sc.node_drift_deg_day * dt) % 360.0

def ground_track(sc: OrbitScenario, jd):
    """Sub-spacecraft latitude/longitude (deg) at epoch(s) jd."""
    dt = (np.asarray(jd) - sc.t_ref_jd) * 86400.0
    u = np.radians(sc.u0_deg) + 2 * np.pi * dt / sc.period_s
    i = np.radians(sc.inclination_deg)
    lat = np.degrees(np.arcsin(np.sin(i) * np.sin(u)))
    dlon = np.degrees(np.arctan2(np.cos(i) * np.sin(u), np.cos(u)))
    lon = (node_longitude(sc, jd) + dlon + 180.0) % 360.0 - 180.0
    return lat, lon

def cross_track_distance_deg(sc: OrbitScenario, jd, lat_deg, lon_deg):
    """Angular distance (deg) of surface points from the orbit plane's ground track at epoch jd (scalar epoch),
    i.e. the plane change needed to overfly them on this pass."""
    lam = np.radians(node_longitude(sc, jd))
    i = np.radians(sc.inclination_deg)
    # orbit normal in ME frame for node longitude lam and inclination i
    n = np.array([np.sin(i) * np.sin(lam), -np.sin(i) * np.cos(lam), np.cos(i)])
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    p = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=-1)
    return np.degrees(np.abs(np.arcsin(np.clip(p @ n, -1, 1))))

def reachable(sc: OrbitScenario, jd, lat_deg, lon_deg):
    return cross_track_distance_deg(sc, jd, lat_deg, lon_deg) <= sc.cross_track_tol_deg

def pass_times(sc: OrbitScenario, lat_deg, lon_deg, jd_start, jd_stop, step_min=10.0):
    """Epochs (JD) in [jd_start, jd_stop] when the site is within the cross-track tolerance (grouped passes).
    Returns list of (jd_centre, min_cross_track_deg, ascending_flag)."""
    jds = np.arange(jd_start, jd_stop, step_min / 1440.0)
    ct = cross_track_distance_deg(sc, jds[:, None], lat_deg, lon_deg).ravel() if False else np.array(
        [cross_track_distance_deg(sc, j, lat_deg, lon_deg) for j in jds])
    ok = ct <= sc.cross_track_tol_deg
    out = []
    if not ok.any():
        return out
    idx = np.where(ok)[0]
    groups = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    for g in groups:
        k = g[np.argmin(ct[g])]
        lat_t, lon_t = ground_track(sc, jds[k])
        # ascending if node longitude is close to site longitude (vs +180)
        dl = (node_longitude(sc, jds[k]) - lon_deg + 180) % 360 - 180
        out.append((float(jds[k]), float(ct[k]), bool(abs(dl) < 90)))
    return out

def impact_time_on_pass(sc: OrbitScenario, jd_pass, lat_deg, lon_deg):
    """Within the pass centred at jd_pass, the time at which the spacecraft reaches the site's latitude
    (ascending or descending leg chosen to match the pass).  Returns JD."""
    dl = (node_longitude(sc, jd_pass) - lon_deg + 180) % 360 - 180
    i = np.radians(sc.inclination_deg)
    u_site = np.arcsin(np.clip(np.sin(np.radians(lat_deg)) / np.sin(i), -1, 1))
    if abs(dl) >= 90:
        u_site = np.pi - u_site
    dt0 = (jd_pass - sc.t_ref_jd) * 86400.0
    u_now = np.radians(sc.u0_deg) + 2 * np.pi * dt0 / sc.period_s
    du = (u_site - u_now) % (2 * np.pi)
    if du > np.pi:
        du -= 2 * np.pi
    return jd_pass + du / (2 * np.pi) * sc.period_s / 86400.0

def ballistic_impact_conditions(altitude_km=100.0, dv_retro_m_s=22.0):
    """Impact speed and flight-path angle for a retrograde de-orbit burn from a circular orbit (two-body).
    Returns (v_impact km/s, angle_from_horizontal deg, time_to_impact s)."""
    a0 = R_MOON + altitude_km
    v0 = np.sqrt(MU_MOON / a0) - dv_retro_m_s / 1000.0
    eps = v0 ** 2 / 2 - MU_MOON / a0
    h = a0 * v0
    a = -MU_MOON / (2 * eps)
    e = np.sqrt(max(0.0, 1 - h ** 2 / (MU_MOON * a)))
    rp = a * (1 - e)
    if rp > R_MOON:
        return None
    v_imp = np.sqrt(2 * (eps + MU_MOON / R_MOON))
    cos_gamma = h / (R_MOON * v_imp)
    gamma = np.degrees(np.arccos(np.clip(cos_gamma, -1, 1)))
    # time from burn to impact: from true anomaly at r=a0 (apoapsis side) to r=R
    nu_imp = np.arccos(np.clip((a * (1 - e ** 2) / R_MOON - 1) / e, -1, 1))
    def M_of(nu):
        E_ = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(nu / 2))
        return E_ - e * np.sin(E_)
    n = np.sqrt(MU_MOON / a ** 3)
    t = (M_of(np.pi) - M_of(nu_imp)) / n
    return v_imp, gamma, t
