"""Mocked-network tests for ``data/ofgem_aggregate.py`` (Phase 05.2 Plans 01–02).

No live network; every test patches ``requests.get``. Pattern mirrors
``tests/data/test_ofgem_ro.py`` which mirrors ``tests/test_ons_gas_download.py``.

Tests (expanded in Plan 02 to cover real XLSX parsing + determinism):
  1.  test_imports_succeed                            — public API surface intact
  2.  test_download_twelve_year_xlsx_fail_loud        — D-17 bare raise on net failure
  3.  test_download_twelve_year_xlsx_writes_xlsx      — happy-path returns path + writes bytes
  3b. test_download_twelve_year_xlsx_output_path_bound_before_try — D-17 gap #2
  4.  test_load_annual_aggregate_csv_skips_comments   — `#` Provenance: header lines skipped
  5.  test_load_roc_prices_csv_validates_schema       — pandera validation on load
  6.  test_xlsx_to_monthly_determinism               — 12-yr XLSX → parse_xlsx_to_monthly() D-21
  7–12. test_annual_xlsx_determinism[SY18..SY23]     — per-year openpyxl CSV-emission D-21 (6 tests)
"""
from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests


# ---------------------------------------------------------------------------
# 1. Public API surface (import smoke test)
# ---------------------------------------------------------------------------
def test_imports_succeed():
    """All four public functions + module constants importable."""
    from uk_subsidy_tracker.data.ofgem_aggregate import (
        XLSX_FILENAME,
        XLSX_URL,
        download_twelve_year_xlsx,
        load_annual_aggregate_csv,
        load_roc_prices_csv,
        ofgem_annual_aggregate_schema,
        ofgem_monthly_schema,
        ofgem_roc_prices_schema,
        parse_xlsx_to_monthly,
    )

    assert callable(download_twelve_year_xlsx)
    assert callable(parse_xlsx_to_monthly)
    assert callable(load_annual_aggregate_csv)
    assert callable(load_roc_prices_csv)
    assert "rocs_report_2006_to_2018_20250410081520.xlsx" in XLSX_URL
    assert XLSX_FILENAME == "rocs_report_2006_to_2018_20250410081520.xlsx"
    assert ofgem_annual_aggregate_schema is not None
    assert ofgem_roc_prices_schema is not None
    assert ofgem_monthly_schema is not None


