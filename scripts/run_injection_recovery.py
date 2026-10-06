"""Injection-recovery experiment (SIMULATION).  Synthetic lunar video frames for four recording systems, with
calibrated synthetic flashes injected at known magnitudes, run through a simple real-time detection pipeline
(running-median difference + PSF-matched filter + 5-sigma threshold, with a dual-camera coincidence option).
Outputs completeness curves and false-alarm rates.  The lunar texture is the scikit-image 'moon' sample image
(a real photograph of the lunar surface, public domain), rescaled to the modelled Earthshine surface brightness;
it is used as an albedo texture only.  Nothing here is observed AYAP-1 footage."""
import sys, os, numpy as np, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
from skimage import data
from scipy.ndimage import gaussian_filter, median_filter, uniform_filter
from ayap1obs import detect as D, impact as I, plotting as P
import matplotlib.pyplot as plt
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
rng = np.random.default_rng(20261005)
tex = data.moon().astype(float); tex = tex / tex.mean()        # albedo texture, mean 1
ILLUM = 0.35

def make_system(name):
    if name == 'NELIOTA-like 1.2 m (R, 23 ms, dual camera)':
        inst = D.Instrument(name, 1.2, 'Rc', 0.8, (17, 14.4), 0.023, 1 / 30, throughput=0.5, obstruction=0.1, read_noise_e=1.5, seeing_arcsec=2.5)
        return inst, dict(n=256, bits=16, dual=True, denoise=False, gain=1.0, pointing_scatter=0.4)
    if name == 'Amateur 0.35 m (broad, 30 fps, 8-bit CMOS)':
        inst = D.Instrument(name, 0.35, 'broad', 1.0, (20, 15), 0.03, 1 / 30, throughput=0.5, obstruction=0.15, read_noise_e=2.0, seeing_arcsec=3.0)
        return inst, dict(n=256, bits=8, dual=False, denoise=False, gain=0.02, pointing_scatter=0.3)
    if name == 'Phone afocal on 20 cm (1/30 s, 8-bit, denoised video)':
        inst = D.phone_instrument('afocal')
        return inst, dict(n=256, bits=8, dual=False, denoise=True, gain=0.01, pointing_scatter=1.0)
    if name == 'Phone standalone 24 mm (1/30 s, 8-bit, denoised video)':
        inst = D.phone_instrument('standalone')
        return inst, dict(n=48, bits=8, dual=False, denoise=True, gain=0.002, pointing_scatter=0.0)
    raise ValueError(name)

def background_map(inst, n, scat_side=True):
    """Per-pixel background electrons per frame: Earthshine-lit textured surface + scattered-light gradient."""
    sb_es = D.earthshine_sb_V(ILLUM) - D.LUNAR_COLOR_VS_V[inst.band]
    N_es = D.photons_from_mag(sb_es, inst.band, inst.area, inst.throughput, inst.exposure_s) * inst.pixel_scale_arcsec ** 2
    ty = rng.integers(0, tex.shape[0] - n) if tex.shape[0] > n else 0
    t = tex[ty:ty + n, ty:ty + n] if tex.shape[0] >= n else np.resize(tex, (n, n))
    t = gaussian_filter(t, max(inst.seeing_arcsec / inst.pixel_scale_arcsec / 2.355, 0.5))
    bkg = N_es * np.clip(t, 0.3, 3.0)
    if scat_side:   # sunlit terminator lies 6' beyond one edge of the field
        x = (np.arange(n) * inst.pixel_scale_arcsec / 60.0)[None, :]
        dist = 6.0 + (n * inst.pixel_scale_arcsec / 60.0 - x)
        sb_sc = D.scattered_sb_V(dist) - D.LUNAR_COLOR_VS_V[inst.band]
        bkg = bkg + D.photons_from_mag(sb_sc, inst.band, inst.area, inst.throughput, inst.exposure_s) * inst.pixel_scale_arcsec ** 2
    return bkg

