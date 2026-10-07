"""Injection-recovery and false-alarm experiment on synthetic lunar video (SIMULATION, release 2).

Scene and atmosphere: an unblurred lunar radiance scene (the scikit-image 'moon' photograph used as an albedo texture
at 1.5 arcsec per texture pixel, scaled to the modelled Earthshine surface brightness at illuminated fraction 0.35, plus
the scattered-light gradient of the sunlit crescent 6' beyond one edge of the field) is convolved IN EVERY FRAME with
that frame's seeing PSF (Gaussian, FWHM varying as a log-normal AR(1) process, 10 % rms, frame-to-frame correlation 0.9)
and shifted by that frame's image motion (AR(1) wander plus white jitter), with 1 % transparency flicker. The injected
flash is a point source convolved with the same PSF and shifted with the same motion; its counts in each exposure are the
cooling-blackbody light curve integrated over the actual exposure interval (random phase), T0 from the broad prior,
tau log-uniform 0.1-1 s.
Detector: Poisson photon noise, Gaussian read noise, charge clipped at the full well, ADC with the stated gain, bias and
bit depth (8-bit video cameras: gain set so that the Earthshine background sits at a fixed code value); phones apply an
in-camera temporal recursive denoising filter.
Pipeline (causal, strictly past frames): sub-pixel cross-correlation registration to the rolling reference, median
normalisation, rolling reference = median of the previous 25 registered frames, difference image, Gaussian matched
filter at the nominal seeing, noise from the median absolute deviation of the filtered difference, candidates = local
maxima >= 5 sigma. NELIOTA-like: two synchronised cameras (Rc and Ic) behind one telescope share the seeing, motion and
transparency, with independent noise; a validated detection needs a candidate in BOTH cameras in the same frame within
2 pixels (the published NELIOTA criterion is detection in both cameras on the same lunar area and frame).
Outputs per system: recovery fraction per injected peak magnitude with Wilson 95 % intervals (NTRIAL trials per bin), a
monotone logistic fit with bootstrap intervals on m50 and m90, and false alarms counted in long blank sequences (all
candidates in the field, and dual-camera coincidences) with exact Poisson 95 % limits.
Approximations: injection trials reuse one pre-rendered background sequence per system (trials differ in time, position,
phase and flash parameters; their background noise is not fully independent); registration shifts are computed on the
background sequence. Not modelled: rolling shutter, compression artefacts, cosmic rays, clouds, real camera firmware.
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
TEX = data.moon().astype(float); TEX /= TEX.mean()
TEX_SCALE = 1.5          # arcsec per texture pixel (declared)
ILLUM = 0.35
K_REF = 25
THRESH = 5.0
MATCH_PX = 2
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

class Sequence:
    """Pre-rendered background sequence for one camera of a system (shared atmosphere for twin cameras)."""
    def __init__(self, inst, opts, scene, atm, rng, n_seq):
        n = opts['n']; self.inst, self.opts, self.n = inst, opts, n
        self.gain = opts['gain'] if opts['gain'] else float(np.median(scene)) / opts['auto_code']
        F = np.fft.fft2(scene)
        self.raw = np.empty((n_seq, n, n), np.float32)            # electrons after photon and read noise (before clip/ADC)
        for k in range(n_seq):
            img = render_clean(F, n, atm['sig'][k], atm['dx'][k], atm['dy'][k]) * atm['tr'][k]
            self.raw[k] = rng.poisson(np.clip(img, 0, None)) + rng.normal(0, inst.read_noise_e, (n, n))
        self.proc = np.empty_like(self.raw)
        for k in range(n_seq):
            self.proc[k] = adc(self.raw[k], inst, opts, self.gain)
        if opts['denoise']:
            self.proc = denoise(self.proc)
        self.shift, self.reg = register_sequence(self.proc)
        self.scale = np.median(self.proc.reshape(n_seq, -1), axis=1)

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

def xcorr_shift(ref, img):
    """Shift (dy, dx) that registers img onto ref: cross-correlation peak with parabolic sub-pixel refinement."""
    n = ref.shape[0]
    cc = np.real(np.fft.ifft2(np.fft.fft2(ref - ref.mean()) * np.conj(np.fft.fft2(img - img.mean()))))
    iy, ix = np.unravel_index(np.argmax(cc), cc.shape)
    def para(cm, c0, cp):
        d = cm - 2 * c0 + cp
        return 0.0 if d >= 0 else 0.5 * (cm - cp) / d
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

def snr_map(cur_reg, ref, sig0, scale_cur, scale_ref, margin):
    d = cur_reg * (scale_ref / max(scale_cur, 1e-9)) - ref
    mf = gaussian_filter(d, sig0)
    c = mf[margin:-margin, margin:-margin]
    noise = 1.4826 * np.median(np.abs(c - np.median(c))) + 1e-12
    return mf / noise

def candidates(s, margin, thresh=THRESH):
    loc = (s == maximum_filter(s, size=3)) & (s >= thresh)
    loc[:margin, :] = False; loc[-margin:, :] = False; loc[:, :margin] = False; loc[:, -margin:] = False
    return np.argwhere(loc)

def blank_false_alarms(seqs, margin):
    """All candidates in each analysed frame of the blank sequences; dual coincidences for twin cameras."""
    n_seq = seqs[0].proc.shape[0]
    per_cam = [[] for _ in seqs]
    for ci, seq in enumerate(seqs):
        reg = seq.reg
        for k in range(K_REF, n_seq):
            ref = np.median(reg[k - K_REF:k], axis=0)
            s = snr_map(reg[k], ref, seq_sig0(seq), seq.scale[k], np.median(ref), margin)
            per_cam[ci].append(candidates(s, margin))
    n_frames = n_seq - K_REF
    out = dict(n_frames=int(n_frames), candidates_per_camera=[int(sum(len(c) for c in pc)) for pc in per_cam],
               frames_with_candidate_per_camera=[int(sum(len(c) > 0 for c in pc)) for pc in per_cam])
    if len(seqs) == 2:
        coinc = 0
        for a, b in zip(per_cam[0], per_cam[1]):
            if len(a) and len(b):
                dd = np.hypot(a[:, None, 0] - b[None, :, 0], a[:, None, 1] - b[None, :, 1])
                coinc += int((dd <= MATCH_PX).any())
        out['dual_coincident_frames'] = coinc
    return out

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
    magnitude is m_peak_band; uses the exact light-curve tables."""
    xs = np.clip(I.xpeak_eval(inst.band, np.array([T0]))[0] * np.linspace(0.6, 1.4, 9) + np.linspace(0, 1e-3, 9), 0, I.X_GRID[-1])
    rate = (I.G_eval(inst.band, np.full(9, T0), (xs + 1e-4)[:, None])[:, 0] - I.G_eval(inst.band, np.full(9, T0), xs[:, None])[:, 0]) / 1e-4
    pk = rate.max()
    b = I.BANDS[inst.band]
    e_norm = 10 ** (-0.4 * m_peak_band) * b['f0'] * b['width'] * tau / pk       # E_bol / (4 pi d^2), J m^-2
    s0 = phase - inst.frame_time_s + inst.frame_time_s * np.arange(n_frames)
    a = np.maximum(s0, 0.0); bb = np.maximum(s0 + inst.exposure_s, 0.0)
    dG = I.G_eval(inst.band, np.full(n_frames, T0), (bb / tau)[:, None])[:, 0] - I.G_eval(inst.band, np.full(n_frames, T0), (a / tau)[:, None])[:, 0]
    return D.photons_from_energy(e_norm * np.clip(dG, 0, None), inst.band, inst.area, inst.throughput)

