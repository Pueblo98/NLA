#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v tectonic >/dev/null 2>&1; then
    tectonic --keep-logs --untrusted main.tex
elif [ -x /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic ]; then
    TECTONIC_CACHE_DIR="$PWD/.build-cache" \
        /Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic \
        --keep-logs --untrusted main.tex
elif command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    bibtex main
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
else
    echo 'Install Tectonic or a LaTeX distribution with pdflatex and bibtex.' >&2
    exit 1
fi
if [ ! -s main.pdf ]; then
    echo 'Compilation did not produce main.pdf.' >&2
    exit 1
fi
