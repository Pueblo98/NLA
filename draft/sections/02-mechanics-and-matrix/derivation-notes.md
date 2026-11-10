# Section 2: supporting algebra

Lucas's Codex, 10 November 2026. Supporting material for the readability revision requested by Lucas in the Section 2 Slack thread. This is an implementation and review reference, outside the main paper. It introduces no new numerical results. The paper keeps the physical explanation and essential equations; this file retains the expanded algebra for reproduction.

## Work balance

Use the strain and plane-stress material matrix defined in `section.tex`. Let $\Omega$ be the solid region, $t$ its constant thickness, $\mathbf g$ the force per unit volume (N/m$^3$), and $\bar\tau$ the applied boundary traction (Pa). A test displacement $\mathbf w$ is any sufficiently regular displacement that is zero in the components prescribed at supports. Multiplying local force balance by this test displacement and integrating by parts gives

\[
\int_\Omega t\,\varepsilon(\mathbf w)^TD\varepsilon(\mathbf u)\,dA
=\int_\Omega t\,\mathbf w^T\mathbf g\,dA
 +\int_{\Gamma_T}t\,\mathbf w^T\bar\tau\,ds.
\]

Here $\Gamma_T$ is the boundary where traction is prescribed; unloaded boundary components have zero traction. Traction equals the stress tensor multiplied by the outward unit normal. Each term has units of work (N m). This is the internal/external work balance used to obtain element stiffness. Source: J. Bleyer's *Isotropic and orthotropic plane stress elasticity*, cited as `bleyer-plane-stress` in `references.bib`.

## Triangle weights and derivatives

For counterclockwise triangle vertices $(x_i,y_i)$, $i=1,2,3$, let $S_e>0$ be the area. For cyclic index triples $(i,j,k)=(1,2,3),(2,3,1),(3,1,2)$, set

\[
a_i=x_jy_k-x_ky_j,\qquad \beta_i=y_j-y_k,\qquad \eta_i=x_k-x_j.
\]

The linear weights and their derivatives are

\[
N_i(x,y)=\frac{a_i+\beta_i x+\eta_i y}{2S_e},\qquad
\partial_xN_i=\frac{\beta_i}{2S_e},\quad
\partial_yN_i=\frac{\eta_i}{2S_e}.
\]

For $d_e=(u_{x,1},u_{y,1},u_{x,2},u_{y,2},u_{x,3},u_{y,3})^T$,

\[
\varepsilon(\mathbf u_h)=B_ed_e,\qquad
B_e=\frac{1}{2S_e}
\begin{bmatrix}
\beta_1&0&\beta_2&0&\beta_3&0\\
0&\eta_1&0&\eta_2&0&\eta_3\\
\eta_1&\beta_1&\eta_2&\beta_2&\eta_3&\beta_3
\end{bmatrix}.
\]

Using the same interpolation for the test movement in the work balance gives $w_e^TK_ed_e$ for its internal work. Because $B_e$, $D$ and $t$ are constant within the triangle,

\[
K_e=\int_{T_e}tB_e^TDB_e\,dA=tS_eB_e^TDB_e.
\]

The third strain component is engineering shear (twice the tensor shear strain), matching `fem/elasticity.py:strain_displacement`. Source for the element construction: University of Alberta, *Two Dimensional Solid Elements: Triangular Elements*, cited as `alberta-triangles`.

## Assembly and loads

Let $P_e$ select the six triangle components from the full interleaved displacement vector: $d_e=P_ed$. Then

\[
K=\sum_e P_e^TK_eP_e.
\]

In code, $P_e$ need not be formed. For a triangle with global vertex indices $(a,b,c)$, its six displacement indices are $(2a,2a+1,2b,2b+1,2c,2c+1)$. Add each entry of $K_e$ at the matching pair of indices. The implementation sums repeated entries and stores the result in compressed sparse row format.

The element body-force vector has vertex blocks $\int_{T_e}tN_i\mathbf g\,dA$. An edge's corresponding blocks are $\int_{\text{edge}}tN_i\bar\tau\,ds$. For constant $\bar\tau$, the two endpoint weights each integrate to half the edge length $\ell$, giving $\ell q/2$ at each endpoint, with $q=t\bar\tau$ in N/m. These are two-component force vectors. Thickness enters stiffness and traction loading once. Fixed total force and fixed traction need separate interpretations when varying thickness.

## Support reduction and reactions

Indices $F$ and $C$ select free and prescribed displacement components, respectively. With reactions zero on $F$, the full balance is

\[
\begin{bmatrix}K_{FF}&K_{FC}\\K_{CF}&K_{CC}\end{bmatrix}
\begin{bmatrix}d_F\\d_C\end{bmatrix}
=\begin{bmatrix}f_F\\f_C+r_C\end{bmatrix}.
\]

Its free rows give $A=K_{FF}$, $x=d_F$ and $b=f_F-K_{FC}d_C$. Its constrained rows give $r_C=K_{CF}d_F+K_{CC}d_C-f_C$. Keep loads applied at constrained components when recovering reactions. The free residual $(Kd-f)_F$ measures imbalance in the solved equations. Applied forces plus reactions should balance force and moment.

## Energy and load sensitivity

For the stated material range, $D$ is positive definite. The assembly formula gives

\[
d^TKd=\sum_e tS_e(B_ed_e)^TD(B_ed_e)\geq0.
\]

The factor $1/2$ converts this quadratic form to stored elastic energy. On a nondegenerate mesh connected through shared edges, zero strain leaves only the two translations and an infinitesimal rotation $\mathbf u=(-y,x)^T$ on each piece. Supports that remove all these motions make $A$ positive definite: extend any nonzero free variation by zero on $C$ and apply the energy formula. Pieces connected only at a vertex can have additional relative rotations and must be checked separately. Counting three constraints alone is insufficient.

For fixed supported $A$ and nonzero $b$, let $Ax=b$ and $A\delta x=\delta b$. Then

\[
\|\delta x\|_2\leq\|A^{-1}\|_2\|\delta b\|_2,
\qquad \|b\|_2\leq\|A\|_2\|x\|_2,
\]

so

\[
\frac{\|\delta x\|_2}{\|x\|_2}
\leq\kappa_2(A)\frac{\|\delta b\|_2}{\|b\|_2},
\qquad
\kappa_2(A)=\frac{\lambda_{\max}(A)}{\lambda_{\min}(A)}.
\]

This is a bound on possible amplification, not a prediction for every perturbation. With supports and prescribed values fixed, changing the free applied loads changes $b$ by the same amount. Eigenvalue-estimation tolerances and checks belong in Section 3; measured estimates and sensitivity belong in Section 6. The proposed sparse routine is documented in the existing `scipy-eigsh` bibliography entry.

## Remaining decisions

Plane stress is a working baseline. The supplied course assembly routine, or permission to use the team's alternative, still needs confirmation. No solver ranking, new experiment or continuum-accuracy claim is established by this derivation. This note and the revised prose were AI-assisted; retain the final report's contributions and AI-use disclosure.
