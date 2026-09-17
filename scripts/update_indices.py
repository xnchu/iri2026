#!/usr/bin/env python3
"""
Download the two IRI indices files (ig_rz.dat, apf107.dat) into src/iri2026/data/.

irimodel.org rejects the default urllib/curl user agent with HTTP 406, so a browser
User-Agent is sent. If irimodel.org fails, the ECHAIM mirror is used.

Part of iri2026 (IRI-2026 update by Xiangning Chu, LASP, University of Colorado Boulder),
derived from iri2020 by Michael Hirsch / space-physics.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

FILES = ["ig_rz.dat", "apf107.dat"]
SOURCES = [
    "https://irimodel.org/indices/",
    "https://chain-new.chain-project.net/echaim_downloads/",
]
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) iri2026-update-indices"

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "src" / "iri2026" / "data"


def fetch(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def download(name: str, outdir: Path, timeout: float = 60.0) -> Path:
    errors = []
    for base in SOURCES:
        url = base + name
        try:
            data = fetch(url, timeout)
        except Exception as e:  # noqa: B902
            errors.append(f"{url}: {e}")
            continue
        if len(data) < 1000:
            errors.append(f"{url}: suspiciously small ({len(data)} bytes)")
            continue
        out = outdir / name
        out.write_bytes(data)
        print(f"{name}: {len(data)} bytes from {url}")
        return out
    raise ConnectionError(f"could not download {name}:\n  " + "\n  ".join(errors))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("-o", "--outdir", type=Path, default=DEFAULT_DIR, help="data directory")
    a = p.parse_args()

    if not a.outdir.is_dir():
        sys.exit(f"{a.outdir} is not a directory")

    for name in FILES:
        download(name, a.outdir)


if __name__ == "__main__":
    main()
