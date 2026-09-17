# IRI-2026 data files

All files in this directory are read by the Fortran code with the data directory
as the current working directory (`base.py` runs `iri2026_driver` with `cwd=data`).
Download date for everything below: **2026-09-16**.

| Group | Files | Fortran unit / reader | Source |
|---|---|---|---|
| CCIR foF2/M(3000)F2 coefficients | `ccir11.asc` .. `ccir22.asc` (month + 10) | unit 10, `irisub.for` | `https://irimodel.org/IRI-2026/IRI-2026.tar` |
| URSI foF2 coefficients | `ursi11.asc` .. `ursi22.asc` (month + 10) | unit 10, `irisub.for` | IRI-2026.tar |
| Shubin (2015) COSMIC hmF2 model | `mcsat11.dat` .. `mcsat22.dat` (month + 10) | unit 15, `irifun.for` `read_data_SD` | IRI-2026.tar |
| IGRF-14 definitive coefficients | `dgrf1945.dat` .. `dgrf2020.dat` (5-year steps) | unit 14, `igrf.for` `GETSHC` | IRI-2026.tar |
| IGRF-14 provisional and secular variation | `igrf2025.dat`, `igrf2025s.dat` | unit 14, `igrf.for` | IRI-2026.tar |
| IBP-2023 plasma bubble model (new in IRI-2026) | `ibp_emp_coeffs.dat` | unit 16, `irifun.for` `IBPLOD` | IRI-2026.tar |
| Solar/ionospheric indices Rz12, IG12 | `ig_rz.dat` | unit 12, `irifun.for` `read_ig_rz` | `https://irimodel.org/indices/ig_rz.dat` |
| Magnetic indices and F10.7 | `apf107.dat` | unit 13, `irifun.for` `readapf107` | `https://irimodel.org/indices/apf107.dat` |

The `igrf2015*.dat` and `igrf2020*.dat` files shipped with iri2020 are no longer
listed in the `FILMOD` table of `igrf.for` and were removed. `dgrf2020.dat` replaces
`igrf2020.dat`.

## Indices files

`ig_rz.dat` and `apf107.dat` are updated by the IRI team roughly monthly. The
copies here were downloaded 2026-09-16: `ig_rz.dat` header says it was updated
8/19/2025 and covers 1958-11 through 2028-11 (predicted beyond the present);
`apf107.dat` ends on 2026-07-28. A date outside the `ig_rz.dat` range makes the
driver fail with `ERROR STOP IG_RZ.DAT out of date index range`.

To refresh them run, from the repository root:

```sh
python scripts/update_indices.py
```

The script sends a browser `User-Agent` header (irimodel.org answers HTTP 406 to
the default `curl`/`urllib` agent) and falls back to the daily-updated ECHAIM
mirror `https://chain-new.chain-project.net/echaim_downloads/` if irimodel.org
is unreachable. Format description:
<https://irimodel.org/indices/IRI-Format-indices-files.pdf>.
