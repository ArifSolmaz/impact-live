# Response to the independent scientific re-audit of release 2.0

The re-audit (7 October 2026, release 2.0.0 snapshot) assessed every finding of the first audit and reported 43 open
items: 3 major, 25 moderate and 15 minor. They concern geometry and orbits (GE), physics (PH), statistics,
reproducibility and records (ST) and the website (WB). This file answers each item. Release 2.1.0 contains the
corrected code, a complete rerun of the pipeline, the regenerated tables, figures, scenario cards and website data,
the revised manuscript and the reproduction-check fix of 2.0.1. The response to the first audit remains in
[AUDIT_RESPONSE.md](AUDIT_RESPONSE.md).

Status labels: **Fixed** (the defect is corrected and the products are regenerated), **Fixed (wording)** (the claim
is corrected; no computation was wrong), **Partly fixed** (corrected as far as the available information allows; what
remains is stated here and as a limitation in the paper).

Paths are relative to the repository root. "Paper" refers to the manuscript sections in `paper/sections/`, which are
not yet in the public repository.

## Summary of consequences for the conclusions

- **Ejecta plume.** Release 2.0 omitted the slow in-domain ejecta (PH-N01) and used one grain distribution
  (PH-N02). With every in-domain speed, a finite source, exposure integration, a camera model and source extinction,
  regolith-like grains still give no detectable plume (largest signal-to-noise ratio 1.2 for a 1-m telescope),
  but fine-rich grains give 8.7 for the near-terminator scenario S2 and the optimistic corner of the declared
  ranges 29. Plume detectability is therefore **not constrained**, and the paper and website now say so
  instead of "no modelled plume is detectable".
- **Opportunities.** Each circular overflight is now mapped to the impact time of a 25-m/s de-orbit burn, both
  traversal directions of every plane are sampled, and the station and class gates are evaluated at that time (GE-01,
  GE-V2-02, GE-V2-03). The products are called circular-overflight screening opportunities; the definite-impact and
  mission-feasible wording is removed. Relative to release 2.0 the window probabilities averaged over start days
  change by at most 0.03 (class A 30-day mean 0.40 → 0.41, class B unchanged at 0.98): under a uniform phase prior a
  constant phase offset largely cancels, as the re-audit anticipated, and the two traversal directions give the same
  statistics. The class-A minima over start days rise (60-day windows 0.00 → 0.15, 90-day 0.22 → 0.29): for 60-day
  windows opening in July 2028 the only class-A opportunities fall on 26 August 2028, when at TUG the Sun is below
  −12° while the waxing Moon is still above 20° for about 8 minutes (20:34–20:41 Istanbul time), an interval that
  release 2.0's nearest-grid-time gates missed. The paper now says that this minimum rests on a single evening.
  Individual opportunity times and catalogue entries change.
- **Network probabilities.** The pooled probabilities change by at most 0.01 after the camera corrections (PH-N05,
  PH-N07, PH-N08). The epistemic 5–95 % ranges no longer contain inner Monte Carlo noise (ST-01); for S1 network A
  the range is 0.42–0.56 (release 2.0: 0.40–0.59).
- **Orbiters.** Danuri is planned to impact the Moon in March 2028, so it is unavailable in the baseline for every
  scenario except S11 (GE-V2-05). LRO seasons are computed from archived Horizons elements and agree with release
  2.0's dates within one day (GE-21).

## Additional problems found during the revision

1. The JPL Horizons LRO record supplied for GE-21 contains, after the last tracking solution (2 September 2026), a
   558-day prediction whose node regresses at 0.004–0.02 deg/day against 0.09–0.12 deg/day (and accelerating) in every
   observed year. A first draft of release 2.1 used the prediction and moved the 2028 seasons by up to two months.
   `ayap1obs/orbiters.py` now uses only the tracking-based elements and extrapolates the node with a quadratic trend;
   a hold-out test (fits ending 2024-03, 2024-09 and 2025-03, compared with the later tracking data) moves season
   boundaries by at most 5 days, and alternative fits give each boundary a range (at most 17 days in the
   domain).
2. The plume aperture (cells above 20 % of the peak excess) is a heuristic, not an optimal filter. Raising the
   dust/ground contrast κ for S2 brightens the small contrast-class region near the impact point and shrinks the
   aperture, so the signal-to-noise ratio for κ = 1 (1.0) is slightly lower than for κ = 0.2 (1.2). This does not
   change any conclusion; the paper calls the aperture heuristic.
