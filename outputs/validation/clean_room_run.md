# Clean-room reproducibility run

Date: 2026-10-06. Purpose: show that the complete pipeline regenerates every output, table, text number and the
manuscript from the code, configuration and input data alone, starting from an empty `outputs/` folder.

## Procedure

1. A copy of the package was made in a scratch directory **without** `outputs/`, `paper/main.pdf` and LaTeX auxiliary
   files, and **without** the generated LaTeX (`paper/sections/numbers.tex`, `tab_*.tex`, `B_scenarios.tex`).
   Inputs present: `ayap1obs/`, `scripts/`, `config/`, `data/` (DE421 arrays, Natural Earth, Horizons tables), `paper/` sources, `research/`, `docs/`.
2. Command: `make all NMC=400 NTRIAL=2` (reduced Monte Carlo and injection sample sizes; production values are
   NMC = 6000 and NTRIAL = 10).
3. Environment: Python 3.13.16; numpy 2.5.3, scipy 1.18.1, astropy 8.0.1, jplephem 2.24, healpy 1.20.1, matplotlib 3.11.2,
   pandas 3.0.5, scikit-image 0.26.0, PyYAML 6.0.3; pdfTeX 3.141592653-2.6-1.40.25 and BibTeX 0.99d (TeX Live 2023); 2 CPU cores.
4. The outputs were compared with the production outputs using `scripts/compare_clean_room.py MAIN_ROOT CLEAN_ROOT`.

## Result

- All 18 Makefile steps (`dirs validate screen converge reach stats calendar refine scenarios injection figures tables pdf`,
  the figures target running seven scripts) completed with exit status 0. Start 03:24:02 UTC, manuscript written 03:55:27 UTC
  (31.5 min). The PDF has 51 pages, with no LaTeX errors, no overfull boxes and no undefined references; 50 figure files were produced, as in the production tree.
- **Deterministic products are bit-identical** to the production outputs: screening and reachability arrays, opportunity
  catalogues and statistics, observing calendar, timeline families, daily availability, convergence check, Stage-2
  refinement, facility–site–time matrix, the seeded prior-predictive magnitude sample and the ephemeris-validation report.
- **Monte Carlo products agree within sampling error**: for the 329 probability-valued text macros that differ, the median
  absolute difference is 0.020 and the 95th percentile 0.040; normalised by the binomial standard error of the
  difference between n = 6000 and n = 400 estimates, the median is 0.79 and 1.8 % exceed 3.

| Headline macro | Production (NMC 6000) | Clean room (NMC 400) |
|---|---|---|
| P(≥1 detection), S1, strategies A / B / C | 0.52 / 0.75 / 0.62 | 0.49 / 0.77 / 0.63 |
| P(≥2 independent), S1, A / B / C | 0.22 / 0.51 / 0.41 | 0.22 / 0.48 / 0.41 |
| P(confirmed), S1, B | 0.52 | 0.49 |
| P(live identifiable transient), S1, C | 0.27 | 0.24 |
| P(eyepiece witness), S1 | 0.10 | 0.10 |
| P(≥1), S1, B, upper half of the η prior | 0.92–0.93 | 0.90–0.94 |
| Peak V median (prior predictive, wide prior) | 12.1 | 12.1 |

## Changes during the run (declared)

- At 03:34:30 UTC, while the scenario step was running and **before** the tables step, `scripts/make_tables.py`,
  `paper/sections/06_results.tex`, `paper/sections/09_conclusions.tex` and `README.md` were updated from the main tree (one
  added macro, `\NoppALunMeanPC`, and the sentences using it). After the run, `make_tables.py` and `06_results.tex` were updated
  once more (the generated phrase `\NCgeBNote`, which replaced a construction that read badly when Monte Carlo noise
  changes the B–C ordering) and `make tables pdf` was re-run in the clean-room copy (03:59–04:00 UTC, exit 0, 51 pages, no errors).
- Documentation-only edits made after the comparison (README run-time and clean-room paragraphs, the clean-room sentence in
  Appendix C of the manuscript, a corrected percentage in the engagement protocol, Appendix A and `docs/`, and PDF title/author metadata in `paper/main.tex`) and the comparison tool `scripts/compare_clean_room.py` (not part of the pipeline) were copied
  into the clean-room copy, and `make pdf` was re-run there (last at 04:07 UTC, exit 0, 51 pages, no errors).
- At the end, `diff -rq` between the clean-room copy and the main tree, excluding `outputs/` and the generated LaTeX, reports
  no differences.

## Earlier attempt

The first clean-room attempt (same day) failed at the convergence step with
`OSError: Cannot save file into a non-existent directory` because the scripts assumed that output folders existed. Every
script now creates its output folders, the Makefile has a `dirs` target, `validate_ephemeris.py` runs from the package
root, and the Horizons tables moved from `outputs/validation/` to `data/horizons/` (they are inputs).

## Comparison report (verbatim output of `compare_clean_room.py`)

#### Deterministic tables (expected identical)

| file | rows (main / clean) | result |
|---|---|---|
| opportunity_statistics.csv | 192 / 192 | identical |
| opportunity_probability_vs_duration.csv | 48 / 48 | identical |
| reachability_region_summary.csv | 42 / 42 | identical |
| observing_windows_calendar.csv | 154 / 154 | identical |
| timeline_families.csv | 60 / 60 | identical |
| daily_availability.csv | 578 / 578 | identical |
| convergence.csv | 7 / 7 | identical |
| refined_windows.csv | 11 / 11 | identical |
| facility_site_time_matrix.csv | 38 / 38 | identical |

9 of 9 deterministic tables identical.

#### Screening and reachability arrays

- `outputs/screening/classes.npz`: 11 arrays, all identical
- `outputs/screening/observers.npz`: 5 arrays, all identical
- `outputs/screening/maps.npz`: 12 arrays, all identical
- `outputs/reachability/reachability_maps.npz`: 12 arrays, all identical

- `catalogue_tol0.6_drift0.0.csv`: 56178 rows, identical
- `catalogue_tol2.5_drift0.0.csv`: 50044 rows, identical

- `peak_magnitude_distribution.json` (seeded prior-predictive sample): 10 values, max difference 0

#### Ephemeris validation report

- `ephemeris_validation.md`: identical

#### Text macros (`paper/sections/numbers.tex`)

- 776 macros in the production run, 776 in the clean run; 401 identical, 375 different, 0 present in only one run.
- 329 differing probability-valued macros (Monte Carlo): median |difference| 0.020, 95th percentile 0.040, maximum 0.100 (faWinSingle).
- Normalised by the binomial standard error of the difference (n = 6000 vs 400): median 0.79, fraction above 3: 0.018. (Draws are not independent across macros, and the prior over luminous efficiency is shared, so this is an indicative check.)
- Other differing (non-probability) macros are Monte Carlo or injection quantities: per-scenario peak-magnitude percentiles from the MC sample (e.g. `pkmedOne` 12.2 → 12.0), the ordered station list `stationsOne`, quartile edges, injection–recovery completeness magnitudes and false-alarm rates (NTRIAL 10 → 2), and the generated phrase `CgeBNote` ("equal or higher in S4 and S11" → "lower in every scenario"; the B–C differences in those scenarios are within sampling error). `faWinSingle` (expected single-station false alarms per hour window, 0.4 → 0.3) is a rate, not a probability, although the check counts it among them.

