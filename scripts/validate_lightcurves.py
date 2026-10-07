"""Accuracy of the fast light-curve integrals used by the Monte Carlo, the injection-recovery tests and the website
(ayap1obs/impact.py: G_eval, W_eval, peak_band_magnitude_fast), against independent quadrature (re-audit PH-N04).

Reference: band fractions by 160-node Gauss-Legendre quadrature of the Planck function in wavelength; time integrals
of exp(-x) f_b(T(x)) by adaptive quadrature (scipy.integrate.quad, relative tolerance 1e-10); band-peak rates by a
dense search in x followed by bounded scalar optimisation. Cases: random draws over the temperature priors used in
the paper (1000-6900 K, including the cool 1300-2500 K sensitivity range), every band, first exposures of 2.3 ms to
1 s with tau = 0.05-2 s, arbitrary intervals [a, b] in x, and the four cases quoted in the re-audit.
Writes outputs/validation/lightcurve_accuracy.json and .md; exits non-zero if the worst error exceeds 0.005 mag."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from ayap1obs import impact as I
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{root}/outputs/validation', exist_ok=True)
H, C, K, SIG = 6.62607015e-34, 2.99792458e8, 1.380649e-23, 5.670374419e-8
GLX, GLW = np.polynomial.legendre.leggauss(160)

def frac_ref(T, band):
    if band == 'vis':
        l1, l2 = 0.40e-6, 0.90e-6
    else:
        b = I.BANDS[band]; l1, l2 = b['lam'] - b['width'] / 2, b['lam'] + b['width'] / 2
    lam = 0.5 * (l2 - l1) * GLX + 0.5 * (l2 + l1)
    B = 2 * H * C ** 2 / lam ** 5 / np.expm1(H * C / (lam * K * T))
    return 0.5 * (l2 - l1) * np.sum(GLW * B) * np.pi / (SIG * T ** 4)

def G_ref(band, T0, a, b):
    Tf = float(I.floor_temperature(T0))
    g = lambda x: np.exp(-x) * frac_ref(Tf + (T0 - Tf) * np.exp(-x), band)
    return quad(g, a, b, epsrel=1e-10, epsabs=0, limit=400)[0]

def peak_ref(band, T0):
    Tf = float(I.floor_temperature(T0))
    g = lambda x: np.exp(-x) * frac_ref(Tf + (T0 - Tf) * np.exp(-x), band)
    xs = np.linspace(0, 8, 801); v = np.array([g(x) for x in xs]); k = int(np.argmax(v))
    if k == 0:
        return g(0.0)
    r = minimize_scalar(lambda x: -g(x), bounds=(xs[max(k - 1, 0)], xs[min(k + 1, 800)]), method='bounded', options=dict(xatol=1e-9))
    return max(-r.fun, v[k])

dm = lambda fast, ref: float(2.5 * np.log10(fast / ref)) if fast > 0 and ref > 0 else float('nan')
rng = np.random.default_rng(11)
bands = ['V', 'Rc', 'Ic', 'J', 'H', 'Ks', 'broad']
rows = []
# 1. first exposures and arbitrary intervals
for _ in range(220):
    band = bands[rng.integers(len(bands))]
    T0 = float(np.exp(rng.normal(np.log(2995.0), 0.28))) if rng.random() < 0.6 else float(rng.uniform(1000.0, 2600.0))
    T0 = float(np.clip(T0, I.T0_MIN, I.T0_MAX)); tau = float(np.exp(rng.uniform(np.log(0.05), np.log(2.0))))
    if rng.random() < 0.5:
        t_e = float(rng.choice([0.0023, 0.023, 0.033, 0.1, 0.25, 1.0])); a, b = 0.0, t_e / tau; kind = 'first exposure'
    else:
        a = float(rng.uniform(0, 5)); b = a + float(np.exp(rng.uniform(np.log(0.005), np.log(3.0)))); kind = 'interval'
    ref = G_ref(band, T0, a, b)
    if ref < 1e-25:
        continue
    fast = float(I.G_eval(band, np.array([T0]), np.array([[b]]))[0, 0] - I.G_eval(band, np.array([T0]), np.array([[a]]))[0, 0])
    rows.append(dict(kind=kind, band=band, T0=T0, tau=tau, a=a, b=b, dmag=dm(fast, ref)))
# 2. W and band peaks
for T0 in np.concatenate([np.linspace(1000, 6900, 25), [1350.0, 1305.0, 2550.0]]):
    rows.append(dict(kind='W (0.40-0.90 um)', band='vis', T0=float(T0), dmag=dm(float(I.W_eval(np.array([T0]))[0]), G_ref('vis', float(T0), 0.0, 60.0))))
    for band in bands:
        rows.append(dict(kind='band peak', band=band, T0=float(T0), dmag=dm(float(I.peak_rate_eval(band, np.array([T0]))[0]), peak_ref(band, float(T0)))))
# 3. the cases quoted by the re-audit (errors there: 0.076, 0.154, 0.078 and 0.060 mag in release 2.0)
quoted = [('V peak at 1350 K', 'V', 'peak', 1350.0, None), ('V fluence, x 2 -> 2.02 at 1350 K', 'V', 'interval', 1350.0, (2.0, 2.02)),
          ('V first 23 ms, tau 0.5 s, 1350 K', 'V', 'interval', 1350.0, (0.0, 0.046)), ('Ks peak at 1350 K', 'Ks', 'peak', 1350.0, None)]
for name, band, kind, T0, ab in quoted:
    if kind == 'peak':
        d = dm(float(I.peak_rate_eval(band, np.array([T0]))[0]), peak_ref(band, T0))
    else:
        fast = float(I.G_eval(band, np.array([T0]), np.array([[ab[1]]]))[0, 0] - I.G_eval(band, np.array([T0]), np.array([[ab[0]]]))[0, 0])
        d = dm(fast, G_ref(band, T0, *ab))
    rows.append(dict(kind='re-audit case: ' + name, band=band, T0=T0, dmag=d))
worst = {}
for r in rows:
    k = r['kind'].split(':')[0] if r['kind'].startswith('re-audit') else r['kind']
    worst[k] = max(worst.get(k, 0.0), abs(r['dmag']))
ok = max(worst.values()) < 0.005
json.dump(dict(passed=ok, threshold_mag=0.005, worst_abs_dmag=worst, cases=rows), open(f'{root}/outputs/validation/lightcurve_accuracy.json', 'w'), indent=1)
with open(f'{root}/outputs/validation/lightcurve_accuracy.md', 'w') as f:
    f.write('# Accuracy of the fast light-curve integrals\n\nFast temperature-table integrals (ayap1obs/impact.py) against independent adaptive quadrature.\n\n'
            '| quantity | worst error (mag) |\n|---|---|\n')
    for k, v in worst.items():
        f.write(f'| {k} | {v:.2e} |\n')
    f.write('\n| re-audit case | error (mag) |\n|---|---|\n')
    for r in rows:
        if r['kind'].startswith('re-audit'):
            f.write(f"| {r['kind'][len('re-audit case: '):]} | {r['dmag']:+.2e} |\n")
for k, v in worst.items():
    print(f'{k:28s} worst |dmag| = {v:.2e}')
print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
