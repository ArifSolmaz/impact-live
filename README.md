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
halka vaat edilmesi gereken şey telemetri, profesyonel teleskopların hızlı tekrarı ve haftalar sonra krater görüntüsüdür.

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
No location data leave the browser.

## Quick start

```bash
# view the site locally
make serve                     # then open http://localhost:8000

# reproduce the analysis (Python 3.12–3.14)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all                       # ~1 h on two cores; regenerates outputs/ and the site data
make all NMC=400 NTRIAL=2      # quicker, lower-precision run (~30 min)
make site                      # only refresh site/data from existing outputs

# check a reproduction (runs in a clean copy, leaves this folder untouched)
make check-quick               # reduced Monte Carlo (30–70 min); prints PASS or FAIL
make check                     # full precision (1–2 h); see docs/REPRODUCING.md
```

`outputs/screening/classes.npz` (67 MB) is not committed; `make dirs screen` regenerates it in a few minutes.
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
| `ayap1obs/` | Python package: ephemeris and lunar orientation, topocentric geometry, surface screening, reachability, terrain, impact physics, detectability, weather, population, Monte Carlo, plotting |
| `scripts/` | pipeline steps (see `Makefile`), `make_site_data.py` (site data), `make_site_moon_assets.py` (Moon texture and feature labels) |
| `config/` | sites, scenarios, instruments, orbit families, orbiters, timeline |
| `data/` | JPL DE421 arrays, Natural Earth coastlines, JPL Horizons validation tables, the typeface used in the figures |
| `outputs/` | validation, screening and reachability maps, scenario cards (JSON), tables (CSV/JSON), figures (PNG/PDF), run logs |
| `research/` | evidence reports with source logs (mission baseline, impact precedents, facilities, orbiters) |
| `docs/` | reproduction guide for reviewers, public-event sequence, live-mode guide |

## Method in brief

1. **Geometry** – JPL DE421 ephemeris and lunar orientation (validated against JPL Horizons to metres in range and
   thousandths of a degree on the lunar sub-points); full lunar surface screened hourly, August 2027 – March 2029,
   for 35 candidate observing sites.
2. **Reachability** – which points a 100-km polar orbit can reach, for an unknown orbit plane, with and without a
   plane-change budget.
3. **Impact physics** – kinetic energy, a cooling-blackbody flash with an uncalibrated luminous-efficiency prior
   (no measurement exists below 2.4 km/s), ejecta-plume and crater scaling checked against LROC-imaged artificial craters.
4. **Detectability** – photon-limited signal-to-noise per instrument with earthshine, scattered light and extinction;
   models of the eye and phones; injection–recovery tests on synthetic video.
5. **Network Monte Carlo** – 6,000 draws per scenario with correlated weather, readiness, field coverage and brightness.

Example (scenario S1, dark mare on a Türkiye spring evening, wide brightness prior): median peak brightness ≈12 mag;
chance of at least one recording 52 % (Türkiye-only network), 75 % (global network), 62 % (public network);
naked-eye and binocular witnessing practically impossible; a 7–15 m crater for orbiters to image later.

## Reproducibility

`make check` re-runs the complete pipeline in a clean copy and compares the result with the archived outputs,
printing PASS or FAIL against stated tolerances; see [docs/REPRODUCING.md](docs/REPRODUCING.md). Fixed seeds
(Monte Carlo and injection-recovery 20261005), pinned package versions (`requirements.txt`), a typeface shipped with
the code for the figures, and verbatim Horizons validation tables make the runs repeatable:

* **Same computer:** every output repeats bit for bit, including the Monte Carlo.
* **Different computer** (macOS on Apple silicon vs Linux on x86-64): deterministic products agree to
  floating-point rounding and Monte Carlo probabilities within sampling error
  ([`outputs/validation/cross_platform_run.md`](outputs/validation/cross_platform_run.md)).
* **From scratch:** a clean-room run starting from an empty `outputs/` folder regenerated every product
  ([`outputs/validation/clean_room_run.md`](outputs/validation/clean_room_run.md)).

Changes between releases are listed in [CHANGELOG.md](CHANGELOG.md).

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
