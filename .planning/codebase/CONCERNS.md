# Codebase Concerns

**Analysis Date:** 2026-04-21

## Tech Debt

**Obsolete chart files not yet deleted:**
- Issue: Two chart modules marked for removal in ARCHITECTURE.md §5.2 still exist in codebase: `scissors.py` (CUT verdict) and `bang_for_buck_old.py` (DELETE verdict). These are dead code consuming maintenance attention.
- Files: `src/cfd_payment/plotting/subsidy/scissors.py`, `src/cfd_payment/plotting/subsidy/bang_for_buck_old.py`
- Impact: Git status noise; potential confusion about which charts are production-ready; deployment includes unused code
- Fix approach: Delete both files immediately. Per ARCHITECTURE.md §5.2, scissors is "strictly dominated by `cfd_dynamics`" and bang_for_buck_old is "obsolete version." Git history preserves them.

**Incomplete chart triage execution:**
- Issue: ARCHITECTURE.md §5.2 documents a full chart triage outcome (9 PRODUCTION, 4 DOCUMENTED, 1 CUT, 1 DELETE), but this is a draft decision document. Seven charts marked "PROMOTE → PRODUCTION" require documentation pages that do not yet exist.
- Files: Triage verdicts in `ARCHITECTURE.md` §5.2 not yet reflected in docs structure
- Impact: Chart status is ambiguous; unclear which charts have documented methodology; risk of deploying undocumented PRODUCTION charts
- Fix approach: ARCHITECTURE.md §11 phase P2 ("Chart triage execution") is planned. This is expected work, not a bug.

**Documentation structure mismatch with ARCHITECTURE:**
- Issue: ARCHITECTURE.md (draft §5.5) prescribes a theme-page structure (`docs/themes/<theme>/index.md` with narrative + embedded charts, plus `methodology.md`). Current `docs/` has obsolete structure with deleted `technical-details/` subdirectory and incomplete chart nav in `mkdocs.yml`.
- Files: `mkdocs.yml` (lines 24–31 still reference deleted `technical-details/gas-counterfactual.md`), `docs/index.md`, deleted `docs/technical-details/` entries show in git status
- Impact: `mkdocs build --strict` will fail on broken references; broken links on live site if deployed
- Fix approach: Rebuild `docs/` directory structure per §5.5 template and update `mkdocs.yml` navigation accordingly. This is phase P2 work.

**Missing provenance metadata for derived data:**
- Issue: ARCHITECTURE.md §9.1 defines a provenance contract: every derived Parquet must carry source file hashes, retrieval timestamps, and pipeline version. No implementation of this metadata pipeline exists.
- Files: No `src/uk_subsidy_tracker/publish/manifest.py` or provenance tracking in current codebase
- Impact: Downstream users (academics, journalists) cannot audit numbers back to raw sources; violates "national resource" governance model
- Fix approach: Phase P3 ("Publishing layer") implements this. Create sidecar `<filename>.meta.json` files alongside Parquet and CSV exports with source provenance.

## Known Bugs

**LCCC data loading assumes exact column schema match:**
- Symptoms: If LCCC upstream changes column names, types, or adds columns without warning, data loading will fail silently or raise pandera validation errors at chart generation time
- Files: `src/cfd_payment/data/lccc.py` (lines 36–74 define pandera schemas), `src/cfd_payment/data/lccc.py::load_lccc_dataset()` (lines 105–114)
- Trigger: Any upstream LCCC schema change; no monitoring for this
- Workaround: Manual inspection of raw CSV before chart generation; tests only run if data is already downloaded
- Root cause: Pandera validation is defensive but happens post-download; no sidecar versioning of the upstream schema

**Test suite does not catch upstream data publication failures:**
- Symptoms: If LCCC data portal goes offline or changes UUID scheme, tests pass (they skip download with `@pytest.mark.skip`), but pipeline breaks during daily CI
- Files: `tests/data/test_lccc.py` (line 12: `@pytest.mark.skip(reason="hits live wwebsite")`)
- Trigger: `refresh.yml` CI runs `download_lccc_datasets()` without pre-checks; failure is discovered at deploy time
- Root cause: Live dependency on LCCC API with no offline validation; skipped tests hide brittleness

**ONS gas price data loading path hardcoded:**
- Symptoms: `load_gas_price()` function exists but implementation is not shown; unclear if it handles missing data, retries, or version pinning
- Files: `src/cfd_payment/data/ons_gas.py` (imported but not examined)
- Impact: Silent failures if ONS URL changes or CSV schema drifts
- Fix approach: Code review of ons_gas.py; add sidecar schema versioning

