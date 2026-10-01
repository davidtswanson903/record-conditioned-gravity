"""Runs stages 0-4 of the realistic-conditions experiment in order, and writes
results/realistic.json. The prose that interprets these numbers lives in
docs-src/realistic.md.njk and docs-src/minimum-time.md.njk, filled in by
`make docs`; this script's job is only the arithmetic.
"""
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import stage0_adapter       # noqa: E402
import stage1_platforms     # noqa: E402
import stage2_virtual       # noqa: E402
import stage3_map           # noqa: E402
import stage4_robust        # noqa: E402

RESULTS_DIR = ROOT / "results"


def main():
    out = {}
    for name, mod in (
        ("stage0_adapter", stage0_adapter),
        ("stage1_platforms", stage1_platforms),
        ("stage2_virtual", stage2_virtual),
        ("stage3_map", stage3_map),
        ("stage4_robust", stage4_robust),
    ):
        t0 = time.time()
        out[name] = mod.run()
        print(f"{name:20s} {time.time() - t0:6.1f}s")

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "realistic.json", "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(f"\nwritten to {RESULTS_DIR / 'realistic.json'}")


if __name__ == "__main__":
    main()
