# AYAP-1 Lunar Impact · impact-live

**Could the end-of-mission impact of Türkiye's first lunar spacecraft be seen from Earth — by whom, from where, and with what?**
This repository holds an open, reproducible analysis of that question and a bilingual (Turkish/English) website
built on its results, including a live page for impact day.

**Website:** published from [`site/`](site/) with GitHub Pages at `https://ArifSolmaz.github.io/impact-live/`.

> **Independent research project.** Not affiliated with or endorsed by TUA or TÜBİTAK UZAY. The impact sites and
> dates used here are **hypothetical test scenarios, not official AYAP-1 targets**. All probabilities assume the
> spacecraft reaches its planned final trajectory. The Live page shows a date only after the mission team publishes one.

## Türkçe özet

Bu depo, Türkiye'nin ilk Ay aracı AYAP-1'in görev sonunda Ay'a çarpmasının Dünya'dan gözlenip gözlenemeyeceğini
inceleyen açık ve tekrarlanabilir bir çalışmayı ve bu çalışmaya dayanan Türkçe/İngilizce bir web sitesini içerir.
Site dört bölümden oluşur: **Keşfet** (11 varsayımsal çarpma senaryosu, Ay'ın Dünya'dan görünüşü, Ay'ı kimlerin
görebileceği ve parlamanın kaydedilme olasılıkları), **Ne görebilirim?** (göz, dürbün, telefon ve teleskopla neyin
mümkün olduğu, bulunduğunuz yerden Ay'ın görünürlüğü ve gözlemci kontrol listesi), **Canlı** (tarih açıklandığında geri
sayım, izleme etkinlikleri ve yayınlar) ve **Bilim ve veri** (yöntem, şekiller, veriler, yeniden üretme).
Başlıca sonuç: parlama büyük olasılıkla çıplak gözle görülemeyecek kadar sönük olacak (orta değer ≈12 kadir);
halka vaat edilmesi gereken şey telemetri, profesyonel teleskopların hızlı tekrarı ve günler ya da aylar sonra krater
görüntüsüdür. Sürüm 2.1, sürüm 1.0.1 ve 2.0'ın iki bağımsız bilimsel incelemesinden sonra düzeltilmiş modellerle
tamamen yeniden hesaplanmıştır ([docs/AUDIT_RESPONSE.md](docs/AUDIT_RESPONSE.md),
[docs/REAUDIT_RESPONSE.md](docs/REAUDIT_RESPONSE.md)).

## What the website shows

| Page | Content |
|---|---|
| Home | The Moon now (or scenario S1), key numbers, what the public can realistically expect |
| Explore | 11 hypothetical scenarios: the Moon as seen from Earth at that moment, where on Earth the Moon is high in a dark sky, observatory availability, detection odds for three observing networks, observing calendar for Türkiye |
| What could I see? | Predicted flash brightness against the limits of eyes, binoculars, phones and telescopes; a flash simulator; "is the Moon up where I am?"; an observer checklist |
| Live | Driven by [`site/data/event.json`](site/data/event.json): countdown, local times, visibility from your location, streams, watch events, updates (see [docs/LIVE_MODE.md](docs/LIVE_MODE.md)) |
| Science & data | Summary, methods, figures, data links, how to reproduce, limitations, citation |

All sky geometry shown for "now" or for a visitor's location is computed in the browser (Astronomy Engine),
cross-checked against the study's JPL DE421 pipeline (lunar sub-points within 0.01°, Moon altitudes within 0.02°).
No location data leave the browser. Scenario values on the site come from release 2.1 of the analysis.

## Quick start

```bash
# view the site locally
make serve                     # then open http://localhost:8000

# reproduce the analysis (Python 3.12–3.14)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all                       # ~3 h on two cores; regenerates outputs/, the site data and the release manifest
make all MC_OUTER=40 MC_INNER=50 NTRIAL=20 NSEQ=500   # quicker, lower-precision run
make site                      # only refresh site/data from existing outputs

# check a reproduction (runs in a clean copy, leaves this folder untouched; one check at a time)
make check-quick               # reduced sample sizes (~1.5 h); prints PASS or FAIL
make check                     # release sample sizes (~3 h); see docs/REPRODUCING.md
make test-checker              # the checker passes the archived outputs and fails eight corruptions (~2 min)
make quotes                    # every reused quotation occurs where research/quotations.csv says it is used
```

`outputs/screening/classes.npz` (78 MB) is not committed; `make dirs screen` regenerates it in a few minutes.
The manuscript is not part of this repository yet, so the `pdf` step is skipped.

### Publishing with GitHub Pages

The workflow in [`.github/workflows/pages.yml`](.github/workflows/pages.yml) publishes `site/` on every push to
`main`. Enable it once under **Settings → Pages → Source: GitHub Actions**, or from a terminal:

```bash
gh api -X POST "repos/{owner}/{repo}/pages" -f build_type=workflow
```

## Repository layout

