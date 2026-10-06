"""Detectability of a lunar impact flash for instruments, humans and cellphones.

Photon-count model (per frame):
  N_src = A_eff * int F_lambda(t) dt * dlam * tau * lam/(hc) * f_ap
  N_bkg = per-pixel background from (Earthshine-lit surface + scattered light from the sunlit crescent + sky)
  SNR   = N_src / sqrt(N_src + n_pix (N_bkg + D t + RN^2))
Background surface brightnesses are *assumptions* with declared values (see BACKGROUND dict) calibrated so that a
NELIOTA-like 1.2-m system reaches a practical single-camera limit near R ~ 12.5 at 30 fps (Bonanos et al. 2018;
Liakos et al. 2020 report the faintest detected flashes at 12.4 mag).
Detection classes: 'obvious' (SNR >= 30, visible in raw frames), 'processed' (8 <= SNR < 30, found by
differencing/matched filtering in near-real time), 'marginal' (5 <= SNR < 8, later analysis / needs a second
camera to be claimed), 'none'.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from . import impact as I

HC = I.H_PLANCK * I.C_LIGHT

@dataclass
class Instrument:
    name: str
    aperture_m: float
    band: str                   # key in impact.BANDS or 'broad' (0.40-0.70 um, phone/RGB)
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
    saturation_e: float = 6e4
    kind: str = 'professional'  # professional / amateur / phone / phone-afocal / eye
    notes: str = ''
    @property
    def area(self):
        return np.pi * (self.aperture_m / 2) ** 2 * (1 - self.obstruction)
    @property
    def duty_cycle(self):
        return self.exposure_s / self.frame_time_s

def band_info(band):
    return I.BANDS[band]

# Lunar colours (Vega mags) relative to V used to convert V surface brightness to other bands (assumption:
# solar colours reddened by the lunar spectrum; Sun V-R=0.36, V-I=0.71, V-J=1.08, V-H=1.37, V-K=1.49; Moon ~ +0.1..0.6)
LUNAR_COLOR_VS_V = {'V': 0.0, 'Rc': 0.5, 'Ic': 1.0, 'J': 1.5, 'H': 1.9, 'Ks': 2.1, 'broad': 0.2}

def earthshine_sb_V(moon_illum_frac):
    """Earthshine-lit lunar surface brightness in V (mag/arcsec^2).  Full-Moon sunlit surface 3.4 mag/arcsec^2;
    Earth at full phase is ~9.7 mag fainter than the Sun seen from the Moon (albedo 0.3, radius 6371 km, 1 au) ->
    13.1; the Earth's illuminated fraction seen from the Moon is (1 - Moon illuminated fraction) to first order."""
    f_earth = np.clip(1.0 - moon_illum_frac, 0.02, 1.0)
    return 13.1 - 2.5 * np.log10(f_earth)

def scattered_sb_V(dist_to_sunlit_arcmin, k_scat=3e-3):
    """Scattered light from the sunlit part of the disk (telescope + atmosphere PSF wing ~ theta^-2):
    mu = 3.4 - 2.5 log10( k_scat (theta/1')^-2 ).  k_scat is an assumption (3e-3 nominal, 1e-3..1e-2 explored)."""
    th = np.maximum(dist_to_sunlit_arcmin, 0.3)
    return 3.4 - 2.5 * np.log10(k_scat * th ** -2)

def sky_sb_V(sun_alt_deg, dark_sky=21.5):
    """Twilight/day sky brightness in V (mag/arcsec^2), simple parametrisation of Patat et al. (2006)-type curves:
    night 21.5; -18..-12: 21.5 -> 17; -12..-6: 17 -> 11; -6..0: 11 -> 5; day ~ 3.5 (near the Moon's position)."""
    s = np.asarray(sun_alt_deg, float)
    return np.interp(s, [-90, -18, -12, -6, 0, 10], [dark_sky, dark_sky, 17.0, 11.0, 5.0, 3.5])

