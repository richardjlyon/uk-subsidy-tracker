---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 04-01-PLAN.md (Wave 0 deps + SEED-001 Tier 2 drift test)
last_updated: "2026-04-22T23:06:14.323Z"
progress:
  total_phases: 12
  completed_phases: 3
  total_plans: 19
  completed_plans: 14
  percent: 74
---

# Project State: UK Renewable Subsidy Tracker

**Last updated:** 2026-04-22
**Session:** Phase 04 Plan 01 complete: Wave 0 deps (pyarrow==24.0.0 + duckdb==1.5.2) added; SEED-001 Tier 2 drift tripwire shipped (tests/fixtures/constants.yaml + tests/fixtures/__init__.py ConstantProvenance/Constants/load_constants extension + tests/test_constants_provenance.py 13-case parametrised test); CHANGES.md [Unreleased] entry recorded; 23 passed + 4 skipped → 36 passed + 4 skipped (zero regressions). METHODOLOGY_VERSION unchanged at "0.1.0". Drift-proof manually verified: edit CCGT_EFFICIENCY 0.55→0.56 fires remediation-hook failure citing METHODOLOGY_VERSION + constants.yaml + CHANGES.md.

---

## Project Reference

**Core value:** Every headline number on the site is reproducible from a single `git clone` + `uv sync` + one command, backed by a methodology page, traceable to a primary regulator source, and survives hostile reading.

**Project docs:**

- `.planning/PROJECT.md` — scope, constraints, key decisions
- `.planning/REQUIREMENTS.md` — v1 requirements with REQ-IDs
- `.planning/ROADMAP.md` — 12-phase plan (P0–P11 mapping)
- `ARCHITECTURE.md` — authoritative design document (§11 has phase plan)
- `RO-MODULE-SPEC.md` — per-scheme module template

**Brownfield note:** Package currently named `cfd_payment`. Phase 1 renames it to `uk_subsidy_tracker`. All scheme modules in phases 5+ use the post-rename package path.

---

## Current Position

Phase: 04 (publishing-layer) — EXECUTING
Plan: 2 of 6 (Plan 01 complete)
**Phase:** 4
**Plan:** 01 complete — Wave 0 deps + SEED-001 Tier 2 drift test shipped
**Status:** Executing Phase 04
**Focus:** Raw-layer migration (Plan 02 next); then derived layer → publishing layer → workflows → docs + benchmark floor.

```
Progress: [███████░░░░░░░░░░░░░░░░░] 3/12 phases complete (14/19 plans = 74%)
```

---

## Performance Metrics

**Phases complete:** 3/12
**Plans complete:** 14/19 (Phase 1 closed 4/4; Phase 2 closed 5/5; Phase 3 closed 4/4; Phase 4 in progress 1/6)
**Requirements delivered:** FND-01, FND-02, FND-03, GOV-05, GOV-06 (CITATION.cff portion), TEST-01, TEST-04, TEST-06, GOV-04 (reinforced in 04-01 via SEED-001 Tier 2 tripwire) + (Phase 3: TRIAGE-01, TRIAGE-02, TRIAGE-03, TRIAGE-04, GOV-01) (+ TEST-02/03/05 formally reassigned to Phase 4 by 02-05 bookkeeping; pre-Parquet scaffolding for TEST-02/03 shipped by 02-02)
**Test coverage:** 36 passing + 4 skipped. `test_counterfactual.py` (6), `test_schemas.py` (5, pre-Parquet scaffolding), `test_aggregates.py` (2, pre-Parquet scaffolding), `test_benchmarks.py` (2 skipped per D-11 fallback — no lccc_self entries, no external anchors transcribed), `test_docs_structure.py` (7, Phase-3 invariants: CUT files absent, 5 themes present, 7 PROMOTE pages exist, D-01 sections present, GOV-01 four-way coverage, mkdocs validation block intact), `test_constants_provenance.py` (13, Phase-4 SEED-001 Tier 2 drift tripwire: 6 name-in-yaml + 6 value-matches-live + 1 non-failing audits-overdue), plus legacy `tests/data/*` (3 passing + 2 skipped). All four §9.6 Phase-2 test classes now present. `test_determinism.py` deferred to Phase 4 Plan 04-03+ per 02-CONTEXT D-03.

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| 02-01 Counterfactual pin + GOV-04 | 3 min | 3 | 3 |
| 02-05 Scope-correction bookkeeping | 5 min | 4 (incl. Task 0 user-approved) | 4 |
| 02-02 Pandera schemas + test_schemas.py + test_aggregates.py scaffolding | 2 min | 3 | 5 |
| Phase 02 P03 | 8min | 2 tasks | 5 files |
| Phase 02 P04 | 30min | 2 tasks | 2 files |
| Phase 03 P01 | 2min | 2 tasks | 3 files |
| Phase 03 P02 | 6min | 5 tasks | 22 files (17 created, 5 modified, 2 deleted) |
| Phase 03 P03 | 9min | 7 tasks | 7 files |
| Phase 03 P04 | 5min | 5 tasks | 3 files (charts regen, ci.yml, test_docs_structure.py, STATE.md) |
| Phase 04 P01 | 5 min | 3 tasks | 6 files |

