"""Deformed plate plot for Ernesto's force-driven case (20 x 20 cells, sparse direct solve).

Saves figures/deformed_plate_force_20x20.png. Run: python fem/plot_deformed.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.tri import Triangulation  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402

from plate import force_driven  # noqa: E402

SCALE = 200
s = force_driven(20)
d = s["d"]
d[s["free"]] = spsolve(s["A"].tocsc(), s["b"])
U = d.reshape(-1, 2)
xy = s["nodes"] + SCALE * U
mag = np.linalg.norm(U, axis=1) * 1e3

fig, ax = plt.subplots(figsize=(6, 5))
tri = Triangulation(xy[:, 0], xy[:, 1], s["triangles"])
pc = ax.tripcolor(tri, mag, shading="gouraud", cmap="viridis")
ax.triplot(tri, color="white", lw=0.3, alpha=0.5)
ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], "k--", lw=1, label="original plate")
fig.colorbar(pc, ax=ax, label="displacement magnitude [mm]")
ax.set_aspect("equal"); ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
ax.set_title(f"Deformed plate, 20 x 20 cells, displacements x{SCALE}")
ax.legend(loc="upper right")
out = os.path.join(os.path.dirname(__file__), "..", "figures", "deformed_plate_force_20x20.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
right = s["side"]["right"]
print(f"max u on right edge {U[right, 0].max() * 1e3:.3f} mm; "
      f"max inward v on top/bottom {max(-U[s['side']['top'], 1].min(), U[s['side']['bottom'], 1].max()) * 1e3:.3f} mm")
print("saved", os.path.normpath(out))