# ---------------------------------------------------------------------------
# 2. download_twelve_year_xlsx — D-17 fail-loud on network failure
# ---------------------------------------------------------------------------
def test_download_twelve_year_xlsx_fail_loud(tmp_path, monkeypatch):
    """Network failure must propagate as RequestException (D-17 fail-loud)."""
    from uk_subsidy_tracker.data import ofgem_aggregate

    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with patch(
        "uk_subsidy_tracker.data.ofgem_aggregate.requests.get",
        side_effect=requests.exceptions.ConnectionError("boom"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            ofgem_aggregate.download_twelve_year_xlsx()


# ---------------------------------------------------------------------------
# 3. download_twelve_year_xlsx — happy path writes bytes + returns path
# ---------------------------------------------------------------------------
def test_download_twelve_year_xlsx_writes_xlsx(tmp_path, monkeypatch):
    """Happy-path returns DATA_DIR/raw/ofgem/<XLSX_FILENAME>; file contains the streamed bytes."""
    from uk_subsidy_tracker.data import ofgem_aggregate

    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
    mock_response.raise_for_status.return_value = None

    with patch(
        "uk_subsidy_tracker.data.ofgem_aggregate.requests.get",
        return_value=mock_response,
    ) as mock_get:
        path = ofgem_aggregate.download_twelve_year_xlsx()

    assert path == tmp_path / "raw" / "ofgem" / ofgem_aggregate.XLSX_FILENAME
    assert path.exists()
    assert path.read_bytes() == b"xlsx-bytes-stub"
    # Phase 4 D-17 timeout discipline.
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs.get("timeout") == 60


# ---------------------------------------------------------------------------
# 3b. Source-grep guard: output_path bound BEFORE try (D-17 gap #2 fix)
# ---------------------------------------------------------------------------
def test_download_twelve_year_xlsx_output_path_bound_before_try():
    """Source-grep guard: `output_path =` must appear BEFORE `try:` block."""
    from uk_subsidy_tracker.data import ofgem_aggregate

    src = inspect.getsource(ofgem_aggregate.download_twelve_year_xlsx)
    assert "output_path" in src
    assert "try:" in src
    output_idx = src.index("output_path")
    try_idx = src.index("try:")
    assert output_idx < try_idx, (
        f"output_path must be bound BEFORE try: block "
        f"(output at {output_idx}, try at {try_idx})"
    )


# ---------------------------------------------------------------------------
# 4. load_annual_aggregate_csv — Provenance comment lines skipped + schema validates
# ---------------------------------------------------------------------------
def test_load_annual_aggregate_csv_skips_comments(tmp_path, monkeypatch):
    """A `# Provenance:` header block is skipped; the remaining rows pass schema validation."""
    from uk_subsidy_tracker.data import ofgem_aggregate

    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", tmp_path)
    csv_dir = tmp_path / "raw" / "ofgem"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "ro-annual-aggregate.csv"
    csv_path.write_text(
        "# Provenance:\n"
        "# - SY17 https://www.ofgem.gov.uk/example/sy17.pdf sha256=abc retrieved_on=2026-04-24\n"
        "scheme_year,year,country,technology,generation_gwh,rocs_issued,ro_cost_gbp_nominal,source_pdf_url\n"
        "SY17,2017,GB,Onshore Wind,12345.6,18000000.0,2300000000.0,https://www.ofgem.gov.uk/example/sy17.pdf\n",
        encoding="utf-8",
    )
    df = ofgem_aggregate.load_annual_aggregate_csv()
    assert len(df) == 1
    assert df.iloc[0]["scheme_year"] == "SY17"
    assert df.iloc[0]["country"] == "GB"


# ---------------------------------------------------------------------------
# 5. load_roc_prices_csv — schema validation on load
# ---------------------------------------------------------------------------
def test_load_roc_prices_csv_validates_schema(tmp_path, monkeypatch):
    """A header-comment-prefixed CSV with valid roc_prices rows loads + validates."""
    from uk_subsidy_tracker.data import ofgem_aggregate

    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", tmp_path)
    csv_dir = tmp_path / "raw" / "ofgem"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "roc-prices.csv"
    csv_path.write_text(
        "# Provenance:\n"
        "# - https://www.ofgem.gov.uk/example/buyout.pdf retrieved_on=2026-04-24\n"
        "obligation_year,buyout_gbp_per_roc,recycle_gbp_per_roc,eroc_gbp_per_roc,mutualisation_gbp_total\n"
        "2021-22,50.80,12.34,5.67,1234567.89\n",
        encoding="utf-8",
    )
    df = ofgem_aggregate.load_roc_prices_csv()
    assert len(df) == 1
    assert df.iloc[0]["obligation_year"] == "2021-22"
    assert df.iloc[0]["buyout_gbp_per_roc"] == pytest.approx(50.80)


# ---------------------------------------------------------------------------
# 6. parse_xlsx_to_monthly — 12-year XLSX determinism (D-21)
# ---------------------------------------------------------------------------
def test_xlsx_to_monthly_determinism():
    """Two calls on the committed 12-year XLSX must return byte-identical DataFrames (D-21).

    Validates that parse_xlsx_to_monthly() is purely deterministic: same
    XLSX bytes → identical year/month/technology/rocs_issued values, same
    row order. No clock or randomness may influence the output.

    Plan 02 replacement for the Plan 01 SKIP-marked placeholder (the XLSX
    is now committed at data/raw/ofgem/rocs_report_2006_to_2018_*.xlsx).
    """
    from uk_subsidy_tracker.data.ofgem_aggregate import parse_xlsx_to_monthly

    df1 = parse_xlsx_to_monthly()
    df2 = parse_xlsx_to_monthly()

    assert len(df1) > 0, "parse_xlsx_to_monthly() returned empty DataFrame"
    pd.testing.assert_frame_equal(df1, df2, check_exact=True)


# ---------------------------------------------------------------------------
# 7–12. parse_annual_xlsx_to_aggregate_rows — per-year determinism (D-21)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("scheme_year", ["SY18", "SY19", "SY20", "SY21", "SY22", "SY23"])
def test_annual_xlsx_determinism(scheme_year: str):
    """Two calls on the same committed XLSX must return byte-identical DataFrames (D-21).

    Validates that parse_annual_xlsx_to_aggregate_rows(scheme_year) is
    purely deterministic: same XLSX bytes → identical scheme_year/year/
    country/technology/generation_gwh/rocs_issued values, same row order.

    Covers SY18 (2019-20) through SY23 (2024-25) — all six scheme years
    for which an XLSX dataset companion is committed to data/raw/ofgem/.
    SY17 is absent (deferred per frontmatter revision_decisions.sy17_disposition).
    """
    from uk_subsidy_tracker.data.ofgem_aggregate import parse_annual_xlsx_to_aggregate_rows

    df1 = parse_annual_xlsx_to_aggregate_rows(scheme_year)
    df2 = parse_annual_xlsx_to_aggregate_rows(scheme_year)

    assert len(df1) > 0, f"parse_annual_xlsx_to_aggregate_rows({scheme_year!r}) returned empty DataFrame"
    pd.testing.assert_frame_equal(df1, df2, check_exact=True)


# ---------------------------------------------------------------------------
# Task 4: download_annual_xlsx — mocked-network tests
# ---------------------------------------------------------------------------

def test_download_annual_xlsx_writes_file_for_sy18(tmp_path, monkeypatch):
    """Happy path: SY18 download writes bytes; output path matches manifest."""
    from unittest.mock import MagicMock
    from uk_subsidy_tracker.data import ofgem_aggregate
    monkeypatch.setattr(
        ofgem_aggregate,
        "DATA_DIR",
        tmp_path,
        raising=False,
    )
    # Mock requests.get to return a fake XLSX payload
    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.iter_content.return_value = [b"PK\x03\x04fake-xlsx-bytes"]
    with patch(
        "uk_subsidy_tracker.data.ofgem_aggregate.requests.get",
        return_value=fake_response,
    ):
        out = ofgem_aggregate.download_annual_xlsx("SY18")
    assert out.name == "ro_annual_report_data_2019-20.xlsx"
    assert out.exists()
    assert out.read_bytes().startswith(b"PK")


def test_download_annual_xlsx_fails_loud_on_network_error():
    """D-17 fail-loud: RequestException propagates."""
    from uk_subsidy_tracker.data import ofgem_aggregate
    with patch(
        "uk_subsidy_tracker.data.ofgem_aggregate.requests.get",
        side_effect=requests.exceptions.ConnectionError("network down"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            ofgem_aggregate.download_annual_xlsx("SY18")


def test_download_annual_xlsx_raises_key_error_for_sy17():
    """SY17 deferred — manifest has no SY17 entry; download must KeyError."""
    from uk_subsidy_tracker.data import ofgem_aggregate
    with pytest.raises(KeyError):
        ofgem_aggregate.download_annual_xlsx("SY17")


# ---------------------------------------------------------------------------
# Task 5: parse_annual_xlsx_to_aggregate_rows + emit_annual_aggregate_csv
# ---------------------------------------------------------------------------

def test_parse_annual_xlsx_sy18_emits_all_technologies_row():
    """SY18 has no per-tech breakdown — must emit exactly 1 row with technology='All technologies'."""
    from uk_subsidy_tracker.data.ofgem_aggregate import parse_annual_xlsx_to_aggregate_rows

    df = parse_annual_xlsx_to_aggregate_rows("SY18")
    assert len(df) == 1, f"Expected 1 row for SY18, got {len(df)}"
    assert df.iloc[0]["technology"] == "All technologies"
    assert df.iloc[0]["scheme_year"] == "SY18"
    assert df.iloc[0]["country"] == "GB"
    assert df.iloc[0]["rocs_issued"] is not None
    assert df.iloc[0]["rocs_issued"] > 0


def test_parse_annual_xlsx_sy21_has_gb_and_ni_rows():
    """SY21 (Figure 3.2/3.3 path) emits rows for both GB (England/Scotland/Wales) and NI."""
    from uk_subsidy_tracker.data.ofgem_aggregate import parse_annual_xlsx_to_aggregate_rows

    df = parse_annual_xlsx_to_aggregate_rows("SY21")
    assert len(df) > 10, f"Expected >10 rows for SY21, got {len(df)}"
    assert set(df["scheme_year"]) == {"SY21"}
    countries = set(df["country"].unique())
    assert "GB" in countries, f"Expected GB in countries, got {countries}"
    assert "NI" in countries, f"Expected NI in countries, got {countries}"
    # No SY17 contamination
    assert "SY17" not in df["scheme_year"].values


def test_emit_annual_aggregate_csv_shape_and_sidecar(tmp_path, monkeypatch):
    """emit_annual_aggregate_csv writes >=30 data rows, Provenance header, 6-source sidecar."""
    import json
    from uk_subsidy_tracker.data import ofgem_aggregate

    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", tmp_path)
    # XLSXes are in the real DATA_DIR — point read path to real files by NOT
    # patching xlsx reads; only patch the output path via output_path kwarg.
    from uk_subsidy_tracker import DATA_DIR as REAL_DATA_DIR

    # Monkeypatching DATA_DIR breaks xlsx_path resolution — restore for parse calls.
    monkeypatch.setattr(ofgem_aggregate, "DATA_DIR", REAL_DATA_DIR)
    out_path = tmp_path / "ro-annual-aggregate.csv"
    result = ofgem_aggregate.emit_annual_aggregate_csv(output_path=out_path)

    assert result == out_path
    assert out_path.exists()

    # Provenance header must be present
    with open(out_path, encoding="utf-8") as f:
        first_line = f.readline()
    assert first_line.startswith("# Provenance:")

    # Data rows
    df = pd.read_csv(out_path, comment="#")
    assert len(df) >= 30, f"Expected >=30 rows, got {len(df)}"
    assert "SY17" not in df["scheme_year"].values

    # Sidecar
    sidecar_path = tmp_path / "ro-annual-aggregate.csv.meta.json"
    assert sidecar_path.exists(), "Sidecar .meta.json must exist alongside CSV"
    meta = json.loads(sidecar_path.read_text())
    assert "sources" in meta, "Sidecar must have sources[] array"
    assert len(meta["sources"]) == 6, f"Expected 6 sources, got {len(meta['sources'])}"
    scheme_years_in_sources = [s["scheme_year"] for s in meta["sources"]]
    assert scheme_years_in_sources == ["SY18", "SY19", "SY20", "SY21", "SY22", "SY23"]
