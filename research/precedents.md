# Comparator evidence: observed artificial lunar impacts, flash calibration and crater sizes

Prepared for the AYAP-1 terminal-impact observation paper. Evidence cutoff 5 October 2026; every URL accessed 2026-10-05.
Companion file: `precedents.csv` (one row per event x observing facility, 15 columns, same content as the per-event tables in section (a)).

## How to read this file

**Verification tags** (used in every table):

- **[V]**: verified in a primary or official source fetched for this work (paper, conference abstract, mission-team post, agency page).
- **[S]**: secondary source fetched (Wikipedia, or a statement quoted inside another paper).
- **[R]**: statement made in a review or forecast paper (mostly Fernando et al. 2026), not checked against its original.
- **[U]**: unverified. The value comes from the task brief or memory, or the source could not be retrieved. Treat it as a placeholder.
- **[C]**: computed here. Lunar geometry uses astropy's built-in ephemeris plus the IAU 2009 (Archinal et al. 2011) lunar rotation model. Checked against a JPL Horizons query for 2026-08-05 06:35 UTC: sub-Earth point 354.5134E/-5.9928 vs Horizons 354.5136E/-5.9932; sub-solar 275.3307E vs 275.3324E; illuminated fraction 59.29% vs 59.29%. Some event times are approximate (marked [U]); minute-level errors change these angles by <0.01 deg.

**Geometry fields.** "x deg from sub-Earth pt" is the selenocentric angle between the site and the geocentric sub-Earth point: under 90 deg means the site faces Earth, about 90 deg is on the limb, and topocentric parallax shifts this by up to ~1 deg. SZA is the smooth-sphere solar zenith angle: over 90 deg is local night. It ignores local topographic shadow, such as the permanently shadowed regions (PSRs). "Moon x% lit" is the illuminated fraction seen from Earth.

**Limits of this search.** WebSearch was disabled. Several key full texts could not be read because the hosts blocked the fetcher (robots rules, HTTP 403) or rate-limited it (HTTP 429): ScienceDirect/Elsevier, Science (science.org), Wiley/AGU, PubMed (reCAPTCHA), NASA ADS, esa.int, the Wayback Machine, JAXA press pages, and the AAO site. Crossref, OpenAlex, Semantic Scholar, Europe PMC and arXiv author pages were often refused with HTTP 429. As a result, the Burchell et al. (2010), Schultz/Colaprete/Gladstone/Hayne (2010), Chanover et al. (2011), Heldmann et al. (2012), Goldstein et al. (1999/2001), Ortiz et al. (2006), Bellot Rubio et al. (2000), Bouley et al. (2012), Suggs et al. (2014), Liakos et al. (2024), Sheward et al. (2024) and Fassett et al. (2024) papers appear only as references, marked [U] or [S]. No numbers have been invented for them.

## Quick-look summary (one line per event)

| Event | UTC | Mass | Speed | Angle from horizontal | Geometry | Earth-based outcome | Orbital outcome | Crater |
|---|---|---|---|---|---|---|---|---|
| SMART-1 | 2006-09-03 05:42:22 | ~285 kg [U] (366 kg launch [V]) | ~2 km/s [V] | ~1 deg [V] | Earth-facing (55 deg), night side, Moon 73% [C] | CFHT 3.6 m WIRCam 2.12 um: flash DETECTED, saturated; dust cloud by differencing [V] | - | scar found 2017 [U] |
| LCROSS Centaur | 2009-10-09 11:31:19.5 | 2271.6 kg [V] | 2.507 km/s [V] | 85.9 deg [V] | PSR; impact pt hidden by 1.8 km hill; Moon 71% [V/C] | No flash in view; plume DETECTED only after PCA (APO V 0.5 s; MRO U 0.034 s); many non-detections [V] | S-SC MIR hot spot + UV/Vis plume [V]; Diviner thermal [S]; LAMP plume [U] | 22 m [R]; model 25-30 m [V] |
| Kaguya | 2009-06-10 18:25 | [U] | ~1.7 km/s [U] | low [U] | near SE limb (87 deg), night, Moon 92% [V/C] | AAT IRIS2 near-IR flash reported [U]; India + Australia [R] | - | - |
| GRAIL Ebb/Flow | 2012-12-17 22:28 | ~130 kg each [V] | ~1.6 km/s [V] | ~2 deg [V] | Earth-facing (85 deg), night, Moon 27% [C] | none found | LAMP plume view [S]; LROC craters [V] | ~5 m each [V] |
| LADEE | 2014-04-18 ~04:30-05:22 | 248 kg [V] | 1.699 km/s [V] | low, westward [V] | geocentric limb (89.7 deg), day [C] | none reported | LROC crater [V] | <3 m [V] |
| Lunar Prospector | 1999-07-31 ~09:52 | 161 kg [U] | ~1.7 km/s [U] | low [U] | beyond limb (92 deg), PSR [C/S] | OH searches (HST, McDonald, Keck): no detection reported [U/R] | - | - |
| Falcon 9 2025-010D | 2026-08-05 06:35 | 4.0-4.9 t [V, conflicting] | 2.43 km/s [V] | ~31 deg [V] | geocentric limb (89.9 deg), sunlit SZA 21 deg, Moon 59% [C] | planned campaign; no published result found [U] | Danuri LUTI + LRO NAC [V] | 18 m, <3 m deep [V] |

## (a) Comparator tables per event

Each event starts with a key-value block of the parameters common to all its rows: mass, speed, incidence angle, target and geometry. The table that follows has one row per observing facility. `precedents.csv` repeats the common parameters on every row.

