// Research paper draft: LEO mega-constellation Kessler risk simulation
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel,
  AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, Math: DMath, MathRun, MathFraction, MathSubScript,
  MathSuperScript,
} = require("docx");

const FONT = "Times New Roman";
const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 22, ...o });
const p = (children, o = {}) =>
  new Paragraph({
    children: Array.isArray(children) ? children : [r(children)],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 160, line: 276 },
    ...o,
  });
const h1 = (t) =>
  new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 },
    children: [new TextRun({ text: t, font: FONT, size: 28, bold: true, color: "1a1a2e" })] });
const h2 = (t) =>
  new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 },
    children: [new TextRun({ text: t, font: FONT, size: 24, bold: true, color: "1a1a2e" })] });
const eq = (runs) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 },
    children: runs });
const it = (t) => r(t, { italics: true });
const sub = (t) => r(t, { subScript: true, italics: true });
const sup = (t) => r(t, { superScript: true });
const caption = (t) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: [new TextRun({ text: t, font: FONT, size: 20, italics: true, color: "444444" })] });
const img = (path, w, hgt) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path),
      transformation: { width: w, height: hgt } })] });

// ---------- tables ----------
const B = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const borders = { top: B, bottom: B, left: B, right: B };
const cell = (t, w, bold = false, shade = false) =>
  new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: shade ? { type: ShadingType.CLEAR, fill: "e8ecf5" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 20, bold })] })],
  });
const table = (widths, rows) =>
  new Table({
    columnWidths: widths, width: { size: widths.reduce((a, b) => a + b), type: WidthType.DXA },
    rows: rows.map((row, i) =>
      new TableRow({ children: row.map((t, j) => cell(t, widths[j], i === 0, i === 0)) })),
  });

const t0 = table([2200, 3580, 3580], [
  ["Dimension", "Legacy orbital-capacity models (e.g., MOCAT)", "This framework"],
  ["System state", "Global multi-decade environmental equilibrium", "Single-event point-stability response"],
  ["Target scale", "Extrapolates aggregate background populations", "Direct operational control loop up to 1e6 nodes"],
  ["Primary variable", "Post-mission-disposal (PMD) failure averages", "Geometric packing layout and active shell dispersion"],
  ["Velocity profile", "Simplified isotropic assumptions across broad orbital regions", "Localized kinetics resolved in 25 km spatial bins"],
]);

const t1 = table([3600, 2200, 3560], [
  ["Parameter", "Value", "Notes"],
  ["Shell altitude / inclination", "550 km / 53.0 deg", "Walker-delta, 10 planes x 10 slots (N=100 baseline)"],
  ["Satellite mass / area / Cd", "260 kg / 25 m2 / 2.2", "Starlink-class; hard-body radius 2 m"],
  ["Station-keeping dead band", "+/- 500 m in semi-major axis", "Impulsive re-boost at band floor"],
  ["Drag uncertainty", "20% (1-sigma, per step)", "Multiplicative white noise on drag acceleration"],
  ["Design life / PMD success", "7 yr / 95%", "Retired satellites replaced in slot"],
  ["Random failure rate", "0.5% per yr", "Failed satellites become derelict (no disposal)"],
  ["Conjunction avoidance", "99% effective", "Applies to trackable objects (>10 cm) vs active satellites"],
  ["External impactor", "10 kg at 12 km/s, t = 5 yr", "Catastrophic per 40 J/g threshold"],
  ["Trackable / lethal thresholds", "Lc > 10 cm / 1-10 cm", "1-10 cm as weighted super-particles (400)"],
  ["Mean crossing velocity", "8 km/s", "Kinetic-theory collision rates, 25 km altitude bins"],
  ["Time step / horizon / seeds", "5 d / 100 yr / 30", "Mean-element secular propagation"],
]);

const t2 = table([2340, 2340, 2340, 2340], [
  ["N (single shell)", "R0 (E[secondary collisions])", "Sampled events", "Source"],
  ["100", "3.5e-5", "0 (30 runs, 100 yr)", "simulation"],
  ["316", "9.1e-5", "0", "simulation, 100 yr"],
  ["1,000", "2.4e-4", "0", "simulation, 100 yr"],
  ["3,162", "7.3e-4", "0", "simulation, 100 yr"],
  ["10,000", "2.1e-3", "0", "simulation, 100 yr"],
  ["25,000", "1.4e-2", "1 catastrophic; 16 debris kills", "direct simulation, 100 yr"],
  ["100,000", "9.1e-2", "4 catastrophic; 70 debris kills", "direct simulation, 40 yr"],
  ["1,000,000 (one shell)", "> 1 (supercritical)", "103 catastrophic in 10 yr; ~3,600 debris kills", "direct simulation, 10 yr"],
  ["1,000,000 (across 40 shells)", "1.4e-2 per shell", "equals N = 25,000 row", "direct simulation, 100 yr"],
]);

