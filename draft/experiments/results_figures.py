"""Figures for Section 6 (results and validation).

Run from the repository root:  python3 draft/experiments/results_figures.py
Reads only finished outputs:
    draft/experiments/results/objects/cases.csv, solver_runs.csv
    draft/experiments/results/square/refinement.json
and re-solves one level-2 mesh of H, L and B with sparse LU (a few seconds) for the
deformed-shape plot, using the unchanged case definitions of objects.py.
Writes draft/sections/06-results-and-validation/figures/results_{deformed,scaling}.{pdf,png}
and prints the fitted log-log slopes and the plotted extrema.
"""
from pathlib import Path
import csv
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from scipy.sparse.linalg import splu  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import objects as O  # noqa: E402

RES = O.ROOT / "draft" / "experiments" / "results"
FIG = O.ROOT / "draft" / "sections" / "06-results-and-validation" / "figures"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dddcd6"
# categorical slots 1-5 of the reference palette, fixed order, plus distinct markers
SERIES = [("grid", "Structured square", "#52514e", "s"),
          ("S", "S (square)", "#2a78d6", "o"),
          ("H", "H (hole)", "#eb6834", "^"),
          ("L", "L (bracket)", "#1baf7a", "D"),
          ("B", "B (beam)", "#6250d6", "v")]
plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ deformed shapes
def deformed():
    cases = {c["name"]: c for c in O.build_cases()}
    spec = [("H-base-L2", "H: plate with hole", 100), ("L-base-L2", "L: bracket", 100),
            ("B-base-L2", "B: beam", 5)]
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 1.85),
                             gridspec_kw=dict(width_ratios=[1, 1, 2.6], wspace=0.08))
    vmax = 400.0
    for ax, (name, title, amp) in zip(axes, spec):
        c = cases[name]
        m, K, f, cons, A, b, free, d, _ = O.build_system(c, {}, {})
        d = d.copy()
        d[free] = splu(A.tocsc()).solve(b)
        sig, vm = O.element_stress(m, d, c["E"], c["nu"])
        xy = m["nodes"] + amp * d.reshape(-1, 2)
        pc = PolyCollection(xy[m["triangles"]], array=vm / 1e6, cmap="Blues",
                            edgecolors="face", linewidths=0.1)
        pc.set_clim(0, vmax)
        ax.add_collection(pc)
        for i, j in m["segments"]:
            ax.plot(*m["nodes"][[i, j]].T, color=MUTED, lw=0.6, ls=(0, (2, 1.5)))
        ax.set_aspect("equal")
        ax.autoscale_view()
        ax.axis("off")
        ax.set_title(f"{title} (×{amp})", fontsize=8, color=INK, pad=2)
        print(f"{name}: max |u| = {1e3 * np.abs(d.reshape(-1, 2)).max():.3f} mm (component), "
              f"max VM = {vm.max() / 1e6:.0f} MPa, amp {amp}")
    cb = fig.colorbar(pc, ax=axes, fraction=0.025, pad=0.01, extend="max")
    cb.set_label("von Mises stress (MPa)", fontsize=7)
    cb.ax.tick_params(labelsize=7)
    save(fig, "results_deformed")


# ------------------------------------------------------------ scaling
def slope(N, y):
    return np.polyfit(np.log(N), np.log(y), 1)[0]


def scaling():
    data = {}
    with open(RES / "objects" / "cases.csv") as fh:
        rows = [r for r in csv.DictReader(fh) if "-base-" in r["case"]]
    with open(RES / "objects" / "solver_runs.csv") as fh:
        cg = {r["case"]: int(r["iterations"]) for r in csv.DictReader(fh) if r["method"] == "CG"}
    for o in "SHLB":
        rs = sorted((r for r in rows if r["object"] == o), key=lambda r: int(r["level"]))
        data[o] = (np.array([int(r["unknowns"]) for r in rs]),
                   np.array([float(r["kappa2"]) for r in rs]),
                   np.array([cg[r["case"]] for r in rs]))
    ref = json.loads((RES / "square" / "refinement.json").read_text())["meshes"]
    data["grid"] = (np.array([r["unknowns"] for r in ref]), np.array([r["kappa2"] for r in ref]),
                    np.array([r["cg_iterations"] for r in ref]))
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.35), gridspec_kw=dict(wspace=0.32))
    for key, label, col, mk in SERIES:
        N, k, it = data[key]
        sk, si = slope(N, k), slope(N, it)
        print(f"{key}: N {N.min()}-{N.max()}, kappa2 slope {sk:.2f}, CG slope {si:.2f}")
        for ax, y, s in ((axes[0], k, sk), (axes[1], it, si)):
            ax.loglog(N, y, color=col, marker=mk, ms=4.5, lw=1.5, mfc=col, mec="white", mew=0.6,
                      label=f"{label}, slope {s:.2f}")
    axes[0].set_ylabel(r"condition number $\kappa_2(A)$")
    axes[1].set_ylabel("CG iterations to $\\eta<10^{-8}$")
    for ax, t in zip(axes, ("(a)", "(b)")):
        ax.set_xlabel("unknowns $N$")
        ax.grid(True, which="major", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.text(0.02, 0.98, t, transform=ax.transAxes, va="top", fontsize=8, color=INK)
        ax.legend(fontsize=6, frameon=False, loc="lower right", handlelength=1.6)
    save(fig, "results_scaling")


if __name__ == "__main__":
    deformed()
    scaling()