3. `scripts/validate_lightcurves.py` truncated the first character of its case labels in the Markdown report; fixed.
4. A reproduction check on macOS (Apple silicon) of the first 2.1 archive reproduced every deterministic product to
   rounding and the scenario Monte Carlo exactly, but failed on the injection fits of the afocal-phone system, where
   1–5 % of even the brightest injected flashes were missed. The cause was the frame registration of the injection
   experiment (unchanged since release 2.0): its unrestricted cross-correlation search occasionally locked onto a
   distant spurious peak in low-contrast 8-bit phone video and jumped by 10–15 pixels, beyond the padded analysis
   crop. Whether a jump fell inside a trial depended on the random realisation, and the realisations differed between
   the computers because one random stream served every system, so a platform-dependent difference in one draw changed
   all later draws. The search is now limited to ±7 pixels (the analysis crops are padded by 8) with the sub-pixel
   step limited to ±0.5 pixel, and every clip, trial and fit bootstrap has its own random stream. The regenerated
   results recover every bright flash in every system; the 50 % recovery magnitudes moved by at most 0.03 mag and the
   false-alarm rates within their clip-bootstrap intervals; 14 of 16 500 blank-clip frames reach the ±7-pixel limit
   (`outputs/tables/injection_recovery.json`, `registration`).

---

## Major

**GE-01 · MAJOR · The reachability mask tests an orbit plane, not a dynamically attainable impact at the stated
epoch.** — *Partly fixed.* `ayap1obs/opportunities.py` (`transfer_offset_s`, `node_occupancy`) now places the impact
Δt = (Δu_d − n t_f)/n before the circular overflight of the target point: 91.50 s for the 25-m/s production burn and
14.73 s for the 50-m/s sensitivity, the values the re-audit derived. Station altitudes, emission and incidence and
the class gates are evaluated at that impact time. `ayap1obs/reachability.propagate_descent` integrates the descent
from the burn state with RK4; for 61 opportunities it lands within 0.42 km of the target, the residual being
the target's own motion during the offset (`outputs/validation/transfer_check.json`). The 50-m/s burn is a
convergence variant (`scripts/check_reachability_convergence.py`). The docstring now calls 3° a flight-path angle at
impact and states that the descents span 84–147° of central angle. Not done: a joint solution of the burn with a
cross-track manoeuvre (the plane change and its timing would shift the phase). The outputs are therefore called
circular-overflight screening opportunities in the code, paper (Methods 5.3, Results 6.2, Conclusions) and website,
and the definite-impact and mission-feasible wording is removed.

**PH-N01 · MAJOR · The new plume conclusion silently excludes slow ejecta that remain inside the cited scaling
domain.** — *Fixed.* `ayap1obs/plume.py` follows every in-domain speed from a 1-m/s floor (`PLUME_V_FLOOR`) or, for
a dark site, from the vertical launch speed needed to reach sunlight and visibility (slower ejecta can never be lit),
declared in each case; the 50-m height floor is removed. For S5 all eight cases are now within the domain (release
2.0: the hollow cases could not be determined), with up to 189 152 kg of visible sunlit ejecta. Speed floors of
0.5, 2 and 5 m/s change the S5 signal-to-noise ratio by at most 4 %
(`outputs/tables/plume_convergence.csv`).

**ST-23 · MAJOR · Missing required products are caught, but the comparison still falsely passes corrupted Monte Carlo,
injection and site products.** — *Fixed.* `scripts/check_reproduction.py` validates the structure of both trees before
comparing them (`validate_products`): probabilities within [0, 1] and equal to k/N, intervals equal to p ± 1.96 SE,
ordered epistemic quantiles, paired differences equal to the difference of the pooled values, the Monte Carlo CSV
tables and the nondominance recomputed from the cards, injection rows, fits (m90 = m50 − w ln 9) and false-alarm
products with consistent totals, and website records for exactly the expected scenarios equal to the cards. The
comparison then covers the epistemic quantiles (within 0.08), the paired differences (within five combined standard
errors), every injection fit (m50, m90 and width within twice the combined bootstrap half-widths), every recovery row
(five binomial standard errors) and the false-alarm products (overlapping clip-bootstrap intervals), and the
deterministic website files. `scripts/test_checker.py` (`make test-checker`) copies the archived outputs and requires
PASS for an unmodified copy and FAIL for each corruption the re-audit used: Monte Carlo CSV tables replaced by text,
S1 intervals set to [0, 1], paired effects set to 999, injection m90/width/recovery fractions set to 999, emptied
false-alarm arrays, a dual coincidence rate of 999, an emptied website scenario list, plus inverted quantiles. All
expectations are met (`make test-checker` on the release 2.1 outputs: 9 of 9 expectations met).

