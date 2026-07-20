#!/usr/bin/env python3
"""
LEO mega-constellation Kessler-risk simulator.
--------------------------------------------
Models N satellites in a Walker shell with:
  - mean-element propagation (J2 secular + exponential-atmosphere drag)
  - stochastic deviations from nominal path (drag uncertainty, along-track jitter)
  - station-keeping dead-band control (delta-V accounting)
  - end-of-life replacement cycle with post-mission-disposal (PMD) success rate
  - external debris strike -> NASA Standard Breakup Model fragment cloud
  - kinetic-theory collision sampling per altitude bin (cascade enabled)
  - Kessler diagnostics: secondary-collision expectation (R0), MC probability,
    fragment cloud evolution (altitude-time density, Gabbard, RAAN spread)

Units: SI internally (m, s, kg, rad). Altitudes reported in km.
Usage: python3 kessler_sim.py [--n 100] [--seeds 30] [--years 100]
"""

import argparse
import json
import numpy as np

# ----------------------------- constants ---------------------------------
MU = 3.986004418e14          # m^3/s^2
VIZ = None                    # optional visualization recorder (dict with 'events')
RE = 6378.137e3              # m
J2 = 1.08262668e-3

# ----------------------------- config ------------------------------------
class Cfg:
    # constellation
    n_sats        = 100
    shell_alt     = 550e3        # m
    inclination   = np.radians(53.0)
    sat_mass      = 260.0        # kg (Starlink-class)
    sat_area      = 25.0         # m^2 (with panels)
    sat_cd        = 2.2
    sat_radius    = 2.0          # m hard-body radius (sigma = pi*(r1+r2)^2)
    derelict_area = 12.5         # m^2 tumbling-averaged projected area (A/2)
    lat_frac      = 0.80         # occupied-band volume fraction (sin i, 53 deg)
    design_life   = 7.0          # yr, then retire+replace
    pmd_success   = 0.95         # prob. retired sat deorbits cleanly
    fail_rate     = 0.005        # /yr random failure -> derelict (can't deorbit)
    deadband      = 500.0        # m semi-major-axis dead-band for station keeping
    drag_sigma    = 0.20         # 1-sigma multiplicative drag uncertainty per step
    avoid_eff     = 0.99         # active sats dodge trackable objects this well
    screen_ratio  = 625.0        # avoidance maneuvers per actual (unmitigated) collision

    # external strike
    strike_year   = 5.0
    imp_mass      = 10.0         # kg external debris
    imp_vel       = 12e3         # m/s relative

    # breakup / debris
    lc_track      = 0.10         # m, trackable threshold (modeled individually)
    lc_small      = 0.01         # m, lethal-but-small lower bound (super-particles)
    n_small_super = 400          # super-particles for 1-10 cm population
    frag_cd       = 2.2

    # collision kinetics
    v_rel         = 8e3          # m/s mean crossing velocity
    bin_lo, bin_hi, bin_w = 200e3, 3100e3, 25e3
    rho_scale     = 1.0          # atmosphere density multiplier (solar-cycle proxy)
    sbm_scale     = 1.0          # breakup fragment-count multiplier (SBM sensitivity)

    # legacy-population benchmark mode (LEGEND-like, no control loop)
    legacy        = False
    n_leg_intact  = 2500
    n_leg_frag    = 7000

    # numerics
    years         = 100.0
    dt            = 5 * 86400.0  # s
    reentry_alt   = 200e3
    seeds         = 30
    hist_every    = 5            # store altitude histogram every k steps

