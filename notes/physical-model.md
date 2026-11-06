# Elastic Deformation of a 2D Plate: The Physical Model

Nov 6, 2026 · Ernesto Corral
> Formulation notes (Stage 1: physical and mathematical model), written by Ernesto with Claude on claude.ai. This file is derivation only: it contains no computed results. The numbers in it are hand estimates, such as pL/E ≈ 0.5 mm. The companion draft with results is `notes/ernesto-draft-force-driven.md`.

The physics of a pulled plate does more than produce a linear system K d = f: it guarantees that K is symmetric, positive definite and sparse, which is exactly what Cholesky, CG and the other solvers in the course need. These notes cover Step 1 of the project methodology (the physical model) and preview Steps 2 and 3.

## 1. What is elastic deformation?

Deformation is any change in the shape or size of a body caused by loads. It is *elastic* when it is reversible: remove the load and the body returns exactly to its original shape, giving back all the energy that was stored in it. A spring is the right mental model.

Metals behave this way because their atoms sit in a lattice held together by bonds that act like tiny springs. Load the material too much and planes of atoms start slipping: the deformation becomes *plastic* (permanent, like a bent paperclip), and eventually the material fractures. In a tensile test, stress vs strain starts with a straight segment. That segment is the only regime we model.

*Linear elasticity* rests on two separate linearities:

