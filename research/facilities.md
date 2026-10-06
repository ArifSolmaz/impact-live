# AYAP-1 lunar impact: inventory of Earth-based observing facilities

**Purpose.** This is a verified inventory of telescopes and fast cameras that could observe the terminal lunar impact of Türkiye's AYAP-1 spacecraft (expected 2027–2028). The impact should produce a faint flash lasting from under a second to a few seconds, and possibly an ejecta plume.
**Evidence cutoff / access date:** 5 October 2026 (all URLs accessed 2026-10-05).
**Companion file:** `facilities.csv`. It has 80 rows, one per telescope/instrument combination, including 26 in Türkiye. It also contains machine-readable coordinates and the MPC cross-checks.

---

## 1. Method, tooling limits and labels

**How sources were retrieved**
- Each source URL was fetched individually with WebFetch, because web search was disabled. 143 fetch attempts are logged in §8.
- Many attempts failed, for these reasons:
  - **Rate limits:** OpenAlex, Crossref and Semantic Scholar returned HTTP 429. arXiv's search and export API are blocked by robots.txt.
  - **Blocked or bot-walled sites:** the Wayback Machine, the SPIE Digital Library (Incapsula), gemini.edu (403) and Palomar (403).
  - **Unrenderable pages:** several Turkish university sites render only through JavaScript.
  - **Wikipedia:** cache-only, so uncached pages could not be fetched.
  - **NASA ADS:** abstract pages worked intermittently and otherwise failed with robots.txt errors.
- Wikipedia was used only as a pointer to primary sources.

**Coordinates**
- The MPC list (`ObsCodes.html`) renders only partially through WebFetch. It returned the numeric codes and early lettered codes verbatim, for example A84, 088, 474 and 809. Shell access to minorplanetcenter.net is blocked.
- For the remaining codes, I used a full mirror of the MPC list: OpenOrb's `OBSCODE.dat` on GitHub, 2717 lines. Its entries agree with the lines the MPC returned directly.
- MPC parallax constants (ρcosφ′, ρsinφ′) were converted to geodetic latitude and height on the WGS84 ellipsoid.
  - With 5-decimal constants, the derived heights are uncertain by about ±30–60 m.
- As a second, independent check I used the astropy site registry (`sites.json`).

**Participation labels**
- **Technically compatible equipment:** an instrument exists that can take sub-second frames (about ≥10–25 fps, or ≤0.1 s cycles) or has proven lunar-flash performance. Pointing at the Moon is not excluded. The label says nothing about availability or willingness.
- **Candidate infrastructure:** the telescope or site could host a visitor fast camera, or could image ejecta at slower cadence. No suitable fast imager was verified.
- **Confirmed participation:** none. No facility has committed, and no commitment was inferred from websites.

**CSV columns** (`facilities.csv`, UTF-8, RFC-4180 quoting):
- **Identity and location:** `id`, `name`, `country`, `site`, `latitude_deg` (N+), `longitude_deg` (E+), `altitude_m`.
- **Coordinate checks:** `coord_source`, `mpc_code`, `mpc_crosscheck`. The last gives the MPC-derived position (and the astropy registry position where one exists), with the horizontal offset and height difference.
- **Instrument:** `aperture_m`, `instruments`, `wavelength_filters`, `max_frame_rate_cadence_duty`, `timing_accuracy`, `fov_pixel_scale`.
- **Operating constraints:** `lunar_tracking_restrictions`, `horizon_pointing_limits`, `climate_weather`.
- **Availability:** `status_2026`, `access`, `participation_label`.
- **Provenance:** `sources` (URLs separated by " ; "), `notes`.

Blank cells mean unknown, and the cell or the notes then say "unverified". Rows whose coordinates were adopted from MPC say so in `coord_source`.

**Geometry used throughout**
- At the mean lunar distance (384,400 km), 1″ ≈ 1.86 km and 1′ ≈ 112 km on the Moon.
- AYAP-1's impact site and time will be predicted in advance. Narrow-field fast cameras (for example HiPERCAM at 2.8′×1.4′ ≈ 310×155 km) are therefore usable if the predicted ground track is accurate to better than about ±50–100 km. Whole-disk monitoring is not required.

---

## 2. Coverage summary

| | Rows | Technically compatible | Candidate | Status flagged uncertain / commissioning / planned |
|---|---|---|---|---|
| Türkiye | 26 | 4 | 22 | TR06, TR07, TR08, TR23, TR24, TR25 |
| International (incl. global/portable) | 54 | 16 | 38 | ES09, ES10, ET01, US06, CL01, JP02 |
| **Total** | **80** | **20** | **60** | 12 |

- 61 rows have numeric coordinates. 51 rows carry an MPC code.
- No row is labelled "confirmed participation".

---

## 3. Best-characterised fast-camera facilities (verified from primary sources)

| Facility (CSV id) | Aperture | Cadence / duty cycle | Timing | FOV / scale | Status 2026 |
|---|---|---|---|---|---|
| **NELIOTA, Kryoneri 1.2 m (GR01)** | 1.2 m prime focus f/2.8 | 30 fps; 23 ms exposure + ~10 ms readout. Two Andor Zyla 5.5 sCMOS, simultaneous R and I (dichroic at 730 nm) | Meinberg LanTime M200/GPS server (NTP) + hardware timestamp per frame | 17.0′×14.4′, 0.8″/px (binned) | **Active: "resumed August 2025, will continue through 2028"** |
| **MIDAS Sevilla / La Hita (ES01–ES03)** | 0.28–0.40 m SCT/Newtonian | 25 fps PAL video (Watec 902H Ultimate), ~100% duty | GPS time inserter, 0.01 s | ~4–8×10⁶ km² of lunar surface per telescope | Active in 2019; 2026 not verified |
| **TNT 2.4 m + ULTRASPEC (TH01)** | 2.4 m | up to ~200 Hz (drift mode); dead time 14.9 ms (0.3 ms in drift mode) | GPS, better than 1 ms absolute | 7.7′×7.7′, 0.45″/px | First light Nov 2013; 2026 not verified; site operates Nov–Apr only |
| **GTC 10.4 m + HiPERCAM (ES06)** | 10.4 m | >1050 Hz windowed; 5 bands u′g′r′i′z′ simultaneously | GPS-based (accuracy not stated) | 2.8′×1.4′, 0.081″/px | Visitor instrument, permanently on GTC since 2023 |
| **SAAO 1.0 m + SHOC (ZA01)** | 1.0 m | 0.01 s (windowed) to ~0.5 s (full frame) cycles; frame-transfer EMCCD | GPS-triggered (POP pulses) | 2.85′×2.85′, 0.167″/px | On the 1.0 m only |
| **TTT 0.8 m ×2 and 2 m (ES08–ES10), Teide** | 0.8 m / 2.0 m | ~67 fps (15 ms readout, IMX455 sCMOS) | not stated | 22.6′×15.1′ at 0.28″/px (0.8 m); 10.2′×6.8′ at 0.19″/px (2 m) | 0.8 m robotic since 2022. 2 m units in commissioning (first light 2025 and 2026) |
| **Seimei 3.8 m + TriCCS (JP01)** | 3.8 m | 98 fps full frame; 3 bands simultaneously | **Header absolute time "occasionally inaccurate"** | not verified | Shared-risk in 2027A |
| **Kiso 1.05 m + Tomo-e Gozen (JP02)** | 1.05 m Schmidt | 2 fps full frame; 160 fps partial frame | GPS, 0.2 ms | 20 deg² | Status page stale (data only to Oct 2021) |
| **APO 3.5 m + Agile (US06)** | 3.5 m | ~1.1 s full frame (faster when windowed) | GPS trigger, ~1 ms | 2.2′×2.2′ | Page last updated 2016; **uncertain** |
| **TUG100 + QHY174GPS guider (TR04), Türkiye** | 1.0 m | camera can do 138 fps (8-bit) / 75 fps (16-bit) | GPS, 1 µs (manufacturer) | 3.86′×2.42′, 0.12″/px | Installed as autoguider |
| **Ulupınar IST60 + Andor iXon Ultra 888 (TR15), Türkiye** | 0.6 m | frame-transfer EMCCD; frame rate not documented | not documented | 9.5′×9.5′, 0.56″/px | Listed; needs verification |