# ------------------------ exponential atmosphere --------------------------
_ATM = np.array([  # h0(km), rho0(kg/m^3), H(km)   (Vallado, Table 8-4)
    [0, 1.225, 7.249], [25, 3.899e-2, 6.349], [30, 1.774e-2, 6.682],
    [40, 3.972e-3, 7.554], [50, 1.057e-3, 8.382], [60, 3.206e-4, 7.714],
    [70, 8.770e-5, 6.549], [80, 1.905e-5, 5.799], [90, 3.396e-6, 5.382],
    [100, 5.297e-7, 5.877], [110, 9.661e-8, 7.263], [120, 2.438e-8, 9.473],
    [130, 8.484e-9, 12.636], [140, 3.845e-9, 16.149], [150, 2.070e-9, 22.523],
    [180, 5.464e-10, 29.740], [200, 2.789e-10, 37.105], [250, 7.248e-11, 45.546],
    [300, 2.418e-11, 53.628], [350, 9.518e-12, 53.298], [400, 3.725e-12, 58.515],
    [450, 1.585e-12, 60.828], [500, 6.967e-13, 63.822], [600, 1.454e-13, 71.835],
    [700, 3.614e-14, 88.667], [800, 1.170e-14, 124.64], [900, 5.245e-15, 181.05],
    [1000, 3.019e-15, 268.00]])

def density(h_m):
    """Atmospheric density [kg/m^3] vs altitude [m], vectorized."""
    hk = np.clip(h_m / 1e3, 0, 2000)
    i = np.clip(np.searchsorted(_ATM[:, 0], hk, side="right") - 1, 0, len(_ATM) - 1)
    return _ATM[i, 1] * np.exp(-(hk - _ATM[i, 0]) / _ATM[i, 2])

# --------------------------- object store (SoA) ---------------------------
ACTIVE, DERELICT, FRAG, SMALL = 0, 1, 2, 3

class Objects:
    """Structure-of-arrays population store."""
    def __init__(s, n0):
        cap = max(4 * n0 + 4000, 8000)
        s.a     = np.zeros(cap)   # semi-major axis (m)
        s.e     = np.zeros(cap)
        s.inc   = np.zeros(cap)
        s.raan  = np.zeros(cap)
        s.u     = np.zeros(cap)   # argument of latitude (rad)
        s.B     = np.zeros(cap)   # ballistic coeff Cd*A/m (m^2/kg)
        s.mass  = np.zeros(cap)
        s.rad   = np.zeros(cap)   # hard-body radius (m)
        s.cls   = np.full(cap, -1, dtype=np.int8)
        s.w     = np.ones(cap)    # statistical weight (super-particles)
        s.age   = np.zeros(cap)   # yr, for design-life retirement
        s.alive = np.zeros(cap, dtype=bool)
        s.n = 0

    def add(s, **kw):
        m = len(kw["a"]); i0 = s.n
        if i0 + m > len(s.a):                      # grow
            for f in ("a e inc raan u B mass rad w age").split():
                setattr(s, f, np.concatenate([getattr(s, f), np.zeros(i0 + m)]))
            s.cls  = np.concatenate([s.cls,  np.full(i0 + m, -1, dtype=np.int8)])
            s.alive = np.concatenate([s.alive, np.zeros(i0 + m, dtype=bool)])
        sl = slice(i0, i0 + m)
        for k, v in kw.items():
            getattr(s, k)[sl] = v
        s.w[sl] = kw.get("w", np.ones(m))
        s.alive[sl] = True
        s.n = i0 + m
        return np.arange(i0, i0 + m)

def _viz_slice(o, i0, i1):
    return dict(a=[round((x - RE) / 1e3, 1) for x in o.a[i0:i1]],
                e=[round(float(x), 4) for x in o.e[i0:i1]],
                inc=[round(float(x), 4) for x in o.inc[i0:i1]],
                raan=[round(float(x), 4) for x in o.raan[i0:i1]],
                u=[round(float(x), 4) for x in o.u[i0:i1]],
                B=[round(float(x), 4) for x in o.B[i0:i1]],
                cls=[int(x) for x in o.cls[i0:i1]])

