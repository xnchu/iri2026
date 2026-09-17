"""
iri2026: IRI-2026 International Reference Ionosphere from Python.

Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space Physics (LASP),
University of Colorado Boulder. Derived from iri2020 by Michael Hirsch / space-physics
(https://github.com/space-physics/iri2020, MIT). IRI model: D. Bilitza and the COSPAR/URSI
IRI Working Group, https://irimodel.org.
"""

from __future__ import annotations
import subprocess
import logging
from dateutil.parser import parse
from datetime import datetime
import xarray
import io
import os
import numpy as np
import importlib.resources as impr

from .build import build

SIMOUT = ["ne", "Tn", "Ti", "Te", "nO+", "nH+", "nHe+", "nO2+", "nNO+", "nCI", "nN+"]

__all__ = ["IRI"]


def IRI(time: str | datetime, altkmrange: list[float], glat: float, glon: float) -> xarray.Dataset:
    if isinstance(time, str):
        time = parse(time)

    assert len(altkmrange) == 3, "altitude (km) min, max, step"
    assert isinstance(glat, (int, float)) and isinstance(
        glon, (int, float)
    ), "glat, glon is scalar"
    # %% build IRI executable if needed
    iri_name = "iri2026_driver"
    if os.name == "nt":
        iri_name += ".exe"

    # %% run IRI
    with (
        impr.as_file(impr.files(__package__).joinpath(iri_name)) as exe,
        impr.as_file(impr.files(__package__).joinpath("data")) as data_path,
    ):

        if not exe.is_file():
            build()

        cmd = [
            str(exe),
            str(time.year),
            str(time.month),
            str(time.day),
            str(time.hour),
            str(time.minute),
            str(time.second),
            str(glat),
            str(glon),
            str(altkmrange[0]),
            str(altkmrange[1]),
            str(altkmrange[2]),
        ]

        logging.info(" ".join(cmd))
        ret = subprocess.check_output(cmd, text=True, cwd=data_path)

    logging.debug(ret)
    if not ret:
        raise RuntimeError("IRI failed to run correctly--gave empty text output")
    # %% get altitude profile data
    Nalt = int((altkmrange[1] - altkmrange[0]) // altkmrange[2]) + 1

    arr = np.genfromtxt(io.StringIO(ret), max_rows=Nalt)
    arr = np.atleast_2d(arr)

    assert arr.ndim == 2 and arr.shape[1] == 12, f"bad text data output format, shape {arr.shape}"

    dsf = {k: (("alt_km"), v) for (k, v) in zip(SIMOUT, arr[:, 1:].T)}
    altkm = arr[:, 0]
    # %% get parameter data
    arr = np.genfromtxt(io.StringIO(ret), skip_header=Nalt)
    assert arr.ndim == 1 and arr.size == 100, "bad text data output format"
    # %% assemble output
    # OARR indices below are 0-based (Fortran OARR(n) -> arr[n-1]); see the OARR
    # table at the top of IRI_SUB in src/irisub.for (IRI-2026).
    iono = xarray.Dataset(
        dsf,
        coords={"time": [time], "alt_km": altkm, "glat": glat, "glon": glon},
        attrs={"f107": arr[40], "ap": arr[51]},  # OARR(41) F10.7 daily, OARR(52) daily ap
    )

    # OARR(1:6)
    for i, p in enumerate(["NmF2", "hmF2", "NmF1", "hmF1", "NmE", "hmE"]):
        iono[p] = (("time"), [arr[i]])

    iono["TEC"] = (("time"), [arr[36]])  # OARR(37), filled by IRITEC in the driver
    iono["EqVertIonDrift"] = (("time"), [arr[43]])  # OARR(44) m/s
    iono["foF2"] = (("time"), [arr[99]])  # OARR(100), local patch in irisub.for
    # new in IRI-2026: occurrence probabilities in [0, 1]; the Fortran code returns
    # -1 when the model is not applicable (e.g. bubbles: daytime or |glat| > 45),
    # which is reported as NaN here.
    iono["EsProb"] = (("time"), [_prob(arr[90])])  # OARR(91) sporadic-E probability
    iono["BubbleProb"] = (("time"), [_prob(arr[91])])  # OARR(92) IBP-2023 bubble probability

    return iono


def _prob(x: float) -> float:
    """occurrence probability in [0, 1]; negative means not computed -> NaN"""
    return float(x) if x >= 0 else float("nan")
