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
| `make validate` | minutes | The ephemeris and lunar orientation agree with JPL Horizons (Earth–Moon range within 4 m, lunar sub-Earth and sub-solar points within 0.006°, topocentric Moon positions within 0.002°). Afterwards `git status outputs/validation` should show no change. |
| `make check-quick` | 30–70 min | The whole pipeline at reduced Monte Carlo sample sizes (NMC = 400, NTRIAL = 2), compared with the archived outputs. |
| `make check` | 1–2 h | The whole pipeline at the production sample sizes (NMC = 6000, NTRIAL = 10), compared with the archived outputs. |

`make check` and `make check-quick` work in a scratch copy (`.check/run`) and never modify your checkout. They
print one line per test and save the report to `.check/report.md`; the full pipeline log is `.check/run.log`.
The reference is the committed release (`git archive HEAD`), so the check is valid even if you have changed files.
Delete `.check/` afterwards if you need the space.

## What is compared and how

| Product | Test | Tolerance |
|---|---|---|
| Deterministic tables: opportunity statistics, observing calendar, launch-to-impact families, daily availability, convergence, refinement, facility matrix, screening summary, reachability catalogues | every value | within 1e-9 + 1e-6 × value (floating-point rounding); text identical |
| Screening and reachability arrays | every element | the same |
| Scenario cards, values that do not depend on random draws (geometry, sites, energy, plume, crater, terrain, population, orbiters) | every value | the same |
| Scenario cards, Monte Carlo probabilities (4 774 values) | difference in binomial standard errors | none above 5, at most 1 % above 3 |
| Ephemeris validation report | whole text | identical |
| Seeded magnitude sample, injection-recovery curves, website data, figures, numbers in the manuscript (when the private `paper/` folder is present) | | reported for information |

**Why the Monte Carlo is tested statistically.** On one computer every output repeats bit for bit, Monte Carlo
included. On another computer the random draws can differ: the correlated-weather draw factorises a covariance
matrix with the local linear-algebra library (OpenBLAS on Linux, Accelerate on Apple silicon), and equally valid
factorisations turn the same random numbers into different but statistically equivalent samples. With reduced
sample sizes (`check-quick`) the standard errors are computed for 6000 archived draws against 400 new ones.

**Why figures are only reported.** Figures use the Inter typeface shipped in `data/fonts`, so their layout is the
same everywhere, but text rasterisation can still differ by a pixel between font-rendering library versions.

## Results so far

* Same computer, repeated runs: bit-identical outputs.
* Clean room (empty `outputs/` folder, reduced sample sizes): every product regenerated; deterministic products
  bit-identical, Monte Carlo within sampling error ([record](../outputs/validation/clean_room_run.md)).
* Second platform (macOS on Apple silicon vs Linux on x86-64, release 1.0.0): deterministic products agreed to
  rounding (largest difference 7 × 10⁻¹⁰ of the value) except a tie between two equally good observing evenings,
  now broken by date; Monte Carlo probabilities 76 % identical, largest difference 0.026, at most 2.5 standard errors;
  677 of the paper's 776 generated numbers identical and the rest within 0.01
  ([record](../outputs/validation/cross_platform_run.md)).

## What a passing check looks like

Output of `make check-quick` on a two-core Linux machine (abridged):

```
Reproduction check: re-running the pipeline in .check/run with NMC=400, NTRIAL=2
Python 3.13.16 (/usr/bin/python3); numpy 2.5.3; reference: committed release (git …)
Full log: .check/run.log
  00:46:31  python scripts/validate_ephemeris.py
  00:46:33  python scripts/run_screening.py
  …
  01:00:15  NMC=400 python scripts/run_scenarios.py
  01:31:29  NTRIAL=2 python scripts/run_injection_recovery.py
  …
Pipeline finished in 68 min. Comparing with the archived outputs:

[PASS] Deterministic tables: 12 of 12 equal to rounding (largest relative difference 0.0e+00)
[PASS] Arrays (screening, reachability): 29 of 29 equal to rounding (largest relative difference 0.0e+00)
[PASS] Scenario cards, deterministic values: 7129 of 7129 equal to rounding (largest relative difference 0.0e+00); 0 text differences
[PASS] Monte Carlo probabilities (NMC 6000 vs 400): 4774 values, 62 % identical; largest difference 0.169; largest 3.5 standard errors (limit 5); 0.08 % beyond 3 (limit 1 %)
[info] Other Monte Carlo summaries in the scenario cards (medians, means, quantiles): 671 values, largest relative difference 0.233
[PASS] Ephemeris validation against JPL Horizons: report identical
…
[PASS] RESULT: the run reproduces the archived outputs
```

On another type of computer the deterministic lines show small non-zero differences (around 1e-14 to 1e-9 of the
values), and with `make check` the Monte Carlo line compares 6000 draws with 6000.

## Independent spot checks

These need no code from this repository.

* **Impact energy.** Scenario S1 assumes 2000 kg at 1.68 km/s: E = ½ m v² = 2.82 × 10⁹ J, about 0.67 t of TNT
  (`outputs/scenarios/S1.json`, `energy`).
* **Moon position.** At the S1 epoch, 2028-04-01 18:00 UTC, the model gives the Moon 52.5° high at azimuth 265.1°
  as seen from TÜBİTAK National Observatory (TUG; 36.8242° N, 30.3356° E, 2500 m), 38.7 % illuminated, and the
  sub-Earth point at lunar longitude −6.34°, latitude −3.30° (`moon` and `sites.TUG` in the same file). Any
  planetarium program, or JPL Horizons (https://ssd.jpl.nasa.gov/horizons/), should agree to a few hundredths of a
  degree (Horizons applies refraction unless set to airless).
* **Validation tables.** The JPL Horizons tables used for validation are stored verbatim in `data/horizons/`, so the
  comparison in `outputs/validation/ephemeris_validation.md` can be redone with any tool.

## Where the numbers in the paper come from

Every computed number quoted in the manuscript is written by `scripts/make_tables.py` into
`paper/sections/numbers.tex`, and the manuscript tables are generated the same way, so the text cannot drift from
the outputs. The manuscript itself is not public yet; when it is, `make all` will also rebuild the PDF and
`make check` will compare its numbers.
