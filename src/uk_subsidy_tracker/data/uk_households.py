"""UK households-count constant — ONS Families and Households time series.

Phase 6 cross-scheme X3 chart denominator. Per-year for historical accuracy
(2014: 26.7M; 2024: 28.6M — 7% drift would mis-scale early bars by 7%).

Provenance:
  source:       ONS Families and Households Dataset 2025 edition
  url:          https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds
  basis:        Labour Force Survey April-June quarter; UK total of single-family
                + multi-family + lone-person households (Sheet 7 'All households' row).
  retrieved_on: 2026-04-25
  next_audit:   2027-04-30  (ONS publishes annually in April)
  file:         familiesandhouseholdsuk2025.xlsx (raw file lives in data/raw/ons/)
  sha256:       computed by data/sidecar.py::write_sidecar; recorded in .meta.json

Pre-2014 handling per CONTEXT Discretion + RESEARCH Q3 recommendation: the
dict deliberately covers 2014-2024 only. The X3 plotting layer skips bars
where ``households_uk`` would be missing (pre-2014 RO years); methodology.md
documents the omission.

Values transcribed from Sheet 7 "Table 7: Households by type of household
and family, United Kingdom, 1996 to 2025", "All households" row. ONS
publishes counts in thousands; the integer count below is value × 1000.
"""
from __future__ import annotations

# Per-year UK households count, ONS published, integer count.
# Verified by reading data/raw/ons/familiesandhouseholdsuk2025.xlsx Sheet 7
# "All households" row on 2026-04-25. Values are the published estimates
# in thousands × 1000 (i.e. the full count).
UK_HOUSEHOLDS: dict[int, int] = {
    2014: 26_734_000,
    2015: 27_046_000,
    2016: 27_109_000,
    2017: 27_226_000,
    2018: 27_576_000,
    2019: 27_824_000,
    2020: 27_893_000,
    2021: 28_119_000,
    2022: 28_243_000,
    2023: 28_358_000,
    2024: 28_609_000,
}


__all__ = ["UK_HOUSEHOLDS"]