- **Material linearity:** stress is proportional to strain (Hooke's law).
- **Geometric linearity:** displacements are so small that every equation can be written on the original, undeformed square, and strain is a linear function of displacement.

Together they make the map from applied forces to displacements linear: double the force and every displacement doubles; two loads together give the sum of their separate responses (superposition). That is the deeper reason the final problem is a *linear* system. Dropping either assumption (large rotations, rubber, plasticity) gives a nonlinear system, usually solved by Newton's method, which needs a linear solve at every iteration, so the course's methods would still do the core work.

## 2. The physical situation we simulate

A thin square plate of side L and thickness t ≪ L, loaded only in its own plane. Concretely: a 1 m × 1 m steel sheet, 1 cm thick.

"Loaded only in its own plane" matters: this is the stretching problem, not bending (a shelf sagging under books is a different, harder theory). All forces lie in the plane of the plate, so it changes shape within that plane.

The left edge is clamped (welded to a rigid wall), the right edge is pulled horizontally, top and bottom are free. The load is applied slowly and held: static equilibrium; vibrations and impacts are not modelled. Dynamics would add a mass matrix and give M ü + K u = f(t), a system of ODEs; staying static means a single linear solve.

Physically, the plate gets longer in x. Because of the Poisson effect it also tries to get narrower in y. The clamped edge can't move, so the plate can't narrow there: the result is a plate that tapers from the clamp toward the pulled edge. For steel at realistic loads the right edge moves well under a millimetre, so deformation plots need a scale factor.

## 3. The forces we apply

- **Applied load:** uniform traction p on the right edge, force per unit area (Pa), pointing in +x, total force F = p · L · t. With p = 100 MPa on a 1 m × 1 cm edge, F = 10⁸ × 1 × 0.01 = 10⁶ N.
  The force is spread over the edge on purpose: in 2D elasticity a point force produces *infinite* displacement at that point (the exact solution behaves like ln(1/r) near the load), so point-loaded FEM values keep growing as the mesh is refined.
- **Body forces** (gravity) set to zero: the plate's weight is ρ g L² t ≈ 7850 × 9.81 × 1 × 0.01 ≈ 770 N, under a thousandth of the 1 MN load. If the plate lay flat, gravity would act out of plane and cause bending, a different model anyway.
- **Reaction forces:** what the clamp exerts to hold the plate. Not known in advance; they come out of the solution and must add up to exactly −F (a free correctness check).
- **Stresses** (internal forces) are not applied; they are the plate's response.

## 4. Displacement, strain and stress

### Displacement
Label each material point by its original position (x, y). After loading it sits at (x + u(x, y), y + v(x, y)). u (horizontal) and v (vertical) form the *displacement field* **u** = (u, v), in metres: the unknowns. Displacement alone doesn't say whether the material is loaded (a rigid slide u = 0.01, v = 0 stretches nothing). What loads the material is how the displacement *varies*: its derivatives, i.e. strain.

### Strain (dimensionless)
A tiny horizontal fibre from (x, y) to (x + dx, y): its right end moves u(x + dx, y) ≈ u(x, y) + (∂u/∂x) dx, so its new length is ≈ dx + (∂u/∂x) dx (vertical motion changes length only at second order). Normal strain:

```
ε_xx = [(dx + ∂u/∂x dx) − dx] / dx = ∂u/∂x        and likewise   ε_yy = ∂v/∂y
```

Shear: two perpendicular fibres; the x-fibre rotates by ∂v/∂x, the y-fibre tilts by ∂u/∂y, the right angle shrinks by their sum:

```
γ_xy = ∂u/∂y + ∂v/∂x
```

Sanity check: a small rigid rotation u = −θy, v = θx gives ε_xx = ε_yy = 0 and γ_xy = −θ + θ = 0. Every point moves, yet no strain: rotating a plate doesn't load it. (Matters for boundary conditions.)

In vector form:

```
ε = [ε_xx, ε_yy, γ_xy]ᵀ = 𝓛 u,     𝓛 = [ ∂/∂x    0    ]
                                         [   0    ∂/∂y  ]
                                         [ ∂/∂y   ∂/∂x  ]
```

𝓛 is a matrix of derivative operators; in FEM it becomes an ordinary matrix of numbers (B). Some books use ε_xy = γ_xy / 2: same physics, different bookkeeping.

### Stress (Pa, in practice MPa)
Internal force per unit area across an imaginary cut. In 2D three numbers capture every orientation: σ_xx (pull across a cut with normal along x), σ_yy (same for y), σ_xy (shear, sliding force along a cut). Moment balance on a tiny square forces σ_xy = σ_yx. Vector form **σ** = [σ_xx, σ_yy, σ_xy]ᵀ.

Traction on a boundary with outward unit normal **n** = (n_x, n_y) (Cauchy's formula, from force balance on a tiny wedge):

```
[T_x]   [σ_xx  σ_xy] [n_x]
[T_y] = [σ_xy  σ_yy] [n_y]          e.g. right edge n = (1, 0)  →  T = (σ_xx, σ_xy)
```

### How the three are connected
1. **Kinematics** (geometry): ε = 𝓛 u.
2. **Constitutive law** (material, Hooke). 1D: σ = E ε (E ≈ 200 GPa steel, 70 GPa aluminium). 2D also needs Poisson's ratio ν (≈ 0.3 steel). With σ_zz = 0 (plane stress):
   ```
   ε_xx = (σ_xx − ν σ_yy)/E,    ε_yy = (σ_yy − ν σ_xx)/E
   ```
   Inverting the 2 × 2 system ([a b; c d]⁻¹ = 1/(ad − bc) [d −b; −c a]):
   ```
   [σ_xx]        E     [1  ν] [ε_xx]
   [σ_yy] = ———————— [ν  1] [ε_yy]
             1 − ν²
   ```
   Shear: σ_xy = G γ_xy with G = E / (2(1 + ν)). Altogether:
   ```
   σ = D ε,    D = E/(1 − ν²) · [ 1  ν  0         ]
                                 [ ν  1  0         ]
                                 [ 0  0  (1 − ν)/2 ]
   ```
   Check of the corner entry: E/(1 − ν²) · (1 − ν)/2 = E / (2(1 + ν)) = G.
   D is **symmetric** and **positive definite** (eigenvalues E/(1 − ν²) times 1 + ν, 1 − ν and (1 − ν)/2, all positive for physical ν; any nonzero strain stores positive energy). K inherits both.
3. **Equilibrium** (Newton, zero acceleration). Force balance on a tiny rectangle [x, x + Δx] × [y, y + Δy] of thickness t, x-direction:
   ```
   [σ_xx(x+Δx, y) − σ_xx(x, y)] Δy t + [σ_xy(x, y+Δy) − σ_xy(x, y)] Δx t + b_x Δx Δy t = 0
   ```
   Divide by Δx Δy t and shrink:
   ```
   ∂σ_xx/∂x + ∂σ_xy/∂y + b_x = 0,     ∂σ_xy/∂x + ∂σ_yy/∂y + b_y = 0      (we take b = 0)
   ```

Substituting kinematics into Hooke into equilibrium leaves two coupled second-order PDEs in u and v alone:

```
E/(1−ν²) u_xx + G u_yy + E/(2(1−ν)) v_xy = 0,      G v_xx + E/(1−ν²) v_yy + E/(2(1−ν)) u_xy = 0
```

(mixed coefficient Eν/(1 − ν²) + G = E/(2(1 − ν))). u and v are coupled, which is why every mesh node carries two interacting unknowns.

## 5. Boundary conditions

*Why we need them.* The equilibrium equations hold inside every elastic body (clamped plate, plate on a hook, plate floating in space). They describe the material, not the situation. Boundary conditions describe the situation; without them there are infinitely many solutions. 1D analogue: u″ = 0 → u = ax + b, two conditions needed.

*Two types*, at every boundary point and in each direction exactly one is prescribed:
- **Displacement** (Dirichlet / essential): "this point is held here."
- **Traction** (Neumann / natural): "this much force per area acts here" (zero = free).

Never both, never neither. With **T** = σ**n**:

| Edge | Outward normal n | Condition | Type |
| --- | --- | --- | --- |
| Left, x = 0 | (−1, 0) | u = 0, v = 0 | Dirichlet (clamped) |
| Right, x = L | (1, 0) | σ_xx = p, σ_xy = 0 | Neumann (pulled) |
| Bottom, y = 0 | (0, −1) | σ_xy = 0, σ_yy = 0 | Neumann (free) |
| Top, y = L | (0, 1) | σ_xy = 0, σ_yy = 0 | Neumann (free) |

*Why the clamp is essential* (the key NLA fact). Without it, rigid motions (2 translations + 1 rotation in 2D) produce zero strain, so u + any rigid motion is also a solution: no uniqueness. With only a one-sided pull there is no static solution at all (the plate accelerates). Discretely: K has a 3-dimensional null space spanned by the rigid motions, so K is singular. Clamping removes all three at once, turning K into positive definite, exactly what Cholesky and CG need.

*Verification variant.* Left edge on rollers (u = 0, v free) with one corner pinned (v(0, 0) = 0): still removes all rigid motions, and has an exact solution (uniform tension):

```
u = p x / E,     v = −ν p y / E
```

Check: ε_xx = p/E, ε_yy = −νp/E, γ_xy = 0 → σ_xx = p, σ_yy = σ_xy = 0 everywhere: satisfies equilibrium and every BC. The FEM code should reproduce it to rounding error: the perfect correctness test before trusting it on the clamped plate (no closed form).

*Caveat.* At the two left corners (clamped meets free) linear elasticity predicts unbounded stresses. Displacements stay finite, but plotted corner stresses keep growing under refinement. Good entry for "problems encountered".

*Complete model (Stage 1 "model and boundary conditions"):*

```
Find u(x,y), v(x,y) on Ω = (0,L) × (0,L) such that:
  ∂σ_xx/∂x + ∂σ_xy/∂y = 0,   ∂σ_xy/∂x + ∂σ_yy/∂y = 0   in Ω,
  σ = D ε,   ε = 𝓛 u,
  u = v = 0 on x = 0,    σ_xx = p, σ_xy = 0 on x = L,
  σ_xy = σ_yy = 0 on y = 0 and y = L.
```

## 6. Assumptions that keep the model manageable

| Assumption | Physically | What it buys us |
| --- | --- | --- |
| Small deformations | strains far below 1 | linear strain formulas; equations on the undeformed square |
| Linear elastic material | stress stays below yield | σ = Dε is linear, so the whole problem is linear |
| Homogeneous | same material everywhere | constant E and ν: the same D in every element |
| Isotropic | same stiffness in every direction | only two material parameters |
| Plane stress | thin plate, in-plane loads, σ_zz = σ_xz = σ_yz = 0 | 3D reduces to 2D: two unknown fields instead of three |
| Static loading | load applied slowly, no vibration | no inertia term: one linear system, not ODEs in time |
| No body forces | gravity negligible | f comes only from the edge traction |
| Distributed load | force spread along the edge | avoids the 2D point-load singularity |
| Perfect clamp | left edge cannot move | Dirichlet conditions remove rigid motions, so K is positive definite |

*Is "small" justified?* Quick estimate (not a result): steel E = 200 GPa, p = 100 MPa → strain ≈ p/E = 5 × 10⁻⁴, right edge moves ≈ 0.5 mm. Stress well below the ≈ 250 MPa yield of structural steel. Linear elasticity justified away from the corners.

*Plane stress vs plane strain.* For a body very long in z (dam, tunnel) one assumes ε_zz = 0 instead. Only D changes, but plane-strain D contains 1/(1 − 2ν), which blows up as ν → 0.5 (nearly incompressible, like rubber) and makes K badly conditioned. For a thin metal plate, plane stress is right; the draft should say so explicitly.

## 7. From physics to a linear system

*The obstacle.* The unknown is a pair of functions (infinitely many values), governed by coupled PDEs with no closed form for the clamped plate. FEM: describe the displacement by its values at finitely many nodes and impose equilibrium in an energy sense.

### Warm-up: a chain of springs
Wall – node 1 – spring k – node 2 – spring k – node 3 ← force F pulling right. Unknowns u_1, u_2, u_3. A spring from i to j is stretched by u_j − u_i, tension k(u_j − u_i). Force balance:

```
node 1:  k(u_2 − u_1) + R = 0          ⇒  k(u_1 − u_2) = R     (reaction from the wall)
node 2: −k(u_2 − u_1) + k(u_3 − u_2) = 0  ⇒  k(−u_1 + 2u_2 − u_3) = 0
node 3: −k(u_3 − u_2) + F = 0          ⇒  k(−u_2 + u_3) = F

  k [ 1 −1  0] [u_1]   [R]
    [−1  2 −1] [u_2] = [0]
    [ 0 −1  1] [u_3]   [F]
```

That is already K u = f, and three things carry over to the plate:
1. K is **symmetric** (each spring couples its two nodes the same way in both directions).
2. Before any BC, K is **singular**: rows sum to zero, K [1, 1, 1]ᵀ = 0; the null vector is a rigid translation (1D version of section 5).
3. The BC repairs it: set u_1 = 0, drop the first equation (it only gives R) and first column:
   ```
   k [ 2 −1] [u_2]   [0]
     [−1  1] [u_3] = [F]
   ```
   Characteristic polynomial λ² − 3kλ + k² = 0, roots λ = k(3 ± √5)/2 ≈ 2.62k and 0.38k, both positive: SPD.
   Solve: row 1 gives u_3 = 2u_2; row 2 gives −k u_2 + 2k u_2 = F; so u_2 = F/k, u_3 = 2F/k. Each spring carries F and stretches F/k. Reaction R = k(0 − F/k) = −F.

*Same equations from energy.* A spring stretched by e stores ½ k e². Total potential energy = stored energy − work of the load:

```
Π(u_2, u_3) = ½ k u_2² + ½ k (u_3 − u_2)² − F u_3   =  ½ uᵀ K u − fᵀ u
∂Π/∂u_2 = k u_2 − k(u_3 − u_2) = 0,     ∂Π/∂u_3 = k(u_3 − u_2) − F = 0
```

Exactly the force balances: equilibrium = minimum of potential energy, ∇Π = Ku − f = 0. This is the link to Steepest Descent and CG.

*The structure behind it.*
1. Geometry: stretches e = A u (e_1 = u_2, e_2 = u_3 − u_2; A has rows (1, 0) and (−1, 1)).
2. Material: tensions w = C e, C = diag(k, k).
3. Equilibrium: Aᵀ w = f.

Chaining: Aᵀ C A u = f, and AᵀCA reproduces the matrix above. This chain is exactly the plate's displacement → strain → stress → force balance. Two-line proof of positive definiteness:

```
xᵀ K x = xᵀ Aᵀ C A x = (Ax)ᵀ C (Ax) ≥ 0
```

Equality only when Ax = 0, i.e. displacements that stretch nothing: rigid motions. Remove them with BCs and K is positive definite. The argument applies word for word to the plate, with C replaced by D.
