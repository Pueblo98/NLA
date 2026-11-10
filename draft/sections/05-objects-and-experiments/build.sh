#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
if [ -n "${TECTONIC_BIN:-}" ]; then
  "$TECTONIC_BIN" --keep-logs --outdir build main.tex
elif command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs --outdir build main.tex
else
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
  bibtex build/main
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
fi
cp build/main.pdf preview.pdf
