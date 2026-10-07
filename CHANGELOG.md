# Changelog

## 1.0.1 (2026-10-07)

Reproducibility and figure fixes after an independent re-run on a second platform (macOS on Apple silicon; see
[`outputs/validation/cross_platform_run.md`](outputs/validation/cross_platform_run.md)). No scientific result changed.

- **Reproduction check.** `make check` and `make check-quick` re-run the whole pipeline in a clean copy and compare
  the result with the archived outputs against stated tolerances, printing PASS or FAIL
  ([`scripts/check_reproduction.py`](scripts/check_reproduction.py), [`docs/REPRODUCING.md`](docs/REPRODUCING.md)).
- **Same figures on every computer.** Figures use the Inter typeface shipped in [`data/fonts`](data/fonts)
  (SIL Open Font License) and ignore local matplotlib settings. PDF figures no longer embed a creation date, so
  repeated runs give identical files.
- **Platform-independent tie-break.** In the launch-to-impact table, when two observing evenings are equally good
  the earlier one is now chosen. Previously the choice depended on the platform's sort routine. Two entries change
  from 2029-01-22 to 2029-01-21 (launch cases L1 and L5, nominal phases).
- **Figure layout.** Shorter panel titles (reachability, surface screening, scenario coverage maps); one label per
  epoch on the orbiter-window timeline; one label for coinciding points in the Pareto plot; legends moved off the
  data; evidence tags placed below the axes; lunar feature labels kept inside the map. In the figure comparing the
  predicted flash brightness with eye, binocular, telescope and phone limits, the limit labels now sit inside the plot
  (they floated far above it and made the figure very tall) and the axis label now correctly reads "brighter to the
  right". The plotted data are unchanged.
- **Website.** Figures and the launch-to-impact data regenerated.

## 1.0.0 (2026-10-06)

First public release: analysis code, input data, outputs and the bilingual website.
