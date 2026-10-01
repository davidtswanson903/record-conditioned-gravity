.PHONY: all test check realistic latex figures docs paper clean

PYTHON ?= python

all: test check realistic latex figures docs

test:
	$(PYTHON) -m pytest tests/ -q

check:
	$(PYTHON) experiments/check/run.py

realistic:
	$(PYTHON) experiments/realistic/run.py

latex: check realistic
	$(PYTHON) scripts/make_latex.py

figures: check realistic
	$(PYTHON) experiments/check/figures.py
	$(PYTHON) experiments/realistic/figures.py

docs: check realistic
	$(PYTHON) scripts/make_docs.py

# Compiles paper/draft/paper.tex against the generated feed (latex, figures).
# Not part of `make all`: the paper is a separate concern from the repository
# (paper/README.md), built on it rather than part of it.
paper: latex figures
	cd paper/draft && pdflatex -interaction=nonstopmode paper.tex
	cd paper/draft && bibtex paper
	cd paper/draft && pdflatex -interaction=nonstopmode paper.tex
	cd paper/draft && pdflatex -interaction=nonstopmode paper.tex

clean:
	rm -rf results/*.json build/figures/* build/latex/numbers.tex build/latex/tables/* build/latex/refs.bib
