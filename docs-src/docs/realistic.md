# Testability under realistic conditions

GENERATED from `docs-src/docs/realistic.md`; every number is read from `results/realistic.json`. Source: `experiments/realistic/` (five stages), built on `rcg.models.gaussian` and `rcg.laws`. Reproduce with `make realistic` (well under an hour).

**The question.** The computational check (`tests.md`) uses idealized two-branch states. A real test uses a massive oscillator in a cryostat, continuously decohered by its environment and read out by light. Does the law's prediction survive contact with a real platform, and can a real experiment tell this law apart from its rivals?

**The headline result: no, not as the naive protocol is specified — and the reason is a shape failure, not a size one.** The same records that shrink the law's own source variance also set the *width* of the one spectral feature that would carry it, through the same localization rate. "Resolvability" — that feature's distance from the main resonance, divided by its own width — is {{resolvabilityOsmium}} on a published optomechanical proposal's own platform, {{resolvabilityTorsion}} on a milligram torsion balance, and {{resolvabilityLevitated}} on a ground-state-cooled levitated sphere. Below one, the feature is a shoulder on the main line, not a resolvable peak, and no integration time recovers it.

## Stage 0 — the adapter

The two-branch law is extended to a continuously decohered Gaussian oscillator, three steps, each forced rather than chosen: how much record exists (the overlap read off the state's purity); what the source is (the law's own interpolation, applied to the conditioned and unconditioned covariances); and what it does (two resonances — the conditional mean's, and the fluctuation about it). The adapter reduces to the two-branch law exactly in the two-branch limit, and the underlying Gaussian filter reproduces both of its required limits (equipartition unconditioned; the ground state fully conditioned) — see `CLAIMS.md`.

## Stage 1 — three real platforms

| platform | source | resolvability | thermal occupation |
| --- | --- | --- | --- |
| osmium microdisc, Paul trap | optomechanical Schrödinger–Newton test proposal | {{resolvabilityOsmium}} | {{nbarOsmium}} |
| milligram torsion balance | a published gravitational-coupling measurement | {{resolvabilityTorsion}} | {{nbarTorsion}} |
| ground-state levitated sphere | a published ground-state cooling result | {{resolvabilityLevitated}} | {{nbarLevitated}} |

Every platform's parameters, with citations and explicitly marked assumptions, are in `data/platforms.yaml`. The law's weight on the unconditioned state is nonzero **only** where thermal occupation is below one half — true of none of the first two platforms, and the reason the third was included at all.

**The third platform's self-gravity frequency is overstated.** The ground-state levitated sphere is silica, and `data/platforms.yaml` uses silicon's published lattice constant for it (the two are chemically related but not identical) because no silica value for the crystal-regime formula is available — marked `ASSUMED` in the data file. The effect this inflates is the one effect this platform could in principle show (§ "f is nonzero only..." above), so the honest direction of the error is toward *overstating* this repository's own best case, not toward hiding a weakness.

## Stage 2 — the virtual experiment, and one correction to the protocol

Simulating the naive lock-in observable (the raw power spectrum at the probe frequency, switched with an ancilla) **fails its own control**: it moves by up to {{qmLockinRaw}} of the baseline signal under standard quantum mechanics, because the ancilla's own backaction heats the oscillator — a real physical effect, not a bug. The second resonance's *weight*, extracted separately from the heating, passes every control exactly. A protocol built on the naive observable would misread ordinary heating as a gravitational signal.

## Stage 3 — the feasibility map

Resolvability does not depend on the oscillator's mass, to {{massIndependenceSpread}} over fourteen orders of magnitude — the opposite of the usual intuition that a stronger self-gravity effect needs more mass. It is bounded by `Q/T`: reaching resolvability one with osmium needs `Q/T` of order {{qtOsmiumMilliHz}} K⁻¹ at a millihertz, or {{qtOsmiumTenHz}} K⁻¹ at ten hertz. A feasible corner exists — 1 mHz, `Q=1e12`, 1 mK meets all three of the experiment's conditions (resolvability one, and separation from each rival law within a month) — but feasibility is a **window, not a threshold**: push `Q` far enough past the floor and the resonance becomes too narrow for a periodogram to gather enough independent samples in reasonable time, and feasibility is lost again from the other side.

## Stage 4 — three challenges, each run rather than argued

1. **Does the conclusion rest on the adapter's one extrapolation** (reading a thermal oscillator's record weight through its state's purity, past where the law is stated for two branches)? An independent second reading — coherence of the reduced state at the material's own lattice scale, sharing no algebra with the purity-based route — agrees on both platforms the conclusion depends on. No.
2. **Is unconditional Schrödinger–Newton excluded by experiment?** No — see `minimum-time.md` and `related-work.md` for the published bound, which reports no evidence either way rather than an exclusion.
3. **Does the same resolvability wall defeat the measurement-conditioned rival law too?** No, and the reason is exact: that rival's broadening rate is one the experimenter sets, while this law's is the environment's own. The rival clears the same imprecision floor this law never does, by a factor of thermal occupation that reaches {{thermalOccupationFactorOsmium}} on the osmium platform. What *does* transfer to every spectroscopic proposal, this law's or any other's, is weaker and is the subject of `minimum-time.md`.
