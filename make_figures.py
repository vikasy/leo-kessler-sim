#!/usr/bin/env python3
"""Figures for the Kessler-risk simulation: constellation health + cascade
diagnostics. Reads mc_runs.npy / detail_run.npy / summary.json."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "lines.linewidth": 2.0})

runs = list(np.load("mc_runs.npy", allow_pickle=True))
detail = np.load("detail_run.npy", allow_pickle=True)[0]
summary = json.load(open("summary.json"))
N = summary["n_sats"]
t = runs[0]["t"]

def band(ax, key, color, label, scale=1.0):
    ys = np.array([r[key] for r in runs]) * scale
    ax.plot(t, ys.mean(0), color=color, lw=1.8, label=label)
    ax.fill_between(t, np.percentile(ys, 5, 0), np.percentile(ys, 95, 0),
                    color=color, alpha=0.18)

# ---------------- 1. object population / runaway curve ----------------
fig, ax = plt.subplots(figsize=(9, 5.5))
band(ax, "n_active", "tab:green", "active satellites")
band(ax, "n_derelict", "tab:orange", "derelicts")
band(ax, "n_frag", "tab:red", "trackable fragments (>10 cm)")
band(ax, "n_small", "tab:purple", "lethal small debris (1-10 cm)")
ax.axvline(5, color="k", ls=":", lw=1, alpha=0.6)
ax.text(5.4, ax.get_ylim()[1] * 0.5, "external strike", rotation=90,
        fontsize=8, alpha=0.7)
ax.set_yscale("symlog", linthresh=1)
ax.set_ylim(bottom=0)
ax.set_xlabel("years"); ax.set_ylabel("objects on orbit")
ax.set_title(f"Population evolution, N={N} constellation "
             f"(mean and 5-95% over {len(runs)} MC runs)")
ax.legend(loc="upper right", fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("fig1_population.png", dpi=300); fig.savefig("fig1_population.pdf")

# ---------------- 2. fragment density heatmap (altitude vs time) -------
H = detail["hists"]          # [time, altbin]
bins = detail["bins_km"]; ht = detail["hist_t"]
fig, ax = plt.subplots(figsize=(9, 5))
Hm = np.ma.masked_less(H.T, 0.5)
pc = ax.pcolormesh(ht, 0.5 * (bins[:-1] + bins[1:]), Hm,
                   norm=LogNorm(vmin=0.5, vmax=max(H.max(), 1)),
                   cmap="inferno", shading="auto")
ax.axhline(550, color="cyan", ls="--", lw=1, label="constellation shell")
ax.set_xlabel("years"); ax.set_ylabel("altitude (km)")
ax.set_ylim(200, 1000)
ax.set_title("Fragment cloud: spatial density vs altitude and time (seed 0)")
ax.legend(loc="upper right", fontsize=9)
fig.colorbar(pc, label="trackable fragments per 25 km bin")
fig.tight_layout(); fig.savefig("fig2_density_heatmap.png", dpi=300); fig.savefig("fig2_density_heatmap.pdf")

# ---------------- 3. Gabbard diagram ------------------------------------
g = detail["gabbard"]
keep = g["prg"] > 200  # suborbital fragments reenter within one revolution
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(g["per"][keep], g["apo"][keep], s=8, c="tab:red", alpha=0.6,
           label="apogee")
ax.scatter(g["per"][keep], g["prg"][keep], s=8, c="tab:blue", alpha=0.6,
           label="perigee")
p0 = 2 * np.pi * np.sqrt(((6378.137 + 550) * 1e3) ** 3 / 3.986004418e14) / 60
ax.axvline(p0, color="k", ls=":", lw=1, alpha=0.6)
ax.set_xlabel("orbital period (min)"); ax.set_ylabel("altitude (km)")
ax.set_title("Gabbard diagram: fragment cloud just after external strike")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("fig3_gabbard.png", dpi=300); fig.savefig("fig3_gabbard.pdf")

# ---------------- 4. constellation health -------------------------------
fig, axs = plt.subplots(2, 2, figsize=(11, 7))
a = axs[0, 0]; band(a, "n_active", "tab:green", "", scale=100.0 / N)
a.set_ylabel("% of design"); a.set_title("Active capacity"); a.set_ylim(0, 110)
a = axs[0, 1]; band(a, "dv", "tab:blue", "")
a.set_ylabel("m/s"); a.set_title("Cumulative station-keeping delta-V per sat")
a = axs[1, 0]; band(a, "avoid", "tab:orange", "")
a.set_ylabel("maneuvers (cum.)"); a.set_title("Collision-avoidance maneuvers")
a = axs[1, 1]; band(a, "coll_total", "tab:red", "")
a.set_ylabel("events (cum.)"); a.set_title("Post-strike collision events")
for a in axs.flat:
    a.set_xlabel("years"); a.grid(alpha=0.3)
fig.suptitle(f"Constellation health, N={N}, 100-year horizon", y=1.0)
fig.tight_layout(); fig.savefig("fig4_health.png", dpi=300); fig.savefig("fig4_health.pdf")

# ---------------- 5. Kessler diagnostics ---------------------------------
fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
a = axs[0]; band(a, "exp_secondary", "tab:red", "")
a.axhline(1.0, color="k", ls="--", lw=1)
a.text(2, 1.15, "cascade threshold (R0=1)", fontsize=8)
a.set_yscale("log"); a.set_xlabel("years")
a.set_ylabel("E[secondary collisions]")
a.set_title("Cascade multiplier R0 (cumulative)")
a.grid(alpha=0.3, which="both")

a = axs[1]
sec = np.array([r["coll_total"][-1] for r in runs])
a.hist(sec, bins=np.arange(-0.5, max(sec.max(), 3) + 1.5), color="tab:red",
       alpha=0.75, rwidth=0.85)
a.set_xlabel("secondary collisions in 100 yr"); a.set_ylabel("MC runs")
a.set_title(f"P(any secondary) = {summary['p_any_secondary']:.2%}")
a.grid(alpha=0.3)

a = axs[2]; band(a, "raan_std", "tab:purple", "")
a.set_xlabel("years"); a.set_ylabel("RAAN spread (deg, circular std)")
a.set_title("Cloud ring->shell smearing (J2)")
a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("fig5_kessler.png", dpi=300); fig.savefig("fig5_kessler.pdf")

print("figures written: fig1..fig5")
