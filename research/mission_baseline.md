# AYAP-1 (Ay Araştırma Programı-1 / TLM-1): factual mission baseline

- **Evidence cutoff:** 5 October 2026. All URLs accessed 2026-10-05.
- **Scope:** Türkiye's first lunar spacecraft (official 2026 name: "Ay Uzay Aracı"; program name: AYAP-1; conference name: TLM-1; IRF name: "Turkish Lunar Mission-1 (AYAP-1)").
- **Method:** WebFetch only. WebSearch was disabled, and curl, wget and python were not used. Every quote below was extracted from the live page by the WebFetch helper model. Short quotes are reproduced as returned. Spot-check diacritics and exact wording against the live page before you cite one.
- **Inferences:** Every inference is labelled **[INFERENCE]**. Anything not labelled that way is a statement made by the cited source.

## Status and source-type definitions

- **confirmed:** a primary or near-primary source states it as a current fact. Examples: hardware built, contract signed, test performed, design specification published.
- **targeted:** a plan, goal or schedule, such as a launch window, orbit or duration.
- **assumed:** an inference made in this report. It is not stated by any source.
- **unknown:** not published in any source reached.

Source types:
- **official agency:** TUA, TÜBİTAK, TÜBİTAK UZAY, Ministry of Industry & Technology.
- **contractor:** includes payload providers such as IRF and Thales Alenia Space.
- **conference abstract**
- **press:** "state agency" marks Anadolu Ajansı (AA) and TRT.
- **encyclopedic:** Wikipedia. Used only as a pointer to references.

---

## (a) Provenance table

Short names used in the Source column:

- **TUA-16Sep26:** https://tua.gov.tr/tr/haberler/turkiye-nin-ay-yolculugunda-geri-sayim-basladi (16 Sep 2026)
- **UZAY-TR-14Sep26:** https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-uzay-aracinin-entegrasyon-faaliyetleri-tamamlandi/ (14 Sep 2026)
- **UZAY-EN-14Sep26:** https://uzay.tubitak.gov.tr/en/integration-activities-of-turkiyes-first-lunar-spacecraft-successfully-concluded/?lang=en (14 Sep 2026; this URL works only with `?lang=en`)
- **TUBITAK-15Sep26:** https://tubitak.gov.tr/tr/haber/turkiyenin-ilk-ay-uzay-aracinin-entegrasyon-faaliyetleri-tamamlandi (15 Sep 2026)
- **UZAY-PROG:** https://uzay.tubitak.gov.tr/uzayin-kesfi-ay-arastirma-programi/ (TR) and https://uzay.tubitak.gov.tr/en/space-exploration-lunar-research-program/?lang=en (EN). Program page, undated. It cites the 14 Sep 2026 milestone, so the current version dates from Sep 2026 or later.
- **UZAY-SWG4:** https://uzay.tubitak.gov.tr/turkiyenin-ay-gorevi-4-ay-bilimsel-calisma-grubu-toplantisi/ (10 Jun 2026)
- **UZAY-SWG2:** https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-gorevi-ayap-1-kapsaminda-30-ve-31-ocak-2024-tarihlerinde-2-bilimsel-calisma-grubu-toplantisi-turk-hava-kurumu-universitesinin-ev-sahipliginde-gerceklesti/ (2 Feb 2024)
- **GLEX25:** https://iafastro.directory/iac/paper/id/93595/abstract-pdf/GLEX-2025,2,2,1,x93595.brief.pdf. Yağlıoğlu, Boğa İnaltekin, Avenoğlu and Nefes (TÜBİTAK UZAY), "The Mission, Science and Technology Objectives of the First Turkish Lunar Mission". Global Space Exploration Conference 2025, session "Lunar, Mars, Near-Earth Asteroids, Deep Space Exploration – Session 2", paper 93595. Conference date and location were not verified in this session.
- **NSP-DOC:** https://cdn.tua.gov.tr/63da672cab079.pdf. "2022-2030 Milli Uzay Programı Strateji Belgesi" (TUA). Circular 2022/4 dated 23 May 2022, published in Resmî Gazete 31845 on 24 May 2022. The Moon program is §3.1.
- **IRF-Dec25:** https://www.irf.se/en/aktuellt/2025/12-02-irf-instrument-for-turkisk-manmission-narmar-sig-leverans-efter-lyckat-test/ ("IRF instrument for Turkish lunar mission nears delivery after successful test"). The date (2 Dec 2025) comes from the URL path. The page shows no date.
- **IRF-Jul26:** https://www.irf.se/en/aktuellt/2026/07-28-svenskt-maninstrument-fran-kiruna-levereras-till-turkiet/ ("Swedish lunar instrument from Kiruna delivered to Türkiye"). The date (28 Jul 2026) comes from the URL path. The page shows no date.
- **IRF-AYAP1:** https://www.irf.se/en/i-rymden/ayap-1/ (undated mission page; Wikipedia cites it with the date 2026-03-31)
- **TAS-Nov23:** https://www.thalesaleniaspace.com/en/press-releases/thales-alenia-space-provide-communication-transponder-turkeys-first-lunar-mission (21 Nov 2023). Mirror: https://www.asdnews.com/news/aerospace/2023/11/22/thales-alenia-space-provide-communication-transponder-turkeys-1st-lunar-mission (22 Nov 2023).
- **DT-…:** DefenceTurk articles (press). The full URLs are in the log (e).

