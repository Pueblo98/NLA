# Objects experiments (Section 5 design, Section 6 evidence): digest

Fresh run of `python3 draft/experiments/objects.py` (repo root), 10 Nov 2026, 648 s total.
Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1, triangle 20250106, Linux x86-64 (4 cores).
Full data: `objects.json` (everything), `cases.csv`, `solver_runs.csv`, `meshes.csv`,
`histories.npz` (residual histories of the four level-2 baselines, key `case|method`), `run.log`.
Figure: `python3 draft/experiments/objects_figure.py` -> `draft/sections/05-objects-and-experiments/figures/objects_meshes.{pdf,png}`.
Units: m, Pa, N; displacements in mm. Rounded to 3-4 significant figures. N = unknowns, m = cells per side (grids).

## Setup (implementation details kept out of the Section 5 prose)

| Object | Outer boundary, CCW (m) | Opening | Matched points |
|---|---|---|---|
| S square | (0,0),(1,0),(1,1),(0,1) | - | right_mid (1,0.5), top_right (1,1) |
| H plate | as S | circle centre (0.5,0.5), R = 0.15 | right_mid (1,0.5), hole_top (0.5,0.65) |
| L bracket | (0,0),(1,0),(1,0.5),(0.5,0.5),(0.5,1),(0,1) | - | right_mid (1,0.25), top_mid (0.25,1), corner (0.5,0.5) |
| B beam | (0,0),(4,0),(4,0.5),(0,0.5) | - | tip_mid (4,0.25), tip_top (4,0.5) |

- Matched points and the pin point (0,0.5) are extra input vertices on the edges (shape unchanged).
- Meshing: each input segment split into ceil(length/h) equal pieces; `triangle.triangulate(..., 'pq30a<sqrt(3)/4 h^2>')`;
  hole = inscribed regular polygon with 4*ceil(2*pi*R/(4h)) vertices + hole seed at the centre. Segment markers carry
  clamp/load labels to subsegments.
- Levels h: S/H/L 0.1, 0.05, 1/30, 0.025 m; B 0.125, 0.0625, 1/24, 0.03125 m (4/8/12/16 elements through depth).
- Material E = 200 GPa, nu = 0.3, t = 0.01 m, plane stress. Clamp u_x = u_y = 0 at all nodes of x = 0.
- Loads (consistent, l q/2 per edge end): S/H/L traction (p,0), p = 100 MPa on x = 1 (resultant 1e6 N; L: 5e5 N);
  B traction (0,-10 MPa) on x = 4, P = 5e4 N. Variants (level 2): H p = 25/250 MPa; L-top: traction (0,+p) on y = 1,
  0<=x<=0.5 (resultant 5e5 N, same A); B-axial: (p,0) on the tip (same A as B-base-L2); H-rollerpin: u_x = 0 on x = 0
  plus u_y = 0 at (0,0.5); H material (E GPa, nu) = (200, 0), (200, 0.45), (70, 0.3).
- Solvers: sparse LU (splu), CG, PCG (diagonal), MINRES, Gauss-Seidel on every system; all eight iterative methods on
  the four level-2 baselines. `solvers/progress_benchmark.iterative` unchanged: x0 = 0, eta < 1e-8, cap 20,000.
- Timing: best of 3 (history in a separate run) EXCEPT Gauss-Seidel outside levels 1-2 of the baselines: one timed run,
  no history (each capped GS run costs 10-40 s). Recorded per row as `timing_runs`.
- Conditioning: eigsh (which='LA' for lambda_max, shift-invert sigma=0 for lambda_min, tol 1e-10) on every system; none
  skipped. Dense eigvalsh cross-check for N <= 1500 (rel. difference <= 7e-10); dense Cholesky succeeded for every
  system with N <= 3000. rho_J and kappa(S) from eigsh on S = D^-1/2 A D^-1/2.
- Beam reference: Euler-Bernoulli PL^3/(3EI) = 51.20 mm, I = t W^3/12 = 1.042e-4 m^4; Timoshenko shear term
  PL/(kappa_s G t W), kappa_s = 5/6, = 0.624 mm; sum 51.82 mm.

## Mesh checks (all pass; `meshes.csv`)

