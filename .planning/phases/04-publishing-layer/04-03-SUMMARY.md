---
phase: 04-publishing-layer
plan: 03
subsystem: derived-layer

tags: [derived-layer, parquet, scheme-contract, schemas, protocol, tdd, gov-02, test-02, test-03, test-05]

# Dependency graph
requires:
  - phase: 04-publishing-layer-01
    provides: "pyarrow + duckdb installed; SEED-001 Tier-2 drift tripwire guards METHODOLOGY_VERSION constant from silent drift"
  - phase: 04-publishing-layer-02
    provides: "data/raw/<publisher>/<file> canonical layout + .meta.json sidecars (SHA-256 + upstream_url); upstream_changed() dirty-check substrate"
provides:
  - "src/uk_subsidy_tracker/schemas/ — five Pydantic row models with dtype + unit JSON Schema metadata (D-10 / D-11). Plan 04-04 manifest.py reads their model_json_schema(mode='serialization')."
  - "src/uk_subsidy_tracker/schemes/__init__.py — SchemeModule typing.Protocol (ARCHITECTURE §6.1). Duck-typed contract; `isinstance(cfd, SchemeModule)` is the conformance smoke. Phase 5 (RO) and every subsequent scheme module copy this pattern."
  - "src/uk_subsidy_tracker/schemes/cfd/ — first real §6.1 implementation (D-01 load-bearing). rebuild_derived(output_dir) emits five Parquet + five schema.json siblings via pinned _write_parquet (D-22). 0.74s end-to-end on full CfD dataset."
  - "data/derived/cfd/*.parquet contract: five grains (station_month / annual_summary / by_technology / by_allocation_round / forward_projection) with methodology_version column on every row (GOV-02 provenance-per-row)."
  - "tests/test_determinism.py — TEST-05 formally satisfied: 10/10 green (5 content-equality via pyarrow.Table.equals() + 5 writer-identity via created_by.startswith('parquet-cpp-arrow'))."
  - "tests/test_schemas.py + tests/test_aggregates.py — TEST-02 (D-19) + TEST-03 (D-20) formally satisfied on Parquet output alongside the Phase-2 raw-CSV scaffolding. Module-scoped derived_dir fixture rebuilds once per module (cheap)."
affects:
  - 04-04-publishing-layer-manifest   # manifest.py reads schemas/cfd.py + schema.json siblings to populate manifest.json tables[] + methodology_version
  - 04-05-workflows-refresh-deploy    # refresh_all.py orchestrates cfd.upstream_changed() → cfd.refresh() → cfd.rebuild_derived() → cfd.regenerate_charts()
  - 04-06-docs-and-benchmark-floor    # docs/data/index.md snippets call pq.read_table(DERIVED_DIR / 'station_month.parquet')
  - 05+                                # RO scheme module copies schemes/cfd/ structure verbatim (hoisting from ro/*.py charts into ro/{cost_model,aggregation,...})

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pinned pyarrow Parquet writer (D-22) shared in cost_model._write_parquet and imported by aggregation + forward_projection: compression='snappy', version='2.6', use_dictionary=True, write_statistics=True, data_page_size=1<<20. Identical settings across every scheme writer; shared helper avoids config drift."
    - "Pydantic row-schema-as-column-order-source-of-truth (D-10): each row model's field declaration order IS the canonical Parquet column order. Derivation code does `df[list(Row.model_fields.keys())]` before writing; downstream tests use the same pattern to assert equality. One source of truth for column order, grep-visible in review."
    - "schema.json sibling emitted alongside each Parquet file (D-11) via emit_schema_json(Model, path). JSON is sort_keys + LF newlines + UTF-8 → byte-stable across platforms. Plan 04-04 manifest.py reads these to populate its tables[] block without re-deriving the schema."
    - "Deterministic 'current year' anchor (D-21): forward_projection.py uses int(gen['Settlement_Date'].max().year) instead of pd.Timestamp.now().year. rebuild_derived is thereby a pure function of raw content; running it at 23:59:59 vs. 00:00:01 on Jan 1 produces bit-identical Parquet."
    - "int64 year casting in rollup builders: pandas `dt.year` returns int32 by default, but the Pydantic row models declare year as int64. Auto-fix (Rule 1) casts `sm['month_end'].dt.year.astype('int64')` in all three rollups so produced Parquet matches declared schema. Without the cast, `pd.testing.assert_series_equal` in test_aggregates fails on int32-vs-int64 index dtype mismatch."
    - "Mergesort stable-sort before Parquet write: `sort_values(..., kind='mergesort')` in every builder's final sort. Stable sort is deterministic across pandas versions; default quicksort is not."

