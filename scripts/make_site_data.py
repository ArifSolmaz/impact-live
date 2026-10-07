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
    'S2': ('Terminatör toz bulutu testi: gün doğumu sınırının 3° ötesi', 'Terminator plume test: 3° beyond the sunrise terminator'),
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
    'S8': ('Güney kutbuna yakın: kutupsal bir yörünge yalnız bazı düzlemlerde noktanın yakınından geçer; nokta kenara çok yakın ve arazi engebeli.', 'Near the south pole: a polar orbit passes close to it only for some orbit planes, and the point is very close to the limb on rough terrain.'),
    'S9': ('Dünya’dan hiçbir zaman görünmez; yalnızca yörünge araçlarıyla sonradan incelenebilir.', 'Never visible from Earth; only later orbiter imaging is possible.'),
    'S10': ('Çarpma enerjisi frenleme ile ~5 kat azalır; daha dik çarpma, daha büyük zaman belirsizliği.', 'Braking cuts the impact energy ~5 times; steeper impact, larger timing uncertainty.'),
    'S11': ('Ay %37 aydınlık, saat 20:00’de TUG’da 45° yükseklikte; Ocak’ta açık gökyüzü olasılığı düşük.', 'Moon 37 % lit, 45° high at TUG at 20:00 Istanbul time; January skies are often cloudy.'),
}
REGION = {'near side central': ('yakın yüz, merkez', 'near side, central'), 'eastern limb region': ('doğu kenar bölgesi', 'eastern limb region'),
          'western limb region': ('batı kenar bölgesi', 'western limb region'), 'polar': ('kutup bölgesi', 'polar region'),
          'far side': ('uzak yüz', 'far side'), 'northern high latitude': ('kuzey yüksek enlem', 'northern high latitude'),
          'southern high latitude': ('güney yüksek enlem', 'southern high latitude')}
PHYS = {'V_BAL': ('Balistik iniş, 1,68 km/s, 3°', 'Ballistic de-orbit, 1.68 km/s, 3°'), 'V_MOD': ('Orta frenleme, 1,35 km/s, 15°', 'Moderate braking, 1.35 km/s, 15°'),
        'V_STR': ('Güçlü frenleme, 0,8 km/s, 40°', 'Strong braking, 0.8 km/s, 40°'), 'V_NSL': ('Yumuşak inişe yakın, 0,3 km/s, 70°', 'Near-soft landing, 0.3 km/s, 70°')}
STRAT = {'A': 'A_turkiye_priority', 'B': 'B_global_science', 'C': 'C_public_participation'}
METRICS = {'any': 'any', 'two': 'two_indep', 'dual': 'dual_validated', 'conf': 'confirmed', 'obvious': 'obvious_any', 'live': 'live', 'rapid': 'rapid', 'turkish': 'turkish'}
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
def plume_summary(c):
    """code: 'cannot' (outside the scaling domain in every case), 'weak' (within-domain cases all below SNR 5),
    'possible' (some case reaches SNR >= 5), 'none' (far side / not computed)."""
    cases = c['plume']['cases']
    if not cases:
        return dict(code='none', snr_max=None)
    det = [r for r in cases if r['status'].startswith('within')]
    if not det:
        return dict(code='cannot', snr_max=None, h_km=r(c['plume']['height_needed_km'], 1))
    # the paper's observer: a 1-m telescope at TUG (extincted); the idealised geocentre observer is not shown
    obs_of = lambda rr: [rr['observers']['TUG']] if 'TUG' in rr['observers'] else list(rr['observers'].values())
    snr = max(max(o['sys0.001']['snr_max'] for o in obs_of(rr)) for rr in det)
    fine = max(max(o['grains_sys0.001']['fine-rich'] for o in obs_of(rr)) for rr in det)
    opt = max(max(o['optimistic_corner_sys0.001']['snr_max'] for o in obs_of(rr)) for rr in det)
    return dict(code='possible' if snr >= 5 else 'weak', snr_max=r(snr, 1), snr_fine=r(fine, 1), snr_optimistic=r(opt, 1), n_within=len(det), n_cases=len(cases),
                h_km=r(c['plume']['height_needed_km'], 1), defaults='regolith grains, p Phi 0.03, kappa 0.2, subtraction systematic 1e-3')
