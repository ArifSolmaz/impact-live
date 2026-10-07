"""Injection-recovery and false-alarm experiment on synthetic lunar video (SIMULATION, release 2.1).

Scene and atmosphere: an unblurred lunar radiance scene (the scikit-image 'moon' photograph used as an albedo texture
at 1.5 arcsec per texture pixel, scaled to the modelled Earthshine surface brightness at illuminated fraction 0.35, plus
the scattered-light gradient of the sunlit crescent 6' beyond one edge of the field) is convolved IN EVERY FRAME with
that frame's seeing PSF (Gaussian, FWHM varying as a log-normal AR(1) process, 10 % rms, frame-to-frame correlation 0.9)
and shifted by that frame's image motion (AR(1) wander plus white jitter), with 1 % transparency flicker. The video is
rendered as independent clips (different texture crops and atmosphere realisations). The injected flash is a point
source convolved with the same PSF and shifted with the same motion; its counts in each exposure are the
cooling-blackbody light curve integrated over the actual exposure interval (random phase), T0 from the broad prior,
tau log-uniform 0.1-1 s.
Detector: Poisson photon noise, Gaussian read noise, charge clipped at the full well, ADC with the stated gain, bias and
bit depth (8-bit video cameras: gain set so that the Earthshine background sits at a fixed code value); phones apply an
in-camera temporal recursive denoising filter.
Pipeline (ONE detection function for injected and blank video, re-audit ST-N01): causal sub-pixel cross-correlation
registration of the full frame to the rolling reference (peak searched within +-7 px, sub-pixel step limited to
+-0.5 px; an unrestricted search occasionally locked onto distant spurious peaks in low-contrast 8-bit phone video);
in a fixed analysis box of W x W pixels: normalisation by the
ratio of the frame's median to the median of the previous 25 frames' medians, reference = median of the previous 25
registered frames, difference image, Gaussian matched filter at the nominal seeing, noise from the median absolute
deviation of the filtered difference inside the box, candidates = local maxima >= 5 sigma. Blank video is tiled into
such boxes; an injection is analysed in the box around the predicted position (truth plus a random offset), and the
truth position is used only AFTER detection, to classify a candidate within 2 pixels as a recovery. NELIOTA-like: two
synchronised cameras (Rc and Ic) behind one telescope share the seeing, motion and transparency, with independent
noise; a validated detection needs candidates in BOTH cameras in the same frame within 2 pixels of each other (and of
the truth for an injection), the same rule as in the blank coincidence count.
Observation window (re-audit ST-N02): every exposure from the onset to 4 tau after it (plus 3 frames for the phone
filter tail), without a frame cap; the frame of first detection is recorded so that recovery within the first 40
frames (release 2.0's cap) can be compared.
Outputs per system: recovery fraction per injected peak magnitude with Wilson 95 % intervals (NTRIAL trials per bin), a
monotone logistic fit with bootstrap intervals on m50 and m90, and false alarms: candidates per analysed box and
frame, the fraction of box-frames with a candidate, and dual-camera coincidences, with clip-level bootstrap intervals
and the dispersion of the per-clip counts (re-audit ST-08: frames within a clip are correlated through the seeing,
motion and rolling reference, so no exact Poisson interval is claimed).
Random numbers: every clip, every trial and the fit bootstrap of each system draw from their own generator, seeded
with [SEED, system index, ...] (numpy SeedSequence), so that a platform-dependent difference in one draw (floating-point
libraries differ between computers) changes at most that clip or trial instead of every later draw.
Approximations: injection trials reuse the pre-rendered background clips (trials differ in clip, time, position, phase
and flash parameters; their background noise is not fully independent); registration shifts are computed on the
background clip. Not modelled: rolling shutter, compression artefacts, cosmic rays, clouds, real camera firmware.
Nothing here is observed footage, and the recovery curves are not an empirical calibration of any real system."""
import sys, os, json, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings('ignore')
from skimage import data
from scipy.ndimage import gaussian_filter, zoom, maximum_filter
from scipy.special import erf
from scipy.stats import chi2
from scipy.optimize import minimize
from ayap1obs import detect as D, impact as I, montecarlo as MC
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('validation', 'screening', 'reachability', 'scenarios', 'tables', 'figures', 'logs'):  # OUTPUT_DIRS
    os.makedirs(os.path.join(root, 'outputs', _d), exist_ok=True)
SEED = 20261007
RNG_NOTE = ('one numpy generator per system and clip, per trial and for the fit bootstrap, each seeded with [SEED, system index, ...], so '
            'that a platform-dependent difference in one random draw cannot shift every later draw')
