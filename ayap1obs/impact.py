"""Impact energy, flash light curves and spectra, ejecta and crater scaling.

Every function states its model and inputs; nothing here is a mission prediction until combined with the
scenario tables in config/scenarios.yaml (which are labelled 'mission-consistent scenario', 'illustrative' or
'bound').  Photometric system: Vega magnitudes; bandpasses approximated as rectangular with the effective
wavelengths/widths and zero points of Bessell et al. (1998) (V, Rc, Ic) and Cohen et al. (2003) (2MASS J, H, Ks).
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

H_PLANCK = 6.62607015e-34; C_LIGHT = 2.99792458e8; K_B = 1.380649e-23; SIGMA_SB = 5.670374419e-8
G_MOON = 1.62     # m/s^2
AU_M = 1.495978707e11
D_MOON_M = 3.844e8   # mean Earth-Moon distance (the geometry module supplies exact ranges per epoch)

# Bands: effective wavelength (m), width (m), Vega zero point F_lambda (W m^-2 m^-1) at the effective wavelength
BANDS = {
    'V':  dict(lam=0.551e-6, width=0.088e-6, f0=3.63e-2),
    'Rc': dict(lam=0.647e-6, width=0.157e-6, f0=2.18e-2),
    'Ic': dict(lam=0.789e-6, width=0.150e-6, f0=1.13e-2),
    'J':  dict(lam=1.235e-6, width=0.162e-6, f0=3.13e-3),
    'H':  dict(lam=1.662e-6, width=0.251e-6, f0=1.13e-3),
    'Ks': dict(lam=2.159e-6, width=0.262e-6, f0=4.28e-4),
    'broad': dict(lam=0.55e-6, width=0.30e-6, f0=3.5e-2),   # unfiltered RGB/CMOS 0.40-0.70 um, Vega-mean zero point (approx.)
}
# Zero points: Bessell et al. (1998) F_lambda(Vega, m=0) in erg cm^-2 s^-1 A^-1: V 3.63e-9, Rc 2.18e-9, Ic 1.13e-9;
# Cohen et al. (2003): J 3.13e-10, H 1.13e-10, Ks 4.28e-11.  1 erg cm^-2 s^-1 A^-1 = 1e-7 J /(1e-4 m^2 s 1e-10 m)
# = 1e7 W m^-2 m^-1, hence V: 3.63e-2 W m^-2 m^-1.

def kinetic_energy(mass_kg, v_km_s):
    return 0.5 * mass_kg * (v_km_s * 1e3) ** 2

def planck_lambda(lam, T):
    """Spectral radiance B_lambda (W m^-2 m^-1 sr^-1)."""
    x = H_PLANCK * C_LIGHT / (lam * K_B * T)
    return 2 * H_PLANCK * C_LIGHT ** 2 / lam ** 5 / np.expm1(np.minimum(x, 700.0))

def band_fraction(T, band, nsub=200):
    """Fraction of blackbody bolometric power emitted inside the (rectangular) band at temperature T."""
    b = BANDS[band]
    lam = np.linspace(b['lam'] - b['width'] / 2, b['lam'] + b['width'] / 2, nsub)
    return np.trapezoid(planck_lambda(lam, T), lam) * np.pi / (SIGMA_SB * T ** 4)

def visible_fraction(T, lam1=0.40e-6, lam2=0.90e-6, nsub=400):
    lam = np.linspace(lam1, lam2, nsub)
    return np.trapezoid(planck_lambda(lam, T), lam) * np.pi / (SIGMA_SB * T ** 4)

@dataclass
class FlashModel:
    """Cooling-blackbody flash.

    Inputs: kinetic energy E_k (J); eta_vis = fraction of E_k radiated between 0.40 and 0.90 um over the whole
    event; T0, Tfloor: initial and final temperatures (K) of the radiating material (exponential cooling with
    e-folding time tau_T); tau_L: e-folding time of the bolometric luminosity (s); solid angle convention:
    'isotropic' (4 pi) or 'hemispheric' (2 pi, radiating surface on the ground - brighter by 0.75 mag).
    The bolometric energy is set so that the visible-band energy equals eta_vis * E_k.
    """
    E_k: float
    eta_vis: float = 1e-4
    T0: float = 2500.0
    Tfloor: float = 1200.0
    tau_T: float = 0.5
    tau_L: float = 0.5
    solid_angle: str = 'isotropic'
    def temperature(self, t):
        return self.Tfloor + (self.T0 - self.Tfloor) * np.exp(-np.asarray(t) / self.tau_T)
    def _lum_shape(self, t):
        return np.exp(-np.asarray(t) / self.tau_L) / self.tau_L     # integrates to 1
    def bolometric_energy(self):
        """E_bol such that integral of L_bol(t) * f_vis(T(t)) dt = eta_vis * E_k."""
        t = np.linspace(0, 10 * max(self.tau_L, self.tau_T), 2000)
        fv = np.array([visible_fraction(T) for T in self.temperature(t)])
        w = np.trapezoid(self._lum_shape(t) * fv, t)
        return self.eta_vis * self.E_k / w
    def luminosity(self, t):
        return self.bolometric_energy() * self._lum_shape(t)
    def band_flux(self, t, band, distance_m=D_MOON_M):
        """F_lambda at Earth in band (W m^-2 m^-1) vs time."""
        omega = 4 * np.pi if self.solid_angle == 'isotropic' else 2 * np.pi
        T = self.temperature(t)
        frac = np.array([band_fraction(Ti, band) for Ti in np.atleast_1d(T)])
        return self.luminosity(t) * frac / (omega * distance_m ** 2) / BANDS[band]['width']
    def magnitude(self, t, band, distance_m=D_MOON_M):
        F = self.band_flux(t, band, distance_m)
        with np.errstate(divide='ignore'):
            return -2.5 * np.log10(F / BANDS[band]['f0'])
    def peak_magnitude(self, band, distance_m=D_MOON_M):
        return float(self.magnitude(np.array([0.0]), band, distance_m)[0])
    def exposure_averaged_magnitude(self, band, t_exp, t_start=0.0, distance_m=D_MOON_M):
        t = np.linspace(t_start, t_start + t_exp, 200)
        F = np.trapezoid(self.band_flux(t, band, distance_m), t) / t_exp
        return float(-2.5 * np.log10(F / BANDS[band]['f0']))
    def fluence(self, band, distance_m=D_MOON_M):
        """Time-integrated band fluence at Earth (J m^-2) and the equivalent 1-s magnitude."""
        t = np.linspace(0, 10 * max(self.tau_L, self.tau_T), 2000)
        F = np.trapezoid(self.band_flux(t, band, distance_m), t) * BANDS[band]['width']
        m1s = -2.5 * np.log10(F / (BANDS[band]['f0'] * BANDS[band]['width'] * 1.0))
        return float(F), float(m1s)
    def duration_above(self, band, mag_limit, distance_m=D_MOON_M):
        t = np.linspace(0, 10 * max(self.tau_L, self.tau_T), 4000)
        m = self.magnitude(t, band, distance_m)
        ok = m < mag_limit
        return float(t[ok].max() - t[ok].min()) if ok.any() else 0.0

def luminous_efficiency_prior(v_km_s, rng, n, kind='slow-impact-wide'):
    """Log10 eta_vis samples.  'slow-impact-wide': log-uniform on [-6, -2.5] (no calibration at < 2.4 km/s,
    bounded above by the natural-flash range 5e-4..3e-3 at 16-72 km/s and below by the requirement that the
    SMART-1 flash (5.7e8 J) saturated a 10-s WIRCam exposure at 2.12 um).  'v3-scaled': central value
    1e-3 * (v/5)^3 (Ernst & Schultz intensity ~ v^3 trend, anchored at ~1e-3 near 5 km/s) with 0.7 dex scatter."""
    if kind == 'slow-impact-wide':
        return rng.uniform(-6.0, -2.5, n)
    if kind == 'v3-scaled':
        c = np.log10(1e-3 * (v_km_s / 5.0) ** 3)
        return rng.normal(c, 0.7, n)
    raise ValueError(kind)

# ---------------------------------------------------------------- ejecta ------------------------------------
def ejecta_mass_above_speed(m_imp, U_km_s, v_m_s, rho_t=1500.0, rho_i=400.0, k=0.3, mu=0.41, nu=0.4, angle_deg=90.0, angle_floor_deg=15.0):
    """Housen & Holsapple (2011) point-source ejecta scaling: cumulative mass ejected faster than v (kg).
    M(>v)/m = (3k/4pi) (rho/delta) [ (v/U) (rho/delta)^nu ]^(-3 mu)   (valid for v << U, gravity regime, porous
    target parameters k=0.3, mu=0.41, nu=0.4).  rho_i is the *bulk* impactor density (a hollow spacecraft bus
    ~100-500 kg/m^3).  For oblique impacts the vertical velocity component U sin(theta) is used, with the same 15-deg
    floor as crater_radius (angle_deg=90 reproduces the vertical/full-speed case and serves as an upper bound)."""
    U = U_km_s * 1e3 * np.sin(np.radians(max(angle_deg, angle_floor_deg)))
    x = (np.asarray(v_m_s) / U) * (rho_t / rho_i) ** nu
    M = (3 * k / (4 * np.pi)) * (rho_t / rho_i) * x ** (-3 * mu) * m_imp
    return np.minimum(M, 100.0 * m_imp)

def ballistic_max_height(v_m_s, launch_angle_deg=45.0):
    return (np.asarray(v_m_s) * np.sin(np.radians(launch_angle_deg))) ** 2 / (2 * G_MOON)

def ballistic_flight_time(v_m_s, launch_angle_deg=45.0):
    return 2 * np.asarray(v_m_s) * np.sin(np.radians(launch_angle_deg)) / G_MOON

def speed_for_height(h_m, launch_angle_deg=45.0):
    return np.sqrt(2 * G_MOON * np.asarray(h_m)) / np.sin(np.radians(launch_angle_deg))

def plume_magnitude(mass_kg, grain_radius_m=1e-5, rho_grain=3000.0, albedo=0.1, phase_func=0.3,
                    distance_m=D_MOON_M, r_au=1.0, m_sun=-26.74, tau_opt=None):
    """Integrated V magnitude of a sunlit dust cloud of mass M (kg) made of grains of radius a (optically thin).
    Geometric cross-section sigma = 3 M / (4 rho a).  m = m_sun - 2.5 log10( p Phi sigma / (pi d^2) ) + 5 log10(r_au).
    Validated against the full Moon: sigma = pi R^2, p = 0.12, Phi = 1 -> -12.7 mag."""
    sigma = 3 * mass_kg / (4 * rho_grain * grain_radius_m)
    if tau_opt is not None:   # cap the effective cross-section when optically thick
        sigma = np.minimum(sigma, tau_opt)
    return m_sun - 2.5 * np.log10(albedo * phase_func * sigma / (np.pi * distance_m ** 2)) + 5 * np.log10(r_au)

def surface_brightness(mag, area_arcsec2):
    return mag + 2.5 * np.log10(area_arcsec2)

# ---------------------------------------------------------------- crater -------------------------------------
CRATER_PARAMS = {
    # Holsapple (1993) / Holsapple & Housen pi-scaling parameter sets (K1, K2, mu, nu, Y Pa)
    'dry sand (gravity)': dict(K1=0.24, K2=0.0, mu=0.41, nu=0.4, Y=0.0),
    'cohesive soil': dict(K1=0.132, K2=0.26, mu=0.41, nu=0.4, Y=1.8e5),
    'lunar regolith (weak)': dict(K1=0.132, K2=0.26, mu=0.41, nu=0.4, Y=1.0e4),
}

def crater_radius(m_imp, U_km_s, angle_deg=90.0, rho_t=1500.0, rho_i=400.0, params='lunar regolith (weak)',
                  g=G_MOON, angle_floor_deg=15.0, K_r=1.1):
    """Transient crater radius (m) from Holsapple (1993) / Holsapple & Housen pi-scaling (volume form):
    pi_V = rho V / m = K1 [ pi2 pi4^((6nu-2-mu)/(3mu)) + (K2 pi3 pi4^((6nu-2)/(3mu)))^((2+mu)/2) ]^(-3mu/(2+mu)),
    pi2 = g a / U^2, pi3 = Y / (rho U^2), pi4 = rho/delta (a = impactor radius from the bulk density delta),
    R = K_r V^(1/3) with K_r = 1.1.  The vertical velocity component U sin(theta) is used, with an angle floor
    (default 15 deg) because the vertical-component rule breaks down for the very shallow (1-5 deg) grazing
    impacts of orbital decay (GRAIL, SMART-1 craters are larger/elongated); the floor is a declared assumption
    tuned so that GRAIL (130 kg, 1.7 km/s) gives ~5 m.  Final rim diameter ~1.2-1.3 x transient."""
    p = CRATER_PARAMS[params]
    U = U_km_s * 1e3 * np.sin(np.radians(max(angle_deg, angle_floor_deg)))
    a = (3 * m_imp / (4 * np.pi * rho_i)) ** (1 / 3)
    pi2 = g * a / U ** 2
    pi3 = p['Y'] / (rho_t * U ** 2)
    pi4 = rho_t / rho_i
    mu, nu = p['mu'], p['nu']
    term = pi2 * pi4 ** ((6 * nu - 2 - mu) / (3 * mu)) + (p['K2'] * pi3 * pi4 ** ((6 * nu - 2) / (3 * mu))) ** ((2 + mu) / 2)
    piV = p['K1'] * term ** (-3 * mu / (2 + mu))
    V = piV * m_imp / rho_t
    return K_r * V ** (1.0 / 3.0)

def crater_diameter_range(m_imp, U_km_s, angle_deg):
    """Spread over parameter sets, bulk densities and rim factors -> (min, median, max) final-rim diameter (m)."""
    vals = []
    for prm in CRATER_PARAMS:
        for rho_i in (150.0, 400.0, 1000.0):
            for rim in (1.2, 1.3):
                vals.append(2 * crater_radius(m_imp, U_km_s, angle_deg, rho_i=rho_i, params=prm) * rim)
    vals = np.array(vals)
    return float(vals.min()), float(np.median(vals)), float(vals.max())

# ---------------------------------------------------------------- SMART-1 conditional bound --------------------------
def smart1_saturation_eta(T0=2500.0, tau=0.5, n_sat_e=(4e4, 1.3e5), overexposure=(1.0, 10.0), area_m2=8.0,
                          throughput=0.35, seeing_arcsec=0.8, pixel_arcsec=0.3, filt_center=2.122e-6, filt_width=0.032e-6,
                          t_exp=10.0, mass_kg=285.0, v_km_s=2.0, distance_m=3.8e8):
    """Visible-band luminous efficiency eta_vis at which the SMART-1 impact (Veillet & Foing 2007: CFHT/WIRCam,
    10-s exposure through a 2.122-um, 32-nm filter, 'extremely over-exposed') would bring the peak pixel to
    `overexposure` x the saturation level `n_sat_e`, in the cooling-blackbody flash model.  All camera parameters are
    DECLARED ASSUMPTIONS (the 2006 settings are unpublished).  Returns (eta_min, eta_max) over the parameter ranges."""
    fm = FlashModel(E_k=kinetic_energy(mass_kg, v_km_s), eta_vis=1.0, T0=T0, Tfloor=min(1200.0, T0 - 100), tau_T=tau, tau_L=tau)
    t = np.linspace(0, t_exp, 4000)
    omega = 4 * np.pi
    lam = np.linspace(filt_center - filt_width / 2, filt_center + filt_width / 2, 50)
    T = fm.temperature(t)
    frac = np.array([np.trapezoid(planck_lambda(lam, Ti), lam) * np.pi / (SIGMA_SB * Ti ** 4) for Ti in T])
    energy_at_earth = np.trapezoid(fm.luminosity(t) * frac, t) / (omega * distance_m ** 2)     # J m^-2 for eta_vis = 1
    photons = energy_at_earth * area_m2 * throughput * filt_center / (H_PLANCK * C_LIGHT)
    sig_pix = seeing_arcsec / 2.355 / pixel_arcsec
    peak_frac = min(1.0, 1.0 / (2 * np.pi * sig_pix ** 2))
    n_peak_eta1 = photons * peak_frac
    lo = min(n_sat_e) * min(overexposure) / n_peak_eta1
    hi = max(n_sat_e) * max(overexposure) / n_peak_eta1
    return lo, hi
