"""The numbers rule: every scientific-notation or percentage value appearing in a
generated document must be traceable to `rcg.emit.macros()`, i.e. to results/.

This does not catch every possible hand-typed numeral (a plain decimal like
"0.5" written directly in prose would slip past it) -- that limitation is
stated here rather than hidden. What it does catch is exactly the
category this house style always uses for a computed value (see `rcg.emit.sig`
and `rcg.emit.pct`'s docstrings): scientific notation and decimal percentages.
Those appearing in a generated document that do NOT match a current macro value
are either stale (the doc was not regenerated after the results changed) or
hand-typed, and either way this test should fail.
"""
import pathlib
import re

import pytest

from rcg import emit

ROOT = pathlib.Path(__file__).resolve().parents[1]

_SCI_RE = re.compile(r"-?\d[\d,]*\.?\d*e[+-]\d+")
_PCT_RE = re.compile(r"-?\d+\.\d+\\?%")

GENERATED_DOCS = [
    ROOT / "README.md",
    ROOT / "LIMITS.md",
    ROOT / "PROVENANCE.md",
    *sorted((ROOT / "docs").glob("*.md")),
]


@pytest.fixture(scope="module")
def macro_values(check_results, realistic_results):
    m = emit.macros(check_results, realistic_results)
    return set(m.values())


@pytest.mark.parametrize("doc", GENERATED_DOCS, ids=lambda p: p.name)
def test_scientific_and_percentage_numbers_trace_to_a_macro(doc, macro_values):
    if not doc.exists():
        pytest.skip(f"{doc} not yet generated -- run `make docs` first")
    text = doc.read_text(encoding="utf-8")
    found = _SCI_RE.findall(text) + _PCT_RE.findall(text)
    untraceable = [tok for tok in found if tok not in macro_values]
    assert not untraceable, (
        f"{doc.name} contains values not found among the current macros() output "
        f"(stale doc, or a hand-typed number): {untraceable}"
    )


def test_every_macro_is_used_somewhere(macro_values):
    """A macro nobody reads is dead weight; this is a prompt to either use it or
    remove it, not a hard requirement, so it only warns via a soft assertion
    message rather than failing the whole suite on one unused macro."""
    import rcg.emit as _emit

    text = "\n".join(
        p.read_text(encoding="utf-8") for p in GENERATED_DOCS if p.exists()
    )
    unused = [v for v in macro_values if str(v) not in text]
    # informational: do not fail the build over this, just surface it
    if unused:
        print(f"\n(info) {len(unused)} macro value(s) not found in any generated doc: "
              f"{unused[:10]}")
