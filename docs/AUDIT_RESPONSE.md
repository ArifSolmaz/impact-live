# Response to the independent scientific audit of release 1.0.1

The audit (7 October 2026, release 1.0.1 snapshot) reported 95 findings: 25 on geometry, ephemerides and orbits
(GE), 31 on physics (PH; PH-20 is consolidated into WB-04), 25 on statistics, social science and reproducibility
(ST; ST-15 is consolidated into GE-22) and 14 on the website (WB). This file answers every finding. Release 2.0
contains the corrected code, a complete rerun of the pipeline, the regenerated tables, figures, scenario cards and
website data, and the rewritten manuscript.

Status labels: **Fixed** (the defect is corrected and the products are regenerated), **Fixed (wording)** (the claim
is corrected; no computation was wrong), **Addressed within scope** (corrected as far as the available information
allows; what remains is stated as a limitation), **Open** (cannot be resolved from the analysis environment; stated
as a limitation in the paper and here).

Paths are relative to the repository root. "Paper" refers to the manuscript sections in `paper/sections/`, which are
not yet in the public repository.

## Summary of consequences for the conclusions

- **Ejecta plume.** With the corrected Housen–Holsapple scaling, its speed domain, a phase-space trajectory model and
  the total background, no modelled plume is detectable with a metre-class telescope in any scenario. Release 1's
  "detectable 3° beyond the terminator" conclusion is withdrawn; near-terminator sites are no longer recommended for a
  plume channel.
- **Opportunity statistics.** Overflights of sampled planes and phases are evaluated at their own times, and the
  headline statistic is now the probability of an opportunity within a terminal window. A Türkiye-evening opportunity
  within a 30-day window is likely from autumn to spring but does not occur for windows that open in summer; release
  1's "≈1 within six months for any plane" was a fixed-start statistic over the whole science phase.
- **Network probabilities.** The event-level Monte Carlo now integrates exposures, shares timing and position errors,
  applies seasonal closures and reports 5–95 % epistemic ranges and Monte Carlo intervals. The values changed, and the
  ranges are wide; the qualitative ranking of the strategies is reported with paired intervals.
- **SMART-1.** The saturated frame is presented as a near-infrared, assumed-camera case; it no longer "favours the
  upper half" of the visible prior.

## Additional problems found during the revision

These were not in the audit and are corrected in release 2.0:

1. `impact.sample_flash_parameters` counted surplus accepted draws as rejections, so the reported energy-cut rejection
   fraction was about 50 % instead of about 2 % (wide prior). The draws themselves were unaffected.
2. The binomial (Wilson) intervals understated the Monte Carlo error because events are nested in epistemic outer
   draws. Release 2.0 reports intervals from the spread of the outer-draw means (`ayap1obs/montecarlo.py`, fields
   `mc_se` and `ci95`), and the reproduction check uses them.
3. The nondominance analysis compared Türkiye-detection probabilities through unpaired intervals; it now uses paired
   intervals like the other objectives (`scripts/make_pareto.py`).
4. The manuscript referred to a function (`reachability.ballistic_impact_conditions`) that no longer exists; the
   de-orbit numbers are now quoted from `reachability.deorbit_trajectory`.

---

## Geometry, ephemerides and orbits (GE)

**GE-01 · MAJOR · The reachability mask tests an orbit plane, not a dynamically attainable impact.** —
*Addressed within scope.* `ayap1obs/reachability.py` (`overflights`) and `ayap1obs/opportunities.py` now enumerate,
for 36 planes and 8 orbital phases, the times at which the spacecraft passes each pixel's along-track position
within the cross-track allowance, and evaluate emission, incidence and observer availability at each overflight's own
time. `reachability.deorbit_trajectory` shows that a 25–50 m/s retrograde burn reaches the surface 27–47 min later at
≈1.68 km/s, so burn and impact lie on the same pass. Navigation dispersions, finite burns, attitude and operational
constraints are not modelled and are stated as such (paper Sections 5.3 and 8); the products are described as
geometric opportunities of hypothetical planes, not mission plans.

