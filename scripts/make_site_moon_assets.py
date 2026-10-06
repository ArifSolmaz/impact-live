"""One-off generator for the website's Moon assets (outputs are committed; re-run only to rebuild them).

Writes
  site/data/moon_features.json    maria, selected craters and landing sites (names, positions, sizes)
  site/assets/img/moon_texture.jpg  equirectangular grey-scale albedo map (longitude -180..180, centre 0 deg)

Sources
  * Feature table: the `pylunar` package (BSD-3-Clause), positions and sizes from the IAU/USGS Gazetteer of
    Planetary Nomenclature.   pip install pylunar        (or set PYLUNAR_DB=/path/to/lunar.db)
  * Albedo map: starry/img/moon.png from the `starry` package source distribution (MIT License, R. Luger et
    al.), derived from NASA lunar imagery.  Set STARRY_MOON_PNG=/path/to/moon.png (the sdist need not be
    installed).  Any other equirectangular map with the same orientation can be dropped in as
    site/assets/img/moon_texture.jpg instead, e.g. the public-domain NASA SVS "CGI Moon Kit" colour map.
"""
import os, sys, json, sqlite3
from PIL import Image

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{root}/site/data', exist_ok=True); os.makedirs(f'{root}/site/assets/img', exist_ok=True)

# ---------------------------------------------------------------- feature labels
DB = os.environ.get('PYLUNAR_DB', '')
if not DB:
    try:
        import pylunar
        DB = os.path.join(os.path.dirname(pylunar.__file__), 'data', 'lunar.db')
    except ImportError:
        pass
if DB and os.path.exists(DB):
    rows = sqlite3.connect(DB).execute('select Name, Latitude, Longitude, Diameter, Type, Delta_Latitude, Delta_Longitude from Features').fetchall()
    F = [dict(name=r[0], lat=float(r[1]), lon=float(r[2]), diam_km=float(r[3]), type=r[4], dlat=float(r[5]), dlon=float(r[6])) for r in rows]
    maria = [f for f in F if f['type'] in {'Mare', 'Oceanus', 'Lacus', 'Sinus', 'Palus'}]
    FAMOUS = ['Copernicus', 'Tycho', 'Kepler', 'Aristarchus', 'Plato', 'Grimaldi', 'Ptolemaeus', 'Clavius',
              'Theophilus', 'Langrenus', 'Petavius', 'Archimedes', 'Eratosthenes', 'Gassendi', 'Schickard', 'Posidonius']
    out = dict(
        source='pylunar lunar.db (BSD-3-Clause); positions/sizes from the IAU/USGS Gazetteer of Planetary Nomenclature',
        maria=[dict(name=m['name'], lat=round(m['lat'], 2), lon=round(m['lon'], 2), diam_km=round(m['diam_km'])) for m in sorted(maria, key=lambda m: -m['diam_km'])],
        craters=[dict(name=f['name'], lat=round(f['lat'], 2), lon=round(f['lon'], 2), diam_km=round(f['diam_km'])) for f in F if f['type'] == 'Crater' and f['name'] in FAMOUS],
        landing=[dict(name=f['name'], lat=round(f['lat'], 3), lon=round(f['lon'], 3)) for f in F if f['type'] == 'Landing Site'],
    )
    json.dump(out, open(f'{root}/site/data/moon_features.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f"moon_features.json: maria {len(out['maria'])}, craters {len(out['craters'])}, landing sites {len(out['landing'])}")
else:
    print('pylunar lunar.db not found - moon_features.json left unchanged')

# ---------------------------------------------------------------- albedo texture
SRC = os.environ.get('STARRY_MOON_PNG', '')
if not SRC:
    try:
        import starry
        SRC = os.path.join(os.path.dirname(starry.__file__), 'img', 'moon.png')
    except Exception:
        pass
if SRC and os.path.exists(SRC):
    im = Image.open(SRC).convert('L')
    if im.size != (2048, 1024):
        im = im.resize((2048, 1024), Image.LANCZOS)
    im.save(f'{root}/site/assets/img/moon_texture.jpg', quality=82, optimize=True, progressive=True)
    print('moon_texture.jpg written from', SRC)
else:
    print('starry moon.png not found - moon_texture.jpg left unchanged')
