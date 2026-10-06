"""Export compact data for the impact-live website (site/data/) from the pipeline outputs.

Run after the pipeline (`make all`, or at least scenarios, tables and figures):   python3 scripts/make_site_data.py
Hand-edited site files that this script never touches: site/data/event.json, site/data/meta.json.

Writes: scenarios.json, sites.json, magnitudes.json, calendar.json, timeline.json, world.json, cities.json,
heat.json + moon_heat_tr.png / moon_heat_cov3.png, and copies selected figures to site/assets/figures/.
"""
import sys, os, json, glob, datetime as dt
import numpy as np, pandas as pd, yaml
from PIL import Image

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
from ayap1obs import impact as I, detect as D, montecarlo as MC

OUT = f'{root}/site/data'; FIG = f'{root}/site/assets/figures'
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

def dump(name, obj):
    json.dump(obj, open(f'{OUT}/{name}', 'w'), ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    print(f'{name:22s} {os.path.getsize(f"{OUT}/{name}") / 1024:7.1f} kB')

def r(x, n=3):
    if x is None: return None
    x = float(x)
    if not np.isfinite(x): return None
    return round(x, n)

cfg = yaml.safe_load(open(f'{root}/config/scenarios.yaml'))
sites_cfg = yaml.safe_load(open(f'{root}/config/sites.yaml'))['sites']
templates = MC.load_templates()

# ------------------------------------------------------------------ countries (names in both languages)
import shapefile
shp = shapefile.Reader(f'{root}/data/coast/ne_50m_admin_0_countries.shp')
flds = [f[0] for f in shp.fields[1:]]
NE = [dict(zip(flds, rec)) for rec in shp.records()]
CNAME = {}
for d in NE:
    for key in ('ISO_A2', 'ISO_A2_EH', 'WB_A2'):
        code = d.get(key)
        if code and code not in ('-99', '-1') and code not in CNAME:
            CNAME[code] = dict(en=d.get('NAME_EN') or d.get('NAME'), tr=d.get('NAME_TR') or d.get('NAME'))

# ------------------------------------------------------------------ observing sites
TIER = {'fast_camera_possible': dict(tr='Hızlı kamera takılabilir (aday)', en='Fast camera possible (candidate)'),
        'fast_camera_large': dict(tr='Büyük teleskop, hızlı kamera', en='Large telescope, fast camera'),
        'nir_large': dict(tr='Büyük teleskop, yakın kızılötesi', en='Large telescope, near-infrared'),
        'amateur_class': dict(tr='Amatör sınıfı teleskop', en='Amateur-class telescope'),
        'lunar_impact_system': dict(tr='Ay çarpma izleme sistemi', en='Lunar-impact monitoring system')}
sites = []
for s in sites_cfg:
    sites.append(dict(id=s['id'], name=s['name'], lat=s['lat'], lon=s['lon'], alt=s.get('alt'), country=s['country'],
                      country_name=CNAME.get(s['country'], dict(en=s['country'], tr=s['country'])), group=s['group'],
                      turkish=s['group'] == 'turkiye', tier=s.get('tier'), tier_label=TIER.get(s.get('tier'), dict(tr='', en='')),
                      approx=bool(s.get('approx', False))))
dump('sites.json', dict(note='Configured observing sites of the study; none has been contacted or confirmed (candidates).', sites=sites))

# ------------------------------------------------------------------ scenarios
NAMES = {
    'S1': ('Uygun: karanlık mare, Türkiye’de bahar akşamı', 'Favourable: dark mare, Türkiye spring evening'),
    'S2': ('Toz bulutu için uygun: gün doğumu sınırının 3° ötesi', 'Favourable for a plume: 3° beyond the sunrise terminator'),
    'S3': ('Ara: yaz sabahı, küçülen Ay, doğu yakın yüz', 'Intermediate: summer morning, waning Moon, eastern near side'),
    'S4': ('Ara: yaz akşamı, alçak Ay, az gözlemevi', 'Intermediate: summer evening, low Moon, few sites'),
    'S5': ('Elverişsiz: güneşli bölge', 'Unfavourable: sunlit terrain'),
    'S6': ('Elverişsiz: karanlık doğu kenarı (sabah)', 'Unfavourable: dark eastern limb (morning)'),
    'S7': ('Elverişsiz: karanlık batı kenarı (akşam)', 'Unfavourable: dark western limb (evening)'),
    'S8': ('Kutup: güney kutbu yaylaları, kenara yakın', 'Polar: south-polar highlands near the limb'),
    'S9': ('Uzak yüz (karşılaştırma)', 'Far side (control)'),
    'S10': ('Zayıf sinyal: S1 geometrisi, güçlü frenleme', 'Weaker signal: S1 geometry with strong braking'),
    'S11': ('Uygun alternatif: kış akşamı (Ocak havası)', 'Favourable alternative: winter evening (January weather)'),
}
WHY = {
    'S1': ('Büyüyen Ay (%39 aydınlık) saat 21:00’de TUG’da 52° yükseklikte; nokta gün doğumu sınırının ~29° batısında, karanlık mare üzerinde.',
           'Waxing Moon (39 % lit) 52° high at TUG at 21:00 Istanbul time; the point lies ~29° west of the sunrise terminator on dark mare.'),
    'S2': ('Aynı akşam; yüzey karanlıkta ama ~2,9 km’nin üstüne çıkan toz güneş ışığı alır. Yakındaki aydınlık arazi parlamayı zorlaştırır.',
           'Same evening; the surface is dark but ejecta above ~2.9 km catch sunlight. Nearby sunlit terrain makes the flash harder to see.'),
    'S3': ('Son dördün Ay, saat 03:00 (halk için uygun olmayan saat), 12 gözlemevi.', 'Last-quarter Moon at 03:00 Istanbul time (an unfriendly hour for the public), 12 sites.'),
    'S4': ('Kısa yaz gecesi; Ay TUG’da yalnızca ~23° yükseklikte, 6 gözlemevi.', 'Short summer night; the Moon is only ~23° high at TUG, 6 sites.'),
    'S5': ('S1 ile aynı akşam ama nokta güneş alan bölgede: parlama, parlak yüzeye karşı neredeyse görünmez.', 'Same evening as S1 but the point is in daylight: the flash is lost against the bright surface.'),
    'S6': ('Nokta Ay’ın kenarına çok yakın; araziyle örtülme olası.', 'The point is very close to the limb; terrain may hide it.'),
    'S7': ('Uygun librasyon noktayı görünür kılar ama kenara yakınlık sorun olmaya devam eder.', 'Favourable libration brings the point into view, but it stays close to the limb.'),
    'S8': ('Hemen her yörüngede ulaşılabilir (zamanlama esnekliği) ama kenara çok yakın ve arazi engebeli.', 'Reachable on almost every orbit (timing flexibility), but very close to the limb on rough terrain.'),
    'S9': ('Dünya’dan hiçbir zaman görünmez; yalnızca yörünge araçlarıyla sonradan incelenebilir.', 'Never visible from Earth; only later orbiter imaging is possible.'),
    'S10': ('Çarpma enerjisi frenleme ile ~5 kat azalır; daha dik çarpma, daha büyük zaman belirsizliği.', 'Braking cuts the impact energy ~5 times; steeper impact, larger timing uncertainty.'),
    'S11': ('Ay %37 aydınlık, saat 20:00’de TUG’da 45° yükseklikte; Ocak’ta açık gökyüzü olasılığı düşük.', 'Moon 37 % lit, 45° high at TUG at 20:00 Istanbul time; January skies are often cloudy.'),
}
REGION = {'near side central': ('yakın yüz, merkez', 'near side, central'), 'eastern limb region': ('doğu kenar bölgesi', 'eastern limb region'),
          'western limb region': ('batı kenar bölgesi', 'western limb region'), 'polar': ('kutup bölgesi', 'polar region'),
          'far side': ('uzak yüz', 'far side'), 'northern high latitude': ('kuzey yüksek enlem', 'northern high latitude'),
          'southern high latitude': ('güney yüksek enlem', 'southern high latitude')}
PLUME = {'shadow': ('Toz bulutu gölgede kalır (görünmez)', 'Ejecta plume stays in shadow (not visible)'),
         'sunlit_over_dark': ('Güneş alan toz bulutu, karanlık zemin üzerinde (dakikalarca görülebilir)', 'Sunlit plume over dark ground (visible for minutes)'),
         'over_sunlit': ('Toz bulutu parlak zemin üzerinde (zor)', 'Plume over bright ground (hard)'),
         'none': ('Dünya’dan görünmez', 'Not visible from Earth')}
def plume_code(reg):
    reg = (reg or '').lower()
    if 'stays in shadow' in reg: return 'shadow'
    if 'sunlit plume over' in reg: return 'sunlit_over_dark'
    if 'sunlit' in reg: return 'over_sunlit'
    return 'none'
PHYS = {'V_BAL': ('Balistik iniş, 1,68 km/s, 3°', 'Ballistic de-orbit, 1.68 km/s, 3°'), 'V_MOD': ('Orta frenleme, 1,35 km/s, 15°', 'Moderate braking, 1.35 km/s, 15°'),
        'V_STR': ('Güçlü frenleme, 0,8 km/s, 40°', 'Strong braking, 0.8 km/s, 40°'), 'V_NSL': ('Yumuşak inişe yakın, 0,3 km/s, 70°', 'Near-soft landing, 0.3 km/s, 70°')}
STRAT = {'A': 'A_turkiye_priority', 'B': 'B_global_science', 'C': 'C_public_participation'}
METRICS = {'any': 'p_any', 'two': 'p_two_indep', 'conf': 'p_confirmed', 'obvious': 'p_obvious_any', 'live': 'p_live', 'rapid': 'p_rapid_replay', 'turkish': 'p_turkish'}
FR = {'SAAO': 'Sutherland', 'KRY': 'NELIOTA (Kryoneri)', 'KOT': 'Kottamia', 'TUG': 'TUG', 'MAID': 'Maidanak', 'SAO': 'Zelenchukskaya', 'DAG': 'DAG', 'BYU': 'Byurakan',
      'SEV': 'MIDAS', 'ORM': 'La Palma', 'CAHA': 'Calar Alto', 'TEI': 'Teide', 'OUK': 'Oukaïmeden', 'TNO': 'Doi Inthanon', 'LIJ': 'Lijiang', 'OKA': 'Okayama', 'KISO': 'Kiso', 'SSO': 'Siding Spring', 'WISE': 'Wise', 'AUKR': 'Ankara Kreiken', 'ULUP': 'Ulupınar', 'EGE': 'Ege', 'IST': 'İstanbul', 'ERC': 'Erciyes', 'HAN': 'Hanle'}
INSTR = {'fast_camera_large': ('hızlı kamera', 'fast camera'), 'fast_camera_possible': ('misafir hızlı kamera', 'visitor fast camera'),
         'lunar_impact_system': ('çift kameralı sistem', 'dual-camera system'), 'midas_video': ('video istasyonu', 'video station'),
         'rtt150_fast': ('RTT150, hızlı kamera', 'RTT150, fast camera'), 'tug_t100_qhy': ('T100, GPS zamanlı kamera', 'T100, GPS-timed camera'),
         'dag_visitor_fast': ('misafir hızlı kamera', 'visitor fast camera'), 'dag_dirac': ('DIRAC, kızılötesi', 'DIRAC, infrared'),
         'nir_large': ('kızılötesi kamera', 'infrared camera'), 'amateur_class': ('amatör teleskop', 'amateur telescope')}
def station_name(key):
    sid, tpl = key.split(':')
    if sid == 'KRY': return dict(tr='NELIOTA (Kryoneri)', en='NELIOTA (Kryoneri)')
    if sid == 'SEV': return dict(tr='MIDAS (Sevilla)', en='MIDAS (Seville)')
    base = FR.get(sid, sid); tr, en = INSTR.get(tpl, ('', ''))
    return dict(tr=f'{base} · {tr}' if tr else base, en=f'{base} · {en}' if en else base)
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{root}/outputs/scenarios/S*.json')}
order = [s['id'] for s in cfg['scenarios'] if s['id'] in cards]
scen = []
for sid in order:
    c = cards[sid]; sc = next(s for s in cfg['scenarios'] if s['id'] == sid)
    p = {}
    for k, key in STRAT.items():
        p[k] = {}
        for prior, tag in (('slow-impact-wide', 'wide'), ('v3-scaled', 'v3')):
            m = c['mc'][f'{key}|{prior}']
            p[k][tag] = {mk: r(m[mm]) for mk, mm in METRICS.items()}
    mB = c['mc']['B_global_science|slow-impact-wide']
    top = sorted(((k, v) for k, v in mB['station_p_det'].items() if v > 0.005), key=lambda x: -x[1])[:8]
    epoch = pd.Timestamp(c['epoch_utc']).tz_localize('UTC')
    pl = c['plume']; code = plume_code(pl.get('regime')) if c['n_sites_available'] else 'none'
    lro = c['orbiters']
    scen.append(dict(
        id=sid, cls=c['cls'], lat=c['lat'], lon=c['lon'], epoch_utc=epoch.strftime('%Y-%m-%dT%H:%M:%SZ'),
        name=dict(tr=NAMES[sid][0], en=NAMES[sid][1]), why=dict(tr=WHY[sid][0], en=WHY[sid][1]),
        physics=dict(code=sc['physics'], v_km_s=c['physics']['v_km_s'], angle_deg=c['physics']['angle_deg'], mass_kg=c['physics']['mass_kg'],
                     sigma_t_min=c['physics']['sigma_t_min'], sigma_along_km=c['physics']['sigma_along_km'],
                     label=dict(tr=PHYS[sc['physics']][0], en=PHYS[sc['physics']][1])),
        energy_GJ=r(c['energy']['E_k_J'] / 1e9, 2), tnt_kg=r(c['energy']['tnt_equiv_kg'], 0),
        moon=dict(subsolar_lon=r(c['moon']['subsolar_lon'], 3), subsolar_lat=r(c['moon']['subsolar_lat'], 3),
                  subearth_lon=r(c['moon']['subearth_lon'], 3), subearth_lat=r(c['moon']['subearth_lat'], 3),
                  illum=r(c['moon']['illum_frac'], 3), age_days=r(c['moon']['moon_age_days'], 1), phase_angle=r(c['moon']['phase_angle'], 1),
                  distance_km=r(c['moon']['distance_km'], 0), light_time_s=r(c['moon']['light_time_s'], 2)),
        geometry=dict(emission=r(c['geometry']['emission_geocentric'], 1), incidence=r(c['geometry']['incidence'], 1), sunlit=bool(c['geometry']['sunlit']),
                      shadow_height_km=r(c['geometry']['shadow_height_km'], 1)),
        region=dict(tr=REGION.get(c['region'], (c['region'],) * 2)[0], en=REGION.get(c['region'], (c['region'],) * 2)[1]),
        n_sites=int(c['n_sites_available']), sites_available=c['sites_available'], turkish_sites=c['turkish_sites_available'],
        site_geom={k: dict(moon_alt=r(v['moon_alt'], 1), sun_alt=r(v['sun_alt'], 1), available=bool(v['available'])) for k, v in c['sites'].items()},
        population_bn=dict(public=r(c['population']['2'] / 1e9, 2), facility=r(c['population']['3'] / 1e9, 2)),
        peakV=dict(median=r(mB['peakV_median'], 1), p10=r(mB['peakV_p10'], 1), p90=r(mB['peakV_p90'], 1)),
        p=p, witness=dict(eyepiece=r(mB['p_eyepiece_witness'], 3), binoculars=r(mB['p_binocular_witness'], 4), naked=r(mB['p_naked_eye_witness'], 4)),
        top_stations=[dict(id=k.split(':')[0], name=station_name(k), p=r(v, 2)) for k, v in top],
        plume=dict(code=code, label=dict(tr=PLUME[code][0], en=PLUME[code][1]), shadow_height_km=r(pl.get('shadow_height_km'), 1),
                   V_mag=r(pl.get('plume_V_mag_10um'), 1), V_mag_upper=r(pl.get('plume_V_mag_10um_upper'), 1)),
        crater_m=[r(x, 0) for x in c['crater']['diameter_m']],
        terrain_p_visible=r(c['terrain']['p_visible_statistical'], 2),
        reach=dict(omega_asc=r(c['reachability'].get('omega0_ascending'), 1), omega_desc=r(c['reachability'].get('omega0_descending'), 1)),
        lro=dict(low_sun=lro['lro_low_sun_next'][1:], first_image_days=[lro['lro_first_image_days'][k] for k in ('well_located_min', 'well_located_typ', 'well_located_max')],
                 release_days=[lro['lro_release_days']['typ_min'], lro['lro_release_days']['typ_max']], p_operational=lro['p_lro_operational']),
    ))
po = pd.read_csv(f'{root}/outputs/tables/opportunity_probability_vs_duration.csv')
popp = lambda tol, cls, N: float(po[(po.tol == tol) & (po.cls == cls) & (po.months == N)].p_at_least_one.values[0])
opportunity = dict(A_3=r(popp(0.6, 'A_turkiye_evening_public', 3), 2), A_6=r(popp(0.6, 'A_turkiye_evening_public', 6), 2),
                   P_3=r(popp(0.6, 'P_plume_global', 3), 2), P_3_pc=r(popp(2.5, 'P_plume_global', 3), 2))
dump('scenarios.json', dict(opportunity=opportunity, note='HYPOTHETICAL test points of the study - not official AYAP-1 targets. Probabilities are conditional on the spacecraft reaching the stated terminal state.',
                            strategies=dict(A=dict(tr='Yalnız Türkiye', en='Türkiye only'), B=dict(tr='Küresel bilim ağı', en='Global science network'),
                                            C=dict(tr='Halka açık ağ', en='Public participation network')),
                            scenarios=scen))

# ------------------------------------------------------------------ flash brightness: prior-predictive sample (same code and seed as make_physics_figures.py)
dist = 3.80e8; ILLUM_PUB = 0.39
rng = np.random.default_rng(1); n = 20000
log_eta = I.luminous_efficiency_prior(1.68, rng, n, 'slow-impact-wide'); T0 = rng.uniform(1800, 3500, n); tau = np.exp(rng.uniform(np.log(0.1), np.log(2), n))
mass = rng.uniform(1600, 2400, n); Ek = I.kinetic_energy(mass, 1.68)
from scipy.interpolate import RegularGridInterpolator
T0g = np.linspace(1800, 3500, 18); taug = np.array([0.1, 0.2, 0.4, 0.8, 1.5, 2.0])
def offset(band):
    offs = np.array([[I.FlashModel(1, 1, t, 1200, ta, ta).peak_magnitude(band, dist) for ta in taug] for t in T0g])
    return RegularGridInterpolator((T0g, np.log(taug)), offs)(np.stack([T0, np.log(tau)], axis=1))
oV = offset('V')
peak = -2.5 * np.log10(10 ** log_eta * Ek) + oV
log_eta2 = I.luminous_efficiency_prior(1.68, rng, n, 'v3-scaled'); peak2 = -2.5 * np.log10(10 ** log_eta2 * Ek) + oV
ref = json.load(open(f'{root}/outputs/tables/peak_magnitude_distribution.json'))
assert abs(np.percentile(peak, 50) - ref['peakV_wide']['p50']) < 1e-9, 'sample differs from make_physics_figures.py'
band_peak = {b: -2.5 * np.log10(10 ** log_eta * Ek) + offset(b) for b in ('Rc', 'Ic', 'broad', 'Ks')}
band_peak['V'] = peak
edges = np.arange(-2.0, 20.0001, 0.25)
hist = lambda x: (np.histogram(x, bins=edges)[0] / len(x)).round(5).tolist()
thr = dict(naked=D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'none'), binoculars=D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'binoculars'),
           eyepiece=D.naked_eye_threshold_mag(0.3, ILLUM_PUB, 'telescope20cm'))