key-files:
  created:
    - "src/uk_subsidy_tracker/schemas/__init__.py — barrel re-exporting all five row models + emit_schema_json"
    - "src/uk_subsidy_tracker/schemas/cfd.py — five Pydantic BaseModel row schemas (StationMonthRow, AnnualSummaryRow, ByTechnologyRow, ByAllocationRoundRow, ForwardProjectionRow); emit_schema_json helper"
    - "src/uk_subsidy_tracker/schemes/__init__.py — SchemeModule @runtime_checkable Protocol (ARCHITECTURE §6.1)"
    - "src/uk_subsidy_tracker/schemes/cfd/__init__.py — five-callable §6.1 contract + DERIVED_DIR; isinstance-conforming"
    - "src/uk_subsidy_tracker/schemes/cfd/cost_model.py — build_station_month + shared _write_parquet (D-22) + loader-owned pandera station_month_schema"
    - "src/uk_subsidy_tracker/schemes/cfd/aggregation.py — build_annual_summary + build_by_technology + build_by_allocation_round (all read station_month.parquet back; D-03 consistency)"
    - "src/uk_subsidy_tracker/schemes/cfd/forward_projection.py — build_forward_projection (hoisted from plotting/subsidy/remaining_obligations.py:80-124; deterministic current-year anchor from max settlement date)"
    - "src/uk_subsidy_tracker/schemes/cfd/_refresh.py — SHA-256 upstream_changed() against .meta.json sidecars + thin refresh() wrapper (Plan 04-05 orchestrates)"
    - "tests/test_determinism.py — 10-case TEST-05 (5 content-equality + 5 writer-identity across grains)"
    - ".planning/phases/04-publishing-layer/04-03-SUMMARY.md"
  modified:
    - ".gitignore — appended `data/derived/` (regenerated, not committed)"
    - "tests/test_schemas.py — added 5 parametrised Parquet-variant tests (D-19) alongside the 5 raw-CSV tests"
    - "tests/test_aggregates.py — added 3 Parquet row-conservation tests (D-20) alongside the 2 raw scaffolding tests"
    - "CHANGES.md — [Unreleased] Added block with schemas/ + schemes/ + test_determinism + Parquet variants + data/derived gitignore; Changed block cites methodology_version propagation (GOV-02). No `## Methodology versions` entry (constant stays at 0.1.0 per CONTEXT D-12)."

key-decisions:
  - "Deterministic current-year anchor in forward_projection.py (max settlement date, NOT pd.Timestamp.now().year). Plan's draft chart code used Timestamp.now().year which breaks D-21 content-identity; using the raw-data-derived anchor keeps rebuild_derived a pure function of raw content. Tradeoff: `remaining_committed_mwh` is measured from the latest data point, not today's calendar date. Acceptable because refresh is daily — the anchor lags at most 24h behind wall-clock, and the alternative (non-determinism) is unacceptable for a reproducibility-first project."
  - "Pydantic model field order = canonical Parquet column order (D-10 literal). The derivation code does `df[list(Row.model_fields.keys())]` as its final column-selection step. One source of truth, grep-visible in every builder. Phase 5 (RO) will inherit this pattern."
  - "int64 year cast in rollup builders (Rule-1 auto-fix during Task 3): pandas dt.year returns int32 by default, but the Pydantic schemas declared year as int64. The test_aggregates Parquet row-conservation test surfaced the mismatch via pd.testing.assert_series_equal index-dtype assertion. Fixed at the producer side (aggregation.py) rather than the consumer (test fixture): the declared schema IS the contract, and produced Parquet must match."
  - "Rollup builders re-read station_month.parquet rather than sharing an in-memory DataFrame (D-03). Guarantees rollup consistency with the upstream grain (what you test is what Plan 04-04 will publish) and isolates each builder from surprise mutations. Tiny I/O cost: full CfD dataset is <20k rows across all grains, 0.74s end-to-end."
  - "SchemeModule is a typing.Protocol, NOT an abc.ABC (RESEARCH §Pattern 3). Modules cannot subclass an ABC in Python — you import a module, not a class. @runtime_checkable gives the isinstance() smoke test for free, and every future scheme module is duck-typed the same way. No inheritance chain to maintain."
  - "Market_Reference_Price_GBP_Per_MWh column kept on StationMonthRow (Step 1.0 pre-flight): grep of data/raw/lccc/actual-cfd-generation.csv header confirmed the column exists. Plan anticipated we might have to drop it if absent; absent-case discipline was documented but not needed here."

