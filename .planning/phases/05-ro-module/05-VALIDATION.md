---
phase: 5
slug: ro-module
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` (inherited) |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ && uv run mkdocs build --strict` |
| **Estimated runtime** | ~60 seconds (quick), ~180 seconds (full incl. mkdocs --strict) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q` (narrow scope — e.g. `-k ro` or `-k benchmarks` where applicable)
- **After every plan wave:** Run full suite `uv run pytest tests/ && uv run mkdocs build --strict`
- **Before `/gsd-verify-work`:** Full suite must be green, including RO chart outputs regenerated and site link-check clean
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Populated by `/gsd-plan-phase` planner agent from per-plan task IDs. Each task cross-references the `<automated>` verify block inside its PLAN.md.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| pending | — | — | RO-01..RO-06 | — | — | — | — | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Critical Invariants (Nyquist Dimension 8)

From `05-RESEARCH.md` §8 Validation Architecture — four invariants map to `schemes/ro/validate()` D-04 checks:

1. **I-1: Banding divergence bounded.** For every station-month, `|ofgem_rocs_issued - (generation_mwh × banding_factor)| / ofgem_rocs_issued ≤ 1%` for ≥95% of stations. `validate()` returns warning if >10 stations or >5% of station population exceed threshold. Observable evidence: warning log + station IDs.
2. **I-2: Turver/REF benchmark alignment.** Aggregate `ro_cost_gbp` 2011-2022 (all-in GB total per D-12 scope) is within ±3% of REF Constable 2025 Table 1 per-year figures. `validate()` returns warning on drift; `tests/test_benchmarks.py::turver` is a hard block (ROADMAP SC #3 binary). Observable evidence: benchmark test pass/fail + per-year delta table.
3. **I-3: Methodology version consistency.** Every RO Parquet's `methodology_version` column equals the live `counterfactual.METHODOLOGY_VERSION` string. `validate()` warns on mismatch. Observable evidence: Parquet column inspection.
4. **I-4: Forward-projection sanity.** No negative `ro_cost_gbp` in `forward_projection.parquet`; no adjacent-year MWh swings >50%. `validate()` warns on violation. Observable evidence: row-level assertion output.

---

## Wave 0 Requirements

- [ ] `tests/data/test_ofgem_ro.py` — scraper-path tests (mocked; no network)
- [ ] `tests/schemas/test_ro_schemas.py` OR parametrised extension of `tests/test_schemas.py` — one stub per RO grain
- [ ] `tests/fixtures/benchmarks.yaml` — `turver:` section scaffold (entries filled in the benchmark-anchor plan)
- [ ] `tests/fixtures/constants.yaml` — new 2002-2017 DEFAULT_CARBON_PRICES entries with Provenance blocks
- [ ] No new framework install — pytest 9.x + pandera + pandas already live

---

## Manual-Only Verifications

All manual-only verifications are consolidated into **Plan 05-13 — Post-Execution Human Review**, which runs at Wave 6 (autonomous: false) AFTER the autonomous chain (Plans 05-01..05-12) completes. This structure lets Waves 1-5 execute fully unattended under `/gsd-execute-phase 5 --auto` and presents a single human checklist at the end.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `docs/schemes/ro.md` renders at localhost:8000/schemes/ro/ with S2-S5 charts embedded | RO-05 | Requires `mkdocs serve` + visual chart-embed check; `mkdocs build --strict` confirms no broken links but chart readability is a human judgement | Covered in **Plan 05-13 Task 2** — reviewer runs `uv run mkdocs serve`, opens `http://localhost:8000/schemes/ro/`, confirms 4 chart embeds render + cross-links + GOV-01 manifest |
| Ofgem raw data files — Option-D stub disposition (if adopted by Plan 05-01 deterministic fallback) | RO-01 | RER migration (2025-05-14) disrupted programmatic scraping; if Plan 05-01 landed on Option D, stub files must be replaced with real exports OR deferred with backlog ticket | Covered in **Plan 05-13 Task 1** — reviewer inspects each `data/raw/ofgem/*` file, decides Replace-now (download + `uv run python scripts/backfill_sidecars.py --force`) OR Defer-with-backlog (via `/gsd-add-backlog`) |
| REF Constable transcription audit | RO-06 | PDF table copy is not byte-exact automatable; per-year figures require human spot-check against `05-RESEARCH.md §5` verbatim transcription | Covered in **Plan 05-13 Task 3** — reviewer spot-checks ≥3-4 year entries in `tests/fixtures/benchmarks.yaml::ref_constable` against `05-RESEARCH.md §5`; amends + re-runs `uv run pytest tests/test_benchmarks.py -k ref_constable -q` if discrepancies found |
| Divergence report triage — if `05-09-DIVERGENCE.md` was auto-created during Plan 05-09 execution | RO-06 | REF reconciliation >3% drift is documented by the executor in a DIVERGENCE.md sentinel which xfails the reconciliation test; reviewer decides tolerance-widen / fix-forward / defer | Covered in **Plan 05-13 Task 4** — reviewer reads `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` (if present), chooses path (a) widen + audit entry, (b) fix-up plan, or (c) defer |
| Investigation report follow-up — real RER credentials plumbing | RO-01 | If autonomous chain landed on Option D, user decides whether to invest in real-scraper plumbing (Playwright + SharePoint-OIDC + CI secrets) as a follow-up phase | Covered in **Plan 05-13 Task 5** — reviewer reads `05-01-TASK-1-INVESTIGATION.md` `## Plan 05-13 Follow-Ups`, decides BACKLOG-ADD / DEFERRED |
| `schemes.ro.validate()` D-04 invariant warnings | RO-02..06 | Runtime validate() returns warnings (not hard-fail) for I-1..I-4; reviewer decides whether each warning is clean, needs fix-up, or backlog | Covered in **Plan 05-13 Task 6** — reviewer runs `uv run python -c "from uk_subsidy_tracker.schemes.ro import validate; print(validate())"` and dispositions each warning |

---

## Validation Sign-Off

- [ ] All tasks in Plans 05-01..05-12 have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (scraper-test stubs, schemas stubs, benchmarks.yaml scaffold, constants.yaml entries)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s (quick) / < 180s (full)
- [ ] Manual-Only Verifications are covered in **Plan 05-13 Post-Execution Human Review** (Wave 6; autonomous: false)
- [ ] `nyquist_compliant: true` set in frontmatter once plan-checker validates per-task coverage

**Approval:** pending
