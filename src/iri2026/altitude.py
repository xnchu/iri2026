"""
iri2026: IRI-2026 International Reference Ionosphere from Python.

Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space Physics (LASP),
University of Colorado Boulder. Derived from iri2020 by Michael Hirsch / space-physics
(https://github.com/space-physics/iri2020, MIT). IRI model: D. Bilitza and the COSPAR/URSI
IRI Working Group, https://irimodel.org.
"""

from __future__ import annotations
from .base import IRI

from argparse import ArgumentParser


def main(time: str, alt_km: list[float], glat: float, glon: float):
    """Height Profile Example"""

    return IRI(time, alt_km, glat, glon)


def cli():
    p = ArgumentParser(description="IRI altitude profile")
    p.add_argument("time", help="time of simulation")
    p.add_argument("latlon", help="geodetic latitude, longitude (degrees)", type=float, nargs=2)
    p.add_argument(
        "-alt_km",
        help="altitude START STOP STEP (km)",
        type=float,
        nargs=3,
        default=(80, 1000, 10),
    )
    P = p.parse_args()

    iono = main(P.time, P.alt_km, *P.latlon)

    try:
        from matplotlib.pyplot import show
        import iri2026.plots as piri

        piri.altprofile(iono)
        show()
    except ImportError:
        pass


if __name__ == "__main__":
    cli()
