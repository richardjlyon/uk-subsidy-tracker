# Phase 2: Test & Benchmark Scaffolding - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship the test-class scaffolding, CI workflow, and methodology-versioning mechanism that make every subsequent scheme phase testable and auditable.

In scope:
- `tests/test_counterfactual.py` pins the gas counterfactual formula (TEST-01).
- `tests/test_schemas.py` validates current raw CSV sources via pandera (pre-Parquet scaffolding variant; grows into Parquet checks in Phase 4).
- `tests/test_aggregates.py` in-memory row-conservation checks on the current CfD pipeline (pre-Parquet scaffolding variant; grows into Parquet checks in Phase 4).
- `tests/test_benchmarks.py` reconciles CfD totals against LCCC self-reconciliation (mandatory floor) + regulator-native external anchors located by the researcher (TEST-04).
- `.github/workflows/ci.yml` runs pytest on push to `main` + pull_request (TEST-06).
- `counterfactual.py` carries `METHODOLOGY_VERSION`; `CHANGES.md` `## Methodology versions` section is seeded with the initial entry (GOV-04).
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` traceability updates to reflect TEST-02/03/05 moving to Phase 4 (see D-04).

Out of scope (belongs to later phases):
- `tests/test_determinism.py` — Phase 4 (Parquet byte-identity is meaningless without Parquet output).
- Parquet-variant schema + aggregate checks — Phase 4 adds them to the same files.
- Daily-refresh CI workflow — Phase 4 (GOV-03).
- `mkdocs build --strict` CI gate — Phase 3 restructures docs; gating now would thrash.
- ruff / pyright / pre-commit gates — Phase 3+ polish.
- Multi-scheme benchmarks (RO/FiT/Constraints/etc.) — later scheme phases.

</domain>

<decisions>
## Implementation Decisions

### Test-class scope — pre-Parquet interpretation of TEST-02/03/05

- **D-01:** TEST-02 (`tests/test_schemas.py`) ships as pandera validation of the current raw CSV sources (LCCC generation, LCCC portfolio, Elexon AGWS, Elexon system prices, ONS gas SAP). Uses the existing `lccc_generation_schema` / `lccc_portfolio_schema` patterns; adds new schemas for Elexon and ONS where absent. File grows into Parquet-schema variants in Phase 4.
- **D-02:** TEST-03 (`tests/test_aggregates.py`) ships as in-memory pandas row-conservation assertions on the current CfD pipeline. Invariant: `sum(payment by year) == sum(payment by year × technology)` across the LCCC daily → monthly → yearly aggregation chain. File grows into Parquet-aggregate variants in Phase 4.
- **D-03:** TEST-05 (`tests/test_determinism.py`) is fully deferred to Phase 4. **No file is created in Phase 2.** Byte-identical Parquet output has no meaning without Parquet writes, which arrive in Phase 4.
- **D-04:** REQ-ID bookkeeping — update `.planning/REQUIREMENTS.md` traceability rows so **TEST-02, TEST-03, TEST-05 move from Phase 2 → Phase 4**. Update `.planning/ROADMAP.md` Phase 2 requirements list (drop TEST-02/03/05), Phase 4 requirements list (add TEST-02/03/05), and Phase 2 success criterion 1 (reword from "all five test classes present and passing" to **"four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`"**). Phase 2 still ships pre-Parquet variants of test_schemas / test_aggregates as useful-today scaffolding — they do not formally satisfy TEST-02/TEST-03 until their Parquet variants ship in Phase 4.

### Benchmark format (TEST-04)

- **D-05:** Benchmark values live in `tests/fixtures/benchmarks.yaml`. Structure per entry: `source`, `year`, `value_gbp_bn`, `url`, `retrieved_on`, `notes`, `tolerance_pct`. A Pydantic model validates the YAML on load. Rationale: cleaner PR diffs than inline dicts, surfaces retrieval metadata (provenance-adjacent), and matches the project's "commit the data" discipline.
- **D-06:** Tolerances live as **named constants** in `tests/test_benchmarks.py` (e.g., `LCCC_SELF_TOLERANCE_PCT = 0.1`, `DESNZ_ANNUAL_TOLERANCE_PCT = 5.0`) with docstring rationale explaining *why* the tolerance is what it is (different CPI basis, scheme-subset mismatch, retrieval-year drift, etc.). Tolerance is a versioned decision, not a knob; divergence is self-documenting in test source.
- **D-07:** A tolerance bump requires a `CHANGES.md` entry under `## Methodology versions` explaining the rationale. PR review alone is insufficient. Enforced by convention + reviewer check; aligns with GOV-04 discipline.
- **D-08:** **Ben Pile and Dav Turver are NOT canonical benchmark sources.** They were commentator references from project-scoping conversations, surfaced in ARCHITECTURE.md / REQUIREMENTS.md language. Phase 2 canon is UK regulator / audit-grade publications. The `gsd-phase-researcher` agent (spawned next by `/gsd-plan-phase 2`) locates specific publications + retrieval URLs.
- **D-09:** Researcher source prioritisation, in order:
  1. **LCCC's own published annual summary totals** — floor benchmark (our pipeline reads LCCC raw data; LCCC also publishes aggregate yearly totals in quarterly/annual reports).
  2. **Ofgem CfD levy spend transparency + CfD budget dashboards** — supplier-levy independent view.
  3. **DESNZ / BEIS CfD Allocation Round summaries + Energy Trends** — government-side contract/capacity/spend anchors.
  4. **NAO + House of Commons Library + Climate Change Committee** — independent scrutineers; audit-grade but lower update cadence.