## Moderate

**GE-04 · MODERATE · The 86° polar scenario is not available on every orbit.** — *Fixed (wording).* Results 6.2 and
Discussion 7.1 now say that only an exact pole lies in every polar plane, that a near-polar point is reached only from
compatible planes, directions and phases within the allowance, and that the polar counts are regional averages.

**GE-08 · MODERATE · The convergence check does not establish convergence of the decision quantities.** — *Fixed.*
`scripts/check_reachability_convergence.py` recomputes six planes with a 5-min grid, 16 phases, phases offset by
22.5°, nodes offset by 2.5° (between the sampled planes), HEALPix Nside 64 (0.92° pixels, finer than the 1.2° full
width of the 0.6° band) and the 50-m/s burn, with the gates at the impact time (GE-V2-03). For six directed planes
(three geometric planes in both directions), numerical refinement (5-min grid, 16 phases, Nside 64) changes the mean
30-day window probability by at most 0.008, its minimum over start days by 0, the probability of a first opportunity
within three months by at most 0.021 and the opportunity-hours per plane by at most 6.5 % (the finer grid has more
pixels). Sampling other planes and phases between the production ones (nodes +2.5°, phases +22.5°) changes them by at
most 0.022, 0, 0.042 and 21.6 %, the plane-to-plane spread of six planes; on the full set, halving the planes or
phases changes the mean by at most 0.006. The 50-m/s burn changes them by at most 0.001, 0, 0 and 0.3 %
(`outputs/tables/reachability_convergence.csv`, column `kind`).

**GE-13 · MODERATE · The plume terrain ray search can declare visibility while the line of sight is blocked.** —
*Fixed.* `ayap1obs/terrain.plume_clearance_height_km` traces the line of sight beyond its closest approach to the
sphere, up to the highest terrain in the DEM, and measures heights above the local ground. `scripts/validate_terrain.py`
adds a regression with a synthetic ridge behind the tangent point (`outputs/validation/terrain_validation.json`,
`ridge_regression`), which release 2.0's search missed.

**GE-21 · MODERATE · Orbiter illumination windows are not reproducible.** — *Fixed.* The JPL Horizons osculating
elements of LRO (daily, 2023–2028, record revised 30 September 2026) are archived in `data/horizons/` and
`scripts/make_orbiter_seasons.py` computes the beta-angle seasons (`outputs/tables/orbiter_seasons.json`), with the
method, ranges and hold-out test described under "Additional problems" above. Checks: predicted overflight incidence
70.5° for the Falcon 9 crater (LROC 67–71°) and 14.8° for SLIM (14°). The low-Sun seasons in the domain are 12 May–13
July 2027; 23 October–21 December 2027; 28 March–28 May 2028; 7 September–5 November 2028; 11 February–10 April 2029;
the four that release 2.0 listed agree with its dates within one day, so the earlier values were right but not
reproducible. Danuri's seasons, provisional in release 2.0, are now computed in the same way from its archived
Horizons elements (KARI solutions to 2026-09-29, query supplied by the author;
`data/horizons/horizons_kplo_elements_2023-2027.txt`): 23 March–2 June and 25 September–3 December 2027, within one
day of the earlier estimate, with the KARI prediction in the same record within 0.6° in beta.

**GE-V2-02 · MODERATE · Geometric polar-plane deduplication omits the opposite traversal direction.** — *Fixed.*
`config/orbit_families.yaml` samples nodes 0–355° (72 directed planes); every statistic marginalises over both
directions. Computed separately (`outputs/tables/opportunity_convergence.csv`, subsets `direction 1` and `direction
2`), the two directions give mean 30-day window probabilities within 0.001, minima over start days within 0.007 and
first-opportunity probabilities within 0.003 of each other, but different opportunity times.