**GE-02 · MODERATE · Opportunity probabilities use a fixed start and the whole science interval.** — *Fixed.*
`scripts/run_opportunity_statistics.py` computes P(≥1 opportunity in [T1, T1+W]) for every start day and W = 7–90 d
(`outputs/tables/opportunity_window_probability.csv`) and, for each launch family and science duration, the
probability for windows opening at the end of the science phase (`timeline_window_probability.csv`). The fixed-start
statistic is kept, labelled as the release-1 comparison.

**GE-03 · MODERATE · The 0.6° band is incorrectly called "no plane change".** — *Fixed (wording).* The allowances are
described as plane changes of ≈17 m/s (0.6°) and ≈71 m/s (2.5°) everywhere (paper, figures, site).

**GE-04 · MODERATE · The 86° polar scenario is not available on every orbit.** — *Fixed.* Each scenario card now gives
the fraction of uniformly distributed polar planes within 0.6°/2.5° of a plane through the point at the epoch and
states that the phase must also be right (`reachability.p_random_polar_plane_within`).

**GE-05 · MAJOR · A fixed inertial plane is rotated with a simplified lunar frame.** — *Fixed.* `reachability.Plane`
and `plane_in_me` use the full DE421 ICRF→ME rotation at every grid time.

**GE-06 · MODERATE · Claimed sensitivity runs are absent.** — *Fixed.* A second family set (88° inclination with J2
nodal drift, −0.042°/day) is run (`opportunities_incl88_j2.npz`), and its window probabilities are compared with the
main set in `timeline_window_probability.csv` and the paper.

**GE-07 · MODERATE · 24 "node families" versus unique planes.** — *Fixed.* The main set has 36 unique polar planes
(nodes 0–175° in 5° steps), stated consistently.

**GE-08 · MODERATE · The convergence check does not test decision quantities.** — *Fixed.*
`scripts/check_reachability_convergence.py` recomputes six planes with a 5-min grid and with 16 phases and compares
the mean 30-day window probability, the first-opportunity probabilities and the opportunity-hours per plane
(`outputs/tables/reachability_convergence.csv`); `opportunity_convergence.csv` gives plane and phase subsets.
`check_convergence.py` is relabelled as a test of broad regional fractions only.

**GE-09 · MODERATE · The configured plume emission limit is unused.** — *Fixed.* The plume class in
`opportunities.node_occupancy` and the scenario cards apply `criteria.plume_sunlit.max_emission_deg`.

**GE-10 · MAJOR · The LOLA reader is shifted by 180°.** — *Fixed (reader); real-file test open.* `terrain.LDEM` parses
the PDS3 map-projection keywords, converts the 0–360° convention and rejects unsupported products;
`scripts/validate_terrain.py` writes a synthetic product with the official conventions and checks bump positions,
latitude orientation and rejection (`outputs/validation/terrain_validation.json`). No real LOLA file could be
downloaded from the analysis environment, so no site-specific terrain test is made (paper Section 5.4).

**GE-11 · MAJOR · Synthetic terrain is not a validated prior and its values are not upper bounds.** — *Fixed.* Three
declared relief levels (RMS 0.3/1.0/2.0 km) give a range of terrain-visibility probabilities, sampled uniformly in
the Monte Carlo and labelled an illustrative sensitivity, neither a validated prior nor a bound.

**GE-12 · MODERATE · Instantaneous spherical incidence does not identify permanent shadow.** — *Fixed (wording).* The
"dark" class is described as the instantaneous spherical night side with a 2° margin, with the caveat about isolated
peaks (`config/domain.yaml`, paper Section 5.2).

**GE-13 · MODERATE · The plume ray search can declare visibility through the sphere.** — *Fixed.*
`terrain.sphere_clearance_height_km` enforces the exact finite-observer limb first, and the terrain ray then traces
the whole line of sight; flat-DEM tests confirm agreement for front-side, near-limb and far-side points.