Other relevant data points:
- **Liverpool Telescope RISE (ES07)** is too slow for the flash. Its minimum exposure is 0.6 s and its timing is accurate only to about 70–90 ms.
- **CFHT WIRCam (US01)** is the precedent for detecting a spacecraft impact. It caught the SMART-1 impact on 3 September 2006 in a 2.122 µm H₂ filter, using 10 s exposures with ~5 s gaps in a 2′×2′ window, and followed the ejecta for ~130 s. CFHT itself notes that WIRCam is "not designed to have such a big and bright light source close by".
- **NELIOTA performance:**
  - Flash detection limit is ~12.4 mag in R and I at lunar phase ~0.1. The faintest flash detected was 11.24 mag (R).
  - Observations are restricted to lunar phase ~10–45% and elevation ≥20°.
  - It detected 31 validated flashes in its first year (54 h on the Moon), and 79 flashes in its first 30 months (Liakos et al. 2020).
  - Statistics published after 2020 (Liakos et al. 2024) could not be verified because the ADS fetch failed.

---

## 4. Türkiye: facility status

### 4.1 Institutional change
- **TÜBİTAK National Observatory (TUG) has been restructured.**
  - The Türkiye National Observatories history page says the new body "qualified" on **25 April 2023**. It is a shared research infrastructure under Law 6550, formed by TÜBİTAK and Atatürk University (ATASAM).
  - The 2026 press brochure ("Türkiye's Windows to the Universe", Y2026-02) describes it as "restructured in 2023 as a Joint Research Infrastructure".
- **New website.** The old site `tug.tubitak.gov.tr` now redirects, for every path, to `gge.tubitak.gov.tr`, a public sky-observation-event application system. The current site is **trgozlemevleri.gov.tr**.
- **Telescopes.** The 2026 website lists six "modern telescopes":
  - Antalya: RTT150, TUG100, TUG060.
  - Erzurum: DAG400, ATA050, DAGTPS.
- **Observing time** is allocated in semesters. The 2025A list of accepted projects shows RTT150 (7 projects), TUG100 (12), TUG060 (2), ATA050 (3), DAGTPS (1) and **DAG400 (none)**. None of these projects involves lunar or high-speed photometry.

### 4.2 Sites (from the official campus pages)

| Site | Coordinates | Altitude | Clear nights/yr | Seeing | Sky brightness | Seasonal |
|---|---|---|---|---|---|---|
| **TUG, Bakırlıtepe (Antalya)** | 36°49′27″N, 30°20′08″E | 2550 m | 200 | 0.86″ | 21.5 mag/arcsec² | Snow ~5 months/yr (average 1.5 m); −28 to +22 °C |
| **DAG, Karakaya Tepesi (Konaklı, Erzurum)** | 39°46′43″N, 41°13′37″E | 3170 m | 240 | 0.93″ | 21.4–21.8 mag/arcsec² | Snow ~7 months/yr (average 3.5 m, up to 7 m); −26 to +25 °C; 1 Gbit/s fibre |

- **MPC cross-check.** MPC code A84 (TUBITAK National Observatory) converts to 36.8253°N, 30.3333°E, 2539 m. That is 0.24 km from the official position, with a height difference of −11 m.
- **Altitude discrepancy.** Published altitudes for TUG differ:
  - 2550 m: official site, 2026.
  - 2500 m: astropy registry, citing the old TUG page.
  - 2450 m: Wikipedia.
- **DAG has no MPC code** in the mirror list.

### 4.3 Telescopes and their relevance to the impact
- **RTT150** (1.5 m RC; Cassegrain f/7.7, 13.3′ field):
  - Instruments: TFOSC, an Andor DW436 CCD and an **Andor iXon+ EMCCD**.
  - The iXon+ is the obvious fast camera at TUG. Its model, frame rate, triggering and current mounting are unverified.
  - RTT150 is a Russian–Turkish collaboration telescope.
- **TUG100** (1.0 m):
  - The main imager is an SI 1100 CCD with 21.5′ field and 0.31″/px. Readout is 48 s, or 13 s binned, so it is too slow for the flash.
  - Its **autoguider is a GPS-timed, global-shutter QHY174GPS** (3.86′×2.42′ field). This is the only fast camera in Türkiye with verified GPS timing, and it is already on a 1-m telescope.
- **TUG060** (0.6 m): Andor iKon-L, 15.6′ field, 6 s readout. Candidate only.
- **Legacy TUG telescopes:** T35, YT40 and ROTSE-IIId are **not listed** on the 2026 site. Their status is uncertain.
- **DAG400** (4.0 m RC, alt-az, f/14.2): **in commissioning.**
  - Instruments: field of 24′×24′ seeing-limited and 7′×7′ diffraction-limited; KORAY K-mirror rotator; TROIA adaptive optics (pyramid sensor, ALPAO 468-actuator mirror); DIRAC camera (H1RG, 0.9–2.4 µm, 33″ field, 33 mas/px); PLACID coronagraph.
  - Status evidence:
    - Technical first light in 2024 and initial testing completed in September 2025 (Wikipedia, citing SPIE 13094 and 13624).
    - "Test observations began in 2025" (TUG press, February 2026).
    - No DAG400 projects were accepted in 2025A.
    - The history page still says the opening "will be in 2025".
  - **Science-operation status in October 2026 is unverified.**
  - No visible-light fast imager is documented. A visitor camera on the seeing-limited field would be needed.
  - DIRAC's K band matches the band in which CFHT detected SMART-1. Its 33″ field covers only about 60 km on the Moon.
- **ATA050** (0.5 m, DAG campus): QHY268M CMOS; exposures from 30 µs. The published field size (26.3′×6.3′) does not match the sensor; I compute about 20′×14′ at 0.19″/px.
- **DAGTPS** (two 0.3 m telescopes): G-DIMM / MASS-DIMM seeing monitors with a DMK 33UX290 camera at 143 fps (rolling shutter, no GPS). Fast, but dedicated to site monitoring.
- **UDF050 SSA telescopes:** the 2026 brochure says 0.5 m space-situational-awareness telescopes will be installed at both sites "by 2026". **Installation is not verified.** If they carry fast CMOS cameras with GPS timing, as is common for satellite tracking, they may be the best-suited new Turkish assets.
- **University observatories:**
  - **Ankara University Kreiken (AUKR):** 39°50′37″N, 32°46′45″E, 1257 m.
    - T80: 0.805 m ASA RC, alt-az Nasmyth; Apogee U47+ camera; 11.8′ field.
    - T40 Kreiken: QHY268M Pro camera.
    - T35: Meade 14″; camera unverified.
  - **ÇOMÜ Ulupınar (Çanakkale):** 410 m, 10 km from Çanakkale; latitude and longitude unverified.
    - T122: Cassegrain–Nasmyth, SBIG STL-1001E, 7.1′ field. The page gives inconsistent figures (1022 mm, f/10).
    - **IST60** (Istanbul University): Andor iXon Ultra 888 EMCCD, 9.5′ field.
    - T40 and T30a (robotic) also on site.
  - **Ege University (Kurudağ, İzmir):**
    - R40: Apogee U42, 23.7′ field.
    - T35: SSP5 photomultiplier photometer.
  - **Adıyaman:** ADYU60, a PlaneWave CDK24.
  - **Çukurova:** UZAYMER RC500 (0.5 m); specifications not rendered.
  - **Erciyes:** UZAYBİMER T40 and T35; specifications not rendered; no 1-m telescope found.
  - **İnönü and Eskişehir Technical University (Yunus Emre):** websites unreachable.
  - **Kandilli (Boğaziçi):** historic and solar instruments only; not relevant.