## Accumulated Context

### Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| 12 GSD phases mapping 1:1 to ARCHITECTURE.md §11 (P0–P11) | User explicitly chose to preserve §11's plan rather than re-bucket |
| GOV requirements distributed across earliest applicable phase | Cross-cutting governance belongs where the mechanism is first built |
| GOV-06 split: CITATION.cff → Phase 1, snapshot URLs → Phase 4 | CITATION.cff is a static doc file; snapshot mechanism is a publishing-layer concern |
| X-04 and X-05 included in Phase 6 | Both are cross-scheme portal charts; Phase 6 already builds X1/X2/X3 cross-scheme infrastructure |
| TRIAGE-04 assigned to Phase 3 | "Every PRODUCTION chart reachable from theme nav" is the exit criterion for Phase 3 triage work |
| Package rename is Phase 1 gate | All subsequent Python code assumes `uk_subsidy_tracker`; rename must land before any new module work |
| GOV-04: METHODOLOGY_VERSION = 1.0.0 + DataFrame column (02-01) | SemVer-shaped module constant (PATCH/MINOR/MAJOR policy); column on `compute_counterfactual()` output propagates the version into any Phase-4 Parquet/manifest — structural handshake, not convention |
| TEST-01: 4-parametrised pin test + remediation-hook failure message (02-01) | `round(actual, 4) == expected` at 4dp across 2019/2022 + zero-gas regression; failure message tells the PR author to bump METHODOLOGY_VERSION + add CHANGES.md entry, making silent constant drift structurally impossible |
| ARCHITECTURE.md §11 P1 amended before ROADMAP edits (02-05 Task 0, user-approved) | Per user memory project_spec_source.md: when ARCHITECTURE.md and ROADMAP disagree, the spec wins. Executor halted correctly on spec-precedence check; user approved Option 1 (amend spec first). test_determinism.py removed from P1 Deliverables (deferred to P3); Ben Pile / REF / Turver anchor replaced by LCCC + regulator-native sources; test_schemas.py + test_aggregates.py added as P1 deliverables with "Parquet variants in P3" qualifier. |
| TEST-02/03/05 formally reassigned Phase 2 → Phase 4 (02-05) | Phase 2 ships pre-Parquet scaffolding variants of test_schemas.py + test_aggregates.py today (useful-today scaffolding, not formal satisfaction); Phase 4 adds Parquet variants + test_determinism.py to close the three formal requirements. ROADMAP.md + REQUIREMENTS.md + CHANGES.md all aligned. |
| Loader-owned pandera validation (02-02) | `.validate()` inside the loader body (not in the test) means every caller benefits — charts, ad-hoc notebooks, future scheme modules — not only the pytest run. Matches the pre-existing `load_lccc_dataset` idiom verbatim. Schema drift fails at read-time, not silently downstream. |
| Row-conservation via `pd.testing.assert_series_equal` (02-02) | Decomposed-then-collapsed groupby sums are algebraically identical under pandas; exact equality is the correct assertion. Tolerance-based comparison would mask the actual failure mode (groupby drops rows on NaN keys). |
| TEST-04: D-11 fallback shipped, not D-10 floor activation (02-03) | `lccc_self: []` in benchmarks.yaml, all external sections empty. LCCC ARA 2024/25 PDF transcription deferred to Phase 3/4 — per plan's own guidance, a wrong floor is worse than no floor. Floor test skips cleanly with D-11-citing reason string; external test parametrises over zero entries (not a failure). |
| TEST-04: Two-layer Pydantic model + source-key injection (02-03) | `BenchmarkEntry` + `Benchmarks` mirrors `LCCCDatasetConfig` + `LCCCAppConfig` from `src/uk_subsidy_tracker/data/lccc.py`. Loader injects parent YAML key as `source` field on each entry before Pydantic validation so test-side failure messages can cite the source by name. |
| TEST-04: Tolerance constants named per-source, not per-entry (02-03) | `LCCC_SELF_TOLERANCE_PCT`, `OBR_EFO_TOLERANCE_PCT` etc. are module-level constants with docstring rationale (D-06). `_TOLERANCE_BY_SOURCE` dict dispatches by source key; `entry.tolerance_pct` YAML field is only a fallback for unnamed sources. Tolerance bumps require CHANGES.md `## Methodology versions` entry (D-07), which means a code PR, which is grep-visible in review. |
| `tests/__init__.py` added as Rule 3 blocking fix (02-03) | Pytest 9.0.3 could not resolve `from tests.fixtures import ...` at collection time without `tests/` being a package. Minimal empty `__init__.py` fixes this without pytest/pyproject config changes; existing `tests/data/*` still collects and passes. |
| Wave 1 nav: rewrite deferred to Plan 03-02 (03-01) | The five-theme docs tree (cost/recipients/efficiency/cannibalisation/reliability) does not exist until Plan 03-02. Rewriting `nav:` in Wave 1 would reference non-existent files, immediately tripping the new `validation.nav.not_found: warn` rule. Adding the validation block first (which is a no-op against the current 3-CfD-chart nav) is strictly safer and gives Plan 03-02's rewrite a strict-mode gate to push against. |
| D-06 theme features locked (03-01) | 10 Material features in exact order: `navigation.tabs`, `navigation.tabs.sticky`, `navigation.sections`, `navigation.top`, `navigation.instant`, `search.suggest`, `search.highlight`, `content.code.copy`, `content.tooltips`, `toc.integrate`. `toc.follow` removed (mutually exclusive with `toc.integrate` per Material docs, RESEARCH Pitfall 4). |
| 7 chart-page stubs shipped before content (03-02) | Plan 03-02 stubs 7 PROMOTE chart pages with D-01 6-section skeleton so that `mkdocs build --strict` passes as the Wave-2 gate; Plan 03-03 replaces `<Stub — ...>` markers with full D-01 content (100-170 lines each). Without stubs, the 22-entry nav rewrite would trip `validation.nav.not_found: warn` on 7 entries and Wave 3 would have no clean gate. |
| PNG stem corrected for cfd-vs-gas-cost Cost-gallery card (03-02) | Plan interface suggested `subsidy_cfd_vs_gas_cost_twitter.png`; actual builder-emitted file (verified against pre-existing chart page L12 reference and deleted docs/charts/index.md L24) is `subsidy_cfd_vs_gas_total_twitter.png`. Using the correct stem prevents broken thumbnails on the Cost theme index after Wave 4 regenerates charts. |
| git mv rename+content-rewrite atomic in a single commit (03-02 Task 1) | Splitting the rename and path-rewrite into two commits drops git's default 50% rename-similarity threshold and loses the `R` status, breaking `git log --follow` for relocated chart pages. Atomic commits preserved 97-98% similarity. |
| D-05a asymmetric methodology linking (03-02 Task 3) | Cost + Efficiency theme methodology pages link OUT to `../../methodology/gas-counterfactual.md` (single shared source of truth for displaced-gas assumption); Recipients, Cannibalisation, Reliability stand alone. Avoids the standard methodology-duplication drift pattern where the same counterfactual gets restated five times. |
| D-01 6-section + GOV-01 four-way coverage manifest locked (03-03) | All 7 PROMOTE chart pages authored to the D-01 6-section structure (What / Argument / Methodology / Caveats / Data & code / See also) with `## Data & code` formatted as a GOV-01 compliance manifest: primary regulator URL + chart source permalink + ≥1 test permalink + reproduce bash block. Grep-verifiable four-way coverage per page; closes GOV-01 structurally for every future chart added to the site. |
| Adversarial-payload-first pattern (03-03) | Each chart's locked rhetorical claim (from RESEARCH §7) appears in the **bold lead** AND as the opening sentence of The Argument AND is restated in paragraph 3 to prevent rhetorical drift when the page gets edited in future passes. Argument paragraphs are numbered (1/2/3) to make structural edits explicit. |
| 04-01 Wave 0: pyarrow>=24.0.0 + duckdb>=1.5.2 added before any Parquet/DuckDB work | Every Phase-4 plan downstream (02-06) depends on at least one. Making the first-plan commit a trivial `chore()` keeps dep churn out of later feature commits. |
| SEED-001 Tier 2: DEFAULT_NON_FUEL_OPEX tracked, not CCGT_EXISTING_FLEET_OPEX_PER_MWH (04-01) | Both live on the module at 5.0 via Python-level alias. Chose the alias because its docstring is the policy-answering one (existing-fleet counterfactual) and it is the default kwarg on `compute_counterfactual()`. Explicit bool exclusion in `_live_constants()` prevents future `FLAG_FOO = True` boolean flags (`bool` is an `int` subclass) from silently entering the tracked-numeric set. |
| METHODOLOGY_VERSION stays "0.1.0" through Phase 4 (04-01 + downstream) | Per CONTEXT D-12 + pre-existing condition: "1.0.0" is reserved for first portal launch (Phase 6+). Phase 4 ensures the value propagates into new Parquet + manifest surfaces; bumping is a later milestone event. |
| TDD RED→GREEN shipped as single task commit, not three (04-01 Task 2) | Plan Task 2 explicitly authorised "three sub-steps in a single task — TDD". RED (test-first) was verified via pytest collection error (`ImportError: cannot import name 'load_constants'`) before loader extension landed in-memory, but ship as one atomic commit so the test + loader + YAML triumvirate travels together in git history — mirrors the `tests/__init__.py` Rule-3 fix pattern from 02-03. |