**GE-V2-03 · MODERATE · Catalogue station counts and class gates are evaluated at a nearest grid time.** — *Fixed.*
`ayap1obs/opportunities.context` and `gates_at` interpolate the continuous station altitudes, illuminated fraction and
elongation from the 10-min grid to each opportunity's impact time before thresholding, and the geocentric emission and
incidence are computed at that time; the catalogue records those gates. An independent recomputation of every one of
the 8842 catalogue rows with astropy at the stored impact time (`scripts/check_catalogue_gates.py`,
`outputs/validation/catalogue_gate_check.json`) finds 15 total-count and 6 Turkish-count differences of one site, each
with a station within 0.007° of a threshold, 0 TUG differences and no row that falls below three sites (release 2.0:
921 of 4450 rows differed).

**GE-V2-05 · MODERATE · Danuri's published planned March 2028 disposal is omitted.** — *Fixed.* KASA's press release of
10 February 2025 (Korean text supplied by the author; the KASA site was not reachable) states that after the extended
mission to the end of 2027 the orbit will be lowered for landing-technology tests and Danuri will be crashed into the
Moon in March 2028. `config/orbiters.yaml` and every card treat Danuri as available (assumed 0.4) only before 1 March
2028 (its computed seasons after that date are flagged); continued operation is a separate changed-plan sensitivity.
The paper (Methods 5.9, Results 6.10, Discussion, Conclusions) and `research/orbiters.md` are updated.

**PH-21 · MODERATE · Crater comparison still mixes assumed inputs with independent validation claims.** — *Fixed.*
`scripts/make_physics_figures.py` adds LCROSS (2271.61 kg, 2.506885 km/s, 85.9°; 22 m from ShadowCam, Fassett et al.
2024, earlier indirect estimates 25–30 m), labels it a near-vertical scaling check (the oblique rules coincide), and
labels LADEE an assumed-angle sensitivity with a censored size. The false "only three with published inputs"
statement is removed, and the paper calls the agreement of broad envelopes qualitative consistency, not evidence for a
rule; it also notes that the LCROSS density calibration is not independent of that event.
(`outputs/tables/ejecta_checks.json`: GRAIL falls between the two envelopes; Falcon 9 and LADEE inside the
vertical-component envelopes; LCROSS inside both.)

**PH-23 · MODERATE · Corrected GRAIL attribution is not reconciled with the main precedent notes.** — *Fixed.*
`research/precedents.md` (quick-look row, GRAIL table, section (d)) and `research/precedents.csv` now give the LAMP
result of Retherford et al. (2013): excess Lyman-α and 185-nm emission from H and Hg in the plumes, an orbital gas
detection that does not conflict with the absence of ground flash or dust reports. The replaced statements are
listed in `research/CHANGELOG.md`.

**PH-24 · MODERATE · Corrected Kaguya source is not reconciled with earlier notes and cadence wording.** — *Fixed.*
The precedent notes and CSV now use the ESA AAT/IRIS2 record (2.3 µm, flash in one frame, Mount Abu reports, launch
mass 2900 kg, impact mass unverified). The cadence is given as the quoted "1 second exposures with 0.6 seconds
intervals", read as gaps between exposures (start-to-start about 1.6 s if so) and marked unverified, in the notes and
in the paper's comparator table (release 2.0: "1-s exposures at 0.6-s intervals").

**PH-32 · MODERATE · Categorical absence-of-calibration wording survives the narrower source review.** — *Fixed
(wording).* Methods 5.5, Sections 4.2 and 8, the efficiency figure tag and `research/precedents.md` now use one scoped statement: we have
not established a calibrated visible-band efficiency transferable to slow, grazing, full-spacecraft impacts, as the
result of the stated search, not proof of absence. Burchell et al. (2010) is cited for what its abstract says.

**PH-N02 · MODERATE · A single assumed grain distribution is treated as a robust plume nondetection result.** —
*Fixed.* Three grain models (regolith, coarse, fine-rich), p Φ 0.01–0.1, dust/ground contrast κ 0.2–1 and the
optimistic corner are run for every within-domain case and stored in the cards (`grains_sys0.001`, `pphi_sys0.001`,
`kappa_sys0.001`, `optimistic_corner_sys0.001`), tabulated (paper Table 11) and shown in Figure 8b. The conclusion is
qualified to regolith-like grains and the stated p Φ and systematic; fine-rich grains are described as the LCROSS
brightness-to-mass convention, not a calibrated fast-ejecta spectrum. Correlating grain size with ejection speed is
not modelled (one-at-a-time sensitivities only).

