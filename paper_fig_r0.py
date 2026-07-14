#!/usr/bin/env python3
"""Publication R0 scaling figure — corrected-physics production data
(tumbling-averaged derelict drag area, latitude-band volume), direct
criticality bracketing, mean-field curve shown as qualitative mechanism."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans",
                     "lines.linewidth": 2.0, "axes.linewidth": 0.8})

# near-linear regime (multi-seed means)
N_lo = np.array([100, 316, 1000, 3162, 10000])
R_lo = np.array([6.18e-5, 1.47e-4, 4.68e-4, 1.32e-3, 6.00e-3])
E_lo = np.array([1.6e-5, 0.28e-4, 0.35e-4, 0.09e-3, 2.5e-3])
c, cov = np.polyfit(np.log10(N_lo), np.log10(R_lo), 1, cov=True)
slope, sl_err = c[0], np.sqrt(cov[0, 0])

# boundary region (direct simulation, dt = 5 d)
N_hi = np.array([25000, 50000, 100000, 150000, 200000])
R_hi = np.array([2.81e-2, 3.51e-2, 3.14e-1, 1.03, 1.92])
E_hi = np.array([1.67e-2, 1.4e-2, 0.90e-1, 0.3, 0.08])
N_sc, R_sc = 1e6, 141.0        # 3 seeds, dt=10 d, +3 yr post-strike

# mean-field curve (qualitative mechanism; single-pole form)
Nstar_mf = 2.1e5
Nx = np.logspace(2, np.log10(Nstar_mf * 0.985), 200)
R_mf = 10 ** np.polyval(c, np.log10(Nx)) / (1 - Nx / Nstar_mf)

fig, ax = plt.subplots(figsize=(7, 5))
ax.axhline(1.0, color="#CC3311", lw=1.5, ls="--")
ax.text(1.3e2, 1.5, r"cascade criticality $R_0 = 1$", color="#CC3311",
        fontsize=10)
# direct criticality bracket
ax.axvspan(1.0e5, 1.5e5, color="#CC3311", alpha=0.12)
ax.text(1.06e5, 2.5e-4, "criticality\nbracketed\ndirectly:\n$N_{crit} \\approx 1.4{\\times}10^5$",
        fontsize=8.5, color="#993322")

Nfit = np.logspace(2, 6.2, 60)
ax.loglog(Nfit, 10 ** np.polyval(c, np.log10(Nfit)), ":", color="#0072B2",
          lw=1.5, label=rf"near-linear law $R_0 \propto N^{{{slope:.2f}\pm{sl_err:.2f}}}$")
ax.loglog(Nx, R_mf, "--", color="#E69F00", lw=1.5, alpha=0.7,
          label=r"mean-field form (qualitative), Eq. (5)")
ax.errorbar(N_lo, R_lo, yerr=E_lo, fmt="o", color="k", ms=6, zorder=5,
            capsize=3, lw=1, label="simulation (4-30 seeds)")
ax.errorbar(N_hi, R_hi, yerr=E_hi, fmt="s", color="#E69F00", ms=7,
            zorder=6, capsize=4, lw=1.2,
            label="direct simulation, boundary region")
ax.loglog([N_sc], [R_sc], "^", color="#CC3311", ms=11, zorder=7)
ax.annotate("$N=10^6$, single shell: SUPERCRITICAL\n"
            r"($E$[secondaries] $\approx 140$ by +3 yr; all seeds"
            "\ncross criticality within the first year)",
            xy=(N_sc, R_sc), xytext=(4.5e2, 4e1), fontsize=9,
            color="#CC3311",
            arrowprops=dict(arrowstyle="->", lw=1, color="#CC3311"))
ax.loglog([25000], [8.8], "v", color="#882255", ms=9, zorder=7)
ax.annotate("pessimistic operations at\n25,000/shell: $R_0 \\approx 8$-$10$",
            xy=(25000, 8.8), xytext=(1.3e2, 3e-1), fontsize=9,
            color="#882255",
            arrowprops=dict(arrowstyle="->", lw=1, color="#882255"))
ax.loglog([1e6], [2.81e-2], "D", color="#009E73", ms=8, zorder=6)
ax.annotate(r"$10^6$ across 40 shells, baseline ops:"
            "\n$R_0 = 0.028$ per shell ($35\\times$ below criticality)",
            xy=(1e6, 2.81e-2), xytext=(2.2e3, 2.2e-3), fontsize=9,
            color="#009E73",
            arrowprops=dict(arrowstyle="->", lw=1, color="#009E73"))

ax.set_xlabel("constellation size $N$ (satellites in shell)")
ax.set_ylabel(r"$R_0$: expected fragment-involved secondary collisions")
ax.set_xlim(80, 4e6); ax.set_ylim(2e-5, 1e3)
ax.legend(loc="lower right", fontsize=8)
ax.grid(alpha=0.3, which="both", lw=0.4)
fig.tight_layout()
fig.savefig("paper_fig5_r0_scaling.png", dpi=300, facecolor="white")
fig.savefig("paper_fig5_r0_scaling.pdf")
print(f"slope {slope:.3f}+-{sl_err:.3f}")
