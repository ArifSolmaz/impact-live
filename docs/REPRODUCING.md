# Reproducing the results

This guide is for reviewers and anyone who wants to confirm that the archived outputs follow from the code and the
input data. One command re-runs everything and reports PASS or FAIL.

## What you need

* Python 3.12–3.14 (tested with 3.13 on Linux x86-64 and on macOS with Apple silicon) and `make`.
* About 2 GB of free disk space. No LaTeX, no internet connection during the run, no GPU.
* Time: `make check-quick` takes about 30–70 minutes and `make check` about 1–2 hours, depending on the computer
  (most of it is the eleven scenario cards and, at full precision, the injection-recovery tests).

## Setup

```bash
git clone https://github.com/ArifSolmaz/impact-live
cd impact-live
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

If `pip` or a suitable Python is missing (common on macOS), [uv](https://docs.astral.sh/uv/) gives a clean environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv venv --python 3.13 .venv && source .venv/bin/activate
~/.local/bin/uv pip install -r requirements.txt
```

## Three levels of checking

| Command | Time | What it shows |
|---|---|---|
| `make validate` | minutes | The ephemeris and lunar orientation agree with JPL Horizons (Earth–Moon range within 1 m; sub-Earth and sub-solar points within about 10⁻⁵° when computed in Horizons' convention, 0.006° in the geometric convention used by the screening; topocentric Moon positions within 0.001°), the Earth-orientation table is recorded, and the LOLA reader passes its synthetic-product test. Afterwards `git status outputs/validation` should show no change. |
| `make check-quick` | about 1 h | The whole pipeline at reduced sample sizes (MC_OUTER = 40, MC_INNER = 50, NTRIAL = 20, NSEQ = 500), compared with the archived outputs. |
| `make check` | about 2 h | The whole pipeline at the release sample sizes (MC_OUTER = 200, MC_INNER = 150, NTRIAL = 100, NSEQ = 3000), compared with the archived outputs. |

`make check` and `make check-quick` first verify the input data against `data/DATA_MANIFEST.sha256`, then work in a
scratch copy (`.check/run`) and never modify your checkout. They print one line per test and save the report to
`.check/report.md`; the full pipeline log is `.check/run.log`. The reference is the committed release
(`git archive HEAD`), so the check is valid even if you have changed files. Delete `.check/` afterwards if you need
the space.

## What is compared and how

| Product | Test | Tolerance |
|---|---|---|
| Required products (tables, arrays, scenario cards, validation reports, injection results, website data, figures) | present in the new run and in the reference | any missing product is a FAIL (`outputs/screening/classes.npz` is not archived in git and is only required in the new run) |
| Deterministic tables: opportunity window probabilities and statistics, opportunity and reachability convergence, observing calendar, launch-to-impact families, daily availability, screening convergence, refinement, facility matrix, screening summary, reachability catalogues | every value | within 1e-9 + 1e-6 × value (floating-point rounding); text identical |
| Screening, reachability and terrain arrays | every element | to rounding; boolean arrays may differ in fewer than 1e-5 of the entries |
| Validation results, the seeded magnitude sample and the LCROSS/crater checks | every value | to rounding |
| Scenario cards, values that do not depend on random draws (geometry, sites, energy, plume, crater, terrain, population, orbiters) | every value | to rounding |
| Scenario cards, Monte Carlo outcome probabilities | difference in Monte Carlo standard errors (computed from the spread of the outer-draw means) | none above 5, at most 1 % above 3 |
| Injection–recovery | m50 of each system; false-alarm rates | m50 within twice the combined bootstrap half-widths; Poisson intervals overlap |
| Website data | every file present; scenario probabilities | equal to the new scenario cards |
| Figures | pixel comparison | reported for information only |

**Why the Monte Carlo is tested statistically.** On one computer every output repeats bit for bit, Monte Carlo
included. On another computer the random draws can differ: the correlated-weather draw factorises a covariance
matrix with the local linear-algebra library (OpenBLAS on Linux, Accelerate on Apple silicon), and equally valid
factorisations turn the same random numbers into different but statistically equivalent samples.

**Why figures are only reported.** Figures use the Inter typeface shipped in `data/fonts`, so their layout is the
same everywhere, but text rasterisation can still differ by a pixel between font-rendering library versions.

## Results so far

* Release 2.0 was produced with a full run on Linux x86-64 (Python 3.13, the pinned packages). It has not yet been
  rerun on a second platform; please run `make check` and report the result.
* Release 1.0.0/1.0.1 (historical): repeated runs on one computer were bit-identical; a clean-room run regenerated
  every product; on a second platform (macOS on Apple silicon) deterministic products agreed to rounding and the
  Monte Carlo within sampling error ([record](../outputs/validation/cross_platform_run.md)). The release-1 numbers
  are superseded by release 2.0.

## What a passing check looks like

```
[PASS] Input data: N files match data/DATA_MANIFEST.sha256
[PASS] Required products: … of … present in the new run, … in the reference (1 deliberately unarchived)
[PASS] Deterministic tables: 16 of 16 equal to rounding
[PASS] Arrays (screening, reachability, terrain experiment): … equal to rounding
[PASS] Validation results and seeded magnitude sample: … values equal to rounding
[PASS] Scenario cards, non-Monte-Carlo values: … numbers compared, 0 differences
[PASS] Monte Carlo outcome probabilities: … values; largest … standard errors (limit 5); … % beyond 3 (limit 1 %)
[PASS] Injection-recovery: m50 and false-alarm rates of 5 systems consistent within their uncertainties
[PASS] Website data: …
[PASS] RESULT: the run reproduces the archived outputs
```

On another type of computer the deterministic lines show small non-zero differences (around 1e-14 to 1e-9 of the
values).

## Independent spot checks

These need no code from this repository.

* **Impact energy.** Scenario S1 assumes 2000 kg at 1.68 km/s: E = ½ m v² = 2.82 × 10⁹ J, about 0.67 t of TNT
  (`outputs/scenarios/S1.json`, `energy`).
* **Moon position.** At the S1 impact time, 2028-04-01 18:00 UTC (photons reach TUG 1.245 s later), the model gives
  the Moon 52.5° high at azimuth 265.1° as seen from TÜBİTAK National Observatory (TUG; 36.8242° N, 30.3356° E,
  2500 m), 38.7 % illuminated, and the sub-Earth point at lunar longitude −6.34°, latitude −3.30° (`moon` and
  `sites.TUG` in the same file). Any
  planetarium program, or JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), should agree to a few hundredths of a
  degree (Horizons applies refraction unless set to airless).
