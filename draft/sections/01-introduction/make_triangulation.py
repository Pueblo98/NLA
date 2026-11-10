"""Generate an illustrative mesh diagram, not a selected simulation case.

Run with Python plus NumPy, SciPy and Matplotlib. No Triangle dependency:
this axis-aligned example uses SciPy Delaunay followed by an exact domain
filter. Project meshes should use boundary-constrained triangulation.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
import numpy as np
from scipy.spatial import Delaunay


def build_mesh():
    boundary = np.array([(0, 0), (3, 0), (3, 1), (1.5, 1), (1.5, 2), (0, 2)])
    points = np.array([
        (x, y)
        for y in np.arange(0, 2.01, 0.5)
        for x in np.arange(0, 3.01, 0.5)
        if x <= 1.5 or y <= 1
    ])
    cells = Delaunay(points).simplices
    centres = points[cells].mean(axis=1)
    cells = cells[(centres[:, 0] < 1.5) | (centres[:, 1] < 1)]

    # Check the filled cells cover precisely this L-shaped region.
    corners = points[cells]
    a, b = corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]
    areas = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]) / 2
    assert np.all(areas > 0)
    assert np.isclose(areas.sum(), 4.5)
    assert not np.any((corners[:, :, 0] > 1.5).any(axis=1)
                      & (corners[:, :, 1] > 1).any(axis=1))
    edges = np.sort(np.concatenate([cells[:, [0, 1]], cells[:, [1, 2]],
                                    cells[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    assert np.all((counts == 1) | (counts == 2))
    return boundary, points, cells


def main():
    boundary, points, cells = build_mesh()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.05))
    fig.subplots_adjust(left=0.015, right=0.99, top=0.83, bottom=0.02, wspace=0.20)
    for ax, title in zip(axes, ["Continuous region", "Same region, triangular mesh"]):
        ax.set_aspect("equal")
        ax.set_xlim(-0.12, 3.12)
        ax.set_ylim(-0.12, 2.12)
        ax.set_axis_off()
        ax.set_title(title, fontsize=10, pad=7)
    axes[0].add_patch(Polygon(boundary, facecolor="#dbe8ef", edgecolor="#234653",
                              linewidth=1.5))
    axes[0].text(0.77, 0.85, "Solid region", ha="center", color="#234653")
    axes[1].add_collection(PolyCollection(points[cells], facecolor="#dbe8ef",
                                          edgecolor="#54788a", linewidth=0.65))
    axes[1].add_patch(Polygon(boundary, fill=False, edgecolor="#234653", linewidth=1.5))
    axes[1].scatter(*points.T, s=9, color="#234653", zorder=3)
    highlight = np.argmin(np.linalg.norm(points[cells].mean(axis=1) - [0.8, 0.7], axis=1))
    axes[1].add_patch(Polygon(points[cells[highlight]], facecolor="#e7b35c",
                              edgecolor="#8d641e", linewidth=1, zorder=2))
    axes[1].annotate("Filled triangle", xy=points[cells[highlight]].mean(axis=0),
                     xytext=(1.85, 1.45), fontsize=9, color="#234653",
                     arrowprops={"arrowstyle": "-", "color": "#8d641e", "lw": 0.8})
    output = Path(__file__).resolve().parent / "figures"
    output.mkdir(exist_ok=True)
    fig.savefig(output / "triangulation.pdf", metadata={"Title": "Region and triangular mesh",
                                                         "Author": "NLA Group 2"})
    fig.savefig(output / "triangulation.png", dpi=220)
    plt.close(fig)
    print(f"Verified diagram: {len(points)} nodes, {len(cells)} triangles, total area 4.5.")


if __name__ == "__main__":
    main()