### Blockers

None currently.

### Todos

- [x] Plan Phase 1 (`/gsd-plan-phase 1`)
- [x] Execute Phase 1 (`/gsd-execute-phase 1`) — 4/4 plans, 5/5 success criteria, MIT licence
- [ ] Rename GitHub repo `cfd-payment` → `uk-subsidy-tracker` (manual UI step; `correction` label already created and will travel on rename)
- [x] Plan Phase 2 (`/gsd-plan-phase 2`)
- [x] Execute Phase 2 Plan 01 — counterfactual pin + GOV-04 seed
- [x] Execute Phase 2 Plan 05 — scope-correction bookkeeping (ROADMAP + REQUIREMENTS + CHANGES + ARCHITECTURE §11 P1 amendment)
- [x] Execute Phase 2 Plan 02 — pandera schemas on elexon/ons_gas + `tests/test_schemas.py` + `tests/test_aggregates.py` pre-Parquet scaffolding
- [x] Execute Phase 2 Plan 03 — `tests/test_benchmarks.py` + `tests/fixtures/benchmarks.yaml` (D-11 fallback shipped)
- [x] Execute Phase 2 Plan 04 — GitHub Actions CI workflow green on push + pull_request (TEST-06; runs 24775720044 + 24775750701)
- [x] Rename GitHub repo (resolved via fresh `richardjlyon/uk-subsidy-tracker` + archive of `cfd-payment`; retrospective Phase-1 shortfall surfaced and closed in Plan 02-04)
- [x] Plan Phase 3 (`/gsd-plan-phase 3`) — Chart Triage Execution (4 plans planned)
- [x] Execute Phase 3 Plan 01 — Wave 1 cleanup: TRIAGE-01 (scissors + bang_for_buck_old deleted) + mkdocs.yml D-06 theme features + validation: block
- [x] Execute Phase 3 Plan 02 — Wave 2: five-theme docs tree + nav: rewrite (TRIAGE-03 shipped; mkdocs --strict clean)
- [x] Execute Phase 3 Plan 03 — Wave 3: PROMOTE chart pages filled with D-01 content (TRIAGE-02 + GOV-01 shipped; mkdocs --strict clean; 7 pages 127-172 lines)
- [x] Execute Phase 3 Plan 04 — Wave 4: full regen + CI strict-build gate (TRIAGE-04)
- [x] Plan Phase 4 (`/gsd-plan-phase 4`) — Publishing Layer (6 plans planned)
- [x] Execute Phase 4 Plan 01 — Wave 0: pyarrow + duckdb deps; SEED-001 Tier 2 constants drift tripwire
- [ ] Execute Phase 4 Plan 02 — Raw-layer migration (`data/*` → `data/raw/<publisher>/<file>` + .meta.json sidecars; loader path updates)
- [ ] Execute Phase 4 Plan 03 — Derived layer: `src/uk_subsidy_tracker/schemas/` Pydantic + `schemes/cfd/*` derivation (cost_model + aggregation + forward_projection writes to `data/derived/cfd/*.parquet`)
- [ ] Execute Phase 4 Plan 04 — Publishing layer: `src/uk_subsidy_tracker/publish/` (manifest.py + csv_mirror.py + snapshot.py); `site/data/manifest.json`
- [ ] Execute Phase 4 Plan 05 — Workflows: `.github/workflows/refresh.yml` (daily cron + PR-based commit-back) + `deploy.yml` (tag-push release asset upload)
- [ ] Execute Phase 4 Plan 06 — Docs + benchmark floor: `docs/data/index.md` + LCCC ARA 2024/25 self-reconciliation floor activation
- [ ] Phase 3/4: transcribe LCCC ARA 2024/25 calendar-year CfD aggregate into `tests/fixtures/benchmarks.yaml::lccc_self` to activate the mandatory D-10 floor check (folded into Phase 4 Plan 06)
- [ ] Phase 3/4: populate external benchmark anchors (OBR EFO calendar-year translation, DESNZ, HoC, NAO) as transcribable figures surface
- [ ] Phase 4+: Author `docs/abbreviations.md` glossary (CfD, AR1, CCGT, MWh, ETS, SCC, LCCC) to populate `content.tooltips` Material feature (OQ5 seed from Phase 3 Plan 03-04 — feature enabled, glossary empty)
- [ ] Phase 4+: Add CF-formula pin test — `tests/test_capacity_factor.py` freezing `CF = generation / (capacity × hours)` per Reliability theme methodology (OQ4 seed from Phase 3 Plan 03-04 — capacity-factor-seasonal chart caveat tracks this)

