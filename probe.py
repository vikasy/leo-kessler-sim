import numpy as np, kessler_sim as ks
for avoid in (0.99, 0.0):
    cfg = ks.Cfg(); cfg.n_sats=10000; cfg.years=100.0; cfg.avoid_eff=avoid
    r = ks.run(cfg, 1001, False)
    ts=r['ts']
    print(f"avoid={avoid}  E[sec]={r['exp_secondary']:.3e}  sampled_sec={ts['coll_total'][-1]:.0f} "
          f"mean_derelict={ts['n_derelict'][ts['t']>10].mean():.1f}  "
          f"mean_frag_after={ts['n_frag'][ts['t']>6].mean():.2f}")