cards = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f'{root}/outputs/scenarios/S*.json')}
order = [s['id'] for s in cfg['scenarios'] if s['id'] in cards]
scen = []
for sid in order:
    c = cards[sid]; sc = next(s for s in cfg['scenarios'] if s['id'] == sid)
    p = {}
    for k, key in STRAT.items():
        p[k] = {}
        for prior, tag in (('wide|broad', 'wide'), ('v-scaled|broad', 'vs')):
            m = c['mc'][prior]['strategies'][key]
            p[k][tag] = {mk: r(m[mm]['p']) for mk, mm in METRICS.items()}
            p[k][tag]['range'] = {mk: [r(m[mm]['outer_p05']), r(m[mm]['outer_p95'])] for mk, mm in METRICS.items()}
    mw = c['mc']['wide|broad']; mB = mw['strategies']['B_global_science']
    top = sorted(((k, v) for k, v in mB['station_p_det'].items() if v > 0.005), key=lambda x: -x[1])[:8]
    epoch = pd.Timestamp(c['epoch_utc']).tz_localize('UTC')
    vis = c['public']['visual']; env = c['crater']['rim_diameter_m']; lro = c['orbiters']['lro']
    lt = c['latency']['light_time_station_range_s']
    scen.append(dict(
        id=sid, cls=c['cls'], lat=c['lat'], lon=c['lon'], epoch_utc=epoch.strftime('%Y-%m-%dT%H:%M:%SZ'),
        name=dict(tr=NAMES[sid][0], en=NAMES[sid][1]), why=dict(tr=WHY[sid][0], en=WHY[sid][1]),
        physics=dict(code=sc['physics'], v_km_s=c['physics']['v_km_s'], angle_deg=c['physics']['angle_deg'], mass_kg=c['physics']['mass_kg'],
                     sigma_t_min=c['physics']['sigma_t_min'], sigma_along_km=c['physics']['sigma_along_km'],
                     label=dict(tr=PHYS[sc['physics']][0], en=PHYS[sc['physics']][1])),
        energy_GJ=r(c['energy']['E_k_J'] / 1e9, 2), tnt_kg=r(c['energy']['tnt_equiv_kg'], 0),
        moon=dict(subsolar_lon=r(c['moon']['subsolar_lon'], 3), subsolar_lat=r(c['moon']['subsolar_lat'], 3),
                  subearth_lon=r(c['moon']['subearth_lon'], 3), subearth_lat=r(c['moon']['subearth_lat'], 3),
                  illum=r(c['moon']['illum_frac'], 3), phase_angle=r(c['moon']['phase_angle'], 1), waxing=bool(c['moon']['waxing']),
                  age_days=r(29.53 * (c['moon']['elongation'] if c['moon']['waxing'] else 360.0 - c['moon']['elongation']) / 360.0, 1),
                  distance_km=r(c['moon']['distance_km'], 0), light_time_s=r(c['moon']['light_time_geocentric_s'], 2),
                  light_time_range_s=[r(lt[0], 3), r(lt[1], 3)] if lt else None),
        geometry=dict(emission=r(c['geometry']['emission_geocentric'], 1), incidence=r(c['geometry']['incidence'], 1), sunlit=bool(c['geometry']['sunlit']),
                      shadow_height_km=r(c['geometry']['shadow_height_km'], 1)),
        region=dict(tr=REGION.get(c['region'], (c['region'],) * 2)[0], en=REGION.get(c['region'], (c['region'],) * 2)[1]),
        n_sites=int(c['n_sites_available']), sites_available=c['sites_available'], turkish_sites=c['turkish_sites_available'], closed_sites=c['sites_closed'],
        site_geom={k: dict(moon_alt=r(v['moon_alt'], 1), sun_alt=r(v['sun_alt'], 1), available=bool(v['available']), visible=bool(v['visible']), closed=bool(v['closed'])) for k, v in c['sites'].items()},
        settlements_bn=dict(public=r(c['population']['by_radius']['10km']['public'] / 1e9, 2), public_range=[r(c['population']['by_radius']['25km']['public'] / 1e9, 2), r(c['population']['by_radius']['0km']['public'] / 1e9, 2)]),
        source_equiv_V=dict(median=r(mw['peakV']['median'], 1), p10=r(mw['peakV']['p10'], 1), p90=r(mw['peakV']['p90'], 1)),
        lab_trend_V=r(c['lab_trend']['V_peak'], 0),
        p=p,
        visual=dict(observable=bool(vis.get('observable', False)), **{k: dict(p=r(vis[a]['p_conditional'], 4), p_weather=r(vis[a]['p_with_weather'], 4))
                                                                       for k, a in (('naked', 'none'), ('binoculars', 'binoculars'), ('eyepiece', 'telescope20cm')) if a in vis}),
        top_stations=[dict(id=k.split(':')[0], name=station_name(k), p=r(v, 2)) for k, v in top],
        plume=plume_summary(c),
        crater=dict(vc=[r(env['vertical-component'][0], 0), r(env['vertical-component'][2], 0)], ve=[r(env['vertical-equivalent'][0], 0), r(env['vertical-equivalent'][2], 0)]),
        terrain=[r(x, 2) for x in c['terrain']['p_terrain_range']],
        reach=dict(p06=r(c['reachability']['p_random_polar_plane_within']['0.6'], 4), p25=r(c['reachability']['p_random_polar_plane_within']['2.5'], 4),
                   node=r(c['reachability']['required_node_mod180_deg'], 1), period_min=r(c['reachability']['orbital_period_min'], 0)),
        lro=dict(p_operational=lro['p_operational_assumed'], season=(lro['low_sun_season'] or {}).get('inside'),
                 days_until=(lro['low_sun_season'] or {}).get('days_until')),
    ))
