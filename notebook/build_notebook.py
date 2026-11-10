"""Generate Group02_Notebook.ipynb (the course's self-contained notebook).

The notebook is the deliverable; this script is how it is produced, so that
edits to the code cells can be reviewed as ordinary Python diffs.

Run from the repository root:
    python notebook/build_notebook.py
    jupyter nbconvert --to notebook --execute --inplace notebook/Group02_Notebook.ipynb

Optional arguments: <output.ipynb> <cases.json>. The Section 5 case
specification is read from the repository and embedded in the notebook, so the
generated notebook does not depend on any other file.
"""
import json
import sys

import nbformat as nbf

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
out_path = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "notebook" / "Group02_Notebook.ipynb")
cases_path = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "draft" / "sections" / "05-objects-and-experiments" / "cases.json")
cases = json.load(open(cases_path))

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))      # noqa: E731
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))        # noqa: E731

# ---------------------------------------------------------------- 0. Title
md(r"""
# Elastic Deformation of Two-Dimensional Objects
**Group 02 · Numerical Linear Algebra and PDEs · companion notebook to `Group02_Report.pdf`**

This notebook reproduces every number, table and figure in the report from scratch. It runs top to bottom with no other files.

**What it does**
1. Builds the linear system $A\mathbf{x}=\mathbf{b}$ for a thin elastic plate using linear triangular finite elements (report §1–2).
2. Solves a small system by hand-checkable direct methods (report §4).
3. Compares direct and iterative solvers on a larger system under one shared protocol (report §3–4).
4. Studies how conditioning and solver effort change with mesh refinement (report §4).
5. Validates the solution with equilibrium checks and an exact test case (report §4).
6. Runs the experiments on additional objects: a long rectangle and a square with a hole (report §5–6).
7. Exports every result table and figure to `outputs/` (Part 8).

**Units** throughout: metres, newtons, pascals.

**Run time:** about 10 minutes on a laptop. Most of it is the full solver protocol on every object case in Part 7. Set `FULL_PROTOCOL = False` in Part 7 for a quick run with CG and PCG only.
""")

md(r"""
## 0. Setup and dependencies

Required: `numpy`, `scipy` (version 1.12 or newer), `matplotlib` (standard scientific Python), and `triangle` (a Python interface to J. R. Shewchuk's Triangle mesh generator, used only in Part 6). The next cell installs `triangle` if it is missing.
""")
code(r"""
import importlib.util, subprocess, sys
if importlib.util.find_spec("triangle") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "triangle"])

import hashlib, json, platform
from time import perf_counter

import numpy as np
import scipy
import matplotlib
import matplotlib.pyplot as plt
import triangle as tr
from scipy.linalg import cho_factor, cho_solve, eigvalsh, inv, lu_factor, lu_solve
from scipy.sparse import coo_matrix, csr_matrix, diags, tril
from scipy.linalg import cholesky, LinAlgError
from scipy.sparse.linalg import cg, eigsh, gmres, minres, splu, ArpackNoConvergence
from scipy.sparse.linalg import norm as spnorm

if tuple(int(p) for p in scipy.__version__.split(".")[:2]) < (1, 12):
    raise RuntimeError(f"SciPy >= 1.12 is required (found {scipy.__version__}): "
                       "the solvers use the `rtol` keyword. Upgrade with: pip install -U scipy")

np.set_printoptions(precision=4, suppress=False, linewidth=110)
from pathlib import Path
OUT = Path("outputs")
(OUT / "results").mkdir(parents=True, exist_ok=True); (OUT / "figures").mkdir(parents=True, exist_ok=True)
def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.png", dpi=180, bbox_inches="tight")
print("python", platform.python_version(), "| numpy", np.__version__, "| scipy", scipy.__version__,
      "| matplotlib", matplotlib.__version__, "| triangle", getattr(tr, "__version__", "installed"))
print(platform.platform())
""")

# ---------------------------------------------------------------- 1. Model
md(r"""
## 1. Physical model (report §1–2)

A thin steel plate of thickness $t$ lies in the $xy$-plane. Its left edge is clamped and a uniform traction $p$ pulls its right edge. We want the displacement field $\mathbf{u}(x,y) = (u_x, u_y)$.

The chain of ideas:

| Quantity | Meaning | Relation |
|---|---|---|
| displacement $\mathbf{u}$ | how far each point moves | unknown |
| strain $\boldsymbol\varepsilon = (\varepsilon_{xx}, \varepsilon_{yy}, \gamma_{xy})$ | local stretching and shearing | derivatives of $\mathbf{u}$ |
| stress $\boldsymbol\sigma = (\sigma_{xx}, \sigma_{yy}, \tau_{xy})$ | internal force per area | $\boldsymbol\sigma = D\,\boldsymbol\varepsilon$ (Hooke's law) |
| equilibrium | every piece is in force balance | gives $K\mathbf{d} = \mathbf{f} + \mathbf{r}$ |

**Plane stress** (the plate is thin, so stresses through the thickness vanish) gives the material matrix

$$
D = \frac{E}{1-\nu^2}\begin{pmatrix}1 & \nu & 0\\ \nu & 1 & 0\\ 0 & 0 & \tfrac{1-\nu}{2}\end{pmatrix},
$$

with Young's modulus $E$ (stiffness) and Poisson's ratio $\nu$ (sideways contraction). $D$ is symmetric positive definite whenever $E>0$ and $-1<\nu<1/2$.

**Baseline case** (used in Parts 2–5): $1\times1$ m steel plate, $E = 200$ GPa, $\nu = 0.3$, $t = 1$ cm, $p = 100$ MPa, so the total pull is $p\,t\,(1\text{ m}) = 10^6$ N.
""")
code(r"""
E, NU, T, P = 200e9, 0.3, 0.01, 100e6     # Pa, -, m, Pa

def material_matrix(E, nu):
    # Plane-stress constitutive matrix D in sigma = D eps (engineering shear strain).
    if not (E > 0 and -1 < nu < 0.5):
        raise ValueError("need E > 0 and -1 < nu < 0.5 for a positive definite D")
    return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])

D = material_matrix(E, NU)
print("D [GPa] =\n", D / 1e9)
print("eigenvalues of D [GPa]:", np.linalg.eigvalsh(D) / 1e9, "-> all positive, D is SPD")
""")

# ---------------------------------------------------------------- 2. FEM
md(r"""
## 2. From triangles to the stiffness matrix (report §2)

We cut the plate into triangles and track only the corner (node) displacements. Node $i$ has two unknowns $(u_{x,i}, u_{y,i})$. We order them as $\mathbf{d} = [u_{x,0}, u_{y,0}, u_{x,1}, u_{y,1}, \dots]$.

Inside one triangle the displacement varies **linearly** between its three corners, so the strain is constant there: $\boldsymbol\varepsilon = B\,\mathbf{d}_e$, where $\mathbf{d}_e$ holds the triangle's 6 corner displacements. For corners $(x_k, y_k)$ in counter-clockwise order, with $b_i = y_j - y_k$, $c_i = x_k - x_j$ ($i,j,k$ cyclic) and area $\Delta$:

$$
B = \frac{1}{2\Delta}\begin{pmatrix} b_1 & 0 & b_2 & 0 & b_3 & 0\\ 0 & c_1 & 0 & c_2 & 0 & c_3\\ c_1 & b_1 & c_2 & b_2 & c_3 & b_3\end{pmatrix},
\qquad
K_e = t\,\Delta\, B^\top D B \quad (6\times 6).
$$

The global stiffness matrix $K$ is the sum of all $K_e$, each placed in the rows and columns of its triangle's unknowns (**assembly**). Nodes shared by several triangles collect contributions from each.
""")
code(r"""
def strain_displacement(xy):
    # Return (B, area) for one triangle with CCW corner coordinates xy (3, 2).
    (x1, y1), (x2, y2), (x3, y3) = xy
    two_area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if two_area <= 0:
        raise ValueError("triangle is degenerate or not counter-clockwise")
    b = np.array([y2 - y3, y3 - y1, y1 - y2])
    c = np.array([x3 - x2, x1 - x3, x2 - x1])
    B = np.zeros((3, 6))
    B[0, 0::2] = b          # eps_xx   = du_x/dx
    B[1, 1::2] = c          # eps_yy   = du_y/dy
    B[2, 0::2] = c          # gamma_xy = du_x/dy + du_y/dx
    B[2, 1::2] = b
    return B / two_area, two_area / 2


def element_stiffness(xy, D, t):
    B, area = strain_displacement(xy)
    return t * area * B.T @ D @ B


def assemble(nodes, triangles, E, nu, t):
    # Global stiffness K (sparse CSR, 2N x 2N). Duplicate entries from shared nodes are summed.
    D = material_matrix(E, nu)
    rows, cols, vals = [], [], []
    for tri in triangles:
        Ke = element_stiffness(nodes[tri], D, t)
        dofs = np.column_stack([2 * tri, 2 * tri + 1]).ravel()
        rows.append(np.repeat(dofs, 6)); cols.append(np.tile(dofs, 6)); vals.append(Ke.ravel())
    n = 2 * len(nodes)
    K = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
    K.sum_duplicates()
    return K
""")
md(r"""
**Quick check on one triangle.** $K_e$ must be symmetric. It must also have exactly three zero eigenvalues: two rigid translations and one rigid rotation move the triangle without straining it, so they store no energy.
""")
code(r"""
xy = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
Ke = element_stiffness(xy, D, T)
ev = np.linalg.eigvalsh(Ke)
print("symmetric:", np.allclose(Ke, Ke.T))
print("eigenvalues of K_e / max:", np.round(ev / ev.max(), 12))
""")

