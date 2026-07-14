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
| 100 | 3.5e-5 | 30 runs, 100 yr, zero sampled secondaries |
| 10,000 | 2.1e-3 | fit regime: R0 ∝ N^0.89 |
| 25,000 | 1.4e-2 | superlinear departure begins |
| 100,000 | 9.1e-2 | 4 catastrophic secondaries sampled (40 yr) |
| 1,000,000 | **> 1 — supercritical** | self-sustaining cascade (direct sim) |
| 1,000,000 across 40 shells | 1.4e-2 per shell | dispersion restores ~100× margin |

## Quick start

```bash
pip install -r requirements.txt

# Baseline: N=100, 30 Monte Carlo seeds, 100 years (~10 s total)
python3 kessler_sim.py --n 100 --seeds 30 --years 100 --out .
python3 make_figures.py          # fig1..fig5 diagnostics

# Chunked / large-N runs with the analytic R0 estimator
python3 run_chunk.py --s0 1 --k 1 --n 25000  --years 100
python3 run_chunk.py --s0 1 --k 1 --n 100000 --years 40
python3 run_chunk.py --s0 1 --k 1 --n 1000000 --years 10 --dt 20

# Publication figure (R0 scaling) and outreach-poster charts
python3 paper_fig_r0.py
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
- Derelict decay from 550 km: 2–5 yr, consistent with observed
  Starlink-class lifetimes

## Limitations

No background debris population, static (no solar cycle) atmosphere,
single mean crossing velocity within altitude bins, simplified A/m and ΔV
distributions. See the paper's Limitations section for the full discussion.

## License

MIT — see [LICENSE](LICENSE).
