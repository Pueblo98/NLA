"""Section 5 experiments: additional objects, meshes and controlled comparisons.

Run from the repository root:  python3 draft/experiments/objects.py
Outputs (overwritten):          draft/experiments/results/objects/
    objects.json      every case: mesh checks, diagnostics, solver records, responses
    meshes.csv        one row per (object, level) mesh
    cases.csv         one row per reduced system (diagnostics + responses)
    solver_runs.csv   one row per (case, method)
    histories.npz     residual histories of the representative systems
    run.log           console log of this run

Objects, loads and supports are defined in OBJECTS / CASES below; all lengths in
metres, stresses in pascals, forces in newtons. Assembly is fem/elasticity.assemble,
consistent edge loads are solvers/system_tools.constant_edge_load, reduction is
solvers/system_tools.reduce_system and every iterative run is
solvers/progress_benchmark.iterative (unchanged), under the common protocol:
x0 = 0, independent relative residual < 1e-8, cap 20,000, Jacobi divergence guard.
"""
from pathlib import Path
import csv
import json
import math
import platform
import sys
import time
from time import perf_counter

import numpy as np
import scipy
import triangle
from scipy.linalg import cholesky, eigvalsh
from scipy.sparse import csgraph, csr_matrix, diags
from scipy.sparse.linalg import eigsh, splu

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "fem"))
sys.path.insert(0, str(ROOT / "solvers"))
from elasticity import assemble, material_matrix, strain_displacement  # noqa: E402
from system_tools import constant_edge_load, reduce_system  # noqa: E402
from progress_benchmark import CAP, METHODS, TOL, iterative  # noqa: E402
from plate import force_driven  # noqa: E402

OUT = ROOT / "draft" / "experiments" / "results" / "objects"

# Baseline material, thickness and load (common brief)
E0, NU0, T0, P0 = 200e9, 0.3, 0.01, 100e6
TAU_BEAM = 10e6          # shear traction on the beam tip (P = tau t h = 50 kN)
MIN_ANGLE = 30           # Triangle quality bound (degrees)
EIG_TOL = 1e-10
DENSE_EIG_MAX = 1500     # dense eigvalsh cross-check of eigsh up to this size
DENSE_CHOL_MAX = 3000    # dense Cholesky PD check up to this size
CORE = ["CG", "PCG (diagonal)", "MINRES", "Gauss-Seidel"]

# Segment markers (>= 2; Triangle reserves 0/1 for unmarked boundaries)
BOTTOM, RIGHT, TOP, LEFT, HOLE, INNER_H, INNER_V = 2, 3, 4, 5, 6, 7, 8


def circle(cx, cy, r, n):
    a = 2 * np.pi * np.arange(n) / n
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])


# ---------------------------------------------------------------- objects
# outer: ordered counter-clockwise vertices; markers[i] labels segment v_i -> v_{i+1}.
# Extra vertices at edge midpoints make matched physical points / pins mesh nodes.
OBJECTS = {
    "S": dict(
        title="Square plate (unstructured)",
        reason="Section 4 geometry meshed with Triangle: structured vs unstructured mesh",
        outer=[(0, 0), (1, 0), (1, .5), (1, 1), (0, 1), (0, .5)],
        markers=[BOTTOM, RIGHT, RIGHT, TOP, LEFT, LEFT],
        holes=[], levels=[0.1, 0.05, 1 / 30, 0.025],
        points={"right_mid": (1, .5), "top_right": (1, 1)}),
    "H": dict(
        title="Square plate with central hole",
        reason="circular opening: stress concentration and a multiply connected domain",
        outer=[(0, 0), (1, 0), (1, .5), (1, 1), (0, 1), (0, .5)],
        markers=[BOTTOM, RIGHT, RIGHT, TOP, LEFT, LEFT],
        holes=[dict(centre=(.5, .5), radius=.15)], levels=[0.1, 0.05, 1 / 30, 0.025],
        points={"right_mid": (1, .5), "hole_top": (.5, .65)}),
    "L": dict(
        title="L-shaped bracket",
        reason="re-entrant corner (stress singularity) and two arms that can be loaded",
        outer=[(0, 0), (1, 0), (1, .25), (1, .5), (.5, .5), (.5, 1), (.25, 1), (0, 1), (0, .5)],
        markers=[BOTTOM, RIGHT, RIGHT, INNER_H, INNER_V, TOP, TOP, LEFT, LEFT],
        holes=[], levels=[0.1, 0.05, 1 / 30, 0.025],
        points={"right_mid": (1, .25), "top_mid": (.25, 1), "corner": (.5, .5)}),
    "B": dict(
        title="Slender cantilever beam",
        reason="bending response with an Euler-Bernoulli/Timoshenko estimate; slender aspect 8:1",
        outer=[(0, 0), (4, 0), (4, .25), (4, .5), (0, .5), (0, .25)],
        markers=[BOTTOM, RIGHT, RIGHT, TOP, LEFT, LEFT],
        holes=[], levels=[0.125, 0.0625, 0.5 / 12, 0.03125],
        points={"tip_mid": (4, .25), "tip_top": (4, .5)}),
}