md(r"""
### Loads, supports and the reduced system

* **Loads.** A constant line load $\mathbf{q}$ (N/m) on a boundary edge of length $\ell$ gives each of its two end nodes the force $\mathbf{q}\,\ell/2$. For a traction $p$ on a plate of thickness $t$, $\mathbf{q} = (t\,p, 0)$.
* **Supports.** Clamped nodes have prescribed displacement $0$. Split the unknowns into free ($F$) and constrained ($C$):

$$
\begin{pmatrix}K_{FF} & K_{FC}\\ K_{CF} & K_{CC}\end{pmatrix}\begin{pmatrix}\mathbf{d}_F\\ \mathbf{d}_C\end{pmatrix} = \begin{pmatrix}\mathbf{f}_F\\ \mathbf{f}_C + \mathbf{r}_C\end{pmatrix}
\quad\Longrightarrow\quad
\underbrace{K_{FF}}_{A}\,\underbrace{\mathbf{d}_F}_{\mathbf{x}} = \underbrace{\mathbf{f}_F - K_{FC}\,\mathbf{d}_C}_{\mathbf{b}}.
$$

The support reactions $\mathbf{r}_C$ follow afterwards from the second block row.

**Why $A$ is SPD.** The stored energy is $\tfrac12\mathbf{d}^\top K\mathbf{d}\ge0$. On its own, $K$ is singular: rigid motions store no energy. Clamping removes every rigid motion, so $\mathbf{x}^\top A\mathbf{x}>0$ for every $\mathbf{x}\neq0$.
""")
code(r"""
def constant_edge_load(nodes, edges, q):
    # Nodal forces (length 2N) for a constant line load q = (qx, qy) [N/m] on the given edges.
    edges = np.asarray(edges)
    lengths = np.linalg.norm(nodes[edges[:, 1]] - nodes[edges[:, 0]], axis=1)
    forces = np.zeros_like(nodes)
    for end in (0, 1):
        np.add.at(forces, edges[:, end], lengths[:, None] * np.asarray(q, float) / 2)
    return forces.ravel()


def reduce_system(K, f, constrained, values):
    # Return A, b, free, d; afterwards fill d[free] with the solution of A x = b.
    c = np.asarray(constrained, dtype=int)
    free = np.setdiff1d(np.arange(f.size), c)
    d = np.zeros(f.size); d[c] = values
    return K[free][:, free], f[free] - K[free][:, c] @ values, free, d


def xy_dofs(node_ids):
    node_ids = np.asarray(node_ids)
    return np.column_stack([2 * node_ids, 2 * node_ids + 1]).ravel()
""")
md(r"""
### Structured mesh of a rectangle

Parts 2–5 use a regular grid: $n_x\times n_y$ square cells, each cut into two triangles along the bottom-left to top-right diagonal. This gives $(n_x+1)(n_y+1)$ nodes.
""")
code(r"""
def rectangle_mesh(Lx, Ly, nx, ny):
    xs, ys = np.linspace(0, Lx, nx + 1), np.linspace(0, Ly, ny + 1)
    X, Y = np.meshgrid(xs, ys)
    nodes = np.column_stack([X.ravel(), Y.ravel()])
    idx = lambda i, j: i + j * (nx + 1)
    tris = []
    for j in range(ny):
        for i in range(nx):
            n0, n1, n2, n3 = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            tris += [(n0, n1, n2), (n0, n2, n3)]
    side = {"left": np.array([idx(0, j) for j in range(ny + 1)]),
            "right": np.array([idx(nx, j) for j in range(ny + 1)])}
    return nodes, np.array(tris), side


def plate_case(nx, ny=None, *, Lx=1.0, Ly=1.0, support="clamp"):
    # Baseline plate. support='clamp': u = 0 on the left edge.
    # support='roller': u_x = 0 on the left edge and u_y = 0 at (0, 0) only (exact solution known).
    ny = nx if ny is None else ny
    nodes, tris, side = rectangle_mesh(Lx, Ly, nx, ny)
    K = assemble(nodes, tris, E, NU, T)
    right_edges = np.column_stack([side["right"][:-1], side["right"][1:]])
    f = constant_edge_load(nodes, right_edges, [T * P, 0.0])
    if support == "clamp":
        c = xy_dofs(side["left"])
    else:
        c = np.append(2 * side["left"], 2 * side["left"][0] + 1)
    c = np.sort(c)
    A, b, free, d = reduce_system(K, f, c, np.zeros(c.size))
    return dict(nodes=nodes, triangles=tris, side=side, K=K, f=f, constrained=c, free=free, d=d, A=A, b=b)
""")

# ---------------------------------------------------------------- 3. Small system
md(r"""
## 3. A small system you can inspect (report §4)

A $2\times2$-cell mesh has 9 nodes. The 3 left nodes are clamped, leaving $6$ free nodes and **12 unknowns**. At this size we can print $A$ and solve it with every direct method.
""")
code(r"""
small = plate_case(2)
A_s, b_s = small["A"].toarray(), small["b"]
print("unknowns:", len(b_s), "| stored nonzeros:", small["A"].nnz, "of", A_s.size)
print("symmetric:", np.allclose(A_s, A_s.T))
ev = eigvalsh(A_s)
print(f"lambda_min = {ev[0]:.4e}, lambda_max = {ev[-1]:.4e}  -> all positive: A is SPD")
print(f"condition number kappa_2 = lambda_max / lambda_min = {ev[-1] / ev[0]:.1f}")
print("\nb [N] (nonzero only at the loaded right-edge x-components):\n", b_s)
""")
code(r"""
fig, ax = plt.subplots(figsize=(4, 3.6))
ax.spy(A_s, markersize=7)
ax.set_title("Nonzero pattern of A (2x2 mesh, 12 unknowns)", fontsize=9)
save(fig, "structured_small_sparsity"); plt.show()
""")
code(r"""
x_direct = {
    "PA = LU":  lu_solve(lu_factor(A_s), b_s),
    "inverse":  inv(A_s) @ b_s,
    "Cholesky": cho_solve(cho_factor(A_s, lower=True), b_s),
}
nb = np.linalg.norm(b_s)
for name, x in x_direct.items():
    print(f"{name:9s} relative residual ||b - Ax|| / ||b|| = {np.linalg.norm(b_s - A_s @ x) / nb:.2e}")
d = small["d"].copy(); d[small["free"]] = x_direct["Cholesky"]
print("\nright-edge horizontal displacements [mm]:", d.reshape(-1, 2)[small["side"]["right"], 0] * 1e3)
""")

