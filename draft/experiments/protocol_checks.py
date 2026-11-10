"""Verify the Section 3 comparison protocol code on this machine.

Run from the repository root:  python3 draft/experiments/protocol_checks.py
Outputs: draft/experiments/results/solvers/protocol_checks.json and .log

Checks (no benchmark numbers are produced here):
1. solvers/progress_benchmark.known_answer_checks(): every method recovers a
   manufactured 2x2 SPD solution, b = 0 returns x = 0 with zero iterations,
   the 3x3 Jacobi radius is 1.5, and the GMRES budget counts inner steps.
2. The divergence guard and the damped-Jacobi bound on that 3x3 SPD matrix:
   ordinary Jacobi must stop at the guard; omega = 0.5 < 2/lambda_max(S) = 0.8
   must reach the target.
3. The sparse eigenvalue estimators of the protocol (eigsh, which='LA' and
   shift-invert sigma=0, tol 1e-10) agree with dense eigvalsh on a small
   clamped-plate system.
"""
from pathlib import Path
import json
import platform
import sys

import numpy as np
import scipy
from scipy.linalg import eigvalsh
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "solvers"))
sys.path.insert(0, str(ROOT / "fem"))
import progress_benchmark as pb  # noqa: E402
from plate import force_driven  # noqa: E402

OUT = ROOT / "draft" / "experiments" / "results" / "solvers"


def extreme_eigs(A, tol=1e-10):
    """Protocol estimator: largest via which='LA', smallest via shift-invert at 0."""
    v0 = np.ones(A.shape[0])
    hi = eigsh(A, k=1, which="LA", tol=tol, v0=v0, return_eigenvectors=False)[0]
    lo = eigsh(A.tocsc(), k=1, sigma=0, which="LM", tol=tol, v0=v0,
               return_eigenvectors=False)[0]
    return float(lo), float(hi)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    pb.known_answer_checks()
    log.append("PASS known_answer_checks (all methods: %s)" % ", ".join(pb.METHODS))

    B = csr_matrix(np.full((3, 3), 0.75) + 0.25 * np.eye(3))
    xe = np.array([1.0, -1.0, 2.0])
    _, kj, sj, _ = pb.iterative(B, B @ xe, "Jacobi", history=False)
    xd, kd, sd, _ = pb.iterative(B, B @ xe, "Damped Jacobi", history=False)
    assert sj == "divergence_guard", sj
    assert sd == "target" and np.linalg.norm(xd - xe) / np.linalg.norm(xe) < 10 * 1e-8, sd  # kappa(B) = 10
    log.append(f"PASS 3x3 SPD: Jacobi stopped by guard after {kj}; damped Jacobi target after {kd}")

    s = force_driven(4)
    A = s["A"].tocsr()
    ev = eigvalsh(A.toarray())
    lo, hi = extreme_eigs(A)
    H = diags(1 / np.sqrt(A.diagonal()))
    S = (H @ A @ H).tocsr()
    evs = eigvalsh(S.toarray())
    slo, shi = extreme_eigs(S)
    rho_dense = float(max(abs(1 - evs)))
    rho_sparse = max(abs(1 - slo), abs(1 - shi))
    rel = lambda a, b: abs(a - b) / abs(b)  # noqa: E731
    assert rel(lo, ev[0]) < 1e-8 and rel(hi, ev[-1]) < 1e-8
    assert rel(rho_sparse, rho_dense) < 1e-8
    log.append(f"PASS eigsh vs eigvalsh on 4x4-cell plate (n={len(s['b'])}): "
               f"kappa {hi/lo:.6e} vs {ev[-1]/ev[0]:.6e}; rho_J {rho_sparse:.6f} vs {rho_dense:.6f}")

    data = dict(
        environment=dict(python=platform.python_version(), numpy=np.__version__,
                         scipy=scipy.__version__, platform=platform.platform(),
                         machine=platform.machine()),
        protocol=dict(tolerance=pb.TOL, iteration_cap=pb.CAP, methods=pb.METHODS,
                      x0="zero", divergence_guard=1e10, damped_jacobi_omega=0.5,
                      gmres_restart="n (full)", timing="best of 3, perf_counter",
                      eigen_tolerance=1e-10),
        checks=dict(
            known_answer_checks="pass",
            spd_3x3=dict(jacobi_status=sj, jacobi_iterations=kj,
                         damped_status=sd, damped_iterations=kd,
                         lambda_max_S=2.5, omega_upper=0.8),
            eig_estimator=dict(unknowns=len(s["b"]), lambda_min_dense=float(ev[0]),
                               lambda_min_sparse=lo, lambda_max_dense=float(ev[-1]),
                               lambda_max_sparse=hi, rho_J_dense=rho_dense,
                               rho_J_sparse=rho_sparse)),
    )
    (OUT / "protocol_checks.json").write_text(json.dumps(data, indent=2) + "\n")
    log.append("environment: " + json.dumps(data["environment"]))
    (OUT / "protocol_checks.log").write_text("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
