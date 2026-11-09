"""Reproduce the Session 22 progress-draft experiment from the repository FEM.

Run from NLA/: python solvers/progress_benchmark.py
No results are imported from a teammate's prose. Outputs: drafts/results/,
figures/progress_residuals.png and figures/progress_refinement.png.
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
from scipy.sparse import diags, tril
from scipy.sparse.linalg import cg, eigsh, gmres, minres, splu, spsolve_triangular

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fem"))
from plate import force_driven  # noqa: E402

TOL = 1e-8
CAP = 20_000
METHODS = ["Jacobi", "Damped Jacobi", "Gauss-Seidel", "SD", "CG", "GMRES (full)", "MINRES", "PCG (diagonal)"]


def iterative(A, b, method, *, cap=CAP, tol=TOL, history=True):
    """Zero initial guess; final acceptance always uses the independent residual.

    MINRES uses a callback exception at the shared true-residual target. Its
    native tolerance is zero to avoid accepting its different stopping test.
    GMRES uses legacy callback semantics: maxiter counts INNER iterations.
    Its history is an Arnoldi residual estimate, with a true final check.
    """
    x = np.zeros_like(b)
    nb = np.linalg.norm(b)
    if nb == 0:
        return x, 0, "zero_rhs", [0.0] if history else []
    hist = [1.0] if history else []
    count = 0
    last = x.copy()

    class TargetReached(Exception):
        pass

    def monitor(xk):
        nonlocal count, last
        count += 1
        if method == "MINRES" or history:
            rr = float(np.linalg.norm(b - A @ xk) / nb)
            if history:
                hist.append(rr)
            if method == "MINRES" and rr < tol:
                last = xk.copy()
                raise TargetReached

    def arnoldi(res):
        nonlocal count
        count += 1
        if history:
            hist.append(float(res))

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
            x, info = minres(A, b, rtol=0, maxiter=cap, callback=monitor, check=True)
            status = f"native_info={info}"
        except TargetReached:
            x = last
            status = "callback_target"
    else:
        D = A.diagonal()
        L = tril(A, format="csr") if method == "Gauss-Seidel" else None
        U = (A - L).tocsr() if L is not None else None
        r = b.copy()
        status = "iteration_limit"
        for count in range(1, cap + 1):
            if method == "Jacobi":
                x += r / D
            elif method == "Damped Jacobi":
                x += 0.5 * r / D
            elif method == "Gauss-Seidel":
                x = spsolve_triangular(L, b - U @ x, lower=True)
            elif method == "SD":
                Ar = A @ r
                x += ((r @ r) / (r @ Ar)) * r
            else:
                raise ValueError(method)
            r = b - A @ x
            rr = float(np.linalg.norm(r) / nb)
            if history:
                hist.append(rr)
            if not np.isfinite(rr) or rr > 1e10:
                status = "divergence_guard"
                break
            if rr < tol:
                status = "target"
                break
    return x, count, status, hist


def known_answer_checks():
    from scipy.sparse import csr_matrix
    A = csr_matrix([[4., 1.], [1., 3.]])
    expected = np.array([1., -2.])
    for method in METHODS:
        x, _, _, _ = iterative(A, A @ expected, method, cap=2000)
        assert np.linalg.norm(x - expected) < 1e-7, method
        z, k, status, _ = iterative(A, np.zeros(2), method)
        assert k == 0 and status == "zero_rhs" and np.all(z == 0), method
    B = csr_matrix(np.full((3, 3), .75) + .25 * np.eye(3))
    ev = eigvalsh(B.toarray())
    assert np.isclose(max(abs(1 - ev)), 1.5)
    _, k, _, _ = iterative(A, A @ expected, "GMRES (full)", cap=1)
    assert k == 1


def main():
    known_answer_checks()
    out = ROOT / "drafts" / "results"
    out.mkdir(parents=True, exist_ok=True)
    s = force_driven(2)
    A, b = s["A"].toarray(), s["b"]
    ev = eigvalsh(A)
    xs = {"PA=LU": lu_solve(lu_factor(A), b), "Inverse": inv(A) @ b,
          "Cholesky": cho_solve(cho_factor(A, lower=True), b)}
    small = {"unknowns": len(b), "stored_nnz": s["A"].nnz,
             "lambda_min": float(ev[0]), "lambda_max": float(ev[-1]),
             "condition": float(ev[-1] / ev[0]),
             "relative_residuals": {k: float(np.linalg.norm(b - A @ v) / np.linalg.norm(b)) for k, v in xs.items()}}
    np.savetxt(out / "small_A.csv", A, delimiter=",")
    np.savetxt(out / "small_b.csv", b, delimiter=",")
    np.savetxt(out / "small_x_cholesky.csv", xs["Cholesky"], delimiter=",")
    records, histories = [], {}
    s = force_driven(20)
    A, b = s["A"], s["b"]
    direct = splu(A.tocsc())
    ref = direct.solve(b)
    for method in METHODS:
        x, k, status, hist = iterative(A, b, method)
        histories[method] = hist
        times = []
        for _ in range(3):
            start = perf_counter()
            xt, kt, st, _ = iterative(A, b, method, history=False)
            times.append(perf_counter() - start)
            assert kt == k and st == status
            assert np.allclose(xt, x, rtol=1e-12, atol=1e-16)
        rr = float(np.linalg.norm(b - A @ x) / np.linalg.norm(b))
        row = dict(method=method, iterations=k, relative_residual=rr,
                   relative_error=float(np.linalg.norm(x-ref) / np.linalg.norm(ref)),
                   accepted=bool(rr < TOL), status=status, best_seconds=min(times),
                   timing_runs_seconds=times)
        records.append(row)
        print(row, flush=True)

    refinement = []
    for n in (10, 20, 40):
        sn = force_driven(n)
        An, bn = sn["A"], sn["b"]
        lo = float(eigsh(An, k=1, which="SA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(bn)))[0])
        hi = float(eigsh(An, k=1, which="LA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(bn)))[0])
        H = diags(1 / np.sqrt(An.diagonal()))
        S = (H @ An @ H).tocsr()
        slo = float(eigsh(S, k=1, which="SA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(bn)))[0])
        shi = float(eigsh(S, k=1, which="LA", return_eigenvectors=False, tol=1e-10, v0=np.ones(len(bn)))[0])
        x, count, _, _ = iterative(An, bn, "CG", history=False)
        dn = sn["d"].copy()
        dn[sn["free"]] = splu(An.tocsc()).solve(bn)
        top = sn["side"]["right"][-1]
        refinement.append(dict(cells=n, unknowns=len(bn), stored_nnz=An.nnz,
                               numeric_nnz=int(np.count_nonzero(np.abs(An.data) > 1e-12 * abs(An.data).max())),
                               condition=hi/lo, jacobi_radius=max(abs(1-slo), abs(1-shi)),
                               omega_upper=2/shi, cg_iterations=count,
                               top_right_u_mm=float(dn[2*top]*1e3)))

    d = s["d"].copy()
    d[s["free"]] = ref
    r = s["K"] @ d - s["f"]
    reactions = np.zeros_like(r)
    reactions[s["constrained"]] = r[s["constrained"]]
    total = (reactions + s["f"]).reshape(-1, 2)
    xy = s["nodes"]
    force = total.sum(axis=0)
    moment = float(np.sum(xy[:, 0]*total[:, 1] - xy[:, 1]*total[:, 0]))
    roller = force_driven(6, 4, Lx=2., Ly=1., support="roller")
    dr = roller["d"].copy()
    dr[roller["free"]] = splu(roller["A"].tocsc()).solve(roller["b"])
    exact = np.column_stack([100e6 * roller["nodes"][:, 0] / 200e9,
                            -.3 * 100e6 * roller["nodes"][:, 1] / 200e9]).ravel()
    rng = np.random.default_rng(2026)
    db = rng.normal(size=len(b))
    db *= 1e-6 * np.linalg.norm(b) / np.linalg.norm(db)
    dx = direct.solve(b + db) - ref
    rel_dx = float(np.linalg.norm(dx) / np.linalg.norm(ref))
    checks = dict(force_imbalance_N=force.tolist(), moment_imbalance_Nm=moment,
                  maximum_support_displacement_m=float(abs(d[s["constrained"]]).max()),
                  sparse_lu_relative_residual=float(np.linalg.norm(b-A@ref)/np.linalg.norm(b)),
                  roller_patch_relative_error=float(np.linalg.norm(dr-exact)/np.linalg.norm(exact)),
                  load_perturbation_relative=1e-6, displacement_perturbation_relative=rel_dx,
                  load_perturbation_seed=2026,
                  maximum_right_u_mm=float(d.reshape(-1, 2)[s["side"]["right"], 0].max()*1e3))
    assert np.linalg.norm(force) < 1e-6
    assert abs(moment) < 1e-6
    assert checks["roller_patch_relative_error"] < 1e-12
    assert checks["maximum_support_displacement_m"] == 0
    data = dict(environment=dict(python=platform.python_version(), numpy=np.__version__,
                                  scipy=scipy.__version__, platform=platform.platform(),
                                  machine=platform.machine()),
                tolerance=TOL, iteration_cap=CAP, small=small,
                solvers=records, refinement=refinement, validation=checks)
    (out / "benchmark.json").write_text(json.dumps(data, indent=2) + "\n")
    (out / "histories.json").write_text(json.dumps(histories) + "\n")
    with (out / "solver_comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[k for k in records[0] if k != "timing_runs_seconds"])
        writer.writeheader()
        writer.writerows([{k:v for k,v in row.items() if k != "timing_runs_seconds"} for row in records])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), constrained_layout=True)
    for name, hist in histories.items():
        for ax in axes:
            ax.semilogy(range(len(hist)), hist, label=name, lw=1)
    for ax in axes:
        ax.axhline(TOL, color="black", ls="--", lw=.8)
        ax.set_xlabel("iteration (GMRES: inner Arnoldi step)")
        ax.set_ylabel("relative residual norm")
        ax.grid(alpha=.2)
    axes[0].set_xlim(0, CAP)
    axes[0].set_ylim(1e-9, 1e11)
    axes[1].set_xlim(0, 350)
    axes[1].set_ylim(1e-9, 10)
    axes[0].set_title("Full iteration budget")
    axes[1].set_title("First 350 iterations")
    axes[0].legend(fontsize=7, ncol=2)
    fig.savefig(ROOT / "figures" / "progress_residuals.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(8, 3), constrained_layout=True)
    ns = [v["unknowns"] for v in refinement]
    axes[0].loglog(ns, [v["condition"] for v in refinement], "o-")
    axes[0].set_ylabel("estimated condition number (2-norm)")
    axes[1].loglog(ns, [v["cg_iterations"] for v in refinement], "o-")
    axes[1].set_ylabel("CG iterations")
    for ax in axes:
        ax.set_xlabel("free displacement unknowns")
        ax.grid(alpha=.2)
    fig.savefig(ROOT / "figures" / "progress_refinement.png", dpi=180)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