### Notes

- Brownfield rename COMPLETE: `src/cfd_payment/` → `src/uk_subsidy_tracker/` via `git mv` (commits 7b5538b, 596594c)
- Python floor bumped 3.11 → 3.12 in pyproject.toml + CLAUDE.md (B-3 resolved)
- MkDocs theme swapped `readthedocs` → `material` with palette toggle; `docs/methodology/gas-counterfactual.md` now canonical (was `docs/technical-details/`)
- Root docs committed: ARCHITECTURE.md, RO-MODULE-SPEC.md, CHANGES.md, CITATION.cff, LICENSE (MIT), README.md
- `scissors.py` and `bang_for_buck_old.py` deleted via `git rm` in Plan 03-01 (history preserved; commit c5cc229). Orchestrator now imports 14 chart modules (was 15). Stale PNG/HTML at `docs/charts/html/subsidy_scissors*` remain gitignored and will be purged via Plan 03-04's full regen.
- `mkdocs.yml` primed with D-06 theme features (10 entries) + root-level `validation:` block (nav.omitted_files: warn + anchor + absolute_links warnings) in Plan 03-01 (commit 575b57d). `nav:` block rewritten to 22-entry 5-theme D-04 tree in Plan 03-02 (commit f17f215); first clean `mkdocs build --strict` of Phase 3 (0 warnings, 0.39s build).
- 5 theme directories created under `docs/themes/` (cost/recipients/efficiency/cannibalisation/reliability) via Plan 03-02 — each carries `index.md` (D-02 hybrid: adversarial claim + grid-cards gallery + cross-theme pointers + methodology link) + `methodology.md` (D-05a theme-specific; Cost + Efficiency link OUT to shared `../../methodology/gas-counterfactual.md`). 3 existing CfD chart pages relocated to `docs/themes/cost/` via `git mv` at 97-98% similarity. `docs/charts/index.md` deleted; `docs/charts/subsidy/` directory removed. `docs/index.md` link-rot fixed with 5-theme "Explore by theme" section.
- 7 PROMOTE chart pages filled with full D-01 content in Plan 03-03 (commits 7f38d46, 3e55b22, 4d57874, 30638bf, 3656da3, b75d36d, f527479): lorenz, cfd-payments-by-category, subsidy-per-avoided-co2-tonne, capture-ratio, capacity-factor-seasonal, generation-heatmap, rolling-minimum — each 127-172 lines, all 6 D-01 H2 sections in canonical order, GOV-01 four-way coverage (PNG + methodology link + ≥1 test permalink + Python source permalink) grep-verifiable per page. D-05 shared gas-counterfactual link present on Efficiency flagship alongside pre-existing Cost-theme pages. OQ4 Phase-4 CF-formula pin-test seed recorded in `capacity-factor-seasonal.md` Caveats. Adversarial rhetorical payloads locked per RESEARCH §7.
- CI is now live: `.github/workflows/ci.yml` single-job pytest on push/PR, pinned `astral-sh/setup-uv@v8.1.0` + `actions/checkout@v5`, green on both trigger paths
- GitHub repo lives at `github.com/richardjlyon/uk-subsidy-tracker` (old `cfd-payment` repo archived; origin URL updated locally)
- Raw data files (5 files, each ≤100MB) now committed under `data/` per CLAUDE.md reproducibility policy (retrospective Phase-1 shortfall fixed in commit 75774b8)
- Derived layer (`data/derived/`) does not exist yet; created in Phase 4
- Publishing layer (`site/data/`) does not exist yet; created in Phase 4
- Wave 0 deps live: `pyarrow==24.0.0` + `duckdb==1.5.2` in `uv.lock` (commit b9c8233). Both wheel-resolved for Python 3.13 on macOS-arm64; linux-x86_64 standard.
- SEED-001 Tier 2 drift tripwire live: `tests/test_constants_provenance.py` 13 cases (6 name-in-yaml + 6 value-matches-live + 1 audits-not-overdue warn) wired against `tests/fixtures/constants.yaml` through `tests/fixtures/__init__.py::load_constants` (commit f2548df). SEED-001 Tier 3 (auto-rendered provenance doc page) deferred per CONTEXT D-25.
- `_TRACKED` allowlist in `tests/test_constants_provenance.py` = 6 constants (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX, DEFAULT_CARBON_PRICES_{2021,2022,2023}). Adding a new regulator-sourced constant to `counterfactual.py` requires adding to both `_TRACKED` AND `constants.yaml` for the tripwire to fire on it.

---

## Session Continuity

**To resume:** Read `.planning/STATE.md` (this file), then `.planning/ROADMAP.md` for phase structure, then `ARCHITECTURE.md §11` for authoritative exit criteria.

**Next command:** `/gsd-execute-phase 4` (continues executing — next plan: 04-02 raw-layer migration). Phase 4 Plan 01 (Wave 0) closed: pyarrow==24.0.0 + duckdb==1.5.2 in uv.lock; SEED-001 Tier 2 drift tripwire shipped (tests/test_constants_provenance.py: 13 cases across 6 tracked constants + 1 non-failing audit warning); 36 passed + 4 skipped (was 23 + 4). Remaining Phase 4 plans: 02-raw-layer-migration → 03-derived-layer → 04-publishing-layer-manifest → 05-workflows → 06-docs-and-benchmark-floor.

**Stopped at:** Completed 04-01-PLAN.md (Wave 0 deps + SEED-001 Tier 2 drift test)

---
*State initialized: 2026-04-21 after roadmap creation*
