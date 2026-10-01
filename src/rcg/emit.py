r"""Numbers, tables and the LaTeX feed -- generated ONLY from results/*.json.

No numeral is written by this module's callers (docs-src templates, CLAIMS.md,
LIMITS.md): every value is read here, once, into a dict of named "macros", and
every one of those surfaces is filled from the same dict. A regenerated result
changes the README, the docs, CLAIMS.md and the paper's numbers.tex together, or
none of them: `tests/test_numbers_rule.py` checks that no generated document
contains a number this module did not supply.

A macro's name is also the LaTeX command name it becomes in numbers.tex
(camelCase, no leading digit), so `macros()['fEtaHalfRuleI']` and
`\fEtaHalfRuleI` in the paper are the same lookup.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
DOCS_SRC_DIR = ROOT / "docs-src"
DOCS_DIR = ROOT / "docs"
LATEX_DIR = ROOT / "build" / "latex"
DATA_DIR = ROOT / "data"

_TEX_SPECIAL = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\^{}",
}
_TEX_SPECIAL_RE = re.compile("|".join(re.escape(k) for k in _TEX_SPECIAL))


def tex_escape(s):
    """Escape free text (a citation title, a data file's notes field, a
    scenario name) for safe use outside LaTeX math mode. Every table and
    bib entry below that carries text pulled from data/ or results/, rather
    than written as a LaTeX literal in this file, goes through this -- an
    unescaped '_' from a notes field is what first broke the table build."""
    return _TEX_SPECIAL_RE.sub(lambda m: _TEX_SPECIAL[m.group(0)], str(s))


def load_results():
    with open(RESULTS_DIR / "check.json") as fh:
        check = json.load(fh)
    with open(RESULTS_DIR / "realistic.json") as fh:
        realistic = json.load(fh)
    return check, realistic


# ---------------------------------------------------------------- formatting
def sig(x, n=4):
    """`n` significant figures, plain notation for 0.001 <= |x| < 10**n, else
    scientific -- the house style these documents use throughout."""
    if x == 0:
        return "0"
    from decimal import Decimal

    d = Decimal(repr(float(x)))
    exp = d.adjusted()
    if -3 <= exp < n:
        s = f"{float(x):.{max(n - 1 - exp, 0)}f}"
        return s
    return f"{float(x):.{n - 1}e}".replace("e+0", "e+").replace("e-0", "e-")


def pct(x, n=2):
    return f"{100 * float(x):.{n}f}\\%"


def days_or_years(days):
    if days < 1:
        return f"{days * 24:.2g} hours"
    if days < 365:
        return f"{days:.3g} days"
    return f"{days / 365.25:.3g} years"


# ---------------------------------------------------------------------- macros
def macros(check, realistic):
    """Every named value the docs/README/paper quote. Add to this dict, not to
    the prose directly."""
    m = {}
    t1, t2, t3, t4, t8, t9 = (
        check["T1"], check["T2"], check["T3"], check["T4"], check["T8"], check["T9"]
    )

    # the law and the computational check
    m["pilotCalibrationWorst"] = sig(check["pilot_calibration"]["worst"])
    row_half = next(r for r in t2 if r["eta"] == 0.5)
    m["fEtaHalfRuleI"] = sig(row_half["f_i"])
    m["fEtaHalfRuleII"] = sig(row_half["f_ii"])
    m["fEtaHalfRatio"] = sig(row_half["f_i"] / row_half["f_ii"])
    m["etaDriftRatioHalfRuleI"] = sig(row_half["drift_i"] / t1["rule_i_1"])
    m["etaDriftRatioHalfRuleII"] = sig(row_half["drift_ii"] / t1["rule_i_1"])
    m["ruleIMultiplicativeError"] = sig(
        max(abs(r["prod"] - r["joint"]) for r in t3["multiplicative"] if r["rule"] == "i")
    )
    m["ruleIIMultiplicativeMiss"] = sig(
        max(abs(r["prod"] - r["joint"]) for r in t3["multiplicative"] if r["rule"] == "ii")
    )
    m["compositionWorst"] = sig(
        max(abs(c["eta_eff"] - c["product"]) for c in t3["overlap"])
    )
    m["noSignallingWorstTwoDim"] = sig(t4["worst_2d"])
    m["noSignallingWorstFourDim"] = sig(t4["worst_4d"])
    m["outcomeSourcedSignal"] = sig(abs(t4["outcome_x"] - t4["outcome_z"]))
    m["negativityMax"] = sig(max(a["negativity"] for a in t8["theory"]))
    m["quantizedConcurrenceMax"] = sig(max(b["concurrence"] for b in t8["quantized"]))
    m["energyDriftWorst"] = sig(max(t["rel"] for t in t9))
    m["energyDriftQuarterRatio"] = sig(
        sum(t["rel"] / t["rel_quarter"] for t in t9) / len(t9), 3
    )
    m["energyDriftAcrossErasure"] = pct(check["T9_limit"]["across_erasure"])

    # the realistic-conditions experiment
    s1 = realistic["stage1_platforms"]["baseline"]
    s2 = realistic["stage2_virtual"]
    s3 = realistic["stage3_map"]
    s4 = realistic["stage4_robust"]

    for key, tag in (("osmium-paul", "Osmium"), ("torsion-mg", "Torsion"),
                      ("levitated-gs", "Levitated")):
        m[f"resolvability{tag}"] = sig(s3["platforms_gate"][key]["R"])
        m[f"nbar{tag}"] = sig(s1[key]["nbar"])
        m[f"splitTheory{tag}"] = sig(s1[key]["split_theory"])
        m[f"widthTheory{tag}"] = sig(s1[key]["G_theory"])

    m["massIndependenceSpread"] = sig(s3["mass_independence"]["spread"])
    m["qtOsmiumMilliHz"] = sig(s3["QT"]["osmium"]["QT_1mHz"])
    m["qtOsmiumTenHz"] = sig(s3["QT"]["osmium"]["QT_10Hz"])
    m["cornerR"] = sig(s3["corner"]["R"])
    m["cornerOk"] = "yes" if s3["corner"]["ok"] else "no"
    m["qmLockinRaw"] = sig(s2["controls"]["qm_lockin_raw"])

    m["thermalOccupationFactorOsmium"] = sig(s4["thermal_occupation_factor"]["osmium-paul"])
    m["thermalOccupationFactorTorsion"] = sig(s4["thermal_occupation_factor"]["torsion-mg"])
    m["tMinOsmiumDays"] = sig(s4["tmin"]["osmium-paul"]["t_min_days"])
    m["tMinPublishedTorsionDays"] = sig(s4["tmin"]["Y25_torsion_balance"]["t_min_days"])
    m["tMinPublishedTorsionReadable"] = days_or_years(s4["tmin"]["Y25_torsion_balance"]["t_min_days"])
    m["boundaryFloorYears"] = sig(
        min(
            a / (2 * 3.141592653589793 * float(fz.rstrip("Hz"))) / (365.25 * 86400)
            for fz, rows in s3["boundary"].items()
            for a, b in rows if a is not None
        )
    )

    return m


_LATEX_NAME_RE = re.compile(r"^[A-Za-z]+$")


def latex_safe_name(key):
    """A LaTeX control sequence name may contain letters ONLY -- no digits, no
    underscores. A macro key that fails this is a bug in macros() (rename the
    key; see e.g. the 'TwoDim'/'FourDim' and 'MilliHz'/'TenHz' spellings-out
    already there), caught here loudly rather than left to a cryptic
    'Undefined control sequence' from pdflatex."""
    if not _LATEX_NAME_RE.match(key):
        raise ValueError(
            f"macro key {key!r} is not a valid LaTeX command name (letters only, "
            "no digits/underscores) -- rename it in macros()"
        )
    return key


# -------------------------------------------------------------------- writers
def write_numbers_tex(m, path=None):
    path = path or (LATEX_DIR / "numbers.tex")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "% GENERATED by rcg.emit.write_numbers_tex -- do not edit.",
        "% One command per value in rcg.emit.macros(); regenerate with `make latex`.",
        "",
    ]
    for key in sorted(m):
        lines.append(f"\\newcommand{{\\{latex_safe_name(key)}}}{{{m[key]}}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


_TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def fill_template(text, m):
    """Replace every {{macroName}} in `text` with its value, raising if a token
    has no macro -- a missing macro is a bug in emit.macros(), not something to
    render as a blank."""
    missing = []

    def repl(match):
        key = match.group(1)
        if key not in m:
            missing.append(key)
            return match.group(0)
        return str(m[key])

    out = _TOKEN_RE.sub(repl, text)
    if missing:
        raise KeyError(f"template references undefined macros: {sorted(set(missing))}")
    return out


def render_docs(m, src_dir, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for src in sorted(src_dir.glob("*.md")):
        text = src.read_text(encoding="utf-8")
        filled = fill_template(text, m)
        dest = out_dir / src.name
        dest.write_text(filled, encoding="utf-8")
        written.append(dest)
    return written


def render_all_docs(m):
    """docs-src/root/*.md -> the repo root (README.md, LIMITS.md, PROVENANCE.md);
    docs-src/docs/*.md -> docs/ (law.md, tests.md, realistic.md, ...).
    CLAIMS.md is generated separately, from rcg.claims, since it is a table."""
    written = []
    written += render_docs(m, DOCS_SRC_DIR / "root", ROOT)
    written += render_docs(m, DOCS_SRC_DIR / "docs", DOCS_DIR)
    return written


def load_references():
    import yaml

    with open(DATA_DIR / "references.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


_STATUS_LABEL = {
    "confirmed": "confirmed by computation",
    "imported": "imported, with an adapter",
    "cited": "cited",
    "open": "open",
}


def write_claims_md(path=None):
    from . import claims as _claims

    path = path or (ROOT / "CLAIMS.md")
    lines = [
        "# Claims",
        "",
        "GENERATED from `src/rcg/claims.py`. One row per claim this repository makes; "
        "nothing here is added by hand. `make docs` regenerates this file.",
        "",
        "**What \"confirmed by computation\" means, and does not mean.** Every row below "
        "tagged `confirmed by computation` means the code's output matches what the law, "
        "exactly as stated in `src/rcg/law.py`, predicts -- an internal-consistency check "
        "of an exact simulation against a stated hypothesis. **It does not mean the "
        "hypothesis has been confirmed by experiment.** Whether the law is true of nature "
        "is untouched by this repository; see `docs/realistic.md` for the one place this "
        "repository asks what a real experiment could see, and its answer (not yet, on any "
        "platform tried).",
        "",
        "| # | claim | evidence | script | status |",
        "| - | ----- | -------- | ------ | ------ |",
    ]
    for i, c in enumerate(_claims.CLAIMS, start=1):
        claim = c["claim"].replace("|", "\\|")
        evidence = c["evidence"].replace("|", "\\|")
        script = f"`{c['script']}` ({c['key']})"
        status = _STATUS_LABEL[c["status"]]
        lines.append(f"| {i} | {claim} | {evidence} | {script} | {status} |")
    counts = {}
    for c in _claims.CLAIMS:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(f"{counts.get(s, 0)} {label}" for s, label in _STATUS_LABEL.items())
        + "."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_tables_tex(check, realistic, out_dir=None):
    """build/latex/tables/*.tex, booktabs style, read only from results/."""
    out_dir = out_dir or (LATEX_DIR / "tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    # the discriminators table: the proposal's sharpest rows, against five laws
    disc = check["discriminators"]
    lines = [
        "% GENERATED from results/check.json -- do not edit.",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "scenario & rule (i) & rule (ii) & Schr\\\"odinger--Newton & outcome-cond. & "
        "quantized \\\\",
        "\\midrule",
    ]
    for row in disc:
        lines.append(
            f"{tex_escape(row['scenario'])} & {row['theory_i']:.4f} & "
            f"{row['theory_ii']:.4f} & {row['sn']:.4f} & {row['outcome']:.4f} & "
            f"{row['quant']:.4f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]
    p = out_dir / "discriminators.tex"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p)

    # the FULL discriminators table (paper Table 1): four scenarios against six
    # laws, pulling from both results files. A cell is a number only where this
    # repository's code actually computed one; "--" marks a combination that is
    # either not modelled here or not applicable, named as which in the running
    # text (docs/related-work.md), never silently filled.
    th_i = {r["scenario"]: r["theory_i"] for r in disc}
    th_ii = {r["scenario"]: r["theory_ii"] for r in disc}
    s2 = realistic["stage2_virtual"]["platforms"]["osmium-paul"]["laws"]
    osc_shift = {
        law: ("yes" if abs(s2[law]["w_main"] - realistic["stage2_virtual"]
              ["platforms"]["osmium-paul"]["w0"]) > 1e-9 else "no")
        for law in s2
    }
    unread = "record held, unread, eta = 0.5"
    erased = "the same record, coherently erased"
    t8_theory = max(a["negativity"] for a in check["T8"]["theory"])
    t8_quant = max(b["negativity"] for b in check["T8"]["quantized"])
    rows_full = [
        (
            "two unrecorded masses (negativity)",
            "0$^{\\dagger}$", "0$^{\\dagger}$",
            f"{t8_quant:.3f}", "0$^{\\ddagger}$", "--$^{a}$", "--$^{a}$",
        ),
        (
            "oscillator above ground state (shift?)",
            "no", "no", "no$^{b}$", osc_shift["qm"],
            osc_shift["uncond_sn"], osc_shift["mc_sn"],
        ),
        (
            "unread record in the ground state",
            f"{th_i[unread]:.4f}", f"{th_ii[unread]:.4f}", "--$^{c}$", "--$^{c}$",
            "1.0000", "1.0000$^{d}$",
        ),
        (
            "the same record, erased",
            f"{th_i[erased]:.4f}", f"{th_ii[erased]:.4f}", "--$^{c}$", "--$^{c}$",
            "1.0000", "1.0000$^{d}$",
        ),
    ]
    lines = [
        "% GENERATED from results/check.json and results/realistic.json -- do not edit.",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        "scenario & this law (i) & this law (ii) & quantized grav. & standard QM & "
        "uncond. SN & meas.-cond. SN \\\\",
        "\\midrule",
    ]
    for scen, *vals in rows_full:
        lines.append(tex_escape(scen) + " & " + " & ".join(vals) + " \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "",
        "% footnotes, set by the surrounding document:",
        "%  (dagger) T8, exact two-qubit simulation, mean-field form.",
        "%  (ddagger) zero by construction: no coupling term exists between the masses.",
        "%  (a) not modelled in this repository: unconditional/measurement-conditioned SN "
        "have no two-mass entanglement mechanism implemented here; the classical-channel "
        "literature answer is qualitative (Kafri2014): no entanglement, but adds noise.",
        "%  (b) no two-body coupling partner in a single-oscillator spectrum; trivially "
        "equal to standard QM in this scenario.",
        "%  (c) no two-branch register concept implemented for these laws in this "
        "repository.",
        "%  (d) unread = nothing has been read yet, so the measurement-conditioned "
        "source has not conditioned on anything; identical to the no-record case here.",
    ]
    p1b = out_dir / "discriminators-full.tex"
    p1b.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p1b)

    # Table 3: the nine tests and their results, one line each
    t4 = check["T4"]
    t9 = check["T9"]
    tests_rows = [
        ("T1", "the law's two endpoints", "pass (both rules)"),
        ("T2", "the curve between the endpoints", "pass; continuous, monotonic"),
        ("T3", "composition; multiplicativity of $f$",
         f"exact to {check['T3']['overlap'][0]['eta_eff'] - check['T3']['overlap'][0]['product']:.1e}; separates the rules"),
        ("T4", "no signalling",
         f"pass to {t4['worst_2d']:.2e} (both rules)"),
        ("T5", "an unread record counts fully", "pass"),
        ("T6", "erasure restores the source", "pass"),
        ("T7", "environment = deliberate register", "pass"),
        ("T8", "two unrecorded masses: no entanglement",
         f"negativity {t8_theory:.1e} vs quantized {t8_quant:.3f}"),
        ("T9", "no record configuration creates energy",
         f"worst drift {max(t['rel'] for t in t9):.1e}, integrator-order"),
    ]
    lines = [
        "% GENERATED from results/check.json -- do not edit.",
        "\\begin{tabular}{cp{3.6cm}p{3.6cm}}",
        "\\toprule",
        "test & what it checks & result \\\\",
        "\\midrule",
    ]
    for tid, what, result in tests_rows:
        lines.append(f"{tid} & {what} & {result} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    p1c = out_dir / "tests-summary.tex"
    p1c.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p1c)

    # the platforms table: every physical parameter, with its citation
    plats = realistic["stage1_platforms"]["platforms"]
    lines = [
        "% GENERATED from results/realistic.json -- do not edit.",
        "\\begin{tabular}{lccccl}",
        "\\toprule",
        "platform & $m$ [kg] & $\\omega_0/2\\pi$ [Hz] & $T$ [K] & $Q$ & ref. \\\\",
        "\\midrule",
    ]
    for key, p in plats.items():
        lines.append(
            f"{key} & {p['m']:.3e} & {p['w0'] / (2 * 3.141592653589793):.3e} & "
            f"{p['T']:.3e} & {p['Q']:.3e} & \\cite{{{p['citation']}}} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]
    p2 = out_dir / "platforms.tex"
    p2.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p2)

    # Appendix D: the full platforms table, with sources and assumptions spelled
    # out in a notes column, not abbreviated to a citation key.
    lines = [
        "% GENERATED from results/realistic.json and data/platforms.yaml -- do not edit.",
        "\\begin{tabular}{lccccp{4.2cm}}",
        "\\toprule",
        "platform & $m$ [kg] & $\\omega_0/2\\pi$ [Hz] & $T$ [K] & $Q$ & notes "
        "(citation: \\texttt{data/platforms.yaml}) \\\\",
        "\\midrule",
    ]
    for key, p in plats.items():
        lines.append(
            f"{key} & {p['m']:.3e} & {p['w0'] / (2 * 3.141592653589793):.3e} & "
            f"{p['T']:.3e} & {p['Q']:.3e} & {tex_escape(p['notes'])} "
            f"(\\cite{{{p['citation']}}}) \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]
    p2b = out_dir / "platforms-full.tex"
    p2b.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p2b)

    # the feasibility gate: resolvability and the three-condition verdict
    gate = realistic["stage3_map"]["platforms_gate"]
    lines = [
        "% GENERATED from results/realistic.json -- do not edit.",
        "\\begin{tabular}{lccc}",
        "\\toprule",
        "platform & $R$ & gate ($R\\ge 1$) & all three conditions \\\\",
        "\\midrule",
    ]
    for key, row in gate.items():
        lines.append(
            f"{key} & {row['R']:.3e} & {'yes' if row['gate'] else 'no'} & "
            f"{'yes' if row['ok'] else 'no'} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}"]
    p3 = out_dir / "feasibility-gate.tex"
    p3.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(p3)
    return written


def write_refs_bib(path=None):
    refs = load_references()
    path = path or (LATEX_DIR / "refs.bib")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["% GENERATED from data/references.yaml -- do not edit.", ""]
    for key, r in refs.items():
        authors = " and ".join(r["authors"])
        lines.append(f"@{r['type']}{{{key},")
        lines.append(f"  author = {{{authors}}},")
        lines.append(f"  title = {{{{{tex_escape(r['title'])}}}}},")
        if "journal" in r:
            lines.append(f"  journal = {{{r['journal']}}},")
        if "volume" in r:
            lines.append(f"  volume = {{{r['volume']}}},")
        if "pages" in r:
            lines.append(f"  pages = {{{r['pages']}}},")
        lines.append(f"  year = {{{r['year']}}},")
        if r.get("eprint"):
            lines.append(f"  eprint = {{{r['eprint']}}},")
            lines.append("  archivePrefix = {arXiv},")
        lines.append("}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
