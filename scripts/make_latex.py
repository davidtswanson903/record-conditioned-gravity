"""`make latex`: writes build/latex/numbers.tex, build/latex/tables/*.tex and
build/latex/refs.bib, reading only from results/*.json and data/references.yaml.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rcg import emit  # noqa: E402


def main():
    check, realistic = emit.load_results()
    m = emit.macros(check, realistic)
    p1 = emit.write_numbers_tex(m)
    tables = emit.write_tables_tex(check, realistic)
    p2 = emit.write_refs_bib()
    print(f"wrote {p1}")
    for t in tables:
        print(f"wrote {t}")
    print(f"wrote {p2}")


if __name__ == "__main__":
    main()
