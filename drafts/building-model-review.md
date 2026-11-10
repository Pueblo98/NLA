# Opening module: implementation review

Lucas's Codex, 10 November 2026. For Hermes and Frambuesa, following Simon's
request to revise the report one module at a time.

## Scope and status

Checked the NLA-1/NLA-2 brief, report guidelines, Lab 5 checklist, the existing
progress draft, `fem/plate.py`, `fem/elasticity.py` and
`solvers/system_tools.py`. The new LaTeX source package and compiled PDF
announced by Hermes are absent from this checkout. This note reviews the
implementation and supplies wording for the mathematical bridge; it is not
an approval of his unseen text or PDF. No replacement module or PDF was made.

Hermes: please add the section `.tex`, standalone preview `.tex`, PDF and build
instructions under `drafts/modules/01-building-model/`. Keep the section
usable through `\input` when the modules are combined. The final report must
use the course's Overleaf template with `clean,onecolumn`; the half-to-one-page
target should also be checked there.

## Facts to retain in the opening

- The current force-driven benchmark is a 1 m square, 0.01 m thick, with
  $E=200$ GPa and $\nu=0.3$. It represents a thin elastic plate with steel-like
  material parameters. The code uses static, homogeneous, isotropic,
  small-strain linear elasticity under plane stress, with no body forces.
- Plane stress means that stresses through the thickness are neglected. The
  loading stretches the plate in its plane; this model does not describe
  bending out of the plane.
- Both displacement components vanish on the left edge. Uniform horizontal
  traction $p=100$ MPa acts on the right edge. Top and bottom are free of
  applied traction. Traction has units Pa; the assembled force vector has
  units N. Multiplication by thickness converts traction into a line load.
- Each triangle has three nodes and six displacement components. Linear
  interpolation makes strain constant inside a triangle. The material law
  maps strain to stress, and finite element equilibrium gives the matrix
  equations. This is an approximation to the continuous displacement field.
- Before supports are applied, $K$ is symmetric positive semidefinite, with
  two rigid translations and one rigid rotation on this connected mesh.
  Positive definiteness applies to the reduced matrix after those motions
  have been removed. Use this distinction when motivating Cholesky and CG.
- The present benchmark uses structured triangular meshes. Constrained
  Delaunay meshes and holes are later work. The repository assembly is our
  implementation; identification of the professor's provided routine is
  still open.

## Suggested mathematical bridge

The following is LaTeX-ready wording for Hermes to integrate where needed,
rather than an additional section to append to the opening:

```latex
We collect the horizontal and vertical displacement of every mesh node in
a vector $d$. Adding the contributions from the triangles gives a sparse
stiffness matrix $K$ and a load vector $f$: only nodes belonging to a common
triangle can be coupled by a matrix entry. At a free node, the internal
elastic forces must balance the applied load. At a fixed node, the support
supplies a reaction force, so its displacement is prescribed instead.
Writing $F$ for the free components and $C$ for the prescribed components,
the equations we solve are
\[
  A x=b,\qquad A=K_{FF},\qquad x=d_F,\qquad
  b=f_F-K_{FC}d_C.
\]
Here the fixed edge has $d_C=0$, so $b=f_F$. Fixing this edge prevents the
plate from translating or rotating as a whole. The reduced matrix $A$ is
therefore symmetric positive definite, which motivates the use of
Cholesky factorization and conjugate gradients.
```

For the force-driven problem, write the full equilibrium relation as
$Kd=f+r$, where $r$ contains support reactions and $r_F=0$. This avoids
implying that constrained rows satisfy the applied-load equations without
reactions. Keep detailed assembly formulas and solver comparisons for later
modules if they make the opening exceed the requested length.

## Numerical spot checks

Executed with the existing offline NumPy/SciPy packages, using
`force_driven(n)` with its default clamp and material parameters:

| Cells per side | Full matrix | Reduced matrix | Rigid modes | Cholesky | Total applied force |
| --- | --- | --- | --- | --- | --- |
| 2 | 18 by 18 | 12 by 12 | 3 | Pass | $(10^6,0)$ N |
| 4 | 50 by 50 | 40 by 40 | 3 | Pass | $(10^6,0)$ N |

Both checks confirmed symmetry of $A$ and $b=f_F$. The full matrix has three
eigenvalues of magnitude below $10^{-12}$ after scaling by its spectral
norm. Applying $K$ to the two translations and the infinitesimal rotation
$(-y,x)$ gives relative defects of $1.777\times10^{-17}$ and
$2.734\times10^{-17}$, respectively. These are small implementation checks,
not a substitute for the energy argument or a continuum-accuracy study.

## Writing and provenance

Use connected explanations, define terms where introduced, and avoid em
dashes as Simon requested. No humanizer skill is listed in this session.
No detector was run by this reviewer, and no score is claimed. Hermes
reported that his detector attempt was blocked. A zero-percent score is
not an acceptance criterion for this review; the checks are correctness,
clarity, attribution and the authors' ability to explain the model. Retain
the required AI-use disclosure and verified citations in the assembled
report. This note and its suggested wording were AI-assisted.
