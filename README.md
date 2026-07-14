# leo-kessler-sim

Fast Monte Carlo simulation of collisional-cascade (Kessler) risk in actively
managed LEO mega-constellations — the simulation infrastructure behind:

> Yadav, V., "Collisional-Cascade Risk in an Actively Managed LEO
> Mega-Constellation: A 100-Year Monte Carlo Assessment of Single-Breakup
> Scenarios," draft manuscript, 2026.

A century of constellation-plus-debris evolution runs in **seconds per
history** at N = 10⁴ satellites and ~20 s at N = 10⁶, on a laptop-class CPU.

## What it models

- **Constellation:** Walker-delta shell (default 550 km / 53°), N configurable
  from 10² to 10⁶; Starlink-class satellites (260 kg, 25 m², Cd 2.2).
- **Dynamics:** mean-element propagation — secular J2 nodal regression +
  piecewise-exponential atmospheric drag evaluated at perigee, with 20%
  (1-σ) stochastic drag dispersion.
- **Operations:** ±500 m dead-band station-keeping with ΔV accounting,
  7-year design life with in-slot replacement, 95% post-mission-disposal
  success, 0.5%/yr random failures → derelicts, 99%-effective conjunction
  avoidance for trackable objects.
- **Fragmentation:** NASA Standard Breakup Model (EVOLVE 4.0 size / A/m /
  ΔV distributions); >10 cm fragments tracked individually, 1–10 cm lethal
  population as weighted super-particles.
- **Collisions:** kinetic-theory sampling per 25-km altitude bin across all
  object-class pairs, with cascade feedback (collisions spawn fragments that
  cause collisions). An analytic accumulator gives a low-variance estimator
  of the cascade multiplier R0 even when sampled counts are zero.

## Key results (reproducible below)

| N (single shell) | R0 = E[secondary collisions per breakup] | Note |
|---|---|---|
| 100 | (6.2 ± 1.6)e-5 | 30 seeds, 100 yr, zero sampled secondaries |
| 10,000 | (6.0 ± 2.5)e-3 | fit regime: R0 ∝ N^0.99 |
| 25,000 | (2.8 ± 1.7)e-2 (10 seeds) | superlinear departure begins |
| 100,000 | 0.31 ± 0.09 (9 seeds) | criticality bracketed directly: N_crit ≈ 1.4e5 |
| 1,000,000 | **≈140 by +3 yr — supercritical** | all seeds cross criticality within 1 yr |
| 1,000,000 across 40 shells | 2.8e-2 per shell | dispersion restores ~35× margin |
| 25,000, degraded operations | ~8–10 — supercritical | ops quality is co-dominant with geometry |

## Quick start

```bash
pip install -r requirements.txt

# Baseline: N=100, 30 Monte Carlo seeds, 100 years (~10 s total)
python3 kessler_sim.py --n 100 --seeds 30 --years 100 --out .
python3 make_figures.py          # fig1..fig5 diagnostics

# Chunked / large-N runs with the analytic R0 estimator
python3 run_chunk.py --s0 1 --k 3 --n 25000  --years 100    # 3 seeds
python3 run_chunk.py --s0 1 --k 3 --n 100000 --years 40
python3 run_chunk.py --s0 1 --k 1 --n 1000000 --years 10 --dt 20

# Sensitivity knobs (paper Section 4.5)
python3 run_chunk.py --s0 1 --k 1 --n 10000 --avoid 0.0   # control-loop ablation
python3 run_chunk.py --s0 1 --k 1 --n 10000 --rho 0.3     # solar-min density proxy
python3 run_chunk.py --s0 1 --k 1 --n 10000 --binw 12.5   # bin-size check
python3 run_chunk.py --s0 1 --k 1 --n 10000 --vrel 4      # crossing-velocity check

# Regime map grid (paper Figure 7): ops quality x shell population
python3 run_chunk.py --s0 1 --k 1 --n 100000 --years 40 --dt 10 --avoid 0.95 --pmd 0.90 --fail 0.01

# LEGEND-like integrated benchmark (paper Section 3.7)
python3 run_chunk.py --s0 1 --k 3 --n 100 --years 100 --legacy

# Publication figures (R0 scaling, regime map) and outreach-poster charts
python3 paper_fig_r0.py
python3 paper_fig_regime.py
python3 kid_charts.py
```

Each `run_chunk.py` invocation prints `E[sec]` — the cascade multiplier R0 —
and saves the full time-series to `chunk_XXX.npy`. `merge_chunks.py`
aggregates chunk files into `mc_runs.npy` / `summary.json`.

## Files

| File | Purpose |
|---|---|
| `kessler_sim.py` | Simulation core + CLI driver (all physics) |
| `run_chunk.py` | Parallel seed-chunk runner for sweeps / large N |
| `merge_chunks.py` | Aggregate chunks → summary statistics |
| `make_figures.py` | Diagnostic figures (population, heatmap, Gabbard, health, cascade) |
| `paper_fig_r0.py` | Publication R0-scaling figure |
| `kid_charts.py` | Simplified charts for the outreach poster |
| `poster.html` | Layman-facing A2 poster (render with WeasyPrint) |
| `make_paper.js` | Manuscript generator (docx-js) |

## Validation

- J2 nodal rate at 550 km / 53°: simulated −4.489°/day vs analytic −4.49°/day
- Fragment count for the 270 kg baseline event: 341 vs NASA SBM 341.7
- Derelict decay from 550 km: 1.1 yr with the tumbling-averaged drag area
  (A/2), at the fast end of the observed 1–5 yr range under the dense-side
  static atmosphere; `--darea` sweeps this leading systematic
- Integrated LEGEND-like benchmark (`--legacy`): catastrophic-collision rate
  0.04–0.16/yr vs LEGEND's published 0.11–0.20/yr, and no-new-launch fragment
  population growth 1.0–1.5×/century

## Limitations

No background debris population, static (no solar cycle) atmosphere,
single mean crossing velocity within altitude bins, simplified A/m and ΔV
distributions. See the paper's Limitations section for the full discussion.

## License

MIT — see [LICENSE](LICENSE).
