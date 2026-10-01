"""Shared fixtures: run each experiment once per test session (each takes well
under a minute) and hand every test the same results dict, rather than re-running
the physics in every test function.

experiments/check/run.py and experiments/realistic/run.py are both literally
named run.py, so they are loaded by file path with distinct module names here
rather than via `sys.path` + `import run`, which would alias one to the other.
"""
import pathlib
import sys
from importlib.machinery import SourceFileLoader

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "realistic"))   # stage0_adapter etc.


def _load(name, path):
    return SourceFileLoader(name, str(path)).load_module()


@pytest.fixture(scope="session")
def check_results():
    mod = _load("rcg_check_run", ROOT / "experiments" / "check" / "run.py")
    return mod.main()


@pytest.fixture(scope="session")
def realistic_results():
    import stage0_adapter
    import stage1_platforms
    import stage2_virtual
    import stage3_map
    import stage4_robust

    return dict(
        stage0_adapter=stage0_adapter.run(),
        stage1_platforms=stage1_platforms.run(),
        stage2_virtual=stage2_virtual.run(),
        stage3_map=stage3_map.run(),
        stage4_robust=stage4_robust.run(),
    )


@pytest.fixture(scope="session")
def legacy():
    import json

    out = {}
    for name in ("out-rs-numbers", "out-rr-numbers", "out-rr-map", "out-rr-robust"):
        with open(ROOT / "tests" / "fixtures" / "legacy" / f"{name}.json") as fh:
            out[name] = json.load(fh)
    return out
