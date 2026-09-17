"""
iri2026 tests (IRI-2026 update by Xiangning Chu, LASP; derived from iri2020 tests by M. Hirsch).

Expected values come from iri2026 runs on 2026-09-16/17 with gfortran 12.5 after the
comparison with iri2020 (docs/comparison_iri2020.md) showed agreement of the peak parameters.
"""

import math
import subprocess

import pytest
from pytest import approx

import iri2026


def test_altitude_profile():
    """same case as iri2020's test; NmF2, hmF2, foF2 agree with iri2020 to < 0.01 %,
    ne at 200 km differs from iri2020 (2.4408e10) because of the IRI-2026 bottomside changes"""
    time = "2015-12-13T10"
    altkmrange = (100, 1000, 10.0)
    glat = 65.1
    glon = -147.5

    iri = iri2026.IRI(time, altkmrange, glat, glon)

    # .item() necessary for stability across OS, pytest versions, etc.
    assert iri["ne"][10].item() == approx(21691295700.0, rel=0.001)
    assert iri.NmF2.item() == approx(77149519900.0, rel=0.001)
    assert iri.hmF2.item() == approx(265.248932, rel=0.001)
    assert iri.foF2.item() == approx(2.49434066, rel=0.001)
    assert iri.TEC.item() == approx(2.09175945e16, rel=0.001)
    assert iri.EsProb.item() == approx(0.115254752, rel=0.001)
    # IBP bubble model not applicable at 65 N -> NaN
    assert math.isnan(iri.BubbleProb.item())


def test_equatorial_probabilities():
    """new IRI-2026 outputs: sporadic-E and plasma bubble occurrence probabilities"""
    iri = iri2026.IRI("2010-03-21T20", (100, 1000, 50.0), 0.0, -60.0)

    es = iri.EsProb.item()
    assert 0.0 <= es <= 1.0
    # 20 UT at 60 W is 16 LT: bubble model (18-06 LT) not applicable -> NaN or in [0, 1]
    bp = iri.BubbleProb.item()
    assert math.isnan(bp) or 0.0 <= bp <= 1.0

    # 02 UT at 60 W is 22 LT: bubble model applies
    iri = iri2026.IRI("2010-03-21T02", (100, 1000, 50.0), 0.0, -60.0)
    bp = iri.BubbleProb.item()
    assert 0.0 <= bp <= 1.0
    assert bp == approx(0.315841824, rel=0.001)
    assert 0.0 <= iri.EsProb.item() <= 1.0


def test_date_beyond_indices():
    """a date beyond the ig_rz.dat range must fail loudly (error stop in irifun.for)"""
    with pytest.raises((subprocess.CalledProcessError, RuntimeError)):
        iri2026.IRI("2035-01-01T00", (100, 1000, 50.0), 0.0, -60.0)