# ---------------------------------------------------------------- 4. Solvers
md(r"""
## 4. Solver comparison on a larger system (report §3–4)

A $20\times20$ mesh gives 840 unknowns. Every method uses the **same protocol**:

* the same $A$ and $\mathbf{b}$, starting guess $\mathbf{x}_0 = 0$;
* target: relative residual $\|\mathbf{b}-A\mathbf{x}_k\|/\|\mathbf{b}\| < 10^{-8}$;
* at most 20,000 iterations;
* each method's own (native) stopping status is recorded, and **separately** a solve is *accepted* only if the residual recomputed from the returned $\mathbf{x}$ is finite and below $10^{-8}$;
* timing is the best of 3 runs (timings depend on the machine; iteration counts do not).

| Method | Requirement on $A$ | Expectation here |
|---|---|---|
| Jacobi | $\rho(I - D_A^{-1}A) < 1$ | not guaranteed even for SPD |
| Damped Jacobi ($\omega = 0.5$) | $\omega < 2/\lambda_{\max}(D_A^{-1}A)$ | converges, slowly |
| Gauss–Seidel | SPD is sufficient | converges, slowly |
| Steepest descent (SD) | SPD | converges, rate set by $\kappa$ |
| Conjugate gradient (CG) | SPD | converges in $O(\sqrt{\kappa})$ iterations |
| CG with diagonal preconditioner (PCG) | SPD and SPD preconditioner | slightly faster than CG |
| MINRES | symmetric | works; it does not use positive definiteness |
| GMRES (no restart) | any nonsingular $A$ | works, but stores a growing basis |

($D_A$ is the diagonal of $A$.)
""")
code(r"""
TOL, CAP = 1e-8, 20_000
METHODS = ["Jacobi", "Damped Jacobi", "Gauss-Seidel", "SD", "CG", "PCG (diagonal)", "MINRES", "GMRES (full)"]


def iterative(A, b, method, *, cap=CAP, tol=TOL, history=True):
    # Zero initial guess. Returns x, iterations, status, residual history.
    # GMRES history is its internal (Arnoldi) residual estimate; its final residual is checked separately.
    x = np.zeros_like(b); nb = np.linalg.norm(b)
    hist = [1.0] if history else []
    count, last = 0, x.copy()

    class TargetReached(Exception):
        pass

    def monitor(xk):
        nonlocal count, last
        count += 1
        if method == "MINRES" or history:
            rr = float(np.linalg.norm(b - A @ xk) / nb)
            if history: hist.append(rr)
            if method == "MINRES" and rr < tol:      # MINRES stops on the shared true-residual target
                last = xk.copy(); raise TargetReached

    def arnoldi(res):
        nonlocal count
        count += 1
        if history: hist.append(float(res))

    if method in {"CG", "PCG (diagonal)"}:
        M = diags(1 / A.diagonal()) if method.startswith("PCG") else None
        x, info = cg(A, b, rtol=tol, atol=0, maxiter=cap, M=M, callback=monitor)
        status = f"native_info={info}"
    elif method == "GMRES (full)":
        x, info = gmres(A, b, rtol=tol, atol=0, restart=A.shape[0], maxiter=cap,
                        callback=arnoldi, callback_type="legacy")
        status = f"native_info={info}"
    elif method == "MINRES":
        try:
            x, info = minres(A, b, rtol=0, maxiter=cap, callback=monitor)
            status = f"native_info={info}"
        except TargetReached:
            x, status = last, "callback_target"
    else:
        Dg = A.diagonal()
        if method == "Gauss-Seidel":
            # x_{k+1} = L^{-1} (b - U x_k), L = lower triangle of A (incl. diagonal), U = strict upper triangle.
            # The triangular factor is prepared once; each step is then one sparse triangular solve.
            L = tril(A, format="csc"); U = (A - L).tocsr()
            Lsolve = splu(L, permc_spec="NATURAL", diag_pivot_thresh=0).solve
        r, status = b.copy(), "iteration cap"
        for count in range(1, cap + 1):
            if method == "Jacobi":          x += r / Dg
            elif method == "Damped Jacobi": x += 0.5 * r / Dg
            elif method == "Gauss-Seidel":  x = Lsolve(b - U @ x)
            elif method == "SD":            Ar = A @ r; x += ((r @ r) / (r @ Ar)) * r
            r = b - A @ x
            rr = float(np.linalg.norm(r) / nb)
            if history: hist.append(rr)
            if not np.isfinite(rr) or rr > 1e10: status = "diverged"; break
            if rr < tol: status = "target"; break
    return x, count, status, hist


def true_check(A, b, x):
    # Independent acceptance: residual recomputed from the returned x.
    rr = float(np.linalg.norm(b - A @ x) / np.linalg.norm(b))
    return rr, bool(np.isfinite(rr) and rr < TOL)
""")
md("Sanity check on a $2\\times2$ SPD system with a known answer. Every method must recover $\\mathbf{x} = (1,-2)$.")
code(r"""
A_t = csr_matrix([[4.0, 1.0], [1.0, 3.0]]); x_t = np.array([1.0, -2.0])
for m in METHODS:
    x, k, s, _ = iterative(A_t, A_t @ x_t, m, cap=2000)
    assert np.linalg.norm(x - x_t) < 1e-7, m
print("all methods recover the known solution")
""")
code(r"""
case = plate_case(20)
A, b = case["A"], case["b"]
lu = splu(A.tocsc()); x_ref = lu.solve(b)          # sparse direct reference solution
print(f"unknowns: {len(b)}, stored nonzeros: {A.nnz} ({100 * A.nnz / len(b)**2:.2f}% of the matrix)")
print(f"sparse LU reference: relative residual {np.linalg.norm(b - A @ x_ref) / np.linalg.norm(b):.1e}")

TIMING_RUNS = 3
rows, histories = [], {}
for m in METHODS:
    x, k, status, hist = iterative(A, b, m)
    histories[m] = hist
    times = []
    for _ in range(TIMING_RUNS):
        t0 = perf_counter(); iterative(A, b, m, history=False); times.append(perf_counter() - t0)
    rr, accepted = true_check(A, b, x)
    err = np.linalg.norm(x - x_ref) / np.linalg.norm(x_ref)
    rows.append((m, k, status, rr, accepted, err, min(times)))

print(f"\n{'method':16s} {'iterations':>10s} {'native status':>16s} {'true rel. residual':>18s} {'accepted':>9s} {'rel. error':>11s} {'best time [s]':>14s}")
for m, k, s, rr, acc, err, tm in rows:
    print(f"{m:16s} {k:10d} {s:>16s} {rr:18.2e} {str(acc):>9s} {err:11.2e} {tm:14.4f}")
""")
code(r"""
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), constrained_layout=True)
for name, hist in histories.items():
    for ax in axes:
        ax.semilogy(range(len(hist)), hist, label=name, lw=1)
for ax in axes:
    ax.axhline(TOL, color="black", ls="--", lw=0.8)
    ax.set_xlabel("iteration (GMRES: inner Arnoldi step)"); ax.set_ylabel(r"$\|b-Ax_k\|/\|b\|$"); ax.grid(alpha=0.2)
axes[0].set(xlim=(0, CAP), ylim=(1e-9, 1e11), title="Full iteration budget")
axes[1].set(xlim=(0, 350), ylim=(1e-9, 10), title="First 350 iterations")
axes[0].legend(fontsize=7, ncol=2)
save(fig, "structured_residual_histories"); plt.show()
""")
md(r"""
**Why Jacobi diverges although $A$ is SPD.** Jacobi converges exactly when the spectral radius $\rho(I - D_A^{-1}A) < 1$. Since $D_A^{-1}A$ is similar to the SPD matrix $S = D_A^{-1/2} A D_A^{-1/2}$, its eigenvalues are real and positive. So $\rho = \max(|1-\lambda_{\min}(S)|, |1-\lambda_{\max}(S)|)$, and Jacobi fails as soon as $\lambda_{\max}(S) > 2$.
""")
code(r"""
H = diags(1 / np.sqrt(A.diagonal()))
S = (H @ A @ H).tocsr()
s_lo = eigsh(S, k=1, which="SA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(b)))[0]
s_hi = eigsh(S, k=1, which="LA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(b)))[0]
print(f"lambda(S) in [{s_lo:.4f}, {s_hi:.4f}]")
print(f"Jacobi spectral radius rho = {max(abs(1 - s_lo), abs(1 - s_hi)):.4f}  (> 1: diverges)")
print(f"damped Jacobi converges for omega < 2 / lambda_max(S) = {2 / s_hi:.4f}  (we use 0.5)")
""")

# ---------------------------------------------------------------- 5. Refinement
md(r"""
## 5. Mesh refinement: conditioning and solver effort (report §4)

Halving the cell size $h$ should multiply the condition number by about 4 ($\kappa = O(h^{-2})$). Since CG needs $O(\sqrt{\kappa})$ iterations, its iteration count should roughly double each time.
""")
code(r"""
def extreme_eigs(A):
    # Smallest and largest algebraic eigenvalues (ARPACK, which="SA" / "LA"), as in the group benchmark.
    kw = dict(k=1, return_eigenvectors=False, tol=1e-10, v0=np.ones(A.shape[0]))
    return eigsh(A, which="SA", **kw)[0], eigsh(A, which="LA", **kw)[0]

refine = []
for n in (10, 20, 40):
    c_n = plate_case(n)
    lo, hi = extreme_eigs(c_n["A"])
    _, k_cg, _, _ = iterative(c_n["A"], c_n["b"], "CG", history=False)
    d_n = c_n["d"].copy(); d_n[c_n["free"]] = splu(c_n["A"].tocsc()).solve(c_n["b"])
    top_right = c_n["side"]["right"][-1]
    refine.append((n, len(c_n["b"]), c_n["A"].nnz, hi / lo, k_cg, d_n[2 * top_right] * 1e3))

print(f"{'cells':>6s} {'unknowns':>9s} {'nnz':>7s} {'kappa':>10s} {'CG its':>7s} {'u_x top-right [mm]':>19s}")
for r in refine:
    print(f"{r[0]:4d}^2 {r[1]:9d} {r[2]:7d} {r[3]:10.0f} {r[4]:7d} {r[5]:19.5f}")
print("kappa ratios:", [f"{refine[i+1][3] / refine[i][3]:.2f}" for i in range(2)],
      "| CG ratios:", [f"{refine[i+1][4] / refine[i][4]:.2f}" for i in range(2)])
""")
code(r"""
fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.2), constrained_layout=True)
ns = [r[1] for r in refine]
axes[0].loglog(ns, [r[3] for r in refine], "o-"); axes[0].set_ylabel(r"condition number $\kappa_2(A)$")
axes[1].loglog(ns, [r[4] for r in refine], "o-"); axes[1].set_ylabel("CG iterations to $10^{-8}$")
for ax in axes:
    ax.set_xlabel("free unknowns"); ax.grid(alpha=0.2, which="both")
save(fig, "structured_refinement"); plt.show()
""")

