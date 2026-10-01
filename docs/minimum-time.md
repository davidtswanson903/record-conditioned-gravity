# A field-wide minimum observation time

GENERATED from `docs-src/docs/minimum-time.md`; every number is read from `results/realistic.json`. Source: `experiments/realistic/stage4_robust.py`.

**Novelty, stated honestly, per this repository's own standard.** The basic relation this section rests on — that the time needed to resolve a spectral feature against a background scales with the feature's own inverse width — is not new. [Helou2017] already derives an explicit, numerically fitted scaling law for exactly this kind of measurement, `tau_min(h) ≈ 27/h^0.73 × 2/γ` (their eq. 120, for a Lorentzian peak of normalized height `h` against a flat background at 10% confidence), in this exact subfield (optomechanical tests of Schrödinger–Newton-type effects). **The result below is a special, law-independent case of that already-published family of bounds, not a new discovery.** What this repository adds, narrowly: a bound that applies to *any* law with a conditioned second resonance, independent of the resolvability or confidence-level details [Helou2017] computes for a specific proposal; and a check against a real experiment's own reported run time rather than only a simulated one.

## The bound this repository derives

A spectral feature of half-width `Gamma` cannot be resolved in less than about one coherence time, `2*pi/Gamma`. This repository's `experiments/realistic/stage4_robust.py` additionally shows that **every law with a conditioned second resonance** — this repository's own, and the measurement-conditioned rival alike — has `Gamma >= 2*gamma` (`gamma` the oscillator's own mechanical damping), because the imprecision floor every readout carries forces it. Combining the two:

```
t_min = pi * Q / omega_0
```

independent of which specific law produces the resonance, its predicted size, or the confidence level demanded. This is weaker than [Helou2017]'s own scaling law (which also captures how the *signal-to-noise* requirement shortens or lengthens the time for a specific proposal) but, unlike it, does not depend on which law or platform is in question: it is a floor under *any* of them. It grows **with** `Q` — sharpening an oscillator's resonance to make a conditioned feature narrower and more distinct costs observation time in exact proportion. It is the reason the feasibility window in `realistic.md` has a ceiling as well as a floor.

## Checked against a published platform

| platform | Q | f0 | t_min |
| --- | --- | --- | --- |
| osmium microdisc (Paul trap proposal) | — | 10 Hz | 963.2 days |
| a published torsion-balance experiment | — | 0.6 mHz | 482.3 (1.32 years) |

The published torsion-balance experiment [Y25] collected three months of data and reports that its system "could not reach the steady state during our observing run," needing on the order of 300 or more days to resolve its expected feature. This repository's bound, computed from its stated `Q` and resonance frequency alone — with no reference to its own reported run time, and with none of [Helou2017]'s signal-strength or confidence-level inputs — gives 482.3 days. The two agree to the right order of magnitude. This is this repository's only external check on the realistic-conditions result, and it is one data point, not a calibrated fit (see `LIMITS.md` item 8).

## What this means for the field

Any proposal for a spectroscopic test of a record-conditioned self-gravity signal — under this law, under the measurement-conditioned alternative, or under any future proposal with the same qualitative shape — inherits a bound of this kind. Raising mechanical quality factor to sharpen the signal is not free; [Helou2017] already shows this quantitatively for a specific proposal, and this repository's simpler, law-independent floor shows it holds across the whole family.