const t3 = table([4680, 2340, 2340], [
  ["Metric (N=100, 100 yr, 30 runs)", "Mean", "Notes"],
  ["Probability of any secondary collision", "0.00", "0/30 runs"],
  ["Cascade multiplier R0", "3.5e-5", "analytic expectation"],
  ["Trackable fragments (peak / at 100 yr)", "341 / ~0", "NASA SBM analytical expectation 341.7 (truncated)"],
  ["Fragment-cloud half-life", "0.84 yr", "550 km source altitude"],
  ["Active capacity at 100 yr", "99.0%", "replacement cycle active"],
  ["Station-keeping delta-V", "~60 m/s per yr", "static mean atmosphere (conservative)"],
  ["Satellites lost to 1-10 cm debris", "0.0", "expected value ~0.03"],
]);

// ---------- content ----------
const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 200 },
    children: [new TextRun({ text: "Collisional-Cascade Risk in an Actively Managed LEO Mega-Constellation: A 100-Year Monte Carlo Assessment of Single-Breakup Scenarios", font: FONT, size: 34, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [new TextRun({ text: "Vikas Yadav", font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    children: [new TextRun({ text: "Draft manuscript - July 2026 - citations and figures to be finalized", font: FONT, size: 20, italics: true, color: "666666" })] }),

  h1("Abstract"),
  p("Proposals for low-Earth-orbit (LEO) mega-constellations now reach the million-satellite scale, raising critical concerns over single-event-triggered Kessler syndromes. This paper isolates the marginal, self-inflicted cascade risk by embedding an active operational control loop directly into a stochastic orbital propagation framework. A 100-year Monte Carlo assessment is conducted for an actively managed Walker shell at 550 km, coupling mean-element propagation (J2 secular perturbations and atmospheric drag with 20% stochastic dispersion) with autonomous conjunction avoidance, dead-band station-keeping with end-of-life replacement, and NASA Standard Breakup Model fragmentation kinematics. Simulating an external 10 kg debris strike - a 270 kg catastrophic fragmentation event producing approximately 341 trackable and 17,000 lethal sub-trackable fragments - reveals that active avoidance and a self-cleaning atmosphere yield zero secondary collisions across thirty baseline histories, establishing a highly sub-critical cascade multiplier of R0 = 3.5e-5 at N = 100. Parametric population scaling from N = 100 to N = 10,000 demonstrates a robust empirical power law, R0 proportional to N^0.89. Direct simulation at larger N, however, reveals a superlinear departure driven by the accumulating derelict inventory and sub-trackable satellite kills: R0 = 0.014 at N = 25,000 and R0 = 0.091 at N = 100,000. Packed into a single 550 km shell, a million-satellite fleet is supercritical - expected secondary collisions exceed unity within a year of the strike and collisional activity becomes self-sustaining - whereas the same fleet distributed across 40 distinct orbital shells remains sub-critical by nearly two orders of magnitude (R0 = 0.014 per shell, simulated directly). These results indicate that million-satellite architectures are not intrinsically Kessler-critical, provided mass is concentrated in strong atmospheric-drag regimes and dispersed across shells. We define the engineered margins of safety controlled by active shell dispersion, post-mission-disposal compliance, and collision-avoidance capability, and locate the shell density (~1e5) beyond which the single-event framing itself breaks down."),
  p([r("Keywords: ", { bold: true }), r("space debris; Kessler syndrome; mega-constellations; NASA breakup model; Monte Carlo simulation; orbital capacity")]),

  h1("1. Introduction"),
  p("Kessler and Cour-Palais [1] first showed that collisions between artificial satellites could become the dominant source of orbital debris, and that above a critical spatial density the debris population grows through collisional cascading even without further launches [2]. The question has acquired new urgency: operational constellations already exceed ten thousand satellites, and in January 2026 SpaceX filed with the U.S. Federal Communications Commission for an orbital data-center constellation of up to one million satellites operating between 500 and 2,000 km [16], alongside its pending application for a 100,000-satellite third-generation Starlink system [17]. The million-satellite regime has thus moved from thought experiment to regulatory docket. At such scales intuition is an unreliable guide - LEO is vast, but fragmentation debris is prolific and fast - and quantitative cascade analysis becomes a prerequisite for both licensing and design."),
  p("Most debris-environment analyses model the full historical population, including rocket bodies and legacy debris, as detailed in the related work reviewed in Section 2. Here we isolate a narrower, sharper question: if a well-designed, actively controlled constellation is struck once by an external debris object, does the resulting fragment cloud propagate into a cascade within the constellation itself? This isolates the marginal risk attributable to the constellation's own population density, which is the quantity most directly controlled by constellation design. We make three contributions: (i) a compact, reproducible simulation framework coupling managed-constellation operations to a debris-generation and collision-kinetics model; (ii) a 100-year Monte Carlo characterization of constellation health and fragment-cloud evolution after a representative strike; and (iii) an empirical scaling law for the cascade multiplier R0 as a function of constellation size, with extrapolation to the million-satellite regime."),

  h1("2. Related Work"),
  p("The foundational literature established both the mechanism and the threshold character of collisional cascading. Kessler and Cour-Palais [1] computed collision frequencies for the 1978 catalog population and predicted the formation of a debris belt; Kessler [2] later formalized the notion of a critical density above which the debris population grows without further launches - the regime now bearing his name. NASA's engineering lineage produced the EVOLVE and LEGEND evolutionary models and, importantly for the present work, the Standard Breakup Model of EVOLVE 4.0 [3], which remains the community reference for fragment size, area-to-mass, and ejection-velocity distributions. Using LEGEND, Liou and Johnson demonstrated that the then-existing LEO population was already collisionally unstable above roughly 800 km even under a no-further-launch assumption [4], [8], establishing that altitude - through the atmospheric drag sink - is the dominant environmental variable in cascade dynamics."),
  p("A second wave of studies addressed the mega-constellation era directly. Lewis, Radtke, and Rossi [9] showed the debris environment to be acutely sensitive to large-constellation deployment parameters, identifying post-mission-disposal (PMD) compliance as the single most influential mitigation lever; Radtke et al. [10] reached similar conclusions for the OneWeb architecture specifically. Le May et al. [11] computed collision probabilities for the proposed broadband constellations against the background debris flux, and Rossi et al. [12] developed short- and long-term analysis tools spanning constellation deployment through end-of-life. Boley and Byers [13] broadened the assessment beyond collision risk to atmospheric and astronomical impacts, arguing that constellation scale itself is a governance problem. Collectively these studies treat the constellation as a source term added to the historical environment; the response of the managed system itself - station-keeping, avoidance, replacement, disposal - is typically represented by aggregate compliance parameters rather than an operating control loop."),
  p("Most recently, the orbital-capacity literature has reframed the question from environment projection to carrying capacity. D'Ambrosio, Lifson, and Linares [14] introduced multi-shell, multi-species source-sink models (MOCAT-3 and successors) that define capacity via the stable equilibria of the debris-satellite system, and the associated open-source Monte Carlo tool MOCAT-MC [15] propagates full object populations with probabilistic failures and collisions. MOCAT-based analyses locate the unstable regime above roughly 600-800 km and find that even small PMD shortfalls have outsized effects at mega-constellation scale - conclusions our results reproduce from the opposite direction. The distinction between these model families and the present framework is worth stating precisely. MOCAT and the legacy evolutionary models resolve multi-decade global background equilibria, driven by aggregate compliance averages applied to whole populations; the present framework resolves the localized, immediate point-stability response of an active operational control loop - station-keeping, autonomous avoidance, in-slot replacement, and disposal - to a single fragmentation event inside the constellation. The gap this paper addresses is therefore the single-event, managed-constellation response: rather than asking how a million satellites perturb the century-scale environment, we ask whether one fragmentation inside an actively controlled shell is self-amplifying, and how that answer scales with shell population. This complements global capacity models by isolating the marginal, design-controllable component of cascade risk within an explicitly modeled operational control loop. Table 1 summarizes the contrast."),
  t0,
  caption("Table 1. Positioning of this framework relative to legacy orbital-capacity models."),

  h1("3. Simulation Framework"),
  h2("3.1 Constellation design and operations"),
  p("The constellation is a Walker-delta shell [6] at 550 km altitude and 53.0 deg inclination, with satellites distributed uniformly over planes in right ascension and phased within planes so that nominal along-track and cross-plane separations are maximized. The baseline uses N = 100 satellites in 10 planes; N is a free parameter. Satellites are Starlink-class (260 kg, 25 m2 cross-section, drag coefficient 2.2). Active satellites perform dead-band station-keeping: when stochastic drag lowers the semi-major axis 500 m below nominal, an impulsive re-boost restores the upper band edge, with delta-V accounted as dv = (v/2)(da/a). Satellites retire at a 7-year design life and are replaced in-slot; disposal succeeds with 95% probability, otherwise the satellite becomes a derelict. Random failures (0.5% per year) also produce derelicts, which cannot maneuver or be disposed. Active satellites avoid trackable conjunctions with 99% effectiveness."),
  h2("3.2 Orbit propagation"),
  p("Objects are propagated in mean orbital elements with a 5-day step over 100 years. Secular J2 nodal regression follows"),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 },
    children: [new DMath({ children: [
      new MathFraction({ numerator: [new MathRun("dΩ")], denominator: [new MathRun("dt")] }),
      new MathRun(" = −"),
      new MathFraction({ numerator: [new MathRun("3")], denominator: [new MathRun("2")] }),
      new MathSubScript({ children: [new MathRun("J")], subScript: [new MathRun("2")] }),
      new MathRun(" n "),
      new MathSuperScript({
        children: [
          new MathRun("("),
          new MathFraction({
            numerator: [new MathSubScript({ children: [new MathRun("R")], subScript: [new MathRun("E")] })],
            denominator: [new MathRun("p")] }),
          new MathRun(")")],
        superScript: [new MathRun("2")] }),
      new MathRun(" cos i"),
    ] })],
  }),
  p("with the corresponding secular rates applied to the argument of latitude. Atmospheric drag uses a piecewise-exponential density model [5] evaluated at perigee altitude, da/dt = -rho B sqrt(mu a), where B = Cd A/m is the ballistic coefficient; eccentricity is damped proportionally, so apogee decays faster than perigee. Path deviations are modeled as 20% (1-sigma) multiplicative white noise on the drag acceleration, representing atmospheric variability and maneuver execution errors. Objects with perigee below 200 km are removed as reentered. The J2-drag mean-element formulation reproduces the analytic nodal rate at the shell (-4.489 deg/day simulated vs. -4.49 deg/day analytic) and yields derelict decay times from 550 km of two to five years, consistent with observed Starlink-class lifetimes."),
  h2("3.3 Fragmentation model"),
  p("Catastrophic collisions (specific impact energy above 40 J/g) generate fragments per the NASA Standard Breakup Model [3]: the cumulative size distribution N(>Lc) = 0.1 M^0.75 Lc^-1.71, with M the total participating mass. Fragments larger than 10 cm are tracked individually; the 1-10 cm lethal-but-untrackable population is represented by 400 weighted super-particles. Area-to-mass ratios follow a lognormal distribution about the EVOLVE 4.0 trend, and ejection velocities follow the EVOLVE delta-V distribution, log10(dv) ~ N(0.9 log10(A/m) + 2.9, 0.4), applied isotropically and mapped through the velocity perturbation to new element sets. For the baseline 270 kg catastrophic event - representing the combined mass of the 260 kg active satellite and the 10 kg external impactor - the NASA Standard Breakup Model yields an analytical expectation of 341.7 fragments above 10 cm, realized as 341 per event under integer truncation, and approximately 17,400 in the 1-10 cm class."),
  h2("3.4 Collision kinetics"),
  p("Collision events are sampled per 25-km altitude bin using kinetic theory: for object classes i and j with bin populations Ni, Nj, mean hard-body radii, and shell volume V, the expected number of collisions per step is Ni Nj sigma v_rel dt / V, with sigma the combined cross-section and v_rel = 8 km/s. Pair channels comprise active-fragment, active-derelict (both attenuated by 99% avoidance), derelict-fragment, derelict-derelict, fragment-fragment (all catastrophic), and active vs. sub-trackable debris (satellite-killing but non-catastrophic, producing a derelict). Events are drawn from Poisson distributions each step; each sampled catastrophic collision invokes the breakup model on the participating objects, enabling cascade feedback. Alongside the sampled events, the simulator accumulates the analytic expectation of fragment-involved collisions, which provides a low-variance estimator of the cascade multiplier R0 even when sampled counts are zero."),
  h2("3.5 Scenario and Monte Carlo design"),
  p("At t = 5 years a 10 kg external debris object (representative of a legacy fragment on a crossing orbit) strikes one randomly selected active satellite at 12 km/s, a catastrophic event by a wide margin. Thirty Monte Carlo histories are run to 100 years for the baseline; single histories suffice for the R0 sweep because the analytic estimator is used. Table 2 summarizes all parameters."),
  t1,
  caption("Table 2. Simulation parameters."),

  h1("4. Results"),
  h2("4.1 Constellation health"),
  p("The managed constellation maintains 99% of design capacity throughout the century (Figures 1 and 2): the replacement cycle absorbs retirements, random failures, and the strike loss. Station-keeping consumes roughly 60 m/s per satellite-year - conservative relative to operational experience because the static mean atmosphere is on the dense side of the solar cycle at 550 km. Expected losses of active satellites to the sub-trackable fragment population are 0.03 satellites over the century; no such loss occurred in the sampled runs. The expected number of unmitigated satellite-fragment collision opportunities (avoidance workload proxy) remains below one conjunction-driven maneuver per satellite-decade after the initial cloud decays. We note the scope of this metric: it counts only conjunctions of active satellites with strike-generated fragments and with derelicts. Nominal intra-constellation conjunctions among actively phased satellites are excluded by construction, since Walker phasing renders them deterministic and margin-protected rather than stochastic; the real operational maneuver load, which also screens against background debris, is correspondingly higher."),
  img("fig1_population.png", 600, 367),
  caption("Figure 1. Population evolution by object class (mean and 5-95% envelope over 30 Monte Carlo runs). The external strike at t = 5 yr injects ~341 trackable and ~17,000 sub-trackable fragments; drag removes the trackable cloud within a decade."),
  img("fig4_health.png", 600, 382),
  caption("Figure 2. Constellation health over the 100-year horizon: active capacity, cumulative station-keeping delta-V, collision-avoidance workload, and post-strike collision events."),
  h2("4.2 Fragment-cloud evolution"),
  p("The breakup produces the classic Gabbard signature (Figure 4): apogees raised and perigees depressed symmetrically about the parent period, with a high-delta-V tail reaching above 2,000 km apogee. Differential nodal precession disperses the cloud from an orbital ring into a shell over months, visible as the RAAN-spread transient (Figure 5, right panel). Spatially, the cloud blooms across 300-1,000 km before drag sweeps it downward (Figure 3): the trackable population halves in 0.84 years and is essentially cleared within ten, while the highest-altitude, lowest-B tail persists longest. The sub-trackable population decays on a similar timescale at the source altitude; its high-altitude remnant persists for decades but at spatial densities too low to matter for the shell."),
  img("fig2_density_heatmap.png", 600, 333),
  caption("Figure 3. Trackable-fragment spatial density vs. altitude and time (single history). The constellation shell at 550 km is marked; drag clears the cloud from below upward."),
  img("fig3_gabbard.png", 540, 371),
  caption("Figure 4. Gabbard diagram of the fragment cloud immediately after the strike (suborbital fragments excluded)."),
  h2("4.3 Cascade response"),
  p("No secondary collision occurred in any of the thirty 100-year histories. The analytic cascade multiplier - the expected number of secondary catastrophic collisions caused by the parent breakup over the cloud lifetime - converges within a decade of the strike to R0 = 3.5e-5 for N = 100 (Figure 5, left panel): the single breakup falls short of self-replacement by more than four orders of magnitude. The dominant channel is fragment vs. derelict, since avoidance suppresses the fragment vs. active channel by two orders of magnitude; the derelict inventory (an equilibrium of one to two objects maintained by the 5% disposal failure and 0.5%/yr failure rates) is thus the constellation's principal contribution to its own cascade exposure."),
  img("fig5_kessler.png", 620, 200),
  caption("Figure 5. Cascade diagnostics: cumulative expected secondary collisions vs. the R0 = 1 criticality threshold (left); Monte Carlo distribution of sampled secondary collisions (center); ring-to-shell RAAN dispersion of the cloud (right)."),
  h2("4.4 Scaling with constellation size"),
  p("Repeating the experiment at N = 316, 1,000, 3,162, and 10,000 in the same shell yields the cascade multipliers of Table 3. Across this range a power-law fit gives R0 proportional to N^0.89 (fitted exponent 0.890; the endpoint pair alone yields 0.889); the exponent falls slightly below unity because a denser constellation also loses its fragment cloud slightly faster to the collisions themselves and to the fixed drag sink. Because expected cascade growth compounds multiplicatively, R0 in this regime also bounds the probability that a single strike initiates any secondary collision."),
  p("The framework's vectorized design permits direct simulation well beyond the fitted range, and the direct results overturn a naive extrapolation (Figure 6). At N = 25,000 (simulated over the full 100 years) the multiplier is R0 = 0.014 - roughly three times the power-law prediction - with one catastrophic secondary (active-derelict) and 16 sub-trackable satellite kills sampled. At N = 100,000 (40-year horizon) R0 = 0.091, nearly six times the extrapolated value, with four catastrophic secondaries sampled and the trackable fragment population peaking at 604, visibly above the 341 injected by the strike: cascade feedback is active. The departure is superlinear because two populations that scale with N compound: the derelict inventory (maintained by the 0.5%/yr failure rate and 5% disposal failures) and the rate of sub-trackable debris kills, each converting active, avoiding satellites into passive collision targets and activating channels whose rates scale as the product of two N-proportional populations."),
  p("At N = 1e6 in a single 550-km shell, direct simulation (10-year horizon, 20-day steps) shows the system is supercritical. Expected fragment-involved secondaries exceed unity within the first year after the strike and grow at roughly 2.4 per year without converging; over ten years the run sampled 103 catastrophic collisions (dominated by active-derelict and derelict-derelict pairs), approximately 3,600 satellites lost to sub-trackable debris, and a trackable fragment population sustained near 6,000. Indeed, at this density the single-event framing itself collapses: the shell's intrinsic derelict production makes it collisionally self-igniting irrespective of the external strike, which merely advances the onset. By contrast, distributing the same million satellites across 40 shells reduces each shell to the directly simulated N = 25,000 case, R0 = 0.014 per shell - sub-critical by nearly two orders of magnitude. Dispersion is therefore not merely prudent but load-bearing: it is the difference between a self-igniting shell and a comfortably stable architecture."),
  t2,
  caption("Table 3. Cascade multiplier vs. constellation size. All entries are simulated; no extrapolated values remain."),
  img("paper_fig5_r0_scaling.png", 520, 371),
  caption("Figure 6. Scaling of the cascade multiplier with single-shell constellation size. The low-N power law (dotted) underestimates beyond N ~ 1e4; direct simulation (orange squares) shows the superlinear derelict-mediated regime, culminating in a supercritical single-shell million-satellite case (red triangle). Dispersing the same fleet across 40 shells (green diamond) restores a two-order-of-magnitude margin."),
  t3,
  caption("Table 4. Baseline outcome summary."),

  h1("5. Discussion"),
  p("Three design levers explain the large sub-criticality margin. First, altitude: at 550 km the atmospheric residence time of fragmentation debris (half-life below one year for trackable fragments) is far shorter than the mean time between debris-generating events, so the environment is strongly self-cleaning; the same breakup at 800-1,200 km, where drag lifetimes reach decades to centuries, would yield a proportionally larger R0 and is the regime in which historical studies find instability [8]. Second, dispersion: R0 scales near-linearly with shell population at moderate densities and superlinearly beyond ~1e4 per shell, so spreading a fixed fleet across shells buys margin more than one-for-one precisely where it matters most - our direct simulations show it is the difference between a supercritical single shell and a stable 40-shell architecture. Third, operations: avoidance suppresses the largest collision channel, and disposal compliance controls the derelict inventory that dominates the residual risk and drives the superlinear regime. The practical reading is that a million-satellite LEO system is not intrinsically Kessler-critical, but neither is it automatically safe: its margin is an engineered quantity determined chiefly by how the fleet is packed."),
  p("The single-event framing bounds, but does not close, the cascade question - and our large-N runs locate where it breaks. Strikes are not rare at scale: the expected rate of external impacts grows with total constellation cross-section and with the background debris flux, so a million-satellite system should anticipate repeated fragmentation events per decade. Because clouds at 550 km decay within a few years, successive sub-critical events do not accumulate at the shell unless their rate approaches the clearing rate. More fundamentally, above roughly 1e5 satellites per shell the constellation's intrinsic derelict production makes collisional activity self-starting, so the relevant stability question shifts from the response to an external perturbation to the equilibrium of the shell's own source and sink terms; a full assessment requires coupling this framework to a background-debris and launch-traffic model, which we identify as the immediate next step."),

  p("These results bear directly on plans now before regulators. SpaceX's January 2026 FCC filing for up to one million solar-powered orbital data-center satellites at 500-2,000 km [16] represents, alongside the 100,000-satellite Starlink Gen3 application [17], the first concrete industrial commitment to the population regime studied here - and, in our reading, an encouraging one. The filing's scale would bring unprecedented on-orbit computing and solar-energy utilization, and our results indicate the ambition is not intrinsically foreclosed by cascade physics - provided the fleet is dispersed: a single 550-km shell holding the full million is supercritical in our direct simulations, but the same fleet spread across roughly 40 shells sits nearly two orders of magnitude below criticality per shell, and the filing's wide 500-2,000 km altitude range is precisely what makes such dispersion available. SpaceX's operational record - demonstrated autonomous conjunction avoidance, propulsive disposal at scale, and the highest PMD compliance rates yet observed - exercises precisely the levers our analysis identifies as decisive. The same analysis, however, sharpens the design question the filing leaves open: the upper portion of the proposed 500-2,000 km range lies in the weak-drag regime where fragment clouds persist for decades and the self-cleaning margin largely vanishes. A capacity-aware deployment that concentrates mass low, disperses it across shells, and reserves high shells for the smallest sustainable populations would let the million-satellite vision proceed on a defensible physical footing, and frameworks of the kind presented here - fast enough to sweep design space - are the natural tool for negotiating that architecture."),

  h1("6. Limitations"),
  p("The model omits the existing background debris population and non-constellation traffic, so all reported risk is the marginal, self-inflicted component; absolute collision rates in the real environment are higher. The static exponential atmosphere neglects solar-cycle density variation, which modulates both station-keeping cost and debris clearing times by factors of a few in either direction. During solar maximum, atmospheric expansion increases drag at 550 km by up to an order of magnitude, clearing fragment clouds substantially faster than the baseline model dictates; the static atmosphere therefore represents a conservative assessment of debris-clearing timelines over much of the cycle, while solar-minimum conditions would lengthen fragment residence (and raise R0) by a bounded factor of a few. On the operations side, the same dense-side static profile makes the quoted station-keeping delta-V conservative. The full solar-cycle sensitivity of R0 should be swept explicitly in future work."),
  p("The kinetic-theory collision sampler assumes a well-mixed population within each 25-km altitude bin, characterized by a single 8 km/s mean crossing velocity. A Walker-delta constellation is not well-mixed: it comprises ordered, near-parallel tracks along which intra-constellation relative velocities approach zero, punctuated by severe relative-velocity spikes at high-latitude planar crossings. The isotropic 8 km/s figure is a spatial-averaging proxy that balances these structural extremes - conservative for co-planar geometry, optimistic for head-on crossings - and is most defensible for the fragment-versus-satellite channels that dominate R0, since post-breakup fragment orbits are rapidly randomized in node and phase. The large-N runs trade horizon and step size for scale (40 years at N = 1e5; 10 years with 20-day steps at N = 1e6); the supercritical finding at 1e6 is insensitive to this because expected secondaries exceed unity within the first year and grow monotonically, but longer single-history runs and multi-seed replication at these scales would tighten the quantitative rates. Finally, fragment area-to-mass and delta-V distributions are simplified relative to the full EVOLVE 4.0 implementation, and satellites are treated as single-body spheres for collision purposes."),

  h1("7. Conclusion"),
  p("A single external fragmentation event in an actively managed 550-km constellation does not initiate a collisional cascade at shell populations up to 1e5, where direct simulation gives R0 = 0.091; at 1e6 in a single shell the system is supercritical and collisional activity becomes self-sustaining, while the same fleet dispersed across 40 shells remains sub-critical by nearly two orders of magnitude (R0 = 0.014 per shell, simulated directly). The underlying mechanism reduces to a balance sheet of debris injection against debris removal: packing density sets the injection-to-exposure product and drives R0 near-linearly (N^0.89) at moderate densities and superlinearly beyond ~1e4 per shell as the derelict inventory compounds, while the atmospheric drag sink at low altitude sets a fast, population-independent removal rate. At 550 km the removal side of the ledger wins comfortably below roughly 1e5 satellites per shell; beyond that, derelict-mediated injection overtakes the fixed sink. Cascade margin is thus governed by four controllable factors - altitude (drag clearing), shell dispersion, disposal compliance, and avoidance capability - and erodes predictably as each is relaxed. The framework presented here runs a century of constellation-plus-debris evolution in seconds per history, making it suitable for direct million-object simulation, multi-shell design optimization, and coupling to background-environment models in future work."),
  p("Because the licensing debate this work informs is ultimately public, we have paired the technical analysis with a science-communication companion: a one-page poster that presents the same results - the domino-score (R0) framing of cascade risk, the growth of risk with packing density, the supercriticality of a single overcrowded shell versus the safety of a dispersed fleet, and the self-cleaning action of the low-altitude atmosphere - in language and visuals accessible to a general audience, including school-age readers. The poster reproduces the Figure 6 scaling result and the fragment-decay history of Figure 1 in simplified form, with all numbers drawn directly from the simulations reported here. We regard such companion artifacts as part of the responsible dissemination of orbital-capacity research, given the level of public concern that the term Kessler syndrome now attracts."),

  h1("References"),
  p("[1] Kessler, D. J., and Cour-Palais, B. G., \"Collision Frequency of Artificial Satellites: The Creation of a Debris Belt,\" Journal of Geophysical Research, Vol. 83, No. A6, 1978, pp. 2637-2646.", { alignment: AlignmentType.LEFT }),
  p("[2] Kessler, D. J., \"Collisional Cascading: The Limits of Population Growth in Low Earth Orbit,\" Advances in Space Research, Vol. 11, No. 12, 1991, pp. 63-66.", { alignment: AlignmentType.LEFT }),
  p("[3] Johnson, N. L., Krisko, P. H., Liou, J.-C., and Anz-Meador, P. D., \"NASA's New Breakup Model of EVOLVE 4.0,\" Advances in Space Research, Vol. 28, No. 9, 2001, pp. 1377-1384.", { alignment: AlignmentType.LEFT }),
  p("[4] Liou, J.-C., and Johnson, N. L., \"Risks in Space from Orbiting Debris,\" Science, Vol. 311, No. 5759, 2006, pp. 340-341.", { alignment: AlignmentType.LEFT }),
  p("[5] Vallado, D. A., Fundamentals of Astrodynamics and Applications, 4th ed., Microcosm Press, Hawthorne, CA, 2013.", { alignment: AlignmentType.LEFT }),
  p("[6] Walker, J. G., \"Satellite Constellations,\" Journal of the British Interplanetary Society, Vol. 37, 1984, pp. 559-572.", { alignment: AlignmentType.LEFT }),
  p("[7] Brouwer, D., \"Solution of the Problem of Artificial Satellite Theory Without Drag,\" The Astronomical Journal, Vol. 64, 1959, pp. 378-397.", { alignment: AlignmentType.LEFT }),
  p("[8] Liou, J.-C., and Johnson, N. L., \"Instability of the Present LEO Satellite Populations,\" Advances in Space Research, Vol. 41, No. 7, 2008, pp. 1046-1053.", { alignment: AlignmentType.LEFT }),
  p("[9] Lewis, H. G., Radtke, J., Rossi, A., et al., \"Sensitivity of the Space Debris Environment to Large Constellations and Small Satellites,\" Proceedings of the 7th European Conference on Space Debris, ESA/ESOC, Darmstadt, 2017.", { alignment: AlignmentType.LEFT }),
  p("[10] Radtke, J., Kebschull, C., and Stoll, E., \"Interactions of the Space Debris Environment with Mega Constellations - Using the Example of the OneWeb Constellation,\" Acta Astronautica, Vol. 131, 2017, pp. 55-68.", { alignment: AlignmentType.LEFT }),
  p("[11] Le May, S., Gehly, S., Carter, B. A., and Flegel, S., \"Space Debris Collision Probability Analysis for Proposed Global Broadband Constellations,\" Acta Astronautica, Vol. 151, 2018, pp. 445-455.", { alignment: AlignmentType.LEFT }),
  p("[12] Rossi, A., Petit, A., and McKnight, D., \"Short-Term Space Safety Analysis of LEO Constellations and Clusters,\" Acta Astronautica, Vol. 175, 2020, pp. 476-483.", { alignment: AlignmentType.LEFT }),
  p("[13] Boley, A. C., and Byers, M., \"Satellite Mega-Constellations Create Risks in Low Earth Orbit, the Atmosphere and on Earth,\" Scientific Reports, Vol. 11, 2021, Art. 10642.", { alignment: AlignmentType.LEFT }),
  p("[14] D'Ambrosio, A., Lifson, M., and Linares, R., \"The Capacity of Low Earth Orbit Computed Using Source-Sink Modeling,\" arXiv:2206.05345, 2022.", { alignment: AlignmentType.LEFT }),
  p("[15] MIT ARCLab, \"MOCAT-MC: MIT Orbital Capacity Assessment Toolbox, Monte Carlo,\" open-source software, https://github.com/ARCLab-MIT/MOCAT-MC, accessed July 2026.", { alignment: AlignmentType.LEFT }),
  p("[16] Foust, J., \"SpaceX Files Plans for Million-Satellite Orbital Data Center Constellation,\" SpaceNews, February 2026 (FCC filing of January 30, 2026).", { alignment: AlignmentType.LEFT }),
  p("[17] \"SpaceX Wants to Launch 100,000 Starlink Satellites to Orbit,\" Space.com, 2025 (FCC application for third-generation Starlink).", { alignment: AlignmentType.LEFT }),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 },
      margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("kessler_constellation_paper.docx", buf);
  console.log("wrote kessler_constellation_paper.docx");
});
