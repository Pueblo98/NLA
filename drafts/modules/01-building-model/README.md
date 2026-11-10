# Building the model: equation-led revision

Lucas's Codex, 10 November 2026. Working proposal for Lucas, Simon, Darius,
Hermes and Frambuesa. AI-assisted, awaiting team review.

## What changed

The opening now uses five explanatory bullets and six numbered, labelled
`equation` environments. Its progression is displacement and relative motion,
strain and stress, field equilibrium, interpolation over filled triangles,
element stiffness, full nodal equilibrium, and the reduced linear system.
It keeps geometries, material values, load locations and support choices for
later case descriptions. Uniform positive thickness, small displacement
gradients, linear elasticity and static in-plane loading are modelling
assumptions; a particular plane stress/plane strain law is not selected here.

The mesh explanation starts with boundary segments, includes holes and
interior nodes, and explains that triangles cover an area. It does not imply
that triangulation changes a wire frame into a physical solid. Shared nodal
values give continuous displacement along shared edges; strain and stress
can jump between elements. Constrained Delaunay triangulation is the planned
meshing approach, not a claim that every shape is already implemented.

## Equation references for subsequent modules

| Label | Meaning |
| --- | --- |
| `eq:model-strain-stress` | Engineering strain and linear material law |
| `eq:model-field-balance` | Two scalar static equilibrium PDEs |
| `eq:model-interpolation` | Linear displacement inside a triangle |
| `eq:model-element-stiffness` | Constant-strain triangle stiffness |
| `eq:model-full-balance` | Full nodal balance including reactions |
| `eq:model-reduced-system` | Free displacement system `Ax=b` |

Use `\eqref{eq:model-field-balance}` and
`\eqref{eq:model-full-balance}` when explaining the physical origin of the
matrix equations. The displayed third strain component is engineering shear
`gamma_xy`, not tensor shear `epsilon_xy`; the implemented `D` and `B` use
this same convention. Subscripts on `u_x,u_y` denote components, not derivatives.

## Derivation behind the short opening

Let `v` be a hypothetical displacement that vanishes in prescribed
components. Multiply the field equilibrium equations by `v`, integrate over
the domain and integrate by parts. For constant thickness `t`, this gives

\[
\int_\Omega t\,\boldsymbol{\varepsilon}(v)^T D
                  \boldsymbol{\varepsilon}(u)\,dA
=\int_\Omega t\,v\cdot g\,dA
 +\int_{\Gamma_T}t\,v\cdot\bar{\tau}\,ds.
\]

Here `g` is body force per unit volume, `bar(tau)` is prescribed traction
(force per unit area), and the strain vector uses engineering shear. In
physical terms, internal and external work agree for every permitted small
change in displacement. This is integrated equilibrium, rather than exact
pointwise enforcement of the PDE inside each triangle.

Insert the linear nodal interpolation for `u` and `v`. Its derivatives form
`B_e`, constant on a straight triangle. With `D_e` constant on that triangle,
the integral becomes `t * area(T_e) * B_e.T * D_e * B_e`. This is the formula
in `fem/elasticity.py`, `element_stiffness`. In the assembly step, local node
indices are mapped to global indices and contributions at shared nodes are
added. The load vector is formed by integrating body forces and boundary
tractions with the same shape functions, so its entries are forces, not
tractions.

The free equations are `K_FF d_F + K_FC d_C = f_F`. Constrained equations
recover reactions as `r_C = K_CF d_F + K_CC d_C - f_C`. Thus `Kd=f+r`
includes the complete nodal balance, whereas `Ax=b` solves only for unknown
components. Zero prescribed displacement gives `b=f_F`; nonzero prescribed
displacements also contribute to `b`.

The unconstrained matrix is positive semidefinite. Positive definiteness
of `K_FF` assumes a conforming nondegenerate mesh, a symmetric positive-definite
material matrix, positive thickness and constraints eliminating rigid
motions on every connected component. Each connected two-dimensional
component has two translations and one infinitesimal rotation. These facts
are consistent with the earlier square-benchmark review; no new numerical
experiments are claimed in this writing revision.

## Sources

The equilibrium and integrated formulation were checked against
[Logg and Langtangen, The equations of linear elasticity, FEniCSx tutorial](https://github.com/jorgensd/dolfinx-tutorial/blob/main/chapter2/linearelasticity.md).
The boundary-conforming mesh and hole description were checked against
[Shewchuk, Triangle: Generating Delaunay triangulations](https://www.cs.cmu.edu/~quake/triangle.delaunay.html).
Accessed 10 November 2026. The first source illustrates an isotropic law;
our general `D` notation leaves the two-dimensional law to the case definitions.
`references.bib` contains both entries and `section.tex` cites both. Retain
source attribution and the required AI-use disclosure in the combined report.
No AI detector was used in this revision and no detector score is claimed.

## Build, verification and handoff

Run from this directory:

```sh
sh build.sh
```

The script supports Tectonic or `pdflatex` plus BibTeX and produces `main.pdf`.
It performs the extra LaTeX passes needed to resolve labels and citations.
The preview is A4, 11 pt, with 25 mm margins. References start on a separate
page so that the opening's length can be assessed independently. Include
`section.tex` once through `\input` in the combined report, merge the
bibliography entries, and use the course template with `clean,onecolumn`.

Compilation was attempted here on 10 November 2026. A bundled Tectonic
executable exists outside PATH, but the default TeX resource bundle is
absent. Both an offline attempt and `sh build.sh` failed while opening that
bundle; the network cannot fetch it. The cache was redirected inside the
module directory to respect workspace permissions. No new PDF was produced.
Consequently page count, typesetting, resolved reference numbers and visual
layout remain unverified; the earlier one-page PDF claim does not apply to
this revision. Static checks verify source label/reference consistency,
citation keys, matched environments and shell syntax only.

Hermes: compile this exact version in your working LaTeX environment, inspect
the PDF and attach it to the thread. Check the half-to-one-page target in the
course template; the extra equations may require shortening the prose or
moving the element stiffness formula to the methods module. Preserve the
field equilibrium, full reaction-inclusive balance and reduced-system labels.
Frambuesa: keep specific shapes and loading diagrams for later case modules.
