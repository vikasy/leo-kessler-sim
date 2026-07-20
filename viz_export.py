#!/usr/bin/env python3
"""Run real kessler_sim scenarios with the VIZ recorder and inject the
event packs into the perturbation visualizer HTML template."""
import json
import kessler_sim as ks

def run_pack(name, label, blurb, **cfg_over):
    ks.VIZ = dict(events=[])
    cfg = ks.Cfg()
    for k, v in cfg_over.items():
        setattr(cfg, k, v)
    r = ks.run(cfg, seed=1001, record_detail=False)
    pack = dict(name=name, label=label, blurb=blurb,
                years=cfg.years, strike_year=cfg.strike_year,
                init=ks.VIZ['init'], alt_nom=ks.VIZ['alt_nom'],
                events=ks.VIZ['events'],
                r0=round(float(r['exp_secondary']), 4))
    ncat = sum(1 for e in pack['events'] if e['k'] in ('col',))
    print(f"[{name}] events={len(pack['events'])} catastrophic={ncat} "
          f"R0={pack['r0']} init_n={len(pack['init']['a'])}")
    ks.VIZ = None
    return pack

packs = [
    run_pack("baseline",
        "Baseline: 2,000 sats, 550 km — strike absorbed",
        "One external strike at year 1. Watch the cloud bloom, smear ring-to-shell under J₂, and drain away under drag. Sub-critical: the constellation shrugs it off.",
        n_sats=2000, shell_alt=550e3, years=12.0, strike_year=1.0,
        design_life=1e9, fail_rate=0.005),
    run_pack("cascade",
        "Degraded ops: 25,000 sats — cascade feedback live",
        "Close to the paper's pessimistic scenario (85% avoidance, 3%/yr failures, solar-min density). Every collision below was sampled by the real simulator — fragments breed collisions breed fragments.",
        n_sats=25000, shell_alt=550e3, years=30.0, strike_year=1.0,
        design_life=1e9, fail_rate=0.03, avoid_eff=0.85, rho_scale=0.6),
]

blob = json.dumps(packs, separators=(',', ':'))
print("pack JSON size:", f"{len(blob)/1e6:.2f} MB")

tpl = open('viz_template.html').read()
assert '/*__VIZPACKS__*/null' in tpl
out = tpl.replace('/*__VIZPACKS__*/null', blob)
open('perturbation_visualizer.html', 'w').write(out)
print("wrote perturbation_visualizer.html", f"{len(out)/1e6:.2f} MB")
