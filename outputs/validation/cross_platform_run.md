# Cross-platform reproduction run

Date: 2026-10-06/07. Purpose: test whether the pipeline gives the same results on a different operating system
and processor architecture, with no involvement of the production environment.

## Platforms

| | Production run (archived outputs) | Independent run |
|---|---|---|
| System | Linux, x86-64 | macOS, Apple silicon (arm64) |
| Python | 3.13.16 | 3.13 (CPython managed by uv) |
| Linear algebra used by numpy | OpenBLAS (bundled with numpy) | Apple Accelerate |
| Packages | as pinned in `requirements.txt` | the same versions (numpy 2.5.3, scipy 1.18.1, astropy 8.0.1, pyerfa 2.0.1.5, jplephem 2.24, healpy 1.20.1, matplotlib 3.11.2, pandas 3.0.5, scikit-image 0.26.0, pillow 12.3.0, PyYAML 6.0.3, pyshp 3.1.6, geonamescache 3.0.2, astropy-iers-data 0.2026.10.5.1.0.7) |

## Procedure

Release 1.0.0 was run on the independent platform with `make all` at the production sample sizes
(NMC = 6000, NTRIAL = 10). Its outputs were compared with the archived outputs using
`python3 scripts/check_reproduction.py --compare ARCHIVED_TREE INDEPENDENT_TREE`; the manuscript's generated numbers
(`paper/sections/numbers.tex`) were compared separately.

## Result (release 1.0.0)

Verbatim output of the comparison tool:

```
[FAIL] Deterministic tables: 11 of 12 equal to rounding (largest relative difference 3.2e-16)
       outputs/tables/timeline_families.csv: best_window: 2 text cells, e.g. "2029-01-22 18:59 UTC" vs "2029-01-21 18:59 UTC"
[PASS] Arrays (screening, reachability): 29 of 29 equal to rounding (largest relative difference 1.5e-14)
[PASS] Scenario cards, deterministic values: 7129 of 7129 equal to rounding (largest relative difference 7.0e-10); 0 text differences
[PASS] Monte Carlo probabilities (NMC 6000 vs 6000): 4774 values, 76 % identical; largest difference 0.026; largest 2.5 standard errors (limit 5); 0.00 % beyond 3 (limit 1 %)
[info] Other Monte Carlo summaries in the scenario cards (medians, means, quantiles): 671 values, largest relative difference 0.0338
[PASS] Ephemeris validation against JPL Horizons: report identical

[info] Seeded flash-magnitude sample: 5 of 10 values identical, largest difference 5.33e-15
[info] Injection-recovery curves: 172 of 172 values identical, largest difference 0
[info] Figures: 0 of 25 pixel-identical
```

Numbers quoted in the manuscript: 677 of 776 identical; the other 99 differ by one unit in the last printed digit
(0.01), as expected from Monte Carlo noise at the rounding boundary. In the abstract one range changed
(0.92–0.93 became 0.92–0.94).

## Findings and changes made in release 1.0.1

1. **Tie in the launch-to-impact table.** For two launch cases (L1 and L5, nominal phases) two observing evenings
   were equally good (same number of available sites). The unstable sort used to pick the best one ordered the tie
   differently on the two platforms (21 or 22 January 2029). `scripts/make_timeline.py` now breaks ties by the
   earlier date with a stable sort; both entries are 2029-01-21 on every platform.
2. **Figure typeface.** The production environment's matplotlib used the Inter typeface by default; a standard
   matplotlib installation uses DejaVu Sans, so the independent run's figures had different text widths and the
   scenario coverage maps had colliding titles. The figures now use Inter files shipped in `data/fonts`
   (SIL Open Font License) and ignore local matplotlib settings; PDF figures no longer embed a creation date.
3. **Figure layout.** A text-collision check of every figure (run while fixing item 2) found overlapping panel titles
   in the reachability and surface-screening figures, overprinted scenario labels on the orbiter-window timeline and
   in the Pareto plot, legends covering data, evidence tags touching axis labels, and lunar feature labels cut off
   at the map edge. In the figure comparing flash brightness with eye, binocular, telescope and phone limits, the
   limit labels were placed in data units far above the plot and the axis label said "brighter to the left" on an
   axis where brighter is to the right. These were corrected. No plotted data changed.

## Why Monte Carlo results differ between platforms

On one platform the pipeline is deterministic: a full re-run of the scenario step at the production sample size
reproduced all scenario cards bit for bit, and a repeated reduced run with a different Python hash seed gave
identical output. Across platforms, the correlated-weather draw (`numpy.random.Generator.multivariate_normal`,
`ayap1obs/weather.py`) factorises the covariance matrix with the local linear-algebra library (OpenBLAS here,
Accelerate on Apple silicon), and equally valid factorisations turn the same random numbers into different, but
statistically equivalent, samples. Library maths functions can also differ in the last bit. The Monte Carlo
outputs are therefore compared statistically, and they agree within sampling error.

## Result (release 1.0.1)

`make check` was run on the independent platform (macOS, Apple silicon, Python 3.13.13, numpy 2.5.3) with release
1.0.1 (git b6ce656) at the production sample sizes (NMC = 6000, NTRIAL = 10); the pipeline took 70 minutes.
Verbatim report (`.check/report.md`):

```
[PASS] Deterministic tables: 12 of 12 equal to rounding (largest relative difference 3.2e-16)
[PASS] Arrays (screening, reachability): 29 of 29 equal to rounding (largest relative difference 1.5e-14)
[PASS] Scenario cards, deterministic values: 7129 of 7129 equal to rounding (largest relative difference 7.0e-10); 0 text differences
[PASS] Monte Carlo probabilities (NMC 6000 vs 6000): 4774 values, 76 % identical; largest difference 0.026; largest 2.5 standard errors (limit 5); 0.00 % beyond 3 (limit 1 %)
[info] Other Monte Carlo summaries in the scenario cards (medians, means, quantiles): 671 values, largest relative difference 0.0338
[PASS] Ephemeris validation against JPL Horizons: report identical

[info] Seeded flash-magnitude sample: 5 of 10 values identical, largest difference 5.33e-15
[info] Injection-recovery curves: 172 of 172 values identical, largest difference 0
[info] Numbers quoted in the manuscript: 677 of 776 identical, largest numeric difference 0.01
[info] Website data files: 8 of 9 identical; largest numeric difference 0.011 (Monte Carlo values)
[info] Figures: 0 of 25 pixel-identical; differing: fig_availability_timeseries.png, fig_ejecta_crater.png, fig_flash_sensitivity.png, fig_injection_recovery.png, fig_lightcurves_limits.png, fig_orbiter_latency.png ...

[PASS] RESULT: the run reproduces the archived outputs
```

The tie in the launch-to-impact table is resolved: all 12 deterministic tables now agree. The comparison counts
(12 tables, 29 arrays, 11 scenario cards, 4774 Monte Carlo probabilities) show that every compared product was
present in both trees. Figures still differ at the pixel level between the two platforms (anti-aliasing of text and
lines differs slightly between builds), so they are reported for information only.

## Limitations of this check

This record establishes computational reproducibility of release 1.0.1, not the correctness of its models. An
independent scientific audit of the same commit (7 October 2026) found errors in the physical models and in some
labels; they are corrected in a later release. The audit also noted that the 1.0.1 checker skipped a product when it
was missing from either tree instead of failing (it did not affect this run, in which every product was present);
the checker of the corrected release requires every product listed in a release manifest.
