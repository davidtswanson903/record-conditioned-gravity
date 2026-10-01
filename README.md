# record-conditioned-gravity

GENERATED from `docs-src/root/README.md`; its numbers come only from `results/`. Run `make docs` after `make check` and `make realistic` to regenerate it.

A sourcing law for gravity's coupling to quantum matter, checked by exact simulation, and tested against what a real laboratory could see.

## 1. The law

Gravity couples not to a quantum system's full superposition, and not to what an observer has measured, but to the system's state **conditioned on whatever physical records of its position exist** — written or not, read or not, however they came to exist. With no record at all, the source is the ordinary quantum mean. With a perfect record, it is the localized state alone. Two closed-form rules interpolate between those endpoints, in the overlap `eta` of the records two branches of the wavefunction would leave behind.

## 2. The predictions

- **Gravity without entanglement.** Two masses held in superposition, with no record of either one, develop **zero** entanglement under this law's mean-field treatment — unlike a quantized two-body coupling, which reaches 0.5274 concurrence in the same test. (Mean-field, not a full master equation — see [`LIMITS.md`](LIMITS.md) item 4.)
- **No added noise, and no signalling.** The law is a function of a system's own reduced state alone, so it cannot be used to send a signal: an operation on a record at the other end of a measurement changes nothing, to 2.220e-16.
- **No self-gravity shift above the motional ground state.** For any oscillator with thermal occupation above one half — essentially every oscillator built today — the law's weight on the unconditioned state is exactly zero, so its resonance sits at the ordinary mechanical frequency with no shift at all.

## 3. The results

**"Confirmed" below means the code matches what the law predicts — an internal-consistency check of an exact simulation against a stated hypothesis, not an experimental confirmation of the hypothesis. [`CLAIMS.md`](CLAIMS.md) says this at its head; §3's last point is the one place this repository asks what a real experiment could actually see.**

- **The law, confirmed in exact simulation, with controls.** Nine tests (T1–T9) all pass; see [`docs/tests.md`](docs/tests.md) and [`CLAIMS.md`](CLAIMS.md).
- **The testing limit, and why it is specific to this law.** The same records that shrink a thermal oscillator's record-conditioned signal also broaden the spectral feature that would carry it, through the same rate: "resolvability" (that feature's offset divided by its own width) reaches only 1.374e-4 on a representative platform, where it would need to reach one — a shape failure, not a size one. See [`docs/realistic.md`](docs/realistic.md).
- **A field-wide minimum observation time**, independent of this law: any spectroscopic test of a conditioned second resonance needs at least `pi * Q / omega_0`, checked against a published torsion-balance experiment's own reported run time. See [`docs/minimum-time.md`](docs/minimum-time.md).

## 4. What is not established

The rule's selection between its two closed forms rests on one criterion (composition), not on a deeper principle; the self-gravity frequency is imported from the literature; the two-body result is mean-field, not a full master equation; classical force noise is not modelled. See [`LIMITS.md`](LIMITS.md) for the complete list.

## 5. Reproduce

```
pip install -e ".[dev]"
make all
```

`make test` runs in under a minute; `make all` (every experiment, every figure, every document) runs in under an hour on a laptop. `make all` leaves `results/*.json` (every number), `build/figures/*.pdf` (every figure), `build/latex/` (every number and table in `\input`-able form), and regenerates every file this README links to.

## 6. Origin

This package rebuilds, as a standalone, reproducible repository, results first obtained as a computational experiment on a separate, unpublished theory of relational quantum gravity. See [`PROVENANCE.md`](PROVENANCE.md) for where the law came from and what, if anything, a reader needs to take on trust from that source. Nothing in this repository requires that theory to be read, checked, or believed: every claim here is checked against the law as stated in [`src/rcg/law.py`](src/rcg/law.py), by exact simulation, in this repository alone.
