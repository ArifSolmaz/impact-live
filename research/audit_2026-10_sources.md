# Sources checked for the audit corrections (October 2026)

Retrieved 7 October 2026 with a page-reading tool that passes page text through a summarising model; short
quotations are as returned by that tool and should be spot-checked against the source before they are quoted in
print. General web search and several publisher sites were unavailable from the analysis environment (listed at
the end), so some values come from later papers that reproduce the original tables; this is stated where it applies.
Data servers for terrain (PDS Geosciences), JPL Horizons, NASA POWER and the JRC population grids could not be
reached from either the cloud environment or the linked computer.

Status labels: **[V]** read on the page; **[V-rep]** read in a later paper that reproduces the original;
**[D]** derived by us from verified values; **[U]** not verified.

**Quotation ledger (release 2.1, re-audit ST-26).** `research/quotations.csv` lists every quotation from an external
source that the manuscript, these notes or the code reuse: the text as printed, the original wording (with a SHA-256
of it), the source, publication and access dates, how it was retrieved, whether it is a direct quotation, a
shortened quotation or our translation, and any correction made in release 2.1. `python3 scripts/check_quotations.py`
(`make quotes`) confirms that each printed text occurs where the ledger says it is used. Raw page snapshots are not
archived (the page-reading tool returns processed text, not the original bytes), so the ledger fixes what was
extracted and where it is used, but cannot by itself prove the source wording; rows marked 'V-tool' should be
spot-checked against the source before print. Statements that nothing was found describe the stated search, not
proof that no such study exists.

## Ejecta and crater scaling

- **Housen & Holsapple (2011), Icarus 211, 856–875, doi:10.1016/j.icarus.2010.09.017.** Equations reproduced as
  LaTeX in Raducan, Davison & Collins (arXiv:2105.01474, Eqs. 1–5) **[V-rep]**:
  - v(x)/U = C1 [(x/a)(ρ/δ)^ν]^(−1/μ) (1 − x/(n2 R))^p, valid for n1 a ≤ x ≤ n2 R, n1 ≈ 1.2
    ("invalid for very fast ejecta, where r < n1 a").
  - M(<x)/m = (3k/4π)(ρ/δ)[(x/a)³ − n1³].
  - Gravity regime: R(ρ/m)^(1/3) = H1 (g a/U²)^(−μ/(2+μ)) (ρ/δ)^((2+μ−6ν)/(3(2+μ))).
  - Strength regime: R(ρ/m)^(1/3) = H2 (Y/(ρU²))^(−μ/2) (ρ/δ)^((1−3ν)/3).
- **HH2011 Table 3** as reproduced in Hirata & Ikeya (2021), Icarus 364, 114474, arXiv:2205.06607, Table B1, and
  cross-checked against Cheng et al. (2020), Icarus 352, 113989, arXiv:2007.15761, Table 3 **[V-rep]**
  (columns: regime, μ, k, C1, H1, H2, n2, p, ρ [kg m⁻³], Y [MPa]; ν = 0.4 and n1 = 1.2 throughout per the Cheng
  et al. footnotes):
  - C1 water: G, 0.55, 0.2, 1.5, H1 0.68, –, 1.5, 0.5, 1000, –
  - C2 rock/basalt: S, 0.55, 0.3, 1.5, –, H2 1.1, 1.0, 0.5, 3000, 30
  - C3 weakly cemented basalt: S, 0.46, 0.3, 0.18, –, H2 0.38, 1.0, 0.3, 2600, 0.45
  - C4/C5 sand: G, 0.41, 0.3, 0.55, H1 0.59, –, 1.3, 0.3, 1600 / 1510, –
  - C6 glass micro-spheres: G, 0.45, 0.5, 1.0, H1 0.8, –, 1.3, 0.3, 1500, –
  - C7 sand/fly ash: S, 0.40, 0.3, 0.55, –, H2 0.40, 1.0, 0.3, 1500, 4×10⁻³
  - C8 perlite/sand: S, 0.35, 0.32, 0.60, –, H2 0.81, 1.0, 0.2, 1200, 2×10⁻³
  - Experimental conditions (Cheng et al.): porosity sand 35 %, sand/fly ash 45 %, perlite/sand 60 %.
