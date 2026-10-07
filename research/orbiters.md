# Lunar-orbiter availability and follow-up capability for the AYAP-1 terminal impact (mid-2027 to 2028)

Evidence cutoff: 5 October 2026. All URLs accessed 2026-10-05. Companion file: `orbiter_latency.csv`.

**Evidence tags used throughout**
- **[V]** verified in a fetched primary or official source (NASA, LROC, KARI, ISRO, JPL Horizons, NAIF, PDS, Firefly, or a peer-reviewed instrument paper).
- **[S]** secondary source only (Wikipedia, Planetary Society).
- **[D]** derived by this report from fetched data, for example JPL Horizons orbital elements or LROC image-ID timing. The method is stated.
- **[U]** unverified. Could not be confirmed with the tools available (WebSearch disabled; several sites 404, robots-blocked or rate-limited).
- **[P]** supplied by the study's author from the original source (text quoted to us; not retrieved by our tools).

**Release 2.1 reconciliation (7 October 2026).** LRO illumination seasons are now computed reproducibly by
`scripts/make_orbiter_seasons.py` from archived JPL Horizons elements (`data/horizons/horizons_lro_elements_2023-2028.txt`,
record revised 30 Sep 2026) and agree with the estimates in section 4 within one day; Danuri's planned March 2028 lunar
impact (KASA, 10 Feb 2025) is now the baseline and its seasons are computed from its archived Horizons elements; the GRAIL LAMP result is taken from Retherford et al. (2013). The replaced
statements are listed in `CHANGELOG.md`.

---

## Key findings

1. **LRO is operating, but its availability in mid-2027 to 2028 is not assured.**
   - Evidence that it is operating:
     - NAC imaged the Falcon 9 stage crater on 11–12 Aug 2026 [V].
     - LROC PDS release 67C came out on 14 Sep 2026 [V].
     - The PDS release schedule runs to data through 14 Mar 2027 [V].
   - Constraints on later operations:
     - NASA stated in June 2024 that LRO "has enough fuel on board to operate until 2027" [V].
     - The FY2027 President's Budget Request (April 2026) proposes a 46% cut to NASA science and termination of about 53 missions. Whether LRO is on that list could not be checked: the list PDF is robots-blocked [U].
     - The 2022 and 2025 Senior Review outcomes could not be retrieved [U].