TEX = data.moon().astype(float); TEX /= TEX.mean()
TEX_SCALE = 1.5          # arcsec per texture pixel (declared)
ILLUM = 0.35
K_REF = 25
THRESH = 5.0
MATCH_PX = 2
BOX = 40                 # analysis box (pixels), identical for injected and blank video
CAP_R20 = 40             # release-2.0 frame cap, kept only for the comparison
NTRIAL = int(os.environ.get('NTRIAL', '100'))
N_SEQ = int(os.environ.get('NSEQ', '3000'))
N_BOOT = 200

def inst_of(name):
    if name == 'nel':
        mk = lambda band: D.Instrument(f'NELIOTA-like {band}', 1.2, band, 0.8, (17.0, 14.4), 0.023, 1 / 30, throughput=0.5, obstruction=0.1, read_noise_e=5.1, seeing_arcsec=2.5, full_well_e=3.0e4)
        return [mk('Rc'), mk('Ic')], dict(label='NELIOTA-like 1.2 m (Rc + Ic twin sCMOS, 23 ms at 30 fps, synchronised)', bits=16, gain=0.46, bias=100, n=96, denoise=False, jitter=0.3, wander=0.6, auto_code=None)
    if name == 'tug':
        return [D.Instrument('TUG T100 + QHY174GPS', 1.0, 'broad', 0.45, (6.0, 4.5), 0.02, 0.0222, throughput=0.45, obstruction=0.15, read_noise_e=2.5, seeing_arcsec=1.5, full_well_e=3.2e4)], \
               dict(label='TUG T100 + QHY174GPS-class (broad, 20 ms at 45 fps, 12-bit)', bits=12, gain=8.0, bias=50, n=128, denoise=False, jitter=0.4, wander=0.8, auto_code=None)
    if name == 'ama':
        return [D.Instrument('Amateur 0.35 m', 0.35, 'broad', 1.0, (20.0, 15.0), 0.03, 1 / 30, throughput=0.5, obstruction=0.15, read_noise_e=2.0, seeing_arcsec=3.0, full_well_e=2.0e4)], \
               dict(label='Amateur 0.35 m (broad, 30 fps, 8-bit video)', bits=8, gain=None, bias=0, n=96, denoise=False, jitter=0.4, wander=0.8, auto_code=40.0)
    if name == 'afo':
        return [D.phone_instrument('afocal')], dict(label='Phone afocal on 20 cm (1/30 s, 8-bit, temporally denoised)', bits=8, gain=None, bias=0, n=96, denoise=True, jitter=1.0, wander=1.5, auto_code=40.0)
    if name == 'std':
        return [D.phone_instrument('standalone')], dict(label='Phone standalone 24 mm (1/30 s, 8-bit, temporally denoised; exposure set by the crescent)', bits=8, gain=None, bias=0, n=48, denoise=True, jitter=0.2, wander=0.3, auto_code=8.0)
    raise ValueError(name)
SYSTEMS = ['nel', 'tug', 'ama', 'afo', 'std']