- **Holsapple, "Craters from Impacts and Explosions" (crater-calculator theory),
  https://www.lpi.usra.edu/lunar/tools/lunarcratercalc/theory.pdf** **[V]**: K1, K2, μ, ν, Y (dyn cm⁻²), ρ (g cm⁻³):
  dry sand 0.132, 0, 0.41, 0.33, 0, 1.7; dry soil 0.132, 0.26, 0.41, 0.33, 2×10⁶, 1.7; lunar regolith 0.132, 0.26,
  0.41, 0.33, 1×10⁵, 1.5; wet soil 0.095, 0.35, 0.55, 0.33, 5×10⁶, 2.1; soft rock 0.095, 0.215, 0.55, 0.33, 1×10⁷, 2.1;
  hard rock 0.095, 0.257, 0.55, 0.33, 1×10⁸, 3.2. Shape: "R = Kr V^(1/3)", Kr = 1.4 (dry sand), 1.1 (dry soils,
  soft rock). "The rim diameter is assumed to be 1.3 times the excavation diameter." Warning for impact speeds below
  1 km/s ("the point source assumption becomes iffy"). A University of Washington version of the same document
  (keith.aa.washington.edu/craterdata/scaling/theory.pdf) lists different constants (e.g. lunar regolith K1 0.15,
  Y 10⁶ dyn cm⁻²); the two sets must not be mixed.
- **LCROSS.** Centaur mass at separation 2271.61 kg, speed 2.506885 km/s, 85.917° from horizontal (Marshall et al.
  2012, Space Sci. Rev. 167, arXiv:1103.1687) **[V]**. Total illuminated plume mass "2,240 ± 400 kg" at 20 s after
  impact, versus "3,150 ± 790 kg" from the shepherding-spacecraft spectrometer for 0–23 s; conversion assumes "average
  particle radius of 2.5 μm and a particle density of 3,000 kg m⁻³ … regolith albedo of 0.17"; low-angle plume speeds
  "up to 500 m s⁻¹" (Strycker et al. 2013, Nat. Commun. 4:2620) **[V]**. Sunlight horizon ~830 m (Hermalyn et al.
  2010, LPSC 41 #2095) **[V]**; hollow projectiles "form an early-stage high angle plume of high speed fine material".
- **Oblique impacts.** Below 5°, "nearly intact ricochet … with velocities close to original impact velocity";
  5–15°, "disruption dominated by 5–10 large fragments retaining about 50 percent of original velocity" (Schultz &
  Gault 1990, GSA Spec. Pap. 247) **[V, abstract]**; shallow impacts "lead to ricochet … at velocities only slightly
  reduced" (Gault & Wedekind 1978) **[V, abstract]**; downrange ejecta mass up to ~8× uprange at 40° (Quillen &
  Doran, arXiv:2404.16677) **[V]**.