Every mesh: all triangles CCW with positive area; min angle 30.0-30.2 deg, max 119.6-120.0 deg; area sum equals the
input-polygon area to <= 1.1e-16 rel.; boundary edges == output segments; every segment endpoint on its input segment;
0 centroids in the hole; 1 connected component; Euler characteristic V-E+T = 1 (0 for H).
Hole polygon vs true disc: solid area too large by 3.4e-3, 1.2e-3, 4.9e-4, 3.1e-4 (rel., levels 1-4) - geometric
discretization error. Nodes/triangles: S 206/370, 763/1444, 1706/3290, 3009/5856; H 201/350, 728/1356, 1606/3060,
2823/5446; L 162/280, 587/1092, 1280/2436, 2276/4390; B 272/470, 1019/1892, 2220/4222, 3905/7520.

Negative control (H level 1, u_x = 0 on x = 0 only, N = 391): lambda_min = 1.7e-6, lambda_2 = 8.0e6,
lambda_max = 1.6e10 N/m (ratio 1.1e-16: singular to rounding); dense Cholesky fails. Every real case: lambda_min > 0
(smallest: B-L4, 1.00e3 N/m).

## Main table: diagnostics, matched response, core solvers

Iterations; `*` = failed eta < 1e-8 (cap or native stop). "F imb"/"M imb": |sum(f + r)| / |applied resultant| and
|moment about origin| / (|resultant| x 1 m). Stored nnz of A includes explicit zeros.

| case | N | nnz | kappa2 | rho_J | kappa(S) | matched | value (mm) | max abs u (mm) | CG | PCG | MINRES | GS | LU eta | F imb | M imb |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-base-L1 | 390 | 5116 | 3375 | 1.272 | 2718 | right_mid ux | 0.4914 | 0.502 | 148 | 133 | 146 | 6816 | 1.6e-14 | 3.9e-15 | 7.2e-16 |
| S-base-L2 | 1484 | 20080 | 1.433e4 | 1.272 | 1.078e4 | right_mid ux | 0.4918 | 0.502 | 292 | 264 | 285 | 20000* | 4.9e-14 | 7.6e-15 | 7.0e-15 |
| S-base-L3 | 3350 | 45836 | 2.913e4 | 1.270 | 2.469e4 | right_mid ux | 0.4919 | 0.502 | 421 | 402 | 414 | 20000* | 1.0e-13 | 1.6e-14 | 8.4e-15 |
| S-base-L4 | 5936 | 81760 | 5.586e4 | 1.243 | 4.352e4 | right_mid ux | 0.4920 | 0.502 | 580 | 528 | 558 | 20000* | 1.5e-13 | 2.9e-16 | 1.0e-14 |
| H-base-L1 | 380 | 4872 | 4521 | 1.282 | 3109 | right_mid ux | 0.6537 | 0.654 | 153 | 141 | 152 | 7956 | 2.1e-14 | 2.8e-15 | 1.2e-16 |
| H-base-L2 | 1414 | 18964 | 1.600e4 | 1.269 | 1.253e4 | right_mid ux | 0.6763 | 0.676 | 306 | 281 | 302 | 20000* | 5.9e-14 | 3.7e-15 | 1.9e-15 |
| H-base-L3 | 3150 | 42820 | 3.509e4 | 1.394 | 3.076e4 | right_mid ux | 0.6846 | 0.685 | 452 | 425 | 438 | 20000* | 1.2e-13 | 6.5e-15 | 6.1e-15 |
| H-base-L4 | 5564 | 76232 | 6.685e4 | 1.383 | 5.546e4 | right_mid ux | 0.6868 | 0.687 | 618 | 573 | 602 | 20000* | 2.0e-13 | 3.0e-14 | 2.5e-14 |
| L-base-L1 | 302 | 3860 | 3298 | 1.177 | 2413 | right_mid ux | 0.4697 | 0.636 | 137 | 120 | 135 | 8545 | 1.4e-14 | 3.6e-15 | 1.7e-15 |
| L-base-L2 | 1132 | 15160 | 1.267e4 | 1.272 | 9960 | right_mid ux | 0.4717 | 0.633 | 271 | 246 | 268 | 20000* | 4.7e-14 | 7.6e-15 | 5.8e-16 |
| L-base-L3 | 2498 | 33924 | 2.826e4 | 1.343 | 2.352e4 | right_mid ux | 0.4724 | 0.631 | 396 | 370 | 390 | 20000* | 9.8e-14 | 3.9e-14 | 1.6e-14 |
| L-base-L4 | 4470 | 61204 | 4.955e4 | 1.306 | 4.200e4 | right_mid ux | 0.4726 | 0.630 | 537 | 499 | 526 | 20000* | 1.6e-13 | 4.4e-14 | 1.1e-14 |
| B-base-L1 | 534 | 6876 | 1.005e6 | 1.442 | 8.119e5 | tip_mid uy | -48.31 | 48.52 | 269 | 244 | 277* | 20000* | 1.8e-11 | 9.7e-12 | 3.1e-11 |
| B-base-L2 | 2020 | 27096 | 3.747e6 | 1.277 | 3.190e6 | tip_mid uy | -50.82 | 51.05 | 534 | 493 | 541* | 20000* | 5.5e-11 | 9.8e-12 | 2.4e-11 |
| B-base-L3 | 4414 | 60012 | 8.422e6 | 1.277 | 7.012e6 | tip_mid uy | -51.29 | 51.53 | 807 | 740 | 811* | 20000* | 1.2e-10 | 8.5e-11 | 2.6e-10 |
| B-base-L4 | 7776 | 106520 | 1.521e7 | 1.430 | 1.340e7 | tip_mid uy | -51.47 | 51.71 | 1067 | 991 | 1066* | 20000* | 1.9e-10 | 2.6e-11 | 1.0e-10 |
| H-p25-L2 | 1414 | 18964 | 1.600e4 | 1.269 | 1.253e4 | right_mid ux | 0.1691 | 0.169 | 306 | 281 | 302 | 20000* | 5.9e-14 | 3.7e-15 | 1.9e-15 |
| H-p250-L2 | 1414 | 18964 | 1.600e4 | 1.269 | 1.253e4 | right_mid ux | 1.691 | 1.691 | 306 | 281 | 302 | 20000* | 6.0e-14 | 3.6e-15 | 1.9e-15 |
| L-top-L2 | 1132 | 15160 | 1.267e4 | 1.272 | 9960 | top_mid uy | 0.3037 | 0.471 | 270 | 247 | 267 | 20000* | 3.5e-14 | 1.2e-15 | 1.6e-15 |
| B-axial-L2 | 2020 | 27096 | 3.747e6 | 1.277 | 3.190e6 | tip_mid ux | 1.997 | 1.997 | 533 | 492 | 529 | 20000* | 2.5e-13 | 2.3e-14 | 1.0e-14 |
| H-rollerpin-L2 | 1434 | 19196 | 2.215e4 | 1.269 | 1.753e4 | right_mid ux | 0.6821 | 0.682 | 331 | 301 | 328 | 20000* | 6.1e-14 | 3.8e-15 | 4.5e-15 |
| H-E200-nu0-L2 | 1414 | 18964 | 1.368e4 | 1.087 | 1.076e4 | right_mid ux | 0.6812 | 0.681 | 278 | 259 | 275 | 20000* | 5.9e-14 | 5.7e-15 | 2.2e-15 |
| H-E200-nu0.45-L2 | 1414 | 18964 | 1.868e4 | 1.388 | 1.466e4 | right_mid ux | 0.6694 | 0.669 | 332 | 301 | 326 | 20000* | 6.1e-14 | 3.7e-15 | 3.1e-15 |
| H-E70-nu0.3-L2 | 1414 | 18964 | 1.600e4 | 1.269 | 1.253e4 | right_mid ux | 1.932 | 1.932 | 307 | 281 | 302 | 20000* | 6.1e-14 | 2.7e-15 | 3.7e-16 |