**GE-14 · MODERATE · Disk figures labelled celestial north up are lunar north up.** — *Fixed.*
`plotting.disk_basis`/`earth_view` build the sky-plane basis with celestial north up and east left and print the
position angle of the lunar pole; views without an epoch are labelled lunar-north-up.

**GE-15 · MINOR · Orthographic approximation of disk coordinates.** — *Fixed.* Exact gnomonic projections from the
observer (`plotting.disk_xy`, `geometry.dist_to_sunlit_arcmin`).

**GE-16 · MODERATE · Future Earth-orientation accuracy is overstated.** — *Fixed.* `ephem.iers_provenance` archives the
table version, its measured and predicted coverage and the values used (`outputs/validation/iers_provenance.json`);
the paper states the ~1 s (≈15″) bound for 2028 and its irrelevance for hour-scale planning.

**GE-17 · MODERATE · Validation prose claims unperformed checks.** — *Fixed.* `scripts/validate_ephemeris.py` computes
every residual it reports, applies thresholds and fails on regression (`ephemeris_validation.json/.md`); the 2029
part is reported as an internal consistency check only.

**GE-18 · MINOR · Retarded barycentric conventions are conflated.** — *Fixed.* Sub-Earth points are compared
like-for-like with Horizons' astrometric convention (agreement ~10⁻⁵°) and sub-solar points with the aberrated
retarded direction; the geometric convention used in the screening differs by ≤0.006°.

**GE-19 · MODERATE · Impact and reception times are not distinguished.** — *Fixed.* `geometry.light_time_s` solves the
one-way light time; station geometry uses the lunar state at emission and the observer at reception; cards store the
impact time in UTC and TDB and each station's reception time.

**GE-20 · MINOR · The geocentre is displaced by 7.137 km.** — *Fixed.* Geocentric card quantities use the zero
observer vector (`geometry.geocentric_surface_geometry`).

**GE-21 · MODERATE · Orbiter illumination windows are not reproducible.** — *Addressed within scope.* The windows are
relabelled "approximate orbit-plane illumination seasons" with their provenance and limits in `config/orbiters.yaml`
(node history and fit not archived; ±3 weeks is a model spread; a season does not guarantee a sunlit pass). The raw
history could not be re-queried from the analysis environment.

**GE-22 · MODERATE · Orbiter latency combines unlike events (consolidates ST-15).** — *Fixed.*
`research/orbiter_latency.csv` adds the event class, the first-image bound (LADEE is an upper bound), the Vikram
confirmation at 87 days and release notes; impacts and context events are separated in the figure and in the
summaries, and release latency is counted from the event.

**GE-23 · MINOR · Plume shadow-height numbers in the configuration contradict each other.** — *Fixed.*
`config/domain.yaml` gives the band 0.5–6° beyond the terminator and the corresponding heights 0.066–9.57 km.

**GE-24 · MODERATE · Seasonal closures are applied in the screening but not in the Monte Carlo.** — *Fixed.* One shared
availability function (`screening.observer_availability`) with geometric and operational parts is used by the
screening, opportunity statistics, refinement and scenarios.

**GE-25 · MINOR · Orbital speed is called ground speed.** — *Fixed (wording).* 1.6335 km/s orbital speed versus
1.5446 km/s sub-spacecraft speed over the reference sphere (paper Section 5.3).

## Physics (PH)

**PH-01 · MAJOR · The Housen–Holsapple cumulative ejecta equation is incorrect.** — *Fixed.* `ayap1obs/plume.py`
implements v(x)/U = C1[(x/a)(ρ/δ)^ν]^(−1/μ)(1 − x/(n2R))^p and M(<x) with the complete Table 3 parameter sets (as
reproduced by Hirata & Ikeya 2021 and Cheng et al. 2020).