# Night-sky floor per band (mag/arcsec^2; dark-site optical values, NIR OH + thermal values typical of Maunakea/Paranal).
DARK_SKY_SB = {'V': 21.5, 'Rc': 20.8, 'Ic': 19.9, 'J': 16.0, 'H': 14.2, 'Ks': 13.0, 'broad': 21.2}
# Colour (band SB minus V SB) of the scattered-sunlight twilight/day sky: solar colours reddened by Rayleigh lambda^-4.
TWILIGHT_COLOR = {'V': 0.0, 'Rc': 0.33, 'Ic': 0.85, 'J': 2.3, 'H': 3.3, 'Ks': 4.4, 'broad': -0.1}

def sky_sb(band, sun_alt_deg):
    """Sky surface brightness in `band`: night floor plus a twilight/daylight component whose V-band curve follows
    Patat et al. (2006)-type values (22.5 at -18 deg, 17 at -12, 11 at -6, 5 at 0, 3.5 in daylight) and is converted
    to other bands with TWILIGHT_COLOR.  Declared assumption."""
    s = np.asarray(sun_alt_deg, float)
    tw_V = np.interp(s, [-90, -18, -12, -6, 0, 10], [40.0, 22.5, 17.0, 11.0, 5.0, 3.5])
    f = 10 ** (-0.4 * DARK_SKY_SB[band]) + 10 ** (-0.4 * (tw_V + TWILIGHT_COLOR[band]))
    return -2.5 * np.log10(f)

# Atmospheric extinction at sea level (mag/airmass; typical clear-sky values) and its scaling with site altitude:
# k(h) = k_sea * (0.55 + 0.45 exp(-h / 2000 m))  ->  e.g. V 0.22 at sea level, 0.15 at 2500 m (declared assumption).
EXT_SEA = {'V': 0.22, 'Rc': 0.15, 'Ic': 0.10, 'J': 0.12, 'H': 0.08, 'Ks': 0.10, 'broad': 0.22}

def extinction_mag(band, airmass, site_alt_m=2500.0):
    X = np.minimum(np.asarray(airmass, float), 10.0)
    return EXT_SEA[band] * (0.55 + 0.45 * np.exp(-site_alt_m / 2000.0)) * X

def total_background_sb(band, moon_illum_frac, dist_sunlit_arcmin, sun_alt_deg, k_scat=3e-3, ext_mag=0.0):
    """Combined background surface brightness (mag/arcsec^2) in the given band: Earthshine-lit surface and scattered
    light from the sunlit crescent (lunar colours, dimmed by the atmospheric extinction `ext_mag` along the line of
    sight) plus the band-specific sky (not extincted)."""
    f_lunar = sum(10 ** (-0.4 * (m - LUNAR_COLOR_VS_V[band] + ext_mag)) for m in [earthshine_sb_V(moon_illum_frac), scattered_sb_V(dist_sunlit_arcmin, k_scat)])
    f_sky = 10 ** (-0.4 * sky_sb(band, sun_alt_deg))
    return -2.5 * np.log10(f_lunar + f_sky)

def photons_from_mag(mag, band, area_m2, throughput, t_s):
    b = band_info(band)
    F = b['f0'] * 10 ** (-0.4 * np.asarray(mag))             # W m^-2 m^-1
    return F * b['width'] * area_m2 * throughput * t_s * b['lam'] / HC

def frame_snr(inst: Instrument, src_mag_avg, bkg_sb, ap_frac=0.8):
    """SNR of a source whose exposure-averaged magnitude is src_mag_avg, against background bkg_sb (mag/arcsec^2)."""
    r_ap = max(1.5 * inst.seeing_arcsec, 1.5 * inst.pixel_scale_arcsec)      # aperture radius
    n_pix = max(np.pi * r_ap ** 2 / inst.pixel_scale_arcsec ** 2, 1.0)
    N_src = photons_from_mag(src_mag_avg, inst.band, inst.area, inst.throughput, inst.exposure_s) * ap_frac
    N_bkg_pix = photons_from_mag(bkg_sb, inst.band, inst.area, inst.throughput, inst.exposure_s) * inst.pixel_scale_arcsec ** 2
    noise = np.sqrt(N_src + n_pix * (N_bkg_pix + inst.dark_e_s * inst.exposure_s + inst.read_noise_e ** 2))
    return N_src / noise, N_src, N_bkg_pix, n_pix

