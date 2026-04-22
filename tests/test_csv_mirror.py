"""CSV-mirror pandas-args discipline (Plan 04-04, D-10).

Seven checks:

1. `test_csv_mirror_written_for_every_parquet` — after build(), every .parquet
   under derived dir has a sibling .csv.
2. `test_csv_column_order_matches_parquet` — CSV header == pq.read_table
   column_names (D-10 column-order source of truth).
3. `test_csv_line_endings_are_lf` — bytes contain `\\n`, never `\\r\\n`
   (Pitfall 4: Windows CRLF).
4. `test_csv_no_bom` — first bytes != UTF-8 BOM `\\xef\\xbb\\xbf`.
5. `test_csv_no_index_column` — no leading unnamed column (D-10).
6. `test_csv_dates_iso8601` — date columns in ISO-8601 format.
7. `test_csv_floats_preserve_precision` — known high-precision values survive
   round-trip without truncation.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.schemes import cfd


@pytest.fixture(scope="module")
def mirror_dir(tmp_path_factory) -> Path:
    """Rebuild derived + write CSV mirrors once per module."""
    from uk_subsidy_tracker.publish import csv_mirror

    out = tmp_path_factory.mktemp("csv-mirror")
    cfd.rebuild_derived(output_dir=out)
    csv_mirror.build(out)
    return out


# ---------------------------------------------------------------------------
# 1. Every Parquet has a sibling CSV
# ---------------------------------------------------------------------------

def test_csv_mirror_written_for_every_parquet(mirror_dir):
    parquets = sorted(mirror_dir.glob("*.parquet"))
    assert parquets, "no parquet files under mirror_dir"
    for p in parquets:
        csv_path = p.with_suffix(".csv")
        assert csv_path.exists(), f"missing CSV mirror for {p.name}"
        assert csv_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# 2. Column order matches Parquet
# ---------------------------------------------------------------------------

def test_csv_column_order_matches_parquet(mirror_dir):
    """D-10: CSV column order = Parquet column order (which = Pydantic field order)."""
    for p in sorted(mirror_dir.glob("*.parquet")):
        parquet_cols = pq.read_table(p).column_names
        csv_path = p.with_suffix(".csv")
        with csv_path.open(newline="") as f:
            reader = csv.reader(f)
            csv_header = next(reader)
        assert csv_header == parquet_cols, (
            f"{p.name}: CSV header {csv_header} disagrees with Parquet cols {parquet_cols}"
        )


# ---------------------------------------------------------------------------
# 3. Line endings are LF (Pitfall 4)
# ---------------------------------------------------------------------------

def test_csv_line_endings_are_lf(mirror_dir):
    """Pinned lineterminator='\\n' means CRLF must not appear in any mirror."""
    for p in sorted(mirror_dir.glob("*.parquet")):
        csv_path = p.with_suffix(".csv")
        raw = csv_path.read_bytes()
        assert b"\r\n" not in raw, (
            f"{csv_path.name}: CRLF found — Windows line endings leaked in"
        )
        assert b"\n" in raw, f"{csv_path.name}: no LF at all; file malformed"


# ---------------------------------------------------------------------------
# 4. No UTF-8 BOM
# ---------------------------------------------------------------------------

def test_csv_no_bom(mirror_dir):
    """encoding='utf-8' (not utf-8-sig) — Excel 2016+ handles BOM-less UTF-8 fine."""
    for p in sorted(mirror_dir.glob("*.parquet")):
        csv_path = p.with_suffix(".csv")
        first = csv_path.read_bytes()[:3]
        assert first != b"\xef\xbb\xbf", (
            f"{csv_path.name}: UTF-8 BOM present — journalists' Unix pipelines "
            "will treat it as the first cell of the first field"
        )


# ---------------------------------------------------------------------------
# 5. No leading unnamed index column (D-10)
# ---------------------------------------------------------------------------

def test_csv_no_index_column(mirror_dir):
    """index=False — no leading unnamed column ('' or 'Unnamed: 0')."""
    for p in sorted(mirror_dir.glob("*.parquet")):
        csv_path = p.with_suffix(".csv")
        with csv_path.open(newline="") as f:
            reader = csv.reader(f)
            csv_header = next(reader)
        # First header cell must be the first Pydantic field (not empty / 'Unnamed').
        first = csv_header[0]
        assert first.strip() != "", f"{csv_path.name}: leading empty header cell"
        assert not first.startswith("Unnamed"), (
            f"{csv_path.name}: pandas index leaked as 'Unnamed: 0'"
        )


# ---------------------------------------------------------------------------
# 6. ISO-8601 dates
# ---------------------------------------------------------------------------

def test_csv_dates_iso8601(mirror_dir):
    """Dates are 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' (ISO-8601).

    station_month carries month_end (a `date` type). Regex check on the first
    data row's month_end column.
    """
    csv_path = mirror_dir / "station_month.csv"
    assert csv_path.exists(), "station_month.csv missing — regen fixture"
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        row = next(reader)
    month_end = row["month_end"]
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$")
    assert iso_pattern.match(month_end), (
        f"month_end={month_end!r} is not ISO-8601 format"
    )


# ---------------------------------------------------------------------------
# 7. Float precision preserved (float_format=None)
# ---------------------------------------------------------------------------

def test_csv_floats_preserve_precision(mirror_dir):
    """float_format=None — pandas default repr preserves enough digits for round-trip.

    Read a float column from Parquet and from CSV; assert the CSV value has
    >=6 significant digits or matches the Parquet value to ~7 decimal places.
    """
    import math

    parquet_path = mirror_dir / "station_month.parquet"
    csv_path = mirror_dir / "station_month.csv"
    assert parquet_path.exists() and csv_path.exists()

    # Find the first row with a non-zero cfd_generation_mwh (float column).
    table = pq.read_table(parquet_path)
    gen_series = table.column("cfd_generation_mwh").to_pylist()
    target_idx = next(
        (i for i, v in enumerate(gen_series)
         if v is not None and v != 0 and not math.isclose(v, round(v))),
        None,
    )
    assert target_idx is not None, (
        "no non-integer float values in cfd_generation_mwh — test fixture too clean"
    )
    parquet_value = gen_series[target_idx]

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    csv_value = float(rows[target_idx]["cfd_generation_mwh"])

    # Assert the round-trip is close to machine-epsilon precision.
    assert math.isclose(csv_value, parquet_value, rel_tol=1e-9), (
        f"float precision lost at row {target_idx}: "
        f"parquet={parquet_value!r} csv={csv_value!r}"
    )