# ---------------------------------------------------------------- 6. Validation
md(r"""
## 6. Validation (report §4)

"All solvers agree" only shows that the *linear system* was solved correctly. To check the *model* we test:

1. **Equilibrium.** Support reactions plus applied loads must sum to zero force and zero moment.
2. **An exact solution.** With a roller support (only $u_x = 0$ on the left edge, plus $u_y = 0$ at one corner) the plate is in uniform tension. The exact displacement $u_x = p\,x/E$, $u_y = -\nu\,p\,y/E$ is linear, so linear triangles must reproduce it to rounding error.
3. **Sensitivity.** A relative perturbation of $10^{-6}$ in $\mathbf{b}$ may change $\mathbf{x}$ by at most $\kappa \cdot 10^{-6}$ (relative).
""")
code(r"""
def equilibrium(case, x):
    d = case["d"].copy(); d[case["free"]] = x
    r = case["K"] @ d - case["f"]                         # nonzero only at supports: the reactions
    reac = np.zeros_like(r); reac[case["constrained"]] = r[case["constrained"]]
    total = (reac + case["f"]).reshape(-1, 2)
    xy = case["nodes"]
    return d, total.sum(axis=0), float(np.sum(xy[:, 0] * total[:, 1] - xy[:, 1] * total[:, 0]))

d20, F_net, M_net = equilibrium(case, x_ref)
print(f"applied load: {case['f'].reshape(-1, 2).sum(axis=0)} N")
print(f"net force  (loads + reactions): {F_net} N")
print(f"net moment (loads + reactions): {M_net:.2e} N m")

roller = plate_case(6, 4, Lx=2.0, Ly=1.0, support="roller")
d_r = roller["d"].copy(); d_r[roller["free"]] = splu(roller["A"].tocsc()).solve(roller["b"])
exact = np.column_stack([P * roller["nodes"][:, 0] / E, -NU * P * roller["nodes"][:, 1] / E]).ravel()
print(f"\nroller test: relative error vs exact solution = {np.linalg.norm(d_r - exact) / np.linalg.norm(exact):.1e}")

rng = np.random.default_rng(2026)
db = rng.normal(size=len(b)); db *= 1e-6 * np.linalg.norm(b) / np.linalg.norm(db)
dx = lu.solve(b + db) - x_ref
lo20, hi20 = extreme_eigs(A)
print(f"\nperturbation: ||db||/||b|| = 1e-6 -> ||dx||/||x|| = {np.linalg.norm(dx) / np.linalg.norm(x_ref):.2e}"
      f"  (bound kappa * 1e-6 = {hi20 / lo20 * 1e-6:.2e})")
""")
code(r"""
def plot_deformed(ax, nodes, tris, d, scale, title):
    u = d.reshape(-1, 2)
    ax.triplot(nodes[:, 0], nodes[:, 1], tris, color="0.8", lw=0.4)
    tp = ax.tripcolor(*(nodes + scale * u).T, tris, np.linalg.norm(u, axis=1) * 1e3, shading="gouraud", cmap="viridis")
    ax.set_aspect("equal"); ax.set_title(title, fontsize=9); ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    return tp

fig, ax = plt.subplots(figsize=(5, 4))
tp = plot_deformed(ax, case["nodes"], case["triangles"], d20, 200, "20x20 plate, displacements x200 (grey: undeformed)")
fig.colorbar(tp, ax=ax, label="|u| [mm]")
save(fig, "structured_deformed_20x20"); plt.show()
print(f"maximum right-edge u_x = {d20.reshape(-1, 2)[case['side']['right'], 0].max() * 1e3:.4f} mm")
""")

# ---------------------------------------------------------------- 7. Other objects
md(r"""
## 7. Other objects and experiments (report §5–6)

> **Status and source.** This part implements the case specification of report §5 exactly as committed in the group repository: `draft/sections/05-objects-and-experiments/cases.json` at commit `2b23fd5` (merge of PR #7). It is embedded below so the notebook stays self-contained. The group has merged it as a working draft but has **not yet formally approved** the object selection. Results here are valid for this specification.

Three objects share the baseline material, thickness, clamp and traction:

* **S**: the unit square (control);
* **R**: a $2\times1$ m rectangle (the load is farther from the clamp);
* **H**: the unit square with a central $0.2\times0.2$ m opening.

Meshes come from **Triangle** (`p`: respect the boundary polygon, `q25`: minimum angle 25°, `a`: maximum triangle area). Boundary split points are inserted on the left and right edges, so the load patches and the partial clamp start and end exactly at nodes. These unstructured meshes are separate from the structured meshes of Parts 3–6, and their results should not be mixed with them.
""")
code("CASES_SOURCE = 'Pueblo98/NLA draft/sections/05-objects-and-experiments/cases.json @ 2b23fd5 (merged PR #7)'\n"
     "CASES = json.loads(r'''" + json.dumps(cases, indent=1) + "''')\n"
     "OBJECTS = {o['id']: o for o in CASES['objects']}\n"
     "AREAS = CASES['meshing']['max_triangle_area_m2']\n"
     "MID = CASES['meshing']['default_max_triangle_area_m2']\n"
     "print(CASES_SOURCE); print('status field:', CASES['status'])\n"
     "print({k: v['name'] for k, v in OBJECTS.items()}); print('max triangle areas:', AREAS)")