- **Science centres and amateurs:**
  - The Konya and Kayseri science-centre websites list planetaria but no observatory or telescope.
  - Bursa: DNS failure.
  - Antalya, Eskişehir Sabancı Space House, İstanbul Planetarium and Gaziantep were not verified.
  - Türk Astronomi Derneği (TAD) is a professional society (IAU national committee; publishes TJAA) and runs IMO fireball reporting. No amateur telescope network was verified.

---

## 5. International facilities: key notes

- **Greece:**
  - **NELIOTA** (GR01) is above.
  - Kryoneri installed a new **ASA800 0.8 m** robotic telescope in April–May 2026 (GR02); its cameras are unverified.
  - The site's coordinates are confirmed against MPC code L10 (30 m apart; height difference +41 m).
- **Spain, MIDAS:**
  - Sevilla station: 37.34611°N, 5.98055°W, 23 m.
  - La Hita: 39.56833°N, 3.18333°W, 674 m. This matches MPC code I95 to within 0.24 km.
  - Equipment: Celestron SCTs with f/3.3 reducers; Watec 902H Ultimate cameras (PAL 25 fps, 720×576); GPS time inserter at 0.01 s.
  - The terminator is avoided to prevent saturation, and a detection must be seen by ≥2 telescopes.
  - La Sagra is named as a station in the 2019 paper (instruments unverified). Calar Alto's role in MIDAS is unverified.
- **Canary Islands:**
  - **GTC/HiPERCAM:** see §3.
  - **Liverpool Telescope / RISE:** see §3.
  - **TTT (Light Bridges):** see §3.
  - **NOT:** no dedicated fast imager is offered. DIPol-UF, a high-speed polarimeter, is a visitor instrument.
  - **WHT and INT are effectively unavailable for imaging.**
    - WHT offers only WEAVE. INT offers only HARPS3.
    - ACAM, ISIS, LIRIS and PF-QHY are not offered.
    - HiPERCAM and ULTRACAM are listed as "formerly visitor" instruments.
  - TCS has been open to the Spanish time-allocation committee (CAT) since 2024A. IAC80 has not been offered through the CAT since 2013A. TNG and the ESA Optical Ground Station were not verified.
  - **CAT calls:** deadlines were 3 Oct 2025 (for 2026A) and 3 Apr 2026 (for 2026B), with director's discretionary time also available. A 2027–2028 campaign would fall under the 2027B/2028A calls; this is inferred from the pattern.
- **Southern Africa:**
  - **SHOC** (Andor iXon 888) now runs only on the 1.0 m (ZA01). It can be mounted on the 1.9 m (1.29′ field, or 2.79′ with reducer) and on Lesedi (5.72′ field).
  - **SALTICAM** can reach 0.05 s in slot mode. SALT's fixed-elevation tracking constraints were not verified.
  - Kottamia 1.88 m (Egypt): 29.933564°N, 31.828223°E, 450 m; ~250 clear nights/yr; matches MPC 088 to within 0.07 km. Its longitude is close to Türkiye's.
  - TRAPPIST-North (Oukaïmeden): 1.8–5 s readout, too slow.
  - Entoto (Ethiopia) and Boyden (South Africa): unverified.
