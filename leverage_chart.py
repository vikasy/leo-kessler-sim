#!/usr/bin/env python3
"""Parameter-leverage chart for the technical poster: how far each
parameter swings R0 across its examined range (Table 6, final paper)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})

items = [   # (label, R0 swing factor across examined range, color)
    ("Full operations loop\n(baseline → pessimistic)", 300, "#882255"),
    ("Atmospheric density\n(solar cycle, 0.3×–3×)", 280, "#0072B2"),
    ("Avoidance effectiveness\n(99% → off)", 160, "#D55E00"),
    ("Derelict tumbling area\n(25 → 6.25 m²)", 35, "#CC3311"),
    ("Shell population N\n(per decade, ∝ N⁰·⁹⁹)", 10, "#009E73"),
    ("Crossing velocity v_rel\n(4 → 12 km/s)", 4.3, "#E69F00"),
    ("Fragment yield (SBM ×2)", 1.4, "#56B4E9"),
    ("Bin size / time step\n(numerics)", 1.6, "#999999"),
]
labels = [i[0] for i in items][::-1]
vals = [i[1] for i in items][::-1]
cols = [i[2] for i in items][::-1]

fig, ax = plt.subplots(figsize=(7.6, 5.6))
y = np.arange(len(items))
ax.barh(y, vals, color=cols, alpha=0.85, height=0.62)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=11)
ax.set_xscale("log")
ax.set_xlabel("factor by which R$_0$ changes across the examined range", fontsize=12)
ax.set_xlim(1, 600)
for yi, v in zip(y, vals):
    ax.text(v * 1.15, yi, f"{v:g}×", va="center", fontsize=12, fontweight="bold")
ax.grid(alpha=0.3, axis="x", which="both", lw=0.5)
ax.set_title("What actually moves the cascade multiplier", fontsize=14, pad=10)
fig.tight_layout()
fig.savefig("poster_leverage.png", dpi=300, facecolor="white")
print("leverage chart done")