code(r"""
def polygon_with_splits(obj):
    # Outer boundary (CCW) with the left/right split points inserted, as a closed vertex loop.
    xl, xr = obj["left_x_m"], obj["right_x_m"]
    right = [(xr, y) for y in obj["right_boundary_splits_y_m"]]            # bottom to top
    left = [(xl, y) for y in obj["left_boundary_splits_y_m"]][::-1]        # top to bottom
    return np.array(right + left)


def mesh_object(obj, max_area, min_angle=25):
    outer = polygon_with_splits(obj)
    verts, segs = [outer], [np.column_stack([np.arange(len(outer)), np.roll(np.arange(len(outer)), -1)])]
    for hole in obj["holes_cw_m"]:
        h = np.array(hole); start = sum(len(v) for v in verts)
        verts.append(h); segs.append(start + np.column_stack([np.arange(len(h)), np.roll(np.arange(len(h)), -1)]))
    geom = dict(vertices=np.vstack(verts), segments=np.vstack(segs))
    if obj["hole_seeds_m"]:
        geom["holes"] = np.array(obj["hole_seeds_m"])
    m = tr.triangulate(geom, f"pq{min_angle}a{max_area}")
    nodes, tris = m["vertices"], m["triangles"]
    tris = np.where((signed_areas(nodes, tris) < 0)[:, None], tris[:, [0, 2, 1]], tris)   # orient CCW
    return nodes, tris


def signed_areas(nodes, tris):
    a = nodes[tris]
    return ((a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 2, 0] - a[:, 0, 0]) * (a[:, 1, 1] - a[:, 0, 1])) / 2


def boundary_edges(tris):
    e = np.sort(np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    uniq, counts = np.unique(e, axis=0, return_counts=True)
    return uniq[counts == 1]


def edge_connected(tris):
    # True if every triangle can be reached from the first one through shared edges.
    from scipy.sparse.csgraph import connected_components
    e = np.sort(np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    owner = np.tile(np.arange(len(tris)), 3)
    _, inv_idx = np.unique(e, axis=0, return_inverse=True)
    order = np.argsort(inv_idx, kind="stable"); s = inv_idx[order]
    pair = np.where(s[1:] == s[:-1])[0]
    i, j = owner[order][pair], owner[order][pair + 1]
    g = coo_matrix((np.ones(len(i)), (i, j)), shape=(len(tris), len(tris)))
    return connected_components(g, directed=False)[0] == 1


def mesh_checks(obj, nodes, tris):
    ar = signed_areas(nodes, tris)
    a = nodes[tris]; cent = a.mean(axis=1)
    in_hole = 0
    for hole in obj["holes_cw_m"]:
        h = np.array(hole)
        in_hole += np.sum((cent[:, 0] > h[:, 0].min()) & (cent[:, 0] < h[:, 0].max()) &
                          (cent[:, 1] > h[:, 1].min()) & (cent[:, 1] < h[:, 1].max()))
    ang = []
    for i in range(3):
        u, v = a[:, (i + 1) % 3] - a[:, i], a[:, (i + 2) % 3] - a[:, i]
        ang.append(np.degrees(np.arccos(np.clip(np.sum(u * v, 1) / np.linalg.norm(u, axis=1) / np.linalg.norm(v, axis=1), -1, 1))))
    return dict(nodes=len(nodes), triangles=len(tris), min_area_m2=float(ar.min()), material_area_m2=float(ar.sum()),
                centroids_in_hole=int(in_hole), min_angle_deg=float(np.min(ang)), edge_connected=bool(edge_connected(tris)))
""")
md(r"""
**Loads and supports on a general mesh.** A load *patch* is an interval $[y_0, y_1]$ of the right edge carrying total force $F$. Its traction is $F/(t\,(y_1-y_0))$, applied to the boundary edges inside the patch. A *clamp* fixes both components at every left-edge node with $y\in[y_0,y_1]$.

**Observables** (all linear functionals $w^\top\mathbf d$ of the displacement, in metres):
* `mean_right_ux`: the integral of $u_x$ over the whole right edge divided by its length, using exact integration of the piecewise-linear trace;
* `mid_ux`, `mid_uy`: both displacement components at the right-edge midpoint $(x_r, 0.5)$ m.

**Condition number.** $\kappa_2(A) = \lambda_{\max}/\lambda_{\min}$ of the supported (free–free), unscaled stiffness matrix $A$, the same definition as in Parts 3–5.
""")
code(r"""
def object_case(obj, nodes, tris, *, load_y=(0.0, 1.0), force=1e6, clamp_y=(0.0, 1.0)):
    xl, xr, tol = obj["left_x_m"], obj["right_x_m"], 1e-9
    K = assemble(nodes, tris, E, NU, T)
    be = boundary_edges(tris)
    on_right = np.all(np.abs(nodes[be][:, :, 0] - xr) < tol, axis=1)
    mid_y = nodes[be][:, :, 1].mean(axis=1)
    right_edges = be[on_right]
    patch = right_edges[(mid_y[on_right] > load_y[0]) & (mid_y[on_right] < load_y[1])]
    traction = force / (T * (load_y[1] - load_y[0]))
    f = constant_edge_load(nodes, patch, [T * traction, 0.0])
    clamp_nodes = np.where((np.abs(nodes[:, 0] - xl) < tol) & (nodes[:, 1] > clamp_y[0] - tol) & (nodes[:, 1] < clamp_y[1] + tol))[0]
    c = np.sort(xy_dofs(clamp_nodes))
    A, b, free, d = reduce_system(K, f, c, np.zeros(c.size))
    return dict(nodes=nodes, triangles=tris, K=K, f=f, constrained=c, free=free, d=d, A=A, b=b,
                right_edges=right_edges, clamp_nodes=clamp_nodes, traction=traction)


def observable_weights(obj, case):
    n, e = case["nodes"], case["right_edges"]
    L = np.linalg.norm(n[e[:, 1]] - n[e[:, 0]], axis=1)
    w_mean = np.zeros(2 * len(n))
    for end in (0, 1):
        np.add.at(w_mean, 2 * e[:, end], L / 2 / L.sum())      # exact for a piecewise-linear trace
    mid = np.argmin(np.linalg.norm(n - [obj["right_x_m"], 0.5], axis=1))
    assert np.allclose(n[mid], [obj["right_x_m"], 0.5]), "right-edge midpoint must be a mesh node"
    w_ux, w_uy = np.zeros(2 * len(n)), np.zeros(2 * len(n))
    w_ux[2 * mid], w_uy[2 * mid + 1] = 1.0, 1.0
    return {"mean_right_ux": w_mean, "mid_ux": w_ux, "mid_uy": w_uy}
""")
md(r"""
**Acceptance checks** (report §5, `proposed_acceptance`). Each check is recorded separately as `pass`, `FAIL` or `unverified`. A case counts as a validated result, and enters plots and conclusions, only if every check passes:

| Check | Metric | Threshold |
|---|---|---|
| structure | positive thickness, admissible $E,\nu$, all triangle areas $>0$, edge-connected solid, at least two distinct clamped nodes (removes all three rigid motions) | all true |
| symmetry | $\|A-A^\top\|_F/\|A\|_F$ | $\le 10^{-12}$ |
| positive definiteness | ≤ 2000 free unknowns: dense Cholesky succeeds. Otherwise: the smallest *algebraic* eigenpair (ARPACK `which="SA"`) has converged, its defect $\|Av-\lambda v\|/(\|A\|_\infty\|v\|) \le 10^{-8}$, and $\lambda > 10\,\|Av-\lambda v\|/\|v\|$. A non-converged or inconclusive diagnostic means **unverified**. | |
| reference residual | $\|b-Ax_{\rm ref}\|/\|b\|$, recomputed independently from the sparse-LU solution | $< 10^{-8}$ |
| supports | largest prescribed-displacement discrepancy | $\le 10^{-12}$ m |
| force balance | $\|\sum_i(\mathbf f_i+\mathbf r_i)\| / \sum_i\|\mathbf f_i\|$, reactions only at constrained components | $\le 10^{-8}$ |
| moment balance | about the origin: $|\sum_i x_i(f+r)_{y,i} - y_i(f+r)_{x,i}| / (L_{\rm char}\sum_i\|\mathbf f_i\|)$, $L_{\rm char}$ = bounding-box diagonal | $\le 10^{-8}$ |

**Algebraic uncertainty estimate.** For an observable $w^\top\mathbf x$ with weights restricted to the free unknowns, we estimate the effect of the algebraic error as $\|w\|_2\,\|b-Ax_{\rm ref}\|_2/\lambda_{\min}$. This is an *estimate, not a certified bound*: $\lambda_{\min}$ is itself an estimate, and assembly and modelling errors are not included. A successive-mesh difference at or below the **sum of both meshes' estimates** is reported as *unresolved*. If $\lambda_{\min}$ is not reliable, the estimate is marked unavailable.

**Solver protocol.** Every distinct linear system in Part 7 is solved with **all eight methods of Part 4 under the same protocol**: $x_0=0$, target $10^{-8}$, cap 20,000, native status recorded, acceptance by the independently recomputed residual, relative error against the sparse-LU reference, and best of 3 timings. Systems that are identical across studies (for example, the baseline case appears in the geometry, mesh, magnitude and support studies) are solved once, and the result is reused.
""")
code(r"""
FULL_PROTOCOL = True          # False: CG and PCG only (quick run; not the agreed Section 3 protocol)
PROTOCOL_METHODS = METHODS if FULL_PROTOCOL else ["CG", "PCG (diagonal)"]


def eig_end(A, which):
    # One end of the spectrum (ARPACK), with convergence and defect diagnostics. Never raises.
    try:
        lam, v = eigsh(A, k=1, which=which, tol=1e-10, v0=np.ones(A.shape[0]), maxiter=50 * A.shape[0])
    except ArpackNoConvergence:
        return dict(value=np.nan, converged=False, defect=np.nan, residual=np.nan)
    lam, v = float(lam[0]), v[:, 0]
    res = float(np.linalg.norm(A @ v - lam * v) / np.linalg.norm(v))
    return dict(value=lam, converged=True, defect=res / spnorm(A, np.inf), residual=res)


def acceptance(case, x):
    A, b, nodes, tris = case["A"], case["b"], case["nodes"], case["triangles"]
    st, val = {}, {}
    clamped_pts = len(np.unique(case["constrained"] // 2))
    struct_ok = (T > 0 and E > 0 and -1 < NU < 0.5 and signed_areas(nodes, tris).min() > 0
                 and edge_connected(tris) and clamped_pts >= 2)
    st["structure"] = "pass" if struct_ok else "FAIL"
    val["symmetry"] = spnorm(A - A.T, "fro") / spnorm(A, "fro")
    st["symmetry"] = "pass" if val["symmetry"] <= 1e-12 else "FAIL"
    lo = eig_end(A, "SA")
    val.update(lambda_min=lo["value"], lambda_min_converged=lo["converged"], lambda_min_defect=lo["defect"])
    lam_ok = lo["converged"] and lo["defect"] <= 1e-8 and lo["value"] > 10 * lo["residual"]
    lam_neg = lo["converged"] and lo["defect"] <= 1e-8 and lo["value"] < -10 * lo["residual"]
    if A.shape[0] <= 2000:
        try:
            cholesky(A.toarray()); st["spd"] = "pass"
        except LinAlgError:
            st["spd"] = "FAIL"
        val["spd_method"] = "dense Cholesky"
    else:
        st["spd"] = "pass" if lam_ok else "FAIL" if lam_neg else "unverified"
        val["spd_method"] = "smallest algebraic eigenpair (SA) diagnostic"
    val["lambda_min_reliable"] = bool(lam_ok)
    val["residual"] = np.linalg.norm(b - A @ x) / np.linalg.norm(b)
    st["residual"] = "pass" if np.isfinite(val["residual"]) and val["residual"] < 1e-8 else "FAIL"
    d, F_net, M_net = equilibrium(case, x)
    val["supports_m"] = float(np.abs(d[case["constrained"]]).max())
    st["supports"] = "pass" if val["supports_m"] <= 1e-12 else "FAIL"
    f_scale = np.linalg.norm(case["f"].reshape(-1, 2), axis=1).sum()
    lo_xy, hi_xy = nodes.min(axis=0), nodes.max(axis=0)
    val["force_balance"] = np.linalg.norm(F_net) / f_scale
    val["moment_balance"] = abs(M_net) / (np.linalg.norm(hi_xy - lo_xy) * f_scale)
    st["force_balance"] = "pass" if val["force_balance"] <= 1e-8 else "FAIL"
    st["moment_balance"] = "pass" if val["moment_balance"] <= 1e-8 else "FAIL"
    return d, dict(status=st, values=val, passed=all(v == "pass" for v in st.values()))


SOLVER_CACHE, SOLVER_ROWS = {}, []

def solver_protocol(A, b, x_ref, system_key):
    if system_key not in SOLVER_CACHE:
        out = {}
        for m in PROTOCOL_METHODS:
            times, runs = [], []
            for _ in range(TIMING_RUNS):
                t0 = perf_counter(); runs.append(iterative(A, b, m, history=False)); times.append(perf_counter() - t0)
            x, k, status, _ = runs[0]
            assert all(r[1] == k and r[2] == status for r in runs), "non-deterministic solver run"
            rr, accepted = true_check(A, b, x)
            out[m] = dict(method=m, iterations=k, native_status=status, true_relative_residual=rr, accepted=accepted,
                          relative_error_vs_lu=float(np.linalg.norm(x - x_ref) / np.linalg.norm(x_ref)),
                          best_seconds=min(times))
        SOLVER_CACHE[system_key] = out
    return SOLVER_CACHE[system_key]


RESULTS = []          # one record per solved case; exported in Part 8

def solve_object(obj, case, *, study, variant, area, system_key):
    A, b = case["A"], case["b"]
    x = splu(A.tocsc()).solve(b)                     # checked same-mesh LU reference
    d, acc = acceptance(case, x)
    W = observable_weights(obj, case)
    r_norm = np.linalg.norm(b - A @ x)
    v = acc["values"]
    rec = dict(case_id=f"{obj['id']}|{study}|{variant}|a={area:g}", object=obj["id"], object_name=obj["name"],
               study=study, variant=variant, max_triangle_area_m2=area, mesh_sha256=case["mesh_sha256"],
               nodes=len(case["nodes"]), triangles=len(case["triangles"]), free_unknowns=len(b), stored_nnz=A.nnz)
    for name, w in W.items():
        rec[name + "_m"] = float(w @ d)
        rec["unc_" + name + "_m"] = (float(np.linalg.norm(w[case["free"]]) * r_norm / v["lambda_min"])
                                     if v["lambda_min_reliable"] else np.nan)
    hi = eig_end(A, "LA")
    rec["lambda_min"], rec["lambda_max"] = v["lambda_min"], hi["value"]
    kappa_ok = v["lambda_min_reliable"] and hi["converged"] and hi["defect"] <= 1e-8
    rec["kappa_2"] = hi["value"] / v["lambda_min"] if kappa_ok else np.nan
    rec["kappa_status"] = "ok" if kappa_ok else "unavailable (eigenvalue diagnostic not reliable)"
    rec.update({f"check_{k}": s for k, s in acc["status"].items()})
    rec.update({f"value_{k}": s for k, s in v.items()})
    rec["passed_all_checks"] = acc["passed"]
    sol = solver_protocol(A, b, x, system_key)
    for m, r in sol.items():
        SOLVER_ROWS.append(dict(case_id=rec["case_id"], system_key=str(system_key), free_unknowns=len(b), **r))
    for m, tag in (("CG", "cg"), ("PCG (diagonal)", "pcg")):
        rec[f"{tag}_iterations"] = sol[m]["iterations"]
        rec[f"{tag}_native_status"] = sol[m]["native_status"]
        rec[f"{tag}_true_relative_residual"] = sol[m]["true_relative_residual"]
        rec[f"{tag}_accepted"] = sol[m]["accepted"]
    rec["all_protocol_methods_accepted"] = all(r["accepted"] for r in sol.values())
    RESULTS.append(rec)
    return d, rec

mm = lambda v: 1e3 * v
ok = lambda r: "pass" if r["passed_all_checks"] else "NOT ACCEPTED"
""")
md(r"""
### 7.1 Meshes

Triangle's output can differ slightly between platforms, even with the same version and options. To make the tables exactly reproducible, the meshes used are saved to `outputs/meshes/` with a SHA-256 fingerprint. When those files are present, they are reused. Set `REGENERATE_MESHES = True` to mesh again from the specification.
""")
code(r"""
REGENERATE_MESHES = False
MESH_DIR = OUT / "meshes"; MESH_DIR.mkdir(parents=True, exist_ok=True)

def mesh_hash(nodes, tris):
    return hashlib.sha256(np.ascontiguousarray(nodes, dtype=np.float64).tobytes()
                          + np.ascontiguousarray(tris, dtype=np.int64).tobytes()).hexdigest()

meshes, mesh_rows = {}, []
for oid, obj in OBJECTS.items():
    for a in AREAS:
        path = MESH_DIR / f"{oid}_a{a:g}.npz"
        if path.exists() and not REGENERATE_MESHES:
            z = np.load(path); nodes, tris, source = z["nodes"], z["triangles"].astype(np.int64), "snapshot"
        else:
            nodes, tris = mesh_object(obj, a); tris = tris.astype(np.int64); source = "generated by Triangle"
            np.savez_compressed(path, nodes=nodes, triangles=tris)
        meshes[oid, a] = (nodes, tris)
        chk = mesh_checks(obj, nodes, tris)
        mesh_rows.append(dict(object=oid, max_triangle_area_m2=a, source=source, file=path.name,
                              sha256=mesh_hash(nodes, tris), **chk))
        print(f"{oid} area<={a:<9g} nodes {chk['nodes']:5d} triangles {chk['triangles']:5d} "
              f"material area {chk['material_area_m2']:.4f} m^2  min angle {chk['min_angle_deg']:.1f} deg  "
              f"hole centroids {chk['centroids_in_hole']}  connected {chk['edge_connected']}  "
              f"[{source}, sha256 {mesh_rows[-1]['sha256'][:12]}]")
        assert chk["min_area_m2"] > 0 and chk["centroids_in_hole"] == 0 and chk["edge_connected"]
MESH_SHA = {(r["object"], r["max_triangle_area_m2"]): r["sha256"] for r in mesh_rows}

def make_case(oid, a, **kw):
    cs = object_case(OBJECTS[oid], *meshes[oid, a], **kw)
    cs["mesh_sha256"] = MESH_SHA[oid, a]
    return cs

fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), gridspec_kw=dict(width_ratios=[1, 2, 1]), constrained_layout=True)
for ax, oid in zip(axes, OBJECTS):
    nodes, tris = meshes[oid, MID]
    ax.triplot(nodes[:, 0], nodes[:, 1], tris, lw=0.4, color="0.3")
    ax.set_aspect("equal"); ax.set_title(f"{OBJECTS[oid]['name']} (area <= {MID} m^2)", fontsize=9)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
save(fig, "objects_meshes"); plt.show()
""")
md(r"""
### 7.2 Geometry study

Baseline load and clamp, middle mesh. This compares deformation and solver effort across the three shapes.
""")
code(r"""
F0 = CASES["baseline"]["total_force_N"][0]
FULL_EDGE, FULL_CLAMP = (0.0, 1.0), (0.0, 1.0)
base = {}
for oid, obj in OBJECTS.items():
    cs = make_case(oid, MID)
    d, rec = solve_object(obj, cs, study="geometry", variant="baseline", area=MID,
                          system_key=(oid, MID, FULL_EDGE, 1.0, FULL_CLAMP))
    base[oid] = (cs, d, rec)

print(f"{'object':28s} {'unknowns':>8s} {'kappa_2':>9s} {'mean u_x right [mm]':>20s} {'mid u_x [mm]':>12s} {'mid u_y [mm]':>12s}  checks")
for oid, (cs, d, r) in base.items():
    print(f"{r['object_name']:28s} {r['free_unknowns']:8d} {r['kappa_2']:9.0f} "
          f"{mm(r['mean_right_ux_m']):20.5f} {mm(r['mid_ux_m']):12.5f} {mm(r['mid_uy_m']):12.2e}  {ok(r)}")

print(f"\nSolver protocol (Part 4 rules) on each object, middle mesh:")
print(f"{'method':16s} " + " ".join(f"{oid + ' its':>9s} {'status':>16s} {'acc.':>5s} {'time [s]':>8s}" for oid in OBJECTS))
for m in PROTOCOL_METHODS:
    cells = []
    for oid in OBJECTS:
        r = SOLVER_CACHE[oid, MID, FULL_EDGE, 1.0, FULL_CLAMP][m]
        cells.append(f"{r['iterations']:9d} {r['native_status']:>16s} {('yes' if r['accepted'] else 'NO'):>5s} {r['best_seconds']:8.3f}")
    print(f"{m:16s} " + " ".join(cells))
""")
code(r"""
fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), gridspec_kw=dict(width_ratios=[1, 2, 1]), constrained_layout=True)
accepted = [(oid, v) for oid, v in base.items() if v[2]["passed_all_checks"]]
vmax = max((np.linalg.norm(d.reshape(-1, 2), axis=1).max() for _, (_, d, _) in accepted), default=1e-3) * 1e3
tp = None
for ax, (oid, (cs, d, r)) in zip(axes, base.items()):
    if r["passed_all_checks"]:
        tp = plot_deformed(ax, cs["nodes"], cs["triangles"], d, 200, f"{r['object_name']}, displacements x200")
        tp.set_clim(0, vmax)
    else:
        ax.text(0.5, 0.5, "not accepted:\nnot plotted", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
if tp is not None:
    fig.colorbar(tp, ax=axes, label="|u| [mm]")
save(fig, "objects_deformed"); plt.show()
""")
md(r"""
### 7.3 Mesh study

The same physical case on three meshes per object. Meshes are not nested, so we report the **successive differences** of each observable, signed and absolute, in metres. These measure mesh dependence, not the error against an exact solution, so no convergence rate is inferred. A difference is only classified if both meshes' cases pass every check; otherwise it is *unverified*.
""")
code(r"""
mesh_study = {}
for oid, obj in OBJECTS.items():
    for a in AREAS:
        cs = make_case(oid, a)
        _, mesh_study[oid, a] = solve_object(obj, cs, study="mesh", variant="baseline", area=a,
                                             system_key=(oid, a, FULL_EDGE, 1.0, FULL_CLAMP))

OBS = ["mean_right_ux", "mid_ux", "mid_uy"]
diff_rows = []
for oid in OBJECTS:
    for a0, a1 in zip(AREAS[:-1], AREAS[1:]):
        r0, r1 = mesh_study[oid, a0], mesh_study[oid, a1]
        for n in OBS:
            signed = r1[n + "_m"] - r0[n + "_m"]
            est = r0["unc_" + n + "_m"] + r1["unc_" + n + "_m"]
            both_ok = r0["passed_all_checks"] and r1["passed_all_checks"]
            status = ("unverified" if not np.isfinite(est) or not both_ok
                      else "unresolved" if abs(signed) <= est else "resolved")
            diff_rows.append(dict(object=oid, area_from_m2=a0, area_to_m2=a1, observable=n,
                                  value_from_m=r0[n + "_m"], value_to_m=r1[n + "_m"], signed_difference_m=signed,
                                  abs_difference_m=abs(signed), summed_algebraic_estimate_m=est, status=status))

print(f"{'obj':3s} {'area':>9s} {'unknowns':>8s} {'kappa_2':>8s} {'CG':>4s} {'GS':>6s}  " + "  ".join(f"{n + ' [mm]':>18s}" for n in OBS) + "  checks")
for oid in OBJECTS:
    for a in AREAS:
        r = mesh_study[oid, a]
        gs = SOLVER_CACHE[oid, a, FULL_EDGE, 1.0, FULL_CLAMP].get("Gauss-Seidel")
        gs_txt = f"{gs['iterations']:6d}" if gs else f"{'-':>6s}"
        print(f"{oid:3s} {a:9g} {r['free_unknowns']:8d} {r['kappa_2']:8.0f} {r['cg_iterations']:4d} {gs_txt}  "
              + "  ".join(f"{mm(r[n + '_m']):18.6f}" for n in OBS) + f"  {ok(r)}")
print(f"\n{'obj':3s} {'areas':>20s} {'observable':>14s} {'signed diff [m]':>16s} {'summed estimate [m]':>20s}  status")
for row in diff_rows:
    areas = f"{row['area_from_m2']:g} -> {row['area_to_m2']:g}"
    print(f"{row['object']:3s} {areas:>20s} {row['observable']:>14s} "
          f"{row['signed_difference_m']:16.3e} {row['summed_algebraic_estimate_m']:20.1e}  {row['status']}")
""")
md(r"""
### 7.4 Load magnitude, load location and supports

* **Magnitude:** $0.5F_0$, $F_0$, $1.5F_0$ on the same mesh. In a linear model the displacement must scale exactly with the load. This checks linearity on a fixed matrix, not sensitivity.
* **Location:** the same total force $F_0$ on a lower, middle or upper patch of the right edge, each 0.25 m high (traction 400 MPa).
* **Supports:** the full left clamp vs. a central half-clamp ($y\in[0.25,0.75]$).
""")
code(r"""
print("Magnitude study (mean right-edge u_x [mm]; ratio to the F0 case)")
for oid, obj in OBJECTS.items():
    vals = {}
    for fac in CASES["studies"]["magnitude"]["force_factors"]:
        cs = make_case(oid, MID, force=fac * F0)
        _, r = solve_object(obj, cs, study="magnitude", variant=f"{fac:g}F0", area=MID,
                            system_key=(oid, MID, FULL_EDGE, fac, FULL_CLAMP))
        vals[fac] = (mm(r["mean_right_ux_m"]), r["passed_all_checks"])
    print(f"  {oid}: " + "  ".join(f"{fac:g}F0 -> {v:.5f} ({v / vals[1][0]:.6f}){'' if okk else ' NOT ACCEPTED'}"
                                   for fac, (v, okk) in vals.items()))

print("\nLocation study (same total force on a 0.25 m patch)")
print(f"  {'obj':3s} {'patch y [m]':>14s} {'mean u_x right [mm]':>20s} {'mid u_x [mm]':>12s} {'mid u_y [mm]':>12s} {'CG':>5s}  checks")
for oid, obj in OBJECTS.items():
    for y0, y1 in CASES["studies"]["location"]["right_edge_intervals_y_m"]:
        cs = make_case(oid, MID, load_y=(y0, y1))
        _, r = solve_object(obj, cs, study="location", variant=f"y=[{y0:g},{y1:g}]", area=MID,
                            system_key=(oid, MID, (y0, y1), 1.0, FULL_CLAMP))
        print(f"  {oid:3s} {f'[{y0:g}, {y1:g}]':>14s} {mm(r['mean_right_ux_m']):20.5f} {mm(r['mid_ux_m']):12.5f} "
              f"{mm(r['mid_uy_m']):12.5f} {r['cg_iterations']:5d}  {ok(r)}")

print("\nSupport study (full-edge load)")
print(f"  {'obj':3s} {'clamp y [m]':>12s} {'unknowns':>8s} {'mean u_x right [mm]':>20s} {'mid u_y [mm]':>12s} {'kappa_2':>9s} {'CG':>5s}  checks")
for oid, obj in OBJECTS.items():
    for y0, y1 in CASES["studies"]["supports"]["left_clamp_intervals_y_m"]:
        cs = make_case(oid, MID, clamp_y=(y0, y1))
        _, r = solve_object(obj, cs, study="supports", variant=f"clamp y=[{y0:g},{y1:g}]", area=MID,
                            system_key=(oid, MID, FULL_EDGE, 1.0, (y0, y1)))
        print(f"  {oid:3s} {f'[{y0:g}, {y1:g}]':>12s} {r['free_unknowns']:8d} {mm(r['mean_right_ux_m']):20.5f} "
              f"{mm(r['mid_uy_m']):12.5f} {r['kappa_2']:9.0f} {r['cg_iterations']:5d}  {ok(r)}")
""")
md("### 7.5 Acceptance and solver summary\n\nEvery case solved in Part 7, with each check recorded separately, followed by the solver protocol for every distinct system.")
code(r"""
CHECKS = ["structure", "symmetry", "spd", "residual", "supports", "force_balance", "moment_balance"]
print(f"{'case':42s} " + " ".join(f"{c[:10]:>10s}" for c in CHECKS) + f" {'residual':>9s} {'force':>8s} {'moment':>8s}")
for r in RESULTS:
    print(f"{r['case_id']:42s} " + " ".join(f"{r['check_' + c]:>10s}" for c in CHECKS)
          + f" {r['value_residual']:9.1e} {r['value_force_balance']:8.1e} {r['value_moment_balance']:8.1e}")
n_pass = sum(r["passed_all_checks"] for r in RESULTS)
n_unverified = sum(any(r["check_" + c] == "unverified" for c in CHECKS) for r in RESULTS)
print(f"\n{n_pass} of {len(RESULTS)} cases pass every check ({n_unverified} with an unverified check)")

print(f"\nIterations per method for each distinct system ({len(SOLVER_CACHE)} systems); '*' = not accepted by the true-residual check")
print(f"{'system (object, area, load patch, load factor, clamp)':58s} " + " ".join(f"{m[:9]:>9s}" for m in PROTOCOL_METHODS))
for key, sol in SOLVER_CACHE.items():
    print(f"{str(key):58s} " + " ".join(f"{sol[m]['iterations']:8d}{'' if sol[m]['accepted'] else '*'}" + (" " if sol[m]['accepted'] else "")
                                        for m in PROTOCOL_METHODS))
""")

