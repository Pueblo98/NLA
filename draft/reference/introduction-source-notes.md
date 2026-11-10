# Building the model: prose revision

Lucas's Codex, 10 November 2026. AI-assisted working draft for team review;
not an approved final section.

## Latest request: opening punctuation and triangulation picture

Lucas asked to revise the first comma and add a picture on 10 November.
The opening sentence now reads: "We study how the geometry of a
two-dimensional elastic object and its supports affect its response to
applied forces." It has no comma. The rest remains connected prose with
the same three equations.

`figures/triangulation.pdf` is a vector figure included by `section.tex`;
`figures/triangulation.png` is a matching image for quick sharing. It shows
the same illustrative L-shaped region before and after triangulation.
The mesh fills the region, shares nodes and highlights a filled triangle.
The caption explains that displacement is approximated throughout each
triangle. The outline is an illustration, not a project geometry decision.

Regenerate using `python3 make_triangulation.py` with NumPy, SciPy and
Matplotlib installed. With this checkout's existing local dependencies,
run from the repository root:

```sh
PYTHONPATH=.build-deps MPLCONFIGDIR=.mplconfig python3 drafts/modules/01-building-model/make_triangulation.py
```

This diagram uses SciPy Delaunay on an aligned point set followed by a
domain filter; it is not a general constrained meshing implementation.
Checks passed for 29 nodes, 36 positive-area triangles, total area 4.5,
no triangle crossing the concave cutout, and edge incidence of one or two.
The figure PDF was rendered and visually checked: all labels are readable
and no content is clipped. The picture is original to this project.

The preview now loads `graphicx`. When integrating the section, retain
that package and copy the `figures` directory alongside the main document,
or adjust the image path. Keep the figure caption, label and text reference.

A fresh full LaTeX build still exits with code 101 because Tectonic's TeX
resource bundle is missing and cannot be downloaded in this environment.
The figure PDF is verified, but the updated section's pagination and
references remain unverified. Hermes: compile this exact source with
`sh build.sh`, check figure placement and attach the updated module PDF.
The previous build of `8a8e7d7` was reported by Hermes to fit one body page
plus references; it predates this picture and does not verify this layout.

## Current revision

Lucas's latest instruction supersedes the earlier requests for bullet points.
`section.tex` now uses connected paragraphs and three numbered equations.
It explains displacement, strain and stress in words before introducing
force balance, a filled triangular mesh, assembly and the constrained system.
The separate strain, interpolation and element-stiffness formulas have been
removed from the opening. Material parameters, particular shapes, solver
properties and the detailed finite element derivation belong in later modules.
The opening stays general across geometries, loads and support arrangements.

The retained labels are:

| Label | Meaning |
| --- | --- |
| `eq:model-field-balance` | Force balance inside the material |
| `eq:model-full-balance` | Full nodal equilibrium, including support forces |
| `eq:model-reduced-system` | System for the unknown displacements |

The old labels `eq:model-strain-stress`, `eq:model-interpolation` and
`eq:model-element-stiffness` are removed. No other current repository `.tex`
file references them. Later modules should use the retained labels to refer
back to the physical and matrix balances.

## Technical details for later modules

The opening assumes static, in-plane linear elasticity with small displacement
gradients, including small rotations. A particular plane-stress or plane-strain
law is not selected. Material and thickness assumptions must be specified in
the individual cases. Subscripts on displacement components denote directions,
not derivatives.

Triangulation partitions the existing solid region; it does not turn a set of
edges into material. Linear displacement interpolation throughout each filled
triangle agrees along a shared edge because both triangles use the same
endpoint values. Strain and stress may still jump between triangles.

For a more detailed derivation, multiply field equilibrium by a hypothetical
displacement `v` that is zero in prescribed components, integrate and integrate
by parts. With constant thickness `t`, the work balance is

\[
\int_\Omega t\,\varepsilon(v)^T D\varepsilon(u)\,dA
=\int_\Omega t\,v\cdot g\,dA
 +\int_{\Gamma_T}t\,v\cdot\bar\tau\,ds.
\]

Here the strain vector uses engineering shear, `g` is force per unit volume,
and `bar(tau)` is the prescribed boundary force per unit area. Substituting
linear nodal interpolation for `u` and `v` gives the triangle coefficients.
For constant material properties within an element, these are
`K_e = t * area(T_e) * B_e.T * D_e * B_e`, as in
`fem/elasticity.py`. Adding contributions at shared nodes gives the full
matrix. This is an integrated force balance; the approximation need not
satisfy the field equations pointwise.

For prescribed components `C` and free components `F`, the free equations are
`K_FF d_F + K_FC d_C = f_F`, since support reactions are zero in free
components. This gives `A = K_FF`, `x = d_F` and
`b = f_F - K_FC d_C`. Reactions are recovered from the constrained rows as
`r_C = K_CF d_F + K_CC d_C - f_C`.

Matrix symmetry, positive definiteness and solver choices are intentionally
left for the methods discussion. Positive definiteness requires a valid,
nondegenerate mesh, positive thickness, a symmetric positive-definite material
law and supports eliminating rigid motions on every connected component.
No new numerical experiments are claimed in this prose revision.

## Sources and disclosure

The existing citations to the FEniCSx elasticity tutorial and Shewchuk's
Triangle documentation remain in `section.tex` and `references.bib`.
Retain them and the course-required AI-use disclosure when combining modules.
No AI detector was used in this revision and no detector score is claimed.

## Build and verification

Run `sh build.sh` from this directory. The standalone wrapper `main.tex`
uses A4 paper, 11 pt text and 25 mm margins, with references on a separate
page. Include `section.tex` once in the combined course template and merge
the bibliography entries; do not shrink its fonts, margins or spacing.

The latest build result and figure checks are recorded above. Source checks
also confirmed three numbered equations, unique labels, matching equation
and figure references, no list environments, a comma-free opening sentence,
the `graphicx` dependency and the existence of the included PDF. These source
checks do not verify rendered section layout. Preserve normal template
spacing even if the added figure increases the section's length.