def trial(seqs, insts, opts, atm, m_peak, rng, margin=12, win=40):
    """One injection: returns (detected per camera, validated dual)."""
    n = opts['n']; n_seq = seqs[0].proc.shape[0]
    T0 = float(I.temperature_prior(rng, 1, 'broad')[0]); tau = float(np.exp(rng.uniform(np.log(0.1), np.log(1.0))))
    Tf = insts[0].frame_time_s; L = int(min(40, np.ceil(4 * tau / Tf) + 2)); ph = rng.uniform(0, Tf)
    k0 = int(rng.integers(K_REF + 5, n_seq - L - 2))
    y, x = rng.uniform(margin, n - margin, 2)
    # counts per camera (the twin camera sees the same flash in its own band; the injected magnitude is the band peak of camera 0)
    cnt0 = flash_counts(insts[0], m_peak, T0, tau, ph, L)
    counts = [cnt0]
    for inst in insts[1:]:
        # same physical flash: scale by the ratio of band energies at equal E_bol
        c1 = flash_counts(inst, m_peak, T0, tau, ph, L)            # band peak set to m_peak in this camera's band ...
        counts.append(c1 * band_peak_ratio(insts[0].band, inst.band, T0))   # ... then the blackbody colour restores one E_bol
    hits = []
    half = win // 2
    yc, xc = int(round(y)), int(round(x))
    found_frames = []
    for ci, (seq, inst) in enumerate(zip(seqs, insts)):
        frames = {}
        for j in range(L):
            k = k0 + j
            st = stamp(n, y + atm['dy'][k], x + atm['dx'][k], atm['sig'][k]) * counts[ci][j] * atm['tr'][k]
            raw = seq.raw[k] + rng.poisson(np.clip(st, 0, None))
            frames[k] = adc(raw, inst, opts, seq.gain)
        if opts['denoise']:                                        # in-camera recursive filter continues from k0-1
            prev = seq.proc[k0 - 1]
            for j in range(L + 3):
                k = k0 + j
                inp = frames[k] if k in frames else adc(seq.raw[k], inst, opts, seq.gain)
                prev = 0.5 * prev + 0.5 * inp; frames[k] = prev
        fr_hit = []
        # the registered frames keep the image position of the start of the sequence, so the flash is searched where the
        # registration actually puts it: (raw position + image motion of frame k + registration shift of frame k)
        ry0 = y + atm['dy'][k0] + seq.shift[k0, 0]; rx0 = x + atm['dx'][k0] + seq.shift[k0, 1]
        yc, xc = int(np.clip(round(ry0), 0, n - 1)), int(np.clip(round(rx0), 0, n - 1))
        y_lo, y_hi = max(yc - half, 0), min(yc + half, n); x_lo, x_hi = max(xc - half, 0), min(xc + half, n)
        reg_mod = {k: fshift(frames[k], *seq.shift[k])[y_lo:y_hi, x_lo:x_hi] for k in frames}
        for k in sorted(frames):
            if k - k0 >= L + 1:
                break
            past = np.array([reg_mod[kk] if kk in reg_mod else seq.reg[kk, y_lo:y_hi, x_lo:x_hi] for kk in range(k - K_REF, k)])
            ref = np.median(past, axis=0)
            s = snr_map(reg_mod[k], ref, seq_sig0(seq), seq.scale[k], np.median(seq.scale[k - K_REF:k]), 4)
            py = int(round(y + atm['dy'][k] + seq.shift[k, 0])) - y_lo; px = int(round(x + atm['dx'][k] + seq.shift[k, 1])) - x_lo
            sub = s[max(py - MATCH_PX, 0):max(py + MATCH_PX + 1, 0), max(px - MATCH_PX, 0):max(px + MATCH_PX + 1, 0)]
            fr_hit.append(bool(sub.size and sub.max() >= THRESH))
        found_frames.append(np.array(fr_hit + [False] * (L + 1 - len(fr_hit)))[:L + 1])
    det = [bool(f.any()) for f in found_frames]
    dual = bool(len(found_frames) == 2 and (found_frames[0] & found_frames[1]).any())
    return det, dual

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
    rng = np.random.default_rng(SEED)
    results = {}
    for name in SYSTEMS:
        tic = time.time()
        insts, opts = inst_of(name)
        n = opts['n']; margin = 12 if n > 60 else 6
        scene0 = scene_e(insts[0], n, rng)
        atm = atmosphere(rng, N_SEQ, insts[0], opts)
        seqs = []
        for inst in insts:
            sc = scene0 * (scene_e(inst, n, np.random.default_rng(0)).mean() / scene0.mean()) if inst is not insts[0] else scene0
            seqs.append(Sequence(inst, opts, sc, atm, rng, N_SEQ))
        bkg_sb = D.total_background_sb(insts[0].band, ILLUM, 8.0, -20.0)
        lim8 = float(D.limiting_magnitude(insts[0], bkg_sb, 8.0)); lim5 = float(D.limiting_magnitude(insts[0], bkg_sb, 5.0))
        mags = np.round(np.arange(lim8 - 2.5, lim8 + 2.01, 0.25), 2)
        rows = []; all_m = []; all_det = []; all_dual = []
        for m in mags:
            det_c = []; dual_c = []
            for _ in range(NTRIAL):
                d, du = trial(seqs, insts, opts, atm, float(m), rng, margin=margin, win=min(40, n - 2))
                det_c.append(d); dual_c.append(du)
            det_c = np.array(det_c); k0 = int(det_c[:, 0].sum())
            row = dict(mag=float(m), n=NTRIAL, k_cam0=k0, frac_cam0=k0 / NTRIAL, wilson_cam0=wilson(k0, NTRIAL))
            if len(insts) == 2:
                k1 = int(det_c[:, 1].sum()); kd = int(np.sum(dual_c))
                row.update(k_cam1=k1, frac_cam1=k1 / NTRIAL, wilson_cam1=wilson(k1, NTRIAL), k_dual=kd, frac_dual=kd / NTRIAL, wilson_dual=wilson(kd, NTRIAL))
            rows.append(row)
            all_m += [m] * NTRIAL; all_det += list(det_c[:, 0]); all_dual += list(dual_c)
        all_m = np.array(all_m); all_det = np.array(all_det, float); all_dual = np.array(all_dual, float)
        def summary(detv):
            m50, w = fit_logistic(all_m, detv)
            boots = []
            for _ in range(N_BOOT):
                idx = np.concatenate([rng.choice(np.where(all_m == u)[0], NTRIAL) for u in mags])
                boots.append(fit_logistic(all_m[idx], detv[idx]))
            b = np.array(boots); m90 = m50 - w * np.log(9); b90 = b[:, 0] - b[:, 1] * np.log(9)
            return dict(m50=m50, width=w, m50_ci95=[float(np.percentile(b[:, 0], 2.5)), float(np.percentile(b[:, 0], 97.5))],
                        m90=float(m90), m90_ci95=[float(np.percentile(b90, 2.5)), float(np.percentile(b90, 97.5))])
        fits = dict(cam0=summary(all_det))
        if len(insts) == 2:
            fits['dual'] = summary(all_dual)
        fa = blank_false_alarms(seqs, margin)
        area_arcmin2 = ((n - 2 * margin) * insts[0].pixel_scale_arcsec / 60.0) ** 2
        fa['analysed_area_arcmin2'] = area_arcmin2
        fa['candidate_rate_per_frame'] = [dict(rate=c / fa['n_frames'], ci95=poisson_ci(c, fa['n_frames'])) for c in fa['candidates_per_camera']]
        if 'dual_coincident_frames' in fa:
            fa['dual_coincidence_rate_per_frame'] = dict(rate=fa['dual_coincident_frames'] / fa['n_frames'], ci95=poisson_ci(fa['dual_coincident_frames'], fa['n_frames']))
        results[name] = dict(label=opts['label'], bands=[i.band for i in insts], ntrial=NTRIAL, n_seq=N_SEQ, rows=rows, fits=fits, false_alarms=fa,
                             analytic_limits=dict(steady_snr8=lim8, steady_snr5=lim5, background_sb=float(bkg_sb),
                                                  note='analytic aperture-sum limits for a source steady over one exposure (not a matched-filter statistic)'),
                             detector=dict(bits=opts['bits'], gain=float(seqs[0].gain), full_well=insts[0].full_well_e, read_noise=insts[0].read_noise_e, denoise=opts['denoise']))
        f = fits['cam0']
        print(f"{name}: m50 {f['m50']:.2f} [{f['m50_ci95'][0]:.2f},{f['m50_ci95'][1]:.2f}] m90 {f['m90']:.2f} | analytic SNR8 {lim8:.2f} | "
              f"candidates/frame {fa['candidate_rate_per_frame'][0]['rate']:.3f}" + (f" | dual m50 {fits['dual']['m50']:.2f}, coincident frames {fa['dual_coincident_frames']}/{fa['n_frames']}" if len(insts) == 2 else '')
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
