# Building the model: proposed general opening

Lucas's Codex, 10 November 2026. For Hermes and Frambuesa, responding to
Simon's instruction to introduce the general problem before selecting shapes.
This is an AI-assisted proposal for review, not a final approved module.

## Scope

`section.tex` explains physical intuition, displacement, strain, stress,
static equilibrium, supports, triangular finite elements and the reduced
linear system. No particular material, shape, thickness, load location or
support arrangement is selected. Small-strain linear elasticity and static
in-plane motion are the modelling assumptions stated in this opening.
The relevant two-dimensional constitutive model, including plane stress or
plane strain, must be justified with the later physical examples.

The existing steel-like square benchmark is one implemented example. It
does not define the scope of the opening or establish that other shapes
have already been implemented. The NLA-1/NLA-2 brief (page 2) expressly asks
for several objects and comparisons of geometry, loads and supports.

This proposal supersedes the case-specific wording suggested in
`../../building-model-review.md` for the opening only. That file's numerical
checks still describe the existing square benchmark.

## Mathematical review

For free displacement components F and prescribed components C, the full
equilibrium relation is $Kd=f+r$, where $r_F=0$ and $r_C$ contains support
reactions. The opening's reduced system means

\[
A=K_{FF},\qquad x=d_F,\qquad b=f_F-K_{FC}d_C.
\]

The unrestricted stiffness matrix is positive semidefinite. A connected,
nondegenerate, conforming triangular mesh with a positive-definite elastic
constitutive law has two rigid translations and one infinitesimal rotation.
The reduced matrix is positive definite when the supports eliminate these
modes. Every disconnected component needs sufficient constraints. Detailed
assembly formulas and matrix proofs belong in later modules.

## Build and handoff

From this directory, use either an installed LaTeX distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

or Tectonic:

```sh
tectonic main.tex
```

`main.tex` is a standalone preview wrapper. Include `section.tex` through
`\input` when combining modules; the final report uses the prescribed
Overleaf template with `clean,onecolumn`.

No `pdflatex`, `tectonic` or `latexmk` executable is available on this
checkout's PATH. No PDF was generated, and the half-to-one-page layout has
not been verified. Hermes: compile and visually inspect this proposal in
your working LaTeX environment, then check its length in the course
template. Integrate into your existing module rather than appending two
openings. Frambuesa: keep the individual geometries and their loading
diagrams for the later case definitions.

Reviewed against the local NLA-1/NLA-2 brief and the previous technical
review. No numerical implementation was changed and no new solver results
are claimed. No detector was run in this revision. Retain the course's
required AI-use disclosure and source attribution in the combined report.
