"""Mocked scraper error-path tests for ofgem_ro.py + roc_prices.py (Plan 05-01).

No network; every test patches `requests.get`. Pattern mirrors
tests/test_ons_gas_download.py (Phase 4 Plan 07 commit ac9675a) for the
D-17 fail-loud contract. Adds an Option-D guard test (Plan 05-01) that
proves stub scrapers raise RuntimeError if accidentally invoked.

8 tests:
  1. test_download_ofgem_ro_register_raises_on_network_failure   (D-17 fail-loud)
  2. test_download_ofgem_ro_register_uses_timeout                (D-17 timeout=60)
  3. test_download_ofgem_ro_register_returns_path_on_success     (happy path)
  4. test_download_ofgem_ro_generation_raises_on_network_failure (D-17 fail-loud)
  5. test_download_roc_prices_raises_on_network_failure          (D-17 fail-loud)
  6. test_download_roc_prices_uses_timeout                       (D-17 timeout=60)
  7. test_ofgem_ro_output_path_bound_before_try                  (D-17 source-grep)
  8. test_download_ofgem_ro_register_option_d_raises_runtime_error  (Option-D guard)
"""
from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pytest
import requests

from uk_subsidy_tracker.data import ofgem_ro, roc_prices


# ---------------------------------------------------------------------------
# ofgem_ro.download_ofgem_ro_register
# ---------------------------------------------------------------------------
def test_download_ofgem_ro_register_raises_on_network_failure(tmp_path, monkeypatch):
    """Network failure must propagate as RequestException, not UnboundLocalError."""
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        ofgem_ro, "_REGISTER_URL", "https://example.test/ro-register.xlsx"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with patch(
        "uk_subsidy_tracker.data.ofgem_ro.requests.get",
        side_effect=requests.exceptions.ConnectionError("boom"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            ofgem_ro.download_ofgem_ro_register()


def test_download_ofgem_ro_register_uses_timeout(tmp_path, monkeypatch):
    """Every requests.get call MUST carry timeout=60 (Phase 4 D-17 convention)."""
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        ofgem_ro, "_REGISTER_URL", "https://example.test/ro-register.xlsx"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
    mock_response.raise_for_status.return_value = None
    with patch(
        "uk_subsidy_tracker.data.ofgem_ro.requests.get",
        return_value=mock_response,
    ) as mock_get:
        ofgem_ro.download_ofgem_ro_register()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs.get("timeout") == 60, (
        f"download_ofgem_ro_register must pass timeout=60; "
        f"got {call_kwargs.get('timeout')!r}"
    )


def test_download_ofgem_ro_register_returns_path_on_success(tmp_path, monkeypatch):
    """Happy path: return path == DATA_DIR/raw/ofgem/ro-register.xlsx; file exists."""
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        ofgem_ro, "_REGISTER_URL", "https://example.test/ro-register.xlsx"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
    mock_response.raise_for_status.return_value = None
    with patch(
        "uk_subsidy_tracker.data.ofgem_ro.requests.get",
        return_value=mock_response,
    ):
        path = ofgem_ro.download_ofgem_ro_register()
    assert path == tmp_path / "raw" / "ofgem" / "ro-register.xlsx"
    assert path.exists()
    assert path.read_bytes() == b"xlsx-bytes-stub"


# ---------------------------------------------------------------------------
# ofgem_ro.download_ofgem_ro_generation
# ---------------------------------------------------------------------------
def test_download_ofgem_ro_generation_raises_on_network_failure(tmp_path, monkeypatch):
    """Network failure on generation downloader must propagate as RequestException."""
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        ofgem_ro, "_GENERATION_URL", "https://example.test/ro-generation.csv"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with patch(
        "uk_subsidy_tracker.data.ofgem_ro.requests.get",
        side_effect=requests.exceptions.Timeout("read-timeout"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            ofgem_ro.download_ofgem_ro_generation()


# ---------------------------------------------------------------------------
# roc_prices.download_roc_prices
# ---------------------------------------------------------------------------
def test_download_roc_prices_raises_on_network_failure(tmp_path, monkeypatch):
    """Network failure on roc_prices downloader must propagate as RequestException."""
    monkeypatch.setattr(roc_prices, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        roc_prices, "_PRICES_URL", "https://example.test/roc-prices.csv"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with patch(
        "uk_subsidy_tracker.data.roc_prices.requests.get",
        side_effect=requests.exceptions.ConnectionError("boom"),
    ):
        with pytest.raises(requests.exceptions.RequestException):
            roc_prices.download_roc_prices()


def test_download_roc_prices_uses_timeout(tmp_path, monkeypatch):
    """Every requests.get call in roc_prices MUST carry timeout=60."""
    monkeypatch.setattr(roc_prices, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        roc_prices, "_PRICES_URL", "https://example.test/roc-prices.csv"
    )
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"obligation_year,buyout\n"]
    mock_response.raise_for_status.return_value = None
    with patch(
        "uk_subsidy_tracker.data.roc_prices.requests.get",
        return_value=mock_response,
    ) as mock_get:
        roc_prices.download_roc_prices()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs.get("timeout") == 60, (
        f"download_roc_prices must pass timeout=60; "
        f"got {call_kwargs.get('timeout')!r}"
    )


# ---------------------------------------------------------------------------
# Static source-grep guards (D-17 discipline)
# ---------------------------------------------------------------------------
def test_ofgem_ro_output_path_bound_before_try():
    """Source-grep guard: `output_path = DATA_DIR` must appear BEFORE `try:`
    in download_ofgem_ro_register (gap #2 fix per Phase 4 Plan 07).
    """
    src = inspect.getsource(ofgem_ro.download_ofgem_ro_register)
    assert "output_path = DATA_DIR" in src, (
        "download_ofgem_ro_register must bind output_path before try:"
    )
    assert "try:" in src, "download_ofgem_ro_register must have try: block"
    output_idx = src.index("output_path = DATA_DIR")
    try_idx = src.index("try:")
    assert output_idx < try_idx, (
        f"output_path must be bound BEFORE try: block "
        f"(output at {output_idx}, try at {try_idx})"
    )


# ---------------------------------------------------------------------------
# Option-D guard (Plan 05-01)
# ---------------------------------------------------------------------------
def test_download_ofgem_ro_register_option_d_raises_runtime_error(
    tmp_path, monkeypatch
):
    """Option-D guard: empty _REGISTER_URL must raise RuntimeError pointing
    at the investigation report. Proves stub scrapers fail-loud if the
    refresh loop accidentally invokes them.
    """
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    monkeypatch.setattr(ofgem_ro, "_REGISTER_URL", "")
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with pytest.raises(RuntimeError) as excinfo:
        ofgem_ro.download_ofgem_ro_register()
    assert "manual refresh" in str(excinfo.value)
    assert "INVESTIGATION.md" in str(excinfo.value)