def scene_e(inst, n, rng):
    """Unblurred background electrons per pixel per exposure (Earthshine-lit texture + scattered-light gradient)."""
    sb_es = D.earthshine_sb_V(ILLUM) - D.LUNAR_COLOR_VS_V[inst.band]
    N_es = D.photons_from_mag(sb_es, inst.band, inst.area, inst.throughput, inst.exposure_s) * inst.pixel_scale_arcsec ** 2
    z = TEX_SCALE / inst.pixel_scale_arcsec                       # texture pixels -> camera pixels
    need = int(np.ceil(n / z)) + 2
    if need < TEX.shape[0]:
        y0, x0 = rng.integers(0, TEX.shape[0] - need, 2); t = TEX[y0:y0 + need, x0:x0 + need]
    else:
        t = np.tile(TEX, (need // TEX.shape[0] + 1, need // TEX.shape[1] + 1))[:need, :need]
    if z < 1:
        t = gaussian_filter(t, 0.5 / z)                           # area-average before downsampling
    t = zoom(t, z, order=1)[:n, :n]
    if t.shape != (n, n):
        t = np.resize(t, (n, n))
    bkg = N_es * np.clip(t / t.mean(), 0.3, 3.0)
    if n * inst.pixel_scale_arcsec < 1800:                        # telescopic field: crescent 6' beyond one edge
        x = (np.arange(n) * inst.pixel_scale_arcsec / 60.0)[None, :]
        dist = 6.0 + (n * inst.pixel_scale_arcsec / 60.0 - x)
        sb_sc = D.scattered_sb_V(dist) - D.LUNAR_COLOR_VS_V[inst.band]
        bkg = bkg + D.photons_from_mag(sb_sc, inst.band, inst.area, inst.throughput, inst.exposure_s) * inst.pixel_scale_arcsec ** 2
    return bkg

def ar1(rng, n, rho, sd):
    x = np.empty(n); x[0] = rng.normal(0, sd)
    e = rng.normal(0, sd * np.sqrt(1 - rho ** 2), n)
    for k in range(1, n):
        x[k] = rho * x[k - 1] + e[k]
    return x

def atmosphere(rng, n, inst, opts):
    sig0 = max(inst.seeing_arcsec / inst.pixel_scale_arcsec / 2.355, 0.5)
    sig = sig0 * np.exp(ar1(rng, n, 0.9, 0.10))
    dx = ar1(rng, n, 0.98, opts['wander']) + rng.normal(0, opts['jitter'], n)
    dy = ar1(rng, n, 0.98, opts['wander']) + rng.normal(0, opts['jitter'], n)
    tr = 1.0 + ar1(rng, n, 0.9, 0.01)
    return dict(sig=sig, dx=dx, dy=dy, tr=tr, sig0=sig0)

def render_clean(scene_F, n, sig, dx, dy):
    """Scene convolved with a Gaussian PSF of width sig (px) and shifted by (dx, dy) px (Fourier domain)."""
    u = np.fft.fftfreq(n)[None, :]; v = np.fft.fftfreq(n)[:, None]
    H = np.exp(-2 * np.pi ** 2 * sig ** 2 * (u ** 2 + v ** 2)) * np.exp(-2j * np.pi * (u * dx + v * dy))
    return np.real(np.fft.ifft2(scene_F * H))

def stamp(n, y, x, sig):
    """Pixel-integrated Gaussian PSF (sum 1) centred at (y, x) on an n x n grid."""
    edges = np.arange(n + 1) - 0.5
    gy = 0.5 * (erf((edges[1:] - y) / (np.sqrt(2) * sig)) - erf((edges[:-1] - y) / (np.sqrt(2) * sig)))
    gx = 0.5 * (erf((edges[1:] - x) / (np.sqrt(2) * sig)) - erf((edges[:-1] - x) / (np.sqrt(2) * sig)))
    return gy[:, None] * gx[None, :]

def adc(e, inst, opts, gain):
    e = np.minimum(e, inst.full_well_e)
    adu = np.clip(np.round(e / gain) + opts['bias'], 0, 2 ** opts['bits'] - 1)
    return (adu - opts['bias']) * gain

class Clip:
    """Pre-rendered background clip for one camera of a system (twin cameras share the clip's atmosphere)."""
    def __init__(self, inst, opts, scene, atm, rng, n_frames):
        n = opts['n']; self.inst, self.opts, self.n, self.atm = inst, opts, n, atm
        self.gain = opts['gain'] if opts['gain'] else float(np.median(scene)) / opts['auto_code']
        F = np.fft.fft2(scene)
        self.raw = np.empty((n_frames, n, n), np.float32)          # electrons after photon and read noise (before clip/ADC)
        for k in range(n_frames):
            img = render_clean(F, n, atm['sig'][k], atm['dx'][k], atm['dy'][k]) * atm['tr'][k]
            self.raw[k] = rng.poisson(np.clip(img, 0, None)) + rng.normal(0, inst.read_noise_e, (n, n))
        self.proc = np.empty_like(self.raw)
        for k in range(n_frames):
            self.proc[k] = adc(self.raw[k], inst, opts, self.gain)
        if opts['denoise']:
            self.proc = denoise(self.proc)
        self.shift, self.reg = register_sequence(self.proc)
        self.scale = np.median(self.proc.reshape(n_frames, -1), axis=1)

def denoise(frames, alpha=0.5, start=None):
    out = frames.copy()
    for k in range(1, len(frames)):
        out[k] = alpha * out[k - 1] + (1 - alpha) * frames[k]
    return out

def fshift(img, dy, dx):
    """Sub-pixel (Fourier) shift of an image by (dy, dx) pixels."""
    n0, n1 = img.shape
    u = np.fft.fftfreq(n1)[None, :]; v = np.fft.fftfreq(n0)[:, None]
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.exp(-2j * np.pi * (u * dx + v * dy))))

MAX_SHIFT = 7            # registration search window (pixels): the analysis crops are padded by 8 px (PAD in trial())