CLAMP_LEFT = [("segment", LEFT, "xy")]
ROLLER_PIN = [("segment", LEFT, "x"), ("point", (0, .5), "y")]
ROLLER_ONLY = [("segment", LEFT, "x")]


def case(name, obj, level, *, loads, supports, E=E0, nu=NU0, t=T0, question, full=False,
         gs_full=False, response):
    return dict(name=name, object=obj, level=level, loads=loads, supports=supports, E=E,
                nu=nu, t=t, question=question, full=full, gs_full=gs_full, response=response)


def build_cases():
    cs = []
    base = {
        "S": dict(loads=[(RIGHT, (P0, 0))], supports=CLAMP_LEFT, response=("right_mid", 0)),
        "H": dict(loads=[(RIGHT, (P0, 0))], supports=CLAMP_LEFT, response=("right_mid", 0)),
        "L": dict(loads=[(RIGHT, (P0, 0))], supports=CLAMP_LEFT, response=("right_mid", 0)),
        "B": dict(loads=[(RIGHT, (0, -TAU_BEAM))], supports=CLAMP_LEFT, response=("tip_mid", 1)),
    }
    for o, spec in base.items():
        for lev in range(4):
            cs.append(case(f"{o}-base-L{lev + 1}", o, lev, question="geometry + refinement",
                           full=(lev == 1), gs_full=(lev <= 1), **spec))
    # load magnitude (linearity): hole plate, level 2
    for p in (25e6, 250e6):
        cs.append(case(f"H-p{int(p / 1e6)}-L2", "H", 1, loads=[(RIGHT, (p, 0))],
                       supports=CLAMP_LEFT, question="load magnitude", response=("right_mid", 0)))
    # load location: L-bracket, same normal traction on the other arm's free end
    cs.append(case("L-top-L2", "L", 1, loads=[(TOP, (0, P0))], supports=CLAMP_LEFT,
                   question="load location", response=("top_mid", 1)))
    # beam under axial tension (same A as B-base-L2, different b)
    cs.append(case("B-axial-L2", "B", 1, loads=[(RIGHT, (P0, 0))], supports=CLAMP_LEFT,
                   question="load type on slender object", response=("tip_mid", 0)))
    # supports: hole plate roller + pin instead of clamp
    cs.append(case("H-rollerpin-L2", "H", 1, loads=[(RIGHT, (P0, 0))], supports=ROLLER_PIN,
                   question="support conditions", response=("right_mid", 0)))
    # material: Poisson ratio and Young's modulus
    for E, nu in ((E0, 0.0), (E0, 0.45), (70e9, 0.3)):
        cs.append(case(f"H-E{int(E / 1e9)}-nu{nu:g}-L2", "H", 1, loads=[(RIGHT, (P0, 0))],
                       supports=CLAMP_LEFT, E=E, nu=nu, question="material",
                       response=("right_mid", 0)))
    return cs


