# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `tests/test_counterfactual.py` — pins the gas counterfactual formula
  against known inputs to 4 decimal places (TEST-01). Asserts
  `METHODOLOGY_VERSION` presence + DataFrame propagation.
- `tests/test_schemas.py` — pandera validation of raw CSV/XLSX sources
  via the existing loaders (pre-Parquet scaffolding; formal TEST-02 in
  Phase 4).
- `tests/test_aggregates.py` — row-conservation assertions on the
  LCCC CfD pipeline (pre-Parquet scaffolding; formal TEST-03 in Phase 4).
- `METHODOLOGY_VERSION` constant in `src/uk_subsidy_tracker/counterfactual.py`
  (GOV-04); `compute_counterfactual()` returns it as a DataFrame column.
- Pandera schemas `elexon_agws_schema`, `elexon_system_price_schema`,
  and `ons_gas_schema`; corresponding loaders now call `.validate()`.
- `tests/test_benchmarks.py` — reconciles CfD pipeline yearly totals
  against the mandatory LCCC self-reconciliation floor (0.1% red line
  per D-10) + regulator-native external anchors at named tolerances
  (TEST-04).
- `tests/fixtures/benchmarks.yaml` — structured benchmark values with
  per-entry source, year, URL, retrieval date, notes, and tolerance;
  Pydantic-validated loader at `tests/fixtures/__init__.py`.

### Changed
- Phase 2 scope correction (CONTEXT D-04): formal `TEST-02`, `TEST-03`,
  `TEST-05` requirement IDs reassigned from Phase 2 to Phase 4.
  Phase 2 still ships pre-Parquet scaffolding variants of
  `tests/test_schemas.py` and `tests/test_aggregates.py` (today), plus
  CI, pin test, and methodology versioning (TEST-01, TEST-04, TEST-06,
  GOV-04). Phase 4 will add the Parquet-schema + Parquet-aggregate
  variants + `tests/test_determinism.py` to satisfy the three formal
  requirements. `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md`
  updated.
- Phase 2 ROADMAP success criterion 1 reworded from "all five test classes" to "four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`" to reflect D-03 deferring `test_determinism.py` to Phase 4 (per Phase 2 CONTEXT D-04).
- Phase 2 ROADMAP success criterion 3 re-anchored from "Ben Pile (2021 + 2026), REF subset, and Turver aggregate" to "LCCC self-reconciliation and any regulator-native external sources the researcher located (OBR, Ofgem, DESNZ, HoC Library, NAO)" (per Phase 2 CONTEXT D-11).
- `ARCHITECTURE.md` §11 P1 deliverables block updated to match the
  above (per user memory: when ARCHITECTURE.md and ROADMAP disagree,
  the spec wins; the spec was amended first, ROADMAP + REQUIREMENTS
  then aligned to it).

## [0.1.0] — 2026-04-21

First tagged pre-release of the UK Renewable Subsidy Tracker, renamed
from the `cfd-payment` single-scheme prototype. Establishes the
publishable baseline for scheme expansion (P1 onward).

### Added
- `ARCHITECTURE.md` at repo root — single source of truth design document.
- `RO-MODULE-SPEC.md` at repo root — per-scheme module template.
- `CHANGES.md` — this file.
- `CITATION.cff` — machine-readable academic citation metadata (CFF 1.2.0).
- `README.md` — repo overview with clone + reproduce block.
- `docs/about/corrections.md` — public corrections mechanism (GOV-05).
- `docs/about/citation.md` — citation stub pointing at root `CITATION.cff`.

### Changed
- Python package renamed from `cfd_payment` to `uk_subsidy_tracker`
  (`src/cfd_payment/` → `src/uk_subsidy_tracker/` via `git mv`).
- `pyproject.toml` project name changed from `cfd-payment` to `uk-subsidy-tracker`;
  wheel packages path updated.
- Bumped Python floor from 3.11 to 3.12 to match project constraint
  (`pyproject.toml` `requires-python = ">=3.12"`; `uv.lock` regenerated;
  `CLAUDE.md` Runtime section aligned with Constraints "Python 3.12+ only").
- All 24 Python source files, 2 test files, and `demo_dark_theme.py`
  rewritten from `from cfd_payment` to `from uk_subsidy_tracker`.
- MkDocs theme changed from `readthedocs` to `material` with opinionated
  baseline config (navigation.tabs, navigation.sections, toc.follow,
  search.suggest, search.highlight, content.code.copy) and light/dark
  palette toggle.
- `mkdocs.yml` site identity updated: `site_name`, `site_url`, `repo_url`,
  `repo_name`, `extra.social.link` all point at `uk-subsidy-tracker`.
- `docs/technical-details/gas-counterfactual.md` moved to
  `docs/methodology/gas-counterfactual.md`; inbound references in
  `docs/index.md`, `docs/charts/index.md`, and the three chart pages
  (`cfd-dynamics.md`, `cfd-vs-gas-cost.md`, `remaining-obligations.md`)
  updated.
- Fixed two stale GitHub URL bugs where `richlyon/cfd-payment` should
  have been `richardjlyon/uk-subsidy-tracker` — one at
  `methodology/gas-counterfactual.md:108` and one at
  `charts/subsidy/cfd-vs-gas-cost.md` lines 162/163.

### Removed
- `docs/technical-details/` directory (all contents either moved to
  `docs/methodology/` or previously deleted).

## Methodology versions

<!--
GOV-04 hook: the gas counterfactual formula in
src/uk_subsidy_tracker/counterfactual.py carries a methodology_version
constant starting in Phase 2 (test scaffolding). Changes to that constant
are logged in this section with rationale and the affected chart list.
-->

### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)

- Formula: `counterfactual_total = gas_fuel_cost + carbon_cost + plant_opex` (all £/MWh).
- Constants pinned: `CCGT_EFFICIENCY = 0.55`; `GAS_CO2_INTENSITY_THERMAL = 0.184`
  tCO2/MWh_thermal; `DEFAULT_NON_FUEL_OPEX = 5.0` £/MWh; annual
  `DEFAULT_CARBON_PRICES` 2018–2026 (EU ETS 2018–2020, UK ETS 2021+).
- Sources: BEIS Electricity Generation Costs 2023 Table ES.1 (CCGT O&M);
  GOV.UK UK ETS published prices (carbon).
- Pinned in `tests/test_counterfactual.py` at 4 decimal places; any change to
  these constants fails the pin test and requires a CHANGES.md entry here.