phone = {mode: D.limiting_magnitude(D.phone_instrument(mode), D.total_background_sb('broad', ILLUM_PUB, 10, -20), 8 / D.phone_processing_penalty(mode)) for mode in ('standalone', 'afocal')}
# instrument limits: same convention as the paper (illum 0.35, 8' from sunlit terrain, Sun -20 deg, SNR 8, above the atmosphere)
fm = I.FlashModel(I.kinetic_energy(2000, 1.68), 1e-4, 2500, 1200, 0.5, 0.5)
colour = {b: fm.peak_magnitude('V', dist) - fm.peak_magnitude(b, dist) for b in ('V', 'Rc', 'Ic', 'broad', 'Ks')}   # V - band for a 2500 K flash
def inst_limit(tname):
    tp = templates[tname]; band = tp['bands'][0]
    inst = D.Instrument(tname, tp['aperture_m'], band, tp['pixel_scale_arcsec'], tuple(tp['fov_arcmin']), tp['exposure_s'], tp['frame_time_s'],
                        throughput=tp['throughput'], obstruction=0.15, read_noise_e=tp['read_noise_e'], seeing_arcsec=tp['seeing_arcsec'])
    ext = float(D.extinction_mag(band, 1.2, 2500.0))
    return band, float(D.limiting_magnitude(inst, D.total_background_sb(band, 0.35, 8.0, -20, ext_mag=ext), 8.0) - ext)