def limiting_magnitude(inst: Instrument, bkg_sb, snr_req=8.0):
    mags = np.linspace(-5, 25, 601)
    snr = np.array([frame_snr(inst, m, bkg_sb)[0] for m in mags])
    ok = snr >= snr_req
    return float(mags[ok].max()) if ok.any() else -np.inf

def bright_limit(inst: Instrument, saturation_e=None):
    """Magnitude at which the peak pixel of a point source reaches the detector saturation level in one frame."""
    sat = inst.saturation_e if saturation_e is None else saturation_e
    sig = max(inst.seeing_arcsec / 2.355 / inst.pixel_scale_arcsec, 0.3)
    peak_frac = min(1.0, 1.0 / (2 * np.pi * sig ** 2))
    n1 = photons_from_mag(0.0, inst.band, inst.area, inst.throughput, inst.exposure_s) * peak_frac   # electrons at m = 0
    return float(2.5 * np.log10(n1 / sat))

def classify(snr):
    snr = np.asarray(snr)
    return np.select([snr >= 30, snr >= 8, snr >= 5], ['obvious', 'processed', 'marginal'], default='none')

def flash_detection(inst: Instrument, flash: I.FlashModel, bkg_sb, distance_m, t_offset_s=None):
    """Best single-frame SNR over the flash, accounting for frame phase (uniform random start if t_offset None ->
    use the mean of 10 phases), duty cycle (flash entirely inside a dead-time gap -> missed)."""
    phases = np.linspace(0, inst.frame_time_s, 10, endpoint=False) if t_offset_s is None else [t_offset_s]
    best = []
    for ph in phases:
        starts = -ph + inst.frame_time_s * np.arange(0, int(np.ceil(10 * max(flash.tau_L, flash.tau_T) / inst.frame_time_s)) + 2)
        snrs = []
        for s in starts:
            a, b = max(s, 0.0), max(s + inst.exposure_s, 0.0)
            if b <= a:
                continue
            m_avg = flash.exposure_averaged_magnitude(inst.band, inst.exposure_s, t_start=a, distance_m=distance_m) if b > 0 else 99
            # if the exposure window begins before t=0 the source is only present for (b-0)/exposure of it
            if a == 0.0 and s < 0:
                frac = min(b, inst.exposure_s) / inst.exposure_s
                m_avg = m_avg - 2.5 * np.log10(frac) if frac > 0 else 99
            snrs.append(frame_snr(inst, m_avg, bkg_sb)[0])
        best.append(max(snrs) if snrs else 0.0)
    return float(np.mean(best)), float(np.min(best)), float(np.max(best))

# ----------------------------------------------------------- human vision ------------------------------------------
def naked_eye_threshold_mag(duration_s, moon_illum_frac, aided='none'):
    """Threshold apparent magnitude for noticing a point flash on the Earthshine-lit disk.
    Assumptions (declared): steady-source limit next to the Moon's glare ~ +3.5 (vs +6 in a dark sky; stars
    within a few degrees of a crescent Moon are seen to ~3-4 mag); temporal integration ~0.1 s (Bloch's law):
    flashes shorter than 0.1 s lose 2.5 log10(0.1/duration); a prepared observer looking at the right place gains
    ~0.5 mag over a casual one; aids: binoculars 7x50 -> +3.5 mag (aperture 50 vs 7 mm, 0.8 transmission, exit
    pupil 7 mm so surface brightness unchanged), 20-cm telescope at 150x -> +6.5 mag (exit pupil 1.3 mm reduces the
    Moon's surface brightness by ~3.6 mag, improving point-source contrast; limited by seeing/eye at ~+10 for
    steady stars).  Brighter illumination (larger crescent) lowers the limit by up to ~1 mag."""
    base = 3.5 - 1.0 * np.clip((moon_illum_frac - 0.1) / 0.5, 0, 1)
    gain = {'none': 0.0, 'binoculars': 3.5, 'telescope20cm': 6.5, 'telescope40cm': 7.5}[aided]
    temporal = -2.5 * np.log10(np.minimum(np.asarray(duration_s) / 0.1, 1.0))
    return base + gain - temporal