def xcorr_shift(ref, img, max_shift=MAX_SHIFT):
    """Shift (dy, dx) that registers img onto ref: cross-correlation peak within +-max_shift pixels, with parabolic
    sub-pixel refinement limited to +-0.5 pixel. The window excludes spurious distant peaks of low-contrast frames
    (8-bit phone video), which otherwise make the registration jump by 10-15 pixels, beyond the padded analysis crop."""
    n = ref.shape[0]
    cc = np.real(np.fft.ifft2(np.fft.fft2(ref - ref.mean()) * np.conj(np.fft.fft2(img - img.mean()))))
    lag = np.fft.fftfreq(n, 1.0 / n)                                  # 0, 1, ..., -1 (circular lags)
    win = (np.abs(lag)[:, None] <= max_shift) & (np.abs(lag)[None, :] <= max_shift)
    iy, ix = np.unravel_index(np.argmax(np.where(win, cc, -np.inf)), cc.shape)
    def para(cm, c0, cp):
        d = cm - 2 * c0 + cp
        return 0.0 if d >= 0 else float(np.clip(0.5 * (cm - cp) / d, -0.5, 0.5))
    fy = para(cc[(iy - 1) % n, ix], cc[iy, ix], cc[(iy + 1) % n, ix]); fx = para(cc[iy, (ix - 1) % n], cc[iy, ix], cc[iy, (ix + 1) % n])
    dy = iy + fy; dx = ix + fx
    return (dy if dy < n / 2 else dy - n), (dx if dx < n / 2 else dx - n)

def register_sequence(proc):
    """Causal sub-pixel registration of each frame to the median of its K_REF registered predecessors.
    Returns (shifts, registered frames)."""
    n_seq = proc.shape[0]; sh = np.zeros((n_seq, 2))
    reg = np.empty_like(proc); reg[:K_REF] = proc[:K_REF]
    for k in range(K_REF, n_seq):
        ref = np.median(reg[k - K_REF:k], axis=0)
        dy, dx = xcorr_shift(ref, proc[k]); sh[k] = (dy, dx)
        reg[k] = fshift(proc[k], dy, dx)
    return sh, reg

def detect_box(cur_box, past_boxes, scale_cur, scale_ref, sig0, inner=4, thresh=THRESH):
    """THE detection step, used identically for injected and blank video: normalise the registered box, subtract the
    median of the past registered boxes, matched-filter, normalise by the MAD noise inside the box and return the local
    maxima >= thresh (box coordinates) and their SNR."""
    d = cur_box * (scale_ref / max(scale_cur, 1e-9)) - np.median(past_boxes, axis=0)
    mf = gaussian_filter(d, sig0)
    c = mf[inner:-inner, inner:-inner]
    s = mf / (1.4826 * np.median(np.abs(c - np.median(c))) + 1e-12)
    loc = (s == maximum_filter(s, size=3)) & (s >= thresh)
    loc[:inner, :] = False; loc[-inner:, :] = False; loc[:, :inner] = False; loc[:, -inner:] = False
    pts = np.argwhere(loc)
    return pts, s[loc] if len(pts) else np.zeros(0)

def boxes_of(n, margin, W):
    """Non-overlapping analysis boxes tiling the frame inside the margin: list of (y0, x0)."""
    st = list(range(margin, n - margin - W + 1, W)) or [margin]
    return [(y0, x0) for y0 in st for x0 in st]

def blank_false_alarms(clips_by_cam, margin, W):
    """Candidates in every analysed box and frame of the blank clips; dual coincidences (both cameras, same frame,
    <= MATCH_PX apart) for twin cameras. Statistics per clip for clip-level resampling."""
    n = clips_by_cam[0][0].n; bx = boxes_of(n, margin, W)
    per_clip = []
    for ci in range(len(clips_by_cam[0])):
        cams = [cl[ci] for cl in clips_by_cam]; nf = cams[0].proc.shape[0]
        cand = np.zeros(len(cams), int); fr_with = np.zeros(len(cams), int); coinc = 0; bf = 0
        for k in range(K_REF, nf):
            for (y0, x0) in bx:
                pts = []
                for j, cl in enumerate(cams):
                    p, _ = detect_box(cl.reg[k, y0:y0 + W, x0:x0 + W], cl.reg[k - K_REF:k, y0:y0 + W, x0:x0 + W], cl.scale[k],
                                      np.median(cl.scale[k - K_REF:k]), seq_sig0(cl))
                    pts.append(p); cand[j] += len(p); fr_with[j] += int(len(p) > 0)
                if len(cams) == 2 and len(pts[0]) and len(pts[1]):
                    dd = np.hypot(pts[0][:, None, 0] - pts[1][None, :, 0], pts[0][:, None, 1] - pts[1][None, :, 1])
                    coinc += int((dd <= MATCH_PX).any())
                bf += 1
        per_clip.append(dict(box_frames=bf, candidates=cand.tolist(), box_frames_with_candidate=fr_with.tolist(), dual_coincident_box_frames=coinc))
    return per_clip, bx

