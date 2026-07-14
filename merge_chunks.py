#!/usr/bin/env python3
"""Merge chunk_*.npy into mc_runs.npy / detail_run.npy / summary.json."""
import glob, json, numpy as np

files = sorted(glob.glob("chunk_*.npy"))
runs = [np.load(f, allow_pickle=True)[0] for f in files]
np.save("mc_runs.npy", np.array([r["ts"] for r in runs], dtype=object),
        allow_pickle=True)
detail = runs[0]  # seed 0 carries detail
np.save("detail_run.npy", np.array([detail], dtype=object), allow_pickle=True)

sec = np.array([r["ts"]["coll_total"][-1] for r in runs])
esec = np.array([r["exp_secondary"] for r in runs])
N = 100
summary = dict(
    n_sats=N, years=100.0, seeds=len(runs),
    p_any_secondary=float(np.mean(sec > 0)),
    mean_secondary=float(sec.mean()),
    R0_expected_secondaries=float(esec.mean()),
    peak_frag=float(max(r["ts"]["n_frag"].max() for r in runs)),
    frag_at_end=float(np.mean([r["ts"]["n_frag"][-1] for r in runs])),
    frag_half_life_yr=float(np.mean([
        r["ts"]["t"][pk + np.argmax(r["ts"]["n_frag"][pk:] <=
                                    0.5 * r["ts"]["n_frag"].max())]
        - r["ts"]["t"][pk]
        for r in runs
        for pk in [int(np.argmax(r["ts"]["n_frag"]))]])),
    active_frac_end=float(np.mean(
        [r["ts"]["n_active"][-1] for r in runs]) / N),
    dv_per_sat_total_ms=float(np.mean([r["ts"]["dv"][-1] for r in runs])),
    avoid_maneuvers_total=float(np.mean([r["ts"]["avoid"][-1] for r in runs])),
    small_debris_kills=float(np.mean([
        sum(1 for c in r["collisions"] if c[1] == "small-debris kill")
        for r in runs])),
)
json.dump(summary, open("summary.json", "w"), indent=2)
print(json.dumps(summary, indent=2))
