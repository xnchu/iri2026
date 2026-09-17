"""
iri2026: IRI-2026 International Reference Ionosphere from Python.

Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space Physics (LASP),
University of Colorado Boulder. Derived from iri2020 by Michael Hirsch / space-physics
(https://github.com/space-physics/iri2020, MIT). IRI model: D. Bilitza and the COSPAR/URSI
IRI Working Group, https://irimodel.org.
"""

import importlib.resources as impr
import shutil
import subprocess
import os
import sys


def build():
    exe = shutil.which("cmake")
    if not exe:
        raise FileNotFoundError("CMake not available")

    with impr.as_file(impr.files(__package__).joinpath("CMakeLists.txt")) as f:
        s = f.parent
        b = s / "build"
        g = []
        if sys.platform == "win32" and not os.environ.get("CMAKE_GENERATOR"):
            g = ["-G", "MinGW Makefiles"]
        subprocess.check_call([exe, f"-S{s}", f"-B{b}"] + g)
        subprocess.check_call([exe, "--build", str(b), "--parallel"])
