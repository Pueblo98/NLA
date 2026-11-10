"""Section 4 square demonstration: fresh numbers and figures.

Run from the repository root:  python3 draft/experiments/square.py

Case: fem/plate.py:force_driven -- 1 m x 1 m plate, E = 200 GPa, nu = 0.3,
t = 0.01 m, plane stress, left edge clamped, uniform traction (p, 0) with
p = 100 MPa on the right edge, top/bottom traction-free, structured mesh with
each cell cut bottom-left -> top-right.

Protocol (common brief / Section 3): same A, b; x0 = 0; acceptance on the
recomputed eta(x) = ||b - A x|| / ||b|| < 1e-8; cap 20,000; Jacobi divergence
guard 1e10; methods from solvers/progress_benchmark.iterative; sparse LU
reference (splu), factorization and solve timed separately; best of 3 timed
runs with histories recorded in a separate run; kappa_2 from eigsh (LA and
shift-invert sigma = 0, tol 1e-10); rho_J = max |1 - lambda(S)|.

Outputs (draft/experiments/results/square/):
  small.json, small_A.csv, small_A_integer.csv, small_b.csv, small_x.csv
  solvers.json, solver_comparison.csv, histories.json
  validation.json, refinement.json, square.log
Figures (draft/sections/04-square-example/figures/, PDF + PNG):
  square_setup (schematic, 2x2 numbering, deformed 20x20), square_residuals
"""
from pathlib import Path
import csv
import json
import platform
import sys
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import cho_factor, cho_solve, eigvalsh, inv, lu_factor, lu_solve
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh, splu

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "solvers"))
sys.path.insert(0, str(ROOT / "fem"))
import progress_benchmark as pb  # noqa: E402
from plate import force_driven  # noqa: E402

OUT = ROOT / "draft" / "experiments" / "results" / "square"
FIG = ROOT / "draft" / "sections" / "04-square-example" / "figures"
E, NU, T, P, L = 200e9, 0.3, 0.01, 100e6, 1.0
TOL, CAP = pb.TOL, pb.CAP
SCALE = 200          # displacement amplification in the deformed view
LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(msg)


def eta(A, b, x):
    return float(np.linalg.norm(b - A @ x) / np.linalg.norm(b))


def best_of_3(fn):
    times, out = [], None
    for _ in range(3):
        t0 = perf_counter()
        out = fn()
        times.append(perf_counter() - t0)
    return min(times), times, out


def extreme_eigs(A, tol=1e-10):
    """Protocol estimator; also returns the eigen-equation residuals."""
    A = A.tocsc()
    v0 = np.ones(A.shape[0])
    hi, vhi = eigsh(A, k=1, which="LA", tol=tol, v0=v0)
    lo, vlo = eigsh(A, k=1, sigma=0, which="LM", tol=tol, v0=v0)
    res = lambda lam, v: float(np.linalg.norm(A @ v[:, 0] - lam[0] * v[:, 0])  # noqa: E731
                               / (abs(lam[0]) * np.linalg.norm(v[:, 0])))
    return float(lo[0]), float(hi[0]), res(lo, vlo), res(hi, vhi)


def jacobi_matrix(A):
    H = diags(1 / np.sqrt(A.diagonal()))
    return (H @ A @ H).tocsr()


def full_solution(s, x):
    d = s["d"].copy()
    d[s["free"]] = x
    return d


def balance(s, d):
    """Reactions from Eq. (mechanics-reactions) and total force/moment imbalance."""
    r = s["K"] @ d - s["f"]
    c = s["constrained"]
    reac = np.zeros_like(r)
    reac[c] = r[c]
    total = (reac + s["f"]).reshape(-1, 2)
    xy = s["nodes"]
    fz = s["f"].reshape(-1, 2)
    rz = reac.reshape(-1, 2)
    moment = lambda F: float(np.sum(xy[:, 0] * F[:, 1] - xy[:, 1] * F[:, 0]))  # noqa: E731
    return dict(applied_force_N=fz.sum(axis=0).tolist(),
                reaction_force_N=rz.sum(axis=0).tolist(),
                force_imbalance_N=total.sum(axis=0).tolist(),
                applied_moment_Nm=moment(fz), reaction_moment_Nm=moment(rz),
                moment_imbalance_Nm=moment(total),
                free_row_residual_max_N=float(np.abs(r[s["free"]]).max()))