Support satisfaction: d_C = 0 exactly in every case. Reaction resultants equal minus the applied resultant to
<= 1e-10 relative in every case.

## Refinement trends (least-squares log-log slopes vs N over levels 1-4)

| object | kappa2 ~ N^a | CG iters ~ N^a | PCG ~ N^a | PCG saving vs CG | change of matched value L1->2, 2->3, 3->4 (mm) |
|---|---|---|---|---|---|
| S | 1.02 | 0.50 | 0.51 | 4.5-10.1 % | 4.3e-4, 1.1e-4, 5.0e-5 |
| H | 1.00 | 0.52 | 0.52 | 6.0-8.2 % | 2.26e-2, 8.3e-3, 2.2e-3 |
| L | 1.01 | 0.50 | 0.53 | 6.6-12.4 % | 2.1e-3, 6.3e-4, 2.8e-4 |
| B | 1.01 | 0.52 | 0.52 | 7.1-9.3 % | 2.52, 0.47, 0.18 (tip deflection magnitude grows) |

So kappa2 ~ N ~ h^-2 and CG iterations ~ sqrt(kappa2). The beam's kappa2 is ~270x the square's at similar N
(lambda_min ~ 1e3-1.5e4 N/m, the soft bending mode), costing ~2x the CG iterations.