- **SMART-1 laboratory simulation** (Burchell, Robin-Williams & Foing 2010, Icarus 207, 28–38): scaled crater
  0.71–6.9 m³; "0.64–6.3 m³ would have been ejecta on ballistic trajectories corresponding to a cloud of
  2200–21,800 kg"; "the flash magnitude was not obtained, so it is not possible to obtain the luminous efficiency"
  (abstract, https://kar.kent.ac.uk/37222/) **[V]**.
- **Regolith grain size.** "The median particle size is 40 to 130 µm, with an average of 70 µm"; "Roughly 10% to 20%
  of the soil is finer than 20 µm" (Lunar Sourcebook ch. 9) **[V]**.

## Luminous efficiency and flash properties

- **Ernst & Schultz (2002), LPSC 33 #1782** **[V]**: Pyrex spheres into pumice dust, 4.05–5.76 km/s, 30–90°,
  photodiode 350–1100 nm; intensity ∝ v³; intensity ∝ cos θ. No luminous efficiency is given. Ernst, Barnouin &
  Schultz (2011, LPSC #2299): power law only above ~4 km/s; below ~3 km/s peak intensity decreases with velocity.
- **Swift et al. (2011), NASA NTRS 20110016594** **[V]**: Pyrex into JSC-1a at 2.4–5.75 km/s, 15–90°; total emission
  over all frames; η = C exp(−Vc²/V²), Vc = 9.3 km/s, C = 1.5×10⁻³. **[D]** Evaluated at 2.4 km/s this gives
  ≈4×10⁻¹⁰; extrapolated to 1.68 km/s it gives ≈7×10⁻¹⁷ (outside the tested range).
- **Flash temperatures.** Avdellidou & Vaubaillon (2019), MNRAS 484, 5212 (arXiv:1902.00987): "approximately 1,300 and
  5,800 K"; Gaussian fit T0 = 2550 K, σ = 600 K with a high-temperature tail **[V]**. Liakos et al. (2024), A&A 687,
  A14: "85% of the peak temperatures of the impacts range between 2000 and 4500 K" **[V]**. Liakos et al. (2020), A&A
  633, A112: ~65 % between 2000 and 3500 K, extremes 1758 and 5722 K **[V]**. Bonanos et al. (2018), A&A 612, A76:
  ~1600–3100 K for the first ten flashes **[V]**.
- **NELIOTA sensitivity** (Xilouris et al. 2018, A&A 619, A141): "SNR = 2.5 level of 12.39 mag in the I-band and 12.41
  mag in the R-band for observations made at low lunar phase (~0.1)"; 23 ms exposures at 30 fps; Andor Zyla 5.5 sCMOS in
  2×2 binning (0.8″ px⁻¹, 17.0′×14.4′); read noise 5.1 e⁻ rms; faintest first-year flash R = 11.24 at phase 0.32
  **[V]**. Liakos et al. (2020): validation requires detection "in the frames of both cameras and on exactly the same
  lunar area" and no motion between frames; faintest validated flash R = 11.94 **[V]**.
- **Sheward et al. (2024), MNRAS 529, 3828, doi:10.1093/mnras/stad2707** **[V]**: one confirmed short-wave infrared flash
  observed at night (J = +3.19 ± 0.18, 2023-01-26), confirmed by visible observers; daylight detection threshold
  estimated as J = +3.4 to +5.6 (V = +4.5 to +6.7 at 2750 K) from daytime backgrounds — an estimate, not a daytime
  detection.
- **Kaguya (10 June 2009).** AAT/IRIS2, "narrow band filter centred at 2.3 µm … 1 second exposures with 0.6 seconds
  intervals"; the flash is in one frame (ESA, sci.esa.int/web/smart-1/-/44977) **[V]**. ESA also notes reports from Mount
  Abu Observatory and a "2-tonne dry mass" **[V]**. Launch mass 2,900 kg (NASA) / 2,885 kg including propellant and the
  two subsatellites (NSSDCA) **[V]**. Impact speed and angle not verified **[U]**.
- **SMART-1 (3 Sep 2006).** CFHT/WIRCam, 10 s exposures with ~5 s gaps; "extremely over-exposed … very difficult to
  estimate the magnitude" (Veillet & Foing 2007, LPSC #1520) **[V]**; filter 2130 nm/~40 nm (LPSC) versus 2122 nm/32 nm
  (CFHT news page) **[V, both]**; ~2 km/s at ~1° grazing (ESA); 366–367 kg at launch; mass at impact not verified **[U]**.
- **GRAIL plumes** (Retherford et al. 2013, LPSC #3004): LAMP detected "excess emission signatures at 185 nm and at
  Lyman-alpha (121.6 nm)" from Hg and H in the plumes; no flash is reported **[V]**.

## Detection, vision, backgrounds

- **Visual thresholds** (Crumey 2014, MNRAS 442, 2600, arXiv:1405.4209) **[V]**: ΔI = F (r B^{1/4} + r′ B^{1/2})² with
  Blackwell constants r1 = 6.505×10⁻⁴, r2 = −8.461×10⁻⁴ (scotopic) and r3 = 1.772×10⁻⁴, r4 = 7.167×10⁻⁵ (photopic),
  split at B = 7.08×10⁻² cd m⁻²; μ_V = 12.58 − 2.5 log B; field factor F typically 1.4–2.4 (F = 2 typical); 90 %
  detection at 1.62× the 50 % contrast. The paper concerns unlimited viewing time; Bloch-law temporal summation
  (~50 ms) is from the vision literature (Gorea 2015, i-Perception 6(4)).
- **Earthshine.** "variations between +12 and +17 mV arcsec² with hourly changes" (Montañés-Rodríguez, Pallé & Goode
  2007, AJ 134, 1145; not Johnson V) **[V]**; Earthshine/sunshine ratio ~10⁻⁴ near new Moon (Pallé et al. 2003, JGR 108,
  4710) **[V]**.
- **Sunlit Moon.** Full-Moon V ≈ −12.74, mean surface brightness ≈ 3.4 mag arcsec⁻² **[D]** (NASA fact sheet;
  Krisciunas & Schaefer 1991, PASP 103, 1033).

## Mission and orbit

- **Launch target wording.** TUA, 16 Sep 2026: "2027 yılının ilk aylarında fırlatılması hedeflenen …", ~two-month
  transfer, 100 km polar circular orbit, at least three months extendable to 1.5 years, controlled end on the
  surface **[V]**. TÜBİTAK UZAY, 14 Sep 2026: "2027 yılının ilk yarısında" **[V]**; programme page: "2027 Q2" **[V]**;
  Minister (AA, 5 Oct 2026): "Gelecek yılın ilk aylarında" **[V, single extraction]**. The statements differ.
- **Low lunar orbit lifetime.** Genova (2026), "Linking Lunar Orbital Dynamics to Planetary Protection Policy", NTRS
  20260002233: 100 km circular orbits, 100×100 gravity field, inclinations 80–95°: "91 orbits (out of 151) impact the
  lunar surface within 2-yrs"; survivors at ~83–87° and ~93–95°; minimum lifetime 168 days **[V]**. Ramanan &
  Adimurthy (2005), J. Earth Syst. Sci. 114, 619: 100 km polar orbit lifetime ~160 days with LP100J **[V]**.

## Social study and data protection

- **Fischer, Sellers & Storksdieck (2025)**, "Harnessing the awe of eclipses to enhance science engagement", Front.
  Astron. Space Sci. 12:1662996: 1,328 completed a survey or interview (Table 1 totals 1,310); awe on the day 8.7/10
  (n = 501); paired test n = 79; follow-up 188 of 700 who agreed (27 %); "14 %" is not stated in the paper (188/1,328
  is derived) **[V]**.
- **ISR eclipse reports (J. D. Miller).** Initial report (2 Oct 2017): 215 million adults, 2,834 in wave 1 and 2,211 in
  the August wave **[V]**. Final report release (15 Aug 2018): 216 million; August wave 2,175; third wave (from October
  2017) 2,212; information seeking ~16 times in the three months after the eclipse, essentially the pre-eclipse rate
  **[V]**.
- **TISP** (Mede et al. 2025, Sci. Data 12, 114; PDF supplied by the author): Table 1 lists "Türkiye | Turkish |
  Bilendi & respondi | 508" **[V]** (the earlier note of 1,020 was the next row, Ukraine). Cronbach's α = 0.93 and
  ω = 0.95 are "in the global sample" **[V]**; no Turkey-specific reliability is reported, and the paper notes that
  respondents from Türkiye often failed attention checks **[V]**.
- **KVKK (Law 6698, as amended by Law 7499, 2024)**, consolidated text via Lexpera **[V]**: Art. 5 — explicit consent
  or one of the listed alternative bases; Art. 6 — special categories (including political opinion and religion)
  may be processed only under the listed conditions, including explicit consent; Art. 9 — transfers abroad require an
  adequacy decision or an appropriate safeguard (standard contract notified to the Authority within five business
  days, binding corporate rules, or a written undertaking with Board permission), or an incidental-transfer exception.

## LRO follow-up precedents

Image times from LROC pages and the LROC data-product pages (data.lroc.im-ldi.com) **[V]**: GRAIL first NAC image
28 Feb 2013 (≈73 d); LADEE image M1163066820R on 19 Aug 2014 05:52 UTC (≈123 d; the page does not say it was the first);
Beresheet 22 Apr 2019 01:47 UTC (≈10.3 d); Longjiang-2 5 Oct 2019 (≈66 d); unidentified rocket body ("The identity of
the rocket body remains unclear") after-image 21 May 2022 (≈78 d); HAKUTO-R M1 first of ten images 26 Apr 2023 01:07 UTC
(≈0.35 d), change-detection image 06:59 UTC (≈0.6 d); Luna 25 24 Aug 2023 18:15 UTC (≈5.3 d), NASA release 31 Aug 2023;
ispace M2 11 Jun 2025 23:23 UTC (≈6.2 d); Falcon 9 stage crater 11 Aug 2026 (6 d; Danuri imaged it "a few hours" after
impact). Vikram: first mosaic acquired 17 Sep 2019 (released 26 Sep) did not identify the site; debris confirmation
released 2 Dec 2019 (≈87 d after the event).

## Not reachable from the analysis environment

General web search (blocked for the organisation); ScienceDirect, IOPscience, NASA ADS full text, arXiv search/API,
science.org, Wiley/AGU, ESA main site (esa.int), JAXA press index, kvkk.gov.tr, mevzuat.gov.tr, resmigazete.gov.tr,
nature.com (rate-limited on the second request); data servers pds-geosciences.wustl.edu, ssd.jpl.nasa.gov,
naif.jpl.nasa.gov, power.larc.nasa.gov, jeodpp.jrc.ec.europa.eu.