- **Hawaii:**
  - CFHT/WIRCam: precedent (see §3). The instrument index page appears outdated, so 2026 status is unverified.
  - **IRTF/MORIS:** Andor iXon Ultra 897 (since November 2016), co-mounted with SpeX, with a TM-4 GPS unit. Frame rate and field of view were not retrieved, because the manual timed out. Simultaneous visible and near-infrared imaging is attractive for flash temperature.
  - Gemini North ('Alopeke): gemini.edu returned 403.
  - Subaru: unverified.
  - LCO 2 m FTN with MuSCAT3: 4 bands, 9.1′ field, 6 s overhead per frame. Suitable only for slow ejecta imaging.
- **Continental US:**
  - APO Agile: status uncertain.
  - Palomar CHIMERA: pages returned 403/404; unverified.
- **Chile:**
  - **ULTRACAM status is uncertain.** ESO's 2026 La Silla instrument list shows the NTT with SOXS (Nasmyth A) and EFOSC2 (Nasmyth B) only.
  - VLT HAWK-I: 7.5′ field, 0.106″/px, includes a 2.12 µm H₂ filter. Fast modes not verified.
  - Danish 1.54 m: DFOSC; its EMCCD camera is unverified.
  - SOAR, Blanco/DECam and Las Campanas: unverified.
- **Asia:**
  - TNT/ULTRASPEC: see §3. Note that the telescope is closed during the May–October monsoon.
  - Seimei/TriCCS: see §3.
  - Tomo-e Gozen: see §3. Kiso's rainy season is June–September.
- **Oceania:** Siding Spring (AAT, ANU 2.3 m, LCO FTS) and Mt John were not verified beyond MPC coordinates.
- **Networks and portable stations:**
  - LCO 1 m Sinistro (28 s overhead) and 0.4 m QHY600 (4 s overhead) are too slow for the flash.
  - Unistellar runs occultation, planetary-defence, exoplanet, comet and satellite campaigns, but **no lunar programme**. Its hardware specifications are not on the science site.
  - Two portable templates are included:
    - QHY174M-GPS class camera: 138 fps, 1 µs GPS timestamps (GL04).
    - MIDAS-type Watec camera plus GPS inserter (GL05).
  - FRIPON-type all-sky meteor cameras were not included. They are not telescopic and cannot reach lunar-flash magnitudes.

---

## 6. Verification notes

### 6.1 Coordinate cross-checks
All values are in `facilities.csv`, column `mpc_crosscheck`.
- **Agreement where an independent primary source exists:**
  - TUG vs MPC A84: 0.24 km, −11 m.
  - Kryoneri vs MPC L10: 0.03 km, +41 m.
  - La Hita vs MPC I95: 0.24 km, +1 m.
  - Kottamia vs MPC 088: 0.07 km, +44 m.
  - Teide (TTT) vs MPC 954: 0.09 km.
  - Okayama vs MPC 371: 0.42 km.
- **Discrepancies:**
  - **TNT:** Dhillon et al. (2014) give 18.573725°N, 98.482194°E. The astropy registry, which cites Wikipedia, gives 18.5906°N, 98.4867°E, 1.9 km away. I adopted the paper's value.
  - **Haleakalā:** the astropy generic entry is 9 km from MPC F65. I adopted MPC.
  - **Las Campanas:** the astropy entry is 1.6 km from MPC 304. I adopted MPC.
  - **Heights derived from MPC** can differ from official values by up to ~100 m, because of the precision of the parallax constants. Examples: NOT −98 m and Las Campanas −103 m relative to generic registry values.

### 6.2 Data inconsistencies found in sources
- **Ulupınar T122:** the name says 122 cm, but the page lists aperture 1022 mm and focal length 10220 mm at f/10. The detector scale implies a focal length of about 11.8 m.
- **ATA050:** the published field of 26.3′×6.3′ does not match the APS-C sensor at f/8.
- **DAGTPS:** the published field of 5.4′×3.7′ is smaller than computed for an IMX290 at 3.0 m focal length (6.4′×3.6′).
- **Kryoneri:** the WebFetch helper labelled the 1.2 m as "Aristarchos". That is the name of NOA's 2.3 m telescope at Helmos, so the label was rejected. The mount details returned probably belong to the new ASA800.
- **CFHT:** the helper said 2.122 µm is "H band". It is in the **K band**, and the CSV uses the correct band.
- **CFHT and APO:** both instrument index pages appear outdated (CFHT lists long-retired instruments; the Agile page was last updated in 2016).

### 6.3 Facilities whose 2026 status is uncertain or not operational
- **TUG:** T35, YT40 and ROTSE-IIId (not listed in 2026).
- **DAG400:** commissioning; science operations unverified.
- **UDF050 SSA telescopes:** planned for 2026; installation unverified.
- **İnönü and ESTÜ Yunus Emre** observatories.
- **TTT3 and TTT4:** commissioning.
- **APO Agile.**
- **NTT/ULTRACAM.**
- **Tomo-e Gozen:** status page stale.
- **Entoto.**
- **WHT and INT:** operational, but they offer no imaging instrument.

---

## 7. Gaps and recommended follow-ups (direct contact needed)

1. **Türkiye National Observatories:**
   - RTT150 iXon+: model, frame rate, GPS triggering, availability.
   - TUG100 QHY174GPS: can it be used as a science camera with a filter, and what is the data path?
   - DAG400: science-operations date, free visible port, Moon-pointing and adaptive-optics policy, whether DIRAC can take fast frames.
   - UDF050 SSA telescopes: installation date and camera specifications.
   - Time-of-opportunity (ToO) and director's time rules.
2. **ÇOMÜ / İstanbul University:**
   - IST60 iXon 888: frame rate and triggering.
   - Exact coordinates of Ulupınar.
   - The T122 aperture discrepancy.
3. **NOA/ESA (NELIOTA):**
   - Collaboration terms for 2027–2028.
   - Whether non-standard lunar phases or pointing at a specific impact site are possible, given that NELIOTA observes at phase 10–45% and elevation ≥20°.
   - The 2024 statistics.
4. **Fast-camera facilities to confirm for 2027–2028:**
   - MIDAS: current stations.
   - SHOC: mounting options.
   - ULTRASPEC: status, and the monsoon window.
   - HiPERCAM: GTC Moon policy, and the 2027B/2028A calls.
   - TTT: Moon policy and timing.
   - TriCCS: GPS fix for header time.
   - MORIS: frame rate and field of view.
   - ULTRACAM: whether it can be mounted after SOXS took the NTT's Nasmyth A focus.
5. **Not retrieved at all:**
   - Gemini 'Alopeke/Zorro and Palomar CHIMERA specifications (blocked).
   - Mt John, AAT/ANU, Subaru, SOAR, Blanco and Las Campanas instruments.
   - Clear-night fractions for most non-Turkish sites.
   - The Turkish science centres other than Konya and Kayseri.
6. **Precedent:** IRTF and APO participation in the 2009 LCROSS campaign was not verified in this pass.

---

## 8. URL log (access date 2026-10-05 for all entries)

Outcome codes:
- OK: content retrieved.
- PARTIAL: some content retrieved.
- REDIRECT: URL redirected.
- FAIL: with a reason.

Totals: 143 logged attempts. 97 OK (some returned only names or links). 2 partial or inconclusive. 4 redirects. 40 failures.

| # | URL | Tool | Outcome | Key facts extracted | Accessed |
|---|---|---|---|---|---|
| 1 | https://www.minorplanetcenter.net/iau/lists/ObsCodes.html | WebFetch | PARTIAL (page truncated by renderer; numeric codes + some lettered codes returned verbatim: A84, 080, 087, 088, 074, 304, 309, 371, 381, 413, 474, 493, 566, 568, 645, 675, 705, 807, 809, 950, 954, B31; later lettered codes not returned) | A84 TUBITAK National Observatory 30.3333 0.80175 +0.59632 | 2026-10-05 |
| 2 | https://www.minorplanetcenter.net/iau/lists/ObsCodes.html (curl) | Bash curl | FAIL 403 egress policy | - | 2026-10-05 |
| 3 | https://raw.githubusercontent.com/oorb/oorb/master/data/OBSCODE.dat | Bash curl | OK (2717-line mirror of the MPC ObsCodes list; used for lettered codes; parallax constants converted to geodetic lat/h on WGS84) | see facilities.csv mpc_code / mpc_crosscheck columns | 2026-10-05 |
| 4 | https://raw.githubusercontent.com/astropy/astropy-data/gh-pages/coordinates/sites.json | Bash curl | OK (astropy site registry; independent cross-check) | tug 36.824166 30.335555 2500 m; TNO 18.5906 98.4867 2457 m; CAHA 37.2236 -2.5461 2168 m; etc. | 2026-10-05 |
| 5 | https://tug.tubitak.gov.tr/ | WebFetch | REDIRECT 302 -> https://gge.tubitak.gov.tr/ ('Gökyüzü Gözlem Etkinliği Başvuru Sistemi'); all tug.tubitak.gov.tr paths redirect | old TUG site no longer serves telescope pages | 2026-10-05 |
| 6 | https://gge.tubitak.gov.tr/ | WebFetch | OK but JS-only shell (title only) | - | 2026-10-05 |
| 7 | https://tug.tubitak.gov.tr/en | WebFetch | REDIRECT 302 -> gge.tubitak.gov.tr | - | 2026-10-05 |
| 8 | https://web.archive.org/web/2025/https://tug.tubitak.gov.tr/en | WebFetch | FAIL SITE_BLOCKED | - | 2026-10-05 |
| 9 | https://export.arxiv.org/api/query?search_query=all:%22Eastern%20Anatolia%20Observatory%22... | WebFetch | FAIL robots.txt | - | 2026-10-05 |
| 10 | https://arxiv.org/search/?query=%22Eastern+Anatolia+Observatory%22&searchtype=all | WebFetch | FAIL robots.txt | - | 2026-10-05 |
| 11 | https://api.openalex.org/works?search=NELIOTA%20lunar%20impact%20flashes... | WebFetch | FAIL HTTP 429 | - | 2026-10-05 |
| 12 | https://api.crossref.org/works?query=NELIOTA+lunar+impact+flashes... | WebFetch | FAIL proxy 429 rate limit | - | 2026-10-05 |
| 13 | http://hea.iki.rssi.ru/rtt150/en/ | WebFetch | FAIL timeout | - | 2026-10-05 |
| 14 | https://en.wikipedia.org/wiki/T%C3%9CB%C4%B0TAK_National_Observatory | WebFetch | OK (pointer only) | 36.82417N 30.33556E; alt 2450 m (Wikipedia); RTT150 2001, T100 2009, T60 2008, YT40 2006, ROTSE-IIId | 2026-10-05 |
| 15 | https://en.wikipedia.org/wiki/Eastern_Anatolia_Observatory (2 queries) | WebFetch | OK (pointer only) | 39.783N 41.233E 3170 m; 'technical first light in 2024, and completed initial testing in September 2025'; refs SPIE 13094 (2024) 'DAG telescope first light commissioning status', SPIE 13624 (2025), TUG press PDF (2026) | 2026-10-05 |
| 16 | https://atasam.atauni.edu.tr/ | WebFetch | OK (links only) | - | 2026-10-05 |
| 17 | https://atasam.atauni.edu.tr/dag/ | WebFetch | OK but outdated (construction 2012-2019) | 4 m, VIS+NIR <3 micron, Karakaya ridges | 2026-10-05 |
| 18 | https://iccecrice2026.org/Docs/Turkiye-National-Observatories.pdf (3 queries) | WebFetch | OK | 'Türkiye's Windows to The Universe', Türkiye National Observatories Press Y2026-02; restructured 2023 as joint research infrastructure (Atatürk Univ.+TÜBİTAK); TUG 2550 m; DAG 3170 m; 6-telescope table (f-ratio column mislabelled 'focal length'); 'Test observations began in 2025'; 0.5 m SSA telescopes (UDF050) to be installed by 2026; web trgozlemevleri.gov.tr | 2026-10-05 |
| 19 | https://trgozlemevleri.gov.tr/ | WebFetch | OK | 6 telescopes: DAG400, ATA050, DAGTPS (Erzurum); RTT150, TUG100, TUG060 (Antalya) | 2026-10-05 |
| 20 | https://trgozlemevleri.gov.tr/tr/teleskoplar/erzurum/dag400 | WebFetch | OK | 4.0 m RC alt-az f/14.2; FoV 24'x24' seeing-limited, 7'x7' diffraction-limited; KORAY K-mirror; DIRAC H1RG 1016x1016 0.9-2.4 um 33 mas/px 33"x33"; TROIA AO (pyramid WFS, ALPAO 468 act.); PLACID coronagraph | 2026-10-05 |
| 21 | https://trgozlemevleri.gov.tr/tr/teleskoplar/antalya/rtt150 (2 queries) | WebFetch | OK | 1.5 m RC equatorial; Cass f/7.7 (11611 mm) 13.3'x13.3' 17.8"/mm; TFOSC, Andor iXon+ EMCCD, Andor DW436; Coude f/48; >40 filters incl. UBVRI, ugriz, ND 0.5/1/2 | 2026-10-05 |
| 22 | https://trgozlemevleri.gov.tr/tr/teleskoplar/antalya/tug100 | WebFetch | OK | 1.0 m RC f/10 ACE equatorial; SI1100 4096x4037 15um 0.31"/px 21.5'x21.5' readout 48 s (1x1) 13 s (2x2), exp from 1 ms; QHY174GPS guider IMX174 1920x1200 0.12"/px 3.86'x2.42' | 2026-10-05 |
| 23 | https://trgozlemevleri.gov.tr/tr/teleskoplar/antalya/tug060 | WebFetch | OK | 0.6 m RC f/10; Andor iKon-L 936 2048x2048 13.5um 0.456"/px 15.6'x15.6' download 6 s | 2026-10-05 |
| 24 | https://trgozlemevleri.gov.tr/tr/teleskoplar/erzurum/ata050 | WebFetch | OK | 0.5 m RC f/8 equatorial; QHY268M (IMX571, 3.76 um), exp 30 us-3600 s; FOV given as 26.3'x6.3' (sic); UVEX and eShel spectrographs; at 'Erzurum DAG yerleşkesi' | 2026-10-05 |
| 25 | https://trgozlemevleri.gov.tr/tr/teleskoplar/erzurum/dagtps | WebFetch | OK | 2x0.3 m ACF f/10 alt-az; FOV 5.4'x3.7'; GDIMM w/ DMK 33UX290 (IMX290 1920x1080, 143 fps, rolling shutter) | 2026-10-05 |
| 26 | https://trgozlemevleri.gov.tr/tr | WebFetch | OK (link list) | campus pages, telescope pages, projects, announcements | 2026-10-05 |
| 27 | https://trgozlemevleri.gov.tr/tr/projeler/gozlem | WebFetch | OK (2 queries) | 2025A accepted projects: RTT150 7, TUG100 12, TUG060 2, ATA050 3, DAGTPS 1, DAG400 none; no lunar/fast-photometry projects | 2026-10-05 |
| 28 | https://trgozlemevleri.gov.tr/tr/yerleskeler/antalya-tug | WebFetch | OK | 36°49'27"N 30°20'08"E 2550 m; sky 21.5 mag/arcsec2; seeing 0.86"; 200 clear nights/yr; snow 5 months avg 1.5 m; -28..+22 C | 2026-10-05 |
| 29 | https://trgozlemevleri.gov.tr/tr/yerleskeler/erzurum-dag | WebFetch | OK | 39°46'43"N 41°13'37"E 3170 m; sky 21.4-21.8; seeing 0.93"; 240 clear nights/yr; snow 7 months avg 3.5 m; 1 Gbit/s fibre | 2026-10-05 |
| 30 | https://trgozlemevleri.gov.tr/tr/duyurular/gozlem | WebFetch | OK but list JS-rendered (no items) | - | 2026-10-05 |
| 31 | https://trgozlemevleri.gov.tr/tr/haberler | WebFetch | OK but list JS-rendered (no items) | - | 2026-10-05 |
| 32 | https://trgozlemevleri.gov.tr/tr/kurumsal/tarihce | WebFetch | OK | TUG est. 1997 at 2550 m; TÜBİTAK+ATASAM joint research infrastructure (Law 6550) qualified 25 Apr 2023; 'DAG ... kurulumu 2024'te tamamlanmış ve 2025 yılında açılışı yapılacak' | 2026-10-05 |
| 33 | https://gozlemevi.comu.edu.tr/ | WebFetch | FAIL DNS | - | 2026-10-05 |
| 34 | https://www.comu.edu.tr/ | WebFetch | OK (no observatory link found) | - | 2026-10-05 |
| 35 | https://en.wikipedia.org/wiki/Ulup%C4%B1nar_Observatory | WebFetch | FAIL (Wikipedia cache-only; page not cached) | - | 2026-10-05 |
| 36 | https://rasathane.ankara.edu.tr/ (2 queries) | WebFetch | OK | telescope list: T80, T40 Kreiken, T35 Meade 14", Coude, 3x Meade 8", ETX-125, SolarMax II; address İncek Bulvarı Ahlatlıbel Ankara | 2026-10-05 |
| 37 | https://gozlemevi.istanbul.edu.tr/ | WebFetch | FAIL (metadata only; JS) | - | 2026-10-05 |
| 38 | https://uzaybimer.erciyes.edu.tr/ | WebFetch | OK (names only) | RT13 & RT5 radio telescopes, T40 optical, T35, portable telescopes | 2026-10-05 |
| 39 | https://uzaybimer.erciyes.edu.tr/tr/t40-optik-teleskop | WebFetch | OK but no specs rendered | - | 2026-10-05 |
| 40 | https://rasathane.ankara.edu.tr/t80-prof-dr-berahitdin-albayrak-teleskobu/ | WebFetch | OK | ASA 805 mm RC alt-az Nasmyth f/6.8 (5476 mm); Apogee Alta U47+ 1024x1024 13um; 11.84'x11.84' w/ 0.69x reducer; SDSS ugriz; Whoppshel fibre spectrograph | 2026-10-05 |
| 41 | https://rasathane.ankara.edu.tr/kreiken-teleskobu/ | WebFetch | OK | Meade 406 mm f/10 (4064 mm) 51"/mm; QHY268M Pro 6280x4210 3.76um; eShel; UBVRI, uvby | 2026-10-05 |
| 42 | https://observatory.comu.edu.tr/ | WebFetch | FAIL DNS | - | 2026-10-05 |
| 43 | https://neliota.astro.noa.gr/ | WebFetch | FAIL too many redirects | - | 2026-10-05 |
| 44 | https://neliota.astro.noa.gr/About | WebFetch | FAIL too many redirects | - | 2026-10-05 |
| 45 | https://kryoneri.astro.noa.gr/ (2 queries) | WebFetch | OK | 37°58'19"N 22°37'07"E; 1.2 m prime-focus telescope, robotic (helper's 'Aristarchos' label rejected - that is NOA's 2.3 m at Helmos); NELIOTA (ESA) since 2015, 'resumed August 2025, continuing through 2028'; new ASA800 0.8 m f/6.5 robotic telescope installed Apr-May 2026; visitor centre closed for construction | 2026-10-05 |
| 46 | https://kryoneri.astro.noa.gr/για-τους-παρατηρητές/ | WebFetch | OK (document list only) | user manual PDF; contact NOA before arrival | 2026-10-05 |
| 47 | https://ui.adsabs.harvard.edu/abs/2018A&A...619A.141X/abstract | WebFetch | OK | Xilouris et al. 2018 A&A 619 A141, arXiv:1809.00495; FOV 17.0'x14.4'; flash limit ~12.4 mag; 31 flashes first year | 2026-10-05 |
| 48 | https://arxiv.org/pdf/1809.00495 | WebFetch | OK | Zyla 5.5 sCMOS x2, 2x2 bin 1280x1080, 0.8"/px, 30 fps (23 ms exp + 10 ms), dichroic 730 nm, R & I, Meinberg LanTime M200/GPS NTP + hardware timestamps; elev limit 20 deg; phase 10-45%; 37°58'19"N 22°37'07"E 930 m; 54 h, 31 validated flashes Feb 2017-Feb 2018 | 2026-10-05 |
| 49 | https://ui.adsabs.harvard.edu/abs/2020A&A...633A.112L/abstract | WebFetch | FAIL robots.txt fetch (x2) | - | 2026-10-05 |
| 50 | https://api.semanticscholar.org/graph/v1/paper/search?... | WebFetch | FAIL 429 | - | 2026-10-05 |
| 51 | https://arxiv.org/a/liakos_a_1 | WebFetch | FAIL proxy 429 | - | 2026-10-05 |
| 52 | https://ui.adsabs.harvard.edu/abs/2019MNRAS.486.3380M/abstract | WebFetch | OK | Madiedo et al. 2019 MNRAS 486 3380, arXiv:1905.04487; flash 21 Jan 2019 04:41:38.09 UT, 0.28 s, peak V=4.2, ~5700 K | 2026-10-05 |
| 53 | https://arxiv.org/pdf/1905.04487 (2 queries) | WebFetch | OK | MIDAS: Sevilla, La Sagra, La Hita; Sevilla: 2x0.36 m + 3x0.28 m (+0.24 m) f/10 SCTs w/ Watec 902H Ultimate + GPS time inserter (400-900 nm), 0.10 m refractors w/ Sony A7S (50 fps video); I filter on one 0.28 m; requires >=2 instruments for confirmation; no frame rate/coords stated | 2026-10-05 |
| 54 | https://ui.adsabs.harvard.edu/abs/2015A&A...577A.118M/abstract | WebFetch | FAIL robots.txt fetch | - | 2026-10-05 |
| 55 | https://www.gtc.iac.es/instruments/hipercam/hipercam.php | WebFetch | OK | HiPERCAM 5 bands u'g'r'i'z'; FOV 2.8'x1.4'; 0.081"/px; >1050 Hz windowed; visitor instrument, permanent home at GTC Folded-Cass since 2023; first light on GTC Feb 2018 | 2026-10-05 |
| 56 | https://telescope.livjm.ac.uk/TelInst/Inst/ | WebFetch | OK | operational: IO:O, LOCI, RISE, SPRAT, FRODOSpec(offline), MOPTOP, LIRIC, SkyCam | 2026-10-05 |
| 57 | https://telescope.livjm.ac.uk/TelInst/Inst/RISE/ | WebFetch | OK | RISE: Andor DW485 e2v CCD47-20 frame transfer 1024x1024; 9.2'x9.2'; 0.54"/px; min exp 1.2 s (1x1) / 0.6 s (2x2); V+R filter; NTP to stratum-1 GPS <70 ms, FITS timestamps not better than 90 ms; ONLINE | 2026-10-05 |
| 58 | https://gozlemevi.istanbul.edu.tr/tr/_ | WebFetch | FAIL (metadata only) | - | 2026-10-05 |
| 59 | https://www.saao.ac.za/astronomers/shoc/ | WebFetch | OK | SHOC Andor iXon 888 EMCCD frame transfer 1024x1024 13um; min cycle ~0.5 s full frame, 0.01 s windowed/binned; 1.0 m 2.85'x2.85' 0.167"/px; 1.9 m 1.29' (2.79' w/ reducer); Lesedi 5.72'; 'now operate exclusively on the 1.0-m' | 2026-10-05 |
| 60 | https://www.saao.ac.za/astronomers/ | WebFetch | OK (names only) | 1.9m, 1.0m, Lesedi, IRSF, PRIME, SALT; instruments SpUpNIC, HIPPO, SHOC, STE3/STE4, Sibonise, Mookodi | 2026-10-05 |
| 61 | https://topswiki.saao.ac.za/index.php/SHOC | WebFetch | OK | GPS POP triggering (internal/external/external start); readout 1-10 MHz; mountable on 1.9 m, 1.0 m, Lesedi | 2026-10-05 |
| 62 | https://irtfweb.ifa.hawaii.edu/~moris/ | WebFetch | OK (history only) | iXon Ultra (USB) since 2016, co-mounted with SpeX | 2026-10-05 |
| 63 | https://irtfweb.ifa.hawaii.edu/~moris/user/ | WebFetch | OK (doc list) | Andor iXon Ultra 897 in use since Nov 2016 | 2026-10-05 |
| 64 | https://www.apo.nmsu.edu/arc35m/Instruments/ | WebFetch | FAIL 404 | - | 2026-10-05 |
| 65 | https://www.apo.nmsu.edu/arc35m/ (2 queries) | WebFetch | OK (labels only) | - | 2026-10-05 |
| 66 | https://www.apo.nmsu.edu/arc35m/Instruments/AGILE/ | WebFetch | OK (page last updated 23 Feb 2016) | Agile e2v CCD47-20 frame transfer 1024x1024; 2.2'x2.2' w/ reducer, 0.258"/px (2x2); ~1.1 s full frame at 1 MHz; GPS hardware trigger, ~1 ms absolute timing | 2026-10-05 |
| 67 | https://www.eso.org/sci/facilities/lasilla/instruments/ultracam.html | WebFetch | FAIL 404 | - | 2026-10-05 |
| 68 | https://www.vikdhillon.staff.shef.ac.uk/ultracam/ | WebFetch | FAIL TLS hostname mismatch | - | 2026-10-05 |
| 69 | https://www.eso.org/sci/facilities/lasilla/instruments.html | WebFetch | OK | La Silla offered: 3.6m EFOSC2/HARPS/NIRPS; NTT SOXS (Nasmyth A), EFOSC2 (Nasmyth B); 2.2m GROND; ULTRACAM not listed | 2026-10-05 |
| 70 | https://ui.adsabs.harvard.edu/abs/2014MNRAS.444.4009D/abstract | WebFetch | FAIL robots.txt fetch | - | 2026-10-05 |
| 71 | https://arxiv.org/abs/1408.2733 | WebFetch | OK | ULTRASPEC on TNT: 1024x1024 frame-transfer EMCCD, 7.7'x7.7', up to ~200 Hz, 330-1000 nm, first light Nov 2013 | 2026-10-05 |
| 72 | https://arxiv.org/pdf/1408.2733 | WebFetch | OK | 0.45"/px; full frame 3.8-12.8 s; dead time 14.9 ms (0.3 ms drift); GPS timestamps <1 ms; TNT 2.4 m RC f/10 alt-az Nasmyth, 4 deg/s slew; 18.573725N 98.482194E 2457 m; season Nov-Apr; ~75% clear in peak season; seeing ~0.9" | 2026-10-05 |
| 73 | https://www.kusastro.kyoto-u.ac.jp/psmt/ | WebFetch | OK (page no longer updated) | Seimei 3.8 m segmented, completed 17 Aug 2018 | 2026-10-05 |
| 74 | http://www.o.kwasan.kyoto-u.ac.jp/inst/triccs/ | WebFetch | OK | TriCCS shared-risk in 2027A; 18-month proprietary period | 2026-10-05 |
| 75 | https://www.o.kwasan.kyoto-u.ac.jp/inst/triccs/inst-info/index.html | WebFetch | OK | g2,r2,i2 or g2,r2,z simultaneous; max 98 fps full frame (2027A); partial readout not offered; 'absolute time in the fits header is occasionally inaccurate' | 2026-10-05 |
| 76 | https://www.o.kwasan.kyoto-u.ac.jp/inst/triccs/image/index.html | WebFetch | OK (no numbers) | - | 2026-10-05 |
| 77 | https://tomoe.mtk.ioa.s.u-tokyo.ac.jp/ | WebFetch | OK | 84 CMOS, 190 Mpix, 20 deg2; 2 fps full / 160 fps partial; GPS absolute time 0.2 ms; ~17 mag per frame | 2026-10-05 |
| 78 | https://tomoe.mtk.ioa.s.u-tokyo.ac.jp/status.html | WebFetch | OK (stale: data to Oct 2021) | rainy season Jun-Sep | 2026-10-05 |
| 79 | https://www.gemini.edu/instrumentation/alopeke-zorro | WebFetch | FAIL 403 | - | 2026-10-05 |
| 80 | https://lco.global/observatory/instruments/ | WebFetch | OK | MuSCAT3 9.1' 0.27"/px overhead 6 s; Sinistro 26' 0.389"/px overhead 28 s; 0.4 m QHY600 1.9x1.2 deg 0.74"/px overhead 4 s; NRES not offered from 2026B | 2026-10-05 |
| 81 | https://www.unistellar.com/citizen-science/ | WebFetch | REDIRECT -> science.unistellar.com | - | 2026-10-05 |
| 82 | https://science.unistellar.com/ | WebFetch | OK | programmes: occultations, planetary defense, exoplanets, comets, cosmic cataclysms, satellites (no lunar impact programme); no specs on page | 2026-10-05 |
| 83 | https://gozlemevi.ege.edu.tr/ | WebFetch | OK | telescopes R40 and T35; Bornova, İzmir; weather monitor + all-sky camera | 2026-10-05 |
| 84 | https://gozlemevi.ege.edu.tr/tr-4305/r40.html | WebFetch | OK | R40: 0.4 m SCT f/10 on ASA DDM160; Apogee Alta U42 2048x2048 13.5um 0.70"/px 23.7'x23.7'; Bessell UBVRI | 2026-10-05 |
| 85 | https://gozlemevi.ege.edu.tr/tr-4307/t35.html | WebFetch | OK | T35: Meade LX200GPS 14" f/10 fork; SSP5 PMT photometer (R6358), 53" aperture; Johnson UBVR; calibrations 2019-2023 | 2026-10-05 |
| 86 | https://astrofizik.comu.edu.tr/ | WebFetch | FAIL DNS | - | 2026-10-05 |
| 87 | https://www.nriag.sci.eg/ | WebFetch | OK (links) | - | 2026-10-05 |
| 88 | https://www.nriag.sci.eg/overview-at-kottamia-astronomical-observatory/ | WebFetch | OK | 29.933564N 31.8282231E 450 m; 74-inch (1.88 m) Grubb Parsons; ~250 clear nights/yr; est. 1964; also 14-inch Celestron | 2026-10-05 |
| 89 | https://ssgi.gov.et/ | WebFetch | FAIL (metadata only) | - | 2026-10-05 |
| 90 | https://www.trappist.uliege.be/cms/c_5006041/en/trappist-portail | WebFetch | FAIL 404 | - | 2026-10-05 |
| 91 | https://www.trappist.uliege.be/ | WebFetch | OK (links) | TRAPPIST-Nord at Oukaimeden | 2026-10-05 |
| 92 | https://www.trappist.uliege.be/cms/c_5284752/fr/trappist-equipement | WebFetch | OK | TRAPPIST-N 0.6 m RC f/8, Astelco NTM-500 GEM; Andor iKon-L BEX2-DD 2048x2048 0.60"/px 20'x20'; readout 1.8-5 s | 2026-10-05 |
| 93 | https://www.cfht.hawaii.edu/News/Smart1/ | WebFetch | OK | SMART-1 impact 3 Sep 2006 detected with WIRCam, H2 2.122 um (32 nm) filter, 10 s exposures + ~5 s gaps, 2'x2' window; flash in one frame (saturated); ejecta followed ~130 s | 2026-10-05 |
| 94 | https://www.cfht.hawaii.edu/Instruments/ | WebFetch | OK but index appears outdated | lists MegaCam, WIRCam, ESPaDOnS etc. | 2026-10-05 |
| 95 | https://lightbridges.es/ | WebFetch | OK | TTT access via Spanish CAT and direct proposals; OTE 2026A | 2026-10-05 |
| 96 | https://ttt.iac.es/ | WebFetch | OK | 4 RC telescopes (2x2 m, 2x0.8 m); 28°17'57"N 16°30'34"W; robotic queue | 2026-10-05 |
| 97 | https://ttt.iac.es/telescopes-instruments/ | WebFetch | OK | TTT1/2 0.8 m f/6.85 alt-az, FERVOR-M IMX455 sCMOS 0.28"/px 22.6'x15.1' 15 ms readout (~67 fps); TTT3 2 m f/6 (first light 2025, advanced commissioning) FERVOR-M 0.19"/px 10.2'x6.8' ~67 fps, COLORS CCD; TTT4 2 m first light 2026 commissioning | 2026-10-05 |
| 98 | https://research.iac.es/OOCC/night-cat/ | WebFetch | OK | CAT telescopes: GTC, WHT, INT, TNG, NOT, Mercator, LT, Stella, TTT; TCS open since 2024A; IAC80 not via CAT since 2013A; deadlines 2026A 3 Oct 2025, 2026B 3 Apr 2026 | 2026-10-05 |
| 99 | https://www.caha.es/ | WebFetch | OK (no specs) | 5 telescopes; CfP; visitor & service mode | 2026-10-05 |
| 100 | https://sites.astro.caltech.edu/palomar/observer/200inchResources/chimera.html | WebFetch | FAIL 404 | - | 2026-10-05 |
| 101 | https://sites.astro.caltech.edu/palomar/observer/200inchResources/ | WebFetch | FAIL 403 | - | 2026-10-05 |
| 102 | https://arxiv.org/abs/1601.02745 | WebFetch | INCONCLUSIVE (could not confirm paper identity) | - | 2026-10-05 |
| 103 | https://www.nasa.gov/centers-and-facilities/marshall/meteoroid-environment-office/ | WebFetch | FAIL 404 | - | 2026-10-05 |
| 104 | https://ui.adsabs.harvard.edu/abs/2020A%26A...633A.112L/abstract | WebFetch | OK | Liakos et al. 2020 A&A 633 A112, arXiv:1911.06101: 79 flashes in first 30 months; masses 0.7 g-8 kg | 2026-10-05 |
| 105 | https://ui.adsabs.harvard.edu/abs/2024A%26A...687A..14L/abstract | WebFetch | FAIL robots.txt fetch (x4; bibcode guessed; unverified) | - | 2026-10-05 |
| 106 | https://www.astro.noa.gr/ | WebFetch | OK (no NELIOTA content) | - | 2026-10-05 |
| 107 | https://www.canterbury.ac.nz/research/research-facilities/mount-john-observatory | WebFetch | FAIL 404 | - | 2026-10-05 |
| 108 | https://www.eso.org/public/teles-instr/lasilla/danish154/ | WebFetch | OK | Danish 1.54 m RC, off-axis equatorial, 2375 m, DFOSC; first light 1978 | 2026-10-05 |
| 109 | https://www.konyabilimmerkezi.com/ | WebFetch | OK (no observatory/telescope mentioned; planetarium only) | - | 2026-10-05 |
| 110 | https://www.tad.org.tr/ | WebFetch | OK | TAD = professional society (IAU national committee, TJAA); 24th National Astronomy Congress Aug 2026 Erzurum; IMO fireball reporting | 2026-10-05 |
| 111 | https://www.tad.org.tr/turkiyede-astronomi/gozlemevleri | WebFetch | OK | list of 13 Turkish observatories with URLs (Kandilli, IU, Ankara, Ege, Çukurova UZAYMER, TUG, Ulupınar caam.comu.edu.tr, Erciyes, ATASAM, İnönü, Adıyaman, ESTÜ Yunus Emre, DAG) | 2026-10-05 |
| 112 | https://caam.comu.edu.tr/ (2 queries) | WebFetch | OK | Ulupınar: 10 km from Çanakkale, 410 m, est. 2001, opened 19 May 2002; 3 robotic telescopes + met station | 2026-10-05 |
| 113 | http://caam.comu.edu.tr/hakkimizda/gozlem-aletleri-r2.html | WebFetch | OK | T122 Cass-Nasmyth alt-az (page: aperture 1022 mm, FL 10220 mm f/10) SBIG STL-1001E 7.1' 0.42"/px; IST60 0.6 m f/8 NTM-500, Andor iXon 888 Ultra DU-888U3 9.5' 0.56"/px; T40 LX200 16" Paramount ME II, Apogee F47 14.2' 0.70"/px; T30a/T30b, T20 etc. | 2026-10-05 |
| 114 | http://astrofizik.eskisehir.edu.tr/ | WebFetch | FAIL robots.txt HTTP 500 | - | 2026-10-05 |
| 115 | http://www.inonu.edu.tr/tr/astronomi | WebFetch | FAIL TLS certificate | - | 2026-10-05 |
| 116 | https://uzaymer.cu.edu.tr/ | WebFetch | OK (links) | - | 2026-10-05 |
| 117 | http://observatory.adiyaman.edu.tr/ | WebFetch | OK (links) | - | 2026-10-05 |
| 118 | https://uzaymer.cu.edu.tr/cu/information-document/teleskoplarimiz | WebFetch | OK | Officina Stellare Pro RC 500 (0.5 m) named; no specs | 2026-10-05 |
| 119 | https://observatory.adiyaman.edu.tr/tr/gozlem-aletleri/teleskoplar | WebFetch | OK | ADYU60 PlaneWave CDK24 0.61 m f/6.5 (3962 mm) ASA DDM160, 58' field; ADYU15 150 mm Newtonian; 'operational' | 2026-10-05 |
| 120 | https://ui.adsabs.harvard.edu/abs/2011PASP..123..461G/abstract | WebFetch | FAIL robots.txt fetch | - | 2026-10-05 |
| 121 | https://irtfweb.ifa.hawaii.edu/~moris/user/ (links query) | WebFetch | OK | documents incl. iXon Ultra 897 specs and TM-4 GPS unit manual | 2026-10-05 |
| 122 | https://irtfweb.ifa.hawaii.edu/~moris/user/IRTF_Moris_Manual.pdf | WebFetch | FAIL timeout | - | 2026-10-05 |
| 123 | https://astronomers.salt.ac.za/instruments/salticam/ | WebFetch | OK | SALTICAM 2x 2048x4102 15um CCDs, ~10' diameter FOV, 320-950 nm, frame-transfer and slot modes down to 0.05 s | 2026-10-05 |
| 124 | https://www.not.iac.es/instruments/ | WebFetch | OK | NOT: ALFOSC, NOTCam, FIES, StanCam; visitor DIPol-UF (high-speed polarimeter), SOFIN; retired LuckyCam | 2026-10-05 |
| 125 | https://www.ing.iac.es/astronomy/instruments/ | WebFetch | OK | WHT: WEAVE only; INT: HARPS3 only; not offered: ACAM, ISIS, LIRIS, PF-QHY; HiPERCAM & ULTRACAM 'formerly visitor' | 2026-10-05 |
| 126 | https://www.bursabtm.org.tr/ | WebFetch | FAIL DNS | - | 2026-10-05 |
| 127 | https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13094/3030690/ | WebFetch | FAIL (Incapsula bot wall) | - | 2026-10-05 |
| 128 | https://rasathane.ankara.edu.tr/ulasim-iletisim/ | WebFetch | OK | 39°50'37"N, 02h11m07s E (=32°46'45"E), 1256.69 m | 2026-10-05 |
| 129 | https://rasathane.ankara.edu.tr/tarihce/ | WebFetch | OK | founded 1954 decision; 18 km S of Ankara; 40 cm in use since 2007, 35 cm since 2009 | 2026-10-05 |
| 130 | https://uzaybimer.erciyes.edu.tr/tr/t35-teleskobu | WebFetch | OK but no specs rendered | - | 2026-10-05 |
| 131 | https://ui.adsabs.harvard.edu/abs/2015A%26A...577A.118M/abstract | WebFetch | OK | Madiedo et al. 2015 A&A 577 A118, arXiv:1503.05227 (Perseids 2012-2013; 1+12 flashes; mag 6.6-9.3) | 2026-10-05 |
| 132 | https://arxiv.org/pdf/1503.05227 | WebFetch | OK | MIDAS: Sevilla 37.34611N 5.98055W 23 m (2x0.36 m + 0.28 m Celestron SCT); La Hita 39.56833N 3.18333W 674 m (0.40 m Newtonian since 2013); Watec 902H Ultimate (ICX439ALL, PAL 720x576, 25 fps interlaced); GPS time inserter 0.01 s; f/3.3 reducers; terminator avoided to prevent saturation | 2026-10-05 |
| 133 | https://www.qhyccd.com/qhy174gps/ | WebFetch | OK | QHY174GPS: IMX174 1920x1200 5.86 um global shutter; 138 fps (8-bit) / 75 fps (16-bit) full frame; up to 305 fps ROI; GPS 1 us timestamps (exposure start/end in header) | 2026-10-05 |
| 134 | https://www.ufs.ac.za/boyden | WebFetch | OK (no specs) | 26 km E of Bloemfontein; public evenings; 'research station' | 2026-10-05 |
| 135 | https://en.wikipedia.org/wiki/Entoto_Observatory_and_Research_Center | WebFetch | FAIL (Wikipedia cache-only) | - | 2026-10-05 |
| 136 | https://trgozlemevleri.gov.tr/tr/kurumsal/hakkimizda | WebFetch | OK | DAG 'completed in 2024', 'opening in 2025'; SSA and space weather aims | 2026-10-05 |
| 137 | https://ui.adsabs.harvard.edu/abs/2024A%26A...687A..14L/abstract | WebFetch | FAIL robots.txt fetch (repeat of #105) | - | 2026-10-05 |
| 138 | https://www.eso.org/sci/facilities/paranal/instruments/hawki.html | WebFetch | OK | HAWK-I 4x H2RG, 7.5'x7.5', 0.106"/px, YJHK + NB incl. H2; UT4 Nasmyth A; fast modes not stated | 2026-10-05 |
| 139 | https://gozlemevi.ege.edu.tr/files/gozlemevi/gokyuzu/reports/Current_Monitor.htm | WebFetch | OK | weather station 'Izmir, Kurudag'; barometer 929.9 mb | 2026-10-05 |
| 140 | https://astronomi.boun.edu.tr/ | WebFetch | REDIRECT -> astronomi.bogazici.edu.tr | - | 2026-10-05 |
| 141 | https://astronomi.bogazici.edu.tr/ | WebFetch | OK | Kandilli: historical/solar instruments (1918 Zeiss equatorial); photosphere archive | 2026-10-05 |
| 142 | https://www.kayseribilimmerkezi.com/ | WebFetch | OK (planetarium; no observatory/telescope mentioned) | - | 2026-10-05 |
| 143 | https://ui.adsabs.harvard.edu/abs/2018A%26A...612A..76B/abstract | WebFetch | FAIL robots.txt fetch | - | 2026-10-05 |
