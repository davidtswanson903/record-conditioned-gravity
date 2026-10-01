# Related work

GENERATED from `docs-src/docs/related-work.md`. Full citations are in `data/references.yaml` (and `build/latex/refs.bib` after `make latex`).

This law sits among several proposals for coupling gravity to quantum matter without quantizing the gravitational field, and among the arguments for why that coupling should be quantized after all. What follows states exactly what differs, one family at a time.

## Unconditional Schrödinger–Newton

The source is the full quantum-mechanical mean density, regardless of what records of a system's position exist. This repository's law reduces to it exactly in the no-record limit (`f(1)=1`; see `law.md`), and departs from it wherever a record exists at all. **Unconditional Schrödinger–Newton is not excluded by experiment.** The most sensitive published test to date [Y25] — an optical cavity of finesse over 350,000 on a 0.6 mHz torsion pendulum, three months of data, sensitivity 0.3 μrad/√Hz at 2.5 mHz — reports no evidence for a semiclassical-gravity effect, and explicitly does not claim to exclude the equation. An earlier draft of this work's own write-up claimed the opposite; see `realistic.md` stage 4 and `LIMITS.md` item 9 for the correction.

## Measurement-conditioned Schrödinger–Newton

The source is conditioned on what an experimenter's own readout has resolved — the two-peak spectral signature this repository's `rcg.laws.sn_conditioned` module reproduces as a limit [Yang2013]. This is the proposal's own discriminator against this repository's law: a distant party's choice of measurement basis moves the measurement-conditioned law's prediction (it signals), where this repository's law — conditioned on every record that exists, not only the readout — does not (`CLAIMS.md`, T4). Realistically, the measurement-conditioned law also avoids the resolvability wall this repository's law does not: its broadening rate is one the experimenter sets, not the environment's own (`realistic.md` stage 4). [Helou2017] and, under a third "causal-conditional" prescription that conditions on the continuous outcome trajectory itself rather than on records or a final readout, the more recent [LiuEtAl2023] extend this same family; the minimum-observation-time scaling this repository borrows (`minimum-time.md`) is [Helou2017]'s own result.

## Classical-channel and spontaneous-localization models

Two distinct ways of avoiding the pathologies of unconditional Schrödinger–Newton without conditioning on records: [Kafri2014] treats the gravitational interaction between two resonators as a genuinely stochastic classical measurement channel, which — like this repository's law — cannot entangle two masses through gravity alone, but which (unlike this repository's law; see `test_the_law_adds_no_noise` in `CLAIMS.md`) necessarily adds decoherence/noise as the price of not signalling, since a classical channel cannot transmit quantum correlations without one. [TilloyDiosi2016] instead sources gravity from the state a spontaneous-localization (collapse) model has already localized, eliminating the single-particle self-interaction unconditional Schrödinger–Newton has and predicting an added gravitational decoherence term tied to the specific collapse model's own parameters. This repository's law shares the "condition on what is actually localized, not the full superposition" intuition with both, but replaces their mechanism (an intrinsically stochastic physical process) with conditioning on records that already exist for other reasons — and adds no noise of its own in doing so (see the new claim and test this build added, above).

## Classical–quantum gravity

[Oppenheim2023] constructs spacetime as a genuinely classical degree of freedom coupled to quantum matter through a trace-preserving, completely positive master equation, forcing quantum mechanics itself to become fundamentally stochastic as the price of a consistent coupling. This is a different scope than this repository's law, which modifies only the *source* term gravity responds to and leaves the matter's quantum dynamics otherwise standard; [Oppenheim2023] modifies the dynamics itself.

## Collapse models

A CSL-type collapse model (`rcg.laws.collapse`) is used in this repository as a rival to exclude, not to test: the point-particle heating rate [BassiRMP2013] at Adler's parameters already exceeds a representative platform's own thermal diffusion rate by eight to eleven orders of magnitude (`results/realistic.json`, `stage2_virtual.platforms.*.csl_relative_to_env`), so this rival is excluded on thermal grounds before any self-gravity question is asked. CSL [GRW1986, BassiRMP2013] and the gravity-motivated Diósi–Penrose criterion [Diosi1989, Penrose1996] are both collapse mechanisms rather than sourcing laws in this repository's sense: they remove superpositions outright rather than conditioning gravity's source on what records of them exist.

## Gravitationally-induced-entanglement proposals

[BoseEtAl2017] and [MarlettoVedral2017], published back to back, propose witnessing the gravitational field's quantum nature directly: two masses, each in a spatial superposition, become entangled through their mutual gravitational attraction if and only if the mediating field is itself quantum. This is exactly the experiment P1 (`README.md` §2; `CLAIMS.md` claim 8) speaks to: this repository's law predicts **zero** entanglement in the unrecorded two-mass case, under its own mean-field treatment, distinguishing it in principle from a quantized mediator — the same qualitative distinction [BoseEtAl2017] and [MarlettoVedral2017] propose to measure directly.

## The case for quantizing gravity

Two arguments motivate the view that gravity must ultimately be quantized rather than sourced semiclassically by any of the above. [EppleyHannah1977]'s thought experiment argues that a classical gravitational field interacting with quantum matter must violate momentum conservation, the uncertainty principle, or no-signalling — contested since on the grounds that the required apparatus may be unbuildable even in principle, but still the standard theoretical starting point. [PageGeilker1981]'s Cavendish-type experiment is the standard *experimental* half of the case: a torsion balance coupled to a source mass whose position is entangled with a radioactive decay always deflects toward one branch or the other, never toward the expectation value unconditional semiclassical gravity predicts — direct evidence against sourcing gravity by the unconditioned mean, though not against conditioning it on records, which is what this repository's law does instead.

## Optomechanical and torsion-balance tests

`data/platforms.yaml` draws its three platforms from [G16] (an osmium microdisc proposal), [W21] (a published milligram torsion-balance measurement), and [D20] (a published ground-state-cooled levitated sphere). `minimum-time.md` checks this repository's own field-wide bound against [Y25]'s reported run time, and credits [Helou2017] for the scaling law it specializes.