**Chart output directory created without validation:**
- Symptoms: `ChartBuilder` and `save_chart()` assume `OUTPUT_DIR` exists and is writable. No exception handling for permission errors or missing parent directories.
- Files: `src/cfd_payment/__init__.py` (lines 4–5: `OUTPUT_DIR = PROJECT_ROOT / "docs" / "charts" / "html"`), `src/cfd_payment/plotting/chart_builder.py` (line 58: `self.output_dir = output_dir or OUTPUT_DIR`)
- Trigger: Run charts with a read-only output path or no parent directory
- Workaround: Ensure directory exists before running charts
- Fix approach: `mkdir(parents=True, exist_ok=True)` in chart generation entry point

## Security Considerations

**No sensitive data identified:**
- All data sources are public government datasets (LCCC, ONS, Ofgem, NESO, UK ETS).
- No API keys, OAuth tokens, or authentication secrets in scope.
- `.env` file is not used; no env-variable injection risk.

**HTTP requests to upstream without timeout or retry budgets:**
- Risk: DDoS attacks or network hangs could block the daily CI pipeline indefinitely
- Files: `src/cfd_payment/data/lccc.py::download_lccc_dataset()` (line 96: `requests.get()` with no timeout)
- Recommendation: Add `timeout=30` to all `requests.get()` calls; implement exponential backoff for transient failures

**No checksum validation for downloaded datasets:**
- Risk: Upstream data corruption or man-in-the-middle attack undetected
- Files: `src/cfd_payment/data/lccc.py::download_lccc_dataset()` (lines 95–100: downloads but does not validate)
- Recommendation: ARCHITECTURE.md §4.1 mandates sidecar `.meta.json` with SHA-256. Implement this and fail fast if hash mismatches.

## Performance Bottlenecks

**No identified performance issues at current scale:**
- CfD dataset is small (~500k rows); charts generate in <1s.
- Daily refresh completes well within GitHub Actions free tier 30-min limit.
- DuckDB / Parquet not yet in use (ARCHITECTURE.md describes plan but not current implementation).

**Future scaling concern (not a blocker):**
- When multi-scheme data is loaded (RO, FiT, constraints, etc.), memory footprint of loading multiple large CSVs into pandas will grow. ARCHITECTURE.md §3 nominates DuckDB to replace pandas for heavy aggregations. No blocker yet.

## Fragile Areas

**Chart generation is coupled to exact LCCC data structure:**
- Files: Every file in `src/cfd_payment/plotting/subsidy/` and `src/cfd_payment/plotting/cannibalisation/` assumes LCCC column names and presence of specific fields (e.g., `Strike_Price_GBP_Per_MWh`, `CFD_Generation_MWh`, `Allocation_round`)
- Why fragile: If LCCC renames a column or removes data, the entire chart regeneration pipeline fails partway through with unhelpful pandas KeyError
- Safe modification: Add a data validation layer that checks expected columns exist before processing. Use pandera to enforce at load time and fail fast.
- Test coverage: No column-existence tests. Add `test_lccc_schema.py` with assertions on required columns.

**Counterfactual formula is hardcoded without version tracking:**
- Files: `src/cfd_payment/counterfactual.py` (lines 12–46: constants and hardcoded carbon prices)
- Why fragile: If a change to CCGT_EFFICIENCY or carbon price assumptions is made, no record of when/why/how previous versions differed. ARCHITECTURE.md §9.4 mandates methodology versioning but it's not implemented.
- Safe modification: Extract counterfactual formula to a timestamped class. Version each assumption. Test that known benchmarks (REF, Turver, etc.) match.
- Test coverage: `test_counterfactual.py` promised in ARCHITECTURE.md §11 P1 does not exist. This is phase P1 work.

**Gas price data loading is opaque:**
- Files: `src/cfd_payment/data/ons_gas.py` (not examined; called by counterfactual)
- Why fragile: Unclear if it handles missing dates, interpolation, or source versioning
- Safe modification: Code review ons_gas.py; add docstring specifying assumptions and edge cases
- Test coverage: `tests/data/test_ons.py` exists but incomplete

**Chart colors are defined in three places:**
- Files: `src/cfd_payment/plotting/colors.py` (shared), `src/cfd_payment/plotting/utils.py::TECHNOLOGY_COLORS` (duplicate), `src/cfd_payment/plotting/subsidy/bang_for_buck_old.py::ROUND_COLORS` (third copy)
- Why fragile: Inconsistency risk; ARCHITECTURE.md §13.3 defines canonical colors but they're scattered
- Safe modification: Centralize all colors in `src/cfd_payment/plotting/colors.py`. Import everywhere. No duplicates.
- Test coverage: None; color changes are undetected until chart review

