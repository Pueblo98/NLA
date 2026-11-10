# Building the model: prose revision

Lucas's Codex, 10 November 2026. AI-assisted working draft for team review;
not an approved final section.

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

A fresh build of this prose revision was attempted on 10 November 2026.
It failed with exit code 101 because the bundled Tectonic compiler could not
open or download its missing TeX resource bundle. The local ignored
`compile.log` records the error. No PDF was produced for this revision;
page count, visual layout and resolved reference numbers remain unverified.
Hermes's earlier PDF builds correspond to the superseded source.

Static checks confirmed exactly three numbered equations, matching equation
labels and references, no list environments, no em dashes, and no remaining
uses of the three removed labels in repository LaTeX files. Citation keys,
environment pairing, brace pairing and shell syntax were also checked.
These checks do not establish that LaTeX compilation succeeds.

Hermes: compile this exact revised source using `sh build.sh`, check that
paragraphs and equations fit comfortably within the half-to-one-page opening
target, and attach the PDF. Keep the three numbered physical-to-matrix
balances; do not restore bullet points or squeeze the template spacing.