def clip_bootstrap(per_clip, key, cam=None, n_boot=2000, seed=5):
    """Rate per box-frame and its clip-level bootstrap 95 % interval; dispersion index of the per-clip counts."""
    k = np.array([c[key][cam] if cam is not None else c[key] for c in per_clip], float); n = np.array([c['box_frames'] for c in per_clip], float)
    rate = k.sum() / n.sum()
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(k), (n_boot, len(k)))
    br = k[idx].sum(axis=1) / n[idx].sum(axis=1)
    exp_k = n * rate
    disp = float(np.sum((k - exp_k) ** 2 / np.maximum(exp_k, 1e-12)) / max(len(k) - 1, 1)) if rate > 0 else None
    lo, hi = (float(np.percentile(br, 2.5)), float(np.percentile(br, 97.5))) if k.sum() > 0 else (0.0, float(3.689 / n.sum()))
    return dict(rate=float(rate), ci95_clip_bootstrap=[lo, hi], total=int(k.sum()), box_frames=int(n.sum()), dispersion_index=disp,
                note='clip-level bootstrap (zero counts: one-sided 97.5 % binomial upper limit over all box-frames, a conditional approximation)')

def seq_sig0(seq):
    return max(seq.inst.seeing_arcsec / seq.inst.pixel_scale_arcsec / 2.355, 0.5)

def poisson_ci(k, n):
    lo = 0.0 if k == 0 else chi2.ppf(0.025, 2 * k) / 2
    hi = chi2.ppf(0.975, 2 * k + 2) / 2
    return [lo / n, hi / n]

def wilson(k, n):
    return list(MC.wilson(k, n))

def flash_counts(inst, m_peak_band, T0, tau, phase, n_frames):
    """Electrons in each exposure (frames start at phase - frame_time + j frame_time) for a flash whose band peak
    magnitude is m_peak_band, from the tabulated light-curve integrals (impact.G_eval, impact.peak_rate_eval; worst error
    below 1e-4 mag, outputs/validation/lightcurve_accuracy.md)."""
    pk = float(I.peak_rate_eval(inst.band, np.array([T0]))[0])
    b = I.BANDS[inst.band]
    e_norm = 10 ** (-0.4 * m_peak_band) * b['f0'] * b['width'] * tau / pk       # E_bol / (4 pi d^2), J m^-2
    s0 = phase - inst.frame_time_s + inst.frame_time_s * np.arange(n_frames)
    a = np.maximum(s0, 0.0); bb = np.maximum(s0 + inst.exposure_s, 0.0)
    dG = I.G_eval(inst.band, np.full(n_frames, T0), (bb / tau)[:, None])[:, 0] - I.G_eval(inst.band, np.full(n_frames, T0), (a / tau)[:, None])[:, 0]
    return D.photons_from_energy(e_norm * np.clip(dG, 0, None), inst.band, inst.area, inst.throughput)