| # | Parameter | Value (quoted as published; TR original + EN translation where relevant) | Units | Source (URL) | Pub./update date | Uncertainty / notes | Status | Source type |
|---|---|---|---|---|---|---|---|---|
| **Identity & governance** |||||||||
| 1 | Mission/spacecraft names | "Türkiye'nin ilk Ay Görevi (AYAP-1)" (UZAY-SWG2). "With the TLM-1 project, Turkiye will realize its first Lunar mission" (GLEX25). "Turkish lunar Mission-1 (AYAP-1)" (IRF-Jul26). The Sept 2026 releases use "Ay Uzay Aracı" (Lunar Spacecraft) and do not use "AYAP-1". TUA still used "AYAP-1" on 2 Sep 2026: https://tua.gov.tr/tr/haberler/turkiye-artemis-mutabakati-ni-imzaladi | – | as listed | 2024–2026 | Naming is inconsistent across sources. Treat AYAP-1, TLM-1 and "Ay Uzay Aracı" as the same spacecraft. | confirmed | official / conference abstract / contractor |
| 2 | Program owner and policy basis | Moon program = National Space Program goal #1 ("Ay Görevi"). §3.1 of the Strategy Document. | – | NSP-DOC; https://uzay.tubitak.gov.tr/milli-uzay-programi-cumhurbaskani-erdogan-tarafindan-tanitildi/ | 10 Feb 2021; 23–24 May 2022 | – | confirmed | official agency |
| 3 | Prime / project executor | "AYAP-1 TÜBİTAK UZAY proje yürütücülüğünde ve Delta V alt yükleniciliğinde gerçekleştirilen" (AYAP-1, carried out with TÜBİTAK UZAY as project executor and Delta V as subcontractor). Also: "TÜBİTAK UZAY, uzay aracının tasarım, test, fırlatma ve operasyonlarını üstlenecek" (TÜBİTAK UZAY will undertake the design, test, launch and operations of the spacecraft). | – | DT-24Apr24 https://www.defenceturk.net/delta-vden-uzay-ucus-testi ; DT-6Feb24 https://www.defenceturk.net/turkiyenin-aya-yolculuk-icin-calismalari-devam-ediyor | 24 Apr 2024; 6 Feb 2024 | Press wording. It is consistent with all TÜBİTAK UZAY releases ("developed under the leadership of TUBITAK UZAY", AA 2 Oct 2026). | confirmed | press |
| 4 | Hybrid propulsion developer | "DeltaV ortaklığıyla geliştirilen yerli Hibrit İtki Sistemi" (domestic Hybrid Propulsion System developed in partnership with DeltaV). Architecture: "Platform modülü TÜBİTAK UZAY tarafından tasarlanan ve itki sistemi DeltaV Uzay Teknolojileri tarafından geliştirilen … iki ayrı modülden oluşan" (two separate modules: a platform module designed by TÜBİTAK UZAY and a propulsion system developed by DeltaV). | – | TUBITAK-15Sep26; DT-24Apr24; DT-3Oct23 https://www.defenceturk.net/ayap-1-uzay-araci-iac-2023te-sergileniyor | 15 Sep 2026; 2023–24 | The Sept 2026 TUA and TÜBİTAK UZAY texts say only "yerli/milli imkânlarla geliştirilen" (domestically developed). Only the TÜBİTAK HQ text names DeltaV. | confirmed | official agency + press |
| 5 | Delta V ownership | "2017 yılında SSB iştiraki olarak kurulan Delta V" (Delta V, established in 2017 as an affiliate of SSB, the Presidency of Defence Industries). NSP-DOC: "SSB ile Delta V Uzay Teknolojileri arasında imzalanan sözleşme kapsamında, hibrit yakıt teknolojisi temelli bir uzay roket motorunun deneysel prototipinin geliştirilmesi amaçlanmıştır" (under a contract signed between SSB and Delta V, the aim is to develop an experimental prototype of a space rocket motor based on hybrid-fuel technology). | – | DT-24Apr24; NSP-DOC | 2024; 2022 | Delta V's own website could not be reached (connection timeout). | confirmed | press / official agency |
| 6 | Other domestic contributors | Solar panels: "TÜBİTAK MAM Malzeme Enstitüsü tarafından üretilecek sabit güneş panelleri" (fixed solar panels to be produced by the TÜBİTAK MAM Materials Institute). Radiation calorimeter: "IRADETS firması tarafından geliştirilen Radyasyon Kalorimetresi" (Radiation Calorimeter developed by IRADETS), presented by Prof. Dr. Behçet Alpat. | – | DT-3Oct23; UZAY-SWG2 | 2023; 2024 | 2023–24 statements. Not re-confirmed in 2026. | confirmed (as of 2023–24) | press / official agency |
| 7 | Roles of ASELSAN, Roketsan | No AYAP-1 role found in any source reached. | – | – | – | Searched TUA, TÜBİTAK UZAY, DefenceTurk and SavunmaSanayiST. | unknown | – |
| 8 | Budget | Not found. NSP-DOC §3.1 gives no budget figure, according to the extraction. | – | NSP-DOC | 2022 | – | unknown | – |
| 9 | Program progress | "Kacir said the program, launched in early 2022, had reached 77% completion, with more than 200 engineers contributing" | %, count | AA https://www.aa.com.tr/en/turkiye/from-ottoman-rocket-man-to-lunar-mission-how-did-turkiye-s-long-road-into-space-begin/4076132 | 2 Oct 2026 | The date of Kacır's statement is not given (probably Sep 2026). Read "launched in early 2022" as the start of the spacecraft project. The policy goal dates from Feb 2021. | confirmed (as stated) | press (state agency) |
| **Integration & test** |||||||||
| 10 | Integration complete / public unveiling | "The Lunar Spacecraft was formally introduced to the public during a press conference held at the TÜBİTAK UZAY (OPMER) facilities on September 14, 2026, with the participation of Mehmet Fatih Kacır." TR: "entegrasyon faaliyetleri 14 Eylül 2026 tarihinde tamamlandı" (integration activities were completed on 14 September 2026). | date | UZAY-EN-14Sep26; UZAY-PROG | 14 Sep 2026 | OPMER = "TÜBİTAK UZAY Optik Sistemler Araştırma Laboratuvarı" (Optical Systems Research Laboratory), per UZAY-TR-14Sep26. | confirmed | official agency |
| 11 | Environmental test campaign | At TUSAŞ USET. TR: "akustik yükler ve titreşim koşullarının yanı sıra, uzay ortamını simüle eden ısıl vakum testleri ile elektromanyetik uyumluluk testlerinden geçirilecek" (it will be put through acoustic loads and vibration conditions, plus thermal-vacuum tests that simulate the space environment and electromagnetic compatibility tests). EN: "Thermal vacuum (TVAC), structural, and electromagnetic compatibility (EMC) tests". | – | TUBITAK-15Sep26; UZAY-EN-14Sep26; TUA-16Sep26 | Sep 2026 | In progress at the cutoff. No completion reported. | targeted (in progress) | official agency |
| 12 | Final pre-launch processing | "brought back to TÜBİTAK UZAY's cleanroom and integration center at the Middle East Technical University (METU) campus for final pre-launch checks". TR: the clean room is "yapımı devam eden" (still under construction). DefenceTurk: "T-STAR Uydu ve Uzay Aracı Tasarım Merkezi'ndeki nihai hazırlıklar" (final preparations at the T-STAR Satellite and Spacecraft Design Center). | – | UZAY-EN-14Sep26; UZAY-TR-14Sep26; DT-15Sep26 https://www.defenceturk.net/ay-uzay-aracinda-test-donemi | Sep 2026 | **[INFERENCE]** T-STAR and the METU clean room are probably the same facility. Not confirmed. | targeted | official agency / press |
| **Launch** |||||||||
| 13 | Launch window (institutional) | TR: "2027 yılının ilk yarısında fırlatılması hedefleniyor" (launch targeted for the first half of 2027). EN: "targeted for launch in the first half of 2027". | – | UZAY-TR-14Sep26; UZAY-EN-14Sep26; TUBITAK-15Sep26 | 14–15 Sep 2026 | – | targeted | official agency |
| 14 | Launch date (spec table) | "Beklenen Fırlatma Tarihi: 2027 Q2" (expected launch date). EN: "Target Launch Date 2027 Q2". | quarter | UZAY-PROG | 2026 | This is the most specific official value found. | targeted | official agency |
| 15 | Launch window (ministerial / agency) | Kacır: "2027'nin ilk aylarında fırlatmayı planladığımız Ay Uzay Aracımız…" (our Lunar Spacecraft, which we plan to launch in the first months of 2027). TUA: "2027 yılının ilk aylarında fırlatılması hedeflenen" (targeted for launch in the first months of 2027). AA: "lift-off is planned for the first months of 2027". | – | TUBITAK-15Sep26; TUA-16Sep26; AA 2 Oct 2026 | Sep–Oct 2026 | "First months" reads earlier than "Q2". See (b). | targeted | official agency / press |
| 16 | Launch site | TUA: "Kennedy Uzay Merkezi'ne gönderilmesi planlanıyor" (planned to be sent to Kennedy Space Center). TÜBİTAK: "ABD'deki Kennedy Uzay Merkezi'ne nakledilecek" (will be transported to Kennedy Space Center in the USA). AA: "shipped to the Kennedy Space Center in the US for launch". TÜBİTAK UZAY TR: "Uzay aracının ABD'deki Cape Canaveral'a sevk edilmesi planlanıyor" (the spacecraft is planned to be shipped to Cape Canaveral, USA). EN: "planned to be shipped to Cape Canaveral". | – | TUA-16Sep26; TUBITAK-15Sep26; AA; UZAY-TR/EN-14Sep26 | Sep–Oct 2026 | These statements describe where the spacecraft is shipped. No pad is named. "Cape Canaveral" can mean the cape, which includes KSC. | targeted | official agency |
| 17 | Launch vehicle and provider | **Not published.** None of TUA, TÜBİTAK, TÜBİTAK UZAY, AA or DefenceTurk (Sep–Oct 2026) names a rocket or provider. The AA article mentions Falcon 9 only for İMECE (2023). | – | all 2026 sources | – | **[INFERENCE]** A KSC/Cape Canaveral launch implies a US commercial launcher. KSC LC-39A is used by SpaceX. That does not make SpaceX/Falcon 9 a confirmed fact. Launch Library 2, Next Spaceflight, Spaceflight Now and Wikipedia "2027 in spaceflight" have no AYAP-1 entry. | unknown | – |
| 18 | Launch contract (date, value) | Not published. | – | – | – | – | unknown | – |
| 19 | Dedicated vs rideshare | Not published. | – | – | – | **[INFERENCE]** The supersynchronous-GTO injection (#20) points to a GTO-class launch. It could be dedicated or a co-passenger slot. No evidence either way. | unknown | – |
| 20 | Injection orbit | "The spacecraft will be launched to a Supersynchronous GTO and will follow a series of transfer orbits until Lunar transfer orbit injection." | – | GLEX25 | 2025 (abstract) | No perigee, apogee or inclination is given. | targeted | conference abstract |
| 21 | Policy on launch | NSP-DOC: "Dünya yörüngesine uluslararası iş birliği ile çıkarılacak yerli uzay aracımız Ay'a ulaşacaktır" (our domestic spacecraft, to be placed in Earth orbit through international cooperation, will reach the Moon). NSP 2021: "uluslararası iş birliği ile yakın Dünya yörüngesinde ateşlenecek milli ve özgün hibrit roketle Ay'a sert iniş" (a hard landing on the Moon with a national, original hybrid rocket to be fired in near-Earth orbit, through international cooperation). | – | NSP-DOC; TÜBİTAK UZAY 10 Feb 2021 | 2021–22 | – | confirmed (policy) | official agency |
| **Spacecraft** |||||||||
| 22 | Mass | TR: "Yaklaşık 3,5 ton ağırlığındaki Ay Uzay Aracı" (the Lunar Spacecraft, weighing approximately 3.5 tons). EN: "launch mass of approximately 3.5 tons". | t | TUA-16Sep26; UZAY-EN-14Sep26; UZAY-SWG4 ("3,5 tonluk") | Jun–Sep 2026 | Approximate. TÜBİTAK UZAY EN calls it launch (wet) mass. | confirmed (approx.) | official agency |
| 23 | Launch-mass ceiling | "Fırlatma Kütlesi: < 3600 kg" (launch mass) | kg | UZAY-PROG | 2026 | Consistent with #22. | confirmed (spec) | official agency |
| 24 | Dry mass; propellant mass (hybrid fuel/oxidizer; bipropellant) | Not published. | kg | – | – | – | unknown | – |
| 25 | Dimensions | "Fırlatma anında 4,1 metre çapa sahip olan araç, panelleri açıldığında 2,7 metreye 8,3 metrelik boyutlara ulaşıyor." (At launch the spacecraft is 4.1 m in diameter; with its panels opened it measures 2.7 m × 8.3 m.) | m | TUBITAK-15Sep26 | 15 Sep 2026 | This is in tension with "fixed solar arrays" (#33). The arrays may be deployed once and then fixed (non-tracking). Not clarified. | confirmed (as stated) | official agency |
| 26 | Power | "Güç Sağlama Kapasitesi: 2,6 kW" (power supply capacity). EN: "Output Power Capability 2.6 kW". | kW | UZAY-PROG | 2026 | Does not say whether this is BOL or EOL, or at what Sun distance. | confirmed (spec) | official agency |
| 27 | Payload capacity | "Görev Yükü Kapasitesi: 300 kg" (payload capacity) | kg | UZAY-PROG | 2026 | – | confirmed (spec) | official agency |
| 28 | Bus / platform | "The TstarD-100, deep-space customized variant of TÜBİTAK UZAY's Tstar platform family, will function in an integrated manner to execute core operations such as power management, telecommunications, flight management, attitude and orbit control (AOCS), and thermal control." | – | UZAY-EN-14Sep26; UZAY-PROG | 2026 | Heritage: Tstar family (İMECE/TÜRKSAT 6A platforms named TstarL and TstarG-100 on https://uzay.tubitak.gov.tr/uydu-platformlari/). That page does not list TstarD-100. | confirmed | official agency |
| 29 | Domestic content | TR: "yüzde 80'in üzerinde yerlilik oranı" (over 80 percent domestic content). "Of the 65 critical equipment … 56 have been developed domestically." "24 structural panels" (primary bus). "Projedeki yazılımların tamamının yerli olduğunu" (all of the project's software is domestic). | %, count | TUA-16Sep26; UZAY-EN-14Sep26; UZAY-SWG4 | 2026 | 56/65 = 86 % by equipment count. Ministry figure: >80 %. | confirmed | official agency |
| 30 | Domestic subsystem list | "spacecraft management equipment, payload interface equipment, chemical propulsion interface equipment, temperature monitoring interface equipment, power conditioning and distribution equipment (PCDU), S and X-Band communication systems (receivers and transmitters, patch and horn antennas, low noise amplifiers, etc.), reaction wheels, inertial measurement units (IMU), flight harness, fixed solar arrays, video cameras, and a vision-based navigation system" | – | UZAY-EN-14Sep26 | 14 Sep 2026 | TÜBİTAK HQ adds "uçuş bilgisayarı" (flight computer). | confirmed | official agency |
| 31 | Communications | 2022 design: "S ve X bant olmak üzere 2 farklı frekans bandında çalışan haberleşme sistemi" (communication system working in two frequency bands, S and X). "S-Bant ile uzkomut ve uzölçüm … haberleşmesi" (telecommand and telemetry over S-band). "Yönlendirilebilir X-Bant anteni ile yüksek hacimli veriler (görüntü ve video gibi) yere aktarılır" (high-volume data such as images and video is sent to the ground via a steerable X-band antenna). Contractor: "Thales Alenia Space will provide an S-Band TT&C (Tracking, Telemetry and Command) Transponder for the AYAP-1 spacecraft". "The TT&C link is also instrumental to monitor the position of the spacecraft by measuring the distance to the ground station." Supplier site: Madrid. Contract with TÜBİTAK UZAY announced 21–22 Nov 2023. | – | DT-16Dec22 https://www.defenceturk.net/ay-gorevi-icin-gelistirilen-ayap-1-uzay-araci-hakkinda-ilk-detaylar ; TAS-Nov23 | 2022; 2023 | The 2026 releases list "S and X-Band communication systems" as domestic. How that relates to the foreign Thales S-band transponder is not stated: they may be complementary units, or there may have been a change. Data rates, EIRP, ground stations and any use of DSN or ESTRACK were not published. | confirmed (components) / unknown (link budget) | official / contractor / press |
| 32 | AOCS and navigation | Reaction wheels, IMU and a vision-based navigation system (2026). Star tracker described in 2022: "Yıldızların fotoğraflarını çekip hafızasındaki haritayla karşılaştırarak" (it photographs stars and compares them with the map in its memory). Lunar-orbit attitude (2022 design): "+Z yönü sürekli olarak Ay yüzeyine, X doğrultusu ise uçuş yönüne doğru bakacak" (+Z will point continuously at the lunar surface and X along the flight direction). | – | UZAY-EN-14Sep26; DT-16Dec22 | 2022–2026 | The attitude law is a 2022 design statement. | confirmed / targeted | official / press |
| 33 | Solar arrays | "sabit güneş panelleri aracın hem +X hem de -X yüzeylerinde bulunacak. Böylece bu panellerden biri sürekli güç üretebilecek" (fixed solar panels will be on both the +X and −X faces, so one of them can always generate power). 2026: "fixed solar arrays". | – | DT-16Dec22; DT-3Oct23; UZAY-EN-14Sep26 | 2022–2026 | See #25 for the "panels opened" wording. | confirmed | press / official |
| **Propulsion** |||||||||
| 34 | Main propulsion | "Milli Hibrit İtki Sistemi (HİS)" (National Hybrid Propulsion System), developed by DeltaV. | – | DT-17Mar22 https://www.defenceturk.net/turkiye-uzay-ajansi-ay-gorevi-hakkinda-yeni-gelismeleri-paylasti ; TUBITAK-15Sep26 | 2022–2026 | – | confirmed | press / official |
| 35 | HİS functional roles | 2022/23: "Hibrit itki sistemi yörünge yükseltme görevinde kullanılarak tarihçe kazanırken" (the hybrid system gains flight heritage by being used for orbit raising). Mar 2022 concept: "Dünya yörüngesinde yapılan testlerden sonra ise Ay yörüngesine girmek için DeltaV'nin hibrit motoru ateşleme yapacak" (after the Earth-orbit tests, DeltaV's hybrid motor will fire to enter lunar orbit). 2026 EOM: "controlled deorbit maneuvers executed utilizing its propulsion systems including domestic Hybrid Propulsion System". | – | DT-3Oct23; SavunmaSanayiST 16 Mar 2022; UZAY-EN-14Sep26 | 2022–2026 | It is not published which burns (orbit raising, TLI, LOI, deorbit) use HİS and which use the bipropellant system. | targeted | press / official |
| 36 | Secondary propulsion | "çift yakıtlı kimyasal itki sistemi ile yörünge ve yönelim elde etme ateşlemeleri gerçekleştirilecek" (orbit- and attitude-acquisition burns will be done with a bipropellant chemical propulsion system). 2026: "chemical propulsion interface equipment". | – | DT-16Dec22; DT-3Oct23; UZAY-EN-14Sep26 | 2022–2026 | Propellants, thrust and supplier not published. | confirmed (existence) | press / official |
| 37 | HİS performance: thrust, Isp, propellants, O/F, burn count, restart, throttling, Δv budget | **Not published** in any source reached. | N, s, m/s | – | – | – | unknown | – |
| 38 | HİS development status, 2022 | "Ön tasarım süreci, uçuş ölçekli ilk test prototipinin üretimi ve uçuş ölçekli yer testlerinin icra edileceği test sistemin üretimi ve kurulumu tamamlandı" (the preliminary design, production of the first flight-scale test prototype, and production and installation of the test system for flight-scale ground tests are complete) | – | https://www.savunmasanayist.com/ay-gorevinde-kullanilacak-milli-hibrit-itki-sisteminin-goruntuleri-paylasildi/ | 16 Mar 2022 | Ground test dates and durations not published. | confirmed (2022) | press (quoting TUA) |
| 39 | HİS igniter space-environment test | "Ay Görevi'nde kullanılacak olan Milli Hibrit İtki Sistemi(HİS) ateşleyicisinin ilk uzay ortam testleri başarıyla gerçekleştirildi" (the first space-environment tests of the HİS igniter for the Moon Mission were successfully completed). Announced by Minister Mustafa Varank on 22 Aug 2022. | – | DT-23Aug22 https://www.defenceturk.net/ay-gorevinde-kullanilacak-hibrit-roket-motorunun-uzay-testleri-yapildi | 23 Aug 2022 | The test vehicle and conditions are not given. | confirmed | press |
| 40 | HİS carried to space | "Dünya'da ilk kez bir Hibrit İtki Sistemi uzaya taşındı!" (for the first time in the world, a hybrid propulsion system was carried to space). Delta V sounding-rocket flight to 103 km, about 13 May 2023. | km | DT-18May23 https://www.defenceturk.net/delta-v-103-km-irtifaya-ulasti | 18 May 2023 | – | confirmed | press (quoting Delta V) |
| 41 | HİS fired in space | "Hibrit İtki Sistemi (HİS) 'Uzayda ateşlenen ilk hibrit sistem' oldu" (HİS became "the first hybrid system fired in space"). "Sonda roket sistemimiz SORS, 100 km irtifayı geçti" (our sounding-rocket system SORS passed 100 km altitude). Announced 29 Oct 2023. "Ay'a Sert İniş Görevi için DeltaV … tarafından geliştirilmektedir" (being developed by DeltaV for the Moon Hard Landing Mission). | km | DT-30Oct23 https://www.defenceturk.net/deltav-uzaydan-cumhuriyetin-yuzuncu-yilinda-bir-ilk | 30 Oct 2023 | Burn duration and thrust not given. Whether this was flight-configuration HİS or a scaled unit is not stated. | confirmed | press (quoting Delta V) |
| 42 | Related Delta V flights | SORS flight on 22 Apr 2024 ("100 km'ye erişme hedefi", a target of reaching 100 km), carrying a TUA logo. HİSTEP two-stage hybrid platform reached "200+ km" on 1 Jun 2025. That article says AYAP-1 was "planned to be completed in 2026". | km | DT-24Apr24; DT-6Jun25 https://www.defenceturk.net/hibrit-itkili-roket-ile-irtifa-rekoru | 2024–25 | These are not AYAP-1 flight hardware. Shown for propulsion heritage only. | confirmed | press |
| **Mission profile** |||||||||
| 43 | Early operations (2022 concept) | "Uzay aracı öncelikle bir fırlatıcı ile uzaya taşınacak. Ardından … sistem başlatması ve takla sönümleme gibi aşamaları gerçekleştirdikten sonra yörünge testlerini icra edecek." (The spacecraft will first be carried to space by a launcher. Then, after phases such as system start-up and tumble damping, it will carry out orbit tests.) DefenceTurk also mentions a "BBQ mode" (helper paraphrase; exact wording not extracted). | – | SavunmaSanayiST 16 Mar 2022; DT-17Mar22 | Mar 2022 | This is a 2022 concept. | targeted | press (quoting TUA) |
| 44 | Transfer | "series of transfer orbits until Lunar transfer orbit injection" (GLEX25). "translunar trajectory lasting approximately two months" (UZAY-EN). TR: "yaklaşık iki aylık yolculuğun ardından" (after a journey of about two months). | months | GLEX25; UZAY-EN-14Sep26; TUA-16Sep26 | 2025–26 | **[INFERENCE]** About 2 months is consistent with multi-burn phasing or orbit raising from supersynchronous GTO (or a low-energy transfer). The burn sequence is not published. | targeted | conference abstract / official |
| 45 | Lunar mission orbit | TR: "Ay yüzeyinden 100 kilometre irtifada bulunan kutupsal ve dairesel görev yörüngesine" (to a polar, circular mission orbit 100 km above the lunar surface). EN: "100 km circular polar lunar orbit". | km | TUA-16Sep26; UZAY-PROG; GLEX25 | 2025–26 | Exact inclination, RAAN/LTAN, period, eclipse statements and frozen-orbit design are not published. | targeted | official |
| 46 | Nominal orbital duration | TR: "en az üç ay boyunca görev yapması" (to operate for at least three months). EN: "a minimum of three months". | months | TUA-16Sep26; UZAY-EN-14Sep26 | Sep 2026 | – | targeted | official |
| 47 | Extended duration | Kacır: "görev performansına bağlı olarak bu süreyi 1,5 yıla kadar uzatabileceğiz" (depending on mission performance, we can extend this period up to 1.5 years). TUA: "bir buçuk yıla kadar uzatılabilmesi hedefleniyor" (extension up to one and a half years is targeted). | years | TUBITAK-15Sep26; TUA-16Sep26; UZAY-PROG | Sep 2026 | IRF sources say up to 6 months. See (b). | targeted | official |
| 48 | End-of-mission (EOM) action | EN: "the spacecraft will be guided toward the lunar surface through controlled deorbit maneuvers executed utilizing its propulsion systems including domestic Hybrid Propulsion System". TR: "kontrollü manevralarla Ay yüzeyine ulaştırılması planlanıyor" (it is planned to bring it to the lunar surface with controlled manoeuvres). DefenceTurk: "kontrollü yavaşlatma manevralarıyla" (with controlled deceleration manoeuvres). | – | UZAY-EN-14Sep26; TUA-16Sep26; DT-15Sep26 | Sep 2026 | – | targeted | official / press |
| 49 | EOM landing type | "Görev sonunda yüzeye sert iniş gerçekleştireceğiz" (at the end of the mission we will make a hard landing on the surface). EN: "execute a hard landing on the surface at the end of the mission". NSP-DOC: "AYAP-1 adlı uzay aracı milli olarak geliştirilmiş hibrit roket motorunu uzayda ateşleyerek Ay'a sert iniş gerçekleştirecektir" (the AYAP-1 spacecraft will make a hard landing on the Moon by firing its nationally developed hybrid rocket motor in space). IRF: "controlled hard landing". | – | UZAY-PROG; NSP-DOC; IRF-AYAP1 | 2022–2026 | The Sept 2026 press releases avoid the words "sert iniş" (hard landing) and "çarpma" (impact). Their content is consistent with a hard landing. | targeted | official / contractor |
| 50 | Guided deceleration | "a de-orbit maneuver will be initiated and the spacecraft will be impacted to a target area on the Lunar surface"; "a guided deceleration will also be attempted before the impact to gain operational experience for the AYAP-2 soft landing mission" | – | GLEX25 | 2025 | **[INFERENCE]** The vision-based navigation system (#30) probably supports this attempt. Not stated. | targeted | conference abstract |
| 51 | Impact target region or coordinates | "a target area on the Lunar surface". No region or coordinates. | – | GLEX25 | – | – | unknown | – |
| 52 | Impact velocity, epoch, geometry | Not published. | – | – | – | – | unknown | – |
| 53 | Separate lander or impactor element | None stated: "a spacecraft is designed with combined features of orbiter and lander". Single spacecraft. | – | GLEX25 | 2025 | AA (8 Nov 2023) says "landing gear" and "image-assisted navigation" were in concept design. Those refer to soft-landing technologies for phase 2. | confirmed (design concept) | conference abstract |
| **Payloads & science** |||||||||
| 54 | Scientific payload manifest (latest) | TR: "İkisi yerli, ikisi uluslararası iş birliğiyle geliştirilen dört bilimsel görev yükünü Ay yörüngesine taşıyacak" (it will carry to lunar orbit four scientific payloads, two domestic and two developed through international cooperation). The four: "Radyasyon Kalorimetresi" (Radiation Calorimeter), "Radyasyon Dozimetresi" (Radiation Dosimeter), "Ay Nötr Parçacık Teleskobu" (Lunar Neutral Particle Telescope; IRF), "Dar Açılı Ay Radyometresi" (Narrow-Angle Lunar Radiometer; "Çin Shenzhen Üniversitesi", China's Shenzhen University). EN: "Lunar Narrow Field of View Radiometer, developed by China's Shenzhen University". | count | UZAY-TR/EN-14Sep26; TUBITAK-15Sep26 | 14–15 Sep 2026 | – | confirmed | official agency |
| 55 | Payload count (earlier) | TR: "altı görev yükünden üçünün yerli" (three of the six payloads are domestic). EN: "three out of six payloads being domestically developed". | count | UZAY-SWG4 (TR + EN) | 10 Jun 2026 | This conflicts with #54 (4 scientific, 2 domestic). **[INFERENCE]** The 6 probably includes 2 imaging payloads. Not confirmed. | confirmed (as stated) | official agency |
| 56 | LNT (Lunar Neutrals Telescope) | Detects "energetic neutral atoms (ENAs) originating from the Moon's surface". Resolution: "unprecedent spatial resolution of 12 km x 12 km". Heritage: "a successful predecessor flown onboard India's lunar mission Chandrayaan-1". Electrical model "delivered to TÜBİTAK UZAY in 2024". Flight model delivered "In June" 2026. PI: Dr Manabu Shimoyama (IRF Kiruna). Agreement signed 5 Jul 2022 (TÜBİTAK UZAY news, 3 Oct 2022). | km | IRF-AYAP1; IRF-Jul26; IRF-Dec25; https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-gorevi-icin-isvec-uzay-fizigi-enstitusu-ile-bilimsel-isbirligi-anlasmasi-imzalandi/ | 2022–2026 | Energy range, mass and power not published. | confirmed | contractor / official |
| 57 | LNR (radiometer) | 2024: "Ay yüzeyindeki ısıl albedo ve sıcaklık modellerine yönelik veri toplamayı amaçlayan … Lunar Narrow Field of View Radiometer (LNR), ROB kıdemli araştırmacıları Dr. Özgür Karatekin ve Dr. Ping Zhu tarafından tanıtıldı" (the LNR, which aims to collect data for thermal-albedo and temperature models of the lunar surface, was presented by ROB senior researchers Dr. Özgür Karatekin and Dr. Ping Zhu; ROB = Royal Observatory of Belgium). 2026: attributed to Shenzhen University (China). | – | UZAY-SWG2; UZAY-TR-14Sep26 | 2024 → 2026 | The change of institution is not explained in any source. | confirmed (both statements) | official agency |
| 58 | Imaging payloads (latest spec) | "0,7 metre çözünürlüklü pankromatik görüntüleme" (0.7 m resolution panchromatic imaging). "60 derece bakış açılı video ve geniş alan RGB görüntüleme" (video with a 60° field of view and wide-area RGB imaging). | m, deg | UZAY-PROG | 2026 | Altitude basis (presumably 100 km), swath, detector, bands and compression are not published. | confirmed (spec) | official agency |
| 59 | Imaging (2022–23 design) | "Yüksek Çözünürlüklü Kamera ile 5 km genişlikte bir alandan 1 m'den daha iyi çözünürlükte görüntüler" (images at better than 1 m resolution over a 5 km wide area with the High-Resolution Camera). "Geniş Açılı Video Kamera ile Ay'a transfer, Ay yörüngesi ve yüzeye iniş aşamaları" (the Wide-Angle Video Camera covers the lunar transfer, lunar orbit and surface-descent phases). | m, km | DT-16Dec22; DT-3Oct23 | 2022–23 | Superseded by #58 (0.7 m). | confirmed (historic) | press (quoting TUA) |
| 60 | Wide-angle camera supplier | "Ay Görevi'nin en önemli bileşenlerinden biri olan geniş açılı kamera sistemi" (the wide-angle camera system, one of the most important components of the Moon Mission). Contract with Poloptech signed 22 Oct 2024 at SAHA EXPO (TÜBİTAK President Orhan Aydın; Poloptech CEO Şimşek Tekerek). | – | https://uzay.tubitak.gov.tr/tubitak-uzay-ve-poloptech-arasinda-genis-acili-kamera-sozlesmesi-imzalandi/ | 22 Oct 2024 | Poloptech's country is not stated on the page. | confirmed | official agency |
| 61 | Science objectives | TR: "Güneş rüzgârlarının Ay yüzeyiyle etkileşimi" (interaction of the solar wind with the lunar surface); "Ay yüzeyindeki suyun oluşum mekanizmaları" (formation mechanisms of water on the lunar surface); "Ay'ın manyetik alanları" (the Moon's magnetic fields); "yüzeyin ısıl özellikleri" (thermal properties of the surface); radiation environment. Named "'Ali Kuşçu Keşif ve Haritalama Hedefleri'" (Ali Kuşçu Exploration and Mapping Objectives). "yüksek çözünürlüklü bir Ay su döngüsü gözlemevi" (a high-resolution lunar water-cycle observatory). | – | TUA-16Sep26; UZAY-SWG4; UZAY-PROG | 2025–26 | – | confirmed | official agency |
| **Ground segment, outreach, international** |||||||||
| 62 | Ground stations, deep-space antenna, DSN/ESTRACK | Not published. The only related item is TÜBİTAK UZAY's DUYARGA project, presented at the Tiandu Forum (Hefei, 4–5 Sep 2025): "Derin Uzay Görevleri için Yazılım, Donanım Geliştirme ve Araştırma Projesi" (Software and Hardware Development and Research Project for Deep-Space Missions). | – | https://uzay.tubitak.gov.tr/tiandu-forumu-2025te-turkiyenin-ay-gorevi-ve-uzay-calismalarina-yonelik-uluslararasi-is-birligi-firsatlari-degerlendirildi/ | 13 Sep 2025 | DUYARGA's link to the AYAP-1 ground segment is not stated. | unknown | official agency |
| 63 | Public outreach / livestream | No livestream plan found. Outreach items: the spacecraft was first shown at IAC 2023 Baku ("ilk kez sergileniyor", exhibited for the first time); public unveiling on 14 Sep 2026; Ali Kuşçu objectives naming. | – | DT-3Oct23; UZAY-EN-14Sep26 | – | – | unknown (livestream) | – |
| 64 | International context | Türkiye signed the Artemis Accords on 31 Aug 2026 as the 71st signatory. TUA: "AYAP-1 ile Türkiye, kendi imkânlarıyla Ay'a uzay aracı geliştiren ve gönderen ülkeler arasına katılmayı hedefliyor" (with AYAP-1, Türkiye aims to join the countries that develop and send spacecraft to the Moon with their own means). Kacır: "Bugüne kadar yalnızca 8 ülke Ay görevi gerçekleştirdi" (so far only 8 countries have carried out a Moon mission). | – | https://tua.gov.tr/tr/haberler/turkiye-artemis-mutabakati-ni-imzaladi ; TUBITAK-15Sep26 | Sep 2026 | TUA gives the signing date as "31 Ağustos 2026". Türkiye Today (5 Oct 2026) says 1 Sep 2026, possibly a time-zone or reporting difference. | confirmed | official agency |
| 65 | Latest leadership statement | TUA President Yusuf Kıraç at IAC 2026 (Antalya): "Önümüzdeki yıl aya erişen, kendi imkanlarıyla ulaşan ilk Müslüman ülke olacağız." (Next year we will be the first Muslim country to reach the Moon with its own means.) | – | https://www.trthaber.com/haber/bilim-teknoloji/turkiyenin-ay-hedefinde-geri-sayim-959151.html | 5 Oct 2026 | – | targeted | press (state broadcaster) |

---

## (b) Timeline of launch-date targets and mission-duration descriptions

| Statement date | Source (type) | Launch / arrival target as stated | Mission duration / EOM as stated | Notes |
|---|---|---|---|---|
| 9–10 Feb 2021 | NSP launch by President Erdoğan; TÜBİTAK UZAY news https://uzay.tubitak.gov.tr/milli-uzay-programi-cumhurbaskani-erdogan-tarafindan-tanitildi/ (official) | "Cumhuriyet'in 100'ncü yılında … Ay'a sert iniş gerçekleştirilecek" (a hard landing on the Moon in the Republic's 100th year), i.e. 2023. Phase 2: "ilk fırlatma bu kez milli roketle yapılacak ve Ay'a yumuşak iniş gerçekleştirilecek" (this time the launch will be on a national rocket and a soft landing will be made). | Hard landing | This is the original "2023 hard landing" goal. |
| 2 Feb 2022 | DefenceTurk https://www.defenceturk.net/turkiyenin-ay-misyonunda-kullanacagi-aracin-tasarimi-basladi (press) | "Bu yıl uzay aracında kullanılacak yerli itki sisteminin tasarımı tamamlanarak entegrasyon süreci başlatılacak" (this year the design of the domestic propulsion system will be completed and integration will begin) | – | – |
| 9 Feb 2022 | DefenceTurk, quoting TUA President S. H. Yıldırım https://www.defenceturk.net/turkiye-nin-aya-gidecek-uzay-araci-imalat-safhasinda (press) | "2 sene içinde Ay'a götürecek olan insansız araç imalat safhasında" (the uncrewed vehicle that will take us to the Moon within 2 years is in the manufacturing phase), i.e. about early 2024 | – | – |
| 23–24 May 2022 | NSP-DOC (official) | "İlk aşamanın … 2023 yılı sonuna kadar gerçekleştirilmesi hedeflenmiştir" (the first phase is targeted for completion by the end of 2023). AYAP-2: "2028 yılında Ay'a ulaşması hedeflenmektedir" (targeted to reach the Moon in 2028). | AYAP-1 hard landing | – |
| 3–6 Oct 2023 | IAC 2023 Baku; DT https://www.defenceturk.net/ayap-1-icin-yeni-tarih-2026 (press) | TUA President: "Ay Araştırmaları Programı'nda 2026'yı hedeflediklerini ifade etti" (he said they are targeting 2026 in the Lunar Research Program) | – | **First public slip: 2023 → 2026.** No official reason given. DefenceTurk commented: "gecikme sebeplerinin kamu oyuyla paylaşılmaması olağan değildir" (it is not normal that the reasons for the delay were not shared with the public). That is press commentary. |
| 8 Nov 2023 | AA https://www.aa.com.tr/en/turkiye/turkiyes-1st-spacecraft-to-travel-to-moon-in-2026/3047053 (press, state agency; info from Ministry/TUA/TÜBİTAK) | "All processes are planned to be completed in 2026, and the vehicle will be launched the same year." | Phase 1: "make first contact with the lunar surface" | Detailed design ongoing. QM production started. |
| 6 Feb 2024 / 24 Apr 2024 | DefenceTurk (press) | Launch 2026 | – | – |
| 9 Feb 2025 | caliber.az https://caliber.az/en/post/turkiye-to-send-two-space-missions-to-the-moon (press, citing TUA) | "The goal is to achieve a hard landing on the Moon in 2026." | Hard landing | "the critical design phase is ongoing" |
| 2025 | GLEX25 (conference abstract) | No date | "mission duration in orbit is expected to be several months"; impact with guided deceleration attempt | – |
| 6 Jun 2025 | DT https://www.defenceturk.net/hibrit-itkili-roket-ile-irtifa-rekoru (press) | "AYAP-1'in 2026 yılında tamamlanması planlanmaktadır" (AYAP-1 is planned to be completed in 2026) | – | Last 2026 reference found. |
| 2 Dec 2025 | IRF-Dec25 (contractor) | "Launch planned for early 2027" | "operate for about three months — with a possible extension to six months"; "concluding its mission with a controlled landing" | **First appearance of 2027 (slip 2026 → 2027).** No reason given in any source. |
| undated (cited 31 Mar 2026) | IRF-AYAP1 (contractor) | "in 2027" | "orbit the Moon at an altitude of 100 kilometers for about three months"; "controlled hard landing" | – |
| 10 Jun 2026 | UZAY-SWG4 (official) | "Uzay aracının 2027 yılı içinde Ay yolculuğuna başlayacağını" (that the spacecraft will start its journey to the Moon within 2027) | – | – |
| 28–30 Jul 2026 | IRF-Jul26 (contractor); DT https://www.defenceturk.net/turkiyenin-ay-programi-icin-gelistirilen-sistem-tubitak-uzayda (press) | "scheduled for launch in 2027" | DT: "3 ay, gerekli görülmesi halinde ise 6 aya kadar görev yapması planlanıyor" (planned to operate 3 months, or up to 6 months if deemed necessary); "kontrollü iniş" (controlled landing) | DT repeats the IRF figures. |
| 14 Sep 2026 | UZAY-TR/EN-14Sep26 (official) | "first half of 2027"; shipped to Cape Canaveral | "minimum of three months … could be extended up to 1.5 years"; "controlled deorbit maneuvers" | – |
| 2026 (current page) | UZAY-PROG (official) | "2027 Q2" | "up to 1.5 years"; "hard landing on the surface at the end of the mission" | – |
| 15–16 Sep 2026 | TUBITAK-15Sep26 (Kacır); TUA-16Sep26 (official) | "2027'nin ilk aylarında" (in the first months of 2027); KSC | "en az 3 ay … 1,5 yıla kadar" (at least 3 months … up to 1.5 years); "kontrollü manevralar" (controlled manoeuvres) | – |
| 2 Oct 2026 | AA (press, state agency) | "first months of 2027"; KSC | "at least three months"; "controlled descent" | – |
| 5 Oct 2026 | TRT Haber (Kıraç at IAC 2026); Türkiye Today https://www.turkiyetoday.com/lifestyle/nasa-deputy-chief-says-turkiye-could-help-build-future-moon-base-3229685 (press) | "Önümüzdeki yıl" (next year); "early 2027" (Kacır, press paraphrase) | – | – |

**Reconciling the launch date.** Sources from Sept–Oct 2026 agree that launch is in H1 2027. "First months of 2027" (Kacır, TUA, AA) and "early 2027" (IRF) read as Q1 or early Q2. "First half of 2027" (TÜBİTAK UZAY, TÜBİTAK) covers both. The program page's spec table says "2027 Q2". That is the most specific institutional value and the least optimistic one. **Working baseline: launch NET Q1 2027, institutional target Q2 2027 (H1 2027).** Arrival in lunar orbit is about 2 months after launch.

**[INFERENCE]** On that basis, lunar orbit insertion would fall around Q2–Q3 2027. That date is not stated by any source.

The program's slips are:
- 2023, the original policy goal: Feb 2021, May 2022.
- About 2024: TUA President, Feb 2022.
- 2026: announced Oct 2023, repeated through Jun 2025.
- 2027: from Dec 2025.

No official reason has been published for either slip.

**Reconciling mission duration.**
- Nominal duration: about 3 months in every source from Dec 2025 on. GLEX 2025 said "several months".
- Extension ceiling: IRF and IRF-derived press (Dec 2025, Jul 2026) say up to 6 months. Official Turkish statements from Sept 2026 and the current program page say up to 1.5 years, "depending on mission performance".
- **Baseline:** at least 3 months, a 6-month extension commonly cited by the payload provider, and up to 18 months as the latest official ceiling. The 18-month figure is the more recent and is official, but it is explicitly performance-dependent.

**Reconciling end-of-mission wording.**
- 2021–2025 sources say "sert iniş" (hard landing).
- GLEX 2025 describes a deorbit, an impact on a target area, and an attempted guided deceleration before impact.
- IRF says "controlled (hard) landing".
- The Sept 2026 releases say "kontrollü (yavaşlatma) manevralarla Ay yüzeyine ulaştırılması" (brought to the lunar surface with controlled (deceleration) manoeuvres) and "controlled deorbit maneuvers".
- The program page (2026) still says "sert iniş".

These are consistent with one plan: a controlled deorbit ending in a hard landing (impact), with a guided-deceleration attempt that gives operational experience for AYAP-2. No source claims that AYAP-1 is designed to survive landing.

---

## (c) AYAP-1 vs AYAP-2 separation

| Attribute | AYAP-1 (TLM-1) | AYAP-2 (TLM-2) | Sources |
|---|---|---|---|
| Phase | First phase of the Lunar Research Program | Second phase | NSP-DOC; GLEX25 |
| Objective | Lunar-orbit science and exploration, then a hard landing at EOM. Program page: "Kendi ürettiğimiz uzay aracı ile Ay yörüngesinde keşif faaliyetleri icra edecek … Görev sonunda yüzeye sert iniş gerçekleştireceğiz" (we will carry out exploration in lunar orbit with a spacecraft we built ourselves … at the end of the mission we will make a hard landing on the surface) | Soft landing and rover science. Program page: "yumuşak iniş teknolojimizi doğrulayacak … Gezici keşif aracımız vasıtasıyla Ay yüzeyinde kapsamlı bilimsel araştırmalara imza atacağız" (we will validate our soft-landing technology … and carry out comprehensive science on the lunar surface with our rover) | UZAY-PROG |
| Landing | Hard landing (controlled deorbit to impact, guided-deceleration attempt) | "Ay yüzeyine yumuşak iniş gerçekleştirecektir" (it will make a soft landing on the lunar surface) | NSP-DOC; GLEX25 |
| Rover | None | Yes: "Ay yüzeyine milli teknolojilerle bir gezenaraç (rover) göndererek" (by sending a rover to the lunar surface with national technologies). Feb 2025: "preliminary studies are being carried out, primarily by student teams, for a rover mission" | NSP-DOC; caliber.az |
| Launch vehicle | Non-Turkish launcher via "uluslararası iş birliği" (international cooperation; NSP-DOC). US launch site (KSC / Cape Canaveral; 2026 releases). Rocket and provider not published. | National: "milli fırlatma aracımızla uzaya çıkacak ve yerli motorlarımızla Ay'a ulaşacak" (it will go to space on our national launch vehicle and reach the Moon with our domestic engines). The vehicle is not named. | NSP-DOC; TUA-16Sep26 |
| Propulsion | DeltaV HİS hybrid, plus a bipropellant chemical system | "yerli motorlar" (domestic engines). No details. | NSP-DOC; DT-16Dec22 |
| Timeline | 2023 (2021 goal) → about 2024 (Feb 2022) → 2026 (Oct 2023) → H1 2027 (current) | 2028 (NSP-DOC 2022). Feb 2025: no specific date. Wikipedia "Early 2030s" cites axar.az, which returned 410 and could not be verified. | NSP-DOC; caliber.az; en.wikipedia (cached) |
| Status (Oct 2026) | Integrated (14 Sep 2026). In environmental testing at USET. | Concept / preliminary studies. 2023 concept-design work on "landing gear" and "image-assisted navigation" (AA 8 Nov 2023). | UZAY-EN-14Sep26; AA |
| Link between the two | The AYAP-1 guided deceleration is "to gain operational experience for the AYAP-2 soft landing mission" | Builds on AYAP-1 experience | GLEX25; UZAY-PROG |

---

## (d) Parameters that remain unpublished (as of 5 Oct 2026)

**Launch and injection**
- Launch vehicle and provider, contract date and value, and whether the launch is dedicated or a rideshare.
- Exact launch date and window, and launch pad.
- Injection orbit parameters (perigee, apogee, inclination, argument of perigee) for the "supersynchronous GTO".
- Separation mass, and COSPAR/NORAD IDs (none issued before launch).

**Mass and propulsion**
- Dry mass, total propellant load, and the split between the hybrid and bipropellant systems.
- Terminal (EOM) mass and remaining propellant.
- HİS thrust, Isp, propellant combination, O/F, total impulse, burn count, restart capability and throttling.
- Bipropellant thruster set and propellants.
- Δv budget: orbit raising, TLI, LOI, station-keeping, deorbit.

**Trajectory and operations**
- Burn sequence and timeline: number and epochs of orbit-raising burns, the TLI/LTO injection burn, LOI burn(s) and circularisation.
- Transfer type (direct vs phasing vs low-energy). Only "~2 months" is given.
- Lunar-orbit plane: exact inclination, RAAN/LTAN, period, eclipse seasons, and frozen-orbit or station-keeping strategy.
- Spacecraft state vectors, ephemerides and covariance (none published, for any phase).

**End of mission**
- Impact target region and coordinates, impact epoch, and impact velocity vector (magnitude, flight-path angle, azimuth).
- Attitude at impact.
- Guided-deceleration Δv and its expected residual velocity.

**Payload and communications data**
- Camera details: detector, focal length, IFOV and swath at 100 km for the 0.7 m camera, spectral bands, frame rate, compression and onboard storage.
- LNT energy range, mass and power. LNR wavelength bands. Dosimeter and calorimeter specifications.
- Downlink: X-band and S-band data rates, EIRP and G/T.
- Ground stations, and any agreements with DSN, ESTRACK or commercial networks.
- Ranging and orbit-determination approach (only Thales' general TT&C ranging statement exists).
- Data release policy (only "verileri ortak kullanılacak şekilde", i.e. data to be shared, for the international payloads).

**Program and outreach**
- Budget.
- Public outreach or livestream plans.

---

## (e) URL log (all accessed 2026-10-05)

Result codes:
- **F:** fetched (content obtained).
- **F-min:** fetched, but the page was a shell or had no relevant content.
- **X:** failed, with the reason given.
- **RD:** redirect failure.

| # | URL | Result |
|---|---|---|
| 1 | https://tua.gov.tr/tr/haberler/turkiye-nin-ay-yolculugunda-geri-sayim-basladi | F (3 queries) |
| 2 | https://tua.gov.tr/tr/haberler | F (page 1 index) |
| 3 | https://tua.gov.tr/en/news | F-min (2020 items only) |
| 4 | https://tua.gov.tr/tr/haberler/turkiye-artemis-mutabakati-ni-imzaladi | F (2) |
| 5 | https://tua.gov.tr/tr/haberler?page=2 | F-min (same as page 1; pagination not resolvable) |
| 6 | https://tua.gov.tr/tr | F-min (JS shell) |
| 7 | https://tua.gov.tr/tr/haberler/turkiye-nin-ilk-yerli-atomik-saati-uzay-yolculuguna-basladi | F (not lunar; RAFS on Transporter-17) |
| 8 | https://uzay.tubitak.gov.tr/en/space-exploration-lunar-research-program | RD (too many redirects) |
| 9 | https://uzay.tubitak.gov.tr/tr/ | X 404 |
| 10 | https://uzay.tubitak.gov.tr/ | F |
| 11 | http://uzay.tubitak.gov.tr/en/space-exploration-lunar-research-program/ | RD (too many redirects) |
| 12 | https://uzay.tubitak.gov.tr/uzayin-kesfi-ay-arastirma-programi/ | F (3) |
| 13 | https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-uzay-aracinin-entegrasyon-faaliyetleri-tamamlandi/ | F (3) |
| 14 | https://uzay.tubitak.gov.tr/en/integration-activities-of-turkiyes-first-lunar-spacecraft-successfully-concluded | RD (too many redirects) |
| 15 | https://uzay.tubitak.gov.tr/uzayi-kesfedin/ | F |
| 16 | https://uzay.tubitak.gov.tr/ayap-1/ | X 404 |
| 17 | https://uzay.tubitak.gov.tr/gundem/haberler | F |
| 18 | https://uzay.tubitak.gov.tr/turkiyenin-ay-gorevi-4-ay-bilimsel-calisma-grubu-toplantisi/ | F (2) |
| 19 | https://uzay.tubitak.gov.tr/gundem/haberler/page/2/ | F |
| 20 | https://uzay.tubitak.gov.tr/en/explore-uzay/ | F-min |
| 21 | https://uzay.tubitak.gov.tr/uzayin-kesfi/ | F |
| 22 | https://uzay.tubitak.gov.tr/wp-content/uploads/sites/132/2026/06/TUBITAK-UZAY_catalog.pdf | X 413 (response >30 MB) |
| 23 | https://uzay.tubitak.gov.tr/uydu-platformlari/ | F (no TstarD-100 listed) |
| 24 | https://www.irf.se/en/aktuellt/2026/07-28-svenskt-maninstrument-fran-kiruna-levereras-till-turkiet/ | F (4) |
| 25 | https://iafastro.directory/iac/paper/id/93595/abstract-pdf/GLEX-2025,2,2,1,x93595.brief.pdf | F (3) |
| 26 | https://www.deltav.com.tr/ | X (robots.txt ConnectTimeout) |
| 27 | https://www.deltav.com.tr/en/ | X (robots.txt ConnectTimeout) |
| 28 | https://deltav.com.tr/ | X (robots.txt ConnectTimeout) |
| 29 | https://en.wikipedia.org/wiki/Turkish_Space_Agency | F (3; cached copy) |
| 30 | https://en.wikipedia.org/wiki/Turkish_lunar_mission | X (cache-only domain; not cached) |
| 31 | https://www.irf.se/en/aktuellt/2025/12-02-irf-instrument-for-turkisk-manmission-narmar-sig-leverans-efter-lyckat-test/ | F (3) |
| 32 | https://www.axar.az/news/world/944014.html | X 410 Gone |
| 33 | https://tr.wikipedia.org/wiki/Ay_Araştırma_Programı | X (cache-only) |
| 34 | https://space.skyrocket.de/doc_sdat/ayap-1.htm | X 404 |
| 35 | https://space.skyrocket.de/doc_sdat/tlm-1.htm | X 404 |
| 36 | https://space.skyrocket.de/directories/sat_c_turkey.htm | F-min (JS-dependent) |
| 37 | https://www.eoportal.org/satellite-missions/ayap-1 | F-min (shell; no mission content) |
| 38 | https://space.skyrocket.de/directories/sat_sci-tech_turk.htm | F-min (no lunar entry) |
| 39 | https://www.aa.com.tr/tr/bilim-teknoloji | F-min |
| 40 | https://www.dailysabah.com/search?query=lunar%20spacecraft | X (robots disallowed) |
| 41 | https://www.hurriyetdailynews.com/search/moon%20mission | X (read timeout) |
| 42 | https://www.dailysabah.com/business/defense | X 404 |
| 43 | https://www.trthaber.com/etiket/ay-gorevi/ | X 404 |
| 44 | https://iafastro.directory/iac/paper/id/93595/summary/ | X 401 |
| 45 | https://www.sanayi.gov.tr/medya/haberler | X (WAF "requested URL was rejected") |
| 46 | https://tua.gov.tr/tr/haberler?sayfa=3 | F-min (same as page 1) |
| 47 | https://tua.gov.tr/en | F-min |
| 48 | https://spacenews.com/?s=turkey+lunar | X (robots disallowed) |
| 49 | https://nextspaceflight.com/launches/ | F-min (no AYAP) |
| 50 | https://nextspaceflight.com/launches/?search=AYAP | F-min (search ignored) |
| 51 | https://www.nasaspaceflight.com/?s=turkey+moon | F-min (no results) |
| 52 | https://uzay.tubitak.gov.tr/gundem/haberler/page/3/ | F |
| 53 | https://uzay.tubitak.gov.tr/gundem/haberler/page/4/ | F |
| 54 | https://uzay.tubitak.gov.tr/tubitak-uzay-ve-poloptech-arasinda-genis-acili-kamera-sozlesmesi-imzalandi/ | F (2) |
| 55 | https://uzay.tubitak.gov.tr/ay-bilimsel-calisma-grubu-3-toplantisi-gerceklestirildi/ | F |
| 56 | https://uzay.tubitak.gov.tr/tiandu-forumu-2025te-turkiyenin-ay-gorevi-ve-uzay-calismalarina-yonelik-uluslararasi-is-birligi-firsatlari-degerlendirildi/ | F (2) |
| 57 | https://uzay.tubitak.gov.tr/gundem/haberler/page/5/ | F (2) |
| 58 | https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-gorevi-ayap-1-kapsaminda-30-ve-31-ocak-2024-tarihlerinde-2-bilimsel-calisma-grubu-toplantisi-turk-hava-kurumu-universitesinin-ev-sahipliginde-gerceklesti/ | F (2) |
| 59 | https://uzay.tubitak.gov.tr/gundem/haberler/page/6/ | F |
| 60 | https://uzay.tubitak.gov.tr/turkiyenin-ilk-ay-gorevi-icin-isvec-uzay-fizigi-enstitusu-ile-bilimsel-isbirligi-anlasmasi-imzalandi/ | F |
| 61 | https://uzay.tubitak.gov.tr/gundem/haberler/page/7/ | F |
| 62 | https://uzay.tubitak.gov.tr/milli-uzay-programi-cumhurbaskani-erdogan-tarafindan-tanitildi/ | F |
| 63 | http://www.deltav.com.tr/ | X (robots.txt ConnectTimeout) |
| 64 | https://www.ssb.gov.tr/ | F-min |
| 65 | https://en.wikipedia.org/wiki/Delta_V_Space_Technologies | X (cache-only) |
| 66 | https://en.wikipedia.org/wiki/Turkish_Space_Agency#Lunar_program | F (cached) |
| 67 | https://www.savunmasanayist.com/etiket/ay-gorevi/ | F |
| 68 | https://www.defenceturk.net/etiket/ay-gorevi | F |
| 69 | https://www.savunmasanayist.com/ay-gorevinde-kullanilacak-milli-hibrit-itki-sisteminin-goruntuleri-paylasildi/ | F (2) |
| 70 | https://www.defenceturk.net/ay-gorevi-icin-gelistirilen-ayap-1-uzay-araci-hakkinda-ilk-detaylar | F (3) |
| 71 | https://www.defenceturk.net/ay-uzay-aracinda-test-donemi | F (2) |
| 72 | https://www.defenceturk.net/turkiye-uzay-ajansi-ay-gorevi-hakkinda-yeni-gelismeleri-paylasti | F |
| 73 | https://www.defenceturk.net/turkiye-nin-aya-gidecek-uzay-araci-imalat-safhasinda | F |
| 74 | https://www.defenceturk.net/etiket/deltav | F |
| 75 | https://www.savunmasanayist.com/etiket/deltav/ | F |
| 76 | https://www.defenceturk.net/deltav-uzaydan-cumhuriyetin-yuzuncu-yilinda-bir-ilk | X ×2 (read timeout), then F (2) |
| 77 | https://www.defenceturk.net/hibrit-itkili-roket-ile-irtifa-rekoru | F (2) |
| 78 | https://www.savunmasanayist.com/etiket/ayap-1/ | X 404 |
| 79 | https://www.defenceturk.net/etiket/ayap-1 | F |
| 80 | https://www.defenceturk.net/ayap-1-icin-yeni-tarih-2026 | F (2) |
| 81 | https://www.defenceturk.net/ayap-1-uzay-araci-iac-2023te-sergileniyor | F (2) |
| 82 | https://www.defenceturk.net/ay-gorevinde-kullanilacak-hibrit-roket-motorunun-uzay-testleri-yapildi | F |
| 83 | https://www.defenceturk.net/delta-vden-uzay-ucus-testi | F (2) |
| 84 | https://www.defenceturk.net/turkiyenin-aya-yolculuk-icin-calismalari-devam-ediyor | F |
| 85 | https://www.defenceturk.net/turkiyenin-ay-programi-icin-gelistirilen-sistem-tubitak-uzayda | F (2) |
| 86 | https://www.defenceturk.net/etiket/ay-arastirma-programi | F |
| 87 | https://www.defenceturk.net/etiket/ay-uzay-araci | F |
| 88 | https://www.defenceturk.net/etiket/tubitak-uzay | F |
| 89 | https://iafastro.directory/iac/archive/browse/GLEX-2025/2/2/ | X 404 |
| 90 | https://www.defenceturk.net/turkiyenin-ay-misyonunda-kullanacagi-aracin-tasarimi-basladi | F |
| 91 | https://www.dailysabah.com/life/science | X 404 |
| 92 | https://www.turkiyetoday.com/search?q=lunar | F |
| 93 | https://www.turkiyetoday.com/lifestyle/nasa-deputy-chief-says-turkiye-could-help-build-future-moon-base-3229685 | F |
| 94 | https://www.turkiyetoday.com/search?q=moon%20spacecraft | F-min |
| 95 | https://www.aa.com.tr/en/science-technology | F |
| 96 | https://www.trthaber.com/haber/bilim-teknoloji/ | F |
| 97 | https://www.aa.com.tr/en/turkiye/from-ottoman-rocket-man-to-lunar-mission-how-did-turkiye-s-long-road-into-space-begin/4076132 | X once (fetch error), then F (3) |
| 98 | https://www.trthaber.com/haber/bilim-teknoloji/turkiyenin-ay-hedefinde-geri-sayim-959151.html | F |
| 99 | https://www.trthaber.com/etiket/ay-uzay-araci/ | X 404 |
| 100 | https://space.skyrocket.de/doc_chr/lau2027.htm | X 404 |
| 101 | https://space.skyrocket.de/doc_chr/lau2026.htm | F-min (no entry; partial page) |
| 102 | https://tua.gov.tr/tr/milli-uzay-programi | F (2) |
| 103 | https://www.tccb.gov.tr/haberler/410/123176/-cumhuriyetimizin-100-yilinda-ay-a-ilk-temasi-gerceklestirecegiz- | X (robots.txt fetch: server disconnected) |
| 104 | https://cdn.tua.gov.tr/63da672cab079.pdf | F (3) |
| 105 | https://tubitak.gov.tr/tr/haberler | F |
| 106 | https://www.defenceturk.net/etiket/delta-v | F |
| 107 | https://www.defenceturk.net/baykar-uzay-sektorune-giris-yapacak | F (content mainly Baykar) |
| 108 | https://www.defenceturk.net/delta-v-103-km-irtifaya-ulasti | F |
| 109 | https://www.defenceturk.net/etiket/hibrit-itki-sistemi | F |
| 110 | https://www.defenceturk.net/etiket/ay-gorevi?page=2 | F-min (same list) |
| 111 | https://uzay.tubitak.gov.tr/turkiye-uzay-vizyonunu-iac-2025te-dunyaya-anlatti/ | F |
| 112 | https://uzay.tubitak.gov.tr/tua-arastirmacilarina-yonelik-uzay-araci-sistem-muhendisligi-ve-yasam-dongusu-egitimi-tamamlandi/ | F |
| 113 | https://iafastro.directory/iac/archive/browse/IAC-25/A3/ | X 404 |
| 114 | https://iafastro.directory/iac/proceedings/GLEX-2025/ | X (robots disallowed) |
| 115 | https://www.hurriyet.com.tr/haberleri/ay-gorevi | F-min (no AYAP items) |
| 116 | https://www.ntv.com.tr/ay-gorevi | X 404 |
| 117 | https://tubitak.gov.tr/tr/haber/turkiyenin-ilk-ay-uzay-aracinin-entegrasyon-faaliyetleri-tamamlandi | F (4) |
| 118 | https://tubitak.gov.tr/en/news | F-min |
| 119 | https://www.trthaber.com/etiket/ay-arastirma-programi/ | X 404 |
| 120 | https://www.trthaber.com/etiket/tubitak-uzay/ | X 404 |
| 121 | https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches | F (cached; no entry) |
| 122 | https://en.wikipedia.org/wiki/List_of_missions_to_the_Moon | F (cached) |
| 123 | https://axar.az/en/news/world/944014.html | X 404 |
| 124 | https://www.irf.se/en/ | F-min |
| 125 | https://www.irf.se/en/aktuellt/ | F-min |
| 126 | https://www.irf.se/aktuellt/2026/07-28-svenskt-maninstrument-fran-kiruna-levereras-till-turkiet/ | RD (too many redirects) |
| 127 | https://tua.gov.tr/tr/ay-arastirma-programi | F-min (site 404 page) |
| 128 | https://tua.gov.tr/tr/milli-uzay-programi/uzay-calismalarimiz | F-min (videos only) |
| 129 | https://tua.gov.tr/tr/milli-uzay-programi/milli-uzay-programi-hakkinda | F-min |
| 130 | https://api.semanticscholar.org/graph/v1/paper/search?query=Turkish+lunar+mission&… | X 429 |
| 131 | https://api.crossref.org/works?query=Turkish+lunar+mission+hybrid&… | X 429 |
| 132 | https://api.openalex.org/works?search=Turkish%20lunar%20mission&… | X 429 |
| 133 | https://api.openalex.org/works?search=hybrid%20rocket%20lunar%20Karabeyoglu&… | X 429 |
| 134 | https://www.savunmasanayist.com/etiket/ay-arastirma-programi/ | X 404 |
| 135 | https://www.savunmasanayist.com/etiket/tubitak-uzay/ | X 404 |
| 136 | https://www.savunmasanayist.com/etiket/ay-gorevi/page/2/ | X 404 |
| 137 | https://www.savunmasanayist.com/?s=ay+uzay+arac%C4%B1 | F-min |
| 138 | https://www.iac2026.org/ | F-min |
| 139 | https://www.defenceturk.net/etiket/spacex | F-min (no lunar items) |
| 140 | https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=AYAP | F (0 results) |
| 141 | https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=Turkish | F (0 results) |
| 142 | https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=Turkey | F (0 results) |
| 143 | https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=lunar&limit=50 | F (no Turkish mission) |
| 144 | https://www.tusas.com/haberler | F-min (site 404 page) |
| 145 | https://www.tusas.com/en/news | F-min (site 404 page) |
| 146 | https://www.tusas.com/medya-merkezi/haberler | F-min (landing page) |
| 147 | https://uzay.tubitak.gov.tr/gundem/haberler/page/8/ | F |
| 148 | https://uzay.tubitak.gov.tr/gundem/haberler/ | F |
| 149 | https://www.sbb.gov.tr/yillik-programlar/ | F |
| 150 | https://www.sbb.gov.tr/wp-content/uploads/2025/10/2026-Yili-Cumhurbaskanligi-Yillik-Programi.pdf | F (helper found no lunar mention; may be truncated) |
| 151 | https://www.dailysabah.com/sitemap/news.xml | X 404 |
| 152 | https://www.aa.com.tr/en/science-technology/turkiye-s-prime-aerospace-tech-event-teknofest-southeast-kicks-off/4073504 | F-min |
| 153 | https://www.hurriyetdailynews.com/ | F-min |
| 154 | https://www.dailysabah.com/sitemap.xml | X 404 |
| 155 | https://uzay.tubitak.gov.tr/en/ | F |
| 156 | https://uzay.tubitak.gov.tr/en/space-exploration-lunar-research-program/?lang=en | F (2); the `?lang=en` variant avoids the redirect loop |
| 157 | https://uzay.tubitak.gov.tr/en/integration-activities-of-turkiyes-first-lunar-spacecraft-successfully-concluded/?lang=en | F (3) |
| 158 | https://uzay.tubitak.gov.tr/en/news/?lang=en | X 404 |
| 159 | https://uzay.tubitak.gov.tr/en/agenda/news/?lang=en | F |
| 160 | https://uzay.tubitak.gov.tr/en/?lang=en | X (read timeout) |
| 161 | https://uzay.tubitak.gov.tr/en/turkish-lunar-mission-the-4th-meeting-of-the-lunar-scientific-working-group/?lang=en | F |
| 162 | https://uzay.tubitak.gov.tr/en/agenda/news/page/2/?lang=en | F |
| 163 | https://spaceflightnow.com/launch-schedule/ | F-min (no entry) |
| 164 | https://www.rocketlaunch.live/?filter=turkey | X 404 |
| 165 | https://www.cnnturk.com/etiket/ay-gorevi | X 404 |
| 166 | https://www.haberturk.com/etiket/ay-gorevi | X (robots disallowed) |
| 167 | https://en.wikipedia.org/wiki/2027_in_spaceflight | F (cached; no AYAP entry) |
| 168 | https://en.wikipedia.org/wiki/AYAP-1 | F (3; cached) |
| 169 | https://www.thalesgroup.com/en/news-centre/press-releases/thales-alenia-space-provide-communication-transponder-turkeys-first | X (Incapsula WAF) |
| 170 | https://www.aa.com.tr/en/turkiye/turkiyes-1st-spacecraft-to-travel-to-moon-in-2026/3047053 | F (2) |
| 171 | https://tua.gov.tr/en/project/ayap-1-3 | F-min |
| 172 | https://www.irf.se/en/i-rymden/ayap-1/ | F (2) |
| 173 | https://caliber.az/en/post/turkiye-to-send-two-space-missions-to-the-moon | F (2) |
| 174 | https://dunyanews.tv/en/Technology/769117 | F-min (served homepage content; no article) |
| 175 | https://www.asdnews.com/news/aerospace/2023/11/22/thales-alenia-space-provide-communication-transponder-turkeys-1st-lunar-mission | F (2) |
| 176 | https://damise.com/en/news/-turkeys-moon-mission-with-the-2026-goal-ayap-1-and-ayap-2-projects | F-min (metadata only) |
| 177 | https://www.thalesaleniaspace.com/en/press-releases/thales-alenia-space-provide-communication-transponder-turkeys-first-lunar-mission | F |
| 178 | https://uzay.tubitak.gov.tr/duyarga/ | X 404 |
| 179 | https://www.defenceturk.net/deltav-uzay-kamyonu-space-tug-ile-uzayda-uydu-nakledecek | F |
| 180 | https://www.savunmasanayist.com/milli-hibrit-uzay-roket-motoru-test-atisina-hazirlaniyor/ | F |
| 181 | https://tr.wikipedia.org/wiki/Delta_V_Uzay_Teknolojileri | X (cache-only) |
| 182 | https://en.wikipedia.org/wiki/Delta_V_Space_Technologies_Inc. | X (cache-only) |
| 183 | https://en.wikipedia.org/wiki/AYAP-2 | X (cache-only) |
| 184 | https://en.wikipedia.org/wiki/Turkish_National_Space_Program | X (cache-only) |
| 185 | https://api.crossref.org/works?query.bibliographic=Turkish+lunar+mission&rows=15 | X (proxy 429; the proxy said not to fetch this page again, so it was not retried) |
| 186 | https://www.defenceturkey.com/en/search?q=lunar | X 404 |
| 187 | https://www.iafastro.org/events/global-series-conferences/glex-2025/ | X 404 |
| 188 | https://www.trtworld.com/search?q=lunar%20spacecraft | X (robots disallowed) |
| 189 | https://www.dailysabah.com/business/tech | X 404 |
| 190 | https://www.aa.com.tr/en/search/?s=lunar%20spacecraft | X (robots disallowed) |
| 191 | https://www.aa.com.tr/tr/search/?s=ay%20uzay%20arac%C4%B1 | X (robots disallowed) |
| 192 | https://www.iletisim.gov.tr/turkce/haberler | F-min |
| 193 | https://www.hurriyet.com.tr/haberleri/ay-uzay-araci | X (robots disallowed) |
| 194 | https://www.hurriyet.com.tr/haberleri/ayap-1 | X (robots disallowed) |

**Unreadable sources worth retrying by other means:**
- The Delta V website (HİS specifications, test firings). The connection timed out.
- The TÜBİTAK UZAY catalog PDF (June 2026). It is larger than 30 MB.
- The Thales Group press-release mirror. The thalesaleniaspace.com version was read instead.
- The Presidency (tccb.gov.tr) Feb 2021 speech.
- The axar.az source behind Wikipedia's "AYAP-2 early 2030s" claim. It returned 410.
- Bibliographic APIs (Crossref, OpenAlex, Semantic Scholar). All returned 429.
