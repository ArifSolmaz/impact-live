"""Impact energy, flash light curves and spectra, flash priors, and crater scaling.

Every function states its model and inputs; nothing here is a mission prediction until combined with the
scenario tables in config/scenarios.yaml. Ejecta and plume models are in plume.py.

Photometric system: Vega magnitudes; bandpasses approximated as rectangular with the effective wavelengths,
widths and zero points of Bessell et al. (1998) (V, Rc, Ic) and Cohen et al. (2003) (2MASS J, H, Ks). 'broad' is an
unfiltered RGB/CMOS band (0.40-0.70 um) used for phones, video and amateur cameras; it is not V.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from functools import lru_cache

H_PLANCK = 6.62607015e-34; C_LIGHT = 2.99792458e8; K_B = 1.380649e-23; SIGMA_SB = 5.670374419e-8
G_MOON = 1.62     # m/s^2
AU_M = 1.495978707e11
D_MOON_M = 3.844e8   # mean Earth-Moon distance; the geometry module supplies exact ranges per epoch and station

# Bands: effective wavelength (m), width (m), Vega zero point F_lambda (W m^-2 m^-1) at the effective wavelength
BANDS = {
    'V':  dict(lam=0.551e-6, width=0.088e-6, f0=3.63e-2),
    'Rc': dict(lam=0.647e-6, width=0.157e-6, f0=2.18e-2),
    'Ic': dict(lam=0.789e-6, width=0.150e-6, f0=1.13e-2),
    'J':  dict(lam=1.235e-6, width=0.162e-6, f0=3.13e-3),
    'H':  dict(lam=1.662e-6, width=0.251e-6, f0=1.13e-3),
    'Ks': dict(lam=2.159e-6, width=0.262e-6, f0=4.28e-4),
    'broad': dict(lam=0.55e-6, width=0.30e-6, f0=3.5e-2),   # unfiltered 0.40-0.70 um, Vega-mean zero point (approx.); NOT V
}
# Zero points: Bessell et al. (1998) F_lambda(Vega, m=0) in erg cm^-2 s^-1 A^-1: V 3.63e-9, Rc 2.18e-9, Ic 1.13e-9;
# Cohen et al. (2003): J 3.13e-10, H 1.13e-10, Ks 4.28e-11.  1 erg cm^-2 s^-1 A^-1 = 1e7 W m^-2 m^-1.

def kinetic_energy(mass_kg, v_km_s):
    return 0.5 * mass_kg * (np.asarray(v_km_s) * 1e3) ** 2

def planck_lambda(lam, T):
    """Spectral radiance B_lambda (W m^-2 m^-1 sr^-1)."""
    x = H_PLANCK * C_LIGHT / (lam * K_B * T)
    return 2 * H_PLANCK * C_LIGHT ** 2 / lam ** 5 / np.expm1(np.minimum(x, 700.0))

def band_fraction(T, band, nsub=200):
    """Fraction of blackbody bolometric power emitted inside the (rectangular) band at temperature T (scalar)."""
    b = BANDS[band]
    lam = np.linspace(b['lam'] - b['width'] / 2, b['lam'] + b['width'] / 2, nsub)
    return np.trapezoid(planck_lambda(lam, T), lam) * np.pi / (SIGMA_SB * T ** 4)

def visible_fraction(T, lam1=0.40e-6, lam2=0.90e-6, nsub=400):
    """Fraction of blackbody bolometric power between 0.40 and 0.90 um (the eta_vis band)."""
    lam = np.linspace(lam1, lam2, nsub)
    return np.trapezoid(planck_lambda(lam, T), lam) * np.pi / (SIGMA_SB * T ** 4)

def _fraction_vec(T, lam1, lam2, nsub):
    T = np.asarray(T, float); flat = T.ravel(); out = np.empty(flat.size)
    lam = np.linspace(lam1, lam2, nsub)
    for k in range(0, flat.size, 4000):
        t = flat[k:k + 4000, None]
        out[k:k + 4000] = np.trapezoid(planck_lambda(lam[None, :], t), lam, axis=1) * np.pi / (SIGMA_SB * t[:, 0] ** 4)
    return out.reshape(T.shape)

def band_fraction_vec(T, band, nsub=200):
    """Vectorised band_fraction over an array of temperatures."""
    b = BANDS[band]
    return _fraction_vec(T, b['lam'] - b['width'] / 2, b['lam'] + b['width'] / 2, nsub)

def visible_fraction_vec(T, nsub=400):
    return _fraction_vec(T, 0.40e-6, 0.90e-6, nsub)

def floor_temperature(T0):
    """Temperature the radiating material cools towards (K): 1200 K, or 0.8 T0 for cool sources (declared)."""
    return np.minimum(1200.0, 0.8 * np.asarray(T0, float))

SOLID_ANGLES = {'isotropic': 4 * np.pi, 'hemispheric': 2 * np.pi}

@dataclass
class FlashModel:
    """Cooling-blackbody flash.

    Inputs: kinetic energy E_k (J); eta_vis = fraction of E_k radiated between 0.40 and 0.90 um over the whole event;
    T0, Tfloor: initial and final temperatures (K) of the radiating material (exponential cooling with e-folding time
    tau_T); tau_L: e-folding time of the bolometric luminosity (s). The bolometric energy is set so that the
    visible-band energy equals eta_vis * E_k.
    solid_angle: 'isotropic' (4 pi, default) or 'hemispheric' (2 pi). The hemispheric value is a normalisation
    convention used only as a sensitivity case (a uniformly emitting hemisphere); it is not a model of a radiating
    ground surface, whose projected radiance depends on the viewing angle.
    """
    E_k: float
    eta_vis: float = 1e-4
    T0: float = 2500.0
    Tfloor: float = 1200.0
    tau_T: float = 0.5
    tau_L: float = 0.5
    solid_angle: str = 'isotropic'

    def __post_init__(self):
        if self.solid_angle not in SOLID_ANGLES:
            raise ValueError(f"solid_angle must be one of {list(SOLID_ANGLES)}, got {self.solid_angle!r}")
        if not self.Tfloor < self.T0:
            raise ValueError('Tfloor must be below T0')

    def temperature(self, t):
        return self.Tfloor + (self.T0 - self.Tfloor) * np.exp(-np.asarray(t, float) / self.tau_T)
    def _lum_shape(self, t):
        t = np.asarray(t, float)
        return np.where(t >= 0, np.exp(-np.maximum(t, 0) / self.tau_L) / self.tau_L, 0.0)     # integrates to 1
    def _tgrid(self, n=3000):
        tmax = 30 * max(self.tau_L, self.tau_T)
        return np.concatenate([[0.0], np.geomspace(1e-6 * min(self.tau_L, self.tau_T), tmax, n)])
    def bolometric_energy(self):
        """E_bol such that integral of L_bol(t) * f_vis(T(t)) dt = eta_vis * E_k."""
        t = self._tgrid()
        fv = np.array([visible_fraction(T) for T in self.temperature(t)])
        w = np.trapezoid(self._lum_shape(t) * fv, t)
        return self.eta_vis * self.E_k / w
    def radiative_efficiency(self):
        """Bolometric radiated energy as a fraction of the kinetic energy (physical consistency check: must be << 1)."""
        return self.bolometric_energy() / self.E_k
    def luminosity(self, t):
        return self.bolometric_energy() * self._lum_shape(t)
    def band_flux(self, t, band, distance_m=D_MOON_M):
        """F_lambda at the observer in band (W m^-2 m^-1) vs time (zero before the onset at t = 0)."""
        T = self.temperature(np.maximum(np.atleast_1d(t), 0.0))
        frac = np.array([band_fraction(Ti, band) for Ti in T])
        return self.luminosity(np.atleast_1d(t)) * frac / (SOLID_ANGLES[self.solid_angle] * distance_m ** 2) / BANDS[band]['width']
    def magnitude(self, t, band, distance_m=D_MOON_M):
        F = self.band_flux(t, band, distance_m)
        with np.errstate(divide='ignore'):
            return -2.5 * np.log10(F / BANDS[band]['f0'])
    def onset_magnitude(self, band, distance_m=D_MOON_M):
        """Magnitude at the onset (t = 0)."""
        return float(self.magnitude(np.array([0.0]), band, distance_m)[0])
    def peak_magnitude(self, band, distance_m=D_MOON_M, return_time=False):
        """True maximum of the band light curve. Cooling can move the band maximum after the onset (notably in the
        near infrared for hot sources); the visible bands normally peak at the onset."""
        tau = max(self.tau_L, self.tau_T)
        t = np.concatenate([[0.0], np.geomspace(1e-4 * tau, 4 * tau, 300)])
        F = self.band_flux(t, band, distance_m)
        k = int(np.argmax(F))
        if 0 < k < len(t) - 1:   # refine with a parabola in log flux
            tt = np.linspace(t[k - 1], t[k + 1], 41); FF = self.band_flux(tt, band, distance_m); k2 = int(np.argmax(FF)); tpk, Fpk = tt[k2], FF[k2]
        else:
            tpk, Fpk = t[k], F[k]
        m = float(-2.5 * np.log10(Fpk / BANDS[band]['f0']))
        return (m, float(tpk)) if return_time else m
    def band_energy(self, band, t1, t2, distance_m=D_MOON_M):
        """Band fluence (J m^-2) received between t1 and t2 (s after the onset); zero before the onset."""
        a, b = max(t1, 0.0), max(t2, 0.0)
        if b <= a:
            return 0.0
        t = np.linspace(a, b, 400) if (b - a) < 0.05 * self.tau_L else np.concatenate([np.linspace(a, min(b, a + 0.05 * self.tau_L), 200), np.geomspace(min(b, a + 0.05 * self.tau_L) + 1e-9, b, 400)])
        return float(np.trapezoid(self.band_flux(t, band, distance_m), t) * BANDS[band]['width'])
    def exposure_averaged_magnitude(self, band, t_exp, t_start=0.0, distance_m=D_MOON_M):
        """Magnitude of a steady source that would give the same counts as the flash in an exposure [t_start,
        t_start + t_exp] (the source is absent before the onset; an exposure that starts before the onset collects
        only the part after it, divided by the full exposure time)."""
        E = self.band_energy(band, t_start, t_start + t_exp, distance_m)
        if E <= 0:
            return np.inf
        return float(-2.5 * np.log10(E / t_exp / BANDS[band]['width'] / BANDS[band]['f0']))
    def fluence(self, band, distance_m=D_MOON_M):
        """Time-integrated band fluence (J m^-2) and the magnitude of a 1-s source with the same fluence."""
        F = self.band_energy(band, 0.0, 30 * max(self.tau_L, self.tau_T), distance_m)
        return F, float(-2.5 * np.log10(F / (BANDS[band]['f0'] * BANDS[band]['width'] * 1.0)))
    def duration_above(self, band, mag_limit, distance_m=D_MOON_M):
        t = np.linspace(0, 10 * max(self.tau_L, self.tau_T), 4000)
        m = self.magnitude(t, band, distance_m)
        ok = m < mag_limit
        return float(t[ok].max() - t[ok].min()) if ok.any() else 0.0

# ------------------------------------------------------------------ fast light-curve integrals ---------------------------
# With tau_T = tau_L = tau the light curve depends on time only through x = t / tau. The band energy received in an
# exposure [a, b] is  E_band = E_bol [G_b(b/tau; T0) - G_b(a/tau; T0)] / (Omega d^2)  with
#   G_b(x; T0) = int_0^x exp(-x') f_b(T(x')) dx',   T(x) = Tf + (T0 - Tf) exp(-x),
# and E_bol = eta_vis E_k / W(T0) with W(T0) = G_vis(inf; T0). The substitution s = exp(-x') turns the time integral
# into a temperature integral:
#   G_b(x; T0) = [Phi_b(T0) - Phi_b(T(x))] / (T0 - Tf),   Phi_b(T) = int^T f_b(T') dT',
# so every exposure integral, W and the band-peak rate follow from ONE temperature table per band. Phi_b is integrated
# with 3-point Gauss-Legendre quadrature on 0.5-K cells and interpolated with cubic Hermite polynomials that use its exact
# derivative f_b; the band fractions integrate the Planck function over the band with 400 (V etc.) or 800 (0.40-0.90 um)
# trapezoid nodes. scripts/validate_lightcurves.py compares these integrals with independent adaptive quadrature over the
# temperature and duration priors and reports the worst-case error (re-audit PH-N04: release 2.0 interpolated a 100-K x
# 700-node table bilinearly, with errors up to 0.15 mag for cool flashes).
T_TAB = np.arange(500.0, 7000.0 + 0.25, 0.5)
T0_MIN, T0_MAX = 1000.0, 6900.0
X_GRID = np.array([0.0, 40.0])          # largest x used for clipping (exp(-40) of the luminosity remains)
_GL_X, _GL_W = np.polynomial.legendre.leggauss(3)

def _band_f(T, band, fine=True):
    if band == 'vis':
        return _fraction_vec(T, 0.40e-6, 0.90e-6, 800 if fine else 400)
    b = BANDS[band]
    return _fraction_vec(T, b['lam'] - b['width'] / 2, b['lam'] + b['width'] / 2, 400 if fine else 200)

@lru_cache(maxsize=None)
def _phi_table(band):
    """(f_b at the nodes, Phi_b at the nodes) on T_TAB."""
    f = _band_f(T_TAB, band)
    h = np.diff(T_TAB); mid = 0.5 * (T_TAB[1:] + T_TAB[:-1])
    nodes = mid[:, None] + 0.5 * h[:, None] * _GL_X[None, :]
    inc = 0.5 * h * (_band_f(nodes, band) * _GL_W[None, :]).sum(axis=1)
    return f, np.concatenate([[0.0], np.cumsum(inc)])

def _phi(band, T):
    f, Phi = _phi_table(band)
    T = np.clip(np.asarray(T, float), T_TAB[0], T_TAB[-1]); dT = T_TAB[1] - T_TAB[0]
    i = np.clip(np.floor((T - T_TAB[0]) / dT).astype(np.int64), 0, len(T_TAB) - 2); t = (T - T_TAB[i]) / dT
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * Phi[i] + (t3 - 2 * t2 + t) * dT * f[i] + (-2 * t3 + 3 * t2) * Phi[i + 1] + (t3 - t2) * dT * f[i + 1]

def _f_interp(band, T):
    f, _ = _phi_table(band)
    T = np.clip(np.asarray(T, float), T_TAB[0], T_TAB[-1]); dT = T_TAB[1] - T_TAB[0]
    i = np.clip(np.floor((T - T_TAB[0]) / dT).astype(np.int64), 0, len(T_TAB) - 2); w = (T - T_TAB[i]) / dT
    return np.exp(np.log(np.maximum(f[i], 1e-300)) * (1 - w) + np.log(np.maximum(f[i + 1], 1e-300)) * w)   # log-linear

def _T0_clip(T0):
    return np.clip(np.asarray(T0, float), T0_MIN, T0_MAX)

def G_eval(band, T0, x):
    """G_b(x; T0) for arrays T0 (n,) and x (n, k) or broadcastable shapes (temperature-integral form, tabulated Phi_b;
    accuracy in outputs/validation/lightcurve_accuracy.md)."""
    T0 = _T0_clip(T0); x = np.clip(np.asarray(x, float), 0.0, X_GRID[-1])
    Tf = floor_temperature(T0)
    T0b = T0.reshape(T0.shape + (1,) * (x.ndim - T0.ndim)); Tfb = Tf.reshape(Tf.shape + (1,) * (x.ndim - Tf.ndim))
    Tx = Tfb + (T0b - Tfb) * np.exp(-x)
    return (_phi(band, T0b) - _phi(band, Tx)) / (T0b - Tfb)

def W_eval(T0):
    T0 = _T0_clip(T0); Tf = floor_temperature(T0)
    return (_phi('vis', T0) - _phi('vis', Tf)) / (T0 - Tf)

def band_rate_eval(band, T0, x):
    """dG_b/dx = exp(-x) f_b(T(x)) (band power per unit bolometric energy per unit x)."""
    T0 = _T0_clip(T0); x = np.clip(np.asarray(x, float), 0.0, X_GRID[-1]); Tf = floor_temperature(T0)
    T0b = T0.reshape(T0.shape + (1,) * (x.ndim - T0.ndim)); Tfb = Tf.reshape(Tf.shape + (1,) * (x.ndim - Tf.ndim))
    return np.exp(-x) * _f_interp(band, Tfb + (T0b - Tfb) * np.exp(-x))

@lru_cache(maxsize=None)
def _peak_table(band):
    """x at the band-rate maximum and the maximum rate on a 1-K grid of T0: maximise (T - Tf) f_b(T) / (T0 - Tf) over
    T in [Tf, T0] (T = T0 is the onset)."""
    T0s = np.arange(T0_MIN, T0_MAX + 0.5, 1.0); Tf = floor_temperature(T0s)
    s = np.linspace(0.0, 1.0, 4001)[None, :]                         # s = exp(-x) in [0, 1]
    T = Tf[:, None] + (T0s - Tf)[:, None] * s
    r = s * _f_interp(band, T)
    k = np.argmax(r, axis=1)
    s_pk = s[0, k]
    x_pk = np.where(s_pk > 0, -np.log(np.maximum(s_pk, 1e-12)), X_GRID[-1])
    return T0s, x_pk, r[np.arange(len(T0s)), k]

def xpeak_eval(band, T0):
    T0s, x_pk, _ = _peak_table(band)
    return np.interp(_T0_clip(T0), T0s, x_pk)

def peak_rate_eval(band, T0):
    T0s, _, r_pk = _peak_table(band)
    return np.exp(np.interp(_T0_clip(T0), T0s, np.log(r_pk)))

def peak_band_magnitude_fast(band, eta, E_k, T0, tau, distance_m=D_MOON_M):
    """Vectorised true band-peak magnitude: max over time of the band flux, from the band-rate maximum tabulated on a 1-K
    grid of T0 (accuracy in outputs/validation/lightcurve_accuracy.md)."""
    E_bol = eta * E_k / W_eval(T0)
    F = E_bol * peak_rate_eval(band, T0) / tau / (4 * np.pi * distance_m ** 2) / BANDS[band]['width']
    return -2.5 * np.log10(F / BANDS[band]['f0'])

# ------------------------------------------------------------------ flash priors --------------------------------------------
ETA_PRIORS = {
    'wide': 'log-uniform eta_vis between 1e-6 and 10^-2.5 (declared assumption; no calibrated visible-band efficiency is established for a spacecraft impact at these speeds)',
    'v-scaled': 'log-normal, centre 1e-3 (v / 5 km/s), 0.7 dex: an ad hoc sensitivity case (an intensity trend ~ v^3 at 4-6 km/s corresponds to eta ~ v at equal duration); anchor and scatter are assumptions, not fits',
}

def luminous_efficiency_prior(v_km_s, rng, n, kind='wide'):
    """log10 eta_vis samples.

    'wide': log-uniform on [-6, -2.5]. A declared assumption: the upper end is the natural-meteoroid flash range
      (about 5e-4 to 3e-3 at 16-72 km/s); nothing establishes the lower end. Laboratory trends point lower still: the
      fit of Swift et al. (2011) to Pyrex-into-regolith-simulant experiments at 2.4-5.75 km/s,
      eta = 1.5e-3 exp(-(9.3 km/s / v)^2), gives ~4e-10 at 2.4 km/s and ~1e-16 if extrapolated to 1.7 km/s (see
      lab_trend_eta). The SMART-1 near-infrared saturation (smart1_saturation_eta) constrains neither end of this
      visible-band prior.
    'v-scaled': log-normal with centre log10[1e-3 (v / 5)] and 0.7 dex scatter. Ernst & Schultz (2002) report a flash
      intensity rising as ~v^3 for 4.05-5.76 km/s; at equal duration and spectrum that implies eta ~ v (not v^3), so
      this case uses eta ~ v. The anchor 1e-3 at 5 km/s and the scatter are assumptions, so this is an ad hoc
      sensitivity case, not an empirically calibrated prior. (Release 1.0 used eta ~ v^3, which implied a radiated
      energy ~ v^5.)"""
    if kind in ('wide', 'slow-impact-wide'):
        return rng.uniform(-6.0, -2.5, n)
    if kind in ('v-scaled',):
        c = np.log10(1e-3 * (np.asarray(v_km_s, float) / 5.0))
        return rng.normal(c, 0.7, n)
    raise ValueError(kind)

def lab_trend_eta(v_km_s):
    """Swift et al. (2011) empirical fit eta = 1.5e-3 exp(-(9.3/v)^2) (v in km/s), measured for Pyrex into JSC-1a at
    2.4-5.75 km/s; values below 2.4 km/s are an extrapolation outside the tested range."""
    return 1.5e-3 * np.exp(-(9.3 / np.asarray(v_km_s, float)) ** 2)

T0_PRIORS = {
    'broad': 'log-normal T0, median 2995 K, sigma_ln 0.28, truncated to 1300-5800 K: chosen so that 85 % lies in 2000-4500 K as for natural flashes (Liakos et al. 2024) and the range matches the 1300-5800 K of Avdellidou & Vaubaillon (2019); natural flashes are an analogue, not a measurement for a spacecraft',
    'cool': 'uniform 1300-2500 K (cooler emission, a spacecraft-specific assumption)',
    'narrow': 'uniform 1800-3500 K (the release-1.0 assumption, kept for comparison)',
}

def temperature_prior(rng, n, kind='broad'):
    if kind == 'broad':
        out = np.empty(n); k = 0
        while k < n:
            x = np.exp(rng.normal(np.log(2995.0), 0.28, 2 * (n - k) + 16)); x = x[(x >= 1300) & (x <= 5800)][: n - k]
            out[k:k + len(x)] = x; k += len(x)
        return out
    if kind == 'cool':
        return rng.uniform(1300.0, 2500.0, n)
    if kind == 'narrow':
        return rng.uniform(1800.0, 3500.0, n)
    raise ValueError(kind)

def duration_prior(rng, n):
    """Luminosity and cooling e-folding time tau (s): log-uniform 0.1-2 s (declared assumption; the Kaguya flash was
    recorded in a single 1-s near-infrared frame, the SMART-1 flash within one 10-s frame)."""
    return np.exp(rng.uniform(np.log(0.1), np.log(2.0), n))

def sample_flash_parameters(rng, n, v_km_s, mass_range, eta_prior='wide', T0_prior='broad', eps_max=0.1, v_scatter=0.03):
    """Joint flash parameters with a physical consistency cut: draws whose bolometric radiated energy exceeds
    eps_max x E_k are rejected (temperature and efficiency are not independent: a cool source radiates little in the
    visible, so a high eta_vis at a low T0 would require E_bol > E_k). Returns dict of arrays and the rejected fraction."""
    out = {k: np.empty(n) for k in ('mass', 'v', 'E_k', 'log_eta', 'T0', 'tau', 'eps')}
    k = 0; tried = 0
    while k < n:
        m = 2 * (n - k) + 64
        mass = rng.uniform(mass_range[0], mass_range[1], m); v = v_km_s * rng.normal(1.0, v_scatter, m)
        E_k = kinetic_energy(mass, v); le = luminous_efficiency_prior(v_km_s, rng, m, eta_prior)
        T0 = temperature_prior(rng, m, T0_prior); tau = duration_prior(rng, m)
        eps = 10 ** le / W_eval(T0)
        ok = eps <= eps_max
        take = np.where(ok)[0][: n - k]
        # count only the draws actually examined: accepted draws beyond the n needed are surplus, not rejections
        tried += m if len(take) < n - k else int(take[-1]) + 1
        for key, arr in (('mass', mass), ('v', v), ('E_k', E_k), ('log_eta', le), ('T0', T0), ('tau', tau), ('eps', eps)):
            out[key][k:k + len(take)] = arr[take]
        k += len(take)
    out['rejected_fraction'] = 1.0 - n / tried if tried else 0.0
    return out

# ------------------------------------------------------------------ crater ---------------------------------------------
# Holsapple, "Craters from Impacts and Explosions" (crater-calculator theory, LPI version,
# https://www.lpi.usra.edu/lunar/tools/lunarcratercalc/theory.pdf): K1, K2, mu, nu, strength Y and density, with the
# volume-to-radius factor Kr from the same document (R = Kr V^(1/3) is the excavation radius; the rim diameter is
# 1.3 x the excavation diameter). A different University of Washington version of the document lists other constants;
# the two must not be mixed.
CRATER_SETS = {
    'dry sand':       dict(K1=0.132, K2=0.0,  mu=0.41, nu=0.33, Y=0.0,   rho=1700.0, Kr=1.4),
    'dry soil':       dict(K1=0.132, K2=0.26, mu=0.41, nu=0.33, Y=2.0e5, rho=1700.0, Kr=1.1),
    'lunar regolith': dict(K1=0.132, K2=0.26, mu=0.41, nu=0.33, Y=1.0e4, rho=1500.0, Kr=1.1),
}
RIM_FACTOR = 1.3   # rim diameter / excavation diameter (Holsapple)

# Housen & Holsapple (2011) crater-radius scaling (their Table 3, as reproduced by Hirata & Ikeya 2021, Table B1)
HH_CRATER_SETS = {
    'sand (HH2011 C4)':          dict(regime='gravity', mu=0.41, nu=0.4, H=0.59, rho=1600.0, Y=0.0),
    'sand/fly ash (HH2011 C7)':  dict(regime='strength', mu=0.40, nu=0.4, H=0.40, rho=1500.0, Y=4.0e3),
    'perlite/sand (HH2011 C8)':  dict(regime='strength', mu=0.35, nu=0.4, H=0.81, rho=1200.0, Y=2.0e3),
}

def impactor_radius(m_imp, rho_i):
    return (3 * m_imp / (4 * np.pi * rho_i)) ** (1 / 3)

def effective_speed(U_km_s, angle_deg, rule='vertical-component'):
    """Speed used in point-source scaling. 'vertical-component': U sin(angle from horizontal), Holsapple's rule for
    non-vertical impacts (not validated at grazing incidence, where much of the impactor ricochets: Schultz & Gault
    1990); 'vertical-equivalent': the full speed, as if the impact were vertical."""
    U = np.asarray(U_km_s, float) * 1e3
    if rule == 'vertical-component':
        return U * np.sin(np.radians(angle_deg))
    if rule == 'vertical-equivalent':
        return U
    raise ValueError(rule)

def crater_radius_holsapple(m_imp, U_ms, rho_i=400.0, params='lunar regolith', g=G_MOON):
    """Excavation radius (m) from the Holsapple pi-scaling volume form:
    pi_V = rho V / m = K1 [ pi2 pi4^((6nu-2-mu)/(3mu)) + (K2 pi3 pi4^((6nu-2)/(3mu)))^((2+mu)/2) ]^(-3mu/(2+mu)),
    pi2 = g a / U^2, pi3 = Y / (rho U^2), pi4 = rho/delta; R = Kr V^(1/3)."""
    p = CRATER_SETS[params]; rho_t = p['rho']
    a = impactor_radius(m_imp, rho_i)
    U = np.asarray(U_ms, float)
    pi2 = g * a / U ** 2; pi3 = p['Y'] / (rho_t * U ** 2); pi4 = rho_t / rho_i
    mu, nu = p['mu'], p['nu']
    term = pi2 * pi4 ** ((6 * nu - 2 - mu) / (3 * mu)) + (p['K2'] * pi3 * pi4 ** ((6 * nu - 2) / (3 * mu))) ** ((2 + mu) / 2)
    V = p['K1'] * term ** (-3 * mu / (2 + mu)) * m_imp / rho_t
    return p['Kr'] * V ** (1.0 / 3.0)

def crater_radius_hh2011(m_imp, U_ms, rho_i=400.0, params='sand (HH2011 C4)', g=G_MOON):
    """Crater radius (m) from Housen & Holsapple (2011):
    gravity:  R (rho/m)^(1/3) = H1 (g a/U^2)^(-mu/(2+mu)) (rho/delta)^((2+mu-6nu)/(3(2+mu)))
    strength: R (rho/m)^(1/3) = H2 (Y/(rho U^2))^(-mu/2) (rho/delta)^((1-3nu)/3)."""
    p = HH_CRATER_SETS[params]; rho_t = p['rho']; mu, nu = p['mu'], p['nu']
    a = impactor_radius(m_imp, rho_i); U = np.asarray(U_ms, float)
    if p['regime'] == 'gravity':
        s = p['H'] * (g * a / U ** 2) ** (-mu / (2 + mu)) * (rho_t / rho_i) ** ((2 + mu - 6 * nu) / (3 * (2 + mu)))
    else:
        s = p['H'] * (p['Y'] / (rho_t * U ** 2)) ** (-mu / 2) * (rho_t / rho_i) ** ((1 - 3 * nu) / 3)
    return s * (m_imp / rho_t) ** (1 / 3)

def crater_rim_diameter_envelope(m_imp, U_km_s, angle_deg, rho_i_range=(150.0, 400.0, 1000.0)):
    """Rim-diameter envelope (m) over parameter sets, bulk densities and the two oblique-impact rules.
    Returns dict: {'vertical-component': (min, median, max), 'vertical-equivalent': (...), 'all': (...)}.
    Neither rule is validated for a hollow spacecraft at grazing incidence; the envelope is a conditional range."""
    res = {}
    for rule in ('vertical-component', 'vertical-equivalent'):
        U = effective_speed(U_km_s, angle_deg, rule)
        vals = [2 * RIM_FACTOR * crater_radius_holsapple(m_imp, U, rho_i, prm) for prm in CRATER_SETS for rho_i in rho_i_range]
        vals += [2 * RIM_FACTOR * crater_radius_hh2011(m_imp, U, rho_i, prm) for prm in HH_CRATER_SETS for rho_i in rho_i_range]
        v = np.array(vals, float)
        res[rule] = (float(v.min()), float(np.median(v)), float(v.max()))
    allv = [res[r][0] for r in res] + [res[r][2] for r in res]
    res['all'] = (float(min(allv)), float(np.median([res[r][1] for r in res])), float(max(allv)))
    return res

# ------------------------------------------------------------------ SMART-1 conditional near-infrared case ------------------------
def smart1_saturation_eta(T0=2500.0, tau=0.5, n_sat_e=(4e4, 1.3e5), overexposure=(1.0, 1.0), area_m2=8.0,
                          throughput=0.35, seeing_arcsec=0.8, pixel_arcsec=0.3, filt_center=2.122e-6, filt_width=0.032e-6,
                          t_exp=10.0, mass_kg=285.0, v_km_s=2.0, distance_m=3.8e8):
    """Illustrative only: the visible-band eta_vis at which the SMART-1 impact would bring the peak pixel of a 10-s
    CFHT/WIRCam exposure through a 2.12-um filter to `overexposure` x the saturation level `n_sat_e`, in the
    cooling-blackbody model at temperature T0. Veillet & Foing (2007) report the frame as 'extremely over-exposed' but
    publish no calibrated degree of saturation; full well, gain, throughput, PSF, the impact mass (~285 kg is not
    verified; 366-367 kg at launch) and the spectrum are ASSUMPTIONS, so the result is an assumed-camera,
    assumed-temperature curve: a conditional lower limit in the near infrared, not a bound on the visible-band prior.
    Returns (eta_min, eta_max) over the parameter ranges."""
    fm = FlashModel(E_k=kinetic_energy(mass_kg, v_km_s), eta_vis=1.0, T0=T0, Tfloor=float(floor_temperature(T0)), tau_T=tau, tau_L=tau)
    t = np.linspace(0, t_exp, 4000)
    lam = np.linspace(filt_center - filt_width / 2, filt_center + filt_width / 2, 50)
    T = fm.temperature(t)
    frac = np.array([np.trapezoid(planck_lambda(lam, Ti), lam) * np.pi / (SIGMA_SB * Ti ** 4) for Ti in T])
    energy_at_earth = np.trapezoid(fm.luminosity(t) * frac, t) / (4 * np.pi * distance_m ** 2)     # J m^-2 for eta_vis = 1
    photons = energy_at_earth * area_m2 * throughput * filt_center / (H_PLANCK * C_LIGHT)
    sig_pix = seeing_arcsec / 2.355 / pixel_arcsec
    peak_frac = min(1.0, 1.0 / (2 * np.pi * sig_pix ** 2))
    n_peak_eta1 = photons * peak_frac
    return min(n_sat_e) * min(overexposure) / n_peak_eta1, max(n_sat_e) * max(overexposure) / n_peak_eta1