**PH-N03 · MODERATE · Plume optical-depth limiting and early peaks depend strongly on the point-source and grid
choices.** — *Fixed.* Finite source (launch radius x(v), launch time x/v), mass deposited by cloud-in-cell on nested
grids (50-m cells within 2 km, 0.5-km cells to 40 km) with the optical depth applied at the deposit resolution,
records every 0.25 s early on, and exposure integration over 1-s windows. `scripts/check_plume_convergence.py` varies
the cell sizes, the number of parcels (×8), the integration and record steps, the speed floor and the source model:
numerical variants change the regolith S2 and S5 signal-to-noise ratios by at most 2 % and 8 %, a
point source at t = 0 by 1 %; a 0.1-s window lowers S2 by 19 %.

**PH-N04 · MODERATE · The claimed exact exposure integrals use coarse temperature/time interpolation with measurable
error.** — *Fixed.* `ayap1obs/impact.py` no longer interpolates a temperature–time table. With x = t/τ every exposure
integral is G_b(x; T0) = [Φ_b(T0) − Φ_b(T(x))]/(T0 − T_f), where Φ_b(T) is the integral of the band fraction over
temperature, tabulated every 0.5 K by Gauss–Legendre quadrature and interpolated with cubic Hermite polynomials that
use its derivative; the visible energy, partial exposures and band peaks follow from the same tables.
`scripts/validate_lightcurves.py` (`make validate`) compares first exposures, arbitrary intervals, band peaks and the
visible energy with independent adaptive quadrature over the temperature and duration priors: worst error
4 × 10⁻⁵ mag (`outputs/validation/lightcurve_accuracy.md`); for the re-audit's cases (V peak and fluence at 1350 K,
first 23-ms exposure, Ks peak) the errors are below 4 × 10⁻⁶ mag (release 2.0: up to 0.15 mag). The paper and the
code describe the integrals as tabulated, with this error budget, instead of exact.

**PH-N05 · MODERATE · The Monte Carlo chooses a noiseless best frame, then adds noise.** — *Fixed.*
`ayap1obs/montecarlo.simulate` gives each candidate frame (first three after the phase and three around each band's
peak, shared by synchronised cameras) independent frame noise plus a camera-level reference and systematic error, and
selects the best frame after the noise; dual-camera validation compares the two cameras frame by frame.

**PH-N06 · MODERATE · The new plume SNR omits source extinction and a complete camera model.** — *Fixed.*
`plume.plume_detectability_multi` extincts the source like the background and uses `CAMERA_1M` (1-m aperture,
0.5″ pixels, full well 60 000 e⁻, read noise 5 e⁻, dark current, 20 reference frames): the exposure is shortened so
that the background fills at most half the full well, frames are co-added over the window with a readout gap, and the
noise includes source and background shot noise, read and dark noise per frame, the reference mean and the
subtraction systematic. The camera settings are stored in each card (`camera`).

**PH-N07 · MODERATE · Source-core saturation is flagged but does not alter counts or SNR.** — *Fixed.*
`detect.clipped_aperture_signal` applies saturation: for a Gaussian PSF with peak-pixel fraction q and headroom
L = full well − background, the recorded signal is (L/q)(1 + ln(qN/L)) when qN > L. It is used by the analytic limits,
the Monte Carlo and the ladder.

**ST-01 · MODERATE · Pooled Monte Carlo precision is fixed; reported epistemic ranges still contain substantial
inner-event simulation noise.** — *Fixed.* `montecarlo.epistemic_quantiles` fits a beta-binomial model to the
per-draw success counts and reports the quantiles of the fitted beta distribution as `outer_p05/50/95`; the raw
sample-proportion quantiles are kept as `outer_raw_p05/95`. The release uses 600 inner events per draw (200 × 600 =
120 000 per scenario, strategy and prior). For S1 with the same 200 outer draws: network A, 150 inner events give a
raw range 0.400–0.587 and a deconvolved 0.428–0.556; 2400 give 0.419–0.561 raw and 0.422–0.556 deconvolved
(`mc_inner_convergence` in `outputs/scenarios/S1.json`; widths of the deconvolved ranges change by at most 0.01).
The pooled standard errors and paired differences keep the clustered estimate. The website caption now reads "range
over the assumption draws (weather, readiness, throughput, background, terrain; finite-sample noise removed)".

