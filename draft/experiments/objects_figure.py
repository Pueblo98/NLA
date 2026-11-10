"""Figure for Section 5: the four objects on their coarsest Triangle meshes,
with clamped edges, loads, support variant and matched response points.

Run from the repository root:  python3 draft/experiments/objects_figure.py
Writes draft/sections/05-objects-and-experiments/figures/objects_meshes.{pdf,png}.
Meshes are regenerated deterministically with objects.mesh (same settings as the runs).
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import objects as O  # noqa: E402

FIG = O.ROOT / "draft" / "sections" / "05-objects-and-experiments" / "figures"
INK, MUTED, MESH = "#0b0b0b", "#52514e", "#b9b8b2"
LOAD, ALT = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6})


def draw_mesh(ax, m):
    ax.triplot(m["nodes"][:, 0], m["nodes"][:, 1], m["triangles"], color=MESH, lw=0.4)
    for (i, j), mk in zip(m["segments"], m["segment_markers"]):
        ax.plot(*m["nodes"][[i, j]].T, color=INK, lw=0.9, solid_capstyle="round")


def clamp(ax, x, y0, y1, depth):
    ax.plot([x, x], [y0, y1], color=INK, lw=2.2)
    for y in np.linspace(y0, y1, max(4, int((y1 - y0) / depth / 1.2))):
        ax.plot([x, x - depth], [y, y - depth], color=INK, lw=0.6)


def arrows(ax, pts, vec, color, ls="-"):
    for p in pts:
        ax.annotate("", xy=p + vec, xytext=p,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.9, ls=ls,
                                    mutation_scale=7, shrinkA=0, shrinkB=0))


def point(ax, xy, label, dx=0.03, dy=0.03, ha="left"):
    ax.plot(*xy, "o", ms=4.2, mfc="white", mec=INK, mew=0.9, zorder=5)
    ax.text(xy[0] + dx, xy[1] + dy, label, ha=ha, va="bottom", color=INK, fontsize=7)


def panel(ax, obj, title):
    m = O.mesh(obj, 0)
    draw_mesh(ax, m)
    ax.set_aspect("equal")
    ax.axis("off")
    c = m["checks"]
    ax.set_title(f"{title}: {c['nodes']} nodes, {c['triangles']} triangles",
                 fontsize=8, color=INK, pad=3)
    return m


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6.3, 2.75))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.36], hspace=0.12, wspace=0.08,
                          left=0.02, right=0.98, top=0.94, bottom=0.0)
    ys = np.linspace(0.05, 0.95, 7)
    # (a) square
    ax = fig.add_subplot(gs[0, 0])
    panel(ax, "S", "(a) S")
    clamp(ax, 0, 0, 1, 0.05)
    arrows(ax, np.column_stack([np.ones(7), ys]), np.array([0.16, 0]), LOAD)
    point(ax, (1, .5), "", 0, 0)
    point(ax, (1, 1), "", 0, 0)
    ax.set_xlim(-0.1, 1.2); ax.set_ylim(-0.05, 1.1)
    # (b) hole plate
    ax = fig.add_subplot(gs[0, 1])
    panel(ax, "H", "(b) H")
    clamp(ax, 0, 0, 1, 0.05)
    arrows(ax, np.column_stack([np.ones(7), ys]), np.array([0.16, 0]), LOAD)
    point(ax, (1, .5), "", 0, 0)
    point(ax, (.5, .65), "", 0, 0)
    ax.plot(0, .5, marker=">", ms=6, mfc=ALT, mec=INK, mew=0.6, zorder=6)
    ax.text(0.04, 0.52, "variant:\nroller + pin", fontsize=6, color=MUTED, va="bottom")
    ax.set_xlim(-0.1, 1.2); ax.set_ylim(-0.05, 1.1)
    # (c) L-bracket
    ax = fig.add_subplot(gs[0, 2])
    panel(ax, "L", "(c) L")
    clamp(ax, 0, 0, 1, 0.05)
    arrows(ax, np.column_stack([np.ones(4), np.linspace(0.05, 0.45, 4)]), np.array([0.16, 0]), LOAD)
    arrows(ax, np.column_stack([np.linspace(0.05, 0.45, 4), np.ones(4)]), np.array([0, 0.16]), ALT,
           ls="--")
    point(ax, (1, .25), "", 0, 0)
    point(ax, (.25, 1), "", 0, 0)
    ax.plot(.5, .5, marker="x", ms=5, color=INK, mew=1.0, zorder=6)
    ax.set_xlim(-0.1, 1.2); ax.set_ylim(-0.05, 1.2)
    # (d) beam
    ax = fig.add_subplot(gs[1, :])
    panel(ax, "B", "(d) B (4 m x 0.5 m)")
    clamp(ax, 0, 0, .5, 0.06)
    # downward shear traction on the tip face, drawn just outside the edge
    arrows(ax, np.column_stack([np.full(3, 4.07), [0.16, 0.32, 0.48]]),
           np.array([0, -0.1]), LOAD)
    point(ax, (4, .25), "", 0, 0)
    ax.set_xlim(-0.15, 4.3); ax.set_ylim(-0.1, 0.6)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"objects_meshes.{ext}", dpi=220)
    print("wrote", FIG / "objects_meshes.pdf")


if __name__ == "__main__":
    main()