po = pd.read_csv(f'{root}/outputs/tables/opportunity_probability_vs_duration.csv')
popp = lambda d, cls, N: float(po[(po.delta == d) & (po.cls == cls) & (po.months == N)].p_at_least_one.values[0])
wp = pd.read_csv(f'{root}/outputs/tables/opportunity_window_probability.csv')
w30 = lambda d, cls: float(wp[(wp.delta == d) & (wp.cls == cls) & (wp.W_days == 30)].p.mean())
opportunity = dict(A_3=r(popp(0.6, 'A_turkiye_evening_public', 3), 2), A_6=r(popp(0.6, 'A_turkiye_evening_public', 6), 2),
                   P_3=r(popp(0.6, 'P_plume_global', 3), 2), P_3_pc=r(popp(2.5, 'P_plume_global', 3), 2),
                   A_w30=r(w30(0.6, 'A_turkiye_evening_public'), 2), B_w30=r(w30(0.6, 'B_global_science'), 2), P_w30=r(w30(0.6, 'P_plume_global'), 2))
MC_META = dict(n_outer=int(cards['S1']['mc_settings']['n_outer']), n_inner=int(cards['S1']['mc_settings']['n_inner']))
dump('scenarios.json', dict(mc=MC_META, opportunity=opportunity, note='HYPOTHETICAL test points of the study - not official AYAP-1 targets. Probabilities are conditional on the spacecraft reaching the stated terminal state; ranges are the 5-95 % spread of the conditional probability over the assumption draws (weather, readiness, station calibration, backgrounds, subtraction systematic, terrain), with the inner Monte Carlo noise removed by a beta-binomial fit.',
                            strategies=dict(A=dict(tr='Yalnız Türkiye', en='Türkiye only'), B=dict(tr='Küresel bilim ağı', en='Global science network'),
                                            C=dict(tr='Halka açık ağ', en='Public participation network')),
                            scenarios=scen))

