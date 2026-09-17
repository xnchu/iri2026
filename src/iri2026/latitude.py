"""
iri2026: IRI-2026 International Reference Ionosphere from Python.

Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space Physics (LASP),
University of Colorado Boulder. Derived from iri2020 by Michael Hirsch / space-physics
(https://github.com/space-physics/iri2020, MIT). IRI model: D. Bilitza and the COSPAR/URSI
IRI Working Group, https://irimodel.org.
"""

from __future__ import annotations
from .vprofile import geoprofile

from pathlib import Path
from argparse import ArgumentParser


def main(time: str, alt_km: float, glat: list[float], glon: float, outfn: Path | None = None):
    """latitude Profile Example"""

    iono = geoprofile(latrange=glat, glon=glon, altkm=alt_km, time=time)

    if outfn:
        outfn = Path(outfn).expanduser()
        print("writing", outfn)
        iono.to_netcdf(outfn)

    return iono


def cli():
    p = ArgumentParser(description="IRI latitude profile")
    p.add_argument("time", help="time of simulation")
    p.add_argument("glon", help="geodetic  longitude (degrees)", type=float)
    p.add_argument(
        "-glat",
        help="geodetic latitude START STOP STEP (degrees)",
        type=float,
        nargs=3,
        default=(-60, 60, 2.0),
    )
    p.add_argument("-alt_km", help="altitude (km)", type=float, default=300.0)
    p.add_argument("-o", "--outfn", help="write data to file")
    P = p.parse_args()

    iono = main(P.time, P.alt_km, P.glat, P.glon, P.outfn)

    try:
        from matplotlib.pyplot import show
        from .plots import latprofile as plot_lat

        plot_lat(iono)
        show()
    except ImportError as e:
        raise SystemExit(f"Skipped plotting tests {e}")


if __name__ == "__main__":
    cli()