- **D-10:** **LCCC self-reconciliation is a mandatory red-line check.** `test_benchmarks.py` always includes `abs(our_yearly_total_gbp - lccc_published_yearly_total_gbp) / lccc_published_yearly_total_gbp <= 0.001` (0.1%). If our pipeline diverges from LCCC's own published aggregate, that is a **pipeline bug**, not a methodology divergence. Always green, always included, never parameterised away.
- **D-11:** **Fallback posture** if the researcher cannot locate useable external anchors beyond LCCC: ship `test_benchmarks.py` with the LCCC floor check only. External anchors land as follow-ups in Phase 3/4 as they are located. Phase 2 does **not** block on external anchor availability. ROADMAP Phase 2 success criterion 3 is re-anchored from "documents divergence from Ben Pile (2021 + 2026), REF subset, and Turver aggregate" to **"documents divergence from LCCC self-reconciliation and any regulator-native external sources the researcher located."**

### Claude's Discretion

- **CI workflow shape (TEST-06)** — default: single-job GitHub Actions workflow at `.github/workflows/ci.yml`, triggered on `push` to `main` + `pull_request`, Python 3.12 only (the floor in `pyproject.toml`), using `astral-sh/setup-uv@v4` with built-in cache, running `uv sync --frozen` then `uv run pytest`. No ruff/pyright/mkdocs-strict gate in Phase 2 — Phase 3 can add them after the doc restructure. The planner MAY expand the matrix or add linters if the researcher surfaces a concern.
- **Methodology versioning (GOV-04) shape** — default: `METHODOLOGY_VERSION: str = "1.0.0"` as a module-level constant in `src/uk_subsidy_tracker/counterfactual.py`, returned as a column in the DataFrame produced by `compute_counterfactual()` so it flows into any Parquet derived in Phase 4 and into `manifest.json` via GOV-02. SemVer semantics: **patch** = tolerance / constant tweak with identical formula shape; **minor** = additive parameter (new input, old calls still work); **major** = formula-shape change (new/dropped term, changed unit convention). `CHANGES.md` seeds `## Methodology versions` → `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)` citing the constants + their sources.
- **Pin test mechanics** — `test_counterfactual.py` asserts `compute_counterfactual(known_inputs)["counterfactual_total"]` equals a hardcoded expected float to 4 decimal places. Any change to `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`, or `DEFAULT_CARBON_PRICES` fails the test and forces the PR author to simultaneously bump `METHODOLOGY_VERSION` and add a CHANGES.md entry. Sample inputs: a 2022 full-year slice (peak gas prices), a 2019 full-year slice (pre-crisis normal), plus a synthetic all-zeros input. Planner MAY refine sample inputs.
- **Benchmark YAML schema location** — default: Pydantic model co-located in `tests/fixtures/__init__.py` or `tests/conftest.py`. Planner decides.
- **`pyproject.toml` test-extras** — Phase 2 does not require adding `pyarrow` (determinism test deferred). `pyyaml` is already a project dependency; no dev-dep changes expected unless the researcher flags one.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative spec
- `ARCHITECTURE.md` §9.4 — Methodology versioning mechanism; defines the GOV-04 contract.
- `ARCHITECTURE.md` §9.6 — Five-class test table (Phase 2 ships four; Phase 4 adds the fifth and Parquet variants).
- `ARCHITECTURE.md` §11 P1 — Phase 2 entry/exit + deliverables (authoritative on "green CI on main, benchmark deltas documented").

