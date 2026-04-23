# Phase 05 Plan 09 — REF Constable Reconciliation Divergence Report

**Created by:** Plan 05-09 executor, 2026-04-23
**Status:** Active sentinel — `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` **xfails while this file exists** (D-14 hard-block temporarily lowered to unblock Phase 5 unattended chain).
**Reviewer gate:** Plan 05-13 Task 4 (Post-Execution Human Review).
**Re-arm trigger:** Delete this file when `schemes.ro.rebuild_derived()` produces non-stub data (Plan 05-13 Ofgem RER plumbing complete).

---

## Executive summary

Under Plan 05-01 Option-D fallback conditions, `data/derived/ro/station_month.parquet` emits a **zero-row canonical-shape Parquet**. The REF Constable reconciliation test parametrises over 22 REF-transcribed years (2002-2023) and every case fails with `"Pipeline has no data for year {N}"` because the pipeline aggregate dict is empty. This is NOT a 3-percent pipeline-vs-REF accuracy miss — it is the absence of real data flowing through the RO pipeline.

Per the plan's executor directive (05-09-PLAN.md Task 2 `<action>` block), the executor:

1. Did NOT raise `REF_TOLERANCE_PCT` (still `3.0` — D-14 preserved).
2. Did NOT delete the test (still parametrised over all 22 REF years).
3. Documented the divergence event here for Plan 05-13 Task 4 review.
4. The sentinel-file xfail escape hatch activates on the next test run so the Phase 5 unattended chain (Plans 10-13) is unblocked.

## Observed divergence

Command executed:

```
uv run python -c "from uk_subsidy_tracker.schemes import ro; ro.rebuild_derived()"
uv run pytest tests/test_benchmarks.py -q -k ref_constable
```

Result (pre-sentinel):

```
22 failed, 2 deselected in 0.69s
FAILED ...::test_ref_constable_ro_reconciliation[ref_constable-2002]
FAILED ...::test_ref_constable_ro_reconciliation[ref_constable-2003]
... (all 22 parametrisations)
FAILED ...::test_ref_constable_ro_reconciliation[ref_constable-2023]

Failure message (for year 2023; identical pattern for all years):
> Failed: Pipeline has no data for year 2023 — either the RO derived Parquet
> was not built before this test or station_month.parquet filtering to
> country='GB' dropped the year.
```

Per-year divergence table (all entries identical — no pipeline data at all):

