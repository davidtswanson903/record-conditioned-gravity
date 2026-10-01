# The computational check

GENERATED from `docs-src/docs/tests.md`; every number is read from `results/check.json`. Source: `experiments/check/run.py`, built on `rcg.models.branches`, `rcg.models.two_mass` and `rcg.records` — exact simulation throughout (split-step Fourier propagation or linear algebra on at most a few hundred dimensions), no sampling and no fitting. Reproduce with `make check`.

Nine tests, T1–T9, plus the three controls that prove the code can tell the laws it compares apart.

| test | what it checks | result |
| --- | --- | --- |
| T1 | the law's two endpoints (no record / a perfect record) | both pass for both rules |
| T2 | the curve between the endpoints is continuous, monotonic, and the two rules are well separated | passes; at `eta=0.5` the rules differ by a factor of ~3.8 |
| T3 | composition: two records compose to the product of their overlaps; multiplicativity of `f` | composition exact to 5.551e-17; multiplicativity separates the two rules (see `law.md`) |
| T4 | no signalling, under random unitaries on 2- and 4-dimensional registers | passes to 2.220e-16 / 2.220e-16, for BOTH rules |
| T5 | an unread record counts the same as a read one | passes |
| T6 | a coherently erased record restores the unconditioned source | passes |
| T7 | ordinary decoherence (a generic environment) is indistinguishable from a deliberate register | passes |
| T8 | two unrecorded masses develop no entanglement under the law | negativity below 1.000e-10 (zero to the arithmetic), against a quantized coupling's 0.5274 concurrence in the same code |
| T9 | no record configuration creates energy | worst drift 2.980e-4, falling by 4.03x when the time step is quartered (first order, the integrator's own) |

**The controls**, which prove the code can represent a difference when the law predicts there should be one, rather than only ever reporting agreement: unconditional Schrödinger–Newton is flat in `eta` (a required negative control); a quantized two-body coupling generates entanglement where the law's mean-field form does not (T8's own control); and a law sourced by the measured *outcome* rather than by existing records signals by 0.3402 where this law signals by zero (T4's control).

## What T4 actually shows

T4 passes for **both** rules equally. No signalling is a property of the law's *shape* — a function of the system's reduced state alone — not of which interpolation rule is chosen. A proposal that treats no signalling as the criterion that selects between the two rules is making a claim this test does not support; see `LIMITS.md` item 1 and `law.md` for what does.

## T9's one necessary correction

The first energy functional tried for T9 — summing each branch's potential energy against the *other* branch's density directly — double-counts the self-interaction and reports a spurious 1–12% drift. The correct, Hamiltonian-generating functional is

```
E = T_A + T_B + (alpha/2)(<n_A K n_A> + <n_B K n_B>) + beta <n_A K n_B>
```

with `alpha, beta` read off the law's own two coefficients (`rcg.models.branches.Branches.weights`). With this functional the drift falls to 2.980e-4, which is integrator error, not physics. Across a *change* of record (rather than within one held fixed) the energy changes by 52.41\% — not a failure, since changing the record changes the Hamiltonian itself; testing whether the *identity* this reflects is honored needs the full mass-plus-register system, which this model does not carry (see `LIMITS.md`).