### Roadmap + requirements
- `.planning/ROADMAP.md` Phase 2 — Success criteria (criterion 1 to reword per D-04; criterion 3 to re-anchor per D-11).
- `.planning/ROADMAP.md` Phase 4 — Requirements list receives TEST-02/03/05 per D-04.
- `.planning/REQUIREMENTS.md` — TEST-01, TEST-04, TEST-06, GOV-04 remain Phase 2; TEST-02/03/05 move to Phase 4 in the traceability table.
- `.planning/PROJECT.md` — Provenance non-negotiable, reproducibility principle, adversarial-proofing quality bar.
- `.planning/STATE.md` — Python 3.12 floor inherited from Phase 1; `CHANGES.md ## Methodology versions` hook already seeded.
- `.planning/phases/01-foundation-tidy/01-CONTEXT.md` — Package-rename decisions D-13/D-14/D-15 (imports are `uk_subsidy_tracker.*` throughout tests); atomic-commit discipline; CHANGES.md Keep-a-Changelog format.

### Codebase maps
- `.planning/codebase/TESTING.md` — Current test patterns, absent-file inventory, §9.6 target scope.
- `.planning/codebase/STACK.md` — pytest 9.0.3+, pandera 0.31+, pandas, uv.
- `.planning/codebase/CONVENTIONS.md` — Naming, import, style conventions tests must follow.
- `.planning/codebase/STRUCTURE.md` — Directory layout (tests/ mirrors src/uk_subsidy_tracker/).

### Files to modify
- `pyproject.toml` — verify `pytest>=9.0.3` in dev-deps; no new deps expected.
- `src/uk_subsidy_tracker/counterfactual.py` — add `METHODOLOGY_VERSION` constant; return it as a DataFrame column from `compute_counterfactual()`.
- `src/uk_subsidy_tracker/data/lccc.py` — existing pandera schemas reused by `test_schemas.py`; may need sibling schemas in `data/elexon.py` and `data/ons_gas.py`.
- `CHANGES.md` — fill `## Methodology versions` with `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)` and (under `[Unreleased]`) note the test + CI scaffolding additions.
- `.planning/ROADMAP.md` — Phase 2 success criterion 1 reword (four classes, not five); Phase 2 success criterion 3 re-anchor (LCCC + regulator-native, not Ben Pile / Turver); Phase 2 requirements list drops TEST-02/03/05; Phase 4 requirements list adds them.
- `.planning/REQUIREMENTS.md` — Traceability table rows for TEST-02, TEST-03, TEST-05 move from Phase 2 to Phase 4.

### Files to create
- `.github/workflows/ci.yml` — pytest-on-push workflow (TEST-06).
- `tests/test_counterfactual.py` — formula pin + METHODOLOGY_VERSION presence check (TEST-01 + part of GOV-04).
- `tests/test_schemas.py` — pandera validation of raw CSV sources (Phase 2 scaffolding; formal TEST-02 satisfied in Phase 4).
- `tests/test_aggregates.py` — in-memory row-conservation assertions (Phase 2 scaffolding; formal TEST-03 satisfied in Phase 4).
- `tests/test_benchmarks.py` — LCCC floor + any researcher-located external anchors (TEST-04).
- `tests/fixtures/benchmarks.yaml` — structured benchmark values with provenance.
- `tests/fixtures/__init__.py` OR extensions to `tests/conftest.py` — YAML loader + Pydantic validator for the benchmarks fixture (planner decides).

### External references
- GitHub Actions + uv integration — https://docs.astral.sh/uv/guides/integration/github/
- `astral-sh/setup-uv` action — https://github.com/astral-sh/setup-uv
- pandera DataFrame schema docs — https://pandera.readthedocs.io/
- pytest 9.x docs — https://docs.pytest.org/en/stable/
- Keep-a-Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/ (already a canonical ref from Phase 1)
- LCCC data portal — https://www.lowcarboncontracts.uk/data-portal (researcher confirms exact annual-totals page)
- Ofgem CfD transparency — https://www.ofgem.gov.uk/environmental-and-social-schemes/contracts-difference-cfd (researcher confirms)
- DESNZ Energy Trends — https://www.gov.uk/government/collections/energy-trends (researcher confirms section + publication cadence)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`src/uk_subsidy_tracker/data/lccc.py`** — `lccc_generation_schema` and `lccc_portfolio_schema` already validate CSVs on load via pandera; `test_schemas.py` reuses them directly. Pattern is `schema.validate(df)` and assert no exception.
- **`LCCCAppConfig`** (Pydantic + PyYAML) — reference idiom for the benchmarks.yaml loader.
- **`src/uk_subsidy_tracker/counterfactual.py`** — formula, constants, and `compute_counterfactual()` exist. Phase 2 adds `METHODOLOGY_VERSION` and a pinning test; the formula itself is NOT refactored.
- **`tests/data/test_lccc.py` + `tests/data/test_ons.py`** — established patterns: flat functions (no classes), module-level imports from package root, `@pytest.mark.skip(reason="hits live website")` for network-dependent tests.
- **Raw CSV + XLSX files already committed** in `data/` (LCCC generation, LCCC portfolio, Elexon AGWS, Elexon system prices, ONS gas SAP) — CI loads them directly without network.

