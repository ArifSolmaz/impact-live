"""Detectability of a lunar impact flash for instruments, the eye and cellphones.

Photon-count model (per frame):
  N_src = (band energy received during the exposure) x A_eff x throughput x lambda/(hc) x f_ap
  N_bkg = per-pixel background (Earthshine-lit surface + scattered light from the sunlit crescent + sky)
  SNR   = N_src / sqrt( N_src + n_pix [B (1 + 1/n_ref) + D t + RN^2] + (s_sys B n_pix)^2 )
This is an analytic aperture-sum estimate of the signal-to-noise ratio of a difference image whose reference is the
mean of n_ref frames, with a background-subtraction systematic s_sys (lunar texture, seeing and registration
residuals). It is not a matched-filter statistic and is not calibrated against real video; the injection-recovery
simulation (scripts/run_injection_recovery.py) tests a matched-filter pipeline on synthetic frames.
Background surface brightnesses are declared assumptions (see the functions below). Detection thresholds are design
rules, not empirical class boundaries: 'obvious' (SNR >= 30; expected to stand out in raw frames), 'detected'
(SNR >= 8; found by differencing/matched filtering), 'marginal' (5 <= SNR < 8).
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from . import impact as I

HC = I.H_PLANCK * I.C_LIGHT

@dataclass
class Instrument:
    name: str
    aperture_m: float
    band: str                   # key in impact.BANDS ('broad' = 0.40-0.70 um phone/RGB/video)
    pixel_scale_arcsec: float
    fov_arcmin: tuple           # (width, height)
    exposure_s: float           # per-frame exposure
    frame_time_s: float         # frame period (1/fps)
    throughput: float = 0.5     # optics x filter x QE (band-averaged)
    obstruction: float = 0.1    # central obstruction area fraction
    read_noise_e: float = 2.0
    dark_e_s: float = 0.01
    seeing_arcsec: float = 2.0
    timing_accuracy_s: float = 0.01
    full_well_e: float = 6e4    # per (binned) pixel
    min_exposure_s: float = 1e-3
    sys_frac: float = 3e-3      # background-subtraction systematic (fraction of the background per pixel)
    n_ref: int = 20             # frames in the running reference
    kind: str = 'professional'  # professional / amateur / phone / phone-afocal
    notes: str = ''
    @property
    def area(self):
        return np.pi * (self.aperture_m / 2) ** 2 * (1 - self.obstruction)
    @property
    def duty_cycle(self):
        return self.exposure_s / self.frame_time_s
    @property
    def saturation_e(self):     # backwards-compatible name
        return self.full_well_e

def band_info(band):
    return I.BANDS[band]

# Lunar colours (Vega mags) relative to V used to convert a V surface brightness of lunar light (sunlit surface,
# Earthshine) to other bands (assumption: solar colours V-R 0.36, V-I 0.71, V-J 1.08, V-H 1.37, V-K 1.49, reddened by
# the lunar spectrum).
LUNAR_COLOR_VS_V = {'V': 0.0, 'Rc': 0.5, 'Ic': 1.0, 'J': 1.5, 'H': 1.9, 'Ks': 2.1, 'broad': 0.2}

def earth_phase_function(alpha_deg):
    """Lambert-sphere phase function Phi(alpha) = [sin a + (pi - a) cos a] / pi, normalised to 1 at full phase."""
    a = np.radians(np.clip(alpha_deg, 0, 180))
    return (np.sin(a) + (np.pi - a) * np.cos(a)) / np.pi

def earthshine_sb_V(moon_illum_frac, offset=0.0, full_earth=13.1):
    """Earthshine-lit lunar surface brightness in V (mag/arcsec^2).
    Model: full_earth (13.1, a declared normalisation for a full Earth) dimmed by a Lambert phase function of the Earth
    as seen from the Moon (Earth phase angle = 180 deg - lunar phase angle), plus `offset` for the epistemic
    uncertainty of the absolute level. Measured Earthshine varies between about +12 and +17 mag/arcsec^2 with lunar phase
    and terrestrial weather (Montanes-Rodriguez, Palle & Goode 2007, AJ 134, 1145; broadband, highland patches); the
    Earthshine/sunlight ratio is ~1e-4 near new Moon (Palle et al. 2003). Not calibrated against local measurements."""
    f = np.clip(np.asarray(moon_illum_frac, float), 0.0, 1.0)
    i_moon = np.degrees(np.arccos(np.clip(2 * f - 1, -1, 1)))         # lunar phase angle (Sun-Moon-Earth)
    phi = np.maximum(earth_phase_function(180.0 - i_moon), 1e-3)
    return full_earth - 2.5 * np.log10(phi) + offset

def scattered_sb_V(dist_to_sunlit_arcmin, k_scat=3e-3):
    """Scattered light from the sunlit part of the disk (telescope + atmosphere PSF wing ~ theta^-2):
    mu = 3.4 - 2.5 log10( k_scat (theta/1')^-2 ).  k_scat is an assumption (3e-3 nominal, 1e-3..1e-2 explored)."""
    th = np.maximum(dist_to_sunlit_arcmin, 0.3)
    return 3.4 - 2.5 * np.log10(k_scat * th ** -2)

# Night-sky floor per band (mag/arcsec^2; dark-site optical values, NIR OH + thermal values typical of Maunakea/Paranal).
DARK_SKY_SB = {'V': 21.5, 'Rc': 20.8, 'Ic': 19.9, 'J': 16.0, 'H': 14.2, 'Ks': 13.0, 'broad': 21.2}
# Band-minus-V colour of the twilight/day sky. Scattered sunlight is blue-weighted (Rayleigh scattering ~ lambda^-4),
# so the sky is relatively fainter in red and infrared bands (positive band - V colours, larger than solar colours).
TWILIGHT_COLOR = {'V': 0.0, 'Rc': 0.33, 'Ic': 0.85, 'J': 2.3, 'H': 3.3, 'Ks': 4.4, 'broad': -0.1}

def sky_sb(band, sun_alt_deg):
    """Sky surface brightness in `band`: night floor plus a twilight/daylight component (V-band curve of Patat et al.
    2006 type: 22.5 at -18 deg, 17 at -12, 11 at -6, 5 at 0, 3.5 in daylight) converted with TWILIGHT_COLOR.
    Declared assumption."""
    s = np.asarray(sun_alt_deg, float)
    tw_V = np.interp(s, [-90, -18, -12, -6, 0, 10], [40.0, 22.5, 17.0, 11.0, 5.0, 3.5])
    f = 10 ** (-0.4 * DARK_SKY_SB[band]) + 10 ** (-0.4 * (tw_V + TWILIGHT_COLOR[band]))
    return -2.5 * np.log10(f)

# Atmospheric extinction at sea level (mag/airmass; typical clear-sky values), scaled with site altitude:
# k(h) = k_sea (0.55 + 0.45 exp(-h / 2000 m)) (declared assumption).
EXT_SEA = {'V': 0.22, 'Rc': 0.15, 'Ic': 0.10, 'J': 0.12, 'H': 0.08, 'Ks': 0.10, 'broad': 0.22}

def extinction_mag(band, airmass, site_alt_m=2500.0):
    X = np.minimum(np.asarray(airmass, float), 10.0)
    return EXT_SEA[band] * (0.55 + 0.45 * np.exp(-np.asarray(site_alt_m, float) / 2000.0)) * X

def sunlit_sb_V(incidence_deg):
    """Sunlit-terrain surface brightness (V mag/arcsec^2): full-Moon mean 3.4, dimmed by 1/cos(incidence)
    (Lambert-like; declared approximation)."""
    return 3.4 + 2.5 * np.log10(1.0 / np.maximum(np.cos(np.radians(incidence_deg)), 0.05))

def total_background_sb(band, moon_illum_frac, dist_sunlit_arcmin, sun_alt_deg, k_scat=3e-3, ext_mag=0.0, es_offset=0.0,
                        sunlit=False, incidence_deg=60.0):
    """Combined background surface brightness (mag/arcsec^2) at the impact point in the given band: lunar light
    (Earthshine-lit surface, or the sunlit surface if `sunlit`, plus scattered light from the crescent), dimmed by the
    atmospheric extinction `ext_mag`, plus the band-specific sky (not extincted)."""
    if sunlit:
        lunar = [sunlit_sb_V(incidence_deg)]
    else:
        lunar = [earthshine_sb_V(moon_illum_frac, es_offset), scattered_sb_V(dist_sunlit_arcmin, k_scat)]
    f_lunar = sum(10 ** (-0.4 * (m - LUNAR_COLOR_VS_V[band] + ext_mag)) for m in lunar)
    f_sky = 10 ** (-0.4 * sky_sb(band, sun_alt_deg))
    return -2.5 * np.log10(f_lunar + f_sky)

def photons_from_mag(mag, band, area_m2, throughput, t_s):
    """Detected photo-electrons from a steady source of magnitude `mag` over t_s seconds."""
    b = band_info(band)
    F = b['f0'] * 10 ** (-0.4 * np.asarray(mag, float))             # W m^-2 m^-1
    return F * b['width'] * area_m2 * throughput * t_s * b['lam'] / HC

def photons_from_energy(energy_J_m2, band, area_m2, throughput):
    """Photo-electrons from a band fluence (J m^-2) collected by the aperture."""
    return np.asarray(energy_J_m2, float) * area_m2 * throughput * band_info(band)['lam'] / HC

def aperture_pixels(inst: Instrument):
    r_ap = max(1.5 * inst.seeing_arcsec, 1.5 * inst.pixel_scale_arcsec)
    return max(np.pi * r_ap ** 2 / inst.pixel_scale_arcsec ** 2, 1.0)

def peak_pixel_fraction(inst: Instrument):
    sig = max(inst.seeing_arcsec / 2.355 / inst.pixel_scale_arcsec, 0.3)
    return min(1.0, 1.0 / (2 * np.pi * sig ** 2))

AP_FRAC = 0.8   # fraction of the point-source light in the photometric aperture (radius 1.5 x FWHM)

def background_e_per_pixel(inst: Instrument, bkg_sb, t_exp=None):
    t = inst.exposure_s if t_exp is None else t_exp
    return photons_from_mag(bkg_sb, inst.band, inst.area, inst.throughput, t) * inst.pixel_scale_arcsec ** 2

def snr_from_counts(inst: Instrument, N_src_total, bkg_sb, t_exp=None):
    """Signal-to-noise (aperture-sum estimate of a difference-image detection) for N_src_total source electrons
    (all of the source light; AP_FRAC of it falls in the aperture)."""
    t = inst.exposure_s if t_exp is None else t_exp
    n_pix = aperture_pixels(inst)
    B = background_e_per_pixel(inst, bkg_sb, t)
    S = np.asarray(N_src_total, float) * AP_FRAC
    var = S + n_pix * (B * (1 + 1.0 / inst.n_ref) + inst.dark_e_s * t + inst.read_noise_e ** 2) + (inst.sys_frac * B * n_pix) ** 2
    return S / np.sqrt(var)

def frame_snr(inst: Instrument, src_mag_avg, bkg_sb, ap_frac=AP_FRAC):
    """SNR of a steady source of magnitude src_mag_avg over one exposure (returns snr, N_src_in_aperture, B_pix, n_pix)."""
    N = photons_from_mag(src_mag_avg, inst.band, inst.area, inst.throughput, inst.exposure_s)
    return snr_from_counts(inst, N, bkg_sb), N * AP_FRAC, background_e_per_pixel(inst, bkg_sb), aperture_pixels(inst)

def limiting_magnitude(inst: Instrument, bkg_sb, snr_req=8.0):
    """Magnitude of a source that is steady over the exposure and reaches snr_req (a flash that fades during the
    exposure must be compared through its exposure-integrated counts, not its peak)."""
    mags = np.linspace(-5, 25, 1201)
    snr = snr_from_counts(inst, photons_from_mag(mags, inst.band, inst.area, inst.throughput, inst.exposure_s), bkg_sb)
    ok = snr >= snr_req
    return float(mags[ok].max()) if ok.any() else -np.inf

def bright_limit(inst: Instrument, bkg_sb=None):
    """Magnitude of a steady point source whose peak pixel (plus background) reaches full well in one frame."""
    B = 0.0 if bkg_sb is None else float(background_e_per_pixel(inst, bkg_sb))
    room = inst.full_well_e - B
    if room <= 0:
        return -np.inf
    n1 = photons_from_mag(0.0, inst.band, inst.area, inst.throughput, inst.exposure_s) * peak_pixel_fraction(inst)
    return float(2.5 * np.log10(n1 / room))

def usable_exposure(inst: Instrument, bkg_sb, fill=0.5):
    """Exposure time the observer would use so that the background stays below fill x full well (bright, sunlit or
    twilight backgrounds); None if even the shortest exposure saturates (configuration unavailable)."""
    rate = float(background_e_per_pixel(inst, bkg_sb, 1.0))
    if rate * inst.exposure_s <= fill * inst.full_well_e:
        return inst.exposure_s
    t = fill * inst.full_well_e / rate
    return t if t >= inst.min_exposure_s else None

def classify(snr):
    snr = np.asarray(snr)
    return np.select([snr >= 30, snr >= 8, snr >= 5], ['obvious', 'detected', 'marginal'], default='none')

def best_frame(inst: Instrument, flash: I.FlashModel, bkg_sb, distance_m, phase_s=0.0, t_exp=None, n_frames=None):
    """Best single-frame SNR of a flash for one exposure phase: exposures start at phase_s - frame_time + k frame_time
    (k = 0, 1, ...), each integrates the received flux over its overlap with t >= 0 (no source before the onset), and
    counts are divided by nothing (they are counts). Returns (snr_best, k_best, counts_best)."""
    t_exp = inst.exposure_s if t_exp is None else t_exp
    n = n_frames or int(np.ceil(6 * max(flash.tau_L, flash.tau_T) / inst.frame_time_s)) + 2
    starts = phase_s - inst.frame_time_s + inst.frame_time_s * np.arange(n)
    counts = np.array([photons_from_energy(flash.band_energy(inst.band, s, s + t_exp, distance_m), inst.band, inst.area, inst.throughput) for s in starts])
    snr = snr_from_counts(inst, counts, bkg_sb, t_exp)
    k = int(np.argmax(snr))
    return float(snr[k]), k, float(counts[k])

# ----------------------------------------------------------- human vision ------------------------------------------
# Crumey (2014, MNRAS 442, 2600) threshold illuminance for a point source on a background of luminance B (cd m^-2):
#   Delta I = F (r1 B^(1/4) + r2 B^(1/2))^2 (scotopic, B < 7.08e-2) or F (r3 B^(1/4) + r4 B^(1/2))^2 (photopic),
# Blackwell constants r1 = 6.505e-4, r2 = -8.461e-4, r3 = 1.772e-4, r4 = 7.167e-5 (lux); mu_V = 12.58 - 2.5 log10 B;
# m_V = -13.99 - 2.5 log10(Delta I / lux). F (field factor) is typically 1.4-2.4. These thresholds are for unlimited
# viewing; for a brief flash we compare the light received in the eye's integration time (~0.1 s, Bloch's law)
# with the steady threshold. 90 % detection corresponds to 1.62x the 50 % contrast (0.52 mag), giving a cumulative
# normal psychometric function with sigma = 0.41 mag.
CRUMEY = dict(r1=6.505e-4, r2=-8.461e-4, r3=1.772e-4, r4=7.167e-5, split=7.08e-2)
T_EYE = 0.1          # s, temporal integration (declared)
PSY_SIGMA = 0.41     # mag

def luminance_from_sb(sb_V):
    return 10 ** ((12.58 - np.asarray(sb_V, float)) / 2.5)

def eye_threshold_mag(bkg_sb_V, F=2.0):
    """50 % detection threshold (V mag) of a steady point source seen by the naked eye on a background of bkg_sb_V."""
    B = luminance_from_sb(bkg_sb_V)
    c = CRUMEY
    dI = np.where(B < c['split'], F * (c['r1'] * B ** 0.25 + c['r2'] * B ** 0.5) ** 2, F * (c['r3'] * B ** 0.25 + c['r4'] * B ** 0.5) ** 2)
    return -13.99 - 2.5 * np.log10(dI)

AIDS = {  # aperture (mm), magnification, transmission
    'none': dict(D=7.0, M=1.0, T=1.0),
    'binoculars': dict(D=50.0, M=7.0, T=0.8),
    'telescope20cm': dict(D=200.0, M=150.0, T=0.7),
}

def visual_threshold_mag(bkg_sb_V, aid='none', F=2.0, pupil_mm=7.0):
    """Threshold for a point source with an optical aid: the aid multiplies the point-source illuminance at the eye by
    T (D/p)^2 (all light enters the eye while the exit pupil <= the eye pupil) and dims the background luminance by
    T (exit pupil / eye pupil)^2 when the exit pupil is smaller than the eye pupil (Schaefer 1990-type scaling).
    Seeing and the eye's resolution limit at high magnification are ignored."""
    a = AIDS[aid]; ep = a['D'] / a['M']
    gain = a['T'] * (min(a['D'], a['M'] * pupil_mm) / pupil_mm) ** 2
    bkg_eye = np.asarray(bkg_sb_V, float) - 2.5 * np.log10(a['T'] * min(1.0, (ep / pupil_mm) ** 2))
    return eye_threshold_mag(bkg_eye, F) + 2.5 * np.log10(gain)

def visual_detection_probability(m_eff, thr, attention=0.5):
    """P(a prepared observer looking at the right place notices the flash) = attention x Phi((thr - m_eff)/0.41).
    m_eff is the magnitude of the light received in the eye's integration time T_EYE. Conditional on a clear,
    unobstructed view; attention is a declared factor (blinks, looking at the right point at the right moment)."""
    from scipy.stats import norm
    return attention * norm.cdf((np.asarray(thr) - np.asarray(m_eff)) / PSY_SIGMA)

# ----------------------------------------------------------- cellphones --------------------------------------------
def phone_instrument(mode='standalone', telescope_aperture_m=0.2, telescope_focal_m=2.0):
    """Representative 2024-26 flagship phone main camera in the broad visible band: 24-mm equivalent, f/1.7,
    1/1.3-inch sensor, 12 MP binned output (2.4 um pixels), video 30 fps with ~1/30 s exposure in auto mode,
    8-bit H.264/HEVC. Physical focal length ~6.9 mm -> aperture 4.1 mm. Afocal coupling through a 20-cm f/10 telescope
    with a 25-mm eyepiece: effective focal length = 2000 x 6.9/25 = 552 mm. Pixel scale = 206265 x 2.4e-6 / f_eff.
    Full well of a 2.4-um binned pixel ~ 6000 e- (declared)."""
    common = dict(obstruction=0.0, read_noise_e=3.0, dark_e_s=0.1, timing_accuracy_s=0.5, full_well_e=6000, min_exposure_s=1e-4, sys_frac=0.01, n_ref=10)
    if mode == 'standalone':
        f_eff = 6.9e-3; ap = 4.1e-3; pix = 206265 * 2.4e-6 / f_eff
        return Instrument('phone standalone 24mm video', ap, 'broad', pix, (72 * 60, 54 * 60), 1 / 30, 1 / 30, throughput=0.45, seeing_arcsec=pix, kind='phone', notes='8-bit video, auto exposure', **common)
    if mode == 'afocal':
        f_eff = telescope_focal_m * (6.9e-3 / 25e-3); pix = 206265 * 2.4e-6 / f_eff
        c = dict(common, obstruction=0.3)
        return Instrument(f'phone afocal on {telescope_aperture_m*100:.0f}-cm telescope', telescope_aperture_m, 'broad', pix, (0.5 * 60, 0.4 * 60), 1 / 30, 1 / 30, throughput=0.3, seeing_arcsec=max(2.0, 2 * pix), kind='phone-afocal', notes='eyepiece projection, vignetting, auto exposure', **c)
    raise ValueError(mode)

def phone_processing_penalty(mode):
    """Multiplicative SNR penalty for phone video pipelines (assumption, to be replaced by measured values): temporal
    denoising / multi-frame merging suppresses single-frame transients (x0.5), 8-bit quantisation and compression
    (x0.8), auto-exposure clipping of the crescent while the dark side sits in the lowest code values (x0.6 unless the
    exposure is locked; x0.8 through a telescope)."""
    return {'standalone': 0.5 * 0.8 * 0.6, 'afocal': 0.5 * 0.8 * 0.8}[mode]