* **Validation tables.** The processed JPL Horizons tables used for validation are stored in `data/horizons/` (the
  raw API responses were not archived), so the comparison in `outputs/validation/ephemeris_validation.md` can be
  redone with any tool.

## Where the numbers in the paper come from

Every computed number quoted in the manuscript is written by `scripts/make_tables.py` into
`paper/sections/numbers.tex` (the script stops if a required output is missing), and the manuscript tables are
generated the same way, so the text cannot drift from the outputs. The manuscript itself is not public yet; when it
is, `make all` will also rebuild the PDF.

## Release manifest

`make manifest` (the last step of `make all`) writes `MANIFEST.sha256` with the SHA-256 of every released file,
`data/DATA_MANIFEST.sha256` for the input data, and `outputs/validation/release_manifest.json` with the version, git
commit, Python and package versions, the hashes of the external data loaded through packages (GeoNames table, lunar
texture, IERS table) and of the configuration files, and the Monte Carlo sizes. Check a copy of the release with
`sha256sum -c --ignore-missing MANIFEST.sha256` (Linux) or `shasum -a 256 -c --ignore-missing MANIFEST.sha256`
(macOS); the manifest also lists the manuscript PDF (`paper/main.pdf`), which is not yet part of the public
repository, hence `--ignore-missing`. `outputs/screening/classes.npz` is regenerated, not archived, and is not listed.