## Other responses

- Hole plate, peak element sigma_xx on hole-adjacent triangles (L1-L4): 279.8, 335.0, 360.5, 367.7 MPa = 2.80, 3.35,
  3.60, 3.68 x p (gross). Still rising; P1 constant-stress elements and a finite clamped plate (d/W = 0.3), not the
  infinite-plate Kirsch setting, so do not compare directly with 3. Hole-top u_y: -0.0832, -0.0983, -0.0992, -0.1024 mm.
- Bracket, max von Mises in triangles touching the re-entrant corner (L1-L4): 119.1, 138.0, 154.4, 177.5 MPa - keeps
  growing (consistent with the singularity), while the corner displacement converges (u_x 0.1242, 0.1266, 0.1278,
  0.1280 mm). Loaded-face mid u_y: 0.2765, 0.2715, 0.2689, 0.2676 mm.
- Beam tip_mid u_y (L1-L4): -48.31, -50.82, -51.29, -51.47 mm vs Euler-Bernoulli 51.20 mm and with shear 51.82 mm.
  FE approaches from below (P1 too stiff in bending); L4 is 0.7 % below the shear-corrected estimate. Tip-top u_x (L4) 4.78 mm.
- Beam axial (L2): tip u_x 1.997 mm vs pL/E = 2.000 mm (0.17 % lower; the clamp restrains contraction at the root).
- Linearity (H-L2): right_mid u_x 0.16907 / 0.67630 / 1.69074 mm for p = 25/100/250 MPa -> u/p identical to 6 digits;
  all iteration counts identical; stresses scale exactly.
- Load location (L-L2, equal resultant 5e5 N, same A): lower-arm end load: loaded-face u_x 0.4717 mm, max|u| 0.633 mm,
  corner VM 138 MPa. Upper-arm end load: loaded-face u_y 0.3037 mm, max|u| 0.471 mm, corner VM 71 MPa, max VM 332 MPa
  (near the clamp). Iterations nearly unchanged (CG 271 vs 270, PCG 246 vs 247, MINRES 268 vs 267).
- Supports (H-L2): roller+pin right_mid u_x 0.6821 vs clamp 0.6763 mm (+0.9 %); N 1434 vs 1414; kappa2 2.215e4 vs
  1.600e4 (+38 %); CG 331 vs 306, PCG 301 vs 281. Peak hole sigma_xx 332 vs 335 MPa.
- Material (H-L2): nu = 0 / 0.3 / 0.45: u 0.6812 / 0.6763 / 0.6694 mm; kappa2 1.368e4 / 1.600e4 / 1.868e4;
  rho_J 1.087 / 1.269 / 1.388; CG 278 / 306 / 332. E = 70 GPa: u = 1.9323 mm = (200/70) x 0.67630 exactly;
  kappa2, rho_J and stresses unchanged; CG 307 vs 306 (rounding), PCG and MINRES identical.
- Structured grids (fem/plate.force_driven, m x m cells, same square problem) vs Triangle meshes of S:

| mesh | N | kappa2 | right_mid u_x | top_right u_x | CG | PCG |
|---|---|---|---|---|---|---|
| grid m=10 | 220 | 2469 | 0.49081 | 0.49385 | 119 | 108 |
| grid m=20 | 840 | 9104 | 0.49160 | 0.49551 | 242 | 226 |
| grid m=30 | 1860 | 1.980e4 | 0.49181 | 0.49591 | 357 | 335 |
| grid m=40 | 3280 | 3.455e4 | 0.49190 | 0.49607 | 469 | 446 |
| S L1 | 390 | 3375 | 0.49141 | 0.49601 | 148 | 133 |
| S L2 | 1484 | 1.433e4 | 0.49183 | 0.49620 | 292 | 264 |
| S L3 | 3350 | 2.913e4 | 0.49194 | 0.49625 | 421 | 402 |
| S L4 | 5936 | 5.586e4 | 0.49199 | 0.49628 | 580 | 528 |

  At similar N (grid m=40, N=3280 vs S L3, N=3350) the Triangle mesh has lower kappa2 (2.91e4 vs 3.45e4) and fewer CG
  iterations (421 vs 469). rho_J is 1.18-1.44 on all baseline Triangle meshes (1.09 for nu = 0) vs 1.96 on the grid (Section 4), so Jacobi still
  diverges but more slowly (guard after 107-170 sweeps vs 49 on the grid).

## Full method set on the level-2 baselines (iterations / final eta / error vs LU / time ms; LU = factor + solve)

