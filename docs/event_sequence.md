# Recommended public-event sequence for the AYAP-1 terminal impact (with contingencies)

Derived from the accompanying paper (release 2.0, in preparation). All times are relative to the predicted impact
time T0 at the lunar surface (the emission time). Photons and the last telemetry frames reach Earth about 1.2–1.35 s
later (the light time differs slightly between stations); ground processing adds an assumed 5–60 s and broadcast
production another 10–60 s.

## Before the event (weeks → hours)
1. **Mission disclosure** (≥ 4 weeks before): orbit plane, predicted impact ellipse and time with uncertainties,
   whether guided braking will be attempted, descent-camera and downlink plan. Release the final tracking solution as
   CCSDS OEM/SPICE.
2. **Orbital tasking**: pre-impact LROC NAC reference images of the ellipse; coordination letters to the LRO project /
   LROC operator, KARI/KASA (Danuri) and ISRO (Chandrayaan-2 OHRC), if these are still operating.
3. **Network rehearsal**: Tier-1 stations (NELIOTA; a Turkish professional station with a GPS-timed fast camera; a
   near-infrared station; a southern-hemisphere station) run the common pointing chart and the real-time pipeline on
   a natural-flash night and on the night before; injection–recovery and blank-sequence false-alarm tests on the actual
   equipment set each station's detection threshold.
4. **Public briefing** framed as technical uncertainty with quantified probabilities: "a flash may be too faint for
   small telescopes; instruments X and Y will try; here is what will be known and when". State explicitly that a
   livestream without a visible transient is not an optical detection. Preregister the engagement study (Appendix A of
   the manuscript) before this briefing.

## Live programme (T0 − 60 min → T0 + 60 min)
5. **Telemetry wall**: range, Doppler, altitude and a countdown to the predicted loss of signal; explain on screen
   that the last data are sent at the impact and arrive about 1.3 s later, and that processing and streaming add tens
   of seconds.
6. **Onboard descent imagery** as received (frames before loss of signal).
7. **Dark-side telescope feeds** (Turkish station + NELIOTA) with the predicted position marked; no claim is made from
   a single feed or a single camera.
8. **Loss of signal** is expected near T0 + light time. Loss of signal alone can also come from occultation,
   antenna, power or communications problems: impact confirmation combines the trajectory and telemetry with
   independent observations when they are available.
9. **T0 + 5–60 min: rapid processed replay** *only if* detections at two sites (or a dual-camera validation at one
   station) are found; otherwise an explicit statement "no optical detection yet; analysis continues; this is likely
   if the flash is in the fainter part of the predictions".

## After the event
10. **T0 + 1–24 h**: consolidated result — a confirmed detection with light curve and timing, or upper limits per
    station.
11. **Orbital crater reveal**, presented as a second, distinct milestone. For past well-located near-side impacts the
    first documented LROC NAC image came 0.6–11 days after the event and the public release 12–34 days after the
    event; far-side, high-latitude or poorly located impacts took about 2–4 months to image and longer to release. This
    is a heuristic from a small sample, not a forecast; if no orbiter is available, a later survey image replaces it.
12. **T0 + ~6 months**: low-Sun morphology and stereo, payload science (LNT, radiometer, radiation), engagement-study
    results.

## Contingency branches (pre-written)
- **No optical detection** (likely in the fainter part of the efficiency prior): run steps 8, 9 (negative), 10, 11.
- **Cloud at the Turkish stations** (TUG climatology in the planning model: monthly cloudy-sky probability 0.30 in
  July–August to 0.68 in December–January): switch the feed to the clearest Tier-1 station; the Turkish venue becomes
  a watch party; record this as an analysis branch in the engagement study.
- **Far-side, limb or sunlit impact**: no optical event is promised; the programme is built on telemetry and the
  crater reveal.
- **Loss of signal earlier or later than predicted**: report the observed loss-of-signal time; stations record
  continuously for ±15 min around the prediction, and the pipeline searches the whole recording.
- **Orbiter unavailable**: replace step 11 with a later survey or a request to other orbiters, and say so in advance.
