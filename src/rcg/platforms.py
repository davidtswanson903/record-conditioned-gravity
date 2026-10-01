"""Loads data/platforms.yaml into Platform objects, with every derived rate
(gamma, D_env, wsn2) computed from the cited inputs and nothing else.

PRECEDENCE, where a platform's entry could state a quantity two ways: an
explicit mass (`mass_u` or `mass_kg`) always wins over a diameter-derived one.
A platform may give both an explicit mass (the cited value) and a diameter (for
the radius gas drag needs); the two need not be bit-identical, since the
published mass and the published diameter, read through the material's
density, typically agree only to each number's own printed precision. Only
when no explicit mass is given does the diameter also supply the mass, via the
sphere formula. (This repository's build caught a case where this went the
other way silently, so it is stated here rather than left implicit in the
code below.)
"""
import pathlib
from dataclasses import dataclass, field

import numpy as np
import yaml

from . import constants as K
from . import law as _law
from .models import gaussian as G

_HERE = pathlib.Path(__file__).resolve()
DATA_DIR = _HERE.parents[2] / "data"


@dataclass(frozen=True)
class Material:
    name: str
    atomic_mass_u: float
    density_kg_m3: float
    sigma_m: float
    dwsn_times_w0: float
    citation: str


@dataclass(frozen=True)
class Platform:
    key: str
    label: str
    citation: str
    material: Material
    m: float
    radius_m: float
    w0: float
    T: float
    gam: float
    D_env: float
    wsn2: float
    notes: str
    extra: dict = field(default_factory=dict, repr=False)

    @property
    def Q(self):
        return self.w0 / self.gam


def _read_yaml(path=None):
    path = pathlib.Path(path) if path else (DATA_DIR / "platforms.yaml")
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _sphere(density_kg_m3, diameter_m):
    r = diameter_m / 2.0
    m = density_kg_m3 * 4.0 / 3.0 * np.pi * r ** 3
    return float(m), float(r)


def load_materials(data=None):
    data = data if data is not None else _read_yaml()
    out = {}
    for name, d in data["materials"].items():
        out[name] = Material(
            name=name,
            atomic_mass_u=d["atomic_mass_u"],
            density_kg_m3=d["density_kg_m3"],
            sigma_m=d["sigma_m"],
            dwsn_times_w0=d["dwsn_times_w0"],
            citation=d["citation"],
        )
    return out


def omega_sn_sq(material):
    return _law.omega_sn_sq_from_shift(material.dwsn_times_w0)


def load_platforms(path=None):
    data = _read_yaml(path)
    materials = load_materials(data)
    out = {}
    for key, d in data["platforms"].items():
        mat = materials[d["material"]]
        # explicit mass always wins: a platform can give BOTH an explicit mass
        # (the cited value) and a diameter (for the radius gas drag needs), and
        # the two need not be bit-identical (the published mass and the published
        # diameter, read through the material's density, agree only to the
        # printed precision of each). Only when no explicit mass is given does
        # the diameter also supply the mass, via the sphere formula.
        if "mass_kg" in d:
            m = d["mass_kg"]
        elif "mass_u" in d:
            m = d["mass_u"] * K.AMU
        else:
            m = None
        if "diameter_m" in d:
            density = d.get("density_kg_m3", mat.density_kg_m3)
            sphere_m, r = _sphere(density, d["diameter_m"])
            if m is None:
                m = sphere_m
        else:
            r = d.get("radius_m", float("nan"))
        if m is None:
            raise ValueError(f"platform {key!r}: no mass given (mass_kg/mass_u/diameter_m)")

        w0 = d["w0_rad_s"]
        if "nbar" in d:
            # invert the Bose factor rather than the high-temperature form: at
            # nbar ~ 0.4 the two differ by a factor of a few, and this is the one
            # platform where it decides whether f is zero or not.
            T = float(K.HBAR * w0 / (K.KB * np.log(1.0 + 1.0 / d["nbar"])))
        else:
            T = d["temperature_K"]

        if "Q" in d:
            gam = w0 / d["Q"]
        else:
            gam = G.gamma_gas(m, r, d["pressure_pa"], T, gas_amu=d.get("gas_amu", 4.0))

        D_env = G.D_thermal(m, gam, w0, T)
        if "heating_nbar_dot" in d:
            D_env += G.D_heating(m, w0, d["heating_nbar_dot"])

        out[key] = Platform(
            key=key,
            label=d["label"],
            citation=d["citation"],
            material=mat,
            m=m,
            radius_m=r,
            w0=w0,
            T=T,
            gam=gam,
            D_env=D_env,
            wsn2=omega_sn_sq(mat),
            notes=d.get("notes", ""),
            extra=d,
        )
    return out


MATERIALS = load_materials()
PLATFORMS = load_platforms()
