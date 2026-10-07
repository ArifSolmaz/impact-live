"""Release manifest (audit ST-24/ST-25): records what produced this release.

Writes
  MANIFEST.sha256                         SHA-256 of every released file (code, configuration, data, outputs, website, and
                                          the manuscript PDF when the private paper/ folder is present), sha256sum format
  data/DATA_MANIFEST.sha256               SHA-256 of the input data files (checked by scripts/check_reproduction.py
                                          before it runs anything)
  outputs/validation/release_manifest.json  version, git commit, environment (Python, platform, package versions),
                                          hashes of the external data loaded through packages (GeoNames table, lunar
                                          texture, IERS table, DE421), configuration hashes and Monte Carlo sizes
Run last (`make manifest`, after `make pdf`)."""
import sys, os, json, hashlib, platform, subprocess, glob, re
import importlib.metadata as md
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def files_under(d, skip=()):
    out = []
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if x not in ('__pycache__', '.check', '.git', '.venv')]
        for f in fn:
            p = os.path.relpath(os.path.join(dp, f), root)
            if f.endswith('.pyc') or f == '.DS_Store' or any(p.startswith(s) for s in skip):
                continue
            out.append(p)
    return sorted(out)

# ---- input data
data_files = files_under('data', skip=('data/DATA_MANIFEST.sha256',))
with open('data/DATA_MANIFEST.sha256', 'w') as f:
    for p in data_files:
        f.write(f'{sha(p)}  {p}\n')
# ---- external data used through packages
ext = {}
try:
    import geonamescache
    p = os.path.join(os.path.dirname(geonamescache.__file__), 'data', 'cities15000.json'); ext['geonames_cities15000'] = dict(package=f"geonamescache {md.version('geonamescache')}", sha256=sha(p))
except Exception as e:
    ext['geonames_cities15000'] = dict(error=str(e))
try:
    import skimage
    p = os.path.join(os.path.dirname(skimage.__file__), 'data', 'moon.png'); ext['lunar_texture_skimage_moon'] = dict(package=f"scikit-image {md.version('scikit-image')}", sha256=sha(p))
except Exception as e:
    ext['lunar_texture_skimage_moon'] = dict(error=str(e))
try:
    import astropy_iers_data
    for p in sorted(glob.glob(os.path.join(os.path.dirname(astropy_iers_data.__file__), 'data', 'finals2000A*'))):
        ext[f'iers_{os.path.basename(p)}'] = dict(package=f"astropy-iers-data {md.version('astropy-iers-data')}", sha256=sha(p))
except Exception as e:
    ext['iers'] = dict(error=str(e))
# ---- environment
reqs = [l.split('==')[0].strip() for l in open('requirements.txt') if '==' in l and not l.startswith('#')]
pkgs = {}
for r in reqs:
    try:
        pkgs[r] = md.version(r)
    except md.PackageNotFoundError:
        pkgs[r] = None
pinned = {l.split('==')[0].strip(): l.split('==')[1].strip() for l in open('requirements.txt') if '==' in l and not l.startswith('#')}
mismatch = {k: (pinned[k], v) for k, v in pkgs.items() if v != pinned.get(k)}
try:
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout.strip())
except Exception:
    commit, dirty = None, None
version = None
for l in open('CITATION.cff'):
    m = re.match(r'version:\s*"?([^"\s]+)"?', l)
    if m:
        version = m.group(1)
cards = sorted(glob.glob('outputs/scenarios/S*.json'))
mc = json.load(open(cards[0]))['mc_settings'] if cards else {}
inj = json.load(open('outputs/tables/injection_recovery.json')) if os.path.exists('outputs/tables/injection_recovery.json') else {}
inj_sizes = {k: dict(ntrial=v['ntrial'], n_seq=v['n_seq']) for k, v in inj.items() if not k.startswith('_')}
# random seeds of every stochastic product (re-audit ST-N03), read from the products where they are stored
seeds = dict(monte_carlo_per_scenario={os.path.basename(c)[:-5]: json.load(open(c))['mc_settings'].get('seed') for c in cards},
             monte_carlo_rule='20261005 + 1000 x scenario index (scripts/run_scenarios.py; the same seed for every prior and sensitivity block of a card)',
             injection_recovery=inj.get('_settings', {}).get('seed'), injection_random_streams=inj.get('_settings', {}).get('random_streams'),
             injection_clip_bootstrap=5, injection_clip_textures='second-camera texture normalisation: clip index c (np.random.default_rng(c))',
             synthetic_terrain=7, prior_predictive_sample=1, website_field_factor_sample=2, sensitivity_ladder=1, lightcurve_validation=11)
# ---- released files
released = []
for d in ('ayap1obs', 'scripts', 'config', 'data', 'research', 'docs', 'site', 'outputs'):
    released += files_under(d, skip=('outputs/logs', 'outputs/screening/classes.npz', 'outputs/validation/release_manifest.json', 'research/engagement.md'))
released += [p for p in ('Makefile', 'requirements.txt', 'README.md', 'CHANGELOG.md', 'CITATION.cff', 'LICENSE') if os.path.exists(p)]
if os.path.exists('paper/main.pdf'):
    released.append('paper/main.pdf')
rec = dict(release=version, release_tag=f'v{version}' if version else None, git_commit=commit, working_tree_dirty=dirty,
           git_note=(None if commit else 'git commit not recorded (manifest written outside the release repository); the release is identified by its tag'),
           python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine(),
           packages=pkgs, packages_differing_from_requirements=mismatch, external_data=ext,
           config_sha256={p: sha(p) for p in sorted(glob.glob('config/*.yaml'))},
           monte_carlo=mc, injection=inj_sizes, random_seeds=seeds, n_released_files=len(released) + 1,
           note='MANIFEST.sha256 lists every released file; data/DATA_MANIFEST.sha256 the input data; regenerate with `make manifest` after `make pdf`.')
os.makedirs('outputs/validation', exist_ok=True)
json.dump(rec, open('outputs/validation/release_manifest.json', 'w'), indent=1)
released.append('outputs/validation/release_manifest.json')
with open('MANIFEST.sha256', 'w') as f:
    for p in sorted(set(released)):
        f.write(f'{sha(p)}  {p}\n')
print(f"release {version}: {len(set(released))} files in MANIFEST.sha256, {len(data_files)} data files; packages differing from requirements: {mismatch or 'none'}")
