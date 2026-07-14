#!/usr/bin/env python3
"""Publication-style R0 scaling figure: fitted small-N regime, direct
large-N simulations showing superlinear departure, supercritical 1e6 point."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Serif",
                     "axes.linewidth": 0.8})

# small-N sweep (analytic estimator, converged)
N_lo = np.array([100, 316, 1000, 3162, 10000])
R_lo = np.array([3.5e-5, 9.1e-5, 2.37e-4, 7.31e-4, 2.07e-3])
c = np.polyfit(np.log10(N_lo), np.log10(R_lo), 1)
slope = c[0]

# direct large-N simulations
N_hi = np.array([25000, 100000])
R_hi = np.array([1.378e-2, 9.126e-2])
N_sc, R_sc = 1e6, 21.96          # supercritical, E[sec] at +5 yr, growing

Nx = np.logspace(2, 6.2, 80)
R_fit = 10 ** np.polyval(c, np.log10(Nx))

fig, ax = plt.subplots(figsize=(7, 5))
ax.axhline(1.0, color="crimson", lw=1.5, ls="--")
ax.text(1.3e2, 1.5, r"cascade criticality $R_0 = 1$", color="crimson",
        fontsize=10)

ax.loglog(Nx, R_fit, ":", color="steelblue", lw=1.5,
          label=rf"low-$N$ power law $R_0 \propto N^{{{slope:.2f}}}$"
                "\n(underestimates beyond $N \\sim 10^4$)")
ax.loglog(N_lo, R_lo, "o", color="k", ms=7, zorder=5,
          label="simulation, single shell (converged)")
ax.loglog(N_hi, R_hi, "s", color="darkorange", ms=8, zorder=6,
          label="direct simulation, superlinear regime")
ax.loglog([N_sc], [R_sc], "^", color="crimson", ms=11, zorder=7)
ax.annotate("$N=10^6$, single shell: SUPERCRITICAL\n"
            r"($E$[secondaries] $\approx 22$ by +5 yr, still growing)",
            xy=(N_sc, R_sc), xytext=(9e2, 2.2e1), fontsize=9.5,
            color="crimson",
            arrowprops=dict(arrowstyle="->", lw=1, color="crimson"))
ax.loglog([1e6], [1.378e-2], "D", color="seagreen", ms=8, zorder=6)
ax.annotate(r"$10^6$ across 40 shells (25,000/shell,"
            "\ndirect simulation): $R_0 = 0.014$ per shell",
            xy=(1e6, 1.378e-2), xytext=(1.3e2, 8e-2), fontsize=9.5,
            color="seagreen",
            arrowprops=dict(arrowstyle="->", lw=1, color="seagreen"))
# connect superlinear trend
Nc = np.array([10000, 25000, 100000, 1e6])
Rc = np.array([2.07e-3, 1.378e-2, 9.126e-2, R_sc])
ax.loglog(Nc, Rc, "-", color="darkorange", lw=1.2, alpha=0.6, zorder=3)

ax.set_xlabel("constellation size $N$ (satellites in shell)")
ax.set_ylabel(r"$R_0$: expected secondary collisions per breakup")
ax.set_xlim(80, 4e6); ax.set_ylim(1e-5, 2e2)
ax.legend(loc="lower right", fontsize=8.5)
ax.grid(alpha=0.3, which="both", lw=0.4)
fig.tight_layout()
fig.savefig("paper_fig5_r0_scaling.png", dpi=170, facecolor="white")
print("done; low-N slope =", slope)