# ------------------------- constellation design ---------------------------
def build_walker(o, cfg, rng):
    """Walker-delta shell: evenly spaced planes/phases -> guaranteed margins."""
    n = cfg.n_sats
    planes = max(int(round(np.sqrt(n))), 1)
    per = int(np.ceil(n / planes))
    idx = np.arange(n)
    pl, sl = idx // per, idx % per
    raan = 2 * np.pi * pl / planes
    u = 2 * np.pi * sl / per + 2 * np.pi * pl / (planes * per)  # phase offset
    o.add(a=np.full(n, RE + cfg.shell_alt), e=np.zeros(n),
          inc=np.full(n, cfg.inclination), raan=raan, u=u,
          B=np.full(n, cfg.sat_cd * cfg.sat_area / cfg.sat_mass),
          mass=np.full(n, cfg.sat_mass), rad=np.full(n, cfg.sat_radius),
          age=rng.uniform(0, cfg.design_life, n))
    o.cls[:n] = ACTIVE

def build_legacy(o, cfg, rng):
    """LEGEND-like legacy population: intact derelicts + fragments,
    catalog-shaped altitude distribution, no control loop."""
    def alt_sample(n):
        u = rng.uniform(size=n)
        h = np.where(u < 0.20, rng.uniform(400e3, 700e3, n),
            np.where(u < 0.60, rng.normal(880e3, 150e3, n),
                     rng.uniform(1000e3, 2000e3, n)))
        return np.clip(h, 300e3, 2000e3)

    ni = cfg.n_leg_intact
    m = np.exp(rng.normal(np.log(900.0), 0.5, ni))       # ~intact masses (kg)
    o.add(a=RE + alt_sample(ni), e=rng.uniform(0, 0.02, ni),
          inc=np.radians(rng.uniform(60, 100, ni)),
          raan=rng.uniform(0, 2 * np.pi, ni), u=rng.uniform(0, 2 * np.pi, ni),
          B=2.2 * 10.0 / m, mass=m, rad=np.full(ni, 1.8))
    o.cls[:ni] = DERELICT

    nf = cfg.n_leg_frag
    lc = (0.1**-1.71 + rng.uniform(size=nf)
          * (1.0**-1.71 - 0.1**-1.71)) ** (-1 / 1.71)
    am = 10 ** rng.normal(np.log10(0.05 * (lc / 0.1) ** -0.5), 0.3)
    o.add(a=RE + alt_sample(nf), e=rng.uniform(0, 0.05, nf),
          inc=np.radians(rng.uniform(60, 100, nf)),
          raan=rng.uniform(0, 2 * np.pi, nf), u=rng.uniform(0, 2 * np.pi, nf),
          B=2.2 * am, mass=np.maximum(0.556945 * lc**2.0047 / am, 1e-4),
          rad=lc / 2)
    o.cls[ni:ni + nf] = FRAG

# ------------------------ NASA standard breakup ----------------------------
def nasa_breakup(o, cfg, rng, i1, m_tot, alt, inc, raan):
    """Catastrophic breakup: spawn trackable frags + small super-particles."""
    a0 = RE + alt
    v0 = np.sqrt(MU / a0)

    def spawn(lc_lo, lc_hi, n_frag, n_model, cls, w_each):
        if n_model <= 0:
            return
        # power-law sizes N(>Lc) ~ Lc^-1.71
        q = rng.uniform(size=n_model)
        lc = (lc_lo**-1.71 + q * (lc_hi**-1.71 - lc_lo**-1.71)) ** (-1 / 1.71)
        am = 10 ** rng.normal(np.log10(0.05 * (lc / 0.1) ** -0.5), 0.3)  # A/m
        mass = np.maximum(0.556945 * lc**2.0047 / am, 1e-4)              # kg
        # EVOLVE 4.0 delta-v: log10(dv) ~ N(0.9*log10(A/m)+2.9, 0.4)
        dv = 10 ** rng.normal(0.9 * np.log10(am) + 2.9, 0.4)
        dv = np.minimum(dv, 1500.0)
        th = np.arccos(rng.uniform(-1, 1, n_model))       # isotropic direction
        ph = rng.uniform(0, 2 * np.pi, n_model)
        dvr = dv * np.sin(th) * np.cos(ph)                # radial
        dvs = dv * np.sin(th) * np.sin(ph)                # along-track
        dvw = dv * np.cos(th)                             # cross-track
        vs = v0 + dvs
        v2 = dvr**2 + vs**2 + dvw**2
        a_new = 1.0 / np.maximum(2.0 / a0 - v2 / MU, 1e-12)
        a_new = np.clip(a_new, RE + 120e3, RE + 3000e3)
        h2 = a0**2 * (vs**2 + dvw**2)                     # (r x v)^2
        e2 = np.clip(1.0 - h2 / (MU * a_new), 0.0, 0.9604)
        di = np.arctan2(dvw, vs)
        o.add(a=a_new, e=np.sqrt(e2), inc=np.abs(inc + di),
              raan=np.full(n_model, raan) + rng.normal(0, 0.01, n_model),
              u=rng.uniform(0, 2 * np.pi, n_model),
              B=cfg.frag_cd * am, mass=mass,
              rad=lc / 2, w=np.full(n_model, w_each))
        o.cls[o.n - n_model:o.n] = cls

    n_track = int(cfg.sbm_scale * 0.1 * m_tot**0.75 * cfg.lc_track**-1.71)
    n_small = int(cfg.sbm_scale * 0.1 * m_tot**0.75 * cfg.lc_small**-1.71) - n_track
    spawn(cfg.lc_track, 1.0, n_track, n_track, FRAG, 1.0)
    ns = min(cfg.n_small_super, n_small)
    if ns > 0:
        spawn(cfg.lc_small, cfg.lc_track, n_small, ns, SMALL, n_small / ns)
    return n_track, n_small

