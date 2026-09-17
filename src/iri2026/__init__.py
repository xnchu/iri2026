"""
iri2026: IRI-2026 International Reference Ionosphere from Python.

Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space Physics (LASP),
University of Colorado Boulder. Derived from iri2020 by Michael Hirsch / space-physics
(https://github.com/space-physics/iri2020, MIT). IRI model: D. Bilitza and the COSPAR/URSI
IRI Working Group, https://irimodel.org.
"""

from .base import IRI
from .vprofile import timeprofile, geoprofile

__all__ = ["IRI", "timeprofile", "geoprofile"]
