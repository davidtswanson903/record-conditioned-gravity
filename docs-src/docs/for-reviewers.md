# A guided path for reviewers

GENERATED from `docs-src/docs/for-reviewers.md`. A path through this repository that a careful reviewer can finish in an afternoon.

## 1. Read the law (about 10 minutes)

Read [`law.md`](law.md) and [`src/rcg/law.py`](../src/rcg/law.py) side by side. The law is ~100 lines including its own derivation comments; `f_rule_i` and `f_rule_ii` are each one line. Check for yourself that `f(0)=0`, `f(1)=1`, and that nothing in the file depends on anything outside it.

## 2. Run the tests (about 5 minutes)

```
pip install -e ".[dev]"
make test
```

This runs every unit test, both equivalence tests (every number this repository produces, checked against the two original experiments' frozen outputs — see `tests/fixtures/legacy/`), and the explicit control tests in `tests/test_controls.py`, in under a minute. Read `tests/test_controls.py` directly; each test is named for the control it checks and is a handful of lines.

## 3. Open the three key figures

- `build/figures/check-2-no-signalling.png` — this law's prediction flat under a distant party's choice of measurement basis, against a rival law that visibly signals.
- `build/figures/realistic-2-resolvability.png` — the feasibility map: where resolvability exceeds one (red contour), against where the three real platforms actually sit (white stars).
- `build/figures/realistic-3-spectra.png` — what a detector would actually see: this law's prediction, the measurement-conditioned rival's, and standard quantum mechanics', effectively coincident at every platform tried.

(Regenerate with `make figures`, after `make check` and `make realistic`.)

## 4. Read the limits

[`LIMITS.md`](../LIMITS.md) — nine items, each naming exactly what is not established and why.

## 5. Where to push hardest

**The rule's selection.** [`LIMITS.md`](../LIMITS.md) item 1 and [`law.md`](law.md) state plainly that composing records multiplicatively is a criterion, not a theorem. If you doubt that criterion, both rules remain live candidates, and everywhere this repository reports a single number for "the law" it should be read as rule (i)'s, with rule (ii)'s available in the same results files for comparison.

**The adapter's extrapolation.** [`LIMITS.md`](../LIMITS.md) item 3 and `rcg.models.gaussian`'s module docstring state the one place this repository's reduction from two branches to a continuous oscillator goes beyond what the law itself states. `realistic.md`'s stage 4 is this repository's own attempt to stress-test that extrapolation with an independent reading; judge for yourself whether it is sufficient.

## 6. The claims table

[`CLAIMS.md`](../CLAIMS.md) is generated from `src/rcg/claims.py` and lists every claim this repository makes, each with the script and output key that produces it and a status (confirmed / imported / cited / open). If a summary written about this repository states something not traceable to a row in that table, treat the summary as wrong.