**PH-02 · MAJOR · Point-source scaling is used outside its speed domain.** — *Fixed.* Speeds above v(n1a) return
"cannot determine"; the arbitrary cap and the oblique-velocity floor are removed; two oblique-impact rules bracket the
grazing case.

**PH-03 · MAJOR · Plume contrast omits the scattered background.** — *Fixed.* `plume_detectability` uses the total
background of `detect.total_background_sb` and a coherent subtraction systematic.

**PH-04 · MAJOR · Cumulative fast ejecta mass is treated as instantaneous.** — *Fixed.* Phase-space model: particles on
two-body trajectories (RK4), sunlight and visibility tested every 2 s, optical-depth-limited cross-sections and
time-resolved signal-to-noise ratios.

**PH-05 · MAJOR · Plume visibility hard-coded to zero at 30 km.** — *Fixed.* Visibility follows from the per-particle
cylindrical shadow and limb tests.

**PH-06 · MAJOR · Intensity ∝ v³ converted into η ∝ v³.** — *Fixed.* At equal duration and spectrum, intensity ∝ v³
implies η ∝ v; the speed-scaled prior is centred on 10⁻³(v/5 km s⁻¹) and labelled an ad hoc extrapolation; the
Swift et al. (2011) laboratory trend is reported as a separate case.

**PH-07 · MAJOR · The adopted temperature range is presented as measured.** — *Fixed.* A broad log-normal prior chosen to
match the natural-flash statistics (85 % between 2000 and 4500 K; Liakos et al. 2024) with cool and narrow
sensitivity cases, labelled an analogue rather than a spacecraft measurement.

**PH-08 · MODERATE · SMART-1 saturation is a conditional near-infrared limit.** — *Fixed (wording).* The values from
`impact.smart1_saturation_eta` are presented as assumed-camera, assumed-temperature illustrations; "extremely
over-exposed" is no longer read as ten times; the visible prior is not truncated or favoured by them.

**PH-09 · MAJOR · No exposure integration over randomly phased frames.** — *Fixed.* Each camera's candidate frames
around the onset and the band peak are integrated exactly with the tabulated G_b at a random exposure phase.

**PH-10 · MAJOR · Timing uncertainties are unused.** — *Fixed.* One impact-time offset per event (σ_t of the physics
case) shifts every station's geometry through derivatives; recording covers ±15 min.

**PH-11 · MAJOR · Single-site confirmation uses the best band.** — *Fixed.* A dual-camera validation requires both
synchronised cameras ≥15 in the same frame (or both independent MIDAS cameras).

**PH-12 · MAJOR · Field coverage is randomised independently per station.** — *Fixed.* One shared position offset per
event is projected into each station's sky with its Jacobian, plus a per-station pointing error.

**PH-13 · MAJOR · SNR computed where the background saturates.** — *Fixed.* Each camera uses the longest exposure that
keeps the background below half the full well; configurations that still saturate are unavailable.

**PH-14 · MODERATE · Witness percentages omit visibility, weather and terrain.** — *Fixed.* The visual model is
evaluated in the Monte Carlo with the public site's geometry, weather and terrain draw and is reported both
conditional on a clear view and with weather.

**PH-15 · MINOR · Photometry ignores topocentric distance.** — *Fixed.* Each station uses its own range.

**PH-16 · MODERATE · Injection texture without seeing.** — *Fixed.* Per-frame seeing (AR(1) log-normal FWHM) is applied
to the unblurred scene and the injected flash alike, with image motion, full-well clipping and digitisation.

**PH-17 · MODERATE · The analytic aperture SNR is labelled a matched filter.** — *Fixed (wording).* It is described as
an analytic aperture-sum estimate; thresholds are design rules; the injection experiment tests an actual matched
filter.

**PH-18 · MODERATE · The NELIOTA calibration compares different SNR definitions.** — *Fixed (wording).* NELIOTA read
noise 5.1 e⁻; the analytic SNR at R = 12.41 is reported as a consistency check against the quoted SNR 2.5, with the
distinction between theoretical sensitivity, faintest observed and faintest validated flash.