# --------------------------------------------------------------------------
def small_system():
    s = force_driven(2)
    A, b = s["A"].toarray(), s["b"]
    scale = E * T / (40 * (1 - NU**2))       # A = scale * integer matrix for nu = 0.3
    Aint = A / scale
    assert np.abs(Aint - np.round(Aint)).max() < 1e-9
    Aint = np.round(Aint).astype(int)
    ev = eigvalsh(A)
    lu = lu_factor(A)
    cho = cho_factor(A, lower=True)
    xs = {"PA=LU": lu_solve(lu, b), "explicit inverse": inv(A) @ b,
          "Cholesky": cho_solve(cho, b)}
    res = {k: eta(A, b, v) for k, v in xs.items()}
    spread = max(np.linalg.norm(xs[a] - xs[c]) for a in xs for c in xs) / np.linalg.norm(xs["Cholesky"])
    d = full_solution(s, xs["Cholesky"])
    U = d.reshape(-1, 2)
    right = s["side"]["right"]
    free_nodes = sorted(set((s["free"] // 2).tolist()))
    bal = balance(s, d)
    small = dict(cells_per_side=2, nodes=len(s["nodes"]), triangles=len(s["triangles"]),
                 full_dofs=len(s["f"]), unknowns=len(b), stored_nnz=int(s["A"].nnz),
                 numeric_nnz=int(np.count_nonzero(Aint)),
                 free_nodes=free_nodes, free_node_xy=s["nodes"][free_nodes].tolist(),
                 free_dofs=s["free"].tolist(), b_N=b.tolist(),
                 integer_scale_N_per_m=scale, integer_matrix=Aint.tolist(),
                 symmetry_max_abs=float(np.abs(A - A.T).max()),
                 eigenvalues_N_per_m=ev.tolist(), lambda_min=float(ev[0]),
                 lambda_max=float(ev[-1]), kappa2=float(ev[-1] / ev[0]),
                 relative_residuals=res, max_relative_difference=float(spread),
                 right_edge_nodes=right.tolist(),
                 right_edge_ux_mm=(U[right, 0] * 1e3).tolist(),
                 right_edge_uy_mm=(U[right, 1] * 1e3).tolist(),
                 pL_over_E_mm=P * L / E * 1e3, balance=bal)
    np.savetxt(OUT / "small_A.csv", A, delimiter=",", fmt="%.17g")
    np.savetxt(OUT / "small_A_integer.csv", Aint, delimiter=",", fmt="%d")
    np.savetxt(OUT / "small_b.csv", b, delimiter=",", fmt="%.17g")
    np.savetxt(OUT / "small_x.csv", xs["Cholesky"], delimiter=",", fmt="%.17g")
    (OUT / "small.json").write_text(json.dumps(small, indent=2) + "\n")
    log(f"small: n={len(b)} kappa={small['kappa2']:.4f} lam=[{ev[0]:.4e},{ev[-1]:.4e}] "
        f"res={res} ux_right_mm={np.round(U[right, 0]*1e3, 4)} uy={np.round(U[right, 1]*1e3, 4)}")
    return s, small


# --------------------------------------------------------------------------
def benchmark():
    s = force_driven(20)
    A, b = s["A"].tocsr(), s["b"]
    n = len(b)
    Ac = A.tocsc()
    tf, tfs, lu = best_of_3(lambda: splu(Ac))
    ts, tss, ref = best_of_3(lambda: lu.solve(b))
    lo, hi, rlo, rhi = extreme_eigs(A)
    S = jacobi_matrix(A)
    slo, shi, _, _ = extreme_eigs(S)
    ev_dense = eigvalsh(A.toarray())
    evS_dense = eigvalsh(S.toarray())
    kappa = hi / lo
    rho = max(abs(1 - slo), abs(1 - shi))
    cg_bound = 0.5 * np.sqrt(kappa) * np.log(2 / TOL)
    diag = dict(cells_per_side=20, nodes=len(s["nodes"]), triangles=len(s["triangles"]),
                unknowns=n, stored_nnz=int(A.nnz),
                numeric_nnz=int(np.count_nonzero(np.abs(A.data) > 1e-12 * np.abs(A.data).max())),
                symmetry_max_abs=float(abs(A - A.T).max()),
                symmetry_relative=float(abs(A - A.T).max() / np.abs(A.data).max()),
                lambda_min=lo, lambda_max=hi, eig_residual_min=rlo, eig_residual_max=rhi,
                lambda_min_dense=float(ev_dense[0]), lambda_max_dense=float(ev_dense[-1]),
                kappa2=kappa, kappa2_dense=float(ev_dense[-1] / ev_dense[0]),
                lambda_min_S=slo, lambda_max_S=shi, rho_J=rho,
                rho_J_dense=float(max(abs(1 - evS_dense))),
                omega_upper_damped_jacobi=2 / shi,
                cg_sqrt_kappa_iteration_estimate=float(cg_bound),
                kappa_S=shi / slo)
    log(f"20x20 diag: {json.dumps(diag)}")
    rows, hists, sols = [], {}, {}
    rows.append(dict(method="Sparse LU (splu)", iterations="", relative_residual=eta(A, b, ref),
                     relative_error=0.0, accepted=bool(eta(A, b, ref) < TOL), status="direct",
                     best_seconds=tf + ts, factor_seconds=tf, solve_seconds=ts,
                     timing_runs_seconds=dict(factor=tfs, solve=tss)))
    for method in pb.METHODS:
        x, k, status, hist = pb.iterative(A, b, method, history=True)
        hists[method] = hist
        bt, times, (xt, kt, st, _) = best_of_3(lambda: pb.iterative(A, b, method, history=False))
        assert kt == k and st == status, (method, k, kt, status, st)
        assert np.allclose(xt, x, rtol=1e-12, atol=1e-16), method
        rr = eta(A, b, x)
        sols[method] = x
        rows.append(dict(method=method, iterations=k, relative_residual=rr,
                         relative_error=float(np.linalg.norm(x - ref) / np.linalg.norm(ref)),
                         accepted=bool(rr < TOL), status=status, best_seconds=bt,
                         timing_runs_seconds=times))
        log(f"{method}: k={k} eta={rr:.3e} status={status} t={bt:.4g}s")
    data = dict(environment=env(), tolerance=TOL, iteration_cap=CAP, diagnostics=diag,
                solvers=rows)
    (OUT / "solvers.json").write_text(json.dumps(data, indent=2) + "\n")
    (OUT / "histories.json").write_text(json.dumps(hists) + "\n")
    keys = ["method", "iterations", "relative_residual", "relative_error", "accepted",
            "status", "best_seconds"]
    with (OUT / "solver_comparison.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows([{k: r[k] for k in keys} for r in rows])
    return s, ref, lu, rows, hists, sols, diag


# --------------------------------------------------------------------------
def validation(s, ref, lu, rows, sols, diag):
    A, b = s["A"], s["b"]
    d = full_solution(s, ref)
    bal = balance(s, d)
    U = d.reshape(-1, 2)
    accepted = [r["method"] for r in rows[1:] if r["accepted"]]
    agree = {m: float(np.linalg.norm(sols[m] - ref) / np.linalg.norm(ref)) for m in accepted}
    agree_mm = {m: float(np.abs(sols[m] - ref).max() * 1e3) for m in accepted}
    # Exact affine patch test on the same 20 x 20 mesh with roller supports.
    r = force_driven(20, support="roller")
    xr = splu(r["A"].tocsc()).solve(r["b"])
    dr = full_solution(r, xr)
    exact = np.column_stack([P * r["nodes"][:, 0] / E, -NU * P * r["nodes"][:, 1] / E]).ravel()
    patch_err = float(np.linalg.norm(dr - exact) / np.linalg.norm(exact))
    patch_bal = balance(r, dr)
    # Seeded load perturbation on the 20 x 20 clamped system.
    rng = np.random.default_rng(2026)
    db = rng.normal(size=len(b))
    db *= 1e-6 * np.linalg.norm(b) / np.linalg.norm(db)
    dx = lu.solve(b + db) - ref
    rel_dx = float(np.linalg.norm(dx) / np.linalg.norm(ref))
    right, top, bottom = s["side"]["right"], s["side"]["top"], s["side"]["bottom"]
    v = dict(balance=bal,
             max_abs_prescribed_displacement_m=float(np.abs(d[s["constrained"]]).max()),
             constrained_dofs=int(len(s["constrained"])),
             sparse_lu_relative_residual=eta(A, b, ref),
             accepted_methods=accepted, relative_difference_to_lu=agree,
             max_abs_difference_to_lu_mm=agree_mm,
             max_right_ux_mm=float(U[right, 0].max() * 1e3),
             min_right_ux_mm=float(U[right, 0].min() * 1e3),
             top_right_ux_mm=float(U[right[-1], 0] * 1e3),
             bottom_right_ux_mm=float(U[right[0], 0] * 1e3),
             mid_right_ux_mm=float(U[right[len(right) // 2], 0] * 1e3),
             max_inward_uy_top_mm=float(-U[top, 1].min() * 1e3),
             max_inward_uy_bottom_mm=float(U[bottom, 1].max() * 1e3),
             max_displacement_mm=float(np.linalg.norm(U, axis=1).max() * 1e3),
             pL_over_E_mm=P * L / E * 1e3, amplification=SCALE,
             patch_test=dict(mesh="20x20 cells, roller: u_x=0 on left edge, u_y=0 at (0,0)",
                             unknowns=len(r["b"]), relative_error=patch_err,
                             max_abs_error_m=float(np.abs(dr - exact).max()),
                             balance=patch_bal),
             perturbation=dict(seed=2026, relative_load_perturbation=1e-6,
                               relative_displacement_change=rel_dx,
                               kappa2=diag["kappa2"], kappa_bound=diag["kappa2"] * 1e-6,
                               amplification_observed=rel_dx / 1e-6))
    (OUT / "validation.json").write_text(json.dumps(v, indent=2) + "\n")
    log(f"validation: {json.dumps(v)}")
    return d, v


# --------------------------------------------------------------------------
def refinement(perturb):
    out = []
    for n in (5, 10, 20, 40, 80):
        s = force_driven(n)
        A, b = s["A"].tocsr(), s["b"]
        lo, hi, rlo, rhi = extreme_eigs(A)
        slo, shi, _, _ = extreme_eigs(jacobi_matrix(A))
        _, kcg, scg, _ = pb.iterative(A, b, "CG", history=False)
        _, kpcg, spcg, _ = pb.iterative(A, b, "PCG (diagonal)", history=False)
        d = full_solution(s, splu(A.tocsc()).solve(b))
        U = d.reshape(-1, 2)
        right = s["side"]["right"]
        row = dict(cells_per_side=n, unknowns=len(b), stored_nnz=int(A.nnz),
                   lambda_min=lo, lambda_max=hi, eig_residuals=[rlo, rhi], kappa2=hi / lo,
                   rho_J=max(abs(1 - slo), abs(1 - shi)), kappa_S=shi / slo,
                   cg_iterations=kcg, cg_status=scg, pcg_iterations=kpcg, pcg_status=spcg,
                   top_right_ux_mm=float(U[right[-1], 0] * 1e3),
                   max_right_ux_mm=float(U[right, 0].max() * 1e3))
        out.append(row)
        log(f"refine {n}: {json.dumps(row)}")
    data = dict(environment=env(),
                case="force_driven clamp, 1 m square, traction 100 MPa, bl-tr diagonals",
                notes="kappa2 via eigsh LA / shift-invert sigma=0, tol 1e-10; CG/PCG under "
                      "the common protocol (x0=0, eta<1e-8, cap 20000); displacements from splu",
                meshes=out, perturbation_20x20=perturb)
    (OUT / "refinement.json").write_text(json.dumps(data, indent=2) + "\n")


def env():
    return dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                platform=platform.platform(), machine=platform.machine(),
                processor=platform.processor())


# --------------------------------------------------------------------------
def figures(small_s, s20, d20, hists, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.tri import Triangulation
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "pdf.fonttype": 42})

    # ---- Figure: setup, 2 x 2 mesh numbering and deformed 20 x 20 plate ----
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.25), constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.15]))
    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#e8eef5", ec="black", lw=1))
    ax.add_patch(Rectangle((-0.09, -0.05), 0.09, 1.1, fc="none", ec="none", hatch="////"))
    ax.plot([0, 0], [-0.05, 1.05], color="black", lw=2)
    for y in np.linspace(0.05, 0.95, 7):
        ax.annotate("", xy=(1.22, y), xytext=(1.0, y),
                    arrowprops=dict(arrowstyle="->", color="#b2182b", lw=0.9))
    ax.text(1.1, 1.06, r"$p$", color="#b2182b", ha="center", va="bottom")
    ax.text(-0.14, 0.5, r"clamped $u_x=u_y=0$", rotation=90, va="center", ha="center",
            fontsize=7)
    ax.text(0.5, 1.03, "free", ha="center", va="bottom", fontsize=7)
    ax.text(0.5, -0.03, "free", ha="center", va="top", fontsize=7)
    ax.annotate("", xy=(0, -0.2), xytext=(1, -0.2), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(0.5, -0.23, r"$L=1$ m", ha="center", va="top", fontsize=7)
    ax.text(0.53, 0.55, "$E=200$ GPa\n" r"$\nu=0.3$" "\n" r"$t=0.01$ m" "\n" r"$p=100$ MPa",
            ha="center", va="center", fontsize=7)
    ax.annotate("", xy=(0.17, 0.08), xytext=(0.05, 0.08), arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("", xy=(0.05, 0.2), xytext=(0.05, 0.08), arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.text(0.18, 0.08, "$x$", va="center", fontsize=7)
    ax.text(0.05, 0.21, "$y$", ha="center", va="bottom", fontsize=7)
    ax.set_xlim(-0.22, 1.3)
    ax.set_ylim(-0.35, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(a) geometry, supports, load")

    ax = axes[1]
    xy, tri = small_s["nodes"], small_s["triangles"]
    ax.triplot(Triangulation(xy[:, 0], xy[:, 1], tri), color="0.55", lw=0.7)
    free_nodes = sorted(set((small_s["free"] // 2).tolist()))
    for node, (x, y) in enumerate(xy):
        if node in free_nodes:
            k = free_nodes.index(node)
            ax.plot(x, y, "o", color="#2166ac", ms=4)
            ax.text(x - 0.03, y + 0.04, f"{node}", fontsize=6.5, ha="right", color="#2166ac")
            ax.text(x + 0.03, y - 0.1, rf"$x_{{{2*k+1}}},x_{{{2*k+2}}}$", fontsize=6.5,
                    color="#2166ac")
        else:
            ax.plot(x, y, "s", mfc="white", mec="black", ms=4)
            ax.text(x - 0.04, y + 0.04, f"{node}", fontsize=6.5, ha="right")
    for y, w in zip((0, 0.5, 1), (0.25, 0.5, 0.25)):
        ax.annotate("", xy=(1.0 + 0.6 * w + 0.04, y), xytext=(1.0, y),
                    arrowprops=dict(arrowstyle="->", color="#b2182b", lw=0.9))
        ax.text(1.0 + 0.6 * w + 0.06, y + 0.05, f"{w:g}", color="#b2182b", fontsize=6.5)
    ax.text(1.27, -0.2, "MN", color="#b2182b", fontsize=6.5, ha="center")
    ax.set_xlim(-0.15, 1.5)
    ax.set_ylim(-0.3, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(r"(b) $2\times2$ cells: unknowns, $b$")

    ax = axes[2]
    U = d20.reshape(-1, 2)
    xy = s20["nodes"]
    dxy = xy + SCALE * U
    mag = np.linalg.norm(U, axis=1) * 1e3
    tr = Triangulation(dxy[:, 0], dxy[:, 1], s20["triangles"])
    pc = ax.tripcolor(tr, mag, shading="gouraud", cmap="viridis")
    ax.triplot(tr, color="white", lw=0.15, alpha=0.5)
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k--", lw=0.8)
    ax.plot([0, 0], [0, 1], color="black", lw=2)
    fig.colorbar(pc, ax=ax, label=r"$|\mathbf{u}|$ [mm]", shrink=0.85, pad=0.02)
    ax.set_aspect("equal")
    ax.set_xlabel("$x$ [m]", labelpad=1)
    ax.set_ylabel("$y$ [m]", labelpad=1)
    ax.set_xlim(-0.05, 1.15)
    ax.set_ylim(-0.05, 1.05)
    ax.tick_params(labelsize=6.5)
    ax.set_title(rf"(c) deformed $20\times20$, $\times{SCALE}$")
    save(fig, "square_setup")

    # ---- Figure: residual histories ----
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.05), constrained_layout=True)
    styles = {"Jacobi": ("#999999", "-"), "Damped Jacobi": ("#a6761d", "-"),
              "Gauss-Seidel": ("#1b9e77", "-"), "SD": ("#e6ab02", "-"),
              "CG": ("#d95f02", "-"), "PCG (diagonal)": ("#7570b3", "--"),
              "MINRES": ("#e7298a", ":"), "GMRES (full)": ("#1f78b4", "-.")}
    labels = {"SD": "steepest descent", "PCG (diagonal)": "PCG (diag.)",
              "Gauss-Seidel": "Gauss–Seidel", "Damped Jacobi": r"damped Jacobi"}
    for ax, xmax in zip(axes, (CAP, 300)):
        for m in pb.METHODS:
            h = np.asarray(hists[m])
            c, ls = styles[m]
            ax.semilogy(np.arange(len(h)), h, color=c, ls=ls, lw=1.0, label=labels.get(m, m))
        ax.axhline(TOL, color="black", ls="--", lw=0.6)
        ax.set_xlim(0, xmax)
        ax.set_xlabel("iteration $k$ (GMRES: inner Arnoldi step)", labelpad=1)
        ax.grid(alpha=0.25, lw=0.5)
    axes[0].set_ylim(1e-9, 1e11)
    axes[1].set_ylim(1e-9, 1e3)
    axes[0].set_ylabel(r"relative residual $\eta(x_k)$")
    axes[0].set_title("(a) full budget")
    axes[1].set_title("(b) first 300 iterations")
    axes[0].legend(fontsize=6, ncol=2, loc="upper right", frameon=False)
    save(fig, "square_residuals")


def save(fig, name):
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pb.known_answer_checks()
    log("known_answer_checks passed; environment " + json.dumps(env()))
    small_s, _ = small_system()
    s20, ref, lu, rows, hists, sols, diag = benchmark()
    d20, v = validation(s20, ref, lu, rows, sols, diag)
    assert np.linalg.norm(v["balance"]["force_imbalance_N"]) < 1e-6
    assert abs(v["balance"]["moment_imbalance_Nm"]) < 1e-6
    assert v["patch_test"]["relative_error"] < 1e-12
    assert v["max_abs_prescribed_displacement_m"] == 0
    refinement(v["perturbation"])
    figures(small_s, s20, d20, hists, rows)
    (OUT / "square.log").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
