# Reproducing the results

This guide is for reviewers and anyone who wants to confirm that the archived outputs follow from the code and the
input data. One command re-runs everything and reports PASS or FAIL.

## What you need

* Python 3.12–3.14 (tested with 3.13 on Linux x86-64 and on macOS with Apple silicon) and `make`.
* About 2 GB of free disk space. No LaTeX, no internet connection during the run, no GPU.
* Time: `make check-quick` takes about 1–1.5 hours and `make check` about 2.5–3.5 hours, depending on the computer
  (the longest steps are the orbit-plane opportunities, about an hour, and their convergence check, about an hour).

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
| `make validate` | minutes | The ephemeris and lunar orientation agree with JPL Horizons (Earth–Moon range within 1 m; sub-Earth and sub-solar points within about 10⁻⁵° when computed in Horizons' convention, 0.006° in the geometric convention used by the screening; topocentric Moon positions within 0.001°), the Earth-orientation table is recorded, and the fast light-curve integrals agree with adaptive quadrature (below 10⁻⁴ mag). Afterwards `git status outputs/validation` should show no change. |
| `make test-checker` | about 2 min | The checker passes an unmodified copy of the archived outputs and fails each of eight corruptions (Monte Carlo tables replaced by text, intervals set to [0, 1], paired effects and injection fits set to 999, inverted quantiles, emptied false-alarm arrays, a 999 coincidence rate, an emptied website scenario list). |
| `make check-quick` | about 1.5 h | The whole pipeline at reduced sample sizes (MC_OUTER = 40, MC_INNER = 50, NTRIAL = 20, NSEQ = 500), compared with the archived outputs. |
| `make check` | about 3 h | The whole pipeline at the release sample sizes (MC_OUTER = 200, MC_INNER = 600, NTRIAL = 100, NSEQ = 3000), compared with the archived outputs. |

`make check` and `make check-quick` first verify the input data against `data/DATA_MANIFEST.sha256`, then work in a
scratch copy (`.check/run`) and never modify your checkout. They print one line per test and save the report to
`.check/report.md`; the full pipeline log is `.check/run.log`. The reference is the committed release
(`git archive HEAD`), so the check is valid even if you have changed files. Delete `.check/` afterwards if you need
the space.

Run one check at a time. A second check started in the same folder stops at once with a message (exit status 3),
because it would delete the working copy of the first one. While the pipeline runs, the terminal shows one line per
step and a "still running" line after every 5 quiet minutes; the opportunity step and its convergence check print
little else for about an hour each.

## What is compared and how

| Product | Test | Tolerance |
|---|---|---|
| Required products (tables, arrays, scenario cards, validation reports, injection results, website data, figures) | present in the new run and in the reference | any missing product is a FAIL (`outputs/screening/classes.npz` is not archived in git and is only required in the new run) |
| Structure of both trees | probabilities in [0, 1] and equal to k/N; intervals equal to their definition; ordered epistemic quantiles; paired differences equal to the difference of the pooled values; Monte Carlo tables and nondominance equal to what the cards imply; injection fits (m90 = m50 − w ln 9), rows and false-alarm totals consistent; website records for exactly the expected scenarios | any violation is a FAIL |
| Deterministic tables: opportunity window probabilities and statistics, opportunity and reachability convergence, plume convergence, observing calendar, launch-to-impact families, daily availability, screening convergence, refinement, facility matrix, screening summary, reachability catalogues | every value | within 1e-9 + 1e-6 × value (floating-point rounding); text identical |
| Screening, reachability and terrain arrays | every element | to rounding; boolean arrays may differ in fewer than 1e-5 of the entries |
| Validation results (including the light-curve accuracy and the transfer check), the orbiter seasons, the seeded magnitude sample and the LCROSS/crater checks | every value | to rounding |
| Scenario cards, values that do not depend on random draws (geometry, sites, energy, plume, crater, terrain, population, orbiters) | every value | to rounding |
| Scenario cards, Monte Carlo outcome probabilities | difference in Monte Carlo standard errors (computed from the spread of the outer-draw means) | none above 5, at most 1 % above 3 |
| Scenario cards, epistemic 5–95 % quantiles (beta-binomial fit) and paired strategy differences | every value | quantiles within 0.08; paired differences within 5 combined Monte Carlo standard errors |
| Injection–recovery | every fit (m50, m90, width), every recovery row, the false-alarm products | fits within twice the combined bootstrap half-widths; recovery fractions within 5 binomial standard errors; clip-bootstrap intervals overlap |
| Website data | every file present; scenario probabilities; deterministic site files | equal to the new scenario cards; deterministic files to rounding |
| Figures | pixel comparison | reported for information only |

**Why the Monte Carlo and the injection experiment are tested statistically.** On one computer every output repeats
bit for bit. On another computer random draws can differ: the correlated-weather draw factorises a covariance matrix
with the local linear-algebra library (OpenBLAS on Linux, Accelerate on Apple silicon), and the injection experiment's
noise draws pass through the local floating-point libraries, so the two computers can produce different but
statistically equivalent samples. In the injection experiment every clip, trial and fit bootstrap has its own random
stream, so such a difference stays local instead of changing every later draw.

**Why figures are only reported.** Figures use the Inter typeface shipped in `data/fonts`, so their layout is the
same everywhere, but text rasterisation can still differ by a pixel between font-rendering library versions.

## Results so far

* Release 2.1 was produced with a full run on Linux x86-64 (Python 3.13, the pinned packages). A complete check of
  the committed release (`make check`, release sample sizes) then passed on the same platform on 7 October 2026: every
  product equal to the archive, the Monte Carlo included, and every figure pixel-identical (pipeline 132 minutes).
* A first check on macOS (Apple silicon, Python 3.13; 8 October 2026) of that archive reproduced every deterministic
  product to rounding (largest relative difference 1e-10) and the scenario Monte Carlo exactly, but failed on the
  injection fits of the afocal-phone system: its random realisation differed from the Linux one and exposed occasional
  registration jumps in phone video. The registration and the random streams were corrected and the injection products
  regenerated (see CHANGELOG and docs/REAUDIT_RESPONSE.md); the complete Linux check of the corrected release then
  passed on 8 October 2026, again with every product and figure identical (pipeline 115 minutes). Please rerun
  `make check` on a second platform and report the result.
* Release 2.0.1: a complete cloud check (release sample sizes) passed on 7 October 2026.
* Release 1.0.0/1.0.1 (historical): repeated runs on one computer were bit-identical; a clean-room run regenerated
  every product; on a second platform (macOS on Apple silicon) deterministic products agreed to rounding and the
  Monte Carlo within sampling error ([record](../outputs/validation/cross_platform_run.md)). The release-1 numbers
  are superseded.

## What a passing check looks like

The input data are verified first (the check stops with a message if a data file differs); the comparison then
prints one line per test:

```
[PASS] Required products: … of … present in the new run, … in the reference (1 deliberately unarchived)
[PASS] Product validation (new run): ids, ranges, p = k/N, intervals, quantiles, paired differences, CSV = cards, nondominance, injection identities, website records: 0 problems
[PASS] Product validation (reference): … 0 problems
[PASS] Deterministic tables: 17 of 17 equal to rounding (largest relative difference …)
[PASS] Arrays (screening, reachability, terrain experiment): … equal to rounding (largest relative difference …)
[PASS] Validation results and seeded magnitude sample: … values equal to rounding
[PASS] Scenario cards, non-Monte-Carlo values: … numbers compared, 0 differences
[PASS] Monte Carlo outcome probabilities: … values; largest … standard errors (limit 5); … % beyond 3 (limit 1 %)
[PASS] Monte Carlo outer-draw quantiles: … values within 0.08 of the reference
[PASS] Paired strategy differences: … values within 5 combined standard errors
[PASS] Injection-recovery: fits, recovery rows and false-alarm products of 5 systems consistent within their uncertainties
[PASS] Website data (deterministic files): … values equal to display rounding
[info] Figures (visual check only): … pixel-identical
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
  redone with any tool. The same folder holds the Horizons osculating elements of LRO and Danuri from which
  `scripts/make_orbiter_seasons.py` computes the illumination seasons.
* **Opportunity catalogue.** `make gatecheck` (about 10 minutes) recomputes the station availability of every
  catalogue entry with astropy at its impact time and compares the counts with the catalogue
  (`outputs/validation/catalogue_gate_check.json`).
* **Quotations.** `research/quotations.csv` lists every reused quotation with its source and original wording;
  `make quotes` confirms that each occurs where it is used. The sources themselves must be opened to verify the
  wording (page snapshots are not archived).

## Where the numbers in the paper come from

Every computed number quoted in the manuscript is written by `scripts/make_tables.py` into
`paper/sections/numbers.tex` (the script stops if a required output is missing), and the manuscript tables are
generated the same way, so the text cannot drift from the outputs. The manuscript itself is not public yet; when it
is, `make all` will also rebuild the PDF.

## Release manifest

`make manifest` (the last step of `make all`) writes `MANIFEST.sha256` with the SHA-256 of every released file,
`data/DATA_MANIFEST.sha256` for the input data, and `outputs/validation/release_manifest.json` with the version, git
commit, Python and package versions, the hashes of the external data loaded through packages (GeoNames table, lunar
texture, IERS table) and of the configuration files, the Monte Carlo and injection sizes, and the random seed of every
stochastic product. Check a copy of the release with
`sha256sum -c --ignore-missing MANIFEST.sha256` (Linux) or `shasum -a 256 -c --ignore-missing MANIFEST.sha256`
(macOS); the manifest also lists the manuscript PDF (`paper/main.pdf`), which is not yet part of the public
repository, hence `--ignore-missing`. `outputs/screening/classes.npz` is regenerated, not archived, and is not listed.