2. **LRO's orbit is no longer the 2015 "20 × 165 km" frozen orbit.**
   - Since about 2019–2020 it has been near-circular: osculating periapsis about 57–88 km and apoapsis about 97–123 km, mean altitude about 90 km. Inclination has drifted to about 82.5–84°, and the period is about 117 min [D from Horizons].
   - At this altitude the NAC pixel scale is about 0.8–1.0 m [V: IM-1 0.89 m; Chang'e 6 0.85 m].
3. **Danuri (KPLO) is operating, with life "extended from 2023 to 2027" [V, KARI]; KASA plans low-altitude landing-technology tests after the end of 2027 and a lunar impact in March 2028 [P: KASA press release, 10 Feb 2025].**
   - It was moved from a 100 km circular orbit to about 60 km (Mar–Sep 2025), then to an elliptical orbit of about 50–65 × 200–215 km with periapsis over the south pole (since about Nov 2025) [D from Horizons/KARI ephemeris].
   - In the Falcon 9 case, Danuri's LUTI imaged the crater **a few hours after impact**. That is the fastest orbital follow-up on record [V].
4. **Chandrayaan-2 orbiter is still operating.**
   - ISRO orbit solutions in Horizons run to 8 Nov 2026 (record revised 30 Sep 2026) [V].
   - OHRC: 0.25 m GSD at 100 km, 3 km swath [V]. ISRO quotes a life of "almost seven years" [V]. No 2027+ commitment was found [U].
5. **Chang'e 7 had not launched as of about 19 Sep 2026** according to the Wikipedia Long March launch list, where it is still "2026 (TBD)" [S].
   - Its orbiter camera is stated as <0.5 m at 100 km [S]. Data access for non-Chinese teams is unverified.
6. **Commercial and other orbiters:** Firefly's Elytra Dark with the Ocula imager (0.2 m at 50 km) is aboard Blue Ghost Mission 2, "no earlier than 2027" [V]. Lunar Trailblazer is lost; recovery efforts ended 31 Jul 2025 [V].
7. **Precedent latency (impact to first NAC image), for events whose location was well known:**
   - 0.6 days (HAKUTO-R M1), 5.3 days (Luna 25), about 6.2 days (ispace M2), about 6.3 days (Falcon 9), 10.7 days (Beresheet, Vikram) [V/D].
   - Months when the location was uncertain or the site was dark: 66 days (Longjiang-2), 73 days (GRAIL), 78 days (CE5-T1), up to 123 days (LADEE).
   - First public release came 12–34 days after impact for the well-located cases.
8. **Observing a plume or flash from orbit is only realistic for a coordinated, controlled impact**, as with LCROSS in 2009 and GRAIL in 2012. For an uncontrolled impact, LRO has line of sight to a random point only about 2.5% of the time [D], before pointing and illumination constraints. The realistic orbiter contributions are:
   - pre-impact reference images
   - crater detection by temporal pairs within about 1–30 days
   - low-Sun morphology and stereo in the next favourable illumination window

---

## (a) Per-orbiter status table

| Orbiter (operator) | Status, Oct 2026 | Approved / stated end | Orbit (2026) | Relevant instruments | Resolution | Pointing / slew | Observation request path | Data release latency | Sources |
|---|---|---|---|---|---|---|---|---|---|
| **LRO** (NASA GSFC; LROC run by Intuitive Machines since 18 May 2026) | **Active** [V]. NAC imaging on 11–12 Aug 2026 [V]; NAIF ck directory updated 2026-10-05 [V] | **No approved end date found** [U]. Fuel "until 2027" (NASA, 18 Jun 2024) [V]. PDS schedule to Release 70 (data to 14 Mar 2027; release 15 Jun 2027) [V]. FY2026 funded (H.R. 6938 signed 23 Jan 2026, NASA $24.4B; Congress rejected most cuts) [S]. FY2027 PBR: Lunar Discovery & Exploration $204.0M (FY2024 $363.4M) [V]; LRO-specific fate [U] | Near-circular. Osculating periapsis ~1795–1825 km radius (alt ~57–88 km), apoapsis ~1834–1860 km (alt ~97–123 km). i ≈ 82.5–84°. P ≈ 7005–7023 s (~117 min). Node regresses ~38–44°/yr (ecliptic frame) [D: Horizons -85] | LROC NAC ×2, WAC; Diviner; LAMP; LOLA; LEND; CRaTER; Mini-RF (bistatic only since the Jan 2011 transmitter failure) | NAC 0.5 m at 50 km → **~0.8–1.0 m at 80–100 km** [V: 0.89 m, 0.85 m examples]. Swath 2 × ~4.5 km at 90 km [D]. WAC 75 m (vis) / 385 m (UV) at 50 km [V]. Diviner 9 channels 0.3–200 µm, ~250 m at 50 km [V] | Routine slews 4–28° on consecutive orbits; 42° (Ch-3) and **68°** oblique demonstrated (Falcon 9) [V]. Pointing timing ±10 s matters ("10 s → 10 mi off-centre") [V] | LROC public target-request tool (https://target.lroc.im-ldi.com/…, robots-blocked) [V exists]. Time-critical events coordinated by LRO project (GSFC) + LROC team, e.g. with CNEOS predictions and Danuri coordinates (Falcon 9) [V] | Featured/press: **7–34 d** after the event when the site is well located [V]. LROC PDS: monthly batches, ~3 months after acquisition (e.g. 67C on 14 Sep 2026 covers 16 May–15 Jun 2026) [V]. Other instruments: quarterly (Release 67 on 15 Sep 2026 covers 15 Mar–14 Jun 2026) [V] | science.nasa.gov LRO pages; lroc.im-ldi.com; pds-geosciences; nasa.gov history (Jun 2024); Horizons |
| **Danuri / KPLO** (KARI/KASA; NASA ShadowCam, run by Intuitive Machines since May 2026) | **Active** [V]. LUTI imaged the Falcon 9 crater on 5 Aug 2026 [V]. Horizons: KARI tag-up data through 24 Aug 2026, predictions to 2 Mar 2027 [V] | "Operational life … extended from 2023 to 2027" (KARI) [V]. Exact end date and any further extension [U] | 100 km circular polar (2023–early 2025) → ~45–78 km (Mar–Sep 2025) → **~48–64 × 200–213 km**, i ≈ 88–90°, periapsis over the south pole (ω ≈ 270–278°) since ~Nov 2025. P ≈ 121 min [D: Horizons -155]. Altitude ≈ 100 km at 20°S, ≈ 155 km at 20°N, ≈ 200 km at 60°N [D] | LUTI (high-res), PolCam, ShadowCam, KMAG, KGRS, DTNPL | LUTI "5 m-grade" (KARI) [V]; actual GSD scales with altitude [D]. ShadowCam **1.7 m/px**, 5.2 km swath at 100 km, >200× NAC sensitivity, SNR >90, **saturates on sunlit terrain** [V]. PolCam [U] | LUTI pointed at a predicted site within hours (Falcon 9) [V]. Slew limits [U] | KARI/KASA, bilateral. In the Falcon 9 case, CNEOS (NASA) passed the predicted point "to the Republic of Korea" [V]. ShadowCam requests through the NASA ShadowCam team [U] | ShadowCam PDS: quarterly, **~11–14 months** lag (21 Aug 2026 release covers Jul–Sep 2025) [V]. LUTI/PolCam public release policy [U] (KPDS host unreachable) | kari.re.kr; shadowcam.im-ldi.com; NASA F9 article; Horizons |
| **Chandrayaan-2 orbiter** (ISRO) | **Active** [V]. ISRO orbit determination to 8 Nov 2026 in Horizons (revised 30 Sep 2026) | "Almost seven years" life (ISRO) [V]. Planned "~7.5 years" [S]. No 2027–28 commitment found [U] | ~100 km polar. Osculating alt ~57–137 km, i ≈ 90–92°, P ≈ 116–119 min [D: Horizons -152] | OHRC, TMC-2, IIRS (0.8–5 µm), DFSAR, CLASS, XSM, CHACE-2 | **OHRC 0.25 m GSD (nadir, 100 km)**, 3 km swath, 3 × 12 km strip; images at Sun elevation ~5–6° [V]. TMC-2 ~5 m / 20 km swath [U] | OHRC stereo by spacecraft pitch: +5° and −25° on consecutive orbits [V]. Has made collision-avoidance manoeuvres for LRO conjunctions (Oct 2021, Nov 2024) [S] | ISRO, bilateral. **No public tasking interface found** [U] | PRADAN/ISDA portal (login required) [V]. Latency [U] | isro.gov.in; pradan.issdc.gov.in; Current Science 118(4):560; Horizons |
| **Chang'e 7 orbiter** (CNSA) | **Not launched** as of ~19 Sep 2026 (Long March list: "2026 (TBD)") [S]. Delivered to Wenchang in Apr 2026 [S] | Planned 8-year mission [S] | Planned lunar polar orbit [U] | High-resolution stereo mapping camera, mini-SAR, IR mineral imager, neutron/gamma spectrometer, magnetometer [S] | Camera <0.5 m at 100 km (>18 km swath); <0.075 m at 15 km [S] | [U] | CNSA, bilateral only [U] | NAOC GRAS release system (JavaScript-only page; policy not read) [U] | en.wikipedia Chang'e 7; planetary.org; CNSA |
| **Queqiao-2** (CNSA relay) | Active [S] | Design life 8–10 yr [S] | 254 × 16,941 km, i = 119°, frozen elliptical [S] | Extreme-UV camera (Earth plasmasphere), neutral-atom imager, VLBI | **No high-resolution lunar surface imager** [S] | n/a | n/a | n/a | en.wikipedia Queqiao-2 |
| **Chang'e 5 orbiter** (CNSA) | In lunar distant retrograde orbit since ~Feb 2022 [S] | [U] | DRO, far from the surface | n/a | Not usable for crater imaging [S] | n/a | n/a | n/a | en.wikipedia Chang'e 5 |
| **Firefly Elytra Dark + Ocula** (commercial; carries ESA Lunar Pathfinder) | Not launched. Blue Ghost Mission 2 "no earlier than 2027" [V]. (Ocula page says first activation "late 2026"; treat as NET 2027) | 5 years in lunar orbit after the lander mission [V] | [U] | Ocula UV/visible imager (built by LLNL) | **0.2 m at 50 km** [V] | [U] | Commercial licensing ("low cost") [V] | [U] | fireflyspace.com |
| **ESA Lunar Pathfinder** | Rides on Elytra Dark (BGM2, NET 2027) [V] | [U] | [U] (ESA page returned 403) | Communications relay | No imager known [U] | n/a | n/a | n/a | fireflyspace.com; esa.int |
| **NASA Lunar Trailblazer** | **Lost.** Launched 26 Feb 2025; contact lost 27 Feb 2025; recovery efforts ended 31 Jul 2025 [V] | Ended | n/a | n/a | n/a | n/a | n/a | n/a | science.nasa.gov/mission/lunar-trailblazer/ |
| Not relied on: IM relay satellites, Astrobotic Griffin-1, ispace M3, IM-3, JAXA/ISRO LUPEX (2028–29), Gateway, Luna 26 (2028–29), Chang'e 8 | Landers, relays or planned only | — | — | — | No substantiated 2027–28 high-resolution imaging orbiter [U]/[S] | — | — | — | Wikipedia lists; IM site (blocked) |

### LRO details requested

**Health** [V]:
- Mini-RF partially failed in January 2011.
- The IMU was powered down in May 2018 to preserve its remaining life.
- Battery: 80 A-hr Li-ion (NSSDC).
- No public 2025–2026 report of reaction-wheel or battery problems was found [U].
- Downlink: 310 Gbit per Ka-band pass, up to 4 passes per day [V].

**Orbit history** [D, Horizons -85, lunar mean equator frame]:

| Period | Orbit |
|---|---|
| 2009–2011 | ~40–60 km near-circular (nominal 50 km), i ≈ 89–90° |
| 2012–2018 | ~20–60 × ~125–195 km, ω ≈ 245–290° (periapsis over the south pole). Since 4 May 2015 ~20 × 165 km [V, NASA] |
| 2019–2026 | e ≈ 0.003–0.018 near-circular ~60–120 km. Periapsis location not fixed (osculating ω varies widely), i.e. no longer the 2015-style south-pole periapsis frozen orbit. Inclination drifting about −0.9°/yr (≈86° in 2023 → ≈82.5° in mid-2026, ecliptic frame) |

**Ground track** [D]:
- Successive orbits shift about 1.07° of longitude: ~32 km at the equator, ~30 km at 20°, ~16 km at 60°.
- A given site passes under the orbit plane once per sidereal month (27.3 d) on the dayside and about 13.7 d later on the nightside.
- LROC: imaging opportunities for a given low-latitude site occur "for only a few days each month" [V, McGetchin post].
- With slews up to about ±30° (about ±50 km at 90 km altitude), 3–5 consecutive orbits can be used per pass. The Falcon 9 sequence used 5 orbits plus an oblique image [V].

**Beta-angle cycle** [D]:
- The ecliptic-frame node regresses about 0.10–0.12°/day while the Sun advances 0.986°/day. The orbit plane therefore cycles relative to the Sun in about **331 days**.
- β = 0 (noon–midnight orbit, eclipse season) about every 165 d; |β| reaches about 82° about every 165 d.
- Incidence at a site of latitude φ at overflight ≈ arccos(cos φ · cos β).
- Validation:

| Case | Predicted incidence | LROC-reported incidence |
|---|---|---|
| Falcon 9 site, 11 Aug 2026 | 70° | 67–71° |
| SLIM, 24 Jan 2024 | 14.6° | 14° |
| McGetchin, Dec 2025 | 37.5° | 38° |
| Vikram, 17 Sep 2019 | 85° | 84° |

**SPICE / ephemerides**:
- NAIF's operational LRO area holds only ck/fk/ik. Operational SPICE is produced at the LRO MOC (GSFC) and is not served by NAIF [V].
- The PDS SPICE archive holds merged reconstructed `lrorg_YYYYDOY_yyyydoy_v01.bsp` files built from daily definitive ephemerides [V]. Latest: `lrorg_2025349_2026074_v01.bsp`, covering 15 Dec 2025–15 Mar 2026, posted 2026-06-04, i.e. about 3 months behind [V].
- **No public predicted ("lrorp") SPK was found** [U].
- JPL Horizons (-85) has reconstructed data to 2026-03-15, concatenated predicts to 2026-08-05, and an "extended forecast" to **2028-02-13** [V]. That forecast shows a constant period (7008.0 s) and a node drift about 16× slower than observed, so it is a low-fidelity placeholder and not usable for planning imaging [D].
  - Release 2.1: the Horizons record revised 30 Sep 2026 (archived in `data/horizons/`) has tag-up solutions to 2026-09-02 and a 558-day prediction to 2028-03-12. Its node regresses at 0.004-0.02 deg/day against 0.09-0.12 deg/day observed in 2023-2026, so it is also treated as a placeholder; only the tracking-based part is used [D].
- Danuri: KARI solutions in Horizons, with predictions to 2027-03-02 [V].
  - Release 2.1: a later query (record with KARI tag-up data through 2026-09-29 and predictions to 2027-04-01; supplied by the study's author, archived as `data/horizons/horizons_kplo_elements_2023-2027.txt`) is used for Danuri's seasons; only the tracking-based part is used [P/D].
- Chandrayaan-2: ISRO orbit determination to 2026-11-08 [V].

### Which LRO instruments could observe what

| Instrument | Plume / flash | Thermal | Crater / ejecta | Geometry needed | Basis |
|---|---|---|---|---|---|
| LROC NAC | Not practical. A pushbroom line scanner would have to be scanning the exact spot at the moment of impact. | No | **Yes**: ~0.8–1 m/px detects ~5–20 m craters and 10–100 m albedo anomalies through before/after ratios | Dayside pass within slew range. Low Sun (incidence ~55–80°) for morphology; matched illumination for ratios | Precedents [V] |
| LROC WAC | No | No | Only for large new craters (McGetchin, 222 m, found in a WAC temporal ratio) | Global coverage | [V] |
| LAMP (FUV imaging spectrograph) | **Yes, if pre-planned.** Watched the GRAIL impact and plume through its slit (2012) [S]. LCROSS plume spectra (2009; Gladstone et al. 2010, Science 330) [U, not retrieved] | — | — | Line of sight to the plume minutes after impact; pre-commanded pointing | GRAIL LAMP view [S]; species detected [U] (Science DOIs 403, Europe PMC 429) |
| Diviner | — | **Yes, within minutes, if pre-planned.** LCROSS: observed the impact point ~90 s after impact at ~80 km range [V] | Cold-spot (fine ejecta) signatures for large craters only (McGetchin: 4-mile cold spot) [V] | Footprint ~250 m at 50 km (~450 m at 90 km [D]). Residual heat from a ~5–20 m crater after hours to days is implausible to detect [D, qualitative] | [V]/[D] |
| LOLA | No | No | Only if a nadir track crosses the crater (5-spot pattern ~50 m) | Nadir only | [V] specs |
| Mini-RF | No | No | Bistatic only, using Earth transmitters; roughness change only for large ejecta blankets [U] | Bistatic geometry | [V] failure 2011 |
| LEND, CRaTER | No | No | No | — | [V] specs |

---

## (b) Precedent-latency table (impact or landing → first NAC image → first public release)

Timing basis:
- "stated" = date given on the page.
- "inferred" = derived from the NAC product ID. The ID number after "M" behaves as LRO mission-elapsed seconds. Calibration against 9 LROC-stated acquisition times fits within hours, with one exception: the IM-2 caption is about 23 h off.

| Event | Impact / landing (UTC) | First post-event NAC image | Δt image | First public release | Δt release | Crater / feature size | Source URL |
|---|---|---|---|---|---|---|---|
| GRAIL A/B (controlled) | 2012-12-17 22:28:51 | 2013-02-28 (stated) | 72.6 d | 2013-03-19 (LROC) | 92 d | Two craters ~5 m, 2.2 km apart | https://lroc.im-ldi.com/images/596 |
| LADEE (controlled, farside) | 2014-04-18 ~04:30 | ~2014-08-19 (inferred; image used in ratio) | ≤123 d | 2014-10-28 (NASA/LROC) | 193 d | Crater <3 m; ejecta 200–300 m | https://lroc.im-ldi.com/images/822 ; https://www.nasa.gov/missions/lro/nasas-lro-spacecraft-captures-images-of-ladees-impact-crater/ |
| Beresheet | 2019-04-11 (~19:23 [U]) | 2019-04-22 ("11 days later") | 10.7 d | 2019-05-15 | 34 d | ~10 m dark smudge; 30–50 m disturbed zone; ~100 m ray | https://lroc.im-ldi.com/images/1101 |
| Longjiang-2 | 2019-07-31 (~14:20 [U]) | 2019-10-05 (stated, from 122 km) | 65.9 d | 2019-11-14 | 106 d | 4 × 5 m crater | https://lroc.im-ldi.com/images/1132 |
| Vikram (Ch-2) | 2019-09-06 (~20:23 [U]) | 2019-09-17 (stated; 1.3 m px, inc 84°) | 10.7 d | 2019-09-26 (first mosaic). Debris confirmed and released 2019-12-02 using 11 Nov images | 20 d / 87 d | Debris field; debris ~750 m NW | https://lroc.im-ldi.com/images/1131 |
| CE5-T1 upper stage | 2022-03-04 (~12:25 [U]) | 2022-05-21 (stated after image; site had to be searched) | 78 d | 2022-06-23 | 111 d | Double crater 18 m + 16 m (29 m max) | https://lroc.im-ldi.com/images/1261 |
| HAKUTO-R M1 | 2023-04-25 16:40 | 2023-04-26 (stated; ~06:57 inferred), 10 images | 0.6 d | 2023-05-23 | 28 d | 60–80 m reflectance change; ≥4 debris pieces | https://lroc.im-ldi.com/images/1302 |
| Luna 25 | 2023-08-19 11:58 | 2023-08-24 18:15–22:12 (stated) | 5.3 d | 2023-08-31 (NASA) | 12 d | ~10 m crater | https://www.nasa.gov/humans-in-space/nasas-lro-observes-crater-likely-from-luna-25-impact/ ; https://lroc.im-ldi.com/images/1311 |
| ispace M2 RESILIENCE | 2025-06-05 18:13 | ~2025-06-11 23:21 (inferred) | ~6.2 d | 2025-06-20 | 15 d | Dark smudge plus bright halo (size not stated) | https://lroc.im-ldi.com/images/1456 |
| **Falcon 9 stage** | **2026-08-05 06:35** | **Danuri LUTI "a few hours later"** [V]. LRO NAC 2026-08-11 (stated; ~12:39 inferred) | **hours (Danuri); 6.3 d (LRO)** | 2026-08-18 (NASA + LROC) | 13 d | **18 m diameter, <3 m deep** (NASA: "60 ft"); V-shaped ejecta; impact ~31° from horizontal | https://science.nasa.gov/solar-system/moon/nasas-lro-images-falcon-9-crater-on-moon-learns-new-details/ ; https://lroc.im-ldi.com/images/1499 |
| *Context: SLIM landing* | 2024-01-19 15:20 | 2024-01-24 ("five days later"; inc 14°, ~80 km) | 4.9 d | 2024-01-26 | 7 d | lander | https://lroc.im-ldi.com/images/1358 |
| *Context: IM-1* | 2024-02-22 23:23:53 | 2024-02-24 18:57 (stated) | 1.8 d | 2024-02-26 | 4 d | lander | https://lroc.im-ldi.com/images/1360 |
| *Context: Chang'e 6* | 2024-06-01 | 2024-06-07 (stated) | ~5.7 d | 2024-06-14 | 13 d | lander | https://lroc.im-ldi.com/images/1374 |
| *Context: Blue Ghost M1* | 2025-03-02 (08:34 [U]) | 2025-03-02 17:49 (stated; oblique from 175 km east) | ~0.4 d | 2025-03-04 | 2 d | lander | https://lroc.im-ldi.com/images/1406 |
| *Context: IM-2* | 2025-03-06 | 2025-03-07 16:54 (caption, "~23.5 h"; the image ID implies 03-06 ~17:46, unresolved) | ~1 d | 2025-03-10 | 4 d | lander in 20 m crater | https://lroc.im-ldi.com/images/1408 |
| *Context: McGetchin (natural)* | 2024-04-11 to 05-22 window | Found in WAC ratio 2025-10-24; NAC 2025-12-05 and 2026-03-03 | ~600 d | 2026-09-16 | ~890 d | 222 m × 43 m; Diviner cold spot ~4 mi | https://science.nasa.gov/solar-system/moon/nasas-moon-orbiter-spots-new-once-in-century-moon-crater/ |

**Falcon 9 extract** (the specific case requested):

| Item | Detail | Basis |
|---|---|---|
| Object | Falcon 9 upper stage from the Blue Ghost 1 launch (15 Jan 2025) | [V] |
| Impact | 5 Aug 2026, 06:35 UTC, ~31° from horizontal | [V] |
| Location | 19.4759°N, 266.7138°E (93.3°W, just beyond the west limb near Einstein/Bell craters), 511 m elevation | [V] |
| Prediction | NASA CNEOS. Prediction ellipses 2.1 × 0.4 mi; accurate to "about 0.6 miles" | [V] |
| First orbital image | Danuri LUTI imaged the crater a few hours after impact and sent coordinates to the LRO team | [V] |
| LRO imaging | First imaged 11 Aug 2026: five NAC images, one per 117-min orbit, slews 23°/11°/4°/17°/28°, then a 68° oblique. Incidence 67–71° (78° oblique); phase 105°→37°; altitude ~90 km (NASA: "about 60 miles … 1 mile per second") | [V] |
| Before image | M1370003265R, ~Mar 2021 | [D] |
| Crater | 18 m diameter, <3 m deep (shadow-measured). V-shaped ejecta to the south. Mature dark streaks plus immature bright ejecta; excavation of weathered material ~1.5 ft | [V] |
| Real-time observation | NASA MEO planned ground-telescope imaging; LRO and ShadowCam planned before/after imaging; "it may take several days to receive imagery" (NASA, 4 Aug 2026). No LRO real-time plume or thermal observation reported | [V] |
| Release | 18 Aug 2026 | [V] |

---

## (c) What an orbiter can realistically contribute to AYAP-1

**1. Pre-impact reference imagery: high confidence, if LRO operates.**
- 17 years of LROC NAC coverage at many illuminations means a "before" image of almost any impact ellipse already exists. Precedents used before images from 2017, 2021, 2022 and 2024 [V].
- A km-scale ellipse fits in one or two NAC swaths (~9 km at 90 km [D]). The Falcon 9 ellipse was 3.4 × 0.64 km [V].
- Best practice: once the impact zone is known (weeks to months ahead), request new NAC images at the incidence and emission geometry expected for the first post-impact passes. Use the LROC target tool plus direct contact with the LROC team (Intuitive Machines) and the LRO project (GSFC).
- For Danuri, ask KARI for pre-impact LUTI frames (Falcon 9 model).

**2. Plume or thermal observation: low probability unless the impact is controlled and coordinated.**
- Both documented orbital observations of an impact event were NASA-controlled impacts with LRO pre-positioned and instruments pre-commanded:
  - LCROSS 2009: Diviner looked about 90 s after impact from about 80 km [V]; LAMP plume spectra [U].
  - GRAIL 2012: LAMP detected H and Hg emission in the impact plumes (Retherford et al. 2013, LPSC #3004) [V].
- Geometric chance that LRO (~90 km altitude) has line of sight to a random impact point at a random time: about 2.5% (horizon range ~550 km) [D].
- For Danuri: ~1.7% at 60 km, ~5% at 200 km altitude [D].
- Additional requirements: impact time known to about a minute and location to about km, days to weeks in advance; LAMP/Diviner pointing loaded in the command sequence; a sunlit or hot plume in the field of view.
- If AYAP-1 ends with a commanded, timed impact, the time could be chosen to coincide with an LRO pass. That needs agreement with the LRO project months ahead and LRO still operating.
- If AYAP-1 decays uncontrolled, plan only for imaging after impact.
- Residual-heat detection of a ~5–20 m crater by Diviner after hours to days is implausible: footprint area ratio ~10⁻³–10⁻⁴ [D, qualitative].
- Ground-based flash monitoring (NASA MEO-type) is the complementary channel. It was attempted for Falcon 9; no result was reported in the fetched sources.

**3. Earliest post-impact image.**
- Fastest path: Danuri LUTI within hours, if Danuri is still operating (extension "to 2027"; planned lunar impact March 2028 [P]) and KARI agrees. Precedent: Falcon 9 [V].
  - GSD will be several metres: altitude ≈ 100 km at 20°S but ≈ 155–200 km at northern mid-latitudes [D].
  - That is enough to detect an 18 m crater and its albedo halo; marginal for a few-metre crater.
- LRO NAC: next dayside overflight of the site, typically 0.4–11 d for well-located events [V/D], up to about 27 d in the worst phasing [D].
- Months when the location is poorly known or the site is dark: CE5-T1 78 d, Longjiang-2 66 d, GRAIL 73 d [V].
- Implication: AYAP-1 should release its final tracking or ephemeris and a predicted impact ellipse quickly (CCSDS OEM/SPICE) so CNEOS or LROC can target. The Falcon 9 prediction was good to about 1 km.
- Chandrayaan-2 OHRC (0.25 m) and Chang'e 7 (<0.5 m, if launched) are capable in principle, but have no public tasking route [U].

**4. Later low-Sun imaging, for morphology and stereo DTMs.**
- For a low-latitude site, LRO gives incidence ≥55° only when |β| ≥ 55°.
- LRO low-Sun seasons, computed in release 2.1 from the tracking-based Horizons elements (to 2026-09-02) with a quadratic node trend (`outputs/tables/orbiter_seasons.json`; boundary ranges from alternative fits grow from ~2 days in mid-2027 to ~1-2 weeks in late 2028) [D]:
  - 12 May–13 Jul 2027
  - 23 Oct–21 Dec 2027
  - 28 Mar–28 May 2028
  - 7 Sep–5 Nov 2028
- Near-noon / eclipse-season windows (|β| ≤ 15°; good for albedo, poor for topography) [D]:
  - 9 Mar–4 Apr 2027
  - 20 Aug–16 Sep 2027
  - 26 Jan–20 Feb 2028
  - 5 Jul–1 Aug 2028
- The 5 Oct 2026 estimates that these replace (low Sun 12 May–13 Jul 2027, 23 Oct–21 Dec 2027, 29 Mar–28 May 2028, 8 Sep–6 Nov 2028; near noon 9 Mar–4 Apr 2027, 20 Aug–16 Sep 2027, 26 Jan–21 Feb 2028, 6 Jul–1 Aug 2028; from a node history sampled every 61 days that was not archived) agree with these within one day. A hold-out test of the quadratic extrapolation (fits ending 2024-03, 2024-09 and 2025-03, compared with tracking data to 2026-09) moved season boundaries by at most 5 days. The extrapolation assumes no LRO orbit manoeuvre.
- At high latitudes (≥60°), incidence stays ≥60° year-round.
- Danuri low-Sun windows: 23 Mar–2 Jun 2027 and 25 Sep–3 Dec 2027, computed in release 2.1 from the archived Horizons elements of Danuri (`data/horizons/horizons_kplo_elements_2023-2027.txt`, tracking to 2026-09-29; query supplied by the study's author) [D]. Danuri's node drifts by only 0.004–0.007°/day, so the seasons repeat almost every year; the 5 Oct 2026 estimate (~23 Mar–2 Jun and ~25 Sep–2 Dec) agrees within one day, and the KARI prediction in the same record gives beta angles within 0.6° of the extrapolation. In the release-2.1 baseline Danuri is not available after its planned March 2028 impact.
- Worst case from impact to the first low-Sun LRO image: about 3.3 months (gap between windows) plus up to 27 d.
- Public release: featured or press images in 1–5 weeks for notable events [V precedents]; LROC PDS about 3 months after acquisition [V]; ShadowCam PDS about 1 year [V].

**5. Availability risk for mid-2027 to 2028.**
- LRO: fuel stated to last "until 2027" [V]; FY2027 budget threat [V] with the LRO-specific outcome [U].
- Danuri: extension "to 2027" [V]; low-altitude tests and a planned lunar impact in March 2028 [P: KASA, 10 Feb 2025].
- Chandrayaan-2: about 7-year life, which ends around 2026 [V].
- Chang'e 7: not launched [S].
- Elytra/Ocula: NET 2027 [V].
- The paper should therefore present orbiter follow-up as contingent. Recommended actions:
  - early coordination letters to the NASA LRO project / LROC (Intuitive Machines), KARI/KASA (Danuri) and ISRO (Chandrayaan-2)
  - sharing AYAP-1 ephemerides with JPL CNEOS
  - a fallback of Earth-based flash monitoring plus later imaging by whichever orbiter survives.

### Items explicitly unverified

- LRO 2022/2025 Senior Review outcomes and "ESM5/ESM6" end dates.
- Whether LRO is on the FY2027 termination list.
- LRO reaction-wheel and battery status in 2025–26.
- Existence of public predicted LRO SPKs ("lrorp").
- Species LAMP detected in the LCROSS plume (Gladstone et al. 2010, not retrievable). GRAIL is resolved: H and Hg (Retherford et al. 2013) [V].
- Exact date of Danuri's planned March 2028 impact (KASA gives the month only) and KARI's stated reasons for the 2025 orbit changes.
- LUTI swath and exact GSD; PolCam specifications.
- Chandrayaan-2 data latency, 2027+ plans and TMC-2 specifications.
- Chang'e 7 launch status from a CNSA primary source, and Chinese data access.
- IM-2 acquisition time inconsistency.
- Impact clock times for Beresheet, Longjiang-2, Vikram, CE5-T1 and Blue Ghost (taken from outside the fetched pages).

---

## (d) URL log (all accessed 2026-10-05)

| # | URL | Outcome | Key content / note |
|---|---|---|---|
| 1 | https://science.nasa.gov/solar-system/moon/nasas-lro-images-falcon-9-crater-on-moon-learns-new-details/ (4 queries) | OK | Pub 18 Aug 2026; impact 5 Aug 2026; LRO 11–12 Aug; 60 ft × <10 ft; CNEOS; Danuri LUTI "a few hours later", "accurate to about 0.6 miles"; ellipses 2.1 × 0.4 mi; ±10 s timing |
| 2 | https://science.nasa.gov/mission/lro/ (3 queries) | OK | Active mission; story links |
| 3 | https://science.nasa.gov/blogs/ | OK | Not relevant |
| 4 | https://science.nasa.gov/solar-system/moon/nasa-will-attempt-to-observe-rocket-parts-lunar-impact/ | 404 | Wrong slug |
| 5 | https://science.nasa.gov/solar-system/moon/nasas-moon-orbiter-spots-new-once-in-century-moon-crater/ | OK | McGetchin 728 ft / 141 ft; impact 11 Apr–22 May 2024; found 24 Oct 2025; NAC 5 Dec 2025 and 3 Mar 2026; Diviner cold spot |
| 6 | https://lroc.im-ldi.com/ | OK | LROC home (Intuitive Machines/ASU) |
| 7 | https://lroc.im-ldi.com/images/1499 (2 queries) | OK | Falcon 9: 06:35 UTC; 31°; 18 m / <3 m; slews; 90 km; Danuri LUTI |
| 8 | https://lroc.im-ldi.com/images/1464 | OK | 22 m new crater (2009–2012 window) |
| 9 | https://lroc.im-ldi.com/news | OK | PDS 67A/B/C releases and coverage |
| 10 | https://science.nasa.gov/blogs/lro/ | 404 | — |
| 11 | https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2009-031A | OK | Mass, battery 80 A-hr, 30 × 180 km quasi-frozen orbit (2015 text) |
| 12 | https://lunar.gsfc.nasa.gov/ | 302 → science.nasa.gov/mission/lro/ | — |
| 13 | https://science.nasa.gov/blogs/science-news/2026/05/18/nasa-transfers-management-of-lunar-science-instruments/ | OK | LROC and ShadowCam management to Intuitive Machines (18 May 2026); PDS by Texas A&M |
| 14 | https://science.nasa.gov/planetary-science/resources/planetary-mission-senior-review/ | 404 | — |
| 15 | https://www.planetary.org/articles/nasa-budget-2026-cancelled-missions | 404 | — |
| 16 | https://en.wikipedia.org/wiki/Lunar_Reconnaissance_Orbiter (2 queries) | OK [S] | IMU 2018; 20 km south-pole periapsis 2015; "fuel until 2027" (cites NASA 2024) |
| 17 | https://science.nasa.gov/mission/lro/stories/ | OK | Story list (summariser misdated the Falcon 9 story as 2024; primary pages say 2026) |
| 18 | https://science.nasa.gov/mission/lro/about/ | OK | 50 km circular from 25 Sep 2009; 20 × 165 km from 4 May 2015; IMU off May 2018 |
| 19 | https://www.nasa.gov/humans-in-space/commercial-space/nasa-will-attempt-to-observe-rocket-parts-lunar-impact/ (2 queries) | OK | 4 Aug 2026 notice; MEO telescopes, LRO, ShadowCam; "several days" for imagery |
| 20 | https://naif.jpl.nasa.gov/pub/naif/LRO/kernels/spk/ | 404 | No SPK directory in the operational area |
| 21 | https://naif.jpl.nasa.gov/naif/data_lunar.html | OK | LRO ck/fk/ik at NAIF |
| 22 | https://naif.jpl.nasa.gov/pub/naif/LRO/kernels/ | OK | ck modified 2026-10-05 |
| 23 | https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/spk/ (2 queries) | OK | Latest lrorg_2025349_2026074_v01.bsp (posted 2026-06-04) |
| 24 | https://naif.jpl.nasa.gov/pub/naif/LRO/kernels/aareadme.txt | OK | Operational SPICE at LRO MOC (GSFC) |
| 25 | https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27-85%27&OBJ_DATA=%27YES%27&MAKE_EPHEM=%27NO%27 | OK | LRO trajectory spans; forecast to 2028-02-13 |
| 26 | https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27-155%27&OBJ_DATA=%27YES%27&MAKE_EPHEM=%27NO%27 | OK | KPLO: KARI solutions to 2027-03-02 |
| 27 | Horizons long-URL element queries (2) | Proxy 403 (URL too long) | Re-run with short URLs |
| 28 | https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=-85&EPHEM_TYPE=E&CENTER=500@301&START_TIME=2026-10-01&STOP_TIME=2026-10-02&STEP_SIZE=12h&OBJ_DATA=NO | OK | LRO ~70 × 110 km, P ~7009 s |
| 29 | same with &REF_PLANE=B | OK | i ≈ 83.3–83.7° (lunar equator) |
| 30 | …COMMAND=-85…START_TIME=2023-01-01&STOP_TIME=2028-01-01&STEP_SIZE=91d…REF_PLANE=B | OK | Quarterly elements 2023–2027 |
| 31 | …COMMAND=-155…START_TIME=2023-01-01&STOP_TIME=2027-03-01&STEP_SIZE=61d…REF_PLANE=B | OK | Danuri orbit history |
| 32 | https://en.wikipedia.org/wiki/Danuri | OK [S] | Outdated |
| 33 | https://shadowcam.im-ldi.com/ | OK | Latest PDS release 21 Aug 2026 |
| 34 | https://www.kari.re.kr/eng/ | OK | "Extended from 2023 to 2027" |
| 35 | https://www.kari.re.kr/eng/contents/193 | OK | 678 kg, 260 kg propellant; LOI 26 Dec 2022; 100 km circular |
| 36 | https://www.kari.re.kr/eng/contents/192 | OK | Korean lander by 2032 |
| 37 | https://www.kari.re.kr/eng/contents/195 | OK | LUTI "5m-grade" |
| 38 | https://kplo.kari.re.kr/ | Fail (DNS/robots) | — |
| 39 | https://shadowcam.im-ldi.com/about | OK | 1.7 m/px; 5.2 × 144 km; >200× NAC; saturates in sunlight |
| 40 | https://ui.adsabs.harvard.edu/abs/2023JAI....1240004R/abstract | Fail (robots) | — |
| 41 | https://lroc.im-ldi.com/about/specs | OK | NAC/WAC specifications |
| 42 | https://lroc.im-ldi.com/about | OK | Target-request URL; data portal; downlink |
| 43 | https://target.lroc.im-ldi.com/output/lroc/lroc_page.html | Fail (robots.txt) | Request tool exists |
| 44 | https://data.im-ldi.com/mds | OK | SER data portal (LROC/ShadowCam) |
| 45 | https://lroc.im-ldi.com/images (plus ?page=2,3,5,6,7,8,11,14,15,19,21,22,23) | OK | Featured-image index navigation (14 fetches) |
| 46 | https://lroc.im-ldi.com/images/1456 (2 queries) | OK | ispace M2: 18:13 UTC, location, image IDs |
| 47 | https://lroc.im-ldi.com/images/1477 | OK | Not relevant (Posidonius Y) |
| 48 | https://lroc.im-ldi.com/images/1478 | OK | Not relevant |
| 49 | https://lroc.im-ldi.com/images/1302 | OK | HAKUTO-R M1 |
| 50 | https://lroc.im-ldi.com/images/1261 | OK | CE5-T1 double crater |
| 51 | https://lroc.im-ldi.com/images/1311 | OK | Luna 25 |
| 52 | https://www.nasa.gov/image-article/nasas-lro-observes-crater-likely-from-russias-luna-25-mission/ | 404 | — |
| 53 | https://lroc.im-ldi.com/images/1358 | OK | SLIM |
| 54 | https://lroc.im-ldi.com/images/1360 | OK | IM-1 |
| 55 | https://lroc.im-ldi.com/images/1374 | OK | Chang'e 6 |
| 56 | https://lroc.im-ldi.com/images/1407 | OK | Blue Ghost (nadir) |
| 57 | https://lroc.im-ldi.com/images/1408 (2 queries) | OK | IM-2 (time inconsistency) |
| 58 | https://lroc.im-ldi.com/images/1101 | OK | Beresheet |
| 59 | https://lroc.im-ldi.com/images/1131 | OK | Vikram |
| 60 | https://lroc.im-ldi.com/images/1132 | OK | Longjiang-2 |
| 61 | https://lroc.im-ldi.com/images/822 (2 queries) | OK | LADEE |
| 62 | https://www.nasa.gov/missions/lro/nasas-lro-observes-crater-likely-from-russias-luna-25-mission/ | 404 | — |
| 63 | https://www.nasa.gov/content/goddard/nasa-lro-spacecraft-captures-images-of-ladees-impact-site/ | 404 | — |
| 64 | https://en.wikipedia.org/wiki/Luna_25 | OK [S] | Used to find the NASA URL |
| 65 | https://en.wikipedia.org/wiki/LADEE | OK [S] | Impact window 04:30–05:22 UTC |
| 66 | https://www.nasa.gov/humans-in-space/nasas-lro-observes-crater-likely-from-luna-25-impact/ | OK | 31 Aug 2023 release; 24 Aug imaging; ~10 m |
| 67 | https://www.nasa.gov/image-article/nasas-lro-spacecraft-captures-images-ladees-impact-crater/ | 404 | — |
| 68 | https://lroc.im-ldi.com/images/596 | OK | GRAIL |
| 69 | https://lroc.im-ldi.com/images/1314 | OK | Chandrayaan-3 oblique (42°) after 4 d |
| 70 | https://en.wikipedia.org/wiki/GRAIL | OK [S] | LAMP view of the GRAIL plume (caption) |
| 71 | https://en.wikipedia.org/wiki/LCROSS | OK [S] | Diviner detected LCROSS in all 4 thermal channels |
| 72 | https://www.nasa.gov/mission_pages/LRO/news/grail-impact.html | 404 | — |
| 73 | https://www.jpl.nasa.gov/news/nasas-lro-sees-grail-impact-plume | 404 | — |
| 74 | https://doi.org/10.1126/science.1186474 | 403 | Gladstone et al. 2010 not retrieved |
| 75 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1126/science.1186474&resultType=core&format=json | 429 rate-limited; not retried | — |
| 76 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1126/science.1197135&resultType=core&format=json | 429 rate-limited; not retried | — |
| 77 | https://www.boulder.swri.edu/lamp/ | OK | General only |
| 78 | https://www.diviner.ucla.edu/ | OK | General only |
| 79 | https://science.nasa.gov/mission/lro/science-and-data/ | OK | Instrument overview |
| 80 | https://www.diviner.ucla.edu/blog | 404 | — |
| 81 | https://science.nasa.gov/mission/lcross/ | OK | Diviner ~90 s after impact at ~80 km; crater ~20 m |
| 82 | https://science.nasa.gov/mission/grail/ | OK | Impact 17 Dec 2012, 1.68 km/s |
| 83 | https://science.nasa.gov/mission/lro/lamp/ | 404 | — |
| 84 | https://nssdc.gsfc.nasa.gov/nmc/experiment/display.action?id=2009-031A-06 / -05 / -04 / -03 / -02 | OK (5 fetches) | CRaTER, LEND, LOLA, LAMP, Diviner specs |
| 85 | https://www.isro.gov.in/Chandrayaan2_home.html | 404 | — |
| 86 | https://pradan.issdc.gov.in/ch2/ | OK | ISDA portal, login; OHRC 0.25 m |
| 87 | https://www.isro.gov.in/Chandrayaan_2.html | OK | 100 km; "almost seven years" |
| 88 | https://www.issdc.gov.in/ch2.html | 404 | — |
| 89 | https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=-152&OBJ_DATA=YES&MAKE_EPHEM=NO | OK | Ch-2 ISRO orbit determination to 2026-11-08 |
| 90 | https://www.isro.gov.in/Chandrayan_2.html | OK | No details |
| 91 | …COMMAND=-152&EPHEM_TYPE=E…2024-01-01→2026-11-01…REF_PLANE=B | OK | Ch-2 orbit ~100 km polar |
| 92 | https://en.wikipedia.org/wiki/Chandrayaan-2 | OK [S] | Collision avoidance with LRO (2021, 2024) |
| 93 | https://www.currentscience.ac.in/Volumes/118/04/0560.pdf | OK | OHRC paper (Chowdhury et al. 2020) |
| 94 | https://www.currentscience.ac.in/Volumes/118/04/0566.pdf | Fail (robots) | TMC-2 not verified |
| 95 | https://en.wikipedia.org/wiki/Chang%27e_7 (2 queries) | OK [S] | Planned Aug 2026; at Wenchang Apr 2026; camera specs |
| 96 | https://www.cnsa.gov.cn/english/ | OK | No Chang'e 7 launch news |
| 97 | https://en.wikipedia.org/wiki/2026_in_spaceflight | OK [S] | Artemis II 1–11 Apr 2026; IM-3/Griffin planned Dec 2026 |
| 98 | https://en.wikipedia.org/wiki/List_of_missions_to_the_Moon | OK [S] | Planned missions 2026–2029 |
| 99 | https://zh.wikipedia.org/wiki/嫦娥七号 | Fail (cache-only) | — |
| 100 | https://spacenews.com/tag/change-7/ | OK, no content | — |
| 101 | https://www.planetary.org/space-missions/change-7 | OK [S] | Launch "second half of 2026" |
| 102 | Horizons COMMAND=Chang / COMMAND=Queqiao | OK | Only Chang'e boosters tracked |
| 103 | https://en.wikipedia.org/wiki/List_of_Long_March_launches_(2025%E2%80%932029) | OK [S] | Chang'e 7 "2026 (TBD)"; latest launch listed 19 Sep 2026 |
| 104 | https://moon.bao.ac.cn/ | JavaScript-only | — |
| 105 | https://www.cnsa.gov.cn/english/n6465645/n6465648/c6840870/content.html | OK | Chang'e 7 AO (21 Sep 2022) |
| 106 | https://shadowcam.im-ldi.com/news | OK | PDS release cadence |
| 107 | https://science.nasa.gov/mission/lunar-trailblazer/ | OK | Lost; ended 31 Jul 2025 |
| 108 | https://shadowcam.im-ldi.com/posts/1500 | OK | 21 Aug 2026 release = Jul–Sep 2025 data |
| 109 | https://shadowcam.im-ldi.com/posts/1479 | OK | 22 May 2026 release = Apr–Jun 2025 data |
| 110 | https://kpds.kari.re.kr/ | Fail (DNS) | — |
| 111 | https://www.kasa.go.kr/eng/ | 404 | — |
| 112 | https://ko.wikipedia.org/wiki/다누리 | OK (disambiguation) | — |
| 113 | https://ko.wikipedia.org/wiki/다누리_(달_탐사선) | Fail (cache-only) | — |
| 114 | https://www.nasa.gov/fy-2026-budget-request/ | OK | Technical supplement link |
| 115 | https://www.planetary.org/articles/fy2026-presidents-budget-request-for-nasa | 404 | — |
| 116 | https://www.nasa.gov/wp-content/uploads/2025/05/fy-2026-budget-technical-supplement-002.pdf (2 queries) | OK (excerpt) | LDEP FY2024 $363.4M → FY2026 request $137.3M; LRO not found in excerpt |
| 117 | https://www.planetary.org/save-nasa-science (2 queries) | OK [S] | FY2026 enacted 23 Jan 2026 ($24.4B); FY2027 PBR −46% science, ~53 missions |
| 118 | https://en.wikipedia.org/wiki/Budget_of_NASA | OK [S] | Congress rejected nearly all FY2026 cuts |
| 119 | https://planetary.s3.amazonaws.com/assets/pdfs/FY-2027-NASA-Budget-Request-List-of-Cancelled-Science-Missions.pdf | Fail (robots) | LRO status on the list unknown |
| 120 | https://www.nasa.gov/wp-content/uploads/2026/04/fiscal-year-2027-full-budget-request.pdf (2 queries) | OK (excerpt) | LDEP FY2027 $204.0M; LRO not named in excerpt |
| 121 | https://science.nasa.gov/planetary-science/programs/planetary-mission-senior-review/ | 404 | — |
| 122 | https://science.nasa.gov/researchers/planetary-mission-senior-review/ | 404 | — |
| 123 | https://science.nasa.gov/planetary-science/ | OK | No Senior Review links |
| 124 | https://www.lpi.usra.edu/leag/ | OK | Nothing on LRO extension |
| 125 | https://www.nasa.gov/history/15-years-ago-lunar-reconnaissance-orbiter-begins-moon-mapping-mission/ | OK | "Enough fuel on board to operate until 2027" (18 Jun 2024) |
| 126 | …COMMAND=-85…2010-01-01→2023-01-01, 183d, REF_PLANE=B | OK | LRO orbit history 2010–2022 |
| 127 | https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/LRO/lamp.html | Fail (robots) | — |
| 128 | https://pds-ppi.igpp.ucla.edu/mission/Lunar_Reconnaissance_Orbiter | OK, no content | — |
| 129 | https://www.nasa.gov/image-article/nasas-lro-spacecraft-captures-images-of-ladees-impact-crater/ | 404 | — |
| 130 | https://www.nasa.gov/missions/lro/nasas-lro-spacecraft-captures-images-of-ladees-impact-crater/ | OK | LADEE release 28 Oct 2014; crater <3 m |
| 131 | …COMMAND=-85&EPHEM_TYPE=E…2023-01-01→2026-09-01, 61d (ecliptic) | OK | Node drift used for the β model |
| 132 | …COMMAND=-155&EPHEM_TYPE=E…2025-11-01→2027-03-01, 60d (ecliptic) | OK | Danuri node and argument of periapsis |
| 133 | https://lroc.im-ldi.com/images/1406 | OK | Blue Ghost oblique 2 Mar 2025 17:49 UTC |
| 134 | https://lroc.im-ldi.com/images/1501 | OK | McGetchin; NAC opportunities "only a few days each month" |
| 135 | https://www.lpi.usra.edu/planetary_news/?s=senior+review | OK, nothing | — |
| 136 | https://www.lpi.usra.edu/planetary_news/?s=Lunar+Reconnaissance+Orbiter | OK | McGetchin feature only |
| 137 | https://www.esa.int/Applications/Connectivity_and_Secure_Communications/Lunar_Pathfinder | 403 | — |
| 138 | https://fireflyspace.com/missions/blue-ghost-mission-2/ | OK | NET 2027; Elytra 5 yr; carries Lunar Pathfinder; Ocula |
| 139 | https://fireflyspace.com/ocula/ | OK | 0.2 m at 50 km; LLNL; late 2026 / 2028 / 2029 |
| 140 | https://www.esa.int/Applications/Connectivity_and_Secure_Communications/Moonlight | OK | "Firefly to take Lunar Pathfinder" (22 Mar 2023) |
| 141 | https://www.intuitivemachines.com/lunardatanetwork | Fail (robots/redirects) | — |
| 142 | https://www.intuitivemachines.com/ | OK, no details | — |
| 143 | https://en.wikipedia.org/wiki/Queqiao-2 | OK [S] | Orbit and payloads |
| 144 | https://en.wikipedia.org/wiki/Chang%27e_5 | OK [S] | Orbiter in DRO since Feb 2022 |
| 145 | https://pds-geosciences.wustl.edu/missions/lro/default.htm (2 queries) | OK | Release 67 on 15 Sep 2026; schedule to Release 70 (data to 14 Mar 2027) |
| 146 | https://export.arxiv.org/api/query?search_query=all:Danuri&max_results=25 | Fail (robots) | — |
| 147 | https://arxiv.org/a/robinson_m_1 | 429 rate-limited; not retried | — |
| 148 | https://lroc.im-ldi.com/about/targeting | 404 | — |
| 149 | https://lroc.im-ldi.com/about/operations | 404 | — |
| 150 | https://www.nasa.gov/mission_pages/grail/news/grail20130319.html | 404 | — |
| 151 | https://www.jpl.nasa.gov/news/nasas-lro-sees-grail-impact-site | 404 | — |
| 152 | https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2022-096A / 2022-094A | Error page (2) | — |
| 153 | https://science.nasa.gov/mission/shadowcam/ | 404 | — |
| 154 | https://science.nasa.gov/mission/kplo/ | 404 | — |
| 155 | https://www.nasa.gov/fy-2027-budget-request/ | 404 | — |
| 156 | https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/aareadme.txt | OK | Points to spkinfo.txt |
| 157 | https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/spk/lrorg_2025349_2026074_v01.lbl | Unreadable (binary) | — |
| 158 | https://naif.jpl.nasa.gov/pub/naif/pds/data/lro-l-spice-6-v1.0/lrosp_1000/data/spk/spkinfo.txt | OK | lrorg = merged reconstructed daily definitive ephemerides |
| 159 | https://en.wikipedia.org/wiki/Chandrayaan-3 | OK [S] | OHRC imaged the Ch-3 lander (date not given) |

Totals: about 195 WebFetch attempts. About 145 returned content (including 13 JPL Horizons API calls). About 50 failed: 404, 403, robots.txt, cache-only, rate-limited (429, not retried), DNS, JavaScript-only or redirect. Direct curl to all hosts was blocked by egress policy (403), so WebFetch was used throughout.

### Method notes for derived items [D]

- **Orbits:** JPL Horizons osculating elements (center 500@301). REF_PLANE=B gives the lunar mean-equator frame; the default is ecliptic J2000. Altitude = radius − 1737.4 km.
- **β model:** β = asin(sin i · sin(Ω_ecl − λ☉)), using a quadratic fit to Horizons Ω_ecl for 2023–2026 (rms 0.15°) and a low-precision solar longitude. Overflight incidence ≈ arccos(cos φ cos β). Validated against four LROC-reported incidence angles (table above). Extrapolation to 2027–28 assumes no plane-change manoeuvres; the linear and quadratic node models differ by about 2–3 weeks by mid-2028.
- **Image-ID timing:** acquisition time = 2023-08-24 18:15 UTC + (ID − 1447540283) s. The anchor is the Luna 25 sequence start. It reproduces IM-1 to 1 min, Blue Ghost to 2 min, and other stated dates within the same day. It conflicts with the IM-2 caption by about 23 h.
- **Line-of-sight fraction:** spherical-cap fraction (1 − cos θ)/2 with cos θ = R/(R + h).
