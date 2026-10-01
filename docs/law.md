# The law

GENERATED from `docs-src/docs/law.md`; every number below is read from `results/check.json` and `results/realistic.json`. See [`src/rcg/law.py`](../src/rcg/law.py) for the implementation these numbers check.

## In three sentences

A quantum system's gravitational source is not its full superposition, and not what an observer has measured of it, but its state **conditioned on whatever physical records of its position exist**, wherever they are, read or not. With no record, the source is the ordinary quantum-mechanical mean; with a perfect record, it is the localized branch alone. Two closed-form rules interpolate between those endpoints in the overlap `eta` that a record would leave between two branches of a superposition:

```
rule (i):    f(eta) = eta
rule (ii):   f(eta) = 1 - sqrt(1 - eta^2)
```

`f(eta)` is the weight the law places on the branch a given description does *not* occupy, normalized to its no-record value. Both rules satisfy `f(0) = 0` and `f(1) = 1` and are continuous and monotonic; nothing is fitted.

## How much record exists

For two branches, the overlap `eta` is exactly `sqrt(2 Tr rho^2 - 1)`, where `rho` is the system's reduced state — basis-independent, and defined for any state, not only a two-branch one. That handle is what lets the law be applied to a real, continuously decohering oscillator (`rcg.models.gaussian`): the overlap is read off the unconditioned state's purity, and the source is built from the state conditioned on every record that exists, which for a Gaussian system is the filtering solution at unit efficiency on every channel.

## What decides between the two rules

Both rules pass every test in [`tests.md`](tests.md) equally, including no signalling — see `CLAIMS.md` claim 6. The one test that separates them is whether `f` is multiplicative under composition of independent records: `f(eta1) f(eta2) = f(eta1 eta2)`. Rule (i) is exact to 0; rule (ii) misses by up to 0.07163. See [`LIMITS.md`](../LIMITS.md) item 1 for what this criterion does and does not rest on.

## f(eta) versus a measured pull

`f(eta)` is the law's own weight, exactly. A *measured* drift between two branches in a model where each branch's wavepacket is free to spread is `f(eta)` times the no-record drift to within a few per cent — at `eta=0.5`, the measured ratio is 0.4800 for rule (i) against `f(0.5) = 0.5000`, and 0.1262 for rule (ii) against `f(0.5) = 0.1340`. The gap is the own-branch term's contribution once the packet has spread; a paper using this law should say which of the two — the law's weight, or a model's reading of it — it is quoting.
