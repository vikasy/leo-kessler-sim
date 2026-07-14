#!/usr/bin/env python3
"""Figure 7: regime map. Cascade stability vs satellites-per-shell and
operational quality, from the 4x5 simulation grid."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from scipy.interpolate import RegularGridInterpolator

plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans", "lines.linewidth": 2.0,
                     "axes.linewidth": 0.8})

# simulation grid: rows = ops quality q, cols = N per shell
q = np.array([0.25, 0.50, 0.75, 1.00])
N = np.array([1e3, 1e4, 2.5e4, 1e5, 1e6])
R0 = np.array([
    [2.32e-3, 1.29e-1, 1.62e+0, 2.92e+1, 8.0e+3],    # q=0.25 poor
    [1.36e-3, 1.28e-2, 2.53e-1, 6.88e+0, 2.92e+3],   # q=0.50 degraded
    [4.68e-4, 6.00e-3, 2.81e-2, 3.14e-1, 1.41e+2],   # q=0.75 baseline
    [1.04e-4, 5.98e-4, 6.20e-3, 7.74e-3, 5.90e-1],   # q=1.00 excellent
])
# direct criticality brackets (lo, hi) per ops row, from simulation
bracket = {0.25: (1.5e4, 2.5e4), 0.50: (2.5e4, 5.0e4), 0.75: (1.5e5, 2.0e5)}

interp = RegularGridInterpolator((q, np.log10(N)), np.log10(R0),
                                 method="linear")
qq = np.linspace(0.25, 1.0, 220)
nn = np.linspace(3, 6, 300)
QQ, NN = np.meshgrid(qq, nn, indexing="ij")
Z = interp(np.stack([QQ.ravel(), NN.ravel()], axis=1)).reshape(QQ.shape)

fig, ax = plt.subplots(figsize=(7.6, 5.2))
cmap = ListedColormap(["#009E73", "#F0E442", "#D55E00"])
ax.contourf(10**NN, QQ, Z, levels=[-9, -1, 0, 9], cmap=cmap, alpha=0.55)
cs = ax.contour(10**NN, QQ, Z, levels=[-1, 0], colors=["#005a45", "#8a3800"],
                linewidths=[1.5, 2.5])
ax.clabel(cs, fmt={-1: r"$R_0 = 0.1$", 0: r"$R_0 = 1$ (criticality)"},
          fontsize=9)
ax.set_xscale("log")

# grid points actually simulated
for i, qv in enumerate(q):
    ax.plot(N, np.full_like(N, qv), "o", color="k", ms=3, alpha=0.45)
# direct criticality brackets per row
for qv, (lo, hi) in bracket.items():
    ax.plot([lo, hi], [qv, qv], "-", color="#7f1010", lw=5, alpha=0.85,
            solid_capstyle="butt", zorder=5)
ax.plot([], [], "-", color="#7f1010", lw=5, label="direct $R_0{=}1$ bracket")

# overlays: (N per shell, ops quality, label, offsets)
cases = [
    (1600, 0.90, "Starlink Gen1\n(~1,600/shell)", (0.28, 0.055), "k", "o"),
    (1200, 0.75, "Kuiper\n(~1,200/shell)", (0.32, -0.02), "k", "o"),
    (648, 0.60, "OneWeb*\n(648, 1,200 km)", (0.25, -0.12), "gray", "s"),
    (2.5e4, 0.75, "1M across\n40 shells", (0.0, 0.06), "navy", "D"),
    (1e6, 0.75, "1M in one shell\n(baseline ops)", (-0.55, 0.055), "navy", "^"),
    (2.5e4, 0.25, "pessimistic ops\n(Sec. 4.6)", (0.0, 0.05), "firebrick", "v"),
    (1e6, 1.00, "1M one shell,\nexcellent ops", (-0.6, -0.14), "navy", "*"),
]
for n0, q0, lab, (dx, dy), col, mk in cases:
    ax.plot([n0], [q0], mk, color=col, ms=9 if mk != "*" else 14,
            mec="white", mew=0.8, zorder=6)
    ax.annotate(lab, xy=(n0, q0), xytext=(n0 * 10**dx, q0 + dy),
                fontsize=8.2, color=col, ha="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=col, alpha=0.6))

ax.set_xlabel("satellites per shell $N$")
ax.set_ylabel("operational quality")
ax.set_yticks([0.25, 0.50, 0.75, 1.00])
ax.set_yticklabels(["poor\n90% avoid, 85% PMD,\n2%/yr fail",
                    "degraded\n95%, 90%, 1%/yr",
                    "baseline\n99%, 95%, 0.5%/yr",
                    "excellent\n99.9%, 99%, 0.2%/yr"], fontsize=8)
ax.set_xlim(4e2, 3e6); ax.set_ylim(0.22, 1.06)
legend = [Patch(fc="#009E73", alpha=0.55, label=r"stable ($R_0 < 0.1$)"),
          Patch(fc="#F0E442", alpha=0.55, label=r"marginal ($0.1 \leq R_0 < 1$)"),
          Patch(fc="#D55E00", alpha=0.55, label=r"supercritical ($R_0 \geq 1$)")]
from matplotlib.lines import Line2D
legend.append(Line2D([0],[0], color="#7f1010", lw=5, label="direct $R_0{=}1$ bracket"))
ax.legend(handles=legend, loc="lower left", fontsize=8.5, framealpha=0.9)
fig.tight_layout()
fig.savefig("paper_fig7_regime_map.png", dpi=300, facecolor="white")
fig.savefig("paper_fig7_regime_map.pdf")
print("regime map done")