**PH-19 · MAJOR · The site's ladder compares peak flashes with steady limits.** — *Fixed.*
`montecarlo.ladder_probabilities` integrates each camera's randomly phased exposures; the site ladder uses it, and
eye methods use the visual-threshold model.

**PH-21 · MODERATE · The crater check mixes tuning and assumed impacts.** — *Fixed.* No parameter is tuned; the
comparison uses only GRAIL, LADEE and the Falcon 9 stage (published mass, speed and angle) as an out-of-sample check
(`outputs/tables/ejecta_checks.json`, paper Figure "ejecta and crater").

**PH-22 · MODERATE · Crater constants and radius conversion.** — *Fixed.* LPI theory-document constants (K1 0.132,
Kr 1.4/1.1, rim factor 1.3) and the HH2011 radius scaling, with the warning not to mix the University of Washington
constants.

**PH-23 · MODERATE · GRAIL gas-plume detections reduced to a disputed report.** — *Fixed.* The LAMP Lyman-α and 185-nm
detections (Retherford et al. 2013) are listed as an orbital spectral detection, separate from ground dust and flash
searches.

**PH-24 · MODERATE · A primary Kaguya record exists.** — *Fixed.* The comparator table cites the ESA observation page
(AAT/IRIS2, 2.3 µm, 1-s exposures at 0.6-s intervals, one frame; Mount Abu reports), launch mass 2900 kg; impact mass
and emitted energy remain uncalibrated.

**PH-25 · MODERATE · Sheward's daytime sensitivity is misreported.** — *Fixed.* Sheward et al. (2024, MNRAS 529, 3828)
is cited for a confirmed night-time SWIR flash (J = +3.19) and for estimated daytime thresholds (J +3.4 to +5.6), not
for daytime detections.

**PH-26 · MODERATE · The phased-flash helper integrates an exposure before the impact.** — *Fixed.* Exact overlap
integral with the exposure clipped at the onset.

**PH-27 · MINOR · `peak_magnitude` returns the onset value.** — *Fixed.* It returns the true band maximum and its time.

**PH-28 · MINOR · tau_opt has the wrong dimensions.** — *Fixed.* The plume model limits each cell's scattering area by
its optical depth, A(1 − e^(−τ)).

**PH-29 · MINOR · The constant-light limit is stated incorrectly.** — *Fixed (wording).* The paper states the
short-exposure limit t_e ≪ τ and the long-exposure limit separately.

**PH-30 · MINOR · The 2π convention is described as a physical surface.** — *Fixed.* Labelled a convention-only
sensitivity; invalid `solid_angle` values raise an error.

**PH-31 · MODERATE · Earthshine derivation and Rayleigh terminology.** — *Fixed.* The Earthshine background is a
declared normalisation (13.1 mag arcsec⁻² at full Earth, Lambert phase law, ±0.5 mag epistemic offset; observed range
+12 to +17); the incorrect derivation and the Rayleigh "reddening" wording are removed.

**PH-32 · MODERATE · Universal absence of measured efficiency below 2.4 km/s is not established.** — *Fixed (wording).*
The scoped statement is used: no calibrated visible-band efficiency transferable to AYAP-1's regime has been
established; the Burchell et al. (2010) laboratory simulation obtained no flash magnitude (abstract).

## Statistics, social science and reproducibility (ST)

**ST-01 · MAJOR · No numerical precision or uncertainty.** — *Fixed.* Pooled probabilities with 95 % Monte Carlo
intervals from the outer-draw means, 5–95 % epistemic ranges, results by efficiency bin and paired differences (paper
Tables "probabilities" and "strategies").

**ST-02 · MODERATE · Weather Beta uncertainty is mislabelled.** — *Fixed.* The Beta draws are epistemic (outer loop) and
described as such.

**ST-03 · MODERATE · Latent correlation described as nearly perfect.** — *Fixed (wording).* For 100 km and p = 0.5 the
indicator correlation is 0.61 (`weather.indicator_correlation`).