**ThemeBuilder and dark theme setup is implicit:**
- Files: `src/cfd_payment/plotting/chart_builder.py::ChartBuilder.__init__()` (line 61: `register_cfd_dark_theme()` called automatically)
- Why fragile: If theme registration fails, it happens at chart build time, not import time
- Safe modification: Move theme registration to module level in `__init__.py` or add explicit setup function. Fail fast.

## Scaling Limits

**Single-process data pipeline limits monthly refresh window:**
- Current capacity: Daily refresh runs sequentially; assumes data download + all chart generation fits in <30 minutes
- Limit: When RO, FiT, constraints, capacity market, and balancing modules are added (per ARCHITECTURE.md §11 P4–P9), sequential pipeline may exceed GitHub Actions timeout
- Scaling path: Implement ARCHITECTURE.md §7.3 dirty-check (skip rebuilds for unchanged sources). Use parallel task groups in GitHub Actions for scheme-independent chart builds.

## Dependencies at Risk

**pandera validation is strict but unhelpful on failure:**
- Risk: Pandera raises opaque errors on schema mismatch; no guidance on which columns are missing/renamed
- Impact: Chart generation fails with cryptic traceback
- Recommendation: Wrap pandera validation in a try-except that prints a diagnostic message listing expected vs actual columns

**Plotly is pinned without upper bound:**
- Risk: If a Plotly 7.x version is released and introduces breaking API changes, chart generation breaks
- Files: `pyproject.toml` (line 14: `plotly` with no version constraint)
- Recommendation: Pin to `plotly>=6.0,<7.0` to prevent silent breakage

**mkdocs-material theme is pinned loosely:**
- Risk: Theme updates can change HTML structure, breaking custom CSS or assumptions
- Files: `pyproject.toml` (line 9: `mkdocs-material>=9.7.6`)
- Recommendation: Pin to `mkdocs-material>=9.7.6,<10.0` for safety; test after updates

## Missing Critical Features

**No automated upstream monitoring:**
- Problem: If LCCC, Ofgem, or ONS change their data schema or go offline, the pipeline fails at daily CI. No alerting.
- Blocks: Cannot detect upstream issues early; journalists/academics discover problems when they check the site
- Recommendation: Add a health-check step in CI that validates upstream schema before downloading. Post alerts to GitHub Issues on failure.

**No data provenance headers in CSV/Parquet exports:**
- Problem: Published datasets lack source attribution, retrieval timestamp, and methodology version
- Blocks: Academic citations cannot trace numbers to original sources; violates ARCHITECTURE.md §9.1 governance model
- Recommendation: Phase P3 ("Publishing layer") implements this. Build `manifest.json` with metadata.

**No test benchmarks against external sources:**
- Problem: ARCHITECTURE.md §11 P1 promises benchmarks against REF, Turver, Ofgem within documented tolerance. These tests do not exist.
- Blocks: Cannot detect systematic errors or divergence from known aggregates
- Recommendation: Phase P1 creates `tests/test_benchmarks.py` with external benchmark comparisons

## Test Coverage Gaps

**Untested areas - counterfactual formula:**
- What's not tested: The gas counterfactual formula (CCGT efficiency, carbon cost, O&M, monthly averaging) is implemented but not validated
- Files: `src/cfd_payment/counterfactual.py`, `src/cfd_payment/data/ons_gas.py` (missing test file)
- Risk: Changes to CCGT_EFFICIENCY or carbon prices propagate to all charts without validation
- Priority: High — this is phase P1 work (ARCHITECTURE.md §11)

**Untested areas - chart aggregation logic:**
- What's not tested: Monthly and annual rollups in chart generation (sum, weighted average, cumsum) are unvalidated
- Files: `src/cfd_payment/plotting/subsidy/cfd_dynamics.py::_prepare()` (lines 32–66, no test)
- Risk: Aggregation errors silently propagate to published numbers
- Priority: High

**Untested areas - data loading edge cases:**
- What's not tested: Missing dates, NaN handling, zero-generation rows, negative payments (clawback scenarios)
- Files: `src/cfd_payment/data/` (load functions lack edge-case tests)
- Risk: Rare data patterns (e.g., wind farm goes offline mid-month) produce incorrect charts
- Priority: Medium

**No determinism tests:**
- What's not tested: ARCHITECTURE.md §11 P1 promises `test_determinism.py` proving "identical input → byte-identical Parquet output." Does not exist.
- Files: No `tests/test_determinism.py`
- Risk: Parquet files are not reproducible; breaks academic citability and version comparison
- Priority: Medium (blocked on Parquet implementation)

---

*Concerns audit: 2026-04-21*