| method | S (N=1484) | H (N=1414) | L (N=1132) | B (N=2020) |
|---|---|---|---|---|
| sparse LU | - / 4.9e-14 / - / 4.45+0.20 | - / 5.9e-14 / - / 4.34+0.21 | - / 4.7e-14 / - / 2.79+0.14 | - / 5.5e-11 / - / 4.73+0.24 |
| Jacobi | 107* (guard) / 1.1e10 / 3.6e7 / 2.7 | 150* / 1.1e10 / 2.4e7 / 3.8 | 164* / 1.2e10 / 3.6e7 / 3.3 | 170* / 1.1e10 / 3.2e4 / 5.5 |
| Damped Jacobi | 20000* / 1.9e-5 / 4.7e-4 / 500 | 20000* / 2.6e-5 / 5.2e-4 / 481 | 20000* / 2.9e-3 / 6.1e-2 / 352 | 20000* / 0.23 / 0.99 / 668 |
| Gauss-Seidel | 20000* / 5.2e-8 / 1.0e-6 / 11710 | 20000* / 4.6e-7 / 8.5e-6 / 11720 | 20000* / 3.8e-6 / 6.6e-5 / 10560 | 20000* / 0.24 / 0.97 / 14830 |
| SD | 20000* / 1.8e-5 / 3.3e-4 / 851 | 20000* / 2.0e-5 / 3.6e-4 / 778 | 20000* / 1.5e-3 / 2.5e-2 / 773 | 20000* / 0.27 / 0.99 / 1204 |
| CG | 292 / 8.8e-9 / 6.9e-10 / 10.8 | 306 / 9.7e-9 / 5.0e-10 / 11.1 | 271 / 9.0e-9 / 4.5e-10 / 6.9 | 534 / 8.7e-9 / 3.0e-13 / 24.0 |
| PCG (diag) | 264 / 9.1e-9 / 9.9e-10 / 10.6 | 281 / 8.2e-9 / 3.1e-10 / 12.2 | 246 / 9.2e-9 / 4.8e-10 / 9.5 | 493 / 9.7e-9 / 4.6e-13 / 20.9 |
| MINRES | 285 / 9.6e-9 / 4.0e-9 / 26.0 | 302 / 9.2e-9 / 2.5e-9 / 26.7 | 268 / 8.5e-9 / 1.3e-9 / 20.5 | 541* / 1.8e-7 / 8.4e-12 / 50.5 |
| GMRES (full) | 277 / 9.3e-9 / 3.8e-9 / 369 | 293 / 9.1e-9 / 2.5e-9 / 310 | 262 / 8.7e-9 / 1.3e-9 / 287 | 516 / 8.3e-9 / 9.8e-12 / 1052 |

Times for every other system are in `solver_runs.csv`. Sparse LU is the fastest method on every system
(about 31 ms at N = 7776, where CG takes 162 ms and PCG 163 ms).

## Caveats for Section 6

1. MINRES fails the shared test on all four beam levels (eta 1.6e-8, 1.8e-7, 6.2e-7, 1.5e-6) although its error vs LU
   is tiny (4e-12 to 6e-11). SciPy's MINRES stopped natively (info = 0, its internal residual estimate reached rounding
   level with rtol = 0) while the recomputed residual had stagnated (L2 history: minimum 1.77e-7 over the final
   iterations). This is a residual-gap / attainable-accuracy effect at kappa2 ~ 1e6-1.5e7, not a large solution error;
   CG and PCG do reach 1e-8. Under the protocol it counts as a failure.
2. Beam systems are much worse conditioned; LU residuals there are 2e-11 to 2e-10 (accepted) and force/moment
   imbalances 1e-11 to 3e-10 relative (about 1e-14 for the plates).
3. Gauss-Seidel reaches 1e-8 only on level 1 of S, H and L; elsewhere it hits the cap, and on the beam it stalls
   (eta 0.2-0.3 at the cap). Its timing is a single run on systems outside levels 1-2 of the baselines (`timing_runs`).
4. Stresses are per-element constants (P1); peaks depend on the mesh and should be presented as trends. Beam stresses
   (450-540 MPa) and the p = 250 MPa case (840 MPa) exceed steel yield: linear-elastic model only.
5. E-scaling invariance holds to rounding only (CG 307 vs 306).
6. Run time 648 s, slightly above the 10-minute target; dominated by capped Gauss-Seidel, damped Jacobi, SD and full
   GMRES on the level-2 baselines.
