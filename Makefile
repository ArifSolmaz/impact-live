PY=python3
NMC?=6000
NTRIAL?=10
all: dirs validate screen converge reach stats calendar refine scenarios injection figures tables site pdf
dirs:
	mkdir -p outputs/validation outputs/screening outputs/reachability outputs/scenarios outputs/tables outputs/figures outputs/logs
validate:
	$(PY) scripts/validate_ephemeris.py
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
calendar:
	$(PY) scripts/make_windows_calendar.py
scenarios:
	NMC=$(NMC) $(PY) scripts/run_scenarios.py
injection:
	NTRIAL=$(NTRIAL) $(PY) scripts/run_injection_recovery.py
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
serve:
	$(PY) -m http.server -d site 8000
pdf:
	@if [ -f paper/main.tex ]; then cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex; else echo "Manuscript not included in this repository yet; skipping the PDF step."; fi
.PHONY: all dirs validate screen converge refine reach stats calendar scenarios injection figures tables site serve pdf clean
clean:
	rm -rf outputs/screening outputs/reachability outputs/scenarios outputs/figures/*.png outputs/figures/*.pdf