### Established Patterns
- Snake-case test file naming (`test_<module>.py`), flat test functions, no shared fixtures yet.
- Absolute imports from `uk_subsidy_tracker.*` throughout tests (no relative imports).
- `@pytest.mark.skip(reason=...)` for network or environment-dependent tests (NOT for Phase-4-deferred tests — those are not authored in Phase 2 at all).
- `pyproject.toml` declares `requires-python = ">=3.12"` — CI matrix matches.
- Atomic commit discipline (per Phase 1 D-16): each test file, the CI workflow, the benchmarks fixture, and the methodology version bump land as separate commits.

### Integration Points
- **`src/uk_subsidy_tracker/data/__init__.py`** re-exports loaders (`load_lccc_dataset`, `load_gas_price`, etc.); tests import from `uk_subsidy_tracker.data`, not from submodule paths.
- **`CHANGES.md` `## Methodology versions` section header** already exists (seeded in Phase 1 per 01-CONTEXT.md specifics); Phase 2 fills it with `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)`.
- **`data/` raw files are ≤100 MB** and live in git (per PROJECT.md file-size constraint); CI does not need to fetch them.
- **GitHub Actions + uv** — `astral-sh/setup-uv` is the Astral-maintained official action; handles `uv sync --frozen` + cache invalidation on `uv.lock` changes.

</code_context>

<specifics>
## Specific Ideas

- `tests/fixtures/benchmarks.yaml` structured with one top-level key per source (`lccc_self`, `ofgem_transparency`, `desnz_energy_trends`, `nao_audit`, etc.), each containing a list of year-keyed entries: `{ year, value_gbp_bn, url, retrieved_on, notes, tolerance_pct }`. Same shape across sources so an adversarial reader scans one file.
- Tolerance philosophy: >5% divergence forces the PR author to (a) fix our pipeline, (b) document a methodology-version-bumping divergence in CHANGES.md, or (c) raise the tolerance with written rationale under `## Methodology versions`. Silent tolerance creep is explicitly forbidden.
- LCCC floor tolerance is 0.1% (tight) because we read LCCC source data; external anchor tolerances typically 3–5% (looser) because independent aggregations use different base assumptions (inflation indexing, scheme-subset scope, retrieval-year drift).
- `METHODOLOGY_VERSION` flows into the counterfactual DataFrame as a column → into any Phase-4 derived Parquet → into `manifest.json` via GOV-02. Ties the test-pinning mechanism directly to the publishing-layer provenance story.
- SemVer for methodology: patch = constant tweak, minor = additive parameter, major = formula-shape change. Gives reviewers a scannable signal of how much a methodology PR changes.
- Test pinning uses 2022 + 2019 sliced LCCC data (real years the project already has) + a synthetic all-zeros input (regression test for NaN handling).

</specifics>

<deferred>
## Deferred Ideas

- **`tests/test_determinism.py`** — Phase 4 (needs Parquet output to verify byte-identity).
- **Parquet-variant checks inside `test_schemas.py` / `test_aggregates.py`** — Phase 4 extends the same files.
- **`mkdocs build --strict` as a CI gate** — Phase 3 owns the doc restructure; it adds the gate in its own CI update.
- **ruff, pyright, pre-commit hooks in CI** — Phase 3+ polish.
- **Daily-refresh CI workflow (06:00 UTC cron, per-scheme dirty-check)** — Phase 4 (GOV-03).
- **Multi-scheme benchmark reconciliations (RO, FiT, Constraints, CM, Balancing, Grid, SEG)** — later scheme phases.
- **Coverage reports (`pytest --cov`)** — not required by PROJECT.md; defer indefinitely unless adopted as a project norm.
- **Benchmark drift monitoring (weekly re-fetch vs. committed YAML + diff report)** — post-P11 steady-state.
- **Zenodo DOI registration for dataset citability** — V2-COMM-01, triggered after Phase 5.
- **Ben Pile / Turver commentator reconciliations** — not canonical; if ever added, they live under a `commentators:` key in `benchmarks.yaml` with explicit "non-canonical" flag so adversarial readers know the distinction.

</deferred>

---

*Phase: 02-test-benchmark-scaffolding*
*Context gathered: 2026-04-22*
