"""Regression guard for ons_gas.download_dataset() error-path.

Gap #2 in .planning/phases/04-publishing-layer/04-VERIFICATION.md:
`output_path` was assigned inside the try block but the except handler
returned it — UnboundLocalError on any network failure. Exercised
precisely when the ONS publisher is unavailable, i.e. when the
'methodologically bulletproof' promise is being tested.

This test pins the D-17 'fail-loud' posture: network failure raises a
RequestException (the workflow job fails loud, opens a refresh-failure
issue), never UnboundLocalError, never a silent un-downloaded path.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from uk_subsidy_tracker.data import ons_gas


def test_download_dataset_raises_on_network_failure(tmp_path, monkeypatch):
    """Network failure must propagate as RequestException, not UnboundLocalError."""
    monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
    with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
               side_effect=requests.exceptions.ConnectionError("boom")):
        with pytest.raises(requests.exceptions.RequestException):
            ons_gas.download_dataset()


def test_download_dataset_uses_timeout(tmp_path, monkeypatch):
    """Every requests.get call MUST carry timeout=60 (Elexon convention)."""
    monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"hello"]
    mock_response.raise_for_status.return_value = None
    with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
               return_value=mock_response) as mock_get:
        ons_gas.download_dataset()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs.get("timeout") == 60, (
        f"ons_gas.download_dataset() must pass timeout=60; got {call_kwargs.get('timeout')!r}"
    )


def test_download_dataset_returns_path_on_success(tmp_path, monkeypatch):
    """Happy path: return the path; file exists with downloaded bytes."""
    monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
    mock_response.raise_for_status.return_value = None
    with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
               return_value=mock_response):
        path = ons_gas.download_dataset()
    assert path == tmp_path / ons_gas.GAS_SAP_DATA_FILENAME
    assert path.exists()
    assert path.read_bytes() == b"xlsx-bytes-stub"
