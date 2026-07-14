#!/usr/bin/env python3
"""Kid-friendly charts for the poster, derived from simulation results."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans",
                     "axes.edgecolor": "#334", "text.color": "#223",
                     "axes.labelcolor": "#223", "xtick.color": "#223",
                     "ytick.color": "#223"})

NAVY, RED, GREEN, GOLD = "#1b2a5e", "#e4572e", "#2e933c", "#f3a712"

# ---------- chart 1: domino score vs constellation size (from sim) --------
N = np.array([100, 316, 1000, 3162, 10000, 25000, 100000])
R0 = np.array([6.2e-5, 1.5e-4, 4.7e-4, 1.3e-3, 6.0e-3, 2.8e-2, 3.1e-1])

fig, ax = plt.subplots(figsize=(8.8, 4.1))
ax.axhspan(1, 300, color=RED, alpha=0.15)
ax.axhline(1, color=RED, lw=3)
ax.text(130, 1.8, "DANGER LINE: above this, crashes snowball!",
        color=RED, fontsize=14, fontweight="bold")
ax.loglog(np.append(N, 1e6), np.append(R0, 140.0), "o-", color=NAVY, lw=3,
          ms=11, label="one lane (crammed)")
ax.loglog([1e6], [140.0], "*", color=RED, ms=28)
ax.annotate("1 MILLION in ONE lane:\nOVER the line - chain reaction!",
            xy=(1e6, 140.0), xytext=(3.5e2, 25), fontsize=13,
            fontweight="bold", color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax.loglog([1e6], [2.8e-2], "D", color=GREEN, ms=14)
ax.annotate("1 MILLION spread over\n40 lanes: 35x below\nthe line - SAFE",
            xy=(1e6, 2.8e-2), xytext=(1.1e4, 3.5e-4), fontsize=13,
            fontweight="bold", color=GREEN,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=2))
ax.set_xlabel("number of satellites", fontweight="bold")
ax.set_ylabel('"domino score" after one crash', fontweight="bold")
ax.set_ylim(1e-5, 300); ax.set_xlim(80, 2e6)
ax.set_yticks([1e-4, 1e-2, 1])
ax.set_yticklabels(["1 in 10,000", "1 in 100", "1 (snowball!)"])
ax.legend(loc="lower right", fontsize=12)
ax.grid(alpha=0.3, which="both")
fig.tight_layout(); fig.savefig("chart_domino.png", dpi=170,
                                facecolor="white")

# ---------- chart 2: space cleans itself (fragment decay, from sim) -------
d = np.load("detail_run.npy", allow_pickle=True)[0]
t, nf, ns = d["ts"]["t"], d["ts"]["n_frag"], d["ts"]["n_small"]
m = (t > 4.5) & (t < 30)
fig, ax = plt.subplots(figsize=(8.8, 4.1))
ax.fill_between(t[m] - 5, nf[m] + ns[m], color=GOLD, alpha=0.35,
                label="tiny bits (1-10 cm)")
ax.fill_between(t[m] - 5, nf[m], color=RED, alpha=0.75,
                label="big pieces (>10 cm)")
ax.set_xlim(-0.5, 20)
ax.set_yscale("symlog", linthresh=10)
ax.set_yticks([0, 10, 100, 1000, 10000])
ax.set_yticklabels(["0", "10", "100", "1,000", "10,000"])
ax.set_xlabel("years after the crash", fontweight="bold")
ax.set_ylabel("pieces of junk still up there", fontweight="bold")
ax.annotate("CRASH!\n~17,000 pieces", xy=(0, 15000), xytext=(3.0, 6000),
            fontsize=14, fontweight="bold", color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=2))
ax.annotate("air drag pulls junk down\nuntil it burns up\nlike shooting stars",
            xy=(8, 60), xytext=(10.5, 400), fontsize=13, color=NAVY,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
ax.legend(loc="upper right", fontsize=12)
ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("chart_cleanup.png", dpi=170,
                                facecolor="white")
print("charts done")
