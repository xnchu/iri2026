"""
Rerun a 3-case subset of scripts/compare_iri2020.py against the reference iri2020 package
with the same thresholds as docs/comparison_iri2020.md. Skipped when iri2020 is not importable.

iri2026: IRI-2026 update by Xiangning Chu (LASP); derived from iri2020 by M. Hirsch.
"""

from __future__ import annotations

import importlib.util

import numpy as np
import pytest

import iri2026

iri2020 = pytest.importorskip("iri2020") if importlib.util.find_spec("iri2020") else None

CASES = [
    ("2012-01-15T12", 65.1, -147.5),
    ("2003-07-15T00", 40.0, -105.3),
    ("2016-10-15T18", -76.8, 166.7),
]
ALTKM = [100.0, 1000.0, 20.0]

# variable: (median threshold %, p95 threshold %), as in docs/comparison_iri2020.md
THRESHOLDS = {
    "NmF2": (1.0, 5.0),
    "foF2": (1.0, 5.0),
    "hmF2": (1.0, 5.0),
    "NmE": (1.0, 5.0),
    "hmE": (1.0, 5.0),
    "ne": (2.0, 30.0),  # altitudes <= 600 km; p95 relaxed from 10 % (see docs)
    "TEC": (3.0, 15.0),  # p95 relaxed from 10 % (see docs)
    "Tn": (1.0, None),
}


def reldiff(ref: np.ndarray, new: np.ndarray) -> np.ndarray:
    ref = np.asarray(ref, float)
    new = np.asarray(new, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.abs(new - ref) / np.abs(ref) * 100.0
    d[~np.isfinite(d) | (ref <= 0)] = np.nan
    return d[np.isfinite(d)]


@pytest.mark.skipif(iri2020 is None, reason="reference iri2020 package not importable")
def test_compare_subset():
    diffs: dict[str, list[np.ndarray]] = {k: [] for k in THRESHOLDS}
    for time, glat, glon in CASES:
        ref = iri2020.IRI(time, ALTKM, glat, glon)
        new = iri2026.IRI(time, ALTKM, glat, glon)
        for var in THRESHOLDS:
            r = ref[var]
            n = new[var]
            if var == "ne":
                r = r.sel(alt_km=slice(None, 600))
                n = n.sel(alt_km=slice(None, 600))
            diffs[var].append(reldiff(r.values, n.values).ravel())

    for var, (tmed, tp95) in THRESHOLDS.items():
        d = np.concatenate(diffs[var])
        med = np.median(d)
        p95 = np.percentile(d, 95)
        assert med < tmed, f"{var}: median relative difference {med:.3g} % >= {tmed} %"
        if tp95 is not None:
            assert p95 < tp95, f"{var}: 95th percentile relative difference {p95:.3g} % >= {tp95} %"
