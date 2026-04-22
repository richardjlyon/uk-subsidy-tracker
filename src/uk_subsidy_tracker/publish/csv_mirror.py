"""Faithful CSV mirror for every derived Parquet (Plan 04-04, D-10).

Journalists open these in Excel; Python / R users read with their native
CSV parsers. Pinned pandas args prevent cross-platform line-ending drift
(Pitfall 4) and preserve full float precision (journalists may need to
reproduce published figures to the last decimal).

Pinned arguments (RESEARCH Pattern 4):

- `index=False` — journalists don't want the row number.
- `encoding="utf-8"` — no BOM (Excel 2016+ handles bare UTF-8 fine).
- `lineterminator="\n"` — LF on every platform, including Windows.
- `date_format="%Y-%m-%dT%H:%M:%S"` — ISO-8601 without sub-seconds.
- `float_format=None` — full pandas default precision; no truncation.
- `na_rep=""` — empty cell for NaN (Excel-friendly).

Column order = Parquet column order = Pydantic field declaration order
(D-10 one source of truth).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # noqa: F401 — re-exported transitively via pyarrow.to_pandas
import pyarrow.parquet as pq


def write_csv_mirror(parquet_path: Path, csv_path: Path) -> None:
    """Faithful CSV mirror of one Parquet file (D-10)."""
    df = pq.read_table(parquet_path).to_pandas()
    df.to_csv(
        csv_path,
        index=False,                       # D-10: no row number
        encoding="utf-8",                  # no BOM; Excel 2016+ handles bare UTF-8
        lineterminator="\n",               # LF even on Windows (Pitfall 4)
        date_format="%Y-%m-%dT%H:%M:%S",   # ISO-8601 no sub-seconds
        float_format=None,                 # full pandas-default precision
        na_rep="",                         # empty cell for NaN
    )


def build(derived_dir: Path) -> list[Path]:
    """Iterate derived_dir, write a .csv next to every .parquet.

    Returns the sorted list of CSV paths written (deterministic order).
    """
    derived_dir = Path(derived_dir)
    written: list[Path] = []
    for parquet_path in sorted(derived_dir.glob("*.parquet")):
        csv_path = parquet_path.with_suffix(".csv")
        write_csv_mirror(parquet_path, csv_path)
        written.append(csv_path)
    return written


__all__ = ["write_csv_mirror", "build"]
