"""`make docs`: renders docs-src/{root,docs}/*.md with the macros read from
results/*.json, and regenerates CLAIMS.md from src/rcg/claims.py.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rcg import emit  # noqa: E402


def main():
    check, realistic = emit.load_results()
    m = emit.macros(check, realistic)
    written = emit.render_all_docs(m)
    for w in written:
        print(f"wrote {w}")
    claims_path = emit.write_claims_md()
    print(f"wrote {claims_path}")


if __name__ == "__main__":
    main()
