---
title: RO Data Strategy — Option A1 (Ofgem-reconstructed primary, REF as cross-check)
date: 2026-04-24
context: Post-Phase-5 RO module discovery — Ofgem withdrew public access to station-level RO data
status: decided
supersedes: Phase 5 Plan 05-13 Follow-Up #4 (credentialed RER scraper) as the primary data path
---

# RO Data Strategy — Option A1

## The Decision

Reconstruct the published RO numbers from **publicly downloadable Ofgem aggregates**, with **REF Constable 2025 as the independent ±3% benchmark cross-check**. Defer station-level analysis (S4 concentration / Lorenz, S5 forward projection) to a future phase that plumbs credentialed RER access — OR obviates the need entirely via REF data-sharing collaboration.

## Why Not the Other Options

**Why not B (commit to credentialed RER scraper now)** — Real work: ~200 LOC Playwright + SharePoint-OIDC click-path + ~150 MB Chromium runtime in CI + GitHub Secrets (`OFGEM_RER_EMAIL`, `OFGEM_RER_SESSION_COOKIE`) + ~30-day session-cookie refresh cadence. Brittle UI surface — every Ofgem SharePoint UI revision breaks the scraper silently. Blocks Phase 6 portal launch on infrastructure work that may turn out to be unnecessary if REF collaboration materialises (see seed `ref-collaboration-followup.md`).

**Why not C (REF Constable as primary, Ofgem as cross-check)** — Inverts the project's "every number traceable to a primary regulator source" rule (PROJECT.md core value). REF is a respected independent analyst but not a regulator. Acceptable as a benchmark; weakens the project's claim if used as the cited primary source for the headline £67bn figure.

## Why A1 Is Defensible

1. **Methodology rule preserved** — every published number traces to an Ofgem-published source (the 2006-2018 monthly XLSX + the 2018-present annual report PDFs).
2. **REF cross-check already wired** — `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` is the formal contract that A1 reconciles to A2 within ±3% per scheme year. The test is currently sentinel-gated by the absent-data DIVERGENCE.md; once real data lands, the sentinel deletes and the test becomes a hard CI block.
3. **Ofgem's withdrawal becomes part of the published analysis** — the methodology section of `docs/schemes/ro.md` will explicitly document the Public Reports Dashboard withdrawal (date, scope, what was lost) and the workaround. This converts the obstruction into evidence rather than a vulnerability.
4. **S4/S5 deferral is honest, not concealed** — the published RO page will carry visible "DEFERRED: data-gated by Ofgem withdrawal" markers for the two missing chart slots, with a link to the corrections / methodology page explaining the situation.
5. **Phase 6 portal unblocked** — S2 (cost dynamics) + S3 (by technology) + the £67bn headline are sufficient to populate the 2×4 scheme-grid tile and to make RO equal-weight with CfD on the portal homepage.

## What Gets Deferred

- **S4 (concentration / Lorenz)** — needs per-station ROC issuance. Marked `DEFERRED: data-gated`.
- **S5 (forward projection)** — needs per-station accreditation_date + DNC + expected_end_date. Marked `DEFERRED: data-gated`.
- **Station-level architecture in `schemes/ro/`** — `cost_model.py::build_station_month()` and the station-grain Parquet emit stay in tree but become dormant code paths, ready for re-activation when credentialed access lands.

## What Gets Built

See Phase 5.2 in ROADMAP.md (RO Data Reconstruction — Aggregate-Grain) for the concrete plan.

## Why Not Re-Litigate Later

If a future maintainer asks "why didn't you just plumb RER credentials?", the answer is in this file: (a) the credentialed-scraper work is real and brittle; (b) the public aggregate path delivers a working portal faster with no methodology compromise; (c) station-level work is parked as a clean, separable backlog item (`999.x`) ready to be picked up if/when REF collaboration falls through OR a credentialed-access decision becomes business-critical.

## References

- `.planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md` — full Ofgem URL probe results (2026-04-23) + Option A/B/C/D assessment + Plan 05-13 follow-up register
- `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` — REF reconciliation sentinel (delete on Phase 5.2 completion)
- `.planning/seeds/ref-collaboration-followup.md` — REF outreach trigger
- `.planning/phases/05-ro-module/05-13-SUMMARY.md` — Phase 5 close-out with full follow-up register
- Ofgem 12-year XLSX: `https://www.ofgem.gov.uk/sites/default/files/2025-05/rocs_report_2006_to_2018_20250410081520.xlsx` (HTTP 200, last modified 2025-05-21, 114 KB, 3 sheets aggregate by tech × month × country)
- Ofgem pre-2007 archive: `https://www.ofgem.gov.uk/sites/default/files/docs/2006/11/ro_weblist_archive_0.xls` (HTTP 200, last modified 2013-07-31, 210 KB)
- Ofgem RO public reports landing: `https://www.ofgem.gov.uk/renewables-obligation-ro/contacts-guidance-and-resources/public-reports-and-data-ro`
- Latest Ofgem annual report: `https://www.ofgem.gov.uk/transparency-document/renewables-obligation-annual-report-scheme-year-23-1-april-2024-31-march-2025`