methods = []
def add(key, tr, en, band, lim, kind, note_tr='', note_en=''):
    bp = band_peak['V' if band in ('V',) else band]
    methods.append(dict(key=key, label=dict(tr=tr, en=en), band=band, limit=r(lim, 2), v_equiv=r(lim + colour.get(band, 0.0), 2), kind=kind,
                        p_bright_enough=r(float(np.mean(bp < lim)), 4), note=dict(tr=note_tr, en=note_en)))
add('phone', 'Telefon kamerası (tek başına)', 'Phone camera (on its own)', 'V', phone['standalone'], 'public')
add('naked', 'Çıplak göz', 'Naked eye', 'V', thr['naked'], 'public')
add('binoculars', 'Dürbün (7×50)', 'Binoculars (7×50)', 'V', thr['binoculars'], 'public')
add('phone_scope', 'Telefon + 20 cm teleskop', 'Phone + 20 cm telescope', 'V', phone['afocal'], 'public')
add('eyepiece', '20 cm teleskop, göz ile', '20 cm telescope, by eye', 'V', thr['eyepiece'], 'public')
for tname, key, tr, en in [('amateur_class', 'amateur', 'Amatör teleskop + hızlı kamera', 'Amateur telescope + fast camera'),
                           ('lunar_impact_system', 'neliota', 'Ay çarpma izleme sistemi (1,2 m)', 'Lunar-impact monitoring system (1.2 m)'),
                           ('fast_camera_large', 'fast_large', '2–4 m teleskop, hızlı kamera', '2–4 m telescope, fast camera'),
                           ('nir_large', 'nir', '2–4 m teleskop, yakın kızılötesi', '2–4 m telescope, near-infrared')]:
    band, lim = inst_limit(tname)
    add(key, tr, en, band, lim, 'instrument', note_tr=f'{band} bandı', note_en=f'{band} band')