**ST-08 · MODERATE · Direct coincidence counts replace the extrapolation, but exact Poisson intervals and one
background clip remain.** — *Fixed.* `scripts/run_injection_recovery.py` renders 10 independent blank clips per system
(different texture crops and atmosphere realisations), counts candidates per 40-px box and frame, and gives
clip-bootstrap 95 % intervals and the dispersion index of the per-clip counts instead of exact Poisson intervals.
Candidate rates per box-frame: NELIOTA-like camera 0.0022 (95 % 0.0007–0.0036), TUG 0.057 (0.031–0.085; dispersion
index 40.3, strongly overdispersed), amateur 0.0149, afocal phone 0.0033, standalone phone 0.0007; 0 NELIOTA-like
coincidences in 2750 box-frames (95 % upper limit 0.0013). Over the frames searched for one injection these rates give
0.09 (NELIOTA-like) to 3.4 (TUG) false candidates. Injection trials still reuse the pre-rendered background clips
(stated in the paper).

**ST-12 · MODERATE · Joint objectives are evaluated, but nonsignificance is treated as no worse.** — *Fixed.*
`scripts/make_pareto.py` reports a descriptive Pareto front (point estimates) and conservative dominance (a strategy
is dominated only if another has no higher weight and simultaneous one-sided 95 % lower bounds, Bonferroni over the
three probabilities, of at least zero on every probability, with one bound above zero or a lower weight). The two
rules give the same classification in release 2.1; strategy B is no longer reported as dominated in S6.

**ST-N01 · MODERATE · Injection recovery and blank false alarms use different pipelines.** — *Fixed.* One function
(`detect_box`) serves injected and blank video with the same registration, reference, normalisation, matched filter,
noise estimate, threshold and box size; the truth position is used only after detection to classify a candidate.

**ST-N02 · MODERATE · Injection observation duration is capped without a convergence argument.** — *Fixed.* Every
exposure from the onset to 4τ after it is searched (no cap); the frame of first detection is stored and the fit
restricted to the first 40 frames is reported. The 50 % recovery magnitudes change by at most 0.01 mag when only the
first 40 frames are searched; almost every recovery happens in the first frames, so the release-2.0 cap did not bias
the results, but it is no longer applied.

**ST-N07 · MODERATE · Concurrent reproduction checks can delete one another's working tree.** — *Fixed (2.0.1).*
`scripts/check_reproduction.py` holds an exclusive lock on `.check/` and refuses a second check (exit status 3), prints
a progress line after 5 quiet minutes and keeps `.check/run.log` current. A complete cloud check of 2.0.1 passed.

**WB-N01 · MODERATE · S2 remains labelled favourable for a plume.** — *Fixed.* S2 is now "Terminator plume test: 3°
beyond the sunrise terminator" with class `test` (`config/scenarios.yaml`), shown with a neutral badge on the website.

**WB-N02 · MODERATE · Detection ladder and simulator extrapolate unsupported magnitude tails.** — *Fixed.*
`scripts/make_site_data.py` keeps ladder points only where at least 50 sampled draws support them, marks magnitudes
beyond the sampled range instead of padding them, and the "see" page states "beyond the simulated range".

## Minor

**GE-03 · MINOR · The 0.6° band is incorrectly called no plane change.** — *Fixed (wording).* Results 6.2 and the
methods describe both allowances as plane changes (≈17 and ≈71 m/s).

**GE-V2-06 · MINOR · The revised LOLA reader does not reject unsupported projections.** — *Fixed.*
`terrain.parse_pds3_label` parses quoted values and `load_real_dem` accepts only simple cylindrical, east-positive,
mean-Earth products with centre longitude 180°, centre latitude 0°, half-grid offsets and radius 1737.4 km;
`scripts/validate_terrain.py` checks that labels violating each condition are rejected.

**GE-V2-07 · MINOR · Exact archived Earth-orientation bound is slightly smaller than reported.** — *Fixed.*
`ephem.iers_provenance` records the held UT1−UTC and the bound 0.9 s + |held| (1.048 s) with the corresponding Earth
rotation (`outputs/validation/iers_provenance.json`).