def witness_probability(flash_peak_mag, duration_s, moon_illum_frac, aided='none', attention=0.5, sigma_thr=1.0):
    """P(a prepared observer notices the flash) = attention x Phi((m_thr - m_peak)/sigma_thr)."""
    from scipy.stats import norm
    thr = naked_eye_threshold_mag(duration_s, moon_illum_frac, aided)
    return attention * norm.cdf((thr - np.asarray(flash_peak_mag)) / sigma_thr)

# ----------------------------------------------------------- cellphones --------------------------------------------
def phone_instrument(mode='standalone', telescope_aperture_m=0.2, telescope_focal_m=2.0):
    """Representative 2024-26 flagship phone main camera: 24-mm equivalent, f/1.7, 1/1.3-inch sensor,
    12 MP binned output (2.4 um pixels), video 30 fps with ~1/30 s max exposure in auto mode, 8-bit H.264/HEVC.
    Physical focal length ~6.9 mm -> aperture 4.1 mm.  Afocal coupling through a 20-cm f/10 telescope with a
    25-mm eyepiece: effective focal length = telescope focal x (phone focal / eyepiece focal) -> 2000 x 6.9/25 = 552 mm.
    Pixel scale = 206265 x 2.4e-6 / f_eff."""
    if mode == 'standalone':
        f_eff = 6.9e-3; ap = 4.1e-3; pix = 206265 * 2.4e-6 / f_eff
        return Instrument('phone standalone 24mm video', ap, 'broad', pix, (72 * 60, 54 * 60), 1 / 30, 1 / 30,
                          throughput=0.45, obstruction=0.0, read_noise_e=3.0, dark_e_s=0.1, seeing_arcsec=pix,
                          timing_accuracy_s=0.5, saturation_e=6000, kind='phone', notes='8-bit video, auto exposure')
    if mode == 'digital-zoom':
        f_eff = 6.9e-3; ap = 4.1e-3; pix = 206265 * 2.4e-6 / f_eff   # digital zoom does not change photons/pixel
        return Instrument('phone 24mm digital zoom', ap, 'broad', pix, (72 * 60 / 5, 54 * 60 / 5), 1 / 30, 1 / 30,
                          throughput=0.45, obstruction=0.0, read_noise_e=3.0, dark_e_s=0.1, seeing_arcsec=pix,
                          timing_accuracy_s=0.5, saturation_e=6000, kind='phone', notes='crop of the same sensor')
    if mode == 'tele-5x':
        f_eff = 23e-3; ap = 23e-3 / 2.8; pix = 206265 * 2.4e-6 / f_eff   # 120-mm equivalent periscope, f/2.8
        return Instrument('phone 5x periscope video', ap, 'broad', pix, (16 * 60, 12 * 60), 1 / 30, 1 / 30,
                          throughput=0.4, obstruction=0.0, read_noise_e=3.0, dark_e_s=0.1, seeing_arcsec=pix,
                          timing_accuracy_s=0.5, saturation_e=6000, kind='phone')
    if mode == 'afocal':
        f_eff = telescope_focal_m * (6.9e-3 / 25e-3); ap = telescope_aperture_m
        pix = 206265 * 2.4e-6 / f_eff
        return Instrument(f'phone afocal on {telescope_aperture_m*100:.0f}-cm telescope', ap, 'broad', pix, (0.5 * 60, 0.4 * 60), 1 / 30, 1 / 30,
                          throughput=0.3, obstruction=0.3, read_noise_e=3.0, dark_e_s=0.1, seeing_arcsec=max(2.0, 2 * pix),
                          timing_accuracy_s=0.5, saturation_e=6000, kind='phone-afocal', notes='eyepiece projection, vignetting, auto exposure')
    raise ValueError(mode)

def phone_processing_penalty(mode):
    """Multiplicative SNR penalty for phone video pipelines (assumption, to be replaced by measured values from
    the injection-recovery experiment): temporal denoising / multi-frame merging suppresses single-frame
    transients (x0.5), 8-bit quantisation and compression (x0.8), auto-exposure clipping of the sunlit crescent
    while the dark side sits in the lowest few code values (x0.6 unless exposure is locked manually)."""
    return {'standalone': 0.5 * 0.8 * 0.6, 'digital-zoom': 0.5 * 0.8 * 0.6, 'tele-5x': 0.5 * 0.8 * 0.6, 'afocal': 0.5 * 0.8 * 0.8}[mode]