**ST-04 · MODERATE · Weather priors mix definitions.** — *Fixed.* Each statistic carries its definition and a
definition-dependent range (`ayap1obs/weather.py`).

**ST-05 · MAJOR · Population sums are not a lower bound.** — *Fixed.* `ayap1obs/population.py` sums GeoNames settlement
populations at their own coordinates, merges duplicates within 10 km (0 and 25 km as a range) and labels the result a
settlement sum, not a census, bound or audience.

**ST-06 · MODERATE · City geometry at cell centres.** — *Fixed.* Exact coordinates; the number reclassified relative to
the old grid is reported in each card.

**ST-07 · MODERATE · Ten-trial injection curves.** — *Fixed.* 100 trials per 0.25-mag step, Wilson intervals, a
monotone logistic fit and bootstrap intervals for m50 and m90.

**ST-08 · MAJOR · Untested coincidence false-alarm extrapolation.** — *Fixed.* False alarms are counted in 3000-frame
blank sequences over the whole field and, for the twin cameras, as same-frame coincidences, with exact Poisson
intervals and no area or independence extrapolation.

**ST-09 · MODERATE · The "running median" was not causal.** — *Fixed.* Causal reference (median of the previous 25
registered frames) after sub-pixel registration.

**ST-10 · MODERATE · Pareto figure counts self-confirmation as two sites.** — *Fixed.* Two sites and dual-camera
validation are separate outcomes; "confirmed" is their union and labelled as such.

**ST-11 · MODERATE · Resource weights presented as telescope time.** — *Fixed (wording).* Illustrative, dimensionless,
author-elicited weights summed over recruited and available stations.

**ST-12 · MODERATE · Nondominance not computed.** — *Fixed.* `outputs/tables/strategy_nondominance.csv`: joint
nondominance within each scenario across P(two sites), P(live), P(Türkiye detection) and the recruited weight, with
paired 95 % intervals.

**ST-13 · MODERATE · The calendar merges separate sessions.** — *Fixed.* `scripts/make_windows_calendar.py` splits
sessions and refines their boundaries on a 5-min grid.

**ST-14 · MODERATE · Launch statements forced into one quarter.** — *Fixed.* The statements are quoted separately
("first months", "first half", "Q2"); a February launch family (L0) is added and the domain starts on 2027-05-01.

**ST-16 · MODERATE · Fischer citation.** — *Fixed.* Heather A. Fischer, Victoria Sellers and Martin Storksdieck,
"Harnessing the awe of eclipses to enhance science engagement", Front. Astron. Space Sci. 12:1662996 (2025).

**ST-17 · MODERATE · Eclipse retention benchmark.** — *Fixed.* The initial report (215 million; 2834 and 2211
respondents) and the final release (216 million; 2175 August and 2212 third-wave respondents; information seeking
at the pre-eclipse rate) are cited separately.

**ST-18 · MODERATE · Awe averages and Turkish reliability.** — *Fixed.* Recruitment, opt-in, follow-up, item and paired
Ns are given separately (14 % is our derived value); the TISP Turkish sample is N = 508 and α = 0.93 is a global
estimate.

**ST-19 · MODERATE · Sample size omits multiplicity.** — *Fixed.* One primary estimand; Holm-powered secondary family
(584 per group at α = 0.01 for d = 0.2); conservative baseline correlations; clustering and weighting sensitivity.

**ST-20 · MODERATE · Immediate outcomes measured at different times.** — *Fixed.* Same short T1 within two hours and a
standardised 24-h follow-up in every arm; elapsed time, mode and intervening announcements recorded.

**ST-21 · MODERATE · Causal estimands undefined.** — *Fixed.* Associational cohort estimand; causal claims reserved for
the randomised presentation comparison; assumptions and an extra pre-event wave required for any causal contrast.