# ---------------------------------------------------------------- meshing
def pslg(obj, h):
    """Subdivide every input segment into pieces of length <= h; return Triangle input."""
    o = OBJECTS[obj]
    verts, segs, marks, loops = [], [], [], []

    def add_loop(poly, mk):
        start = len(verts)
        loop = []
        n = len(poly)
        for i in range(n):
            a, b = np.asarray(poly[i], float), np.asarray(poly[(i + 1) % n], float)
            k = max(1, math.ceil(np.linalg.norm(b - a) / h - 1e-9))
            for j in range(k):
                verts.append(a + (b - a) * j / k)
                marks.append(mk[i])
                loop.append(len(verts) - 1)
        m = len(verts) - start
        for i in range(m):
            segs.append((start + i, start + (i + 1) % m))
        loops.append(loop)

    add_loop(o["outer"], o["markers"])
    hole_pts, hole_polys = [], []
    for hl in o["holes"]:
        r = hl["radius"]
        n = 4 * math.ceil(2 * np.pi * r / (4 * h))      # multiple of 4: hole top is a vertex
        poly = circle(*hl["centre"], r, n)[::-1]         # clockwise for the inner loop
        add_loop([tuple(p) for p in poly], [HOLE] * n)
        hole_pts.append(hl["centre"])
        hole_polys.append(poly)
    return np.array(verts), np.array(segs), np.array(marks), hole_pts, hole_polys


def polygon_area(p):
    p = np.asarray(p)
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))


def inside(poly, pts):
    """Even-odd ray casting; poly (n,2), pts (m,2)."""
    x, y = pts[:, 0], pts[:, 1]
    res = np.zeros(len(pts), bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        xin = x1 + (y - y1) * (x2 - x1) / np.where(y2 != y1, y2 - y1, 1)
        res ^= cond & (x < xin)
    return res


def point_segment_distance(p, a, b):
    ab = b - a
    s = np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0, 1)
    return float(np.linalg.norm(p - (a + s * ab)))