**PH-14 · MINOR · Visual outcome branch still evaluates uncertain events at nominal geometry.** — *Fixed.*
`montecarlo.visual_model` evaluates the public site's Moon and Sun altitudes, airmass and the point's visibility for
each event with its shared time and position offsets.

**PH-N08 · MINOR · The analytic reference variance includes background shot noise but omits read and dark noise.** —
*Fixed.* `detect.noise_terms` adds (B + dark·t + RN²)/n_ref per pixel for the reference mean.

**ST-04 · MINOR · Weather priors are qualified in the model and paper, but the website still calls them
climatological averages.** — *Fixed.* Limitation 4 on the science page now reads, in both languages, that the weather
probabilities are illustrative planning priors derived from site statistics with different definitions and from
assumptions, not calibrated hourly climatology or forecasts (`site/assets/js/i18n.js`, `lim.4`).

**ST-26 · MINOR · Source status is more honest, but quotation provenance is still not archived.** — *Partly fixed.*
`research/quotations.csv` lists every reused external quotation (31 rows): the text as printed and where it is used,
the original wording and its SHA-256, the source, publication and access dates, the retrieval method, whether it is a
direct, shortened or translated quotation, and any correction. `scripts/check_quotations.py` (`make quotes`) confirms
that each printed text occurs where the ledger says. Five manuscript quotations were corrected (paraphrases in
quotation marks replaced by exact text; capitalisation and word endings as in the sources). Raw page snapshots cannot
be archived: the page reader returns processed text, not the original bytes. Literature-negative statements are now
phrased as the result of the stated search.

**ST-N03 · MINOR · Manuscript gives the wrong injection random seed.** — *Fixed.* The appendix gives 20261007 (from the
injection results) and `outputs/validation/release_manifest.json` exports every seed (`random_seeds`).

**ST-N04 · MINOR · Weather sensitivity cases are claimed but not run.** — *Fixed.* `scripts/run_scenarios.py` runs a
flat seasonal pattern, correlation lengths of 250 and 1000 km and halved and doubled prior spreads for S1 (spring) and
S11 (winter) and stores them (`mc_weather_sensitivity`). For S1 they move P(any, B) by at most 0.02 and P(two sites, B)
by at most 0.03; for S11 the flat pattern raises P(any, B) from 0.57 to 0.65 and P(two sites, B) from 0.27 to 0.37,
which shows that the guessed winter cloudiness drives the S11 difference. `ayap1obs/weather.py` and the paper say the
pattern is guessed, not evidence.

**ST-N05 · MINOR · Preliminary engagement notes retain superseded protocol instructions.** — *Fixed.* Section (c) of
`research/engagement.md` (private) is marked as superseded by Appendix A, with the conflicting timing, estimand,
power-correlation and consent statements named.

**ST-N06 · MINOR · Population agglomeration is described as merging, while the implementation deletes records.** —
*Fixed (wording).* The paper and a correction note in `AUDIT_RESPONSE.md` say that smaller records within the radius
are heuristically excluded (their population is not added), and the 0/10/25-km results are heuristic sensitivity
cases, not bounds.

**WB-N03 · MINOR · Explorer claims 6,000 simulations although release 2 uses 30,000.** — *Fixed.*
`site/data/scenarios.json` exports `mc.n_outer` and `mc.n_inner`, and both languages render "200 assumption draws ×
600 events = 120,000 events" from them.

**WB-N04 · MINOR · Mobile science page expands beyond the viewport.** — *Fixed.* Grid tracks use `minmax(0, 1fr)`,
grid children have `min-width: 0` and code blocks are bounded; at 390 px the page width equals the viewport in both
languages (browser test with headless Chromium: scrollWidth 390 px on all five pages in both languages, 0 failures).

**WB-N05 · MINOR · Approximate-zero formatting repeats the approximation symbol.** — *Fixed.* `fmt.pct` owns the
symbol and renders tiny values as "below 0.1 %" instead of "≈0 %".

**WB-N06 · MINOR · Science summary presents two strategy point estimates as an unlabeled range.** — *Fixed.* The
summary names each value with its network: recordings at two separate sites have a model chance of 21 % with the
Türkiye network and 47 % with the global network (filled from the scenario data).
