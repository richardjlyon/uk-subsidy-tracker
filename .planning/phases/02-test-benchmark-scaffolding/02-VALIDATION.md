---
phase: 2
slug: test-benchmark-scaffolding
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | `pyproject.toml` (no `[tool.pytest.ini_options]` section yet — may add during Phase 2) |
| **Quick run command** | `uv run pytest tests/test_counterfactual.py` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~15 seconds (Phase 2 suite is small; existing `tests/data/` hits skipped where network-dependent) |

---

## Sampling Rate

- **After every task commit:** Run the quick command targeting the test file just modified (e.g. `uv run pytest tests/test_counterfactual.py` after counterfactual work)
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite must be green locally AND in CI (GitHub Actions)
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

> Filled in by planner during `/gsd-plan-phase 2`. Each task's `<automated>` verification command goes here so the executor knows exactly how to sample.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {2-XX-YY} | {01..} | 1+ | {TEST-01/TEST-04/TEST-06/GOV-04 + pre-Parquet TEST-02/03 scaffolding} | — (no threat model blockers for this phase) | N/A (test infrastructure phase) | unit / integration / ci | `uv run pytest {path}` or `gh workflow view ci` | ⬜ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Phase 2 IS the test infrastructure wave — there is no upstream Wave 0 to inherit. The following must exist before any task reports green:

- [ ] `tests/test_counterfactual.py` — pins formula (TEST-01 + GOV-04 pin mechanism)
- [ ] `tests/test_schemas.py` — pandera validation of raw CSVs (pre-Parquet scaffolding for TEST-02, grows in Phase 4)
- [ ] `tests/test_aggregates.py` — row-conservation on CfD pipeline (pre-Parquet scaffolding for TEST-03, grows in Phase 4)
- [ ] `tests/test_benchmarks.py` — LCCC self-reconciliation floor + any regulator-native external anchors (TEST-04)
- [ ] `tests/fixtures/benchmarks.yaml` — structured benchmark values with provenance (D-05)
- [ ] `tests/fixtures/__init__.py` OR extensions to `tests/conftest.py` — YAML loader + Pydantic validator (D-05, planner decides location)
- [ ] `.github/workflows/ci.yml` — pytest-on-push workflow (TEST-06)
- [ ] `METHODOLOGY_VERSION` constant in `src/uk_subsidy_tracker/counterfactual.py` + returned as DataFrame column (GOV-04)
- [ ] `CHANGES.md ## Methodology versions` seeded with `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)` (GOV-04)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Actions workflow triggers on push + PR and reports pass/fail | TEST-06 | The first real run can only happen post-merge into `main`; local act-runner simulation is not authoritative. | 1. Merge PLAN.md branches. 2. Observe green check on `main` via `gh run list --limit 3`. 3. Open a throwaway PR with a trivial change; confirm CI runs and reports on the PR. |
| LCCC self-reconciliation tolerance (≤0.1%) holds against LCCC's published annual-total PDF | TEST-04 | LCCC publishes annual totals as PDF tables, not machine-readable JSON. Figure extraction is a one-time transcription per year. | 1. Open LCCC ARA 2024/25 + any newer published report. 2. Transcribe annual CfD settlement total(s) into `tests/fixtures/benchmarks.yaml` under `lccc_self:`. 3. Run `uv run pytest tests/test_benchmarks.py::test_lccc_self_reconciliation`. 4. Divergence >0.1% → pipeline bug, not a test config issue. |
| Benchmark YAML retrieval URLs still resolve | TEST-04 | URLs can rot between quarterly LCCC releases. Detection is out-of-band from pytest. | During quarterly refresh, run a one-liner (future phase) that curls every `url:` in `benchmarks.yaml`; any 404 triggers a manual re-pin. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (four test files + CI workflow + methodology version + CHANGES.md entry)
- [ ] No watch-mode flags (pytest is invoked one-shot, not `--looponfail`)
- [ ] Feedback latency < 20s on local runs
- [ ] `nyquist_compliant: true` set in frontmatter after plan-checker approves the per-task map

**Approval:** pending