def mesh(obj, level):
    o = OBJECTS[obj]
    h = o["levels"][level]
    V, S, M, hole_pts, hole_polys = pslg(obj, h)
    amax = h * h * np.sqrt(3) / 4
    opts = f"pq{MIN_ANGLE}a{amax:.10f}"
    data = dict(vertices=V, segments=S, segment_markers=M[:, None])
    if hole_pts:
        data["holes"] = np.array(hole_pts, float)
    tri = triangle.triangulate(data, opts)
    nodes, tris = tri["vertices"], tri["triangles"]
    segs, smark = tri["segments"], tri["segment_markers"].ravel()
    # ---- checks
    xy = nodes[tris]
    two_area = ((xy[:, 1, 0] - xy[:, 0, 0]) * (xy[:, 2, 1] - xy[:, 0, 1])
                - (xy[:, 2, 0] - xy[:, 0, 0]) * (xy[:, 1, 1] - xy[:, 0, 1]))
    areas = two_area / 2
    angles = []
    for i in range(3):
        u = xy[:, (i + 1) % 3] - xy[:, i]
        v = xy[:, (i + 2) % 3] - xy[:, i]
        c = np.sum(u * v, 1) / np.linalg.norm(u, axis=1) / np.linalg.norm(v, axis=1)
        angles.append(np.degrees(np.arccos(np.clip(c, -1, 1))))
    angles = np.array(angles)
    edge_len = np.concatenate([np.linalg.norm(xy[:, (i + 1) % 3] - xy[:, i], axis=1) for i in range(3)])
    exact_poly_area = polygon_area(o["outer"]) - sum(abs(polygon_area(p)) for p in hole_polys)
    true_area = polygon_area(o["outer"]) - sum(np.pi * hl["radius"] ** 2 for hl in o["holes"])
    # boundary edges = edges used by exactly one triangle
    e = np.sort(np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), axis=1)
    ue, cnt = np.unique(e, axis=0, return_counts=True)
    bnd = {tuple(x) for x in ue[cnt == 1]}
    segset = {tuple(sorted(x)) for x in segs}
    # every output segment lies on an input segment with the same marker
    seg_dev = 0.0
    for (i, j), mk in zip(segs, smark):
        cand = [k for k in range(len(S)) if M[k] == mk]
        for p in (nodes[i], nodes[j]):
            seg_dev = max(seg_dev, min(point_segment_distance(p, V[S[k, 0]], V[S[k, 1]]) for k in cand))
    cent = xy.mean(axis=1)
    in_hole = int(sum(inside(p, cent).sum() for p in hole_polys))
    adj = csr_matrix((np.ones(len(ue)), (ue[:, 0], ue[:, 1])), shape=(len(nodes),) * 2)
    ncomp = csgraph.connected_components(adj, directed=False)[0]
    euler = len(nodes) - len(ue) + len(tris)
    pts = {}
    for k, p in o["points"].items():
        dist = np.linalg.norm(nodes - np.asarray(p), axis=1)
        assert dist.min() < 1e-12, (obj, level, k)
        pts[k] = int(dist.argmin())
    checks = dict(
        h=h, triangle_options=opts, nodes=len(nodes), triangles=len(tris),
        boundary_segments=len(segs), min_area=float(areas.min()),
        all_ccw_positive=bool(areas.min() > 0), min_angle_deg=float(angles.min()),
        max_angle_deg=float(angles.max()), edge_min=float(edge_len.min()),
        edge_max=float(edge_len.max()), edge_mean=float(edge_len.mean()),
        area_sum=float(areas.sum()), pslg_area=exact_poly_area,
        area_rel_error_vs_pslg=float(abs(areas.sum() - exact_poly_area) / exact_poly_area),
        area_rel_diff_vs_true_geometry=float(abs(areas.sum() - true_area) / true_area),
        boundary_edges_equal_segments=bool(bnd == segset),
        max_segment_deviation_m=seg_dev, centroids_in_holes=in_hole,
        connected_components=int(ncomp), euler_characteristic=int(euler),
        expected_euler=1 - len(o["holes"]))
    assert checks["all_ccw_positive"] and checks["boundary_edges_equal_segments"]
    assert seg_dev < 1e-12 and in_hole == 0 and ncomp == 1 and euler == 1 - len(o["holes"])
    assert checks["area_rel_error_vs_pslg"] < 1e-12
    return dict(nodes=nodes, triangles=tris, segments=segs, segment_markers=smark,
                points=pts, checks=checks, hole_polys=hole_polys)


# ---------------------------------------------------------------- system
def build_system(c, mcache, kcache):
    key = (c["object"], c["level"])
    if key not in mcache:
        mcache[key] = mesh(*key)
    m = mcache[key]
    kkey = key + (c["E"], c["nu"], c["t"])
    if kkey not in kcache:
        t0 = perf_counter()
        kcache[kkey] = (assemble(m["nodes"], m["triangles"], c["E"], c["nu"], plane="stress",
                                 thickness=c["t"]), perf_counter() - t0)
    K, t_asm = kcache[kkey]
    nodes = m["nodes"]
    f = np.zeros(2 * len(nodes))
    for mk, tau in c["loads"]:
        edges = m["segments"][m["segment_markers"] == mk].astype(int)
        f += constant_edge_load(nodes, edges, [c["t"] * tau[0], c["t"] * tau[1]])
    cons = []
    for kind, where, comps in c["supports"]:
        if kind == "segment":
            ids = np.unique(m["segments"][m["segment_markers"] == where])
        else:
            ids = np.array([int(np.linalg.norm(nodes - np.asarray(where), axis=1).argmin())])
            assert np.linalg.norm(nodes[ids[0]] - np.asarray(where)) < 1e-12
        for comp in comps:
            cons.append(2 * ids + (0 if comp == "x" else 1))
    cons = np.unique(np.concatenate(cons))
    A, b, free, d = reduce_system(K, f, cons, np.zeros(cons.size))
    return m, K, f, cons, A.tocsr(), b, free, d, t_asm


