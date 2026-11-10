"""Explanatory diagrams for the visual progress report; no new solver results.

Run from NLA/: python drafts/make_visual_progress_figures.py
"""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
from scipy.sparse.linalg import spsolve
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fem"))
from plate import rectangle_mesh, force_driven

OUT = ROOT / "figures" / "visual_progress"
OUT.mkdir(parents=True, exist_ok=True)
BLUE, TEAL, ORANGE, GRAY = "#214f73", "#147d85", "#bd692c", "#788693"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    fig, ax = plt.subplots(figsize=(10, 1.75))
    ax.set(xlim=(0, 10), ylim=(0, 1.7))
    ax.axis("off")
    stages = [("Describe the object", "outline, material\nloads and supports"),
              ("Divide into triangles", "two displacements\nat each node"),
              ("Balance the forces", "assemble and support\nthe stiffness system"),
              ("Solve and check", "deformation, residual\nand mesh comparison")]
    for i, (a, b) in enumerate(stages):
        x = i * 2.55
        ax.add_patch(Rectangle((x, .18), 2.25, 1.28, facecolor="#eff5f8", edgecolor=BLUE, lw=1.2))
        ax.text(x+1.125, 1.12, a, ha="center", va="center", weight="bold", fontsize=10.5, color=BLUE)
        ax.text(x+1.125, .61, b, ha="center", va="center", fontsize=10)
        if i < 3:
            ax.annotate("", (x+2.52, .82), (x+2.27, .82), arrowprops={"arrowstyle": "->", "color": TEAL, "lw": 2})
    save(fig, "model_path.png")

    fig, axes = plt.subplots(1, 3, figsize=(10, 2.6))
    p = np.array([[0., 0.], [1., 0.], [0., 1.]])
    variants = [p + [.2, .08], p * [1.25, 1.], p @ np.array([[1., 0.], [.4, 1.]] )]
    titles = ["Move together", "Stretch horizontally", "Change the angle"]
    captions = ["No strain from translation", "Horizontal strain", "Shear strain"]
    for ax, q, title, caption in zip(axes, variants, titles, captions):
        ax.add_patch(Polygon(p, fill=False, edgecolor=GRAY, linestyle="--", lw=1.5))
        ax.add_patch(Polygon(q, facecolor="#d5edef", edgecolor=TEAL, alpha=.9, lw=1.8))
        ax.scatter(*q.T, s=22, c=TEAL)
        for a, b in zip(p, q):
            if np.linalg.norm(b-a) > .01:
                ax.annotate("", b, a, arrowprops={"arrowstyle": "->", "color": ORANGE, "lw": 1.5})
        ax.set_title(title, color=BLUE, weight="bold", fontsize=12)
        ax.text(.65, -.22, caption, ha="center", fontsize=10)
        ax.set(xlim=(-.18, 1.5), ylim=(-.33, 1.3), aspect="equal")
        ax.axis("off")
    fig.tight_layout()
    save(fig, "strain_intuition.png")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    nodes, tris, _, _ = rectangle_mesh(1, 1, 2, 2)
    ax.triplot(nodes[:, 0], nodes[:, 1], tris, color=GRAY, lw=1)
    ax.scatter(*nodes.T, s=22, color=BLUE)
    ax.plot([-.025, -.025], [0, 1], color=BLUE, lw=5)
    for y in np.linspace(0, 1, 5):
        ax.annotate("", (1.27, y), (1.02, y), arrowprops={"arrowstyle": "->", "color": ORANGE, "lw": 1.5})
    ax.text(-.12, .5, "both movements fixed", rotation=90, ha="center", va="center", fontsize=9)
    ax.text(1.12, 1.12, "traction p", ha="center", color=ORANGE)
    ax.set(xlim=(-.28, 1.4), ylim=(-.15, 1.28), aspect="equal", xlabel="x (m)", ylabel="y (m)")
    ax.set_title("9 nodes, 8 triangles, 12 free values", fontsize=11, color=BLUE)
    ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
    A = np.loadtxt(ROOT / "drafts/results/small_A.csv", delimiter=",")
    scaled = A / np.abs(A).max()
    im = axes[1].imshow(scaled, cmap="RdBu_r", vmin=-1, vmax=1)
    axes[1].set_title("The coupled 12 by 12 matrix", fontsize=11, color=BLUE)
    axes[1].set(xlabel="displacement index", ylabel="equilibrium equation index")
    axes[1].set_xticks([0, 5, 11], [1, 6, 12]); axes[1].set_yticks([0, 5, 11], [1, 6, 12])
    fig.colorbar(im, ax=axes[1], fraction=.046, pad=.04, label="entry / largest magnitude")
    fig.tight_layout()
    save(fig, "small_square_matrix.png")

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.1))
    for ax in axes:
        ax.set(xlim=(-.15, 1.15), ylim=(-.3, 1.2), aspect="equal")
        ax.axis("off")
    axes[0].add_patch(Rectangle((0, 0), 1, 1, facecolor="#d5edef", edgecolor=TEAL, lw=2))
    axes[1].add_patch(Rectangle((0, 0), 1, 1, facecolor="#f8eadf", edgecolor=ORANGE, lw=2))
    axes[1].add_patch(Circle((.5, .5), .21, facecolor="white", edgecolor=ORANGE, lw=2))
    axes[2].add_patch(Polygon([(0,0),(1,0),(1,.42),(.42,.42),(.42,1),(0,1)], facecolor="#f8eadf", edgecolor=ORANGE, lw=2))
    titles = ["Square: computed baseline", "Hole: candidate", "L-shape: candidate"]
    labels = ["Check methods and refinement", "How does an opening alter response?", "How does a corner affect refinement?"]
    for ax, title, label in zip(axes, titles, labels):
        ax.set_title(title, fontsize=11, color=BLUE, weight="bold")
        ax.text(.5, -.19, label, ha="center", fontsize=8.7)
    save(fig, "geometry_candidates.png")

    # Redraw saved measurements with readable, non-overlapping axis ticks.
    measurements = json.loads((ROOT / "drafts/results/benchmark.json").read_text())["refinement"]
    unknowns = [r["unknowns"] for r in measurements]
    fig, axes = plt.subplots(1, 2, figsize=(9.3, 3.2))
    for ax, key, title, ylabel, yticks in [
        (axes[0], "condition", "Conditioning", "estimated condition number", [2500, 10000, 35000]),
        (axes[1], "cg_iterations", "CG work", "iterations to the residual target", [100, 200, 500]),
    ]:
        ax.plot(unknowns, [r[key] for r in measurements], "o-", color=BLUE, lw=1.6, ms=6)
        ax.set(xscale="log", yscale="log", xlabel="free displacement unknowns", ylabel=ylabel)
        ax.set_title(title, color=BLUE, weight="bold", fontsize=12)
        ax.xaxis.set_major_locator(FixedLocator(unknowns))
        ax.yaxis.set_major_locator(FixedLocator(yticks))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_locator(NullLocator())
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:,.0f}"))
        ax.grid(alpha=.2)
        ax.margins(x=.12, y=.12)
    fig.tight_layout(w_pad=2.2)
    save(fig, "refinement_summary.png")

    # One untimed solve redraws the established square, without rerunning timings.
    baseline = force_driven(20)
    baseline["d"][baseline["free"]] = spsolve(baseline["A"].tocsc(), baseline["b"])
    displacement = baseline["d"].reshape(-1, 2)
    actual_max = float(displacement[baseline["side"]["right"], 0].max()*1e3)
    saved = json.loads((ROOT / "drafts/results/benchmark.json").read_text())["validation"]["maximum_right_u_mm"]
    assert np.isclose(actual_max, saved, rtol=1e-10)
    deformed = baseline["nodes"] + 200*displacement
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.55), layout="constrained")
    axes[0].triplot(*baseline["nodes"].T, baseline["triangles"], color="#a6bac7", lw=.35)
    axes[0].plot([0, 0], [0, 1], color=BLUE, lw=3)
    for y in np.linspace(.1, .9, 5):
        axes[0].annotate("", (1.12,y), (1.,y), arrowprops={"arrowstyle":"->", "color":ORANGE})
    colours = axes[1].tripcolor(*deformed.T, baseline["triangles"],
                               np.linalg.norm(displacement,axis=1)*1e3,
                               shading="gouraud", cmap="viridis")
    axes[1].triplot(*deformed.T, baseline["triangles"], color="white", lw=.22, alpha=.45)
    axes[1].plot([0,1,1,0,0], [0,0,1,1,0], "--", color="#222222", lw=1, label="original outline")
    axes[1].legend(loc="lower right", fontsize=8)
    for ax, title in zip(axes, ["Original square and loading", "Deformed square: displacement x200"]):
        ax.set(xlim=(-.06, 1.16), ylim=(-.06, 1.06), aspect="equal", xlabel="x (m)", ylabel="y (m)")
        ax.set_title(title, color=BLUE, fontsize=10.8, weight="bold")
    fig.colorbar(colours, ax=axes[1], shrink=.84, label="actual displacement magnitude (mm)", pad=.025)
    save(fig, "deformation_comparison.png")


if __name__ == "__main__":
    main()
