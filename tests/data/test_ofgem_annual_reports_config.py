"""Unit tests for ofgem_annual_reports.yaml + load_ofgem_annual_reports_config."""
from __future__ import annotations

import pytest

from uk_subsidy_tracker.data.ofgem_aggregate import (
    OfgemAnnualReportsConfig,
    load_ofgem_annual_reports_config,
)


def test_config_loads_and_validates_six_entries() -> None:
    cfg = load_ofgem_annual_reports_config()
    assert isinstance(cfg, OfgemAnnualReportsConfig)
    assert len(cfg.reports) == 6, f"expected 6 SY18-SY23 reports, got {len(cfg.reports)}"
    scheme_years = sorted([r.scheme_year for r in cfg.reports])
    assert scheme_years == ["SY18", "SY19", "SY20", "SY21", "SY22", "SY23"]


def test_each_entry_carries_required_fields() -> None:
    cfg = load_ofgem_annual_reports_config()
    for r in cfg.reports:
        assert r.scheme_year.startswith("SY"), r
        assert r.url.startswith("https://www.ofgem.gov.uk/sites/default/files/"), r
        assert r.local_filename.endswith(".xlsx"), r
        assert r.expected_min_size_bytes > 0, r
        assert r.notes, r


def test_sy18_url_verbatim_from_context_md() -> None:
    cfg = load_ofgem_annual_reports_config()
    sy18 = cfg.by_scheme_year("SY18")
    assert sy18.url == (
        "https://www.ofgem.gov.uk/sites/default/files/docs/2021/03/"
        "ro_annual_report_data_2019-20.xlsx"
    )


def test_sy23_url_verbatim_from_context_md() -> None:
    cfg = load_ofgem_annual_reports_config()
    sy23 = cfg.by_scheme_year("SY23")
    assert sy23.url == (
        "https://www.ofgem.gov.uk/sites/default/files/2026-03/"
        "Renewables_Obligation_Annual_Report_Scheme_Year_23_Dataset-"
        "20260327121339.xlsx"
    )


def test_sy17_absent_from_manifest_deferred() -> None:
    """SY17 deferred per revision_decisions.sy17_disposition — must NOT appear."""
    cfg = load_ofgem_annual_reports_config()
    with pytest.raises(KeyError):
        cfg.by_scheme_year("SY17")