def extreme_eigs(A):
    n = A.shape[0]
    v0 = np.ones(n)
    hi = float(eigsh(A, k=1, which="LA", tol=EIG_TOL, v0=v0, return_eigenvectors=False)[0])
    lo = float(eigsh(A.tocsc(), k=1, sigma=0, which="LM", tol=EIG_TOL, v0=v0,
                     return_eigenvectors=False)[0])
    return lo, hi


def diagnostics(A):
    n = A.shape[0]
    t0 = perf_counter()
    lo, hi = extreme_eigs(A)
    Hs = diags(1 / np.sqrt(A.diagonal()))
    S = (Hs @ A @ Hs).tocsr()
    slo, shi = extreme_eigs(S)
    out = dict(unknowns=n, stored_nnz=int(A.nnz),
               numeric_nnz=int(np.count_nonzero(np.abs(A.data) > 1e-12 * np.abs(A.data).max())),
               symmetry_rel=float(abs(A - A.T).max() / abs(A).max()),
               lambda_min=lo, lambda_max=hi, kappa2=hi / lo,
               S_lambda_min=slo, S_lambda_max=shi, rho_J=max(abs(1 - slo), abs(1 - shi)),
               kappa2_jacobi_scaled=shi / slo, eig_method="eigsh LA + shift-invert sigma=0",
               diag_positive=bool(A.diagonal().min() > 0))
    if n <= DENSE_EIG_MAX:
        ev = eigvalsh(A.toarray())
        out["dense_kappa2"] = float(ev[-1] / ev[0])
        out["dense_vs_eigsh_kappa_rel"] = float(abs(ev[-1] / ev[0] - out["kappa2"]) / out["kappa2"])
    if n <= DENSE_CHOL_MAX:
        try:
            cholesky(A.toarray(), lower=True)
            out["dense_cholesky"] = "success"
        except np.linalg.LinAlgError as exc:
            out["dense_cholesky"] = f"failed: {exc}"
    out["positive_definite"] = bool(lo > 0)
    out["diagnostics_seconds"] = perf_counter() - t0
    return out


def time_best(fn, reps=3):
    ts = []
    for _ in range(reps):
        t0 = perf_counter()
        r = fn()
        ts.append(perf_counter() - t0)
    return r, ts


def protocol(A, b, methods, gs_full, keep_hist):
    Ac = A.tocsc()
    lu, tf = time_best(lambda: splu(Ac))
    ref, ts = time_best(lambda: lu.solve(b))
    nb = np.linalg.norm(b)
    recs = [dict(method="splu", iterations=None,
                 relative_residual=float(np.linalg.norm(b - A @ ref) / nb), relative_error=0.0,
                 accepted=bool(np.linalg.norm(b - A @ ref) / nb < TOL), status="direct",
                 best_seconds=min(tf) + min(ts), factor_best_seconds=min(tf),
                 solve_best_seconds=min(ts), timing_runs=3,
                 lu_fill_nnz=int(lu.L.nnz + lu.U.nnz))]
    hists = {}
    for method in methods:
        if method == "Gauss-Seidel" and not gs_full:
            t0 = perf_counter()
            x, k, status, _ = iterative(A, b, method, history=False)
            times = [perf_counter() - t0]
            note = "single timed run without history (Gauss-Seidel cost policy)"
        else:
            x, k, status, hist = iterative(A, b, method, history=keep_hist)
            if keep_hist:
                hists[method] = np.asarray(hist)
            times = []
            for _ in range(3):
                t0 = perf_counter()
                xt, kt, st, _ = iterative(A, b, method, history=False)
                times.append(perf_counter() - t0)
                assert kt == k and st == status, (method, k, kt, status, st)
            note = "best of 3; history recorded in a separate run" if keep_hist else "best of 3"
        rr = float(np.linalg.norm(b - A @ x) / nb)
        recs.append(dict(method=method, iterations=int(k), relative_residual=rr,
                         relative_error=float(np.linalg.norm(x - ref) / np.linalg.norm(ref)),
                         accepted=bool(rr < TOL), status=status, best_seconds=min(times),
                         timing_runs=len(times), timing_note=note))
    return ref, recs, hists