# ------------------------------------------------------------------ flash brightness and the detection ladder (S1 geometry seen from Istanbul)
c1 = cards['S1']; g_ist = c1['sites']['IST']; ILLUM_PUB = c1['moon']['illum_frac']
phys = cfg['physics']['V_BAL']; dist = 3.80e8
rng = np.random.default_rng(1); n = 40000          # the same sample as make_physics_figures.py
fp = {k: I.sample_flash_parameters(rng, n, phys['v_km_s'], phys['mass_kg'], k, 'broad', 0.1) for k in ('wide', 'v-scaled')}
pk = {k: I.peak_band_magnitude_fast('V', 10 ** f['log_eta'], f['E_k'], f['T0'], f['tau'], dist) for k, f in fp.items()}
ref = json.load(open(f'{root}/outputs/tables/peak_magnitude_distribution.json'))
assert abs(np.percentile(pk['wide'], 50) - ref['peakV_wide']['p50']) < 1e-9, 'sample differs from make_physics_figures.py'
edges = np.arange(-2.0, 22.0001, 0.25)
hist = lambda x: (np.histogram(x, bins=edges)[0] / len(x)).round(5).tolist()
f = fp['wide']; eta = 10 ** f['log_eta']; E_bol = eta * f['E_k'] / I.W_eval(f['T0'])
X = MC.kasten_young(g_ist['moon_alt']); extV = float(D.extinction_mag('V', X, 100.0))
G1 = I.G_eval('V', f['T0'], (D.T_EYE / f['tau'])[:, None])[:, 0]
m_eff = -2.5 * np.log10(E_bol / (4 * np.pi * (g_ist['range_km'] * 1e3) ** 2) * G1 * 10 ** (-0.4 * extV) / D.T_EYE / I.BANDS['V']['width'] / I.BANDS['V']['f0'])
bkgV = float(D.total_background_sb('V', ILLUM_PUB, g_ist['dist_sunlit_arcmin'], g_ist['sun_alt'], 3e-3, extV))
Fv = np.exp(np.random.default_rng(2).uniform(np.log(1.4), np.log(24.0), n))
pdet = {}
for key, aid in (('naked', 'none'), ('binoculars', 'binoculars'), ('eyepiece', 'telescope20cm')):
    pdet[key] = D.visual_detection_probability(m_eff, D.visual_threshold_mag(bkgV, aid, Fv), 0.5)
lad_inst = [('phone', D.phone_instrument('standalone'), D.phone_processing_penalty('standalone')), ('phone_scope', D.phone_instrument('afocal'), D.phone_processing_penalty('afocal'))]
for tname, key in (('amateur_class', 'amateur'), ('lunar_impact_system', 'neliota'), ('fast_camera_large', 'fast_large'), ('nir_large', 'nir')):
    tp = templates[tname]; st = MC.Station({'id': 'REF', 'alt': 2500.0, 'group': 'ref', 'lat': 0, 'lon': 0}, tname, tp, tp['p_ready'])
    lad_inst.append((key, st.instrument(tp['bands'][0]), 1.0))
lad_pub, pkV_l, fp_l, det_pub = MC.ladder_probabilities(lad_inst[:2], 'wide', 'broad', n, 1, tuple(phys['mass_kg']), phys['v_km_s'], g_ist['range_km'] * 1e3, ILLUM_PUB,
                                                        g_ist['dist_sunlit_arcmin'], g_ist['sun_alt'], float(X), 100.0, return_det=True)