inj = json.load(open(f'{root}/outputs/tables/injection_recovery.json'))
dump('magnitudes.json', dict(
    note='Predicted peak brightness of the impact flash (ballistic case, 2 t at 1.68 km/s) under the wide luminous-efficiency prior (MODEL). Lower magnitude = brighter.',
    bins=dict(start=-2.0, step=0.25, count=len(edges) - 1),
    hist=dict(wide=hist(peak), v3=hist(peak2)),
    pct=dict(wide=dict(p5=r(np.percentile(peak, 5), 2), p50=r(np.percentile(peak, 50), 2), p95=r(np.percentile(peak, 95), 2)),
             v3=dict(p5=r(np.percentile(peak2, 5), 2), p50=r(np.percentile(peak2, 50), 2), p95=r(np.percentile(peak2, 95), 2))),
    colour_2500K={k: r(v, 2) for k, v in colour.items()}, methods=methods,
    injection={k: dict(mags=v['mags'], completeness=v['completeness'], false_alarm_per_frame=v['false_alarm_per_frame']) for k, v in inj.items()},
))

# ------------------------------------------------------------------ observing calendar and mission timeline
cal = pd.read_csv(f'{root}/outputs/tables/observing_windows_calendar.csv')
dump('calendar.json', dict(note='Türkiye observing windows (Moon > 25 deg at TUG, dark sky, 12-50 % lit), screening at 1-h steps.',
                           windows=[dict(date=row.date_utc, session='evening' if str(row.session).startswith('evening') else 'morning', start=row.window_start_utc,
                                         end=row.window_end_utc, hours=int(row.hours), best_utc=row.best_hour_utc, best_ist=row.best_hour_istanbul, illum=r(row.illum, 2),
                                         alt_tug=r(row.moon_alt_tug, 1), alt_dag=r(row.moon_alt_dag, 1), n_sites=int(row.n_sites_available), n_tr=int(row.n_turkish))
                                    for row in cal.itertuples()]))