def element_stress(m, d, E, nu):
    D = material_matrix(E, nu, "stress")
    sig = np.empty((len(m["triangles"]), 3))
    for i, tri in enumerate(m["triangles"]):
        B, _ = strain_displacement(m["nodes"][tri])
        de = np.column_stack([d[2 * tri], d[2 * tri + 1]]).ravel()
        sig[i] = D @ (B @ de)
    vm = np.sqrt(sig[:, 0] ** 2 - sig[:, 0] * sig[:, 1] + sig[:, 1] ** 2 + 3 * sig[:, 2] ** 2)
    return sig, vm


def validate(m, K, f, cons, d):
    r = K @ d - f
    reac = np.zeros_like(r)
    reac[cons] = r[cons]
    tot = (f + reac).reshape(-1, 2)
    xy = m["nodes"]
    F = tot.sum(0)
    Mz = float(np.sum(xy[:, 0] * tot[:, 1] - xy[:, 1] * tot[:, 0]))
    fa = f.reshape(-1, 2)
    Fa = float(np.linalg.norm(fa.sum(0)))
    Ma = float(np.sum(xy[:, 0] * fa[:, 1] - xy[:, 1] * fa[:, 0]))
    R = reac.reshape(-1, 2).sum(0)
    return dict(applied_resultant_N=fa.sum(0).tolist(), applied_moment_origin_Nm=Ma,
                reaction_resultant_N=R.tolist(),
                force_imbalance_rel=float(np.linalg.norm(F) / Fa),
                moment_imbalance_Nm=Mz, moment_imbalance_rel=float(abs(Mz) / (Fa * 1.0)),
                max_support_displacement_m=float(np.abs(d[cons]).max()),
                free_residual_force_rel=float(np.abs(np.delete(r, cons)).max() / np.abs(f).max()))


# ---------------------------------------------------------------- main
class Tee:
    def __init__(self, path):
        self.f = open(path, "w")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        self.f.write(s + "\n")
        self.f.flush()