patterns-established:
  - "Scheme-module layout template for Phase 5+: schemes/<scheme>/{__init__.py, cost_model.py, aggregation.py, forward_projection.py, _refresh.py}. Each writer function takes `output_dir: Path` and writes `<grain>.parquet` + `<grain>.schema.json` via the shared _write_parquet + emit_schema_json helpers. RO (Phase 5) copies this verbatim with ofgem-specific loader imports."
  - "Pydantic Field(..., description=..., json_schema_extra={'dtype': ..., 'unit': ...}) idiom: every field on every row model carries these three pieces of metadata. Plan 04-04 manifest.py will render dtype + unit into user-facing table documentation without additional schema wrangling."
  - "TDD RED→GREEN shipped across two commits: test(04-03) with test_determinism.py failing ModuleNotFoundError (commit 6b695cd), feat(04-03) with schemes/cfd/ turning it green (commit e00a4f6). Makes the RED state an artefact in git history — anyone auditing can `git show 6b695cd -- tests/test_determinism.py` to see the tripwire's original shape."

requirements-completed:
  - TEST-02
  - TEST-03
  - TEST-05
  - GOV-02    # methodology_version column on every derived row; Plan 04-04 surfaces it on manifest.json. This substrate + the manifest together close GOV-02.

# Metrics
duration: 11min
completed: 2026-04-22
---

# Phase 4 Plan 03: Derived Layer + CfD Scheme Module Summary

**Shipped the derived Parquet layer (5 grains × 3,624 total rows) via the pinned pyarrow writer (0.74s end-to-end), declared the ARCHITECTURE §6.1 SchemeModule Protocol, and promoted TEST-02 / TEST-03 / TEST-05 from Phase-2 scaffolding to formal satisfaction — tests/test_determinism.py passes 10/10 via `pyarrow.Table.equals()`, Parquet variants of test_schemas.py + test_aggregates.py green against the Pydantic row models.**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-04-22T23:20:40Z
- **Completed:** 2026-04-22T23:31:59Z
- **Tasks:** 4 completed (4/4)
- **Files changed:** 14 (10 new + 4 modified)

## Accomplishments

- **Derived-layer contract is real (D-01 load-bearing).** `cfd.rebuild_derived(output_dir=tmp)` emits five Parquet files + five JSON-Schema siblings in 0.74 seconds on the full CfD dataset (3,460 station-months + 11 annual + 52 by-technology + 33 by-allocation-round + 68 forward-projection rows). Content-identity holds across rebuilds per D-21: `pyarrow.Table.equals()` returns True on every grain across two successive runs. Phase 5 (Renewables Obligation) has a verbatim template to copy.
- **TEST-02 / TEST-03 / TEST-05 formally closed on Parquet output.** Moving from Phase-2 raw-CSV scaffolding to derived-Parquet validation was the rationale for reassigning these three requirement IDs from Phase 2 to Phase 4 (commit 02-05). All three are now green: 5 parametrised `test_parquet_grain_schema` cases (every row validates against its Pydantic model via `model.model_validate`), 3 `test_*_vs_*_parquet` row-conservation cases (`pd.testing.assert_series_equal` at exact equality), and 10 `test_parquet_content_identical` + `test_file_metadata_created_by_is_pyarrow` cases in the new `tests/test_determinism.py`.
- **SchemeModule contract is grep-visible and isinstance-checkable.** `src/uk_subsidy_tracker/schemes/__init__.py` declares a `@runtime_checkable typing.Protocol` with `DERIVED_DIR` + five callables; `isinstance(cfd, SchemeModule)` returns True. The duck-typed contract means every future scheme module (RO, FiT, SEG, Constraint Payments, Capacity Market, Balancing Services, Grid Socialisation) has one structural surface to implement with zero inheritance machinery.
- **methodology_version column on every derived row (GOV-02 substrate).** Every Parquet row carries `methodology_version: "0.1.0"` propagated from `counterfactual.METHODOLOGY_VERSION`; Plan 04-04's `manifest.json` will surface it at the top-level `methodology_version` key. A disputed figure becomes traceable to the methodology revision that produced it. GOV-02 closes when Plan 04-04 exposes the column upstream.
- **Determinism discipline holds without gymnastics.** No `datetime.now()`, no `time.time()`, no `random.*` anywhere in `src/uk_subsidy_tracker/schemes/cfd/` (grep returns only a docstring comment reinforcing the rule). The `forward_projection.py` "current year" anchor comes from `int(gen['Settlement_Date'].max().year)` — the latest data point, not the wall clock. Content-identity test passes 10/10.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pydantic row schemas + SchemeModule Protocol + determinism RED test** — `6b695cd` (test)
2. **Task 2: Implement schemes/cfd/ derived-layer builders — GREEN** — `e00a4f6` (feat)
3. **Task 3: Parquet-variant tests in test_schemas + test_aggregates (D-19 + D-20) + Rule-1 int64 year cast** — `1a0575f` (test)
4. **Task 4: CHANGES.md entry for derived layer + scheme contract + TEST-02/03/05 formalisation** — `79ccb2b` (docs)