| REF year | REF £bn | Pipeline £bn | Divergence | Reason |
|----------|---------|--------------|------------|--------|
| 2002 | 0.3 | (no data) | N/A | zero-row Parquet |
| 2003 | 0.4 | (no data) | N/A | zero-row Parquet |
| 2004 | 0.5 | (no data) | N/A | zero-row Parquet |
| 2005 | 0.6 | (no data) | N/A | zero-row Parquet |
| 2006 | 0.7 | (no data) | N/A | zero-row Parquet |
| 2007 | 0.9 | (no data) | N/A | zero-row Parquet |
| 2008 | 1.0 | (no data) | N/A | zero-row Parquet |
| 2009 | 1.1 | (no data) | N/A | zero-row Parquet |
| 2010 | 1.3 | (no data) | N/A | zero-row Parquet |
| 2011 | 1.5 | (no data) | N/A | zero-row Parquet (ROADMAP SC #3 window start) |
| 2012 | 2.0 | (no data) | N/A | zero-row Parquet |
| 2013 | 2.6 | (no data) | N/A | zero-row Parquet |
| 2014 | 3.1 | (no data) | N/A | zero-row Parquet |
| 2015 | 3.7 | (no data) | N/A | zero-row Parquet |
| 2016 | 4.5 | (no data) | N/A | zero-row Parquet |
| 2017 | 5.3 | (no data) | N/A | zero-row Parquet |
| 2018 | 5.9 | (no data) | N/A | zero-row Parquet |
| 2019 | 6.3 | (no data) | N/A | zero-row Parquet |
| 2020 | 5.7 | (no data) | N/A | zero-row Parquet |
| 2021 | 6.4 | (no data) | N/A | zero-row Parquet (D-11 mutualisation year) |
| 2022 | 6.4 | (no data) | N/A | zero-row Parquet (ROADMAP SC #3 window end) |
| 2023 | 6.8 | (no data) | N/A | zero-row Parquet (REF series end) |

## Root cause (verified on 2026-04-23)

Inspection of upstream raw files:

```
data/raw/ofgem/ro-register.csv    — ABSENT (required by cost_model.build_station_month)
data/raw/ofgem/ro-generation.csv  — 72 bytes (header-only CSV stub from Plan 05-01 Option-D fallback)
data/raw/ofgem/roc-prices.csv     — see sidecar; Plan 05-01 seed
```

Plan 05-01 adopted Option-D (committed header-only stubs with verified SHA-256 sidecars) because Ofgem's Renewables Energy Register (`rer.ofgem.gov.uk`) replaced the legacy `renewablesandchp.ofgem.gov.uk` on 2025-05-14 and now requires SharePoint + email-auth for public data access (05-RESEARCH.md §1, LOW-MEDIUM confidence). The programmatic RER plumbing is Plan 05-13's explicit scope (Post-Execution Human Review gate).

With zero rows in `station_month.parquet`:

- `ro_annual_totals_gbp_bn` fixture returns `{}` (after the in-fixture empty-check short-circuits on `len(df) == 0`).
- Every REF-year `entry.year` lookup in the parametrised test returns `None`.
- Each parametrisation raises `pytest.fail("Pipeline has no data for year ...")` — correct D-14 diagnostic behaviour under zero-data conditions.

**This is NOT a banding error, NOT a scope mismatch, NOT a carbon-price extension regression.** It is the absence of raw Ofgem data flowing through the pipeline, by design, as of Phase 5 Plan 01.

## Classification (D-14 ladder)

Per the plan's D-14 diagnostic ladder in the test failure message:

1. **REF scope difference?** — N/A. Cannot evaluate scope alignment when pipeline output is empty.
2. **Banding error?** — N/A. `rocs_issued` and `rocs_computed` are both absent (zero rows).
3. **Carbon-price extension regression?** — N/A. No station-month rows exercise the `_annual_counterfactual_gbp_per_mwh` helper yet.

**Classification:** **Data-absence divergence, not methodological divergence.** Resolution path is Plan 05-13 (Ofgem RER scraper + backfill), not a pipeline-internal regression.

## Suggested remediation (Plan 05-13 Task 4 review)

Option A (RECOMMENDED — matches plan's intended resolution path):
- Plan 05-13 plumbs real Ofgem data via RER (MS Graph API / Playwright email-auth / direct RER dashboard URLs per CONTEXT §"Claude's Discretion - Ofgem scraper mechanism").
- After rebuild, delete this `05-09-DIVERGENCE.md` file.
- Re-run `uv run pytest tests/test_benchmarks.py -q -k ref_constable`.
- If all 22 REF years now pass within ±3%, D-14 hard block restored; RO-06 closed.
- If any REF year now fails the ±3% check, the divergence is methodological: re-write this file with a root-cause hypothesis from the D-14 ladder (REF scope vs D-12 scope / banding / carbon-price extension) and re-queue Plan 05-13 Task 4.

Option B (if Option A blocked):
- Document scope-delta explicitly in `benchmarks.yaml::ref_constable` audit header (e.g. "REF excludes mutualisation on 2021-22" if that emerges).
- Adjust `REF_TOLERANCE_PCT` ONLY with a `CHANGES.md ## Methodology versions` entry per D-07.

Option C (DO NOT choose):
- Silent `pytest.skip` reintroduction — forbidden by D-14.
- Deleting the `test_ref_constable_ro_reconciliation` test — would regress RO-06 gate.

## Re-arm verification (for Plan 05-13 Task 4 reviewer)

After Plan 05-13 lands real Ofgem data and `schemes.ro.rebuild_derived()` produces non-stub output:

```bash
# 1. Confirm non-stub derived Parquet
uv run python -c "
from uk_subsidy_tracker.schemes import ro
import pyarrow.parquet as pq
t = pq.read_table(ro.DERIVED_DIR / 'station_month.parquet')
print('num_rows:', t.num_rows)
assert t.num_rows > 0, 'still stub — RO data not landed'
"

# 2. Delete this sentinel
rm .planning/phases/05-ro-module/05-09-DIVERGENCE.md

# 3. Re-run REF reconciliation (HARD BLOCK now active)
uv run pytest tests/test_benchmarks.py -q -k ref_constable

# Expected: 22 passed (within ±3% for every REF-transcribed year).
# If any year fails: do NOT restore this sentinel. Follow the plan's D-14
# ladder (REF scope vs our D-12 scope / banding / carbon-price extension)
# and resolve before phase exit.
```

## Cross-references

- `.planning/phases/05-ro-module/05-CONTEXT.md` D-13 (REF anchor), D-14 (hard block discipline)
- `.planning/phases/05-ro-module/05-RESEARCH.md` §5 (REF Constable 2025 transcription)
- `.planning/phases/05-ro-module/05-09-PLAN.md` Task 2 `<action>` (DIVERGENCE.md executor directive)
- `.planning/phases/05-ro-module/05-13-PLAN.md` Task 4 (Post-Execution Human Review — the gate that resolves this)
- `.planning/phases/05-ro-module/05-01-SUMMARY.md` (Option-D fallback posture for raw Ofgem files)
- `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` (the test this sentinel xfails)
- `tests/fixtures/benchmarks.yaml::ref_constable` (the 22 REF Table 1 entries)
