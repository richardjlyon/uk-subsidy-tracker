---
phase: 6
slug: flagship-cross-scheme-charts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-25
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Sourced from `06-RESEARCH.md` §"Validation Architecture (Nyquist Dim 8)".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml [tool.pytest.ini_options]` (default `testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest tests/test_aggregates.py tests/test_schemas.py tests/test_determinism.py tests/test_headline_sync.py -x` |
| **Full suite command** | `uv run pytest -v` |
| **Estimated runtime** | ~30s (quick) / ~2-3 min (full suite + mkdocs build --strict) |

---

## Sampling Rate

- **After every task commit:** Run quick command (~30s)
- **After every plan wave:** Run `uv run pytest -v` + `uv run mkdocs build --strict` + `uv run python -m uk_subsidy_tracker.plotting`
- **Before `/gsd-verify-work` (phase gate):** Full suite green + `mkdocs --strict` clean + all 5 X-chart PNG + HTML + .div.html artefacts present in `docs/charts/html/` + `cross_scheme.parquet` byte-identical across two consecutive rebuilds
- **Max feedback latency:** 30 seconds for quick command

---

## Per-Task Verification Map

> Plan IDs are tentative pending planner output; planner finalises wave/plan numbering. Status updated as plans land.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 6-W1-CSP | 06-01 | 1 | X-01..X-05 (substrate) | — | cross_scheme.parquet schema conforms to CrossSchemeRow | unit | `uv run pytest tests/test_schemas.py -k portal -x` | ❌ W1 (extend) | ⬜ pending |
| 6-W1-RC | 06-01 | 1 | D-03 | — | sum(cross_scheme by scheme) == per-scheme annual_summary totals | unit | `uv run pytest tests/test_aggregates.py::test_cross_scheme_row_conservation -x` | ❌ W1 (extend) | ⬜ pending |
| 6-W1-DET | 06-01 | 1 | D-21 | — | cross_scheme.parquet byte-identical across rebuilds | unit | `uv run pytest tests/test_determinism.py -k cross_scheme -x` | ❌ W1 (extend) | ⬜ pending |
| 6-W1-PROV | 06-01 | 1 | GOV-04 | — | uk_households constant matches yaml fixture; Provenance: docstring grep-discoverable | unit | `uv run pytest tests/test_constants_provenance.py -k UK_HOUSEHOLDS -x` | ❌ W1 (extend `_TRACKED`) | ⬜ pending |
| 6-W1-RFL | 06-01 | 1 | GOV-03 | — | refresh_all per-scheme dirty-check includes portal scheme | integration | `uv run pytest tests/test_refresh_loop.py -k portal -x` | ❌ W1 (extend) | ⬜ pending |
| 6-W2-X1 | 06-02 | 2 | X-01 | — | X1 stacked chart renders from cross_scheme.parquet | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x1_stacked_total` | ❌ W2 | ⬜ pending |
| 6-W2-X2 | 06-02 | 2 | X-02 | — | X2 cumulative premium chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x2_cumulative_premium` | ❌ W2 | ⬜ pending |
| 6-W2-X3 | 06-02 | 2 | X-03 | — | X3 per-household chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x3_per_household` | ❌ W2 | ⬜ pending |
| 6-W3-X4 | 06-03 | 3 | X-04 | — | X4 cost-per-MWh chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x4_cost_per_mwh` | ❌ W3 | ⬜ pending |
| 6-W3-X5 | 06-03 | 3 | X-05 | — | X5 2022-crisis chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x5_2022_crisis` | ❌ W3 | ⬜ pending |
| 6-W5-MKD | 06-05 | 5 | PORTAL-01 | — | docs/portal/* + docs/index.md build with --strict zero warnings | integration | `uv run mkdocs build --strict` | ✅ existing gate | ⬜ pending |
| 6-W6-HSY | 06-06 | 6 | D-09 + D-11 | — | homepage + cfd.md + ro.md prose ↔ parquet totals (1 d.p.) | unit | `uv run pytest tests/test_headline_sync.py -x` | ❌ W6 (net-new) | ⬜ pending |
| 6-W7-REF | 06-07 | 7 | D-03 (REF anchor) | — | sum(cross_scheme[CfD]+[RO]) ≈ REF subset within ±N% | integration | `uv run pytest tests/test_benchmarks.py::test_ref_total_reconciliation -x` | ❌ W7 (net-new) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

> "Wave 0" here = pre-W1 fixture/test scaffolding required before Wave 1 plans can execute. The planner folds these into W1 task `read_first` + `acceptance_criteria` blocks; no separate Wave 0 needed because pytest infra is already in place.

- [ ] `tests/test_headline_sync.py` — net-new file; 7+ parametrised cases (Wave 6)
- [ ] `tests/test_aggregates.py::test_cross_scheme_row_conservation` — append to existing file (Wave 1)
- [ ] `tests/test_schemas.py` — extend `_GRAIN_MODELS` to include `("cross_scheme", CrossSchemeRow)` (Wave 1)
- [ ] `tests/test_determinism.py` — append `PORTAL_GRAINS = ("cross_scheme",)` parametrisation (Wave 1)
- [ ] `tests/test_benchmarks.py::test_ref_total_reconciliation` — append; extends `_TOLERANCE_BY_SOURCE` dispatch (Wave 7)
- [ ] `tests/test_constants_provenance.py::_TRACKED` — extend with `UK_HOUSEHOLDS_*` synthetic keys (Wave 1)
- [ ] `tests/test_refresh_loop.py` — extend with portal scheme invariant (Wave 1)
- [ ] `src/uk_subsidy_tracker/data/uk_households.py` — net-new module + `Provenance:` docstring (Wave 1)
- [ ] `tests/fixtures/constants.yaml` — add per-year UK_HOUSEHOLDS entries mirroring `DEFAULT_CARBON_PRICES_YYYY` shape (Wave 1)
- [ ] `data/raw/ons/familiesandhouseholdsuk2025.xlsx` + `.meta.json` — net-new raw file + sidecar (Wave 1)

**Framework install:** None needed — pytest, pyarrow, plotly, kaleido, pandera, pydantic, mkdocs-material all verified installed at the versions required (per RESEARCH.md §"Test Framework").

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Twitter-PNG hero visual sanity (text legibility, scheme-band ordering, caption placement) | X-01..X-05 visual quality | Pixel-perfect chart QA is human-judgment; automated test verifies file existence + dimensions only | After Wave 2/3, open `docs/charts/html/x{1..5}-*.png` in browser at 100%; verify (a) all scheme bands labelled, (b) Twitter-card 1200×675 aspect honoured, (c) caption ≤ 2 lines, (d) X1 "All-time" view fills horizontal extent |
| Material grid card responsive layout (mobile breakpoint) | PORTAL-01 | MkDocs Material handles responsiveness; but the 3-card row needs a visual check at narrow widths | `uv run mkdocs serve`; visit `localhost:8000`; resize to ≤768px width; verify cards stack vertically and headline figures remain readable |
| `docs/portal/methodology.md` reads coherently end-to-end | D-09 + D-Claude's Discretion | Methodology page is editorial — passes mkdocs --strict but readability needs human review | After Wave 4, read methodology page top-to-bottom; verify: (i) cross-scheme aggregation rule clear, (ii) scheme-year vs calendar-year explained, (iii) no-counterfactual exclusion list present, (iv) per-household division convention stated, (v) partial-coverage caveat language present, (vi) REF cited clinically (no peer-publisher framing) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or W1 fixture dependencies declared
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 1 covers all MISSING references (cross_scheme schema, row conservation, determinism, provenance, refresh loop)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s for quick command
- [ ] Phase-gate manual verifications scheduled (PNG QA + responsive layout + methodology read-through)
- [ ] `nyquist_compliant: true` set in frontmatter once planner has emitted PLAN.md files with the W1 fixture tasks

**Approval:** pending