lad_pro, pkV_p, fp_p, det_pro = MC.ladder_probabilities(lad_inst[2:], 'wide', 'broad', n, 1, tuple(phys['mass_kg']), phys['v_km_s'], g_ist['range_km'] * 1e3, ILLUM_PUB,
                                                        g_ist['dist_sunlit_arcmin'], -18.0, float(X), 2500.0, return_det=True)
N_MIN = 50                                          # bins with fewer prior draws are not shown (re-audit WB-N02)
def pav_decreasing(y, w):
    """Weighted isotonic (non-increasing) regression by pool-adjacent-violators."""
    blocks = []
    for yi, wi in zip(y, w):
        blocks.append([yi * wi, wi, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] < blocks[-1][0] / blocks[-1][1]:
            a = blocks.pop(); blocks[-1][0] += a[0]; blocks[-1][1] += a[1]; blocks[-1][2] += a[2]
    out = []
    for sw, ww, nn in blocks:
        out += [sw / ww] * nn
    return np.array(out)
def curve(pkv, d):
    """P(detect | peak V) per histogram bin: only bins with >= N_MIN prior draws (others null), weighted isotonic fit
    (brighter is never less detectable); no padding or extrapolation outside the sampled range."""
    nb = len(edges) - 1; idx = np.digitize(pkv, edges) - 1; ok_i = (idx >= 0) & (idx < nb)
    n = np.bincount(idx[ok_i], minlength=nb); sd = np.bincount(idx[ok_i], weights=d[ok_i], minlength=nb)
    pop = np.where(n >= N_MIN)[0]
    out = [None] * nb
    if len(pop):
        fit = pav_decreasing(sd[pop] / n[pop], n[pop])
        for i, v in zip(pop, fit):
            out[int(i)] = round(float(v), 4)
    return out, n
def half_point(cv):
    """Peak V where the detection chance falls to half its maximum within the sampled range (linear interpolation
    between bins); None if the chance is never measurably above zero or if it is still above half at the faintest
    sampled bin (flagged 'beyond')."""
    vals = [(i, v) for i, v in enumerate(cv) if v is not None]
    if not vals: return None
    mx = max(v for _, v in vals)
    if mx <= 0: return None
    mid = 0.5 * (edges[1:] + edges[:-1])
    above = [k for k, (i, v) in enumerate(vals) if v >= 0.5 * mx]
    k = max(above)
    if k == len(vals) - 1: return None
    (i0, v0), (i1, v1) = vals[k], vals[k + 1]
    return r(mid[i0] + (mid[i1] - mid[i0]) * (v0 - 0.5 * mx) / max(v0 - v1, 1e-9), 2)
def beyond_range(cv):
    vals = [v for v in cv if v is not None]
    return bool(vals and max(vals) > 0 and vals[-1] >= 0.5 * max(vals))
def sampled_range(cv):
    pop = [i for i, v in enumerate(cv) if v is not None]
    return [r(edges[pop[0]], 2), r(edges[pop[-1] + 1], 2)] if pop else None
LABELS = {'phone': ('Telefon kamerası (tek başına)', 'Phone camera (on its own)'), 'naked': ('Çıplak göz', 'Naked eye'), 'binoculars': ('Dürbün (7×50)', 'Binoculars (7×50)'),
          'phone_scope': ('Telefon + 20 cm teleskop', 'Phone + 20 cm telescope'), 'eyepiece': ('20 cm teleskop, göz ile', '20 cm telescope, by eye'),
          'amateur': ('Amatör teleskop + hızlı kamera', 'Amateur telescope + fast camera'), 'neliota': ('Ay çarpma izleme sistemi (1,2 m)', 'Lunar-impact monitoring system (1.2 m)'),
          'fast_large': ('2–4 m teleskop, hızlı kamera', '2–4 m telescope, fast camera'), 'nir': ('2–4 m teleskop, yakın kızılötesi', '2–4 m telescope, near-infrared')}
methods = []
pmax_of = lambda cv: r(max([v for v in cv if v is not None] or [0.0]), 3)
for key in ('naked', 'binoculars', 'eyepiece'):
    cv, nn = curve(pk['wide'], pdet[key])
    methods.append(dict(key=key, label=dict(tr=LABELS[key][0], en=LABELS[key][1]), kind='public', band='V', p=r(pdet[key].mean(), 4), half=half_point(cv), beyond=beyond_range(cv),
                        pmax=pmax_of(cv), sampled=sampled_range(cv), curve=cv, n_draws=nn.tolist(), basis='visual'))
for lad, det, pkv in ((lad_pub, det_pub, pkV_l), (lad_pro, det_pro, pkV_p)):
    for key, o in lad.items():
        cv, nn = curve(pkv, det[key].astype(float))
        methods.append(dict(key=key, label=dict(tr=LABELS[key][0], en=LABELS[key][1]), kind='public' if key.startswith('phone') else 'instrument', band=o['band'], p=r(o['p'], 4),
                            half=half_point(cv), beyond=beyond_range(cv), pmax=pmax_of(cv), sampled=sampled_range(cv), curve=cv, n_draws=nn.tolist(), basis='camera'))
inj = json.load(open(f'{root}/outputs/tables/injection_recovery.json'))
dump('magnitudes.json', dict(
    note=('Prior-predictive peak brightness of the flash (ballistic case, 1.6-2.4 t at 1.68 km/s; broad temperature prior; radiated energy <= 10 % of the kinetic energy) as an '
          'unocculted source-equivalent V magnitude at 380 000 km (MODEL). The ladder gives the probability of detection over that sample at the S1 geometry seen from Istanbul '
          f'(Moon {g_ist["moon_alt"]:.0f} deg high, {100 * ILLUM_PUB:.0f} % lit): eye methods use the conditional visual-threshold model (first 0.1 s, field factor 1.4-24, attention 0.5); cameras use exposure-integrated '
          'counts for randomly phased frames, noise applied before the best frame is chosen (SNR 8; phones in their broad band with the declared processing penalty). '
          f'Curves: bins with at least {N_MIN} prior draws only (null elsewhere: not sampled), weighted isotonic fit; half = peak V at which the chance falls to half its maximum within the sampled range.'),
    bins=dict(start=-2.0, step=0.25, count=len(edges) - 1),
    hist=dict(wide=hist(pk['wide']), vs=hist(pk['v-scaled'])),
    pct={k: dict(p5=r(np.percentile(v, 5), 2), p50=r(np.percentile(v, 50), 2), p95=r(np.percentile(v, 95), 2)) for k, v in (('wide', pk['wide']), ('vs', pk['v-scaled']))},
    lab_trend_V=r(c1['lab_trend']['V_peak'], 0), methods=methods,
    injection={k: dict(label=v['label'], band=v['bands'][0], m50=r(v['fits']['cam0']['m50'], 2), m50_ci=[r(x, 2) for x in v['fits']['cam0']['m50_ci95']],
                       m90=r(v['fits']['cam0']['m90'], 2), fa_per_box_frame=r(v['false_alarms']['candidate_rate_per_box_frame'][0]['rate'], 4), ntrial=v['ntrial'])
               for k, v in inj.items() if not k.startswith('_')},
))

# ------------------------------------------------------------------ observing calendar and mission timeline
dom = yaml.safe_load(open(f'{root}/config/domain.yaml')); CC = dom['criteria']['calendar']
cal = pd.read_csv(f'{root}/outputs/tables/observing_windows_calendar.csv')
dump('calendar.json', dict(
    criteria=dict(site=CC['site'], moon_alt_min=CC['min_moon_alt_deg'], sun_alt_max=CC['max_sun_alt_deg'], illum_min=CC['illum_min'], illum_max=CC['illum_max'], elongation_min=CC['min_elongation_deg'],
                  refine_step_min=CC['refine_step_minutes']),
    domain=dict(start=dom['domain']['start_utc'][:10], stop=dom['domain']['stop_utc'][:10]),
    note=('Observing sessions in which the calendar criterion holds at TUG (config/domain.yaml); start and end refined on a 5-min grid; times are full ISO timestamps in UTC and '
          'Istanbul time (UTC+3) with their own dates; night = local date of the evening; geometric planning windows only (no trajectory or weather).'),
    windows=[dict(night=row.night_istanbul, session='evening' if str(row.session).startswith('evening') else 'morning', start_utc=row.start_utc, end_utc=row.end_utc,
                  start_ist=row.start_istanbul, end_ist=row.end_istanbul, minutes=int(row.duration_min), best_utc=row.best_utc, best_ist=row.best_istanbul, illum=r(row.illum, 2),
                  alt_tug=r(row.moon_alt_tug, 1), alt_dag=r(row.moon_alt_dag, 1), n_sites=int(row.n_sites_available), n_tr=int(row.n_turkish))
             for row in cal.itertuples()]))
tf = pd.read_csv(f'{root}/outputs/tables/timeline_families.csv'); tf = tf[tf.phase_case == 'nominal']
nz = lambda v: None if (v is None or (isinstance(v, float) and not np.isfinite(v))) else v
dump('timeline.json', dict(note='Launch-to-impact families (MODELLING CHOICES spanning the published launch statements; nominal phase durations).',
                           families=[dict(launch=row.launch, launch_date=row.launch_date, loi=row.loi_date, science_start=row.science_start, months=int(row.science_months),
                                          impact_date=row.impact_date, n_sessions=nz(row.n_evening_sessions_pm15d), best_session=str(row.best_session_istanbul),
                                          lro_season=bool(row.in_LRO_low_sun_season), p30_A=nz(r(getattr(row, 'p30_A', None), 2)), p30_B=nz(r(getattr(row, 'p30_B', None), 2)))
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

# ------------------------------------------------------------------ Moon heat layers (hours over the screening domain), equirectangular PNG
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
heat['note'] = (f"Hours in [{dom['domain']['start_utc'][:10]}, {dom['domain']['stop_utc'][:10]}) UTC at 1-h steps (HEALPix nside 32 screening), interpolated to 1 deg and smoothed with a Gaussian of " 
                'sigma 3 x 4 pixels (~4 deg). h_tr: point dark, Earth-facing and flash-favourable with >=1 Turkish site available, colour scale clipped '
                'between the near-side 5th percentile (lo_hours) and the whole-surface 99.5th percentile (max_hours). h_plume_tr: point dark with '
                'possibly sunlit ejecta and >=1 Turkish site, scale 0..99.5th percentile. Geometry only (no orbit, terrain or weather); not a target map.')
heat['smoothing_sigma_px'] = [3.0, 4.0]
heat['interval'] = [dom['domain']['start_utc'][:10], dom['domain']['stop_utc'][:10]]
dump('heat.json', heat)

# ------------------------------------------------------------------ figures for the science page (downscaled copies)
FIGS = ['fig_surface_screening', 'fig_reachability', 'fig_availability_timeseries', 'fig_flash_sensitivity', 'fig_lightcurves_limits',
        'fig_public_thresholds', 'fig_ejecta_crater', 'fig_plume_S2', 'fig_plume_and_earthview', 'fig_timeline_families', 'fig_orbiter_windows',
        'fig_pareto', 'fig_injection_recovery', 'fig_sensitivity', 'fig_scenario_S1_coverage']
for f in FIGS:
    src = f'{root}/outputs/figures/{f}.png'
    if not os.path.exists(src): continue
    im = Image.open(src).convert('RGB')
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(f'{FIG}/{f}.jpg', quality=84, optimize=True, progressive=True)
print('figures copied:', len(os.listdir(FIG)))
