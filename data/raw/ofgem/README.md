# `data/raw/ofgem/` — Ofgem RO Raw Data

**Status as of Plan 05-01 (2026-04-23):** Option-D fallback. Three header-only stub
files committed; real Ofgem exports awaited via Plan 05-13 post-execution review.

See `.planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md` for the
full Options A/B/C/D assessment that led to this fallback.

## Files

| File | Status | Real source (when ready) |
|------|--------|--------------------------|
| `ro-register.xlsx` | Header-only stub (1 row, ~9 columns, ~5 KB) | Ofgem RER station-register export (`rer.ofgem.gov.uk`, SharePoint-OIDC auth required) |
| `ro-generation.csv` | Header-only stub (1 row, 5 columns, ~80 bytes) | Ofgem monthly ROC issuance CSV (same SharePoint source) |
| `roc-prices.csv` | Header-only stub (1 row, 5 columns, ~80 bytes) | Ofgem public PDF transparency documents (transcription deferred to Plan 05-13) |

## How sidecars stay valid

Each `*.meta.json` sidecar carries the SHA-256 of the **stub bytes** as
shipped. `schemes/ro/_refresh.py::upstream_changed()` (shipped in a later
Plan 05-XX) compares this sha256 to the file on disk; while the stub
remains in place, the daily refresh cron auto-skips and never invokes
the scraper functions (which would `RuntimeError` if invoked).

When the real export lands, both the raw file AND its sidecar must be
re-written together (one atomic commit, mirroring the Phase 4 D-04
discipline) so the cron continues to compute `upstream_changed() == False`
on subsequent runs.

## How NOT to refresh

**Do not run `download_ofgem_ro_register()`, `download_ofgem_ro_generation()`,
or `download_roc_prices()` directly today.** These functions raise
`RuntimeError("manual refresh — see INVESTIGATION.md ...")` precisely
to surface the Option-D state if invoked. The fail-loud behaviour is the
intended D-17 discipline (Phase 4 Plan 07).