# ---------------------------------------------------------------- export
md(r"""
## 8. Exported results

Every table and figure above is written to `outputs/` next to this notebook, so the report can cite a traceable source:

* `outputs/results/objects_cases.csv`: one row per Part 7 case (case ID, mesh fingerprint and size, observables in metres, algebraic estimates, λ and κ with status, CG/PCG status and acceptance, every acceptance check with its value);
* `outputs/results/objects_solvers.csv`: the full solver protocol (8 methods) for every case: iterations, native status, true residual, accepted, error against LU, best time;
* `outputs/results/objects_mesh_differences.csv`: successive-mesh differences (signed and absolute) with resolved, unresolved or unverified status;
* `outputs/results/objects_meshes.csv` and `outputs/meshes/*.npz`: the exact meshes used (nodes, triangles), with SHA-256 fingerprints;
* `outputs/results/structured_solvers.csv`, `structured_refinement.csv`, `structured_validation.json`: Parts 3–6 (structured meshes; keep them separate from Part 7);
* `outputs/results/manifest.json`: environment, the specification source, observable and κ definitions, thresholds, protocol and outcome counts;
* `outputs/figures/*.png`.
""")
code(r"""
import csv
def write_csv(path, rows):
    with open(path, "w", newline="") as fh:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)

RES = OUT / "results"
write_csv(RES / "objects_cases.csv", RESULTS)
write_csv(RES / "objects_solvers.csv", SOLVER_ROWS)
write_csv(RES / "objects_mesh_differences.csv", diff_rows)
write_csv(RES / "objects_meshes.csv", mesh_rows)
write_csv(RES / "structured_solvers.csv",
          [dict(method=m, iterations=k, native_status=s, true_relative_residual=rr, accepted=acc, relative_error_vs_lu=err,
                best_seconds=tm, mesh="20x20 structured", free_unknowns=len(b)) for m, k, s, rr, acc, err, tm in rows])
write_csv(RES / "structured_refinement.csv",
          [dict(cells=f"{r[0]}x{r[0]}", free_unknowns=r[1], stored_nnz=r[2], kappa_2=r[3], cg_iterations=r[4],
                top_right_ux_mm=r[5]) for r in refine])
(RES / "structured_validation.json").write_text(json.dumps(dict(
    small_2x2=dict(unknowns=len(b_s), kappa_2=float(ev[-1] / ev[0])),
    net_force_N=F_net.tolist(), net_moment_Nm=M_net,
    roller_relative_error=float(np.linalg.norm(d_r - exact) / np.linalg.norm(exact)),
    perturbation=dict(relative_load=1e-6, relative_displacement=float(np.linalg.norm(dx) / np.linalg.norm(x_ref)), seed=2026),
    jacobi_spectral_radius=float(max(abs(1 - s_lo), abs(1 - s_hi)))), indent=2))
manifest = dict(
    specification_source=CASES_SOURCE, specification_status_field=CASES["status"],
    environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                     matplotlib=matplotlib.__version__, triangle=str(getattr(tr, "__version__", "")), platform=platform.platform()),
    material=dict(E_Pa=E, nu=NU, thickness_m=T, model="plane stress"),
    meshes=dict(source="outputs/meshes/*.npz (see objects_meshes.csv for SHA-256)",
                note="Triangle output can differ across platforms; the saved meshes are the ones behind every Part 7 number"),
    observables=dict(mean_right_ux="integral of u_x over the whole right edge / its length (exact for the piecewise-linear trace), metres",
                     mid_ux="u_x at the right-edge midpoint (x_r, 0.5), metres",
                     mid_uy="u_y at the right-edge midpoint (x_r, 0.5), metres"),
    condition_number="kappa_2 = lambda_max / lambda_min of the supported (free-free), unscaled stiffness matrix A; "
                     "ARPACK which='LA' and which='SA'; reported only when both eigenpairs converged with defect <= 1e-8",
    algebraic_estimate="||w_free||_2 ||b - A x_ref||_2 / lambda_min_est; an estimate, not a certified bound; a successive difference "
                       "<= the sum of both meshes' estimates is 'unresolved'",
    solver_protocol=dict(methods=PROTOCOL_METHODS, full_protocol=FULL_PROTOCOL, tolerance=TOL, iteration_cap=CAP, x0="zero",
                         acceptance="independently recomputed relative residual finite and < 1e-8; native status recorded separately",
                         timing=f"best of {TIMING_RUNS} runs; machine dependent", reuse="identical systems solved once"),
    acceptance_thresholds=CASES["proposed_acceptance"],
    outcomes=dict(cases_total=len(RESULTS), cases_passing_all_checks=int(n_pass), cases_with_unverified_check=int(n_unverified),
                  distinct_systems=len(SOLVER_CACHE),
                  solver_runs_accepted=int(sum(r["accepted"] for s in SOLVER_CACHE.values() for r in s.values())),
                  solver_runs_total=int(sum(len(s) for s in SOLVER_CACHE.values()))))
(RES / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
for p in sorted(OUT.rglob("*.*")):
    print(p, p.stat().st_size, "bytes")
""")

