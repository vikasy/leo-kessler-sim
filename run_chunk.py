#!/usr/bin/env python3
"""Run a chunk of MC seeds in parallel and save partial results.
Exposes sensitivity knobs: --avoid, --binw, --rho, --vrel, --dt."""
import argparse, numpy as np
from concurrent.futures import ProcessPoolExecutor
import kessler_sim as ks

ap = argparse.ArgumentParser()
ap.add_argument("--s0", type=int, required=True)
ap.add_argument("--k", type=int, default=4)
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--years", type=float, default=100.0)
ap.add_argument("--dt", type=float, default=5.0, help="step (days)")
ap.add_argument("--avoid", type=float, default=0.99)
ap.add_argument("--binw", type=float, default=25.0, help="bin width (km)")
ap.add_argument("--rho", type=float, default=1.0, help="density multiplier")
ap.add_argument("--vrel", type=float, default=8.0, help="crossing velocity (km/s)")
ap.add_argument("--pmd", type=float, default=0.95)
ap.add_argument("--fail", type=float, default=0.005)
ap.add_argument("--sbm", type=float, default=1.0, help="SBM fragment multiplier")
ap.add_argument("--legacy", action="store_true", help="LEGEND-like benchmark mode")
ap.add_argument("--darea", type=float, default=12.5, help="derelict tumbling area (m^2)")
ap.add_argument("--tag", default="", help="suffix for chunk filenames")
args = ap.parse_args()

cfg = ks.Cfg()
cfg.n_sats = args.n
cfg.years = args.years
cfg.dt = args.dt * 86400.0
cfg.avoid_eff = args.avoid
cfg.bin_w = args.binw * 1e3
cfg.rho_scale = args.rho
cfg.v_rel = args.vrel * 1e3
cfg.pmd_success = args.pmd
cfg.fail_rate = args.fail
cfg.sbm_scale = args.sbm
cfg.derelict_area = args.darea
if args.legacy:
    cfg.legacy = True
    cfg.strike_year = 1e9      # no external strike in benchmark mode
    cfg.bin_hi = 2100e3        # extend altitude grid to cover legacy population
    cfg.lat_frac = 1.0         # legacy population spans high inclinations

with ProcessPoolExecutor(max_workers=4) as ex:
    futs = {s: ex.submit(ks.run, cfg, 1000 + s, s == 0)
            for s in range(args.s0, args.s0 + args.k)}
    for s, f in futs.items():
        r = f.result()
        np.save(f"chunk_{s:03d}{args.tag}.npy", np.array([r], dtype=object),
                allow_pickle=True)
        print(f"[mc] seed {s}: sec={r['ts']['coll_total'][-1]:.0f} "
              f"E[sec]={r['exp_secondary']:.3e}", flush=True)