**Test count:** 46 passed + 4 skipped → 54 passed + 4 skipped (+18 from Phase-4 Plan 03: 10 determinism + 5 parquet schemas + 3 parquet aggregates; zero regressions).

## Row Counts per Grain (rebuild envelope)

One rebuild of `cfd.rebuild_derived()` on the full CfD dataset produced (Plan 04-04 `validate()` check's reference envelope):

| Grain | Rows | Parquet bytes | Schema JSON bytes |
|---|---|---|---|
| `station_month.parquet` | 3,460 | 77,567 | 2,475 |
| `annual_summary.parquet` | 11 | 4,861 | 1,648 |
| `by_technology.parquet` | 52 | 4,727 | 1,277 |
| `by_allocation_round.parquet` | 33 | 5,356 | 1,564 |
| `forward_projection.parquet` | 68 | 8,372 | 2,111 |
| **Total** | **3,624** | **100,883** | **9,075** |

Rebuild time: **0.74 seconds** on the full raw dataset (M3 MacBook Pro, Python 3.13.11). Gives Plan 04-05's `refresh.yml` workflow a cheap budget — the 5-minute daily cron has 400× slack over the derivation step.

## Files Created / Modified

### Created
- `src/uk_subsidy_tracker/schemas/__init__.py` — 21 lines; barrel re-exporting `StationMonthRow`, `AnnualSummaryRow`, `ByTechnologyRow`, `ByAllocationRoundRow`, `ForwardProjectionRow`, `emit_schema_json`.
- `src/uk_subsidy_tracker/schemas/cfd.py` — 185 lines; five `BaseModel` subclasses with Field-level `description` + `json_schema_extra={"dtype": ..., "unit": ...}` on every field, `methodology_version: str` last on every row. `emit_schema_json(model, path)` writes sort_keys + LF-newline JSON Schema siblings.
- `src/uk_subsidy_tracker/schemes/__init__.py` — 60 lines; `@runtime_checkable` `SchemeModule` `typing.Protocol` (ARCHITECTURE §6.1 verbatim).
- `src/uk_subsidy_tracker/schemes/cfd/__init__.py` — 131 lines; five `SchemeModule` callables (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`) + `DERIVED_DIR`. `validate()` returns a list of warnings across three checks (row-count drift, null technology, methodology_version agreement).
- `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` — 153 lines; `build_station_month(output_dir)` + loader-owned `station_month_schema` pandera DataFrameSchema + shared `_write_parquet(df, path)` helper (D-22 pinned).
- `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` — 200 lines; three rollup builders re-reading `station_month.parquet` (D-03). `build_annual_summary` joins daily `compute_counterfactual()` output; `build_by_allocation_round` pulls `Avoided_GHG_tonnes_CO2e` from raw LCCC.
- `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` — 128 lines; hoisted from `plotting/subsidy/remaining_obligations.py:80-124`. Deterministic current-year anchor.
- `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` — 64 lines; SHA-256 `upstream_changed()` against .meta.json sidecars; thin `refresh()` wrapper (Plan 04-05 orchestrates full workflow).
- `tests/test_determinism.py` — 76 lines; 10 cases (5 content + 5 writer-identity) parametrised across grains.
- `.planning/phases/04-publishing-layer/04-03-SUMMARY.md` (this file).

### Modified
- `.gitignore` — appended `data/derived/` under a Phase-4 comment block.
- `tests/test_schemas.py` — 83 → 131 lines; preserved 5 raw-CSV tests + module-scoped `derived_dir` fixture + parametrised `test_parquet_grain_schema`. Grep-visible discipline: every row model validated per row on read-back.
- `tests/test_aggregates.py` — 57 → 131 lines; preserved 2 raw scaffolding tests + module-scoped `derived_dir` + 4 read fixtures + 3 row-conservation tests (`annual_vs_station_month`, `by_tech_vs_annual`, `by_round_vs_annual`) — all exact-equality via `pd.testing.assert_series_equal`.
- `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` — Rule-1 auto-fix during Task 3: `sm['month_end'].dt.year.astype('int64')` in all three rollup builders, `daily.index.year.astype('int64')` in the counterfactual join, and `gen['Settlement_Date'].dt.year.astype('int64')` in the avoided-CO2 join — producing Parquet now agrees with the int64 year dtype declared by the Pydantic row models.
- `CHANGES.md` — [Unreleased] `### Added` gains bullets for `schemas/`, `schemes/__init__.py`, `schemes/cfd/`, `test_determinism.py`, Parquet variants in test_schemas + test_aggregates, and the `data/derived/` gitignore. `### Changed` notes `methodology_version` propagation (GOV-02). No `## Methodology versions` entry — constant stays at `"0.1.0"` per CONTEXT D-12.

## Protocol Conformance Smoke

```
$ uv run python -c "from uk_subsidy_tracker.schemes import cfd, SchemeModule; assert isinstance(cfd, SchemeModule), 'cfd does not satisfy SchemeModule'; print('isinstance OK')"
isinstance OK
```

`cfd` module has `DERIVED_DIR: Path` and the five required callables with matching signatures. Every future scheme module (`ro`, `fit`, `seg`, ...) will fail this smoke if it omits any callable.

## TDD Self-Check (Determinism Tripwire)

Confirmed via a deliberate tamper: rebuild twice, then double `cfd_payments_gbp` in one `annual_summary.parquet`; `pq.read_table(tmp1).equals(pq.read_table(tmp2))` returns `False`. The `test_parquet_content_identical[annual_summary]` assertion would surface this as:

```
Parquet content drift for annual_summary — same raw input should produce
identical rows. If intentional (methodology change), bump
METHODOLOGY_VERSION (currently '0.1.0') and add a CHANGES.md `## Methodology versions` entry.
```

This is the intended remediation hook from RESEARCH §Pattern 1 — the tripwire directs the PR author to the three-step methodology-bump discipline.

## Validate() Output

Against the canonical `data/derived/cfd/` output of a fresh rebuild:

```
1 warning:
  validate: latest-year row count drift > 10% (655 -> 266)
```

Expected: 2026 is a partial year (4 months of settlement data as of 2026-04-22), so the count is structurally lower than full-year 2025. This is a **benign calendar-edge warning**, not a data-quality issue. Plan 04-06 will add a partial-year guard (either `year < current_year_anchor` filter, or `partial_year` flag on the last row) to silence this specific case while preserving the drift check for completed-year-to-completed-year transitions.

## Column-Availability Result (Step 1.0 Pre-flight)

`Market_Reference_Price_GBP_Per_MWh` **was** present in `data/raw/lccc/actual-cfd-generation.csv` (confirmed via `head -1 | tr ',' '\n'`). **No columns dropped** from the Pydantic row models vs. the plan's interface sketch. StationMonthRow retains all 9 fields as authored.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] KeyError 'date' in build_annual_summary**
- **Found during:** Task 2, first rebuild_derived() run
- **Issue:** `daily = pd.concat([daily_gen, cf_daily.reindex(...)], axis=1)` followed by `daily.reset_index().rename(columns={"index": "date"})` — concat preserves `daily_gen`'s index *name* (`Settlement_Date`), so `reset_index().rename(columns={"index": "date"})` silently no-ops and the subsequent `daily["date"].dt.year` raises KeyError.
- **Fix:** Use `daily.index.year` directly rather than renaming. Works because the index is already datetime-typed from `daily_gen`'s groupby.
- **Files modified:** `src/uk_subsidy_tracker/schemes/cfd/aggregation.py`
- **Commit:** `e00a4f6`

**2. [Rule 1 — Bug] int32-vs-int64 year dtype mismatch in rollup Parquets**
- **Found during:** Task 3, `test_annual_vs_station_month_parquet` failing with "Series.index are different ... Attribute dtype are different [left]: int32 [right]: int64"
- **Issue:** Pandas' `dt.year` returns int32 by default, but the Pydantic row models (`AnnualSummaryRow.year`, `ByTechnologyRow.year`, `ByAllocationRoundRow.year`) declare `json_schema_extra={"dtype": "int64"}`. Produced Parquet carried int32 `year`, disagreeing with its declared schema.
- **Fix:** Cast `year` to `int64` in all three rollup builders at the point of computation (`sm['month_end'].dt.year.astype('int64')`). Test fixture also casts in `station_month` fixture so both sides of `pd.testing.assert_series_equal` agree.
- **Files modified:** `src/uk_subsidy_tracker/schemes/cfd/aggregation.py`, `tests/test_aggregates.py`
- **Commit:** `1a0575f`

### Rule-Rejected Alternatives

- Considered using `pd.Timestamp.now().year` as the current-year anchor in `forward_projection.py` (as the chart source file does). Rejected because it breaks D-21 content-identity (rebuild at 23:59 vs 00:01 Dec 31/Jan 1 would produce different Parquet). Replaced with `int(gen['Settlement_Date'].max().year)`. **Not a deviation** — plan explicitly warned against any clock-reading source under Pitfall 1.

## Issues Encountered

- **Plan's draft aggregation.py concat sketch had a latent bug** — the `reset_index().rename(columns={"index": "date"})` pattern fails when the Series index already has a name. Fix was trivial (use `.index.year` directly) but spotted only when the determinism test ran. Documented under Deviations #1 so Phase 5 doesn't copy the bug forward.
- **Python bool/int subclass + pandera strict=False interaction** — `methodology_version` is a str column; no issue, but note: pandera with `strict=False` will accept extra columns at schema-validation time. For this plan that's fine (column order already enforced via `df[list(Row.model_fields.keys())]` before validation), but Phase 5+ should know the loose-strict posture is intentional.

## User Setup Required

None — no external service configuration required for this plan. Data is local, derivation is pure, tests run in-process.

## Verification Results

**Plan `<success_criteria>` block:**

| Criterion | Result |
|---|---|
| `cfd.rebuild_derived()` produces 5 Parquet + 5 schema.json siblings under `data/derived/cfd/` (or passed output_dir) | PASS (both paths verified; tmp and canonical) |
| TEST-02 formalised: Parquet-variant tests in `tests/test_schemas.py` | PASS (5 parametrised cases green) |
| TEST-03 formalised: Parquet row-conservation tests in `tests/test_aggregates.py` | PASS (3 cases green, exact equality) |
| TEST-05 formalised: `tests/test_determinism.py` 10/10 | PASS (5 content + 5 writer-identity) |
| `SchemeModule` Protocol declared + `isinstance(cfd, SchemeModule)` | PASS |
| `methodology_version` column on every derived row | PASS (visible in each `<grain>.schema.json`) |
| Full pytest suite green | PASS (54 passed + 4 skipped) |
| Chart generation + mkdocs-strict build still work (D-02) | PASS (14/14 OK; mkdocs exit 0) |
| `.gitignore` excludes `data/derived/` | PASS (`grep -q "^data/derived/" .gitignore` exits 0) |
| `CHANGES.md` records derived layer + scheme contract + formalised TEST-02/03/05 | PASS (all grep checks green) |

**Plan `<verification>` block (all automated):**

| Check | Result |
|---|---|
| `uv run pytest tests/test_determinism.py -v` — 10 passed | PASS |
| `uv run pytest tests/test_schemas.py -v` — ≥10 passed (5 raw + 5 Parquet) | PASS (10 passed) |
| `uv run pytest tests/test_aggregates.py -v` — 5 passed (2 raw + 3 Parquet) | PASS (5 passed) |
| `uv run pytest tests/` — full suite green | PASS (54 passed + 4 skipped) |
| `isinstance(cfd, SchemeModule)` | PASS |
| `uv run python -m uk_subsidy_tracker.plotting` | PASS (14/14 OK) |
| `uv run mkdocs build --strict` | PASS (exit 0) |
| No non-determinism sources (`! grep datetime.now\|time.time\|random.` in `src/uk_subsidy_tracker/schemes/cfd/`) | PASS (only a docstring comment reinforcing the rule) |

**Per-task acceptance criteria:** all four tasks hit 100% of their declared criteria (exhaustive grep + test-run check).

## Next Plan Readiness

**Plan 04-04 (publishing-layer manifest) is fully unblocked.** It can now:
- Read `methodology_version` from any derived Parquet's `methodology_version` column or from `cfd.METHODOLOGY_VERSION` import.
- Read per-table schemas from either the Pydantic models (`model.model_json_schema(mode='serialization')`) or the pre-emitted `<grain>.schema.json` siblings.
- Compute manifest row counts and byte sizes from `pq.read_metadata()` on each Parquet.
- Stamp the canonical `DERIVED_DIR` path (`data/derived/cfd/`) on manifest entries.

**Plan 04-05 (workflows refresh+deploy) has its orchestration primitives:**
- `cfd.upstream_changed()` → SHA-compare dirty check
- `cfd.refresh()` → thin wrapper (Plan 04-05 orchestrates the full workflow)
- `cfd.rebuild_derived()` → full derivation (0.74s)
- `cfd.regenerate_charts()` → delegate to `uk_subsidy_tracker.plotting.__main__.main`
- `cfd.validate()` → health checks on derived output

**Plan 04-06 (docs + benchmark floor) has real Parquet files to snippet against.** `docs/data/index.md` journalist-how-to blocks can call `pq.read_table("data/derived/cfd/station_month.parquet")` on any reader's machine after `git clone + uv sync + python -c "from uk_subsidy_tracker.schemes import cfd; cfd.rebuild_derived()"` — the single-command reproduction promise of the project is now structurally testable.

**No known blockers** for the remaining three Phase-4 plans.

## Self-Check: PASSED

- [x] `src/uk_subsidy_tracker/schemas/__init__.py` exists
- [x] `src/uk_subsidy_tracker/schemas/cfd.py` exists
- [x] `src/uk_subsidy_tracker/schemes/__init__.py` exists (contains `class SchemeModule`, `@runtime_checkable`)
- [x] `src/uk_subsidy_tracker/schemes/cfd/__init__.py` exists (contains `def rebuild_derived`, `DERIVED_DIR`)
- [x] `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exists (`def build_station_month`)
- [x] `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` exists (three builders)
- [x] `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` exists (`def build_forward_projection`)
- [x] `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` exists (`def upstream_changed`, `def refresh`)
- [x] `tests/test_determinism.py` exists
- [x] `tests/test_schemas.py` modified (contains `test_parquet_grain_schema`)
- [x] `tests/test_aggregates.py` modified (contains `test_annual_vs_station_month_parquet` and two sibling tests)
- [x] `.gitignore` modified (contains `data/derived/`)
- [x] `CHANGES.md` modified (all required grep signals present)
- [x] Commit `6b695cd` in git log (Task 1: test RED)
- [x] Commit `e00a4f6` in git log (Task 2: feat GREEN)
- [x] Commit `1a0575f` in git log (Task 3: test Parquet variants + Rule-1 int64 fix)
- [x] Commit `79ccb2b` in git log (Task 4: docs CHANGES)
- [x] 5/5 Parquet + 5/5 schema.json siblings under `data/derived/cfd/`
- [x] Full test suite: 54 passed + 4 skipped
- [x] `uv run python -m uk_subsidy_tracker.plotting` — 14/14 OK
- [x] `uv run mkdocs build --strict` — exit 0

---
*Phase: 04-publishing-layer*
*Plan: 03 (Wave 3 — derived-layer CfD scheme)*
*Completed: 2026-04-22*
