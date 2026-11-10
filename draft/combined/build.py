"""Combine every drafted section into one preview PDF (not the final course template).

Run from the repository root: python3 draft/combined/build.py
Includes each draft/sections/NN-*/section.tex that exists, merges their
references.bib files (first entry per key wins) and compiles with pdflatex+bibtex.
"""
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
SECTIONS = sorted((HERE.parent / "sections").glob("[0-9][0-9]-*/section.tex"))

entries, order = {}, []
for sec in SECTIONS:
    bib = sec.parent / "references.bib"
    if bib.exists():
        for chunk in re.split(r"(?=^@)", bib.read_text(), flags=re.M):
            m = re.match(r"@\w+\{([^,]+),", chunk.strip())
            if m and m.group(1) not in entries:
                entries[m.group(1)] = chunk.strip()
                order.append(m.group(1))
(HERE / "references.bib").write_text("\n\n".join(entries[k] for k in order) + "\n")

paths = "".join("{../sections/%s/}" % s.parent.name for s in SECTIONS)
inputs = "\n".join("\\input{../sections/%s/section.tex}" % s.parent.name for s in SECTIONS)
(HERE / "main.tex").write_text(r"""\documentclass[a4paper,11pt]{article}
\usepackage[margin=25mm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{url}
\graphicspath{%s}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.6}
\renewcommand{\textfraction}{0.1}
\renewcommand{\floatpagefraction}{0.85}
\setcounter{topnumber}{3}
\title{Elastic Deformation of Two-Dimensional Objects\\\large Combined working draft}
\author{Group 02}
\date{\today}
\begin{document}
\maketitle
%s
\bibliographystyle{amsplain}
\bibliography{references}
\end{document}
""" % (paths, inputs))

run = lambda *c: subprocess.run(c, cwd=HERE, capture_output=True, text=True)
for step in (["pdflatex", "-interaction=nonstopmode", "main.tex"], ["bibtex", "main"],
             ["pdflatex", "-interaction=nonstopmode", "main.tex"],
             ["pdflatex", "-interaction=nonstopmode", "main.tex"]):
    run(*step)
log = (HERE / "main.log").read_text(errors="ignore")
problems = [l for l in log.splitlines() if re.search(r"undefined|Overfull|multiply defined|! ", l)]
(HERE / "draft-report.pdf").write_bytes((HERE / "main.pdf").read_bytes())
print("sections:", [s.parent.name for s in SECTIONS])
print("problems:", *problems[:20], sep="\n  ")
