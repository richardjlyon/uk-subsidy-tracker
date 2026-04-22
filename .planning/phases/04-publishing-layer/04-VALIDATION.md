---
phase: 4
slug: publishing-layer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (configured) |
| **Config file** | `pyproject.toml` (tool.pytest.ini_options) |
| **Quick run command** | `uv run pytest tests/ -x --ff` |
| **Full suite command** | `uv run pytest tests/` |
| **Estimated runtime** | ~60 seconds (full suite, excluding live-network tests) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x --ff`
- **After every plan wave:** Run `uv run pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

*Populated by gsd-planner per task. Each plan task's `<acceptance_criteria>` maps to an automated command where possible; remaining rows fall back to Wave 0 scaffolding or manual verification.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 4-XX-YY | XX | Z | REQ-XX | T-4-XX / — | {behavior} | unit/integration | `{command}` | ✅ / ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Infrastructure that must exist before execution starts (or is added in the first wave):

- [ ] `tests/test_determinism.py` — new file for Parquet determinism check (D-21). No current scaffolding.
- [ ] `tests/test_constants_provenance.py` — new file for `counterfactual.py` constants drift test (D-24).
- [ ] `tests/fixtures/constants.yaml` — new provenance YAML for six counterfactual constants (D-23).
- [ ] `tests/fixtures/__init__.py` — extend with `ConstantProvenance` Pydantic model + `load_constants()` loader alongside existing `BenchmarkEntry` + `load_benchmarks()`.
- [ ] `pyproject.toml` — add `pyarrow` (Parquet engine + determinism-strip) and `duckdb` (deps-declared in ARCHITECTURE §3; docs snippets use it) — must land before any Parquet write task runs.
- [ ] Parquet-variant rows in `tests/test_schemas.py` (D-19) and `tests/test_aggregates.py` (D-20) — beside existing raw-CSV scaffolding.
- [ ] `tests/fixtures/benchmarks.yaml::lccc_self` transcription (D-26) — activates mandatory D-10 floor check from Phase 2 (currently `lccc_self: []`).

---

## Validation Architecture (Nyquist — ≥ 3 Independent Axes)

Per RESEARCH.md §14, six independent validation axes are in scope. Each axis catches a distinct failure class; any single axis failing proves the others cannot substitute for it.

| # | Axis | What it catches | Primary tests | Requirements |
|---|------|-----------------|---------------|--------------|
| 1 | **Schema conformance** | Derived Parquet columns / dtypes / nullability drift from the Pydantic schema | `tests/test_schemas.py` Parquet variants; `*.schema.json` JSON-Schema validators; pandera loader-owned `validate()` | TEST-02, PUB-05 |
| 2 | **Row conservation** | Silent duplication / dropouts across grains during rollup | `tests/test_aggregates.py` Parquet variants: `sum(payment by year) == sum(payment by year × technology) == sum(payment by station_month)` | TEST-03 |
| 3 | **Determinism (modulo Parquet metadata)** | Non-reproducible Parquet output (row-group timestamps, `created_by`) masking a functional change | `tests/test_determinism.py` using `pyarrow.Table.equals()` after write→read→re-write | TEST-05, PUB-01 |
| 4 | **Benchmark floor reconciliation** | Silent change in the counterfactual calc or aggregation that slips past schema + row-conservation | `tests/test_benchmarks.py` with activated `benchmarks.yaml::lccc_self` entry (D-26); 0.1% tolerance | GOV-02 (transparency), PUB-05 (provenance) |
| 5 | **Manifest round-trip** | `Manifest` Pydantic drift: field rename, type change, unit omission surfaces as external-consumer breakage | Write `manifest.json` → read → `Manifest.model_validate()` → `json.dumps(sort_keys=True)` must be byte-identical to original | PUB-01, PUB-02 |
| 6 | **Constants drift (SEED-001 Tier 2)** | Live `counterfactual.py` constant changed without YAML / CHANGES.md / methodology_version update | `tests/test_constants_provenance.py` — reflection + value-equality; `next_audit` date warning | GOV-04 (methodology versioning spec), SEED-001 |

**Nyquist compliance:** ≥ 3 axes required; 6 delivered. Each axis is independent: schema passes ≠ rows pass ≠ bytes pass ≠ numbers pass ≠ contract survives ≠ constants pinned.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| External consumer fetches `manifest.json`, follows a `parquet_url`, retrieves Parquet + CSV + `schema.json` | PUB-02 | End-to-end test requires Cloudflare Pages deploy (post-merge); cannot run in-CI until site is live | 1. After a refresh-PR merges, wait for Pages deploy; 2. `curl https://<host>/data/manifest.json | jq '.datasets[0].parquet_url'`; 3. `curl -O <url>`; 4. Confirm file opens in pandas / DuckDB / Excel |
| Versioned snapshot URL resolves ≥1 year after creation | PUB-03, GOV-06 | Longevity cannot be proved in-CI; release asset URL stability inherits GitHub's retention | Manual probe during release; CITATION template documents the pattern; future regression: follow a published URL from an older `CHANGES.md` entry |
| Daily refresh workflow opens PR when upstream SHA changes | GOV-03 | Requires live cron + upstream to have actually changed | First 14 days of cron runs reviewed manually; downstream: GitHub Issue labelled `refresh-failure` is a surfaced sentinel |
| `docs/data/index.md` snippets (pandas, DuckDB, R) actually work for a reader | PUB-04 | Prose + code-block; cannot be executed in-CI without extra lift | Manual copy-paste test from the rendered MkDocs page; add to Phase 4 gsd-verify-work UAT |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (see Wave 0 Requirements above)
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending (gsd-planner populates the Per-Task Verification Map; gsd-plan-checker approves Nyquist compliance before execution)