def beam_reference(E, nu, t, L=4.0, h=0.5, tau=TAU_BEAM):
    P = tau * t * h
    I = t * h ** 3 / 12
    G = E / (2 * (1 + nu))
    eb = P * L ** 3 / (3 * E * I)
    shear = P * L / (5 / 6 * G * t * h)
    return dict(P_N=P, I_m4=I, delta_EB_m=eb, delta_shear_m=shear, delta_Timoshenko_m=eb + shear)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = Tee(OUT / "run.log")
    t_start = perf_counter()
    env = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
               triangle=getattr(triangle, "__version__", "unknown"),
               platform=platform.platform(), machine=platform.machine(),
               processor=platform.processor(), date=time.strftime("%Y-%m-%d %H:%M:%S"))
    log("environment", json.dumps(env))
    mcache, kcache = {}, {}
    results, hist_store = [], {}
    for c in build_cases():
        t0 = perf_counter()
        m, K, f, cons, A, b, free, d, t_asm = build_system(c, mcache, kcache)
        diag = diagnostics(A)
        assert diag["positive_definite"] and diag["diag_positive"], c["name"]
        methods = METHODS if c["full"] else CORE
        ref, recs, hists = protocol(A, b, methods, c["gs_full"], keep_hist=c["full"])
        for k, v in hists.items():
            hist_store[f"{c['name']}|{k}"] = v
        d[free] = ref
        val = validate(m, K, f, cons, d)
        sig, vm = element_stress(m, d, c["E"], c["nu"])
        U = d.reshape(-1, 2)
        pt, comp = c["response"]
        resp = {f"{k}_u{'xy'[j]}_mm": float(U[i, j] * 1e3) for k, i in m["points"].items()
                for j in (0, 1)}
        resp["matched_point"] = pt
        resp["matched_component"] = "xy"[comp]
        resp["matched_value_mm"] = float(U[m["points"][pt], comp] * 1e3)
        resp["max_abs_displacement_mm"] = float(np.linalg.norm(U, axis=1).max() * 1e3)
        resp["max_von_mises_MPa"] = float(vm.max() / 1e6)
        if c["object"] == "H":
            on_hole = np.isin(m["triangles"], np.unique(
                m["segments"][m["segment_markers"] == HOLE])).any(1)
            resp["hole_max_sigma_xx_MPa"] = float(sig[on_hole, 0].max() / 1e6)
        if c["object"] == "L":
            touch = (m["triangles"] == m["points"]["corner"]).any(1)
            resp["corner_max_von_mises_MPa"] = float(vm[touch].max() / 1e6)
        rec = dict(name=c["name"], object=c["object"], level=c["level"] + 1,
                   question=c["question"], E_Pa=c["E"], nu=c["nu"], t_m=c["t"],
                   loads=[dict(marker=mk, traction_Pa=list(tau)) for mk, tau in c["loads"]],
                   supports=[dict(kind=k, where=w if k == "segment" else list(w), comps=cp)
                             for k, w, cp in c["supports"]],
                   constrained_dofs=int(cons.size), mesh=m["checks"], assembly_seconds=t_asm,
                   diagnostics=diag, solvers=recs, validation=val, response=resp,
                   case_seconds=perf_counter() - t0)
        if c["object"] == "B":
            rec["beam_reference"] = beam_reference(c["E"], c["nu"], c["t"])
        results.append(rec)
        short = {r["method"]: (r["iterations"], r["accepted"]) for r in recs}
        log(f"{c['name']:<22} n={diag['unknowns']:>5} kappa={diag['kappa2']:.4e} "
            f"rhoJ={diag['rho_J']:.5f} resp={resp['matched_value_mm']:.6f} mm "
            f"Fimb={val['force_imbalance_rel']:.1e} {short} ({rec['case_seconds']:.1f}s)")
        for r in recs:
            log("   ", json.dumps({k: v for k, v in r.items() if k != "timing_note"}))

    # ---- negative control: roller-only support leaves a rigid vertical translation
    m, K, f, cons, A, b, free, d, _ = build_system(
        dict(object="H", level=0, E=E0, nu=NU0, t=T0, loads=[(RIGHT, (P0, 0))],
             supports=ROLLER_ONLY), mcache, kcache)
    ev = eigvalsh(A.toarray())
    try:
        cholesky(A.toarray(), lower=True)
        chol = "success (numerically; check eigenvalues)"
    except np.linalg.LinAlgError as exc:
        chol = f"failed: {exc}"
    neg = dict(case="H-rolleronly-L1", supports="u_x = 0 on left edge only", unknowns=int(A.shape[0]),
               lambda_min=float(ev[0]), lambda_2=float(ev[1]), lambda_max=float(ev[-1]),
               lambda_min_over_max=float(ev[0] / ev[-1]), dense_cholesky=chol,
               note="expected one zero eigenvalue (rigid vertical translation); not solved")
    log("negative control", json.dumps(neg))

    # ---- structured comparison for the square (fem/plate.py rectangle mesh, same load)
    structured = []
    for n in (10, 20, 30, 40):
        s = force_driven(n)
        A, b = s["A"], s["b"]
        x = splu(A.tocsc()).solve(b)
        dd = s["d"].copy()
        dd[s["free"]] = x
        U = dd.reshape(-1, 2)
        ids = {k: int(np.linalg.norm(s["nodes"] - np.asarray(p), axis=1).argmin())
               for k, p in OBJECTS["S"]["points"].items()}
        lo, hi = extreme_eigs(A.tocsr())
        its = {mth: iterative(A, b, mth, history=False)[1] for mth in ("CG", "PCG (diagonal)")}
        structured.append(dict(cells_per_side=n, nodes=len(s["nodes"]), triangles=len(s["triangles"]),
                               unknowns=len(b), stored_nnz=int(A.nnz), kappa2=hi / lo,
                               right_mid_ux_mm=float(U[ids["right_mid"], 0] * 1e3),
                               top_right_ux_mm=float(U[ids["top_right"], 0] * 1e3),
                               cg_iterations=int(its["CG"]), pcg_iterations=int(its["PCG (diagonal)"])))
        log("structured", json.dumps(structured[-1]))

    total = perf_counter() - t_start
    data = dict(
        environment=env, protocol=dict(tol=TOL, cap=CAP, x0="zeros", methods_full=METHODS,
                                       methods_core=CORE, eig_tol=EIG_TOL,
                                       eig_note="eigsh on every system (shift-invert sigma=0 was fast enough everywhere; none skipped)",
                                       gauss_seidel_policy="Gauss-Seidel timed best-of-3 with separate history only on levels 1-2 base meshes; elsewhere one timed run without history (each capped run costs ~5-20 s)",
                                       timing="best of 3 perf_counter runs, excluding assembly, diagnostics, history runs"),
        settings=dict(E_Pa=E0, nu=NU0, t_m=T0, p_Pa=P0, tau_beam_Pa=TAU_BEAM, min_angle_deg=MIN_ANGLE,
                      max_area_rule="a_max = sqrt(3)/4 h^2 (equilateral triangle of side h); boundary segments split to length <= h",
                      markers=dict(bottom=BOTTOM, right=RIGHT, top=TOP, left=LEFT, hole=HOLE,
                                   inner_horizontal=INNER_H, inner_vertical=INNER_V)),
        objects={k: dict(title=v["title"], reason=v["reason"], outer=v["outer"], markers=v["markers"],
                         holes=v["holes"], levels_h=v["levels"], points=v["points"])
                 for k, v in OBJECTS.items()},
        cases=results, negative_control=neg, structured_square=structured,
        total_seconds=total)
    (OUT / "objects.json").write_text(json.dumps(data, indent=1) + "\n")
    np.savez_compressed(OUT / "histories.npz", **hist_store)
    with (OUT / "meshes.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        keys = ["h", "nodes", "triangles", "boundary_segments", "min_angle_deg", "max_angle_deg",
                "min_area", "edge_min", "edge_max", "area_rel_error_vs_pslg",
                "area_rel_diff_vs_true_geometry", "boundary_edges_equal_segments",
                "centroids_in_holes", "connected_components", "euler_characteristic"]
        w.writerow(["object", "level"] + keys)
        for (o, lev), m in sorted(mcache.items()):
            w.writerow([o, lev + 1] + [m["checks"][k] for k in keys])
    with (OUT / "cases.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        dk = ["unknowns", "stored_nnz", "numeric_nnz", "lambda_min", "lambda_max", "kappa2", "rho_J"]
        w.writerow(["case", "object", "level", "question", "E_Pa", "nu"] + dk +
                   ["matched_point", "matched_component", "matched_value_mm", "max_abs_displacement_mm",
                    "force_imbalance_rel", "moment_imbalance_rel"])
        for r in results:
            w.writerow([r["name"], r["object"], r["level"], r["question"], r["E_Pa"], r["nu"]] +
                       [r["diagnostics"][k] for k in dk] +
                       [r["response"]["matched_point"], r["response"]["matched_component"],
                        r["response"]["matched_value_mm"], r["response"]["max_abs_displacement_mm"],
                        r["validation"]["force_imbalance_rel"], r["validation"]["moment_imbalance_rel"]])
    with (OUT / "solver_runs.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        sk = ["method", "iterations", "relative_residual", "relative_error", "accepted", "status",
              "best_seconds", "timing_runs"]
        w.writerow(["case", "unknowns"] + sk)
        for r in results:
            for s in r["solvers"]:
                w.writerow([r["name"], r["diagnostics"]["unknowns"]] + [s.get(k) for k in sk])
    log(f"total {total:.1f} s")


if __name__ == "__main__":
    main()
