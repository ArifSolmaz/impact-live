# Changelog

## 2.1.0 (2026-10-07)

Corrected analysis after an independent scientific re-audit of release 2.0 (43 open items: 3 major, 25 moderate,
15 minor). Every product was regenerated with one version of the code; the point-by-point response is
[docs/REAUDIT_RESPONSE.md](docs/REAUDIT_RESPONSE.md). Includes the 2.0.1 reproduction-check fix.

**Changed conclusions**
- Plume: with regolith-like grains no modelled plume is detectable with a metre-class telescope, but fine-grained
  ejecta or optimistic photometry would make the near-terminator plume detectable, so plume detectability is not
  constrained (release 2.0: "no modelled plume is detectable"). Release 2.0 omitted the slow in-domain ejecta.
- Opportunities are called circular-overflight screening opportunities, not definite or mission-feasible impacts.
  The mean window probabilities change by at most 0.03; the class-A minima over start days rise (60-day windows
  0.00 to 0.15, 90-day 0.22 to 0.29) because the exact-time gates admit a short evening interval on 26 August 2028
  that release 2.0's nearest-grid-time gates missed.
- Danuri is not available after its planned lunar impact in March 2028 (KASA); LRO and Danuri seasons are computed
  from archived Horizons elements (they agree with release 2.0's dates within one day).
- Network probabilities are unchanged within 0.01; their epistemic ranges no longer include inner Monte Carlo noise.

**Geometry and orbits**
- Each circular overflight is mapped to the impact time of a 25-m/s de-orbit burn (91.5 s earlier; 14.7 s at 50 m/s),
  checked by RK4 propagation; release 2.0 placed the burn 141 km along track from where it must be.
- Both traversal directions of every polar plane (72 directed planes); station counts and class gates at the impact
  time from continuous station altitudes; convergence variants add HEALPix Nside 64, offset nodes and phases and the
  50-m/s burn.
- Terrain ray tracing continues past the closest approach (ridge regression test); the LOLA reader parses quoted
  label values and rejects unsupported projections, frames and offsets; the UT1 bound is 0.9 s plus the held offset.
- LRO and Danuri beta-angle seasons from the tracking-based part of archived JPL Horizons elements with a fitted node
  trend, alternative fits and a hold-out test (`scripts/make_orbiter_seasons.py`; the Horizons predictions are not
  used).

**Physics and detection**
- Light-curve integrals rewritten as temperature integrals tabulated every 0.5 K (no time grid), validated against
  adaptive quadrature (worst error below 1e-4 mag; `scripts/validate_lightcurves.py`); release 2.0's tables erred by
  up to 0.15 mag for cool flashes.
- Monte Carlo: per-frame noise before the best frame is chosen, a shared reference and systematic term per camera,
  saturation clipping of the source counts, reference noise on background, dark and read noise; public visual model
  at each event's geometry.
- Plume: every in-domain ejecta speed from 1 m/s, finite source, mass on nested grids, grain, p Phi and contrast
  sensitivities, additive and contrast classes, exposure integration with a camera model and source extinction;
  numerical convergence study (`scripts/check_plume_convergence.py`).
- Crater comparison adds LCROSS (22 m, ShadowCam; Fassett et al. 2024) and treats LADEE as an assumed-angle,
  censored check; wording no longer claims evidence for a rule.
- Injection-recovery and false alarms use one detection pipeline, independent clips, 40-px boxes, clip-bootstrap
  intervals and no frame cap (first-40-frame comparison kept). The frame registration searches only +-7 px with
  sub-pixel steps of at most 0.5 px (an unrestricted search occasionally jumped 10-15 px in phone video, found by a
  macOS reproduction check), and every clip, trial and fit bootstrap has its own random stream.

**Statistics, records and reproducibility**
- Epistemic ranges by beta-binomial deconvolution of the inner sampling (600 inner events), with an inner-size
  convergence check; conservative and descriptive nondominance; weather sensitivities run and exported for S1/S11.
- `make check` validates the structure of the products and compares quantiles, fits and false-alarm products;
  `make test-checker` proves it fails eight corruptions that passed release 2.0's checker.
- Quotation ledger (`research/quotations.csv`, `make quotes`); precedent notes reconciled (Kaguya cadence wording,
  GRAIL LAMP, LCROSS crater, scoped efficiency statement); random seeds exported in the release manifest; injection
  seed corrected in the manuscript (20261007).

**Website**
- S2 relabelled as a terminator plume test; detection-ladder tails beyond the simulated range are no longer padded;
  weather probabilities described as planning priors, not climatology; simulation counts, strategy values and number
  formatting corrected; the 2.1 notice; mobile layout of the science page fixed.

## 2.0.1 (2026-10-07)

Reproduction tooling only; the analysis code and every product are those of 2.0.0.
- `make check` now runs one at a time per folder. A second check started while one was running deleted the first
  one's working copy (`.check/run`), and the first then stopped with a misleading "can't open file" error; the second
  check is now refused with a message (exit status 3).
- The check prints a "still running" line every 5 minutes, so the half-hour overflight step no longer looks stalled,
  and keeps `.check/run.log` current while it runs.

## 2.0.0 (2026-10-07)

Corrected analysis after an independent scientific audit of release 1.0.1 (95 findings). Every product was
regenerated with one version of the code; the point-by-point response is [docs/AUDIT_RESPONSE.md](docs/AUDIT_RESPONSE.md).
Release-1 numbers are superseded.

**Changed conclusions**
- No modelled ejecta plume is detectable with a metre-class telescope in any scenario (release 1: detectable 3° beyond
  the terminator). The corrected Housen–Holsapple scaling respects its normalisation and speed domain, and a
  phase-space plume model with the total background replaces the instantaneous estimate.
- Opportunity statistics are terminal-window probabilities for sampled orbit planes and phases. A Türkiye-evening
  opportunity within 30 days is likely from autumn to spring but does not occur for windows opening in summer.
- Network probabilities come from an event-level Monte Carlo with exposure integration, shared timing and position
  errors, seasonal closures and dual-camera validation, and are reported with 5–95 % epistemic ranges and Monte Carlo
  intervals.
- The saturated SMART-1 frame is a near-infrared, assumed-camera case; it no longer "favours" part of the visible prior.

**Geometry and orbits**
- Trajectory-level overflights of 36 polar planes × 8 phases evaluated at their own times (`ayap1obs/opportunities.py`);
  full DE421 lunar rotation; J2-drift sensitivity set; convergence of the decision quantities
  (`scripts/check_reachability_convergence.py`).
- Light-time-consistent station geometry (impact time at the Moon, reception time per station); IERS provenance;
  like-for-like Horizons validation with thresholds; exact gnomonic disk projections; celestial-north-up disk views.
- LOLA reader with PDS3 label parsing and a synthetic-product test; synthetic terrain as a declared three-level range.
- Seasonal closures applied everywhere through one availability function; screening domain starts 2027-05-01 and a
  February launch family is added.

**Physics and detection**
- Speed-scaled efficiency prior η ∝ v (from intensity ∝ v³); laboratory-trend case reported separately; broad
  temperature prior with cool and narrow sensitivities; corrected energy-cut rejection accounting.
- Crater constants from the Holsapple theory document and Housen & Holsapple (2011), no tuning; out-of-sample check
  against GRAIL, LADEE and the Falcon 9 stage; LCROSS like-for-like calibration of the bulk density.
- Injection–recovery: per-frame seeing and image motion, detector clipping and digitisation, causal reference,
  sub-pixel registration, 100 trials per 0.25 mag, logistic fits with bootstrap intervals, measured false-alarm
  rates in blank sequences.

**Statistics, social science and reproducibility**
- Monte Carlo intervals from the outer-draw means; paired strategy differences; joint nondominance.
- Settlement sums from GeoNames at exact coordinates with agglomeration radii (not a census or audience).
- Engagement protocol: primary estimand, Holm-powered secondary family, equal T1 timing, KVKK Articles 5, 6 and 9.
- Literature corrections: Kaguya (ESA record), GRAIL LAMP detections, Sheward et al. (2024), Fischer et al. (2025),
  the 2017-eclipse reports, the TISP Turkish sample (N = 508).
- `make check` requires an explicit list of products and verifies the data manifest; `make manifest` writes
  `MANIFEST.sha256`, `data/DATA_MANIFEST.sha256` and `outputs/validation/release_manifest.json`; all data-bearing
  packages are pinned.

**Website**
- Data rebuilt from release 2.0; the provisional-results notices are replaced by a release-2.0 note; calendar criteria filled from the configuration;
  exposure-integrated detection ladder; broad-band phone limits; sky-condition and occultation wording; event polling
  in every state.

## 1.0.2 (2026-10-07)

Website wording and behaviour fixes after an independent scientific audit of release 1.0.1. The analysis code and
its results are unchanged; the corrected models follow in the next release, and the website now says so.

- **Revision notice.** The home, Explore, See and Science pages say that the ejecta-plume estimates and the network
  probabilities are being recomputed with a corrected model, and that the percentages shown are provisional.
- **Calendar.** The caption now states the criteria the calendar actually uses (Moon altitude ≥20° at TUG, Sun
  ≤−12°, illuminated fraction 5–60 %, elongation >30°); it previously quoted narrower criteria. The best hour is shown
  with its Istanbul date (it was paired with the UTC date) and rounded to the hourly grid (some times showed a minute
  early, e.g. 18:59). The bars are labelled as sampled hours.
- **Flash animation.** Labelled as an illustration whose spot size, contrast, zoom and timing are not calibrated, and
  the result reads "above/below the assumed brightness threshold" instead of "visible/not visible".
- **Brightness thresholds.** Phone limits are labelled and compared in the broad visible band in which they are
  computed (they were labelled V). The note now explains that comparing the flash's peak with a steady-source limit
  overstates the chances of slow cameras.
- **Earth map and location check.** The Earth map is titled as sky conditions for observing the Moon, with a note when
  the impact point itself is hidden from Earth; the location check says that it covers only the Moon's altitude and the
  darkness of the sky.
- **Scenario details.** The far-side control shows "not observable from Earth" instead of an expected brightness
  (the model value is labelled as an unocculted source-equivalent); the telescope-eye value is labelled as a
  conditional threshold model; the LRO line separates the assumed probability that LRO is operating from the rough
  image latency; the population line says that overlapping GeoNames entries are not removed; plume labels no longer
  claim minute-long visibility or certain invisibility.
- **Moon map layers.** The legends give the exact interval, the ~4° smoothing and the percentile clipping of the
  colour scale.
- **Wording.** Categorical statements were qualified (flash duration, binocular and phone detection, telemetry
  "confirming" the impact, crater imaging "weeks later", luminous efficiency "never measured", reachability, the
  near-infrared advantage). Telemetry wording now distinguishes loss of signal from impact confirmation.
- **Live page.** `event.json` is re-read every minute in every state (previously only while the status was "live"),
  with a "last check" time; the location check follows a newly announced time or the demo unless the user picked a
  time. The home page keeps "Moon now" current.
- **Reproduction record.** `make check` with release 1.0.1 passed on macOS/Apple silicon
  ([`outputs/validation/cross_platform_run.md`](outputs/validation/cross_platform_run.md)).

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
