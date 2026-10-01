# Provenance

Where the law in [`src/rcg/law.py`](src/rcg/law.py) came from, and what a reader does and does not need to take on trust from that source.

## What this repository is

This package was extracted from a computational research program on an unpublished, independent theory of relational quantum gravity, developed outside this repository. That theory derives the sourcing law this repository implements — the claim that gravity couples to a quantum system's state conditioned on the physical records that exist of its position — from a larger axiomatic framework not reproduced here.

**This repository does not ask a reader to accept that framework.** The law is stated here in full, in ordinary quantum-mechanical language (density matrices, reduced states, decoherence), with no vocabulary or notation specific to its origin. Every claim this repository makes is checked against that stated law, by exact simulation, in this repository alone — not against the originating theory's further claims, and not by appeal to its authority.

## What is, and is not, inherited

**Inherited:** the law's two closed forms (`rcg.law.f_rule_i`, `rcg.law.f_rule_ii`) and the physical picture — conditioning on existing records rather than on measurement outcomes or on nothing — that motivates them. These are the starting point this repository takes as given and then checks.

**Not inherited, and not needed:** the originating theory's broader claims (about gravity's origin, about cosmology, or about anything outside this one sourcing law), its internal vocabulary, or its own derivation of the law from more basic postulates. A reader who doubts or rejects that larger theory can still read this repository's law as a standalone hypothesis — stated plainly in §1 of [`README.md`](README.md) — and judge this repository's results on their own terms.

**One check is explicitly a port check, not an independent confirmation, and is named as such.** [`CLAIMS.md`](CLAIMS.md)'s `pilot_calibration` row regenerates the originating theory's own stored numbers from its own model, to confirm this *rebuild* implements the same law its source did — before anything else in this repository is built on top of it. That check cannot be independently verified by a reader without access to the (unpublished) source repository, and this repository does not ask a reader to take its result on faith for anything beyond that one purpose: every other claim in `CLAIMS.md` is checked against the law as this repository states it, with no further appeal to the source.

## What to cite

If this repository's law or results are used, cite this repository (`CITATION.cff`). The originating theory is unpublished and is not a citable source; none of this repository's claims depend on it being one.