| Path | Content |
|---|---|
| `site/` | the website (static HTML/CSS/JS, no build step); `site/data/` holds its data files |
| `ayap1obs/` | Python package: ephemeris and lunar orientation, topocentric geometry, surface screening, orbit-plane overflights and opportunity classes, terrain, impact physics, ejecta plume, detectability, weather, settlement populations, Monte Carlo, plotting |
| `scripts/` | pipeline steps (see `Makefile`), `make_site_data.py` (site data), `make_release_manifest.py`, `check_reproduction.py`, `test_checker.py`, `check_quotations.py` |
| `config/` | sites, scenarios, instruments, orbit families, orbiters, timeline, screening domain and criteria |
| `data/` | JPL DE421 arrays, Natural Earth coastlines, processed JPL Horizons validation tables, the typeface used in the figures; `DATA_MANIFEST.sha256` |
| `outputs/` | validation, screening and reachability arrays, scenario cards (JSON), tables (CSV/JSON), figures (PNG/PDF), run logs |
| `research/` | evidence reports with source logs and status labels (mission baseline, impact precedents, facilities, orbiters, sources checked for the corrections, quotation ledger) |
| `docs/` | reproduction guide, response to the scientific audit, public-event sequence, live-mode guide |

## Method in brief

1. **Geometry** – JPL DE421 ephemeris and lunar orientation, validated against JPL Horizons (range to about 1 m,
   lunar sub-points to about 10⁻⁵° in Horizons' convention); impact time at the Moon and reception time at each
   station; the lunar surface screened hourly from May 2027 to March 2029 for 35 candidate observing sites.
2. **Circular-overflight screening opportunities** – for 72 hypothetical directed polar orbit planes (36 planes flown
   in both directions) and 8 orbital phases, every overflight of every point is mapped to the impact time of a 25-m/s
   de-orbit burn and evaluated at that time; the headline statistic is the probability of an opportunity within a
   terminal window, for an unknown plane and phase. Not a mission plan: burn targeting, the cross-track manoeuvre and
   operations are not modelled.
3. **Impact physics** – kinetic energy; a cooling-blackbody flash with an uncalibrated luminous-efficiency prior and a
   laboratory-trend case reported separately; crater rim diameters from published scaling tables, checked out of sample
   against LROC-imaged artificial craters; a phase-space ejecta-plume model within the Housen–Holsapple scaling domain.
4. **Detectability** – exposure-integrated signal-to-noise per camera with Earthshine, scattered light, sky, extinction
   and saturation; a conditional visual-threshold model; phone limits in their broad band; injection–recovery of a
   causal detection pipeline on synthetic video with measured false-alarm rates.
5. **Network Monte Carlo** – 200 epistemic draws × 600 events per scenario with shared impact time and position, correlated
   weather, readiness, calibration, backgrounds and terrain; per-frame noise before the best frame is chosen; three
   network strategies compared on the same events.

Example (scenario S1, dark mare on a Türkiye spring evening, wide brightness prior, conditional on the planned final
trajectory): median peak brightness ≈12 mag; chance of at least one recording 49 % (Türkiye-only network; 5–95 %
epistemic range 42–56 %), 69 % (global network; 62–77 %) and 58 % (public network; 51–65 %); detections at two sites
21 %, 47 % and 39 %; naked-eye and binocular witnessing practically impossible; no detectable ejecta plume with
regolith-like grains, although fine-grained ejecta could make the near-terminator plume detectable (so a plume must not
be promised); a 5–30 m crater for orbiters to image later. These values depend steeply on the unknown luminous
efficiency.

## Reproducibility

`make check` verifies the input data against `data/DATA_MANIFEST.sha256`, re-runs the complete pipeline in a clean copy,
requires every product to be present and compares the result with the archived outputs, printing PASS or FAIL against
stated tolerances; see [docs/REPRODUCING.md](docs/REPRODUCING.md). Fixed seeds, pinned package versions (including the
data-bearing packages), a typeface shipped with the code and the processed Horizons validation tables make the runs
repeatable; `MANIFEST.sha256` and `outputs/validation/release_manifest.json` identify every file, package and external
data set of the release.

* **Same computer:** every output repeats bit for bit, including the Monte Carlo.
* **Different computer:** deterministic products are expected to agree to floating-point rounding and Monte Carlo
  probabilities within their Monte Carlo errors (verified for release 1 on macOS/Apple silicon vs Linux/x86-64,
  [`outputs/validation/cross_platform_run.md`](outputs/validation/cross_platform_run.md)).

Changes between releases are listed in [CHANGELOG.md](CHANGELOG.md); the responses to the independent scientific audits
of release 1.0.1 and release 2.0 are [docs/AUDIT_RESPONSE.md](docs/AUDIT_RESPONSE.md) and
[docs/REAUDIT_RESPONSE.md](docs/REAUDIT_RESPONSE.md).

## Credits and licences

* Code: MIT ([LICENSE](LICENSE)). Results, figures, tables and texts: CC BY 4.0.
* Moon albedo map (`site/assets/img/moon_texture.jpg`): from the open-source *starry* package (MIT, R. Luger et al.),
  derived from NASA lunar imagery. Any equirectangular map with longitude −180…180 (0° at the centre) can replace it,
  e.g. the public-domain NASA SVS "CGI Moon Kit" colour map.
* Lunar feature names and positions: IAU/USGS Gazetteer of Planetary Nomenclature via *pylunar* (BSD-3-Clause).
* Figure typeface: [Inter](https://github.com/rsms/inter) 4.0 (SIL Open Font License, The Inter Project Authors), `data/fonts/`.
* Sky calculations in the browser: [Astronomy Engine](https://github.com/cosinekitty/astronomy) (MIT, D. Cross).
* World map: [Natural Earth](https://www.naturalearthdata.com/) (public domain). Cities: GeoNames via *geonamescache* (CC BY 4.0).
* Ephemeris: JPL DE421 (Folkner et al. 2009) as packaged in the `de421` Python distribution; validation tables from JPL Horizons.

## Citation

See [CITATION.cff](CITATION.cff). The accompanying scientific paper is in preparation; a link will be added when it is published.
