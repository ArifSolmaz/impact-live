# Running the Live page on impact day

The Live page (`site/live.html`) is driven by one file: **`site/data/event.json`**. Edit it on GitHub
(open the file, click the pencil icon, edit, "Commit changes"); the Pages workflow republishes the site in about a
minute. Browsers may keep the previous copy for up to ~10 minutes (GitHub Pages caching), and the page itself
re-reads `event.json` every 60 seconds while `status` is `"live"`.

Only publish what the mission team has announced. Do not put a date or target into this file before it is official.

## Fields

| Field | Meaning |
|---|---|
| `status` | `"planning"` (no date yet), `"announced"` (date known), `"live"` (impact day), `"completed"` (after the event) |
| `updated_utc` | when you last edited the file, e.g. `"2028-03-31T09:00:00Z"` |
| `impact_utc` | official predicted impact time in UTC, ISO 8601 ending in `Z` |
| `impact_uncertainty_min` | timing uncertainty in minutes (number) |
| `target` | `{"lat": 8.0, "lon": -22.0, "name": {"tr": "…", "en": "…"}}` — selenographic latitude/longitude (east positive) |
| `mission_status` | short status text shown on the home page, `{"tr": "…", "en": "…"}` |
| `streams` | `[{"name": "TUA canlı yayın", "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX", "lang": "tr"}]` — the first YouTube link is embedded while `status` is `"live"` |
| `watch_events` | `[{"name": {"tr": "…", "en": "…"}, "place": "Ankara", "url": "https://…"}]` |
| `updates` | `[{"time_utc": "2028-04-01T18:05:00Z", "tr": "…", "en": "…"}]` — newest first is not required |
| `results` | after the event: `{"summary": {"tr": "…", "en": "…"}, "links": [{"label": {"tr": "…", "en": "…"}, "url": "https://…"}]}` |

## Example: impact day

```json
{
  "status": "live",
  "updated_utc": "2028-04-01T17:30:00Z",
  "impact_utc": "2028-04-01T18:00:00Z",
  "impact_uncertainty_min": 2,
  "target": {"lat": 8.0, "lon": -22.0, "name": {"tr": "Açıklanan hedef", "en": "Announced target"}},
  "mission_status": {"tr": "Araç son yörüngesinde.", "en": "The spacecraft is on its final trajectory."},
  "streams": [{"name": "Live stream", "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX", "lang": "tr"}],
  "watch_events": [],
  "updates": [{"time_utc": "2028-04-01T17:30:00Z", "tr": "Yayın başladı.", "en": "The live programme has started."}],
  "results": null
}
```

Check the file is valid JSON before committing (for example with `python3 -m json.tool site/data/event.json`).
A broken file stops the Live page from updating. Preview locally with `make serve` and open
http://localhost:8000/live.html. Add `?demo=1` to the URL to preview the page with the hypothetical S1 scenario.