tf = pd.read_csv(f'{root}/outputs/tables/timeline_families.csv'); tf = tf[tf.phase_case == 'nominal']
dump('timeline.json', dict(note='Launch-to-impact families (SCENARIO ASSUMPTIONS; nominal phase durations).',
                           families=[dict(launch=row.launch, launch_date=row.launch_date, loi=row.loi_date, science_start=row.science_start, months=int(row.science_months),
                                          impact_date=row.impact_date, n_windows=str(row.n_evening_windows_pm15d), best_window=str(row.best_window), lro=bool(row.in_LRO_low_sun_window))
                                     for row in tf.itertuples()]))

# ------------------------------------------------------------------ world map (Natural Earth, simplified)
def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; ab = b - a; L = np.hypot(*ab)
    rel = pts - a
    d = np.abs(ab[0] * rel[:, 1] - ab[1] * rel[:, 0]) / L if L > 0 else np.hypot(rel[:, 0], rel[:, 1])
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(pts[:i + 1], eps)[:-1], rdp(pts[i:], eps)])
    return np.vstack([a, b])
def rings(shape, eps):
    out = []; parts = list(shape.parts) + [len(shape.points)]
    for i in range(len(parts) - 1):
        pts = np.array(shape.points[parts[i]:parts[i + 1]], float)
        if len(pts) < 4: continue
        span = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]))
        if span < 0.6: continue                      # drop tiny islands
        s = rdp(pts, eps)
        if len(s) >= 4: out.append(np.round(s, 2).tolist())
    return out