# ------------------------------ simulation --------------------------------
def run(cfg, seed, record_detail=False):
    rng = np.random.default_rng(seed)
    o = Objects(max(cfg.n_sats, cfg.n_leg_intact + cfg.n_leg_frag))
    if cfg.legacy:
        build_legacy(o, cfg, rng)
    else:
        build_walker(o, cfg, rng)
    a_nom = RE + cfg.shell_alt
    if VIZ is not None:
        VIZ['init'] = _viz_slice(o, 0, o.n)
        VIZ['alt_nom'] = cfg.shell_alt / 1e3

    n_steps = int(cfg.years * 365.25 * 86400 / cfg.dt)
    bins = np.arange(cfg.bin_lo, cfg.bin_hi + cfg.bin_w, cfg.bin_w)
    nb = len(bins) - 1
    Vbin = (4 * np.pi * (RE + 0.5 * (bins[:-1] + bins[1:])) ** 2 * cfg.bin_w
            * cfg.lat_frac)                    # occupied latitude band only
    B_der = cfg.sat_cd * cfg.derelict_area / cfg.sat_mass

    ts = {k: np.zeros(n_steps) for k in
          ("t n_active n_derelict n_frag n_small dv maneuvers avoid "
           "exp_secondary coll_total raan_std").split()}
    hists, hist_t = [], []
    gabbard = None
    struck = False
    cum_dv = cum_man = cum_avoid = 0.0
    exp_sec = 0.0
    collisions = []   # (t_yr, kind)

    for k in range(n_steps):
        t = k * cfg.dt
        t_yr = t / (365.25 * 86400)
        al = o.alive[:o.n]
        idx = np.nonzero(al)[0]
        a, e, inc = o.a[idx], o.e[idx], o.inc[idx]
        cls = o.cls[idx]

        # ---- propagation: J2 secular + drag on mean elements -------------
        nmm = np.sqrt(MU / a**3)
        p = a * (1 - e**2)
        o.raan[idx] += -1.5 * J2 * nmm * (RE / p) ** 2 * np.cos(inc) * cfg.dt
        o.u[idx] = (o.u[idx] + nmm * cfg.dt) % (2 * np.pi)

        hp = a * (1 - e) - RE                          # perigee altitude
        rho = density(hp) * cfg.rho_scale
        fdrag = 1.0 + cfg.drag_sigma * rng.standard_normal(len(idx))
        dadt = -rho * np.maximum(fdrag, 0.1) * o.B[idx] * np.sqrt(MU * a)
        o.a[idx] += dadt * cfg.dt
        o.e[idx] = np.maximum(e + dadt * cfg.dt / a * e, 0.0)

        # ---- station keeping (active sats only) ---------------------------
        act = idx[cls == ACTIVE]
        low = act[o.a[act] < a_nom - cfg.deadband]
        if len(low):
            da = (a_nom + cfg.deadband) - o.a[low]
            vv = np.sqrt(MU / o.a[low])
            cum_dv += np.sum(0.5 * vv * da / o.a[low]) / max(cfg.n_sats, 1)
            cum_man += len(low)
            o.a[low] = a_nom + cfg.deadband

        # ---- aging: retirement + replacement, random failures -------------
        o.age[act] += cfg.dt / (365.25 * 86400)
        retire = act[o.age[act] > cfg.design_life]
        if len(retire):
            ok = rng.uniform(size=len(retire)) < cfg.pmd_success
            o.alive[retire[ok]] = False                # clean deorbit
            o.cls[retire[~ok]] = DERELICT              # stuck on orbit
            o.B[retire[~ok]] = B_der                   # tumbling drag area
            if VIZ is not None and len(retire[~ok]):
                VIZ['events'].append(dict(t=round(t_yr, 3), k='der', idx=[int(x) for x in retire[~ok]]))
        fail = np.array([], dtype=int)
        if len(act):
            pf = cfg.fail_rate * cfg.dt / (365.25 * 86400)
            fail = act[rng.uniform(size=len(act)) < pf]
            o.cls[fail] = DERELICT                     # failed -> derelict
            o.B[fail] = B_der                          # tumbling drag area
            if VIZ is not None and len(fail):
                VIZ['events'].append(dict(t=round(t_yr, 3), k='der', idx=[int(x) for x in fail]))
        rep = np.concatenate([retire, fail])           # replace slots (batched)
        if len(rep):
            m = len(rep)
            j = o.add(a=np.full(m, a_nom), e=np.zeros(m),
                      inc=np.full(m, cfg.inclination),
                      raan=o.raan[rep].copy(), u=o.u[rep].copy(),
                      B=np.full(m, cfg.sat_cd * cfg.sat_area / cfg.sat_mass),
                      mass=np.full(m, cfg.sat_mass),
                      rad=np.full(m, cfg.sat_radius), age=np.zeros(m))
            o.cls[j] = ACTIVE

        # ---- external debris strike ---------------------------------------
        if (not struck) and t_yr >= cfg.strike_year:
            struck = True
            al2 = np.nonzero(o.alive[:o.n] & (o.cls[:o.n] == ACTIVE))[0]
            if len(al2):                    # legacy mode has no strike target
                tgt = rng.choice(al2)
                m_tot = o.mass[tgt] + cfg.imp_mass
                nb0 = o.n
                nasa_breakup(o, cfg, rng, tgt, m_tot,
                             o.a[tgt] - RE, o.inc[tgt], o.raan[tgt])
                o.alive[tgt] = False
                if VIZ is not None:
                    VIZ['events'].append(dict(t=round(t_yr, 3), k='strike',
                        parent=int(tgt), new=_viz_slice(o, nb0, o.n)))
                collisions.append((t_yr, "external strike"))
                if record_detail:                       # Gabbard snapshot
                    fr = np.nonzero(o.alive[:o.n] & (o.cls[:o.n] == FRAG))[0]
                    gabbard = dict(
                        per=2 * np.pi * np.sqrt(o.a[fr] ** 3 / MU) / 60,
                        apo=(o.a[fr] * (1 + o.e[fr]) - RE) / 1e3,
                        prg=(o.a[fr] * (1 - o.e[fr]) - RE) / 1e3)

        # ---- reentry cleanup ----------------------------------------------
        gone = idx[(o.a[idx] * (1 - o.e[idx]) - RE) < cfg.reentry_alt]
        o.alive[gone] = False

        # ---- kinetic collision sampling per altitude bin -------------------
        al = o.alive[:o.n]
        idx = np.nonzero(al)[0]
        cls = o.cls[idx]
        hnow = o.a[idx] - RE
        bi = np.clip(((hnow - cfg.bin_lo) // cfg.bin_w).astype(int), 0, nb - 1)

        # per-bin weighted counts and mean cross-sections per class
        def binstat(mask):
            wsum = np.bincount(bi[mask], weights=o.w[idx][mask], minlength=nb)
            rsum = np.bincount(bi[mask], weights=(o.w * o.rad)[idx][mask],
                               minlength=nb)
            return wsum, np.divide(rsum, wsum, out=np.zeros(nb), where=wsum > 0)

        mA, mD, mF, mS = (cls == ACTIVE), (cls == DERELICT), (cls == FRAG), (cls == SMALL)
        NA, rA = binstat(mA); ND, rD = binstat(mD)
        NF, rF = binstat(mF); NS, rS = binstat(mS)

        def rate(N1, r1, N2, r2, same=False, avoid=1.0):
            sig = np.pi * (r1 + r2) ** 2
            n12 = N1 * N2 if not same else 0.5 * N1 * np.maximum(N1 - 1, 0)
            return avoid * n12 * sig * cfg.v_rel / Vbin * cfg.dt

        pair_defs = [   # (rates, class1, class2, catastrophic?)
            (rate(NA, rA, NF, rF, avoid=1 - cfg.avoid_eff), ACTIVE, FRAG, True),
            (rate(NA, rA, ND, rD, avoid=1 - cfg.avoid_eff), ACTIVE, DERELICT, True),
            (rate(ND, rD, NF, rF), DERELICT, FRAG, True),
            (rate(ND, rD, ND, rD, same=True), DERELICT, DERELICT, True),
            (rate(NF, rF, NF, rF, same=True), FRAG, FRAG, True),
            (rate(NA, rA, NS, rS), ACTIVE, SMALL, False),  # kills sat
        ]
        lam_frag_involved = (pair_defs[0][0] + pair_defs[2][0]
                             + pair_defs[4][0]).sum()
        exp_sec += lam_frag_involved
        cum_avoid += cfg.screen_ratio * (
            rate(NA, rA, NF, rF).sum() + rate(NA, rA, ND, rD).sum())

        for lam, c1, c2, cat in pair_defs:
            nev = rng.poisson(np.minimum(lam, 100.0))  # cap guards event loop
            if not cat:                    # sub-trackable kills: batched
                for b in np.nonzero(nev)[0]:
                    cand1 = idx[(bi == b) & (cls == c1)]
                    if not len(cand1):
                        continue
                    nkill = min(int(nev[b]), len(cand1))
                    hit = rng.choice(cand1, size=nkill, replace=False)
                    o.cls[hit] = DERELICT
                    o.B[hit] = B_der
                    collisions.extend([(t_yr, "small-debris kill")] * nkill)
                    if VIZ is not None:
                        VIZ['events'].append(dict(t=round(t_yr, 3), k='kill', idx=[int(x) for x in hit]))
                continue
            for b in np.nonzero(nev)[0]:
                for _ in range(int(nev[b])):
                    cand1 = idx[(bi == b) & (cls == c1)]
                    cand2 = idx[(bi == b) & (cls == c2)]
                    if not len(cand1) or not len(cand2):
                        continue
                    i1 = rng.choice(cand1); i2 = rng.choice(cand2)
                    if i1 == i2:
                        continue
                    m_tot = o.mass[i1] + o.mass[i2]
                    nb0 = o.n
                    nasa_breakup(o, cfg, rng, i1, m_tot,
                                 o.a[i1] - RE, o.inc[i1], o.raan[i1])
                    o.alive[i1] = o.alive[i2] = False
                    collisions.append((t_yr, f"{c1}-{c2}"))
                    if VIZ is not None:
                        VIZ['events'].append(dict(t=round(t_yr, 3), k='col',
                            c1=int(c1), c2=int(c2), i1=int(i1), i2=int(i2),
                            new=_viz_slice(o, nb0, o.n)))

        # ---- bookkeeping ---------------------------------------------------
        al = o.alive[:o.n]; c = o.cls[:o.n]
        ts["t"][k] = t_yr
        ts["n_active"][k]   = np.sum(al & (c == ACTIVE))
        ts["n_derelict"][k] = np.sum(al & (c == DERELICT))
        ts["n_frag"][k]     = np.sum(al & (c == FRAG))
        ts["n_small"][k]    = np.sum(o.w[:o.n][al & (c == SMALL)])
        ts["dv"][k], ts["maneuvers"][k], ts["avoid"][k] = cum_dv, cum_man, cum_avoid
        ts["exp_secondary"][k] = exp_sec
        ts["coll_total"][k] = len(collisions) - (1 if struck else 0)
        fr = al & (c == FRAG)
        if fr.any():
            ra = o.raan[:o.n][fr]
            ts["raan_std"][k] = np.degrees(np.sqrt(np.maximum(
                -2 * np.log(np.abs(np.mean(np.exp(1j * ra))) + 1e-12), 0.0)))
        if record_detail and k % cfg.hist_every == 0:
            hh = o.a[:o.n][fr] - RE
            hists.append(np.histogram(hh / 1e3, bins=bins / 1e3,
                                      weights=o.w[:o.n][fr])[0])
            hist_t.append(t_yr)

    out = dict(ts=ts, collisions=collisions, exp_secondary=exp_sec)
    if record_detail:
        out["hists"] = np.array(hists); out["hist_t"] = np.array(hist_t)
        out["bins_km"] = bins / 1e3; out["gabbard"] = gabbard
    return out

# ------------------------------- driver -----------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=Cfg.n_sats)
    ap.add_argument("--seeds", type=int, default=Cfg.seeds)
    ap.add_argument("--years", type=float, default=Cfg.years)
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    cfg = Cfg(); cfg.n_sats = args.n; cfg.years = args.years; cfg.seeds = args.seeds

    print(f"[cfg] N={cfg.n_sats} shell={cfg.shell_alt/1e3:.0f}km "
          f"i={np.degrees(cfg.inclination):.0f}deg horizon={cfg.years:.0f}yr "
          f"seeds={cfg.seeds}")

    # sanity: J2 nodal rate
    a = RE + cfg.shell_alt; nmm = np.sqrt(MU / a**3)
    od = -1.5 * J2 * nmm * (RE / a) ** 2 * np.cos(cfg.inclination)
    print(f"[check] J2 RAAN rate = {np.degrees(od)*86400:.3f} deg/day "
          f"(expect ~ -4.5 for 550km/53deg)")

    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as ex:
        futs = [ex.submit(run, cfg, 1000 + s, s == 0) for s in range(cfg.seeds)]
        runs = []
        for s, f in enumerate(futs):
            runs.append(f.result())
            print(f"[mc] seed {s+1}/{cfg.seeds}: "
                  f"secondary collisions={runs[-1]['ts']['coll_total'][-1]:.0f} "
                  f"E[sec]={runs[-1]['exp_secondary']:.3e}", flush=True)

    np.save(f"{args.out}/mc_runs.npy",
            np.array([r["ts"] for r in runs], dtype=object), allow_pickle=True)
    np.save(f"{args.out}/detail_run.npy",
            np.array([runs[0]], dtype=object), allow_pickle=True)

    sec = np.array([r["ts"]["coll_total"][-1] for r in runs])
    esec = np.array([r["exp_secondary"] for r in runs])
    summary = dict(
        n_sats=cfg.n_sats, years=cfg.years, seeds=cfg.seeds,
        p_any_secondary=float(np.mean(sec > 0)),
        mean_secondary=float(sec.mean()),
        R0_expected_secondaries=float(esec.mean()),
        peak_frag=float(max(r["ts"]["n_frag"].max() for r in runs)),
        frag_at_end=float(np.mean([r["ts"]["n_frag"][-1] for r in runs])),
        active_frac_end=float(np.mean(
            [r["ts"]["n_active"][-1] for r in runs]) / cfg.n_sats),
        dv_per_sat_total_ms=float(np.mean([r["ts"]["dv"][-1] for r in runs])),
    )
    with open(f"{args.out}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("[summary]", json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