def psf_kernel(inst, n=15):
    sig = max(inst.seeing_arcsec / inst.pixel_scale_arcsec / 2.355, 0.6)
    y, x = np.mgrid[-n // 2 + 1:n // 2 + 1, -n // 2 + 1:n // 2 + 1]
    k = np.exp(-(x ** 2 + y ** 2) / (2 * sig ** 2)); return k / k.sum()

def render(inst, opts, bkg, src_e=None, pos=None, nframes=40, flash_frames=None):
    n = bkg.shape[0]; frames = np.zeros((nframes, n, n))
    k = psf_kernel(inst)
    flat = 1.0 + rng.normal(0, 0.005, bkg.shape)        # 0.5 % uncorrected flat-field residual (fixed pattern)
    for f in range(nframes):
        sig = max(inst.seeing_arcsec / inst.pixel_scale_arcsec / 2.355, 0.6) * rng.normal(1.0, 0.05)   # seeing variation frame to frame (5 %: consecutive 33-ms frames are correlated)
        transp = rng.normal(1.0, 0.01)                      # transparency/scintillation flicker of the whole frame (1 %)
        img = bkg * transp
        if src_e is not None and f in flash_frames:
            s = np.zeros_like(img); s[pos[0], pos[1]] = src_e[flash_frames.index(f)] * transp
            img = img + gaussian_filter(s, sig)   # kernel integrates to 1: total source electrons preserved
        if opts['pointing_scatter'] > 0:   # tracking jitter in pixels
            sh = rng.normal(0, opts['pointing_scatter'], 2); img = np.roll(np.roll(img, int(round(sh[0])), 0), int(round(sh[1])), 1)
        img = img * flat
        img = rng.poisson(np.clip(img, 0, None)).astype(float) + rng.normal(0, inst.read_noise_e, img.shape)
        if opts['bits'] == 8:   # ADC: 8-bit quantisation with auto gain chosen so the Earthshine sits at ~ 40 ADU
            adu = np.clip(np.round(img * (40.0 / np.median(bkg))), 0, 255); img = adu / (40.0 / np.median(bkg))
        frames[f] = img
    if opts['denoise']:   # phone-like temporal denoising: exponential running average (alpha 0.5) applied in-camera
        out = np.zeros_like(frames); acc = frames[0]
        for f in range(nframes):
            acc = 0.5 * acc + 0.5 * frames[f]; out[f] = acc
        frames = out
    return frames

def detect(frames, inst, opts, thresh=5.0, pos=None, flash_frames=None, tol=3):
    """Photometric normalisation + running-median subtraction + PSF matched filter with an *empirical* noise
    estimate (MAD of the filtered difference image).  Returns (max SNR at the injected position over the flash
    frames, list of per-frame false-alarm flags on the central region excluding the injected position)."""
    sig = max(inst.seeing_arcsec / inst.pixel_scale_arcsec / 2.355, 0.6)
    scale = np.median(frames, axis=(1, 2)); fr = frames * (scale.mean() / scale)[:, None, None]
    # frame registration (integer-pixel, phase correlation against the first-pass median), as any lunar pipeline does
    med0 = np.median(fr, axis=0); F0 = np.fft.fft2(med0 - med0.mean())
    for f in range(fr.shape[0]):
        Ff = np.fft.fft2(fr[f] - fr[f].mean()); cc = np.real(np.fft.ifft2(F0 * np.conj(Ff)))
        dy, dx = np.unravel_index(np.argmax(cc), cc.shape); dy = dy if dy < cc.shape[0] // 2 else dy - cc.shape[0]; dx = dx if dx < cc.shape[1] // 2 else dx - cc.shape[1]
        if dy or dx:
            fr[f] = np.roll(np.roll(fr[f], dy, 0), dx, 1)
    med = np.median(fr, axis=0)
    snr_at = 0.0; fa = []
    n = fr.shape[1]
    for f in range(fr.shape[0]):
        mf = gaussian_filter(fr[f] - med, sig)
        c = mf[8:-8, 8:-8]
        noise = 1.4826 * np.median(np.abs(c - np.median(c))) + 1e-9
        s = mf / noise
        if pos is not None and flash_frames is not None and f in flash_frames:
            y0, y1 = max(pos[0] - tol, 0), min(pos[0] + tol + 1, n); x0, x1 = max(pos[1] - tol, 0), min(pos[1] + tol + 1, n)
            snr_at = max(snr_at, float(s[y0:y1, x0:x1].max()))
        mask = np.ones_like(s, dtype=bool); mask[:8, :] = False; mask[-8:, :] = False; mask[:, :8] = False; mask[:, -8:] = False
        if pos is not None:
            mask[max(pos[0] - 2 * tol, 0):pos[0] + 2 * tol + 1, max(pos[1] - 2 * tol, 0):pos[1] + 2 * tol + 1] = False
        fa.append(bool(s[mask].max() > thresh))
    return snr_at, fa

systems = ['NELIOTA-like 1.2 m (R, 23 ms, dual camera)', 'Amateur 0.35 m (broad, 30 fps, 8-bit CMOS)', 'Phone afocal on 20 cm (1/30 s, 8-bit, denoised video)', 'Phone standalone 24 mm (1/30 s, 8-bit, denoised video)']
mags = {systems[0]: np.arange(7, 15.1, 0.5), systems[1]: np.arange(4, 13.1, 0.5), systems[2]: np.arange(2, 12.1, 0.5), systems[3]: np.arange(-4, 6.1, 0.5)}
results = {}
NTRIAL = int(os.environ.get('NTRIAL', '12'))
for name in systems:
    inst, opts = make_system(name)
    bkg = background_map(inst, opts['n'], scat_side=(opts['n'] > 100))
    comp = []; fa = 0; nfa = 0
    for m in mags[name]:
        det = 0
        for trial in range(NTRIAL):
            tau = float(np.exp(rng.uniform(np.log(0.1), np.log(1.0))))
            fm = I.FlashModel(E_k=1.0, eta_vis=1.0, T0=2500, Tfloor=1200, tau_T=tau, tau_L=tau)
            # scale so that peak magnitude in this band == m
            offset = m - fm.peak_magnitude(inst.band)
            nfl = max(1, int(np.ceil(tau * 3 / inst.frame_time_s)))
            t0 = rng.uniform(0, inst.frame_time_s)
            src = []
            for j in range(nfl):
                a = t0 + j * inst.frame_time_s; m_avg = fm.exposure_averaged_magnitude(inst.band, inst.exposure_s, t_start=a) + offset
                src.append(D.photons_from_mag(m_avg, inst.band, inst.area, inst.throughput, inst.exposure_s))
            pos = (rng.integers(12, opts['n'] - 12), rng.integers(12, opts['n'] - 12))
            flash_frames = list(range(15, 15 + nfl))
            fr = render(inst, opts, bkg, src, pos, nframes=30, flash_frames=flash_frames)
            snr, hits = detect(fr, inst, opts, pos=pos, flash_frames=flash_frames)
            ok = snr >= 5.0
            if opts['dual']:
                fr2 = render(inst, opts, bkg, src, pos, nframes=30, flash_frames=flash_frames); snr2, _ = detect(fr2, inst, opts, pos=pos, flash_frames=flash_frames); ok = ok and snr2 >= 5.0
            det += ok
        comp.append(det / NTRIAL)
    # false alarms: pure background runs
    for trial in range(6):
        fr = render(inst, opts, bkg, None, None, nframes=30); snr, hits = detect(fr, inst, opts); fa += sum(hits); nfa += len(hits)
    results[name] = dict(ntrial=NTRIAL, mags=[float(x) for x in mags[name]], completeness=comp, false_alarm_per_frame=fa / nfa, dual=opts['dual'], band=inst.band, pixel_scale=inst.pixel_scale_arcsec,
                         analytic_8sigma_limit=float(D.limiting_magnitude(inst, D.total_background_sb(inst.band, ILLUM, 8.0, -20), 8.0)))
    print(name, 'completeness', np.round(comp, 2), 'FA/frame %.3f' % (fa / nfa), 'analytic 8-sigma limit %.1f' % results[name]['analytic_8sigma_limit'])
json.dump(results, open(f'{root}/outputs/tables/injection_recovery.json', 'w'), indent=1)
import runpy
runpy.run_path(os.path.join(root, 'scripts', 'make_injection_figure.py'), run_name='__main__')