land, turkey = [], []
for d, shape in zip(NE, shp.shapes()):
    rr = rings(shape, 0.12)
    land.extend(rr)
    if d.get('ADM0_A3') == 'TUR': turkey = rings(shape, 0.03)
dump('world.json', dict(source='Natural Earth 1:50m admin-0 countries (public domain), simplified', land=land, turkey=turkey))

# ------------------------------------------------------------------ cities for the location search
import geonamescache
gcities = geonamescache.GeonamesCache().get_cities().values()
TRCHARS = set('İıŞşĞğÇçÖöÜü')
def display_name(c):
    if c['countrycode'] == 'TR':
        for alt in c.get('alternatenames', []):
            if any(ch in TRCHARS for ch in alt) and alt.replace('İ', 'I').replace('ı', 'i').replace('ş', 's').replace('Ş', 'S').replace('ğ', 'g').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u') == c['name']:
                return alt
    return c['name']
cities = [c for c in gcities if (c['countrycode'] == 'TR' and c['population'] >= 40000) or c['population'] >= 1000000]
cities.sort(key=lambda c: (c['countrycode'] != 'TR', -c['population']))
dump('cities.json', dict(source='GeoNames via geonamescache (CC BY 4.0)', fields=['name', 'country', 'lat', 'lon', 'pop'],
                         cities=[[display_name(c), c['countrycode'], round(c['latitude'], 3), round(c['longitude'], 3), int(c['population'])] for c in cities]))

