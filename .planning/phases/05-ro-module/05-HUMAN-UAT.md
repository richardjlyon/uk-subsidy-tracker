---
status: partial
phase: 05-ro-module
source: [05-VERIFICATION.md, 05-13-SUMMARY.md]
started: 2026-04-23T07:14:31Z
updated: 2026-04-23T07:14:31Z
---

# Phase 5 Human Verification Items

All 5 items are genuine human actions (credentials / PDF transcription / upstream data arrival / live browser check). Documented in Plan 05-13's Human-Action Follow-Up Register with re-arm verification bash blocks.

## Current Test

[awaiting human action — see .planning/phases/05-ro-module/05-13-SUMMARY.md §HA-* register]

## Tests

### 1. HA-01 — Real Ofgem RER data plumbing
expected: 3 Option-D stubs at `data/raw/ofgem/{ro-register.xlsx, ro-generation.csv, roc-prices.csv}` replaced with real Ofgem RER exports. Sidecar sha256 matches. `schemes.ro.rebuild_derived()` produces non-zero-row Parquet grains.
re-arm: `grep -c "option-d-stub" data/raw/ofgem/*.meta.json` → 0
priority: HIGH (blocks every downstream RO deliverable)
result: [pending]

### 2. HA-02 — NIROC primary-source transcription
expected: 12 `[ASSUMED]` entries in `src/uk_subsidy_tracker/data/ro_bandings.yaml` replaced with Utility Regulator NI banding factors + Provenance blocks (source/url/retrieved_on).
re-arm: `grep -c "\[ASSUMED\]" src/uk_subsidy_tracker/data/ro_bandings.yaml` → 0
priority: MEDIUM
result: [pending]

### 3. HA-03 — EU ETS 2005-2017 carbon-price audit
expected: 13 `[VERIFICATION-PENDING]` entries in `tests/fixtures/constants.yaml` verified against EEA "Emissions, allowances, surplus and prices in the EU ETS 2005-2020" viewer + Bank of England EUR/GBP annual-average series.
re-arm: `grep -c "VERIFICATION-PENDING" tests/fixtures/constants.yaml` → 0
priority: LOW (next_audit 2027-01-15)
result: [pending]

### 4. HA-04 — REF reconciliation hard-block re-arm
expected: After HA-01 lands real RO data, `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` sentinel deleted; 22 xfailed `test_ref_constable_ro_reconciliation` cases re-arm to hard-block and reconcile within ±3% of REF Constable 2025 Table 1.
re-arm: `uv run pytest tests/test_benchmarks.py -k ref_constable -v` → all passed (0 xfailed)
priority: AUTO-FOLLOW (depends on HA-01)
result: [pending]

### 5. HA-05 — Browser-based visual inspection
expected: `uv run mkdocs serve` + open `docs/schemes/ro.md` in browser. Verify 4 RO chart embeds render, PNG thumbnails load, interactive Plotly HTML hovers work, GOV-01 four-way coverage links resolve.
re-arm: Live manual check (mkdocs --strict is strong proxy but not a substitute for live Plotly interaction)
priority: LOW
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps

(none — all 5 items are pending genuine human action, not gaps against phase completion criteria)