# ---------------------------------------------------------------- summary
md(r"""
## 9. Summary

**Structured square (Parts 3–6).** The supported stiffness matrix $A$ is sparse, symmetric and positive definite, as the energy argument predicts, and its condition number grows like $h^{-2}$. The direct methods solve the small system to rounding accuracy. On the larger system, the Krylov methods (CG, PCG, MINRES, GMRES) reach the target in a few hundred iterations, while Gauss–Seidel needs tens of thousands. Steepest descent and damped Jacobi stop at the iteration cap. Positive definiteness does **not** guarantee that Jacobi converges: its iteration matrix has spectral radius above 1. Equilibrium and an exact linear solution confirm that the model is assembled correctly, not just that the linear system was solved.

**Other objects (Part 7).** The cell below derives every Part 7 statement from the exported records. A comparison is printed only when all the cases it uses pass every acceptance check.
""")
code(r"""
acc_cases = [r for r in RESULTS if r["passed_all_checks"]]
print(f"Acceptance: {len(acc_cases)} of {len(RESULTS)} cases pass every check; "
      f"{manifest['outcomes']['solver_runs_accepted']} of {manifest['outcomes']['solver_runs_total']} solver runs reach the target "
      f"(by the true residual) within the cap.\n")
g = {r["object"]: r for r in RESULTS if r["study"] == "geometry"}
def both_ok(*rs): return all(r["passed_all_checks"] for r in rs)
for o in ("R", "H"):
    if both_ok(g[o], g["S"]):
        print(f"{o} vs S (same mesh-area limit {MID}): mean right-edge u_x x{g[o]['mean_right_ux_m'] / g['S']['mean_right_ux_m']:.3f}, "
              f"kappa_2 x{g[o]['kappa_2'] / g['S']['kappa_2']:.2f}")
    else:
        print(f"{o} vs S: not reported (a case failed acceptance)")
for oid in OBJECTS:
    d_last = [r for r in diff_rows if r["object"] == oid and r["observable"] == "mean_right_ux"][-1]
    if d_last["status"] == "unverified":
        print(f"{oid}: last mesh step not reported (unverified)")
    else:
        print(f"{oid}: last mesh step changes mean right-edge u_x by {d_last['abs_difference_m']:.2e} m "
              f"({100 * d_last['abs_difference_m'] / abs(d_last['value_to_m']):.3f}% of its value); {d_last['status']}")
sup = {(r["object"], r["variant"]): r for r in RESULTS if r["study"] == "supports"}
for oid in OBJECTS:
    full, half = sup[oid, "clamp y=[0,1]"], sup[oid, "clamp y=[0.25,0.75]"]
    if both_ok(full, half):
        print(f"{oid}: half clamp vs full clamp: mean u_x x{half['mean_right_ux_m'] / full['mean_right_ux_m']:.3f}, "
              f"kappa_2 x{half['kappa_2'] / full['kappa_2']:.2f}")
mag = [r for r in RESULTS if r["study"] == "magnitude"]
if both_ok(*mag):
    lin = max(abs(r["mean_right_ux_m"] / g[r["object"]]["mean_right_ux_m"] - float(r["variant"][:-2])) for r in mag)
    print(f"linearity: largest deviation of u(cF0)/u(F0) from c = {lin:.1e}")
print("\nInterpretation notes:")
print("* The square with an opening changes more between meshes than S or R. This is consistent with stress concentrating at its")
print("  re-entrant corners, but the measurements alone neither prove that cause nor give a convergence rate.")
print("* u_y at the right-edge midpoint is close to zero by symmetry for S and H, and of the same order as its mesh-to-mesh")
print("  changes. It should not be interpreted as a physical result.")
""")
md(r"""
## Code provenance and AI use

The finite-element assembly, load/support handling and solver protocol in this notebook are self-contained copies of the group repository's `fem/elasticity.py`, `fem/plate.py`, `solvers/system_tools.py` and `solvers/progress_benchmark.py`. The only change is that the Gauss–Seidel triangular solve is prepared once with a sparse factorisation. It gives the same iterates and iteration counts, much faster. The Part 7 case specification and acceptance criteria come from report §5 (`cases.json` @ `2b23fd5`). Library routines: SciPy (sparse LU, CG, GMRES, MINRES, ARPACK eigenvalues) and Triangle by J. R. Shewchuk, via the `triangle` Python package (meshing). AI assistance was used in writing this code. See the AI-use statement in the report.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"}})
nbf.write(nb, out_path)
print("wrote", out_path, "with", len(cells), "cells")