def trial(clips_by_cam, insts, opts, m_peak, rng, margin=12, W=BOX):
    """One injection analysed with detect_box. Returns (detected per camera, validated dual, first detection frame
    index after the onset or None, number of frames in the search window: onset to 4 tau plus the phone filter tail;
    a single camera stops at its first recovery, which does not shorten the window counted here)."""
    n = opts['n']; ci = int(rng.integers(len(clips_by_cam[0]))); cams = [cl[ci] for cl in clips_by_cam]
    nf = cams[0].proc.shape[0]; atm = cams[0].atm
    T0 = float(I.temperature_prior(rng, 1, 'broad')[0]); tau = float(np.exp(rng.uniform(np.log(0.1), np.log(1.0))))
    Tf = insts[0].frame_time_s; ph = rng.uniform(0, Tf)
    tail = 3 if opts['denoise'] else 0
    L = int(np.ceil(4 * tau / Tf) + 2); L = min(L, nf - K_REF - 6 - tail)             # cap only by the clip length
    k0 = int(rng.integers(K_REF + 5, nf - L - tail))
    y, x = rng.uniform(margin + 4, n - margin - 4, 2)
    cnt0 = flash_counts(insts[0], m_peak, T0, tau, ph, L)
    counts = [cnt0] + [flash_counts(inst, m_peak, T0, tau, ph, L) * band_peak_ratio(insts[0].band, inst.band, T0) for inst in insts[1:]]
    # analysis box around the PREDICTED position (truth + random offset within +-5 px), clipped to the frame
    yc = y + atm['dy'][k0] + cams[0].shift[k0, 0] + rng.uniform(-5, 5); xc = x + atm['dx'][k0] + cams[0].shift[k0, 1] + rng.uniform(-5, 5)
    y0 = int(np.clip(round(yc) - W // 2, 0, n - W)); x0 = int(np.clip(round(xc) - W // 2, 0, n - W))
    PAD = 8                                                         # registration of a padded crop (shifts are < 8 px)
    ry0, ry1 = max(y0 - PAD, 0), min(y0 + W + PAD, n); rx0, rx1 = max(x0 - PAD, 0), min(x0 + W + PAD, n)
    by, bx_ = y0 - ry0, x0 - rx0
    def near_truth(p, k, cl):
        ty = y + atm['dy'][k] + cl.shift[k, 0]; tx = x + atm['dx'][k] + cl.shift[k, 1]
        return np.hypot(p[:, 0] - ty, p[:, 1] - tx) <= MATCH_PX if len(p) else np.zeros(0, bool)
    hits = []                                                       # per camera: list over frames of candidate arrays (frame coordinates)
    stop_single = len(cams) == 1                                    # single camera: stop at the first recovery
    for j, (cl, inst) in enumerate(zip(cams, insts)):
        frames = {}
        for jj in range(L):
            k = k0 + jj
            st = stamp(n, y + atm['dy'][k], x + atm['dx'][k], atm['sig'][k])[ry0:ry1, rx0:rx1] * counts[j][jj] * atm['tr'][k]
            frames[k] = adc(cl.raw[k, ry0:ry1, rx0:rx1] + rng.poisson(np.clip(st, 0, None)), inst, opts, cl.gain)
        if opts['denoise']:                                        # in-camera recursive filter continues from k0-1
            prev = cl.proc[k0 - 1, ry0:ry1, rx0:rx1]
            for jj in range(L + tail):
                k = k0 + jj
                inp = frames[k] if k in frames else adc(cl.raw[k, ry0:ry1, rx0:rx1], inst, opts, cl.gain)
                prev = 0.5 * prev + 0.5 * inp; frames[k] = prev
        reg = {}
        per_frame = []
        for k in sorted(frames):
            reg[k] = fshift(frames[k], *cl.shift[k])[by:by + W, bx_:bx_ + W]
            past = np.array([reg[kk] if kk in reg else cl.reg[kk, y0:y0 + W, x0:x0 + W] for kk in range(k - K_REF, k)])
            p, _ = detect_box(reg[k], past, cl.scale[k], np.median(cl.scale[k - K_REF:k]), seq_sig0(cl))
            pf = p + np.array([y0, x0]) if len(p) else np.zeros((0, 2))
            per_frame.append((k, pf))
            if stop_single and len(pf) and near_truth(pf, k, cl).any():
                break
        hits.append(per_frame)
    det = []; first = None
    for j, (cl, per_frame) in enumerate(zip(cams, hits)):
        ok = [bool(near_truth(p, k, cl).any()) for k, p in per_frame]
        det.append(any(ok))
        if j == 0 and any(ok):
            first = int(np.argmax(ok))
    dual = False
    if len(cams) == 2:
        for (k, p0), (_, p1) in zip(hits[0], hits[1]):
            a0 = p0[near_truth(p0, k, cams[0])]; a1 = p1[near_truth(p1, k, cams[1])]
            if len(a0) and len(a1) and (np.hypot(a0[:, None, 0] - a1[None, :, 0], a0[:, None, 1] - a1[None, :, 1]) <= MATCH_PX).any():
                dual = True; break
    return det, dual, first, L + tail

_RATIO = {}
def band_peak_ratio(b0, b1, T0):
    """Ratio (band b1 peak photon-normalised flux)/(band b0) for a common E_bol, used so that both cameras see one
    physical flash: flash_counts(b, m) sets each band's own peak to m; multiplying by 10^(-0.4 (m_b1 - m_b0)) restores
    the colour of a blackbody at T0."""
    m0 = I.peak_band_magnitude_fast(b0, np.array([1e-4]), np.array([1e9]), np.array([T0]), np.array([0.5]))[0]
    m1 = I.peak_band_magnitude_fast(b1, np.array([1e-4]), np.array([1e9]), np.array([T0]), np.array([0.5]))[0]
    return 10 ** (-0.4 * (m1 - m0))

def fit_logistic(m, det):
    """MLE of P(m) = 1 / (1 + exp((m - m50) / w)); returns (m50, w)."""
    m = np.asarray(m, float); det = np.asarray(det, float)
    def nll(p):
        m50, lw = p; w = np.exp(lw)
        z = np.clip((m - m50) / w, -50, 50); P_ = 1 / (1 + np.exp(z)); P_ = np.clip(P_, 1e-9, 1 - 1e-9)
        return -np.sum(det * np.log(P_) + (1 - det) * np.log(1 - P_))
    um = np.unique(m); fr = np.array([det[m == u].mean() for u in um])
    m0 = float(um[np.argmin(np.abs(fr - 0.5))]) if len(um) else 0.0
    r = minimize(nll, [m0, np.log(0.3)], method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-6, maxiter=2000))
    return float(r.x[0]), float(np.exp(r.x[1]))

def main():
    results = {'_settings': dict(seed=SEED, ntrial=NTRIAL, n_seq=N_SEQ, k_ref=K_REF, threshold_sigma=THRESH, match_px=MATCH_PX, box_px=BOX,
                                 max_shift_px=MAX_SHIFT, random_streams=RNG_NOTE)}
    n_clips = max(2, min(10, N_SEQ // 250)); clip_len = N_SEQ // n_clips
    for si, name in enumerate(SYSTEMS):
        tic = time.time()
        insts, opts = inst_of(name)
        n = opts['n']; margin = 12 if n > 60 else 6; W = min(BOX, n - 2 * margin)
        clips_by_cam = [[] for _ in insts]
        for c in range(n_clips):
            rc = np.random.default_rng([SEED, si, 0, c])                     # this clip's own stream
            scene0 = scene_e(insts[0], n, rc)
            atm = atmosphere(rc, clip_len, insts[0], opts)
            for j, inst in enumerate(insts):
                sc = scene0 * (scene_e(inst, n, np.random.default_rng(c)).mean() / scene0.mean()) if j else scene0
                clips_by_cam[j].append(Clip(inst, opts, sc, atm, rc, clip_len))
        bkg_sb = D.total_background_sb(insts[0].band, ILLUM, 8.0, -20.0)
        lim8 = float(D.limiting_magnitude(insts[0], bkg_sb, 8.0)); lim5 = float(D.limiting_magnitude(insts[0], bkg_sb, 5.0))
        mags = np.round(np.arange(lim8 - 2.5, lim8 + 2.01, 0.25), 2)
        rows = []; all_m = []; all_det = []; all_dual = []; all_cap = []; n_frames_used = []
        for mi, m in enumerate(mags):
            det_c = []; dual_c = []; cap_c = []
            for ti in range(NTRIAL):
                rt = np.random.default_rng([SEED, si, 1, mi, ti])               # this trial's own stream
                d, du, first, nfr = trial(clips_by_cam, insts, opts, float(m), rt, margin=margin, W=W)
                det_c.append(d); dual_c.append(du); cap_c.append(first is not None and first < CAP_R20); n_frames_used.append(nfr)
            det_c = np.array(det_c); k0 = int(det_c[:, 0].sum())
            row = dict(mag=float(m), n=NTRIAL, k_cam0=k0, frac_cam0=k0 / NTRIAL, wilson_cam0=wilson(k0, NTRIAL), k_cam0_first40=int(np.sum(cap_c)))
            if len(insts) == 2:
                k1 = int(det_c[:, 1].sum()); kd = int(np.sum(dual_c))
                row.update(k_cam1=k1, frac_cam1=k1 / NTRIAL, wilson_cam1=wilson(k1, NTRIAL), k_dual=kd, frac_dual=kd / NTRIAL, wilson_dual=wilson(kd, NTRIAL))
            rows.append(row)
            all_m += [m] * NTRIAL; all_det += list(det_c[:, 0]); all_dual += list(dual_c); all_cap += cap_c
        all_m = np.array(all_m); all_det = np.array(all_det, float); all_dual = np.array(all_dual, float); all_cap = np.array(all_cap, float)
        rb = np.random.default_rng([SEED, si, 2])                              # bootstrap of the fits
        def summary(detv):
            m50, w = fit_logistic(all_m, detv)
            boots = []
            for _ in range(N_BOOT):
                idx = np.concatenate([rb.choice(np.where(all_m == u)[0], NTRIAL) for u in mags])
                boots.append(fit_logistic(all_m[idx], detv[idx]))
            b = np.array(boots); m90 = m50 - w * np.log(9); b90 = b[:, 0] - b[:, 1] * np.log(9)
            return dict(m50=m50, width=w, m50_ci95=[float(np.percentile(b[:, 0], 2.5)), float(np.percentile(b[:, 0], 97.5))],
                        m90=float(m90), m90_ci95=[float(np.percentile(b90, 2.5)), float(np.percentile(b90, 97.5))],
                        width_ci95=[float(np.percentile(b[:, 1], 2.5)), float(np.percentile(b[:, 1], 97.5))])
        fits = dict(cam0=summary(all_det), cam0_first40_frames=summary(all_cap))
        if len(insts) == 2:
            fits['dual'] = summary(all_dual)
        per_clip, bx = blank_false_alarms(clips_by_cam, margin, W)
        fa = dict(n_clips=n_clips, clip_frames=clip_len, analysed_frames_per_clip=clip_len - K_REF, boxes_per_frame=len(bx), box_px=W,
                  box_area_arcmin2=(W * insts[0].pixel_scale_arcsec / 60.0) ** 2, per_clip=per_clip,
                  candidate_rate_per_box_frame=[clip_bootstrap(per_clip, 'candidates', j) for j in range(len(insts))],
                  box_frames_with_candidate=[clip_bootstrap(per_clip, 'box_frames_with_candidate', j) for j in range(len(insts))])
        if len(insts) == 2:
            fa['dual_coincidence_rate_per_box_frame'] = clip_bootstrap(per_clip, 'dual_coincident_box_frames')
        fa['median_frames_per_injection'] = float(np.median(n_frames_used))
        fa['expected_false_candidates_per_injection_window'] = fa['candidate_rate_per_box_frame'][0]['rate'] * fa['median_frames_per_injection']
        shifts = np.concatenate([np.abs(cl.shift[K_REF:]).max(axis=1) for cams in clips_by_cam for cl in cams])
        reg = dict(max_abs_shift_px=float(shifts.max()), frames=int(len(shifts)), frames_at_search_limit=int((shifts >= MAX_SHIFT - 0.5).sum()),
                   note=f'registration shifts of the blank clips (search window +-{MAX_SHIFT} px; frames whose shift reaches the window limit)')
        results[name] = dict(label=opts['label'], bands=[i.band for i in insts], ntrial=NTRIAL, n_seq=N_SEQ, rows=rows, fits=fits, false_alarms=fa, registration=reg,
                             analytic_limits=dict(steady_snr8=lim8, steady_snr5=lim5, background_sb=float(bkg_sb),
                                                  note='analytic aperture-sum limits for a source steady over one exposure (not a matched-filter statistic)'),
                             detector=dict(bits=opts['bits'], gain=float(clips_by_cam[0][0].gain), full_well=insts[0].full_well_e, read_noise=insts[0].read_noise_e, denoise=opts['denoise']))
        f = fits['cam0']; c0 = fa['candidate_rate_per_box_frame'][0]
        print(f"{name}: m50 {f['m50']:.2f} [{f['m50_ci95'][0]:.2f},{f['m50_ci95'][1]:.2f}] m90 {f['m90']:.2f} (first 40 frames: m50 {fits['cam0_first40_frames']['m50']:.2f}) | "
              f"analytic SNR8 {lim8:.2f} | candidates/box-frame {c0['rate']:.4f} [{c0['ci95_clip_bootstrap'][0]:.4f},{c0['ci95_clip_bootstrap'][1]:.4f}] disp {c0['dispersion_index']}"
              + (f" | dual m50 {fits['dual']['m50']:.2f}, coincident box-frames {fa['dual_coincidence_rate_per_box_frame']['total']}/{fa['dual_coincidence_rate_per_box_frame']['box_frames']}" if len(insts) == 2 else '')
              + f" ({time.time()-tic:.0f}s)", flush=True)
    # NELIOTA consistency check (not a validation): SNR of a steady R = 12.41 source in one 23-ms exposure at phase 0.1
    insts, _ = inst_of('nel'); inst = insts[0]
    bk = D.total_background_sb('Rc', 0.1, 8.0, -20.0)
    snr_1241 = float(D.frame_snr(inst, 12.41, bk)[0])
    results['_neliota_check'] = dict(quoted='Xilouris et al. (2018): SNR 2.5 at R = 12.41 for lunar phase ~0.1 (23 ms, 0.8 arcsec px)', model_snr_at_12_41=snr_1241,
                                     note='the analytic model with the declared background, throughput and aperture; agreement of this one number does not calibrate the background, throughput or false-alarm behaviour across phase, band and site')
    json.dump(results, open(f'{root}/outputs/tables/injection_recovery.json', 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
    import runpy
    runpy.run_path(os.path.join(root, 'scripts', 'make_injection_figure.py'), run_name='__main__')
