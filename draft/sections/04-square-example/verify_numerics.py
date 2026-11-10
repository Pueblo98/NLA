"""Independent numerical handoff for Hermes's Section 4 draft.

From NLA/: PYTHONPATH=.build-deps python3 draft/sections/04-square-example/verify_numerics.py
Uses the current team FEM and solver implementations, not a second assembly.
Writes only numerical-review/ here; does not replace historical benchmarks.
"""
from pathlib import Path
import csv
import json
import platform
import sys

import numpy as np
import scipy
from scipy.linalg import cholesky, lu, solve_triangular
from scipy.sparse import diags
from scipy.sparse.linalg import cg, eigsh, splu

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "fem"))
sys.path.insert(0, str(ROOT / "solvers"))
from plate import force_driven  # noqa: E402
from progress_benchmark import METHODS, iterative  # noqa: E402


def write_csv(path, header, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def balance(s, x):
    d = s["d"].copy()
    d[s["free"]] = x
    reaction = np.zeros_like(d)
    reaction[s["constrained"]] = (s["K"] @ d - s["f"])[s["constrained"]]
    applied = s["f"].reshape(-1, 2)
    support = reaction.reshape(-1, 2)
    xy = s["nodes"]

    def moment(forces):
        return float(np.sum(xy[:, 0] * forces[:, 1] - xy[:, 1] * forces[:, 0]))

    force_error = (applied + support).sum(axis=0)
    moment_error = moment(applied + support)
    force_scale = s["params"]["p"] * s["params"]["t"] * s["params"]["Ly"]
    length_scale = max(s["params"]["Lx"], s["params"]["Ly"])
    rr = float(np.linalg.norm(s["b"] - s["A"] @ x) / np.linalg.norm(s["b"]))
    assert np.linalg.norm(force_error) / force_scale < 1e-11
    assert abs(moment_error) / (force_scale * length_scale) < 1e-11
    assert np.array_equal(d[s["constrained"]], s["prescribed"])
    assert rr < 1e-11
    return {
        "relative_residual": rr,
        "applied_force_N": applied.sum(axis=0).tolist(),
        "support_force_N": support.sum(axis=0).tolist(),
        "force_imbalance_N": force_error.tolist(),
        "applied_moment_about_origin_Nm": moment(applied),
        "support_moment_about_origin_Nm": moment(support),
        "moment_imbalance_about_origin_Nm": moment_error,
        "maximum_support_error_m": float(np.max(np.abs(d[s["constrained"]] - s["prescribed"]))),
        "right_edge_ux_mm_bottom_to_top": (d.reshape(-1, 2)[s["side"]["right"], 0] * 1e3).tolist(),
    }


def eigencheck(A):
    results = []
    for which in ("SA", "LA"):
        values, vectors = eigsh(A, k=1, which=which, tol=1e-11, v0=np.ones(A.shape[0]))
        value, v = float(values[0]), vectors[:, 0]
        defect = float(np.linalg.norm(A @ v - value * v) / (abs(value) * np.linalg.norm(v)))
        assert value > 0 and defect < 1e-8
        results.append({"eigenvalue": value, "relative_eigenpair_residual": defect})
    return results


def main():
    out = HERE / "numerical-review"
    out.mkdir(exist_ok=True)
    old = json.loads((ROOT / "drafts/results/benchmark.json").read_text())
    small = force_driven(2)
    A, b = small["A"].toarray(), small["b"]
    assert np.allclose(A, np.loadtxt(ROOT / "drafts/results/small_A.csv", delimiter=","), rtol=1e-14, atol=1e-6)
    assert np.array_equal(b, np.loadtxt(ROOT / "drafts/results/small_b.csv", delimiter=","))
    L = cholesky(A, lower=True)
    y = solve_triangular(L, b, lower=True)
    x = solve_triangular(L.T, y, lower=False)
    assert np.allclose(x, np.loadtxt(ROOT / "drafts/results/small_x_cholesky.csv", delimiter=","), rtol=1e-12, atol=1e-16)
    # scipy.linalg.lu returns A = P L U, hence the row permutation is P.T.
    P, low, upper = lu(A)
    permutation_defect = np.linalg.norm(P.T @ A - low @ upper) / np.linalg.norm(A)
    assert permutation_defect < 1e-14
    np.savetxt(out / "small_cholesky_L.csv", L, delimiter=",")
    np.savetxt(out / "small_cholesky_y.csv", y, delimiter=",")
    # Convenient report scaling: Ahat xhat = bhat with xhat in millimetres.
    np.savetxt(out / "small_A_scaled.csv", A / 1e9, delimiter=",")
    np.savetxt(out / "small_b_scaled.csv", b / 1e6, delimiter=",")
    write_csv(out / "small_unknowns.csv", ["free_index", "global_dof", "node", "component", "node_x_m", "node_y_m", "displacement_mm"],
              [[i, int(g), int(g // 2), "ux" if g % 2 == 0 else "uy", *small["nodes"][g // 2], x[i] * 1e3]
               for i, g in enumerate(small["free"])])

    large = force_driven(20)
    A, b = large["A"], large["b"]
    reference = splu(A.tocsc()).solve(b)
    records = []
    for method in METHODS:
        computed, count, status, _ = iterative(A, b, method, history=False)
        rr = float(np.linalg.norm(b - A @ computed) / np.linalg.norm(b))
        baseline = next(row for row in old["solvers"] if row["method"] == method)
        assert (rr < 1e-8) == baseline["accepted"], method
        records.append({"method": method, "iterations": count, "status": status,
                        "accepted": bool(rr < 1e-8), "relative_residual": rr,
                        "relative_reference_error": float(np.linalg.norm(computed - reference) / np.linalg.norm(reference)),
                        "stored_benchmark_iterations": baseline["iterations"]})

    # Save fields at selected algebraic iterations for optional draft figures.
    snapshots = []
    snapshot_rows = []
    step = 0

    def capture(k, field):
        d = large["d"].copy()
        d[large["free"]] = field
        snapshots.append({"iteration": k, "relative_residual": float(np.linalg.norm(b - A @ field) / np.linalg.norm(b)),
                          "relative_reference_error": float(np.linalg.norm(field - reference) / np.linalg.norm(reference))})
        for node, (coords, displacement) in enumerate(zip(large["nodes"], d.reshape(-1, 2))):
            snapshot_rows.append([k, node, *coords, *displacement])

    def monitor(field):
        nonlocal step
        step += 1
        if step in (5, 25, 100):
            capture(step, field)

    capture(0, np.zeros_like(b))
    last, info = cg(A, b, rtol=1e-8, atol=0, maxiter=20_000, callback=monitor)
    assert info == 0 and np.linalg.norm(b - A @ last) / np.linalg.norm(b) < 1e-8
    capture(step, last)
    write_csv(out / "cg_snapshots.csv", ["iteration", "node", "x_m", "y_m", "ux_m", "uy_m"], snapshot_rows)

    H = diags(1 / np.sqrt(A.diagonal()))
    eig_A = eigencheck(A)
    eig_S = eigencheck((H @ A @ H).tocsr())
    lo, hi = [item["eigenvalue"] for item in eig_S]
    result = {
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()},
        "small": {"nodes": len(small["nodes"]), "triangles": len(small["triangles"]), "unknowns": len(x),
                  "free_global_dofs": small["free"].tolist(), "x_mm": (x * 1e3).tolist(),
                  "lu_row_permutation_relative_defect": float(permutation_defect), "validation": balance(small, x)},
        "large": {"nodes": len(large["nodes"]), "triangles": len(large["triangles"]), "unknowns": len(b),
                  "stored_nnz": A.nnz, "relative_symmetry_defect": float(np.linalg.norm((A - A.T).data) / np.linalg.norm(A.data)),
                  "extreme_eigenpairs_A": eig_A, "extreme_eigenpairs_diagonally_scaled_A": eig_S,
                  "condition_estimate": eig_A[1]["eigenvalue"] / eig_A[0]["eigenvalue"],
                  "jacobi_spectral_radius": max(abs(1 - lo), abs(1 - hi)),
                  "damped_jacobi_spectral_radius_omega_half": max(abs(1 - .5 * lo), abs(1 - .5 * hi)),
                  "jacobi_weight_upper_bound": 2 / hi, "validation": balance(large, reference),
                  "solvers": records, "cg_snapshots": snapshots},
        "limits": ["Reuses the team's FEM; this is not an independent FEM implementation.",
                   "No timings measured here; historical timing data remain unchanged.",
                   "Intermediate CG fields approximate static equilibrium and are not physical time steps.",
                   "No continuum-error or mesh-convergence claim follows from these checks."]}
    (out / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
