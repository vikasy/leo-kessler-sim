#!/usr/bin/env python3
"""Run a chunk of MC seeds in parallel and save partial results."""
import argparse, numpy as np
from concurrent.futures import ProcessPoolExecutor
import kessler_sim as ks

ap = argparse.ArgumentParser()
ap.add_argument("--s0", type=int, required=True)
ap.add_argument("--k", type=int, default=4)
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--years", type=float, default=100.0)
args = ap.parse_args()

cfg = ks.Cfg(); cfg.n_sats = args.n; cfg.years = args.years
with ProcessPoolExecutor(max_workers=4) as ex:
    futs = {s: ex.submit(ks.run, cfg, 1000 + s, s == 0)
            for s in range(args.s0, args.s0 + args.k)}
    for s, f in futs.items():
        r = f.result()
        np.save(f"chunk_{s:03d}.npy", np.array([r], dtype=object),
                allow_pickle=True)
        print(f"[mc] seed {s}: sec={r['ts']['coll_total'][-1]:.0f} "
              f"E[sec]={r['exp_secondary']:.3e}", flush=True)