**ST-22 · MODERATE · EU hosting treated as adequate.** — *Fixed.* Article 5 bases, Article 6 special categories and
Article 9 transfer mechanisms described; foreign services only after institutional review of the specific mechanism.

**ST-23 · MAJOR · The checker passes with missing products.** — *Fixed.* `scripts/check_reproduction.py` requires an
explicit product list, fails on missing products, verifies the data manifest and tests injection and website values.

**ST-24 · MODERATE · Stale checksum manifest.** — *Fixed.* `scripts/make_release_manifest.py` regenerates
`MANIFEST.sha256`, `data/DATA_MANIFEST.sha256` and `outputs/validation/release_manifest.json` after the PDF.

**ST-25 · MODERATE · Data-bearing dependencies unpinned.** — *Fixed.* All packages pinned (including
astropy-iers-data, geonamescache, scikit-image, pyshp, PyYAML); the release manifest hashes the GeoNames table, the
lunar texture and the IERS table actually loaded.

**ST-26 · MODERATE · Verified-source language exceeds the archive.** — *Addressed within scope.*
`research/audit_2026-10_sources.md` records the sources checked for the corrections with status labels (read on the
page, read in a reproduction, derived, not verified); unrecorded titles are marked in the bibliography; the paper no
longer calls helper-extracted facts "verified". Page snapshots and quotation hashes are not archived (stated as a
limitation).

## Website (WB)

**WB-01 · MAJOR · Calendar criteria do not describe the calendar.** — *Fixed.* One named criterion
(`config/domain.yaml: criteria.calendar`) generates the calendar, and the caption is filled from `calendar.json`.

**WB-02 · MODERATE · The animation claims accurate size and duration.** — *Fixed (wording).* "Illustration only" note
in both languages; no calibrated renderer is attempted.

**WB-03 · MODERATE · Categorical visible/not-visible verdict.** — *Fixed.* "Above/below the assumed brightness
threshold", conditional-result note, and exposure-integrated ladder probabilities.

**WB-04 · MODERATE · Broad-band phone limits labelled V (consolidates PH-20).** — *Fixed.* Phone methods are exported
and compared in the broad band; the physics figure shows them on a separate broad-band panel.

**WB-05 · MODERATE · Earth-map shading read as impact visibility.** — *Fixed.* Titled as sky conditions; an occultation
note appears when the point is hidden; station markers include the point's visibility; the location check says what
it covers.

**WB-06 · MODERATE · Heat display hides smoothing and clipping.** — *Fixed.* Legends state the exact interval,
percentile clipping, ~4° smoothing and the geometric nature of the layer.

**WB-07 · MODERATE · Far-side control given an expected brightness.** — *Fixed.* "Not observable from Earth", with the
unocculted source-equivalent value labelled as such.

**WB-08 · MODERATE · LRO survival shown as an imaging probability.** — *Fixed.* The assumed operating probability and
the heuristic latency are separate statements.

**WB-09 · MODERATE · The live page does not poll in planning/announced states.** — *Fixed.* `event.json` is re-read
every minute in every state (live page) and every five minutes on the home page, which also refreshes the "Moon now"
view.

**WB-10 · MODERATE · Switching to the example leaves the old time.** — *Fixed (release 1.0.2).*

**WB-11 · MODERATE · Categorical public copy.** — *Fixed (wording).* Duration "expected to be brief, uncertain";
binocular detection "very unlikely under these assumptions"; loss of signal versus impact confirmation distinguished.

**WB-12 · MODERATE · Legacy figures.** — *Fixed.* Every figure in `outputs/figures` and `site/assets/figures` is
regenerated by the release-2 pipeline; no legacy output tree is distributed.

**WB-13 · MINOR · Truncated timestamps.** — *Fixed.* Calendar times are built from exact integer offsets and rounded to
the grid.

**WB-14 · MODERATE · UTC date with Istanbul time.** — *Fixed.* Full ISO timestamps in UTC and Europe/Istanbul are
exported and rendered.