### SMART-1 (ESA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2006-09-03 05:42:21.759 [V ESA] |
| Impact mass | ~285 kg [U, task brief]; 366 kg at launch [V ESA] |
| Speed | ~2 km/s [V ESA] |
| Incidence (from horizontal) | ~1 deg grazing [V ESA] |
| Material/target assumptions | edge of Lacus Excellentiae; slopes of a mountain near Lehmann C / Drebbel D [V Veillet & Foing 2007] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 34.26S 46.19W (ESA: 34.4S 46.2W); night side ~9 deg past terminator (SZA 99 deg), Earthshine-lit; 55 deg from sub-Earth pt (well placed); Moon 73% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| CFHT 3.6 m / WIRCam (4x HAWAII-2RG, 0.3"/pix ~0.5 km/pix) | H2 1-0 S(1) narrowband: 2122 nm, 32 nm BW [V ESA caption]; abstract says ~2130 nm, 40 nm BW [V Veillet & Foing] | 10 s exposures, ~5 s gaps (~15 s cycle); sequence ~-20 to +40 min | DETECTED flash: saturated/'extremely over-exposed', elongated to S along motion, diffraction spikes; magnitude NOT determined. Ejecta/dust cloud DETECTED 10-20 s after impact, not centred on trajectory | Flash obvious in raw frame (saturated). Ejecta cloud only after pre/post-impact differencing (later analysis) | Veillet & Foing 2007, LPSC 38 #1520 https://www.lpi.usra.edu/meetings/lpsc2007/pdf/1520.pdf ; ESA captions https://sci.esa.int/web/smart-1/-/39964-contour-plot-of-impact-flash , https://sci.esa.int/web/smart-1/-/39968-impact-dust-cloud | conference abstract + agency caption | V |
| Amateur observer, New Mexico (equipment unknown) | unknown | unknown | 'possible detection' of flash (as reported by Veillet & Foing); no published photometry | unknown | Veillet & Foing 2007 (as above) | conference abstract | V (claim reported) / U (detection itself) |
| Other registered participants: ESA OGS Tenerife 1 m & 18 cm; Calar Alto 2.2/3.5 m; TNG 3.58 m La Palma; SAAO; Argentina 0.63 m; Llano del Hato 1.0/0.65 m; Clay Center 0.63 m; Florida Tech 0.8 m; MSFC 0.25 m; MDM 2.4/1.3 m; IRTF 3 m; Subaru auxiliary 0.3 m (400-800 nm); Odin satellite; radio/VLBI (ATCA, Mt Pleasant, Medicina, ROEN, TIGO) | optical/NIR/radio (per site) | not published | No detections published/found; 'most other attempts unsuccessful due to weather and observing geometry' (Veillet & Foing). No quantitative upper limits found | n/a | ESA participating-observatory list https://sci.esa.int/web/smart-1-lunar-impact/39928-participating-observatories ; Veillet & Foing 2007 | agency page (pre-impact list) + abstract | V (list) / U (individual outcomes) |
| Laboratory simulation (Univ. Kent light-gas gun) - Burchell, Robin-Williams & Foing 2010 | n/a | n/a | Lab simulations of the SMART-1 impact; abstract/content NOT retrieved (Elsevier paywall, robots-blocked) | n/a | Burchell et al. 2010, Icarus 207:28-38, doi:10.1016/j.icarus.2009.10.005 | peer-reviewed | U (metadata only) |

### LCROSS Centaur (NASA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2009-10-09 11:31:19.506 [V Marshall et al. 2012] |
| Impact mass | 2271.61 kg at separation [V Marshall 2012]; 2305 kg often quoted [R Fernando 2026] |
| Speed | 2.506885 km/s [V Marshall 2012] |
| Incidence (from horizontal) | 85.917 deg (3.67+/-2.3 deg from local vertical) [V Marshall 2012] |
| Material/target assumptions | Cabeus permanently shadowed regolith; water 6.3+/-1.6 wt% [V Strycker 2013] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 84.6796S 48.7093W; PSR floor in topographic shadow (smooth-sphere SZA 83.5 deg); impact point hidden from Earth behind ~1.8 km foreground hill - plume visible only above that height [V Strycker 2013]; 82.6 deg from sub-Earth pt; Moon 71% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| ARC 3.5 m, Apache Point / Agile frame-transfer CCD (0.26"/pix, 0.46 km) | V + neutral-density filter | 0.5 s frames, 45 min continuous | DETECTED ejecta plume (no flash in view): max 10.0+/-0.1 mag/arcsec^2 at 17-27 s, ~3.6 km altitude; background 6.75 mag/arcsec^2 (3.25 mag brighter); illuminated mass 2240+/-400 kg at 20 s; peak optical depth 0.0018+/-0.0002 | NOT visible in raw frames; PCA filtering of 240 s series (961 components; PCs 1-4 removed), pre/post background subtraction, 2.5 s boxcar, 4x4-pix boxes (later analysis, published 4 yr after) | Strycker et al. 2013, Nat. Commun. 4:2620 https://www.nature.com/articles/ncomms3620 | peer-reviewed | V |
| Magdalena Ridge Obs. 2.4 m / PHOTGJON | U | 0.034 s | DETECTED plume, 9.3 sigma | PCA filtering required (standard differencing/median failed) | Strycker et al. 2023, Remote Sens. 15:37 https://www.mdpi.com/2072-4292/15/1/37 | peer-reviewed | V |
| Magdalena Ridge Obs. 2.4 m / PHOTDOC | U | 0.034 s | DETECTED plume, 6.2 sigma | PCA filtering required | Strycker et al. 2023 (as above) | peer-reviewed | V |
| MMT 6.5 m / CCD47 | 700 nm | 0.079 s | NOT detected (no quantitative limit given in summary) | PCA attempted | Strycker et al. 2023 | peer-reviewed | V |
| NMSU 1.0 m (APO) / StellaCam video | R | video rate | NOT detected | PCA attempted; 8-bit/gamma-corrected video identified as limiting | Strycker et al. 2023 | peer-reviewed | V |
| TMO 0.6 m / Goodrich NIR video camera | NIR | video rate | NOT detected | PCA attempted | Strycker et al. 2023 | peer-reviewed | V |
| HST WFC3 imaging + STIS spectroscopy | WFC3 filter ~300 nm; STIS 210-310 nm | STIS long exposures split into short subexposures; WFC3 3 pairs incl. 45 s exposures, pairs just before/after impact | NOT detected: no OH or other radicals (10 sigma), no obvious ejecta, no glow; OH column upper limit transcribed as '<4x10^5 cm^-2' (helper transcription; check original) | later analysis (preliminary results at LPSC 2010) | Storrs & Colaprete 2010, LPSC 41 #2196 https://www.lpi.usra.edu/meetings/lpsc2010/pdf/2196.pdf | conference abstract | V (numbers flagged) |
| Subaru 8.2 m (Hong et al. 2011) | unverified | unverified | Reported failure to detect plume (as cited by Strycker 2013) | unverified | Hong et al. 2011, cited in Strycker et al. 2013 | peer-reviewed (not retrieved) | S |
| NMSU-NASA MSFC campaign (Chanover et al. 2011) | multiple (unverified) | unverified | Reported non-detection (as cited by Strycker 2013); later reprocessing of APO data gave the 2013 detection | later analysis | Chanover et al. 2011, JGR 116, E08 (not retrieved) | peer-reviewed (not retrieved) | S |
| McMath-Pierce solar telescope, Na exosphere spectroscopy (Killen et al. 2010) | Na D (589 nm) | first ~9 min after impact (details unverified) | DETECTED sodium: ~2 g of Na ejected in the first 9 min; modelled release 0.5-2.6 (1.5+/-1) kg Na assuming 1000 K gas. The only ground 'detection' before 2013, per Strycker 2013 | later analysis (spectral modelling) | Killen et al. 2010, GRL 37, doi:10.1029/2010GL045508 (NTRS abstract https://ntrs.nasa.gov/citations/20110013531) | peer-reviewed (abstract via NTRS) | V (abstract) |
| Palomar Hale 5 m with adaptive optics; amateur telescopes | unverified | unverified | No plume detected ('neither the impact nor its dust cloud could be seen from Earth') | n/a | Wikipedia LCROSS (secondary) https://en.wikipedia.org/wiki/LCROSS | secondary | S |
| Keck, Gemini, IRTF, other campaign telescopes (Heldmann et al. 2012 summary) | unverified | unverified | Campaign summary paywalled; per-site results and upper limits NOT verified | unverified | Heldmann et al. 2012, Space Sci. Rev. 167:93-140, doi:10.1007/s11214-011-9759-y (abstract only) | peer-reviewed (abstract only) | U |
| LCROSS Shepherding S/C: MIR1 thermal camera, NIR2 camera, UV/Vis spectrometer | mid-IR, near-IR, UV/visible | in situ, through S-SC impact 4 min later | Thermal hot spot ~90+/-25 m wide (MIR1); dark region 62+/-20 m, bright ejecta ring 158+/-40 m [V Marshall full text]; NTRS abstract summary gives a '20 m diameter crater surrounded by 160 m diameter ejecta region' (extractions differ; check original); illuminated plume mass 3150+/-790 kg at 0-23 s from UV/Vis (as quoted by Strycker 2013); flash characteristics (Schultz et al. 2010) NOT retrieved | immediate (real-time downlink) + later analysis | Marshall et al. 2012, SSR 167 https://ntrs.nasa.gov/api/citations/20140005563/downloads/20140005563.pdf ; Schultz et al. 2010 Science 330:468 (not retrieved) | peer-reviewed | V (Marshall) / U (Schultz) |
| LRO Diviner radiometer | thermal IR (4 thermal channels) | orbital pass | Thermal signature detected in all four thermal channels (secondary); Hayne et al. 2010 details NOT retrieved | later analysis | Hayne et al. 2010 Science 330:477 (not retrieved); Wikipedia LCROSS | peer-reviewed (not retrieved) + secondary | S |
| LRO LAMP UV spectrograph | far-UV | orbital pass | Plume observed (Gladstone et al. 2010) - details NOT retrieved | later analysis | Gladstone et al. 2010 Science 330:472 (not retrieved) | peer-reviewed (not retrieved) | U |

### LCROSS Shepherding Spacecraft (NASA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2009-10-09 11:35:36.116 [V Marshall 2012] |
| Impact mass | 617.18 kg at separation [V Marshall 2012]; 621 kg often quoted [U] |
| Speed | ~2.5 km/s [V NTRS abstract, Fandozzi et al. 2025] |
| Incidence (from horizontal) | steep (near-vertical) [U] |
| Material/target assumptions | Cabeus PSR, 2.803 km SW of Centaur crater [V Marshall] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 84.719S 49.61W [V Marshall] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| Same assets as for the Centaur (S-SC impact ~4 min later) | - | - | S-SC crater not identified in available imagery (Marshall 2012); no Earth-based detection reported |  | Marshall et al. 2012 | peer-reviewed | V |

### Kaguya/SELENE main orbiter (JAXA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2009-06-10 18:25 [V JAXA] |
| Impact mass | unverified (Wikipedia list gives 1984 kg, apparently not an impact mass) |
| Speed | ~1.7 km/s [U, task brief] |
| Incidence (from horizontal) | low (orbital decay-type) [U] |
| Material/target assumptions | south-eastern near-side highlands [U] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 65.5S 80.4E, 'near side, night time area' [V JAXA]; SZA 101 deg (~11 deg past terminator), 87.4 deg from sub-Earth pt (near SE limb, strongly foreshortened); Moon 92% lit, age 17.3 d [C/V] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| Anglo-Australian Telescope 3.9 m / IRIS2 near-IR camera | near-IR (filter unverified) | unverified | Reported DETECTION of impact flash (task brief); primary publication/AAO report NOT located | unverified | not retrieved (AAO site robots/SSL failure; JAXA press pages 403/blocked) | - | U |
| Professional observatory in India (unnamed) | unverified | unverified | Fernando et al. 2026: flash 'observed from at least two professional observatories in India and Australia' (cites Shirao & Wood 2011, Kaguya Lunar Atlas) | unverified | Fernando et al. 2026, arXiv:2607.14625 https://arxiv.org/abs/2607.14625 | preprint (review statement) | R |

### GRAIL Ebb & Flow (NASA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2012-12-17 14:28 PST = 22:28 UTC (Ebb; Flow ~shortly after) [V LROC] |
| Impact mass | ~130 kg each at impact (arrived ~200 kg, ~70 kg fuel used) [V LROC] |
| Speed | ~1600 m/s [V LROC] (1.68 km/s [S Wikipedia]) |
| Incidence (from horizontal) | ~2 deg [V LROC] |
| Material/target assumptions | unnamed highland massif between Philolaus and Mouchez (near Goldschmidt) [S] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | Ebb 75.609N 333.407E (=26.593W), Flow 75.651N 333.168E [V LROC] (task brief's '26.6E' should read 26.6W); night side (SZA 102 deg), 84.8 deg from sub-Earth pt; Moon 27% lit (waxing crescent) [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LRO LAMP UV spectrograph | far-UV | slit observation of impact | Wikipedia caption: LAMP slit view 'showing the impact and the resulting plume'; primary (Retherford et al.) NOT retrieved. Conflicts with Fernando 2026 statement that no flash/plume detection has been reported for GRAIL | later analysis | Wikipedia GRAIL (secondary); Fernando et al. 2026 (review) | secondary / review | S/R (conflict) |
| LROC NAC (stereo M1116729371LR, 28 Feb 2013) | visible | single post-impact epoch | Two craters ~5 m diameter each; dark, irregularly distributed ejecta, little ejecta to the south | before/after comparison (later analysis) | LROC 'Impact!' 19 Mar 2013 https://lroc.im-ldi.com/images/596 | mission team post | V |
| Ground-based | - | - | No ground-based attempt or result found | - | - | - | U |

### LADEE (NASA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2014-04-18, between 04:30 and 05:22 UT [S Wikipedia] |
| Impact mass | ~248 kg [V LROC] |
| Speed | 1699 m/s [V LROC] |
| Incidence (from horizontal) | low angle, heading west (value not given) [V LROC] |
| Material/target assumptions | eastern rim of Sundman V crater (highlands) [V LROC] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 11.8494N 266.7507E (=93.25W) [V LROC]; geocentrically on the limb (89.7 deg from sub-Earth pt), sunlit (SZA ~54 deg); Moon 90% lit [C]; described as far side by NASA [S] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (ratio of M1163066820RE / M1101816767RE) | visible | - | Crater <3 m (models predicted ~1.8 m); V-shaped ejecta to NW, bright material >200 m W, minor SE ejecta 20-30 m; 295 m N of predicted location | before/after ratio images (later analysis) | LROC 'LADEE Impact Crater Found!' 28 Oct 2014 https://lroc.im-ldi.com/images/822 | mission team post | V |
| Ground-based | - | - | None reported/found (limb/far-side geometry) | - | - | - | U |

### Lunar Prospector (NASA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 1999-07-31 ~09:52 UT [U] |
| Impact mass | 161 kg [U task brief]; Wikipedia list 126 kg [S] |
| Speed | ~1.7 km/s [U] |
| Incidence (from horizontal) | low [U] |
| Material/target assumptions | permanently shadowed crater near south pole (cold trap) [U/S] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 87.7S 42.35E [S Wikipedia]; ~91.8 deg from sub-Earth pt (impact point beyond limb; only material rising above limb observable); smooth-sphere SZA ~89.5 deg (PSR); Moon 91% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| HST, McDonald, Keck and others (Goldstein et al. 1999 GRL; 2001) | OH 308-309 nm UV emission (and others) [U] | unverified | No detection of OH/water reported (task brief); primary papers NOT retrieved; Fernando 2026: no flash or plume detection reported for Lunar Prospector | unverified | Goldstein et al. 1999 GRL 26 (not retrieved); Fernando et al. 2026 (review) | peer-reviewed (not retrieved) / review | U/R |

### Hiten (ISAS)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 1993-04-10 18:03:25.7 [S Wikipedia] |
| Impact mass | ~143 kg [S] |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | between Stevinus and Furnerius [S] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 34.3S 55.6E; trajectory moved to near side 'so that it could be observed' [S]; night side (SZA 100 deg), 57 deg from sub-Earth pt; Moon 80% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| Anglo-Australian Telescope (per Fernando 2026 citing Cudnik 2009) | unverified | unverified | Fernando 2026: 'impact flash from Hiten was captured by the Anglo-Australian telescope (Cudnik 2009)'; original not retrieved | unverified | Fernando et al. 2026 (review statement); Cudnik 2009 (book, not retrieved) | review | R |

### Chandrayaan-1 Moon Impact Probe (ISRO)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2008-11-14 ~15:01 UT [U] |
| Impact mass | ~35 kg [S] |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | near Shackleton, south pole [S] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 89.77S 39.4W [S]; 84 deg from sub-Earth pt, near-terminator polar (SZA 88 deg); Moon 97% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| - | - | - | No Earth-based observation found | - | - | - | U |

### Chang'e 1 (CNSA)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2009-03-01 ~08:13 UT [U] |
| Impact mass | unverified (Wikipedia list 2000 kg) |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | Mare Fecunditatis area [U] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 1.50S 52.36E [S]; sunlit (SZA ~71 deg), 57 deg from sub-Earth pt; Moon 19% lit (waxing crescent) [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| - | - | - | No primary report of Earth-based observation retrieved | - | - | - | U |

### Chang'e 5-T1 booster / rocket body (identity unresolved per LROC)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2022-03-04 (~12:25 UT [U]) |
| Impact mass | unverified (~2.8 t [S]) |
| Speed | unverified (~2.6 km/s [U]) |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | Orientale ejecta over Hertzsprung rim [V LROC] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 5.226N 234.486E, far side (130 deg from sub-Earth pt) [V/C]; not observable from Earth |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (M1407760984R 21 May 2022 vs M1400727806L 28 Feb 2022) | visible | - | Double crater: eastern 18 m superimposed on western 16 m, ~28 m long; 'may indicate large masses at each end' | before/after search (later analysis) | LROC 'Mystery Rocket Body Found!' 23 Jun 2022 https://lroc.im-ldi.com/images/1261 | mission team post | V |

### Beresheet (SpaceIL)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2019-04-11 [V LROC] (~19:23 UT [U]) |
| Impact mass | unverified (~150 kg [S]) |
| Speed | '~1000 m/s faster than intended' [V LROC] |
| Incidence (from horizontal) | <10 deg [V LROC] |
| Material/target assumptions | Mare Serenitatis [U] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 32.5956N 19.3496E [V LROC]; sunlit (SZA ~81 deg), 39 deg from sub-Earth pt; Moon 39% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (M1310536929R, 11 d after) | visible | - | No crater detectable at NAC scale ('gouge rather than crater'); ~10 m dark smudge; reflectance halo 30-50 m; ray ~100 m to S | before/after ratio | LROC 'Beresheet Crash Site Spotted!' 15 May 2019 https://lroc.im-ldi.com/images/1101 | mission team post | V |

### Chandrayaan-2 Vikram (ISRO)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2019-09-06 ~20:23 UT [U] |
| Impact mass | ~1471 kg [S] |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | south polar highlands [U] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 70.88S 22.78E [S]; sunlit near terminator (SZA ~84 deg), 69 deg from sub-Earth pt; Moon 57% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (debris field; not fetched by this task) | visible | - | Not verified here | - | LROC post (id 1131 per parallel log; not fetched here) | mission team post | U |

### HAKUTO-R Mission 1 (ispace)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2023-04-25 ~16:40 UTC (12:40 pm EDT) [V LROC] |
| Impact mass | unverified (~340 kg [S]) |
| Speed | unverified (free fall after propellant exhaustion [U]) |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | near Atlas crater [V LROC] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 47.581N 44.094E [V LROC]; sunlit (SZA ~79 deg), 65 deg from sub-Earth pt; Moon 30% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (M1437131607R, 26 Apr 2023) | visible | - | At least four prominent debris pieces; possible small crater; higher-reflectance area ~60-80 m across | before/after comparison | LROC 23 May 2023 https://lroc.im-ldi.com/images/1302 | mission team post | V |

### Luna 25 (Roscosmos)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2023-08-19 11:58 UTC [V LROC] |
| Impact mass | unverified (~1750 kg [S]) |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | SW rim of Pontecoulant G [V LROC] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 57.865S 61.360E [V LROC]; sunlit near terminator (SZA ~86 deg), 74 deg from sub-Earth pt; Moon 8.5% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (M1447547309R etc., 24 Aug 2023) | visible | - | New crater ~10 m across | before (Jun 2022) / after comparison | LROC 'Luna 25 Impact Crater' 29 Nov 2023 https://lroc.im-ldi.com/images/1311 | mission team post | V |

### ispace Mission 2 RESILIENCE

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2025-06-05 18:13 UTC [V LROC] |
| Impact mass | unverified (~340 kg [S]) |
| Speed | unverified |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | Mare Frigoris [U] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 60.4445N 355.4120E [V LROC]; sunlit (SZA ~78 deg), 58 deg from sub-Earth pt; Moon 74% lit [C] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (M1504323448R) | visible | - | Dark smudge surrounded by subtle bright halo (no crater size given) | before/after comparison | LROC 20 Jun 2025 https://lroc.im-ldi.com/images/1456 | mission team post | V |

### Falcon 9 upper stage 2025-010D (Blue Ghost 1 launch, 15 Jan 2025)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 2026-08-05 06:35 UTC [V LROC]; predicted 06:35:37.5 +/- few s [V Gray] |
| Impact mass | ~4000 kg [V Fernando] / ~4900 kg [V Gray] / 3900 kg [S Wikipedia] - conflict |
| Speed | 2.43 km/s [V Fernando; Gray] |
| Incidence (from horizontal) | ~31 deg [V LROC; Gray]; Fernando v1 gave 34 deg from vertical (=56 deg from horizontal) - conflict |
| Material/target assumptions | near Einstein crater; regolith vs bedrock unknown pre-impact [V Fernando]; ejecta mixed mature + immature (>50 cm depth) [V LROC] |
| Geometry (lat, lon, illumination, Earth visibility, phase) | 19.4759N 266.7138E (=93.29W), 511 m elev. [V NASA/LROC]; geocentrically on the limb (89.9 deg from sub-Earth pt), sunlit (SZA ~21 deg); Moon 59% lit [C/Horizons] |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| KPLO/Danuri LUTI camera | visible | single image a few hours after impact | Crater imaged; CNEOS predicted location accurate to ~0.6 mi (~1 km) | post-event targeting | NASA 18 Aug 2026 https://science.nasa.gov/solar-system/moon/nasas-lro-images-falcon-9-crater-on-moon-learns-new-details/ ; LROC https://lroc.im-ldi.com/images/1499 | agency press release + team post | V |
| LRO NAC (11-12 Aug 2026; before M1370003265R, after M1541091337R; oblique M1541154479) | visible | multiple phase angles 105-37 deg | Crater 18 m (~60 ft) diameter, <3 m (<10 ft) deep; V-shaped ejecta/forbidden zone on S side | before/after comparison | LROC 'Falcon 9 Impact!' 18 Aug 2026 https://lroc.im-ldi.com/images/1499 ; NASA 18 Aug 2026 | team post + press | V |
| Planned ground: ARC 3.5 m APO (high-cadence imaging); LDT 4.3 m (Na spectroscopy); VLT UT2/UVES (OH, Na, K); NASA Impact Flash citizen science; Lunar Impact Flash network/portal | V, R, I, J (J for daylight); Li I 670.8 nm; Na, K, OH | >=20 fps recommended for flash | NO published observational result found as of 2026-10-05 (NASA/LROC/Project Pluto pages silent on Earth-based observations; arXiv astro-ph.EP Aug-Sep 2026 listings only partially checked) - unverified | differencing vs stacked reference recommended (Fernando 2026) | Fernando et al. 2026 arXiv:2607.14625 | preprint (plan) | V (plan) / U (outcome) |

### Apollo S-IVB stages (Apollo 13,14,15,17)

| Parameter | Value |
|---|---|
| Impact time (UTC) | 1970-1972 |
| Impact mass | ~13.5-14.0 t [S] |
| Speed | ~2.5-2.6 km/s [U] |
| Incidence (from horizontal) | unverified |
| Material/target assumptions | mare/highland |
| Geometry (lat, lon, illumination, Earth visibility, phase) | near side |

| Observatory / instrument | Wavelength / band | Cadence / exposure | Actual result | Processing required | Reference (URL, year) | Type | Status |
|---|---|---|---|---|---|---|---|
| LROC NAC (crater survey) | visible | - | Craters >35 m, 35-40 m diameter, irregular outlines (no double craters) | - | LROC 'Mystery Rocket Body Found!' https://lroc.im-ldi.com/images/1261 | mission team post | V (crater sizes) |

### Planning study: Fernando et al. (2026), arXiv:2607.14625v1 (submitted 16 July 2026). Forecasts are kept separate from outcomes.

Source: https://arxiv.org/pdf/2607.14625 and https://arxiv.org/html/2607.14625. Title: "Observational planning for the 2026 August 5 Falcon 9 Upper Stage lunar impact". Authors: B. Fernando, J. Heldmann, B. Gray, J. Ortiz, B. Euser, D. Z. Seligman, E. Kim, A. Colaprete, E. M. Alessi, D. Koschny, A. Cook, J. Green, P. King, S. Teng, D. Graninger, A. Goldberg, W. Cooke, M. F. Skrutskie, K. Schlaufman, N. Schmerr, C. M. Donahue, C. A. Schmidt and N. J. Chanover. Type: preprint (not peer reviewed at the time of access). The study reports **no observations**; everything in it is a forecast or a plan. Only v1 was read. A v2 request was refused (HTTP 429), so whether a v2 exists is unverified.

| Item | Fernando et al. 2026 (forecast/plan) [V as stated in the preprint] | Outcome / check |
|---|---|---|
| Target event | Falcon 9 upper stage COSPAR 2025-010D (SatCat 62719), ~12 m x 4 m; 2026-08-05 ~06:35 UT (JD 2461257.774); near Einstein crater (88W, 15N); 'sunlit terrain near the eastern limb as seen from Earth'; visible only thanks to libration | Outcome: impact 06:35 UTC at 19.4759N 266.7138E (93.29W) per LROC, ~200 km from the forecast point [C]; geocentrically 89.9 deg from the sub-Earth point, so marginal [C] |
| Impact parameters | 2.43 km/s at 34 deg from vertical; ~4000 kg (all propellant spent); KE 11.8 GJ; momentum 9.7 MN s (5.5 MN s vertical) | Outcome: Gray (1 Aug update) gives ~4900 kg, 31 deg above horizon, 14.5 GJ; LROC gives ~31 deg from horizontal |
| Flash brightness | 'from M=+3 at the brightest to undetectably dim (fainter than M=+15 for an impactor hitting bedrock)'; band of M not specified in the extracted text | Outcome: no published magnitude or detection found [U] |
| Physical argument | At ~2 km/s the stage shocks regolith (sound speed ~hundreds of m/s) but not bedrock (1000-2000 m/s); flash brightness 'decreases nonlinearly with impact velocity'; eta 'on the order 10^-3' for meteoroids, 'potentially lower' for slow artificial impactors | No explicit eta value or light-curve model is given |
| Flash duration / cadence | 'flashes themselves last less than a second'; 'ideally at least 20+ frames per second' | - |
| Bands | V, R, I standard; J favoured for daylight; possible Li I 670.8 nm emission (Falcon 9 lithium; Wing et al. 2026) | - |
| Facilities allocated | ARC 3.5 m APO (high-cadence imaging); LDT 4.3 m (Na spectroscopy); VLT UT2/UVES (OH, Na, K); LRO and KPLO (KPLO conjunction within a few km ~2 min before impact); NASA Impact Flash citizen science; Lunar Impact Flash Network/Portal (lif.mi.imati.cnr.it) | Outcome: Danuri/LUTI imaged the crater hours later; LRO NAC on 11-12 Aug [V]. No ground results found [U] |
| Observing strategy | Observer in local darkness (S America, low-mid-latitude N America; not Hawaii/Alaska); practice run the night before (4 Aug); telescope required (even 10 cm); if the flash is not obvious, difference the flash frame against a stacked frame from just before/after | - |
| Plume / crater forecast | HOSS shock-physics: ~1.12e6 kg excavated (pi-scaling 1.2e6 kg), 150-200x impactor mass; max plume height ~1.5 km; minutes to tens of minutes; optical depth ~0.001; crater 20-30 m (by analogy with Chang'e 5 and LCROSS) | Outcome: crater 18 m, <3 m deep (LROC) [V], smaller than forecast |
| Historical claims | Hiten flash captured by AAT (Cudnik 2009); SMART-1 resolved at CFHT but 'no actual measurement of flash magnitude from an artificial lunar impact has ever been published'; Kaguya flash seen from India and Australia; LCROSS 22 m crater and ~350 t excavated; no flash or plume reported for Lunar Prospector or GRAIL | See cross-check table (e) |

## (b) Luminous-efficiency evidence

| Source (type) | Value(s) | Band / definition | Velocity range | Method | Statements relevant to 1-3 km/s | Status / URL |
|---|---|---|---|---|---|---|
| Swift et al. 2011, NASA/CP 'Meteoroids 2010' (conference paper) | eta = 1.5e-3 * exp[-(9.3 km/s)^2 / v^2]; C and Vc each +/-10% | Camera band (Sony ICX248AL silicon CCD QE) | Lab: 2.4-5.75 km/s (Pyrex spheres 6.35 mm, 0.29 g, into JSC-1a at 15-90 deg elevation, NASA AVGR). Lunar: 27-71 km/s | Exponential fit to lab and shower-derived values | 'extremely large variation with velocity in the laboratory range of 2 to 6 km/s'; a 1000 K lower bound corresponds to V_T ~1.2 km/s. The formula gives eta(1.7)=1.5e-16, eta(2.0)=6.1e-13, eta(2.43)=6.5e-10, eta(3)=1.0e-7, eta(5)=4.7e-5, eta(20)=1.2e-3 [C]. Values below 2.4 km/s are extrapolations | V https://ntrs.nasa.gov/api/citations/20110016594/downloads/20110016594.pdf |
| Moser et al. 2011, NASA/CP 'Meteoroids 2010' | eta_cam = 1.5-1.6e-3 (2008 Taurids), 1.1-1.2e-3 (2006 Geminids), 1.3-1.4e-3 (2007 Lyrids) | Camera band ~400-800 nm; spherical emission assumed | 27, 35, 49 km/s | Bellot Rubio method: model impacts matched to 36 flashes (12 per shower) | Roughly constant at 27-72 km/s | V https://ntrs.nasa.gov/api/citations/20110016597/downloads/20110016597.pdf |
| Bonanos et al. 2018, A&A 612, A76 (NELIOTA) | 1.1-1.3e-3 (Swift formula at assumed 16-24 km/s) | R (641 nm), I (798 nm), 30 fps | 16-24 km/s assumed | Two-band photometry of 10 flashes | Flash T ~1600-3100 K; masses 100 g to ~55 kg depend on assumed velocity | V https://www.aanda.org/articles/aa/full_html/2018/04/aa32109-17/aa32109-17.html |
| Avdellidou & Vaubaillon 2019, MNRAS 484, 5212 | eta1 = 5e-4 and eta2 = 1.5e-3 adopted; quotes a literature range of 5e-4 to 2e-3 | R and I; blackbody fit | Meteor-stream velocities; sporadics 24 km/s | 55 NELIOTA flashes | T 1300-5800 K, distribution 'significantly broader than a Gaussian' | V https://academic.oup.com/mnras/article/484/4/5212/5307086 |
| Madiedo et al. 2014, MNRAS (arXiv:1402.5490) | eta = 0.002 adopted | V | not extracted | 2013 Sep 11 flash: V = 2.9+/-0.2, >8 s, 15.6+/-2.5 t TNT | Its crater was later found at ~34 m vs 46-56 m predicted (LROC) | V https://arxiv.org/abs/1402.5490 ; https://lroc.im-ldi.com/images/810 |
| Madiedo et al. 2019, MNRAS 486, 3380 | eta = 3e-3 adopted | B 4.75, V 4.2, R 3.53 (multi-band) | 17 km/s assumed | 2019 Jan 21 eclipse flash: 0.28 s; T 5700+/-300 K; m 45+/-8 kg; KE 6.55e9 J | Predicted crater 10.1-15.8 m | V https://academic.oup.com/mnras/article/486/3/3380/5480892 |
| Liakos et al. 2020, A&A 633, A112 (NELIOTA) | not extracted (only part of the text was readable) | R, I | - | 79 flashes; R to ~12 mag; masses 0.7 g-8 kg | - | V (partial) https://www.aanda.org/articles/aa/full_html/2020/01/aa36709-19/aa36709-19.html |
| Ernst & Schultz 2002, LPSC 33 #1782 (laboratory) | No absolute eta. T rises with v as a power law of slope ~0.75 (T^4 ~ v^3), so I ~ v^3; intensity ~ cos(theta) as stated | Photodiode 350-1100 nm, 40 ns rise time | 4.05-5.76 km/s; 30-90 deg from horizontal; Pyrex 0.635 cm into pumice dust (AVGR) | Lab gas gun | No statement on behaviour below ~4 km/s or on target sound speed | V https://www.lpi.usra.edu/meetings/lpsc2002/pdf/1782.pdf |
| Sheward et al. 2022, EPSC2022-1077 (abstract) | - | J (1.25 um) | - | Detectability test, 0.5 m telescope + Ninox 640 II | Flash T 1300-5800 K (mean 2800 K, peak 1.035 um). Solar/flash irradiance ratio: R 57x, I 28x, J 10x. A J=5.42 star gave SNR 147 (night side), 42 (terminator), 21 (dayside), 19 (bright limb) | V https://meetingorganizer.copernicus.org/EPSC2022/EPSC2022-1077.html |
| Acar & Ates 2021, EPSC2021-498 (abstract; first detections from Turkey) | - (radiated energy only, f = 2, 500 nm passband) | unfiltered/visible, 15 fps | - | ISTEK Belde Obs., Istanbul, 16-inch SCT | Two flashes on 2017-12-12: 7.98 and 7.48 mag, 0.53 s and 0.47 s; 1.96e6 J and 2.33e6 J radiated | V https://meetingorganizer.copernicus.org/EPSC2021/EPSC2021-498.html |
| Fernando et al. 2026 (preprint) | 'on the order 10^-3' (meteoroids); 'potentially lower' for slow artificial impactors | - | 2.43 km/s target | Review/forecast | Attributes significant dimming below the target sound speed to Ernst & Schultz 2002 and Swift et al. 2010 (see cross-check) | R |
| Bellot Rubio et al. 2000, ApJL 542, L65 (Leonids) | ~2e-3 per task brief | ? | ~72 km/s | - | - | U (DOI fetch refused, 429) |
| Ortiz et al. 2006, Icarus 184, 319 | ~2e-3 per task brief | ? | sporadics | - | - | U (not retrieved) |
| Suggs et al. 2014; Bouley et al. 2012; Yanagisawa et al. 2006/2008; Liakos et al. 2024; Sheward et al. 2024 (SWIR); Schultz & Eberhardy 2015; Ernst & Schultz 2005/2007; Burchell et al. (1-3 km/s flash) | not retrieved | - | - | - | No numbers are quoted for these here | U |

## (c) Crater sizes for scaling-law validation

KE is computed here as 0.5 m v^2, using only the inputs shown. Where any input is [U] the KE is [U] too.

| Impactor | Mass at impact | Speed | Angle from horizontal | KE | Target | Crater / scar | Source |
|---|---|---|---|---|---|---|---|
| GRAIL Ebb, Flow (2012) | ~130 kg each [V] | ~1.6 km/s [V] | ~2 deg [V] | 1.7e8 J each [C] | highland massif | ~5 m each; dark irregular ejecta, little to the S [V] | LROC images/596 |
| LADEE (2014) | 248 kg [V] | 1.699 km/s [V] | low, westward [V] | 3.6e8 J [C] | Sundman V east rim (highland) | <3 m (models: ~1.8 m); V-shaped NW ejecta, bright material >200 m [V] | LROC images/822 |
| SMART-1 (2006) | ~285 kg [U] | ~2 km/s [V] | ~1 deg [V] | ~5.7e8 J [U] | Lacus Excellentiae edge | Scar reported found in LRO images in 2017 (Stooke); size NOT verified [U] | - |
| Beresheet (2019) | ~150 kg [S] | ~1 km/s ('~1000 m/s faster than intended') [V] | <10 deg [V] | ~7.5e7 J [U] | mare | No crater resolvable; ~10 m dark smudge, 30-50 m halo, ~100 m ray to S [V] | LROC images/1101 |
| Luna 25 (2023) | ~1750 kg [S] | [U] | [U] | [U] | Pontecoulant G SW rim | ~10 m crater [V] | LROC images/1311 |
| LCROSS Centaur (2009) | 2271.6 kg [V] | 2.507 km/s [V] | 85.9 deg [V] | 7.1e9 J [C] | PSR regolith, volatile-bearing | 22 m [R, Fernando citing Fassett et al. 2024]; Marshall 2012: modelled 25-30 m, dark region 62+/-20 m, MIR hot spot 90+/-25 m (full text) vs '20 m crater, 160 m ejecta' (NTRS abstract summary) [V, extractions differ]; pre-impact expectation ~27 m / 350 t [S] | Marshall et al. 2012 |
| Falcon 9 2025-010D (2026) | ~4000 kg [V Fernando] / ~4900 kg [V Gray] | 2.43 km/s [V] | ~31 deg [V] | 1.18e10 J / 1.45e10 J [C] | regolith vs bedrock unknown; ejecta from >50 cm depth | 18 m (~60 ft), <3 m (<10 ft) deep; V-shaped ejecta and forbidden zone to the S [V]; forecast was 20-30 m | LROC images/1499; NASA release |
| Rocket body, 4 Mar 2022 (attributed elsewhere to CE5-T1; LROC: identity unresolved) | ~2.8 t [S] | ~2.6 km/s [U] | [U] | [U] | Orientale ejecta over Hertzsprung rim | Double crater: 18 m (E) + 16 m (W), ~28 m long [V] | LROC images/1261 |
| Apollo S-IVB 13, 14, 15, 17 | ~13.5-14.0 t [S] | ~2.5-2.6 km/s [U] | [U] | ~4e10 J [U] | mare/highland | >35 m, 35-40 m, irregular outlines [V] | LROC images/1261 |
| HAKUTO-R M1 (2023) | ~340 kg [S] | [U] (slow) | [U] | - | near Atlas | Debris (>=4 pieces), possible small crater, 60-80 m bright area [V] | LROC images/1302 |
| ispace M2 Resilience (2025) | ~340 kg [S] | [U] | [U] | - | Mare Frigoris | Dark smudge with subtle bright halo; no size given [V] | LROC images/1456 |
| Natural: 2013 Sep 11 flash (V=2.9, >8 s) | ~450 kg [U] | ~17 km/s [U] | - | 15.6 t TNT = 6.5e10 J [V] | Mare Nubium area (17.2S 20.5W) | ~34 m (predicted 46-56 m), ejecta >500 m [V] | LROC images/810; Madiedo 2014 |
| Natural: 2019 Jan 21 eclipse flash (V=4.2, 0.28 s) | 45+/-8 kg [V] | 17 km/s (assumed) [V] | - | 6.55e9 J [V] | 29.2S 67.5W | Predicted 10.1-15.8 m [V]; observed size not verified [U] | Madiedo 2019 |

For scale: an AYAP-1 envelope of 300-1500 kg at 1.5-1.7 km/s gives KE ~3.4e8 to 2.2e9 J [C]. That brackets GRAIL, LADEE and SMART-1 (0.17-0.57 GJ) at the low end. It is about 3-40x below LCROSS and Falcon 9 (7-15 GJ).

## (d) What the primary literature does and does not support for ~1-3 km/s spacecraft impacts

**Supported**

1. **A slow, grazing impact can produce an easily recorded near-IR flash.** SMART-1 hit at ~2 km/s and ~1 deg, at night in Earthshine, with a mass of ~285 kg [U] (366 kg at launch [V]). It saturated a single 10-s exposure on the CFHT 3.6 m with WIRCam, through a narrowband H2 filter at 2.12 um (32-40 nm wide). The flash was elongated along the direction of motion and showed diffraction spikes [V: Veillet & Foing 2007; ESA captions]. Differencing pre- and post-impact frames then revealed a dust cloud 10-20 s after impact [V].
2. **No artificial-impact flash magnitude, light curve, colour or temperature has been published.** The CFHT frame was saturated and its photometry was never reported. Fernando et al. (2026) say the same, and I found nothing that contradicts it. The search was not exhaustive.
3. **Most other attempts failed or were never reported.** SMART-1 had about 20 registered optical, radio and space facilities; no other confirmed detection exists, only one "possible" amateur detection in New Mexico, with failures attributed to weather and geometry. No quantitative upper limits were found.
4. **A thin plume needs heavy post-processing to see from the ground.** The LCROSS Centaur (2.27 t, 2.51 km/s, near-vertical) hit a PSR whose impact point was hidden from Earth. The plume was recovered only after PCA filtering, in APO 3.5 m V-band frames (0.5 s) and MRO 2.4 m U-band frames (0.034 s). It peaked at 10.0 mag/arcsec^2 at 17-27 s, against a 6.75 mag/arcsec^2 background and 251x fainter than the brightest foreground ridge, with optical depth ~0.0018.
   - The MMT 6.5 m (700 nm), NMSU 1 m (R video), TMO 0.6 m (NIR video), HST (UV), Subaru, the Hale 5 m with adaptive optics, and amateurs all reported nothing.
   - Standard differencing and median filtering failed on these data. The requirements identified were a linear ADC of at least 16 bits, no gamma correction, and scattered light kept within the dynamic range [V: Strycker et al. 2013, 2023].
5. **The meteoroid-regime luminous efficiency is ~5e-4 to 3e-3 at 16-72 km/s** (Moser 2011; Bonanos 2018; Avdellidou & Vaubaillon 2019; Madiedo 2014/2019) [V].
   - Laboratory data down to 2.4 km/s (Swift 2011) and 4 km/s (Ernst & Schultz 2002) show a steep fall with decreasing velocity (I ~ v^3 at 4-6 km/s).
   - The Swift exponential gives eta ~1e-9 to 1e-10 at 2.4-2.5 km/s. Taken at face value it gives eta ~1e-13 to 1e-16 at 1.7-2.0 km/s, which is below its fitted range [C].
6. **Natural flash temperatures are 1300-5800 K (mean ~2800 K)** [V: Avdellidou & Vaubaillon 2019; Sheward 2022]. NELIOTA flashes are brighter in I than in R. J-band cuts the solar-to-flash contrast from 57x (R) to 10x and allows daytime detection of J ~5.4 sources [V: Sheward EPSC 2022]. Both documented artificial-impact flash detections were in the near-IR on the night side (SMART-1 [V]; Kaguya [U]).
7. **Natural flash durations** [V]:
   - NELIOTA: from single 33-ms frames to multi-frame events (Bonanos 2018: 33-165 ms);
   - the V=4.2 eclipse flash: 0.28 s (Madiedo 2019);
   - the 7.5-8 mag ISTEK flashes: 0.47-0.53 s (Acar & Ates 2021);
   - the V=2.9 event of 2013 Sep 11: over 8 s (Madiedo 2014).

   The only artificial-impact constraint is that the SMART-1 flash fell inside one 10-s exposure. Fernando et al. expect under 1 s for the Falcon 9 and recommend at least 20 fps [R].
8. **Craters from 1-2.6 km/s artificial impacts have now been imaged:**
   - a few metres for 130-250 kg (GRAIL ~5 m, LADEE <3 m);
   - ~10 m for Luna 25, whose mass and speed are unverified;
   - 16-18 m for multi-tonne stages (CE5-T1 double crater; Falcon 9 18 m, <3 m deep);
   - 35-40 m for S-IVBs [V].
   Very low angles give gouges or asymmetric ejecta instead of round craters (Beresheet: no crater; GRAIL: little ejecta to the S; Falcon 9 and LADEE: V-shaped patterns) [V]. Two pre-impact crater predictions were too large: Falcon 9 (20-30 m forecast vs 18 m) and the natural 2013 Sep 11 flash (46-56 m vs 34 m) [V].
9. **Lunar impact flashes have already been detected from Türkiye.** ISTEK Belde Observatory in Istanbul (16-inch SCT, Skyris 274M, 15 fps, network-synchronised timing) recorded two flashes on 2017-12-12, of 7.98 and 7.48 mag lasting 0.53 and 0.47 s [V: Acar & Ates, EPSC 2021].

**Not supported, or unresolved**

- **No luminous efficiency has been measured at or below 2.4 km/s for regolith, at lunar scale or for spacecraft-like projectiles.** The SMART-1 detection seems inconsistent with the Swift extrapolation. At ~0.57 GJ (if 285 kg at 2 km/s), eta ~6e-13 would give ~3e-4 J of light, far below detectability. A meteoroid-like eta ~1e-3 to 1.5e-3 would give ~0.6-0.9 MJ, within a factor of ~3 of the ~2 MJ radiated by the 7.5-8 mag ISTEK flashes. This suggests the exponential law should not be extrapolated to slow, grazing spacecraft impacts, or that other processes dominate in the near-IR: hot fragments, propellant or structural materials, cooler thermal emission lasting seconds. *This is an inference from the fetched sources; no fetched paper quantifies it.*
- **The Kaguya detection (AAT/IRIS2) cannot be pinned down.** I could not locate a primary source for its band, cadence, brightness or processing. The Hiten (AAT, 1993) claim rests only on Fernando et al. (citing Cudnik 2009). Both remain [U]/[R].
- **The Falcon 9 ground campaign has no outcome on record.** No ground-based detection or non-detection was found in any fetched source up to 5 Oct 2026 (NASA and LROC releases, Project Pluto, and partially checked arXiv astro-ph.EP listings for Aug-Sep 2026). The final site was geocentrically on the limb (89.9 deg) and sunlit, which is a hard geometry for flash detection.
- **The GRAIL plume is disputed.** A Wikipedia caption says LRO LAMP viewed "the impact and the resulting plume". Fernando et al. say no plume has been reported for GRAIL. The primary LAMP paper was not retrieved.
- **Angle dependence at grazing incidence for spacecraft is unquantified.** Ernst & Schultz cover only 30-90 deg, and their stated cos(theta) convention is ambiguous. There is also no quantitative regolith-versus-bedrock flash dependence beyond the qualitative argument in Fernando et al.

**Lessons on geometry**

- Every Earth-based flash detection or claim (SMART-1, Kaguya, Hiten) comes from a night-side site on the Earth-facing hemisphere.
- Impacts where the impact point could not be seen from Earth produced at best plume or exospheric signatures (LCROSS: hidden PSR; Lunar Prospector: beyond the limb) or none at all (LADEE and Falcon 9 on the limb; CE5-T1 on the far side).

## (e) Review statements checked against originals

| Statement | Made by | Checked against | Verdict |
|---|---|---|---|
| No flash magnitude from any artificial impact has ever been published | Fernando 2026 (cites Burchell 2010) | Veillet & Foing 2007: image 'saturated and it is very difficult to estimate the magnitude'; photometry 'pending' | Agrees (no later magnitude found here) |
| SMART-1 seen with the '4-metre class' CFHT | Fernando 2026 | CFHT is a 3.6 m telescope; WIRCam (ESA; Veillet & Foing) | Agrees |
| SMART-1 filter | ESA caption: 2122 nm, 32 nm BW | LPSC abstract: ~2130 nm, 40 nm BW | Minor disagreement; same H2 1-0 S(1) filter |
| SMART-1 mass ~285 kg | task brief | ESA: 366 kg at launch; Wikipedia list: 307 kg | Unresolved; impact mass not verified |
| LCROSS Centaur 2305 kg | Fernando 2026; task brief | Marshall 2012: 2271.61 kg at separation (S-SC 617.18 kg) | Small disagreement (likely different epoch/definition) |
| LCROSS 22 m crater, ~350 t excavated | Fernando 2026 (cites Fassett 2024) | Fassett 2024 not retrieved; Marshall 2012 modelled 25-30 m; Wikipedia gives 350 t and ~27 m as pre-impact expectations | Partially consistent; the 350 t figure appears to be a pre-impact prediction |
| Kaguya flash seen from India and Australia | Fernando 2026 (cites Shirao & Wood 2011) | Primary not found; JAXA page gives only time/site | Not checked |
| Hiten flash captured by AAT | Fernando 2026 (cites Cudnik 2009) | Not found; Wikipedia says only that the impact was moved to the near side 'so that it could be observed' | Not checked |
| No flash or plume reported for Lunar Prospector or GRAIL | Fernando 2026 | Wikipedia GRAIL: LAMP slit view 'showing the impact and the resulting plume' | Possible disagreement for GRAIL (primary not retrieved) |
| Flash dims significantly once v is below target sound speed | Fernando 2026 (cites Ernst & Schultz 2002; Swift et al. 2010) | E&S 2002 covers 4.05-5.76 km/s with no sound-speed statement; Swift 2011 shows a steep fall from 6 to 2 km/s and a ~1.2 km/s (1000 K) threshold | Steep decline supported; sound-speed framing not in the cited texts |
| Falcon 9 impact at 88W 15N, 34 deg from vertical, ~4000 kg | Fernando 2026 v1 | Gray (1 Aug): 19.461N 266.707E, 31 deg above horizon, ~4900 kg. LROC: 19.4759N 266.7138E, ~31 deg from horizontal | Disagreement (~200 km; angle); Gray's 8 Jun update moved the solution ~170 km NW |
| GRAIL ~75.6N 26.6E; ~200 kg each | task brief | LROC: 333.407E (=26.6W); ~130 kg at impact (~200 kg on arrival) | Corrected |
| LADEE 3 m crater; far side | task brief | LROC: <3 m (1.8 m predicted); site 89.7 deg from sub-Earth point (geocentric limb) [C] | Agrees (crater); 'far side' is marginal |
| LADEE speed | Wikipedia: 5800 km/h (1.61 km/s) | LROC: 1699 m/s | Minor disagreement; LROC used |
| Beresheet ~10 m crater | task brief | LROC: no crater detectable; ~10 m dark smudge | Disagreement (a smudge, not a crater) |
| CE5-T1 double crater 18 m / 16 m | task brief | LROC: 18 m + 16 m, but 'identity of the rocket body remains unclear' | Sizes agree; attribution not made by LROC |
| Apollo S-IVB 30-40 m | task brief | LROC: 35-40 m | Agrees |
| GRAIL 4-6 m | task brief | LROC: ~5 m | Agrees |
| Luna 25 ~10 m | task brief | LROC: ~10 m | Agrees |

## (f) URL log (accessed 2026-10-05; the last few entries ran just after 00:00 UTC on 2026-10-06 and are marked)

Fetch outcomes as reported by the fetch tool. Fetches that hit the cache were not counted separately; re-prompts of a cached URL are noted in the outcome. Requests refused with 429 by the fetch proxy were not retried.

| # | URL | Outcome | Notes | Accessed |
|---|---|---|---|---|
| 1 | https://arxiv.org/abs/2607.14625 | FAIL (helper reported no parsable text) | abs page; PDF/HTML used instead | 2026-10-05 |
| 2 | https://science.nasa.gov/solar-system/moon/nasas-lro-images-falcon-9-crater-on-moon-learns-new-details/ | OK (2 prompts) | NASA release 18 Aug 2026 (upd. 19 Aug) | 2026-10-05 |
| 3 | https://export.arxiv.org/api/query?id_list=2607.14625 | FAIL robots.txt disallowed |  | 2026-10-05 |
| 4 | https://arxiv.org/pdf/2607.14625 | OK | Fernando et al. 2026 full text (v1, 16 Jul 2026) | 2026-10-05 |
| 5 | https://arxiv.org/html/2607.14625 | OK (4 prompts) | Fernando et al. HTML incl. reference list | 2026-10-05 |
| 6 | https://api.crossref.org/works?query=SMART-1+lunar+impact+flash&rows=20... | OK | search substitute | 2026-10-05 |
| 7 | https://www.lpi.usra.edu/meetings/lpsc2007/pdf/1520.pdf | OK (2 prompts) | Veillet & Foing 2007 LPSC 38 #1520 | 2026-10-05 |
| 8 | https://doi.org/10.1016/j.icarus.2009.10.005 | REDIRECT (Elsevier linkinghub) | Burchell et al. 2010 | 2026-10-05 |
| 9 | https://www.sciencedirect.com/science/article/pii/S001910350900414X | FAIL robots.txt disallowed |  | 2026-10-05 |
| 10 | https://api.crossref.org/works?query=SMART-1+impact+observation+ejecta+flash+Moon+2006... | OK (nothing new) |  | 2026-10-05 |
| 11 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.icarus.2009.10.005 | FAIL 429 |  | 2026-10-05 |
| 12 | https://ui.adsabs.harvard.edu/abs/2010Icar..207...28B/abstract | FAIL robots.txt fetch failed |  | 2026-10-05 |
| 13 | https://api.crossref.org/works/10.1016/j.icarus.2009.10.005 | OK (metadata only; no abstract) | Burchell, Robin-Williams, Foing; Icarus 207(1):28-38 | 2026-10-05 |
| 14 | https://www.esa.int/Science_Exploration/Space_Science/SMART-1/SMART-1_impact_flash_and_debris_crash_scene_investigation | FAIL 403 |  | 2026-10-05 |
| 15 | https://api.elsevier.com/content/article/PII:S001910350900414X?httpAccept=text/plain | FAIL 403 |  | 2026-10-05 |
| 16 | https://kar.kent.ac.uk/cgi/search/simple?q=SMART-1+lunar+impact+Burchell | FAIL robots.txt (504) |  | 2026-10-05 |
| 17 | https://api.openalex.org/works/doi:10.1016/j.icarus.2009.10.005 | OK (abstract field null) |  | 2026-10-05 |
| 18 | https://api.openalex.org/works?search=Kaguya%20impact%20flash... | FAIL 429 |  | 2026-10-05 |
| 19 | https://api.openalex.org/works?search=SELENE%20impact%20observation%20Anglo-Australian%20Telescope... | FAIL 429 |  | 2026-10-05 |
| 20 | https://api.crossref.org/works?query=Kaguya+SELENE+impact+flash+observation... | FAIL WebFetch-proxy 429 (not retried) |  | 2026-10-05 |
| 21 | https://en.wikipedia.org/wiki/SELENE | OK (secondary) | 18:25 UTC 10 Jun 2009; 65deg30'S 80deg24'E | 2026-10-05 |
| 22 | http://www.kaguya.jaxa.jp/en/communication/KAGUYA_Lunar_Impact_e.htm | OK | JAXA: 18:25 GMT; E80.4 S65.5; near side night-time area; Moon age 17.3 | 2026-10-05 |
| 23 | https://ja.wikipedia.org/wiki/かぐや_(探査機) | FAIL cache-only domain |  | 2026-10-05 |
| 24 | https://ja.wikipedia.org/wiki/%E3%81%8B%E3%81%90%E3%82%84_(%E6%8E%A2%E6%9F%BB%E6%A9%9F) | FAIL cache-only domain |  | 2026-10-05 |
| 25 | https://global.jaxa.jp/press/2009/06/ | FAIL 403 |  | 2026-10-05 |
| 26 | https://web.archive.org/web/2009/http://www.kaguya.jaxa.jp/en/communication/KAGUYA_Lunar_Impact_e.htm | FAIL site blocked |  | 2026-10-05 |
| 27 | https://en.wikipedia.org/wiki/Anglo-Australian_Telescope | OK (no Kaguya mention) |  | 2026-10-05 |
| 28 | https://api.crossref.org/works?query.bibliographic=Kaguya+lunar+impact+flash+infrared+Anglo-Australian... | FAIL WebFetch-proxy 429 (not retried) |  | 2026-10-05 |
| 29 | https://www.nature.com/articles/ncomms3620 | OK | Strycker et al. 2013 Nat. Commun. 4:2620 | 2026-10-05 |
| 30 | https://ntrs.nasa.gov/api/citations/search?q=LCROSS%20observation%20campaign%20strategies%20lessons%20learned | OK (0 results) |  | 2026-10-05 |
| 31 | https://ntrs.nasa.gov/api/citations/search?q=LCROSS%20impact%20observations | OK | led to Marshall et al. 2012; Killen et al. 2010 | 2026-10-05 |
| 32 | https://ntrs.nasa.gov/api/citations/search?q=Heldmann%20LCROSS%20ground-based%20observation%20campaign | OK (0 results) |  | 2026-10-05 |
| 33 | https://link.springer.com/search?query=LCROSS+observation+campaign... | FAIL robots.txt disallowed |  | 2026-10-05 |
| 34 | https://link.springer.com/article/10.1007/s11214-011-9759-y | OK (abstract only; paywalled) | Heldmann et al. 2012 SSR 167:93-140 | 2026-10-05 |
| 35 | https://ntrs.nasa.gov/api/citations/search?q=%22LCROSS%20Observation%20Campaign%22 | OK (0 results) |  | 2026-10-05 |
| 36 | https://pubmed.ncbi.nlm.nih.gov/?term=LCROSS&size=50 | FAIL WebFetch-proxy 429 (not retried) |  | 2026-10-05 |
| 37 | https://ntrs.nasa.gov/api/citations/20140005563/downloads/20140005563.pdf | OK | Marshall et al. 2012 SSR (Locating the LCROSS impact craters) | 2026-10-05 |
| 38 | https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024GL110355 | FAIL 403 | Fassett et al. 2024 GRL | 2026-10-05 |
| 39 | https://ntrs.nasa.gov/api/citations/search?q=ShadowCam%20LCROSS%20crater | OK (0 results) |  | 2026-10-05 |
| 40 | https://arxiv.org/a/liakos_a_1 | FAIL WebFetch-proxy 429 (not retried) |  | 2026-10-05 |
| 41 | https://ntrs.nasa.gov/api/citations/search?q=luminous%20efficiency%20lunar%20impact | OK | found Swift 2011, Moser 2011/2017 | 2026-10-05 |
| 42 | https://ntrs.nasa.gov/api/citations/20110016594/downloads/20110016594.pdf | OK (2x) | Swift et al. 2011 exponential eta model | 2026-10-05 |
| 43 | https://ntrs.nasa.gov/api/citations/20110016597/downloads/20110016597.pdf | OK | Moser et al. 2011 eta from showers | 2026-10-05 |
| 44 | https://ntrs.nasa.gov/api/citations/search?q=flux%20kilogram-sized%20meteoroids%20lunar%20impact%20monitoring | OK |  | 2026-10-05 |
| 45 | https://en.wikipedia.org/wiki/List_of_artificial_objects_on_the_Moon | OK (secondary) | masses/coords table | 2026-10-05 |
| 46 | https://www.lroc.asu.edu/posts | REDIRECT to https://lroc.im-ldi.com/images |  | 2026-10-05 |
| 47 | https://lroc.im-ldi.com/images | OK | LROC featured images index (48 pages) | 2026-10-05 |
| 48 | https://lroc.im-ldi.com/images/1499 | OK | LROC 'Falcon 9 Impact!' (Robinson, 18 Aug 2026) | 2026-10-05 |
| 49 | https://lroc.im-ldi.com/images/1499 (2nd prompt) | OK | quotes: 31 deg from horizontal, 18 m diameter, <3 m deep, forbidden zone south | 2026-10-05 |
| 50 | https://lroc.im-ldi.com/images/1456 | OK | ispace M2 RESILIENCE impact site (20 Jun 2025) | 2026-10-05 |
| 51 | https://lroc.im-ldi.com/images?search=impact+site | OK (search not effective) |  | 2026-10-05 |
| 52 | https://en.wikipedia.org/wiki/Lunar_Atmosphere_and_Dust_Environment_Explorer | OK (secondary) | impact 18 Apr 2014 04:30-05:22 UT, 5800 km/h; NASA 2014-10-28 release cited | 2026-10-05 |
| 53 | https://arxiv.org/html/2607.14625 (4th prompt) | OK | review statements on Hiten, Kaguya (India+Australia), LCROSS 22 m crater, libration | 2026-10-05 |
| 54 | https://ssd.jpl.nasa.gov/api/horizons.api?...COMMAND='301'...CENTER='500@399'...2026-08-05 06:25-06:45 | OK | sub-Earth lon 354.514E lat -5.993; sub-solar 275.332E 0.472N; illum 59.29% | 2026-10-05 |
| 55 | https://www.projectpluto.com/25010d.htm | OK | Bill Gray: 06:35:37.5 UTC, 19.461N 266.707E, ~4900 kg, 2.43 km/s, 31 deg above horizon, last update 1 Aug 2026 | 2026-10-05 |
| 56 | https://arxiv.org/list/astro-ph.EP/2026-08?skip=0&show=2000 | OK (likely only first 50 of 313 seen) | no matching titles in visible part | 2026-10-05 |
| 57 | https://arxiv.org/list/astro-ph.EP/2026-09?skip=0&show=2000 | OK (only first 50 of 223 seen) | no matching titles in visible part | 2026-10-05 |
| 58 | https://arxiv.org/pdf/2607.14625v2 | FAIL WebFetch proxy 429 (not retried); existence of v2 unverified |  | 2026-10-05 |
| 59 | https://www.lpi.usra.edu/meetings/lpsc2010/pdf/2196.pdf | OK | Storrs & Colaprete 2010 HST LCROSS: no OH, no ejecta | 2026-10-05 |
| 60 | https://ntrs.nasa.gov/api/citations/search?q=NMSU%20Marshall%20LCROSS%20observational%20campaign | OK (0 results) |  | 2026-10-05 |
| 61 | https://ntrs.nasa.gov/api/citations/search?q=Chanover | OK | found Strycker et al. 2023 Remote Sensing 15:37 | 2026-10-05 |
| 62 | https://www.mdpi.com/2072-4292/15/1/37 | OK | Strycker et al. 2023 Remote Sensing: PCA detection in APO + MRO; MMT/NMSU/TMO no detection | 2026-10-05 |
| 63 | https://www.science.org/doi/10.1126/science.1187454 | FAIL 403 | Schultz et al. 2010 Science | 2026-10-05 |
| 64 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=LCROSS%20AND%20PUB_YEAR:2010... | FAIL WebFetch proxy 429 (not retried) |  | 2026-10-05 |
| 65 | https://ntrs.nasa.gov/api/citations/search?q=GRAIL%20impact%20plume | OK (0 results) |  | 2026-10-05 |
| 66 | https://en.wikipedia.org/wiki/Gravity_Recovery_and_Interior_Laboratory | OK (secondary) | 1.68 km/s, 75.62N 26.63W | 2026-10-05 |
| 67 | https://www.nasa.gov/mission_pages/LRO/news/grail-impact.html | FAIL 404 |  | 2026-10-05 |
| 68 | https://api.openalex.org/works?search=lunar%20impact%20flash... | FAIL 429 (target) |  | 2026-10-05 |
| 69 | https://www.aanda.org/articles/aa/full_html/2018/04/aa32109-17/aa32109-17.html | OK | Bonanos et al. 2018 A&A 612 A76 NELIOTA temps | 2026-10-05 |
| 70 | https://www.aanda.org/articles/aa/full_html/2020/01/aa36709-19/aa36709-19.html | OK (2 prompts; partial text) | Liakos et al. 2020 A&A 633 A112: 79 flashes, R to ~12 mag, masses 0.7 g-8 kg | 2026-10-05 |
| 71 | https://www.jstage.jst.go.jp/result/global/-char/en?globalSearchKey=SELENE+impact+flash | OK (no relevant result) |  | 2026-10-05 |
| 72 | https://en.wikipedia.org/wiki/Hiten | OK (disambiguation) |  | 2026-10-05 |
| 73 | https://en.wikipedia.org/wiki/Hiten_(spacecraft) | OK (secondary) | impact 18:03:25.7 UT 10 Apr 1993, 34.3S 55.6E; moved to near side "so that it could be observed" | 2026-10-05 |
| 74 | https://science.nasa.gov/mission/hiten/ | FAIL 404 |  | 2026-10-05 |
| 75 | https://html.duckduckgo.com/html/?q=Kaguya+impact+flash+Anglo-Australian+Telescope+IRIS2+2009 | FAIL server error |  | 2026-10-05 |
| 76 | https://www.aao.gov.au/ | OK (archived AAO site, no Kaguya content on landing page) |  | 2026-10-05 |
| 77 | https://www.aao.gov.au/press/kaguya/ | FAIL robots.txt SSL error |  | 2026-10-05 |
| 78 | http://www.kaguya.jaxa.jp/index_e.htm | OK (no impact-observation news) |  | 2026-10-05 |
| 79 | https://lroc.im-ldi.com/images?page=37 | OK | Mar-Apr 2011 posts (IDs ~300) | 2026-10-05 |
| 80 | https://lroc.im-ldi.com/images?page=28 | OK | May-Jun 2012 posts | 2026-10-05 |
| 81 | https://lroc.im-ldi.com/images?page=22 | OK | Mar-Apr 2013 posts; 'Impact!' 19 Mar 2013 id 596 | 2026-10-05 |
| 82 | https://lroc.im-ldi.com/images/596 | OK | LROC 'Impact!' 19 Mar 2013: GRAIL craters ~5 m, ~130 kg, ~2 deg, ~1600 m/s | 2026-10-05 |
| 83 | https://lroc.im-ldi.com/images?page=14 | OK | Aug 2014-Jan 2015 posts; LADEE id 822; 'Another New Crater!' id 810 | 2026-10-05 |
| 84 | https://lroc.im-ldi.com/images/822 | OK | LROC 'LADEE Impact Crater Found!' 28 Oct 2014 | 2026-10-05 |
| 85 | https://lroc.im-ldi.com/images/810 | OK | LROC 'Another New Crater!' (11 Sep 2013 MIDAS flash -> ~34 m crater) | 2026-10-05 |
| 86 | https://lroc.im-ldi.com/images?page=11 | OK | Feb-Jul 2016 posts | 2026-10-05 |
| 87 | https://lroc.im-ldi.com/images?page=9 | OK | Mar-Oct 2017 posts (no SMART-1 post) | 2026-10-05 |
| 88 | https://lroc.im-ldi.com/images?page=6 | OK | Dec 2018-Jul 2019; Beresheet id 1101 | 2026-10-05 |
| 89 | https://lroc.im-ldi.com/images/1101 | OK (2 prompts) | LROC 'Beresheet Crash Site Spotted!' 15 May 2019 | 2026-10-05 |
| 90 | https://lroc.im-ldi.com/images?page=3 | OK | Apr 2022-Aug 2023; CE5-T1 id 1261, Hakuto-R id 1302, 'Three Impact Events' id 1275 | 2026-10-05 |
| 91 | https://lroc.im-ldi.com/images/1261 | OK | LROC 'Mystery Rocket Body Found!' 23 Jun 2022: double crater 18 m + 16 m; S-IVB 35-40 m | 2026-10-05 |
| 92 | https://lroc.im-ldi.com/images/1302 | OK | LROC 'Impact Site of the HAKUTO-R Mission 1 Lunar Lander' 23 May 2023 | 2026-10-05 |
| 93 | https://lroc.im-ldi.com/images?page=2 | OK | Aug 2023-Mar 2025; Luna 25 id 1311 | 2026-10-05 |
| 94 | https://lroc.im-ldi.com/images/1311 | OK | LROC 'Luna 25 Impact Crater' 29 Nov 2023: ~10 m crater | 2026-10-05 |
| 95 | https://ntrs.nasa.gov/api/citations/search?q=Lunar%20Prospector%20impact | OK (no relevant result) |  | 2026-10-05 |
| 96 | https://api.crossref.org/works?query.bibliographic=Impacting+Lunar+Prospector+in+a+cold+trap... | FAIL 429 (target) |  | 2026-10-05 |
| 97 | https://skyandtelescope.org/?s=Kaguya+impact | FAIL robots.txt disallowed |  | 2026-10-05 |
| 98 | https://arxiv.org/a/sheward_d_1 | FAIL WebFetch proxy 429 (not retried) |  | 2026-10-05 |
| 99 | https://www.lpi.usra.edu/meetings/lpsc2002/pdf/1782.pdf | OK (2 prompts) | Ernst & Schultz 2002 LPSC: 4.05-5.76 km/s, T~v^0.75, I~v^3, 350-1100 nm | 2026-10-05 |
| 100 | https://arxiv.org/abs/1402.5490 | OK | Madiedo et al. 2014 (11 Sep 2013 flash): V=2.9, >8 s, 15.6 t TNT, eta=0.002 | 2026-10-05 |
| 101 | https://doi.org/10.1093/mnras/stz932 | REDIRECT to academic.oup.com |  | 2026-10-05 |
| 102 | https://academic.oup.com/mnras/article/486/3/3380/5480892 | OK | Madiedo et al. 2019 MNRAS 486:3380 eclipse flash | 2026-10-05 |
| 103 | https://sci.esa.int/web/smart-1/-/39961-impact-landing-ends-smart-1-mission-to-the-moon | OK | ESA: 05h42m21.759s UT; ~2 km/s; grazing ~1 deg; dark area near terminator; 366 kg at launch; observers worldwide | 2026-10-05 |
| 104 | https://sci.esa.int/web/smart-1/-/39962-cfht-image-of-smart-1-impact | OK | ESA caption: IR image 3.6 m CFHT at ~05:42:15 UT | 2026-10-05 |
| 105 | https://sci.esa.int/web/smart-1/-/39963 | FAIL 404 | guessed ID | 2026-10-05 |
| 106 | https://sci.esa.int/science-e/www/area/index.cfm?fareaid=98 | OK | ESA legacy SMART-1 impact area: 34.4S 46.2W; links to participating observatories, flash contour, dust cloud | 2026-10-05 |
| 107 | https://sci.esa.int/web/smart-1-lunar-impact/39928-participating-observatories | OK | pre-impact list of ~20 participating radio/optical/space observatories (no results) | 2026-10-05 |
| 108 | https://sci.esa.int/web/smart-1/-/39968-impact-dust-cloud | OK | ESA: CFHT WIRCam 2122 nm H2 filter 32 nm BW, 10 s exposures, 2x2 arcmin (~200 km) frames, dust plume found by Veillet | 2026-10-05 |
| 109 | https://sci.esa.int/web/smart-1/-/39964-contour-plot-of-impact-flash | OK | ESA: flash "so bright that it is saturated"; elongated to S in direction of motion; 0.3"/pix ~0.5 km | 2026-10-05 |
| 110 | https://pubmed.ncbi.nlm.nih.gov/20966243/ | FAIL reCAPTCHA page |  | 2026-10-05 |
| 111 | https://en.wikipedia.org/wiki/LCROSS | OK (secondary) | no Earth visibility of impact/plume per WP; Hale AO non-detection; Diviner 4 channels; pre-impact 350 t / 27 m crater expectation | 2026-10-05 |
| 112 | https://meetingorganizer.copernicus.org/EPSC2022/EPSC2022-1077.html | OK | Sheward et al. EPSC 2022: J-band all-hours LIF; MagJ 5.423 star SNR 21 dayside/19 bright limb/147 nightside; LIF T 1300-5800 K mean 2800 K | 2026-10-05 |
| 113 | https://meetingorganizer.copernicus.org/EPSC2021/EPSC2021-498.html | OK | Acar & Ates EPSC 2021: first Turkish LIF detections 12 Dec 2017, ISTEK Belde Obs. 16-in SCT 15 fps; 7.98/7.48 mag; 0.53/0.47 s | 2026-10-05 |
| 114 | https://api.crossref.org/works?query.bibliographic=Kaguya+impact+flash+Moon+2009+observation... | FAIL WebFetch-proxy 429 (not retried) |  | 2026-10-05 |
| 115 | https://ssd.jpl.nasa.gov/api/horizons.api?...TLIST (14 epochs) | FAIL WebFetch-proxy 403 (URL too long) | geometry computed locally instead (astropy + IAU 2009 lunar rotation), validated vs Horizons row #54 | 2026-10-05 |
| 116 | https://doi.org/10.1086/312906 | FAIL WebFetch-proxy 429 (not retried) | Bellot Rubio et al. 2000 ApJL | 2026-10-05 |
| 117 | https://api.semanticscholar.org/graph/v1/paper/search?query=lunar+impact+flash+luminous+efficiency... | FAIL 429 (target) |  | 2026-10-05 |
| 118 | https://doi.org/10.1093/mnras/stz355 | REDIRECT to academic.oup.com/mnras/article/484/4/5212/5307086 | Avdellidou & Vaubaillon 2019 | 2026-10-05 |
| 119 | https://academic.oup.com/mnras/article/484/4/5212/5307086 | OK | Avdellidou & Vaubaillon 2019 MNRAS 484:5212: 55 NELIOTA flashes, T 1300-5800 K; eta 5e-4 and 1.5e-3; sporadic 24 km/s | 2026-10-05 |
| 120 | https://ntrs.nasa.gov/api/citations/search?q=LCROSS%20cratering%20experiment | FAIL robots.txt fetch failed (transient) |  | 2026-10-05 |
| 121 | https://arxiv.org/html/2607.14625v1 | OK (accessed 2026-10-06 UTC) | verbatim Hiten and Kaguya sentences confirmed; no DOIs in reference list except Burchell 2010 | 2026-10-06 (UTC, just after midnight) |
| 122 | https://ntrs.nasa.gov/api/citations/search?q=LCROSS%20impact%20plume | OK (accessed 2026-10-06 UTC) | Killen et al. 2010 abstract: McMath-Pierce ~2 g Na in first 9 min, 0.5-2.6 kg Na released; Marshall 2012 abstract: 20 m crater + 160 m ejecta; Fandozzi 2025: both impacts ~2.5 km/s | 2026-10-06 (UTC, just after midnight) |
| 123 | https://ntrs.nasa.gov/api/citations/search?q=Kaguya%20impact | OK (no relevant result; accessed 2026-10-06 UTC) |  | 2026-10-06 (UTC, just after midnight) |
| 124 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.icarus.2009.10.005?fields=title,abstract,year,venue | FAIL 429 (target; accessed 2026-10-06 UTC) | Burchell et al. 2010 abstract still unavailable | 2026-10-06 (UTC, just after midnight) |

Total fetch attempts logged: 124.