# ------------------------------------------------------------------ Moon heat layers (hours over Aug 2027 - Mar 2029), equirectangular PNG
from scipy.spatial import cKDTree
mp = np.load(f'{root}/outputs/screening/maps.npz')
la, lo = np.radians(mp['lat']), np.radians(mp['lon'])
tree = cKDTree(np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
Wd, Hd = 360, 180
glon = np.radians((np.arange(Wd) + 0.5) - 180.0); glat = np.radians(90.0 - (np.arange(Hd) + 0.5))
GL, GA = np.meshgrid(glon, glat)
_, idx = tree.query(np.c_[(np.cos(GA) * np.cos(GL)).ravel(), (np.cos(GA) * np.sin(GL)).ravel(), np.sin(GA).ravel()])
heat = {}
near = np.abs(mp['lon']) < 80
for key, fname, lo_pct in (('h_tr', 'moon_heat_tr.png', 5), ('h_plume_tr', 'moon_heat_plume.png', None)):
    v = mp[key][idx].reshape(Hd, Wd)
    from scipy.ndimage import gaussian_filter
    v = gaussian_filter(v.astype(float), sigma=(3.0, 4.0), mode=('nearest', 'wrap'))   # ~4 deg smoothing: broad pattern, no hourly-sampling stripes
    vmax = float(np.percentile(mp[key], 99.5)); vlo = float(np.percentile(mp[key][near], lo_pct)) if lo_pct else 0.0
    Image.fromarray((np.clip((v - vlo) / (vmax - vlo), 0, 1) * 255).round().astype(np.uint8), mode='L').save(f'{OUT}/{fname}', optimize=True)
    heat[key] = dict(file=fname, lo_hours=round(vlo), max_hours=round(vmax))
heat['note'] = ('Hours (Aug 2027 - Mar 2029, 1-h steps). h_tr: point dark, Earth-facing and flash-favourable with >=1 Turkish site available '
                '(scaled between the near-side 5th percentile and the 99.5th percentile). h_plume_tr: point dark with sunlit ejecta and >=1 Turkish site. '
                'Geometry only (no orbit or weather).')
dump('heat.json', heat)

# ------------------------------------------------------------------ figures for the science page (downscaled copies)
FIGS = ['fig_surface_screening', 'fig_reachability', 'fig_availability_timeseries', 'fig_flash_sensitivity', 'fig_lightcurves_limits',
        'fig_public_thresholds', 'fig_ejecta_crater', 'fig_plume_and_earthview', 'fig_timeline_families', 'fig_orbiter_windows',
        'fig_pareto', 'fig_injection_recovery', 'fig_sensitivity', 'fig_scenario_S1_coverage']
for f in FIGS:
    src = f'{root}/outputs/figures/{f}.png'
    if not os.path.exists(src): continue
    im = Image.open(src).convert('RGB')
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(f'{FIG}/{f}.jpg', quality=84, optimize=True, progressive=True)
print('figures copied:', len(os.listdir(FIG)))
