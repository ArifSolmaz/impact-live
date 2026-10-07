PY=python3
# Monte Carlo sizes (release 2.1 archive: MC_OUTER=200 MC_INNER=600 NTRIAL=100 NSEQ=3000)
MC_OUTER?=200
MC_INNER?=600
NTRIAL?=100
NSEQ?=3000
all: dirs validate screen converge reach stats reachconv calendar refine orbiters scenarios plumeconv injection figures tables site pdf manifest
dirs:
	mkdir -p outputs/validation outputs/screening outputs/reachability outputs/scenarios outputs/tables outputs/figures outputs/logs
validate:
	$(PY) scripts/validate_ephemeris.py
	$(PY) scripts/validate_lightcurves.py
screen:
	$(PY) scripts/run_screening.py
converge:
	$(PY) scripts/check_convergence.py
refine:
	$(PY) scripts/run_refinement.py
reach:
	$(PY) scripts/run_reachability.py
stats:
	$(PY) scripts/run_opportunity_statistics.py
reachconv:
	$(PY) scripts/check_reachability_convergence.py
calendar:
	$(PY) scripts/make_windows_calendar.py
orbiters:
	$(PY) scripts/make_orbiter_seasons.py
scenarios:
	MC_OUTER=$(MC_OUTER) MC_INNER=$(MC_INNER) $(PY) scripts/run_scenarios.py
plumeconv:
	$(PY) scripts/check_plume_convergence.py
injection:
	NTRIAL=$(NTRIAL) NSEQ=$(NSEQ) $(PY) scripts/run_injection_recovery.py
figures:
	$(PY) scripts/make_surface_maps.py
	$(PY) scripts/make_reachability_figure.py
	$(PY) scripts/make_physics_figures.py
	$(PY) scripts/make_timeline.py
	$(PY) scripts/make_matrix_and_orbiters.py
	$(PY) scripts/make_pareto.py
	$(PY) scripts/make_injection_figure.py
tables:
	$(PY) scripts/make_tables.py
site:
	$(PY) scripts/make_site_data.py
manifest:
	$(PY) scripts/make_release_manifest.py
serve:
	$(PY) -m http.server -d site 8000
# re-run everything in a clean copy (.check/run) and compare with the archived outputs; see docs/REPRODUCING.md
check:
	$(PY) scripts/check_reproduction.py
check-quick:
	$(PY) scripts/check_reproduction.py --quick
# independent exact-time check of the opportunity catalogue with astropy (about 10 min; re-audit GE-V2-03)
gatecheck:
	$(PY) scripts/check_catalogue_gates.py
# every reused quotation occurs where research/quotations.csv says it is used (re-audit ST-26)
quotes:
	$(PY) scripts/check_quotations.py
# the checker must pass the archived outputs and fail each corruption used in the re-audit
test-checker:
	$(PY) scripts/test_checker.py
pdf:
	@if [ -f paper/main.tex ]; then cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex; else echo "Manuscript not included in this repository yet; skipping the PDF step."; fi
.PHONY: all dirs validate screen converge refine reach stats reachconv calendar orbiters scenarios plumeconv injection figures tables site manifest serve check check-quick test-checker quotes gatecheck pdf clean
clean:
	rm -rf outputs/screening outputs/reachability outputs/scenarios outputs/figures/*.png outputs/figures/*.pdf
