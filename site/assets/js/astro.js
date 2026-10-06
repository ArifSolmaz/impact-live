// Sky geometry in the browser, using Astronomy Engine (window.Astronomy, MIT licence).
// Validated against the study's DE421 pipeline: sub-Earth/sub-solar lunar points within 0.01 deg,
// topocentric Moon altitudes within 0.02 deg (scenario S1).
const A = () => window.Astronomy;
const D2R = Math.PI / 180;

function rotz(a, v) { const c = Math.cos(a), s = Math.sin(a); return [c * v[0] + s * v[1], -s * v[0] + c * v[1], v[2]]; }
function rotx(a, v) { const c = Math.cos(a), s = Math.sin(a); return [v[0], c * v[1] + s * v[2], -s * v[1] + c * v[2]]; }
function toMoonBody(t, v) {
  const ax = A().RotationAxis(A().Body.Moon, t);            // IAU pole (ra in hours, dec in deg) and prime-meridian angle W (deg)
  let w = rotz(Math.PI / 2 + ax.ra * 15 * D2R, v); w = rotx(Math.PI / 2 - ax.dec * D2R, w); return rotz(ax.spin * D2R, w);
}
function latlon(v) { const r = Math.hypot(v[0], v[1], v[2]); return { lat: Math.asin(v[2] / r) / D2R, lon: Math.atan2(v[1], v[0]) / D2R }; }

/** Selenographic sub-Earth and sub-solar points, illuminated fraction and distance at a date. */
export function moonGeometry(date) {
  const t = A().MakeTime(date);
  const m = A().GeoMoon(t), s = A().GeoVector(A().Body.Sun, t, true);
  const ill = A().Illumination(A().Body.Moon, t);
  return {
    subEarth: latlon(toMoonBody(t, [-m.x, -m.y, -m.z])),
    subSolar: latlon(toMoonBody(t, [s.x - m.x, s.y - m.y, s.z - m.z])),
    illum: ill.phase_fraction,
    distance_km: Math.hypot(m.x, m.y, m.z) * A().KM_PER_AU,
  };
}

/** Geographic points where the Moon and the Sun are overhead (for the Earth map). */
export function subPoints(date) {
  const t = A().MakeTime(date); const rot = A().Rotation_EQJ_EQD(t);
  const gast = A().SiderealTime(t);
  const f = (v) => {
    const r = Math.hypot(v.x, v.y, v.z);
    let lon = Math.atan2(v.y, v.x) / D2R - gast * 15; lon = ((lon % 360) + 540) % 360 - 180;
    return { lat: Math.asin(v.z / r) / D2R, lon, dist_km: r * A().KM_PER_AU };
  };
  return { moon: f(A().RotateVector(rot, A().GeoMoon(t))), sun: f(A().RotateVector(rot, A().GeoVector(A().Body.Sun, t, true))) };
}

/** Altitude (deg) of a body seen from (lat, lon) given its sub-point; topocentric parallax for the Moon. */
export function altitudeFromSubpoint(lat, lon, sp) {
  const H = (lon - sp.lon) * D2R;
  const s = Math.sin(lat * D2R) * Math.sin(sp.lat * D2R) + Math.cos(lat * D2R) * Math.cos(sp.lat * D2R) * Math.cos(H);
  const alt = Math.asin(Math.max(-1, Math.min(1, s))) / D2R;
  if (!sp.dist_km || sp.dist_km > 1e7) return alt;
  return alt - Math.asin((6371 / sp.dist_km) * Math.cos(alt * D2R)) / D2R;
}

/** Topocentric altitude/azimuth of the Moon or Sun for an observer (refraction included). */
export function altaz(bodyName, date, lat, lon, elev = 0) {
  const t = A().MakeTime(date); const obs = new (A().Observer)(lat, lon, elev);
  const body = bodyName === 'sun' ? A().Body.Sun : A().Body.Moon;
  const eq = A().Equator(body, t, obs, true, true); const h = A().Horizon(t, obs, eq.ra, eq.dec, 'normal');
  return { alt: h.altitude, az: h.azimuth };
}
export function illumination(date) { return A().Illumination(A().Body.Moon, A().MakeTime(date)).phase_fraction; }
