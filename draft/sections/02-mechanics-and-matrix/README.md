# Section 2. Displacement, Forces and Matrix Construction

**Status: Section 2 remains a review draft. Hermes reports successful compilation and visual inspection of the unchanged source in the Section 2 Slack thread on 10 November 2026. The compiled artifact is not present in this checkout; local compilation remains blocked.**

## Scope

Use [the Section 2 roadmap entry](../../ROADMAP.md#2-displacement-forces-and-matrix-construction) as the source of truth for this section's purpose, required contents, boundaries and expected output. Do not duplicate or silently redefine that scope here.

Follow [the shared writing rules](../../WRITING_RULES.md), including the review of all previous sections after each section is completed. Existing full progress reports are [reference material](../../reference/), not an approved replacement for this section.

## Files

- [section.tex](section.tex): this section's body, without a preamble.
- [main.tex](main.tex): standalone A4/11 pt preview wrapper with 25 mm margins, using section number 2. It is not the final course template.
- [references.bib](references.bib): four cited primary educational/documentation sources, checked online on 10 November. URLs also appear in the notes so the `amsplain` bibliography retains them.
- [build.sh](build.sh): compiles the exact LaTeX source to `main.pdf` with Tectonic or pdflatex/BibTeX.
- [build-status.txt](build-status.txt): historical diagnostic output from the failed local compilation; it does not describe Hermes's later successful build.
- `preview.pdf`: **absent from this checkout**. Hermes reports attaching the compiled PDF in Slack; independent artifact verification and repository synchronization remain pending.
- [review-2026-11-10.md](review-2026-11-10.md): proposed prose cuts and cross-section integration checks. The LaTeX body is unchanged.

## Draft decisions and boundaries

Simon's section-two request authorises this module. Lucas's Codex prepared the mechanics and matrix construction for coordination with Hermes; formal shared ownership is not assigned here.

The draft bridges from the introduction's reduced system to its derivation. It defines engineering shear, the plane-stress material law, the virtual-work balance, linear triangle interpolation and its strain matrix, element stiffness and sparse assembly. It also defines consistent edge loads, component-wise support reduction, reaction recovery, the energy argument for positive definiteness and the condition-number sensitivity bound. It contains no new experiment or solver ranking. The existing introduction and roadmap were not edited.

- Plane stress is a **working baseline**, matching the existing plate benchmarks, not a confirmed course requirement. Material values and case-specific geometry, supports and loads remain for Sections 4 and 5. Review this assumption with Hermes.
- The source identifies `fem/elasticity.py:assemble` as the team's current implementation. The provided course routine is still missing from this checkout; permission to substitute the team implementation is unconfirmed and must be resolved with the professor before final submission. The source flags this explicitly.
- General constrained meshes through `triangle` are specified rather than claimed as implemented. Existing rectangular benchmarks use structured triangles.
- The strain-energy proof distinguishes the unsupported singular matrix from its supported positive-definite reduction. It requires supports on every component and excludes components connected only by node hinges.
- Extreme-eigenvalue estimation and convergence/eigenpair checks are a proposed measurement procedure for later results, not a newly executed conditioning study.
- No additional geometry illustration was added: the preceding introduction already contains a triangulation picture. This section concentrates on the algebra behind it.

## Checks and reproducibility

Reread all of Section 1 after drafting, including its ending beside this section's opening. Detailed formulas stay here; the introduction's intuitive material explanation and diagram were not repeated. Necessary balance and reduced-system notation is restated to make the derivation explicit. The draft matches the code's engineering-shear convention, interleaved component ordering, thickness factors and reaction sign.

Source checks passed: nine unique labels (section plus eight equations), all three internal equation references resolve, four citation keys match exactly four bibliography entries, and LaTeX environments balance. These checks do not establish compilation or layout correctness.

Existing FEM checks passed with the available Python 3.13 interpreter, from the repository root:

```sh
PYTHONPATH=.build-deps /Users/lucasportela/.local/bin/python3 fem/check_fem.py
```

Output: `PASS: D, rigid-body null space, hand example, patch test, SPD, force/moment balance, linearity`.
The system `python3` selected by a login shell is Python 3.9 and cannot load the existing Python 3.13 binary dependencies; use the explicit compatible interpreter above. No numerical code was changed.

The compilation command `sh build.sh > build-status.txt 2>&1` exited 101. Bundled Tectonic exists, but its TeX resource bundle is not cached and downloading `https://relay.fullyjustified.net/default_bundle_v33.tar.index.gz` failed in this environment. No alternate TeX installation was found. This is an environment dependency, not evidence that the source compiles. A replacement PDF rendered by another document engine would not satisfy the request for compiled LaTeX, so none was produced.

Hermes handoff, from this folder on a machine with a working TeX installation/bundle:

```sh
sh build.sh
# Render and inspect main.pdf, including equations, bibliography and page breaks.
# After the exact-source PDF passes visual review:
cp main.pdf preview.pdf
```

Hermes has since reported successful Tectonic compilation of the unchanged source, three pages including references, resolved equation references/citations, and visual inspection without clipping or overflow. This is teammate-reported evidence from Slack, not an independent local check. Please save that exact-source PDF as `preview.pdf` here and retain the build evidence alongside it. If the proposed prose cuts are incorporated, compile and visually inspect the revised source before replacing the preview. Retain normal fonts, margins and spacing. Keep this module subject to team review; final-template integration and the report's overall 10-page limit remain to be checked.

## Attribution and disclosure

This is AI-assisted prose and mathematical exposition drafted by Lucas's Codex using the group's prior formulation notes and current implementation. The four external sources are cited where used. No new results are claimed, no human contribution is assigned without confirmation, and human mathematical/source review is still required. Carry the actual author contributions and AI-use disclosure into the final report.

## Handoff status

- Contribution: Lucas's Codex drafted the section and proposed simplifications; Hermes reports compiling, visually inspecting and attaching the unchanged-source PDF in Slack.
- Draft/review: source checks and existing FEM checks passed; Hermes's PDF review is recorded as reported evidence. Team review of the section and proposed cuts remains pending.
- Open decisions: confirm plane-stress baseline; obtain the supplied assembly routine or explicit permission for the alternative.
- Next action: synchronize Hermes's reviewed PDF and build evidence into this folder. Incorporate agreed prose cuts, then rebuild and inspect the exact revised source. When merging bibliographies, retain a single `shewchuk-triangle` entry with its URL in `note` for `amsplain`; see the review note. Do not post it as a final draft yet.
