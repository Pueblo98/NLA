# Section 2. Displacement, forces and matrix construction

**Status: simplified for third-year level, 10 November 2026 (AI-assisted, for team review; not final).** Light trims to about 1.6 preview pages of body: precise thickness statement (K and f both proportional to t under traction loading, so d is independent of t), present-tense mesh sentence (structured square mesh in Section 4, Triangle for other objects in Section 5), shorter assembly footnote, eigensolver sentence moved to Section 3. `main.tex` now defines preview labels for Sections 4 and 5 and starts equations at (4). Built with pdflatex/BibTeX and inspected; `preview.pdf` matches the current source. The `scipy-eigsh` entry in `references.bib` is no longer cited here (Section 3 cites it). Build-failure notes below are historical.

Follow the [shared writing rules](../../WRITING_RULES.md) and [Section 2 roadmap](../../ROADMAP.md#2-displacement-forces-and-matrix-construction).

## Current files

- [section.tex](section.tex): current report body. Three connected stages explain material response, triangle contributions and supports, with matrix properties following from the supported system.
- [main.tex](main.tex): standalone A4/11 pt wrapper with 25 mm margins and section number 2. This is not the final course template.
- [references.bib](references.bib): existing four-source bibliography, unchanged by this rewrite.
- [derivation-notes.md](derivation-notes.md): expanded work balance, triangle-coordinate formulas, strain matrix, assembly indices, support blocks and load-sensitivity bound. Supporting algebra for reproduction and review; it is outside the main paper.
- [build.sh](build.sh): exact-source Tectonic or pdflatex/BibTeX build.
- [readability-checks.txt](readability-checks.txt): checks for the rewritten source and its connection to Section 1.
- [readability-build-status.txt](readability-build-status.txt): current build failure; Tectonic's missing TeX bundle cannot download. The source has not reached TeX compilation.
- [review-2026-11-10.md](review-2026-11-10.md): historical review and current revision record. Earlier statements that the source was unchanged or awaiting permission no longer describe the current revision.
- [build-status.txt](build-status.txt): historical build failure for the earlier source.

There is no `preview.pdf` in this checkout. Hermes previously reported successful compilation and visual inspection of the earlier source, with three pages including references. That PDF does not represent the current rewrite and must not be presented as its preview.

## What changed

Lucas's Codex rewrote the section after Lucas's readability request. Each stage explains its purpose before introducing notation. The explicit coordinate expansion of the strain matrix, full work integral, full block system and perturbation bound moved to the supporting derivation note. The paper retains the material law, element stiffness, support reduction, reactions, energy argument and condition number. It explains what the matrices do and what load sensitivity means in ordinary language. Four subsections became three.

After revising, Section 1 was reread in full and its ending compared with the new opening. The introduction, roadmap, numerical code, numerical results and bibliography remain unchanged. Sections 3–7 currently provide scope READMEs rather than complete section prose, so the larger-paper check uses their roadmap entries. No new experiment or solver ranking is claimed.

## Checks and build handoff

Static checks found 12 unique labels across Sections 1 and 2, no unresolved references or missing citation keys, and balanced LaTeX environments. The five distinct cited bibliography keys resolve. Both standalone bibliographies include `shewchuk-triangle`; retain one URL-bearing record when combining them. These checks do not verify PDF layout. The source and supporting algebra were compared with the existing assembly implementation for component order, shear convention, thickness factors and reaction sign. Numerical code was not changed, so no new numerical test run is claimed.

The revised build command was run from this folder:

```sh
sh build.sh > readability-build-status.txt 2>&1
```

It exited 101 because Tectonic's TeX resource bundle is not cached and its download failed. No replacement PDF from another rendering engine was created. The final small prose edits do not change that environment diagnosis; the completed current source requires a fresh build on a working TeX installation.

Hermes: build the current `main.tex`, render and inspect every page, check equations, bibliography, references and page breaks, then save the reviewed exact-source PDF as `preview.pdf`. Record the successful build evidence here. Keep normal fonts, margins and spacing. Final integration still needs the required `clean,onecolumn` course template and a check of the complete report's ten-page limit.

Darius-codex and pablo-agent: review the current paragraphs for flow against Section 1, using the supporting note if checking expanded algebra. This is an applied rewrite, not a request to approve the old proposed cuts.

## Open decisions and attribution

- Plane stress remains a working baseline, not a confirmed course requirement.
- The supplied course assembly routine is missing; obtain it or explicit permission to substitute `fem/elasticity.py:assemble` before final submission.
- General boundary-respecting meshes through `triangle` are planned; current rectangular examples use structured triangles.
- Supports must remove rigid motions on every separate piece. Pieces joined only at a node require a separate check.
- Eigenvalue estimation is proposed methodology; its tolerances and results belong in Sections 3 and 6.

The rewrite and supporting exposition were AI-assisted by Lucas's Codex. Existing citations are retained. Human mathematical review, actual member contributions and AI-use disclosure remain required for the final report. This section is not marked final and is not authorized for the final-drafts channel.
