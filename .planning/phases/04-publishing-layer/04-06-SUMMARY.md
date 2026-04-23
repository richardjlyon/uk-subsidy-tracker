---
phase: 04-publishing-layer
plan: 06
subsystem: docs

tags: [docs, benchmarks, citation, journalism, lccc-floor, pub-04, pub-06, gov-06, test-04]

# Dependency graph
requires:
  - phase: 04-publishing-layer-04
    provides: "`src/uk_subsidy_tracker/publish/manifest.py` (manifest.json contract + Pydantic Manifest/Dataset/Source models) — the journalist/academic-facing docs page (docs/data/index.md) documents this contract verbatim. `versioned_url` field on every Dataset is the citation anchor referenced in Section 3 (How to cite it)."
  - phase: 04-publishing-layer-05
    provides: ".github/workflows/deploy.yml — makes the versioned-snapshot URLs (`releases/download/v<YYYY.MM>/manifest.json`) resolvable in practice. The docs page's BibTeX template + APA citation both anchor on these URLs; without deploy.yml they would be aspirational."
  - phase: 02-test-benchmark-scaffolding-03
    provides: "tests/test_benchmarks.py + tests/fixtures/benchmarks.yaml + tests/fixtures/__init__.py (Benchmarks + BenchmarkEntry Pydantic loader). Phase 2 shipped the D-11 fallback posture (empty lccc_self); Phase 4 Plan 06 Task 3 re-examines that posture and re-confirms it."
  - phase: 03-chart-triage-execution
    provides: "docs/index.md five-theme homepage + docs/methodology/gas-counterfactual.md. The Data nav tab slots in between the Reliability theme and About; the docs/data/index.md body cross-links to methodology/gas-counterfactual.md and about/corrections.md."

provides:
  - "docs/data/index.md (144 lines) — journalist/academic how-to-use-our-data page. Six canonical sections (What we publish / How to use it / How to cite it / Provenance guarantees / Known caveats and divergences / Corrections and updates) per CONTEXT D-27 verbatim. Copy-pasteable working snippets for pandas + DuckDB + R that fetch manifest.json via HTTPS and follow URL fields to Parquet/CSV. BibTeX + APA citation templates anchored on releases/tag/v<YYYY.MM>. SHA-256 integrity check snippet. Cross-links to methodology/gas-counterfactual.md, about/corrections.md, CITATION.cff, CHANGES.md, and tests/test_benchmarks.py. Closes PUB-04 + PUB-06 end-to-end (external consumer can fetch manifest → follow URL → retrieve Parquet/CSV with provenance)."
  - "mkdocs.yml Data nav tab — 22 → 23 top-level nav entries. `Data: data/index.md` slots between Reliability theme and About section (alphabetical-adjacent placement; matches the CONTEXT D-04 tree). mkdocs build --strict stays green; 0 warnings/errors."
  - "docs/index.md homepage link — 'For journalists and academics → Use our data' pointer to docs/data/index.md. Surfaces the citation workflow on the landing page so academic readers don't need to hunt through theme tabs."
  - "docs/about/citation.md versioned-snapshot URL pattern (GOV-06) — 'Citing a specific data snapshot' section with BibTeX template anchored on releases/tag/v<YYYY.MM>. Pattern: always tag-name; never main or latest/. Cross-links to docs/data/index.md for full reader-side documentation."
  - "tests/fixtures/benchmarks.yaml::lccc_self 2026-04-22 audit note — YAML header extended with explicit Phase-4-Plan-06 audit record: ARA 2024/25 reports FY without quarterly breakdown (RESEARCH Pitfall 7); 0.1% floor against FY-vs-CY mismatch is strictly worse than no floor per D-10/D-11; awaiting future LCCC quarterly publication. D-11 fallback preserved with explicit evidence (Disposition C per user decision)."
  - "CHANGES.md [Unreleased] consolidation — three new ### Added entries (docs/data/index.md, mkdocs.yml Data nav tab, docs/index.md homepage link) + two new ### Changed entries (docs/about/citation.md versioned-snapshot pattern, tests/fixtures/benchmarks.yaml::lccc_self Disposition C). Single coherent block summarising the full Phase-4 delivery, ready to become [0.2.0] on first release tag."

affects:
  - 05+                              # Every future scheme (RO, FiT, SEG, ...) lands new entries in manifest.json; docs/data/index.md snippets continue to work unchanged because they iterate manifest.datasets[]. Adding a scheme-specific how-to section is a one-line edit when the first non-CfD scheme ships.
  - 06-cross-scheme-portal           # Phase 6 X-01/X-02/X-03 portal charts + PORTAL-01 homepage will extend docs/index.md's "For journalists and academics" section with per-scheme citation hints; the Data nav tab becomes the canonical landing for multi-scheme fetch workflows.

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Data nav tab as top-level entry (not a section): single-page nav entry without subpages. mkdocs-material renders it as a clickable tab; if future subpages land (e.g. per-scheme data guides), promote to a section with `Data: - Overview: data/index.md - CfD: data/cfd.md ...`. Inline expansion path documented in Plan 04-06 PLAN.md Step 2A."
    - "Versioned-snapshot URL pattern for academic citation (GOV-06): `https://github.com/richardjlyon/uk-subsidy-tracker/releases/tag/v<YYYY.MM>` for the release anchor + `https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v<YYYY.MM>/manifest.json` for the machine-readable entry point. GitHub releases carry retention guarantees; this pattern survives repo renames and custom-domain migrations. BibTeX + APA templates in both docs/data/index.md (Section 3) and docs/about/citation.md reinforce the pattern from two surfaces."
    - "D-11 fallback with explicit audit log: `lccc_self: []` persists through Phase 4 by design. YAML header carries a dated audit trail (2026-04-22 entry added this plan) recording each Phase's re-examination attempt, reasoning, and follow-up. Future Phases (5+) inherit the pattern — any Phase that touches benchmarks.yaml updates the header audit log with its own dated entry."

key-files:
  created:
    - "docs/data/index.md — 144 lines, six D-27 sections, three working language snippets (pandas + DuckDB + R), BibTeX + APA citation templates, SHA-256 integrity check, full cross-links"
    - ".planning/phases/04-publishing-layer/04-06-SUMMARY.md (this file)"
  modified:
    - "mkdocs.yml — +1 line: `- Data: data/index.md` nav entry between Reliability and About (22 → 23 top-level entries)"
    - "docs/index.md — 'For journalists and academics' section with Use our data link + manifest.json anchor"
    - "docs/about/citation.md — new 'Citing a specific data snapshot' section with versioned-snapshot BibTeX template"
    - "tests/fixtures/benchmarks.yaml — 12-line audit note block (Disposition C) added to YAML header above `lccc_self: []`"
    - "CHANGES.md — three new ### Added bullets (Plan 04-06) at top of section; two new ### Changed bullets (Plan 04-06) at top of section"
    - ".planning/STATE.md — Plan 04-06 closure; progress 18/19 → 19/19 plans; Phase 4 complete"
    - ".planning/ROADMAP.md — Phase 4 plan progress row updated (6/6 complete)"
    - ".planning/REQUIREMENTS.md — PUB-04 + GOV-05 marked complete in traceability table"

key-decisions:
  - "Disposition C (D-11 fallback re-confirmed) per user decision. User's rationale: 'Not opening the PDF; accepting the plan's autonomous-fallback default. Keep lccc_self: [] empty (matches Phase 2 posture). Record a 2026-04-22 audit note in the YAML header: we re-examined the LCCC ARA 2024/25 question as part of Phase 4; without a quarterly breakdown the FY-vs-CY reconciliation (RESEARCH Pitfall 7) prevents activating the 0.1% floor; fallback preserved with explicit evidence.' The plan's autonomous_fallback clause explicitly authorised Disposition C without human PDF transcription; user re-confirmed this path at the checkpoint. Disposition A/B required human PDF reading and were not exercised."
  - "Data nav entry as single top-level page (not a section). Rationale: only one page to expose (docs/data/index.md); a section wrapper would add nav hierarchy overhead without navigational payoff. Future subpages (per-scheme data guides when Phase 5+ ships) can promote to `Data: - Overview: data/index.md - CfD: data/cfd.md ...` with a two-line mkdocs.yml edit. Matches CONTEXT D-27 single-page intent."
  - "Versioned-snapshot citation anchored on releases/tag URL (not releases/download/...manifest.json). Rationale: the tag URL is the canonical durable anchor; GitHub release pages carry retention guarantees and render the release notes + asset list as a permanent record. Academic citations resolve to the tag page; the manifest.json asset URL lives alongside it in the BibTeX `note` field for machine-readable fetches. Pattern reinforced from two surfaces (docs/data/index.md Section 3 + docs/about/citation.md) to maximise grep-discoverability for future reviewers."
  - "Data nav slot between Reliability (last theme tab) and About. Rationale: alphabetical-adjacent-to-About placement matches the CONTEXT D-04 nav tree mental model (themes first, then meta tabs). Could equally live after Home or before themes; chose end-of-themes for least visual disruption to the five-theme navigation locked in Phase 3."

patterns-established:
  - "Phase-dated audit log in YAML fixture headers: `tests/fixtures/benchmarks.yaml` now carries an explicit 'Audit: 2026-04-22 — Phase 4 Plan 06 (Disposition C)' block above `lccc_self: []`. Every future Phase that re-examines the benchmark floor appends its own dated entry with reasoning + follow-up. Phase 5 (RO module) inherits this template; if a future regulator publication supplies a clean CY aggregate, that Phase populates the list AND appends an audit entry recording the transcription source + date."
  - "Public contract documentation pattern for data consumers: docs/data/index.md is the single discoverable starting point for external consumers (journalists, academics, adversarial analysts). Section 1 (What we publish) enumerates artefact types; Section 2 (How to use it) gives three-language fetch snippets; Section 3 (How to cite it) locks the citation pattern; Section 4 (Provenance guarantees) maps manifest fields to the reproducibility contract; Section 5 (Known caveats) cross-links to tests/test_benchmarks.py; Section 6 (Corrections) wires the GitHub Issues `correction` label. Future scheme docs pages (docs/schemes/ro.md in Phase 5+) link INTO this page for the fetch/cite/provenance sections rather than duplicating them."
  - "Two-surface citation pattern enforcement: the versioned-snapshot URL pattern is documented in BOTH docs/data/index.md (audience: external consumers) AND docs/about/citation.md (audience: readers clicking 'About' from nav). Grep for `releases/tag` surfaces both. Reduces risk of the pattern drifting in one place without the other — a change to the URL shape must update both files in the same PR."

requirements-completed:
  - PUB-04    # docs/data/index.md journalist/academic how-to-use-our-data page (6 D-27 sections, 3 language snippets, SHA-256 integrity, full cross-links)
  - TEST-04   # Benchmark infrastructure + 2026-04-22 audit note preserving D-11 fallback per Disposition C (test_benchmarks.py skip-clean path already shipped in Phase 2; this plan's re-examination closes the Phase-4 D-26 follow-up)

# PUB-06 was already closed in 04-04 (manifest.json public contract shipped);
# the Plan 06 snippets in docs/data/index.md exercise that contract end-to-end,
# but do not re-close the requirement. Similarly GOV-06 was closed in 04-04
# (versioned_url field) and operationalised in 04-05 (deploy.yml); Plan 06's
# docs/about/citation.md update documents the URL pattern but does not
# re-close the requirement.

# Metrics
duration: ~10min
completed: 2026-04-22
---

# Phase 4 Plan 06: Docs + Benchmark Floor Summary

**Shipped the journalist/academic-facing `docs/data/index.md` how-to-use-our-data page (6 canonical sections + 3 language snippets + BibTeX/APA citation templates + SHA-256 integrity check), wired it into the 23-entry top-level nav via a new `Data` tab, extended `docs/about/citation.md` with the versioned-snapshot URL pattern (GOV-06), and re-confirmed the D-11 `lccc_self` fallback per user-selected Disposition C with an explicit 2026-04-22 audit note citing the ARA 2024/25 FY-vs-CY limitation (RESEARCH Pitfall 7). Phase 4 closes with 69 passed + 4 skipped, `mkdocs build --strict` green, and all six plans shipped in order.**

## Performance

- **Duration:** ~10 min end-to-end (across checkpoint pause)
- **Started:** 2026-04-23T00:05Z
- **Completed:** 2026-04-22 (user calendar date; session crossed UTC midnight)
- **Tasks:** 4 completed (4/4) — 2 pre-checkpoint + 1 post-checkpoint + 1 consolidation
- **Files changed:** 6 (1 new + 5 modified)

## Accomplishments

- **docs/data/index.md shipped, 144 lines, all six D-27 sections authored verbatim.** What we publish / How to use it / How to cite it / Provenance guarantees / Known caveats and divergences / Corrections and updates. Copy-pasteable working snippets: pandas (with SHA-256 integrity check using hashlib), DuckDB (INSTALL httpfs + read_parquet over HTTPS), R (arrow + httr + jsonlite). BibTeX + APA citation templates both anchored on the versioned-snapshot URL pattern `releases/tag/v<YYYY.MM>`. Cross-links to methodology/gas-counterfactual.md, about/corrections.md, CITATION.cff, CHANGES.md, tests/test_benchmarks.py — four-way-coverage discoverable from the single how-to page. Closes PUB-04 end-to-end; demonstrates PUB-06 (external consumer fetch workflow) with executable snippets.

- **Top-level Data nav tab wired in (23 entries, up from 22).** mkdocs.yml gains `- Data: data/index.md` between the Reliability theme and About section. `mkdocs build --strict` stays green (0 warnings, 0 errors) — the build's `validation.nav.not_found: warn` rule (Phase 3 Plan 01) validates the new entry. Homepage gains a "For journalists and academics → Use our data" pointer in docs/index.md, surfacing the citation workflow on the landing page.

- **Versioned-snapshot URL pattern documented from two surfaces (GOV-06 reinforced).** docs/about/citation.md gains a "Citing a specific data snapshot" section with a BibTeX template anchored on `releases/tag/v<YYYY.MM>`. Pattern: always tag-name; never `main` or `latest/`. docs/data/index.md Section 3 carries the same pattern plus APA and full BibTeX with manifest.json download URL. Grep `releases/tag` now surfaces both files — drift-resistant.

- **D-11 fallback re-confirmed with explicit 2026-04-22 audit note (Disposition C).** User decision at checkpoint: accept autonomous fallback, do not transcribe the ARA 2024/25 PDF this session. benchmarks.yaml header gains a 12-line audit block recording: (a) Phase 4 Plan 06 re-examined D-11 posture per CONTEXT D-26; (b) the ARA 2024/25 PDF reports FY Apr 2024 – Mar 2025 without a quarterly breakdown that reconstructs CY 2024 cleanly; (c) a 0.1% floor tolerance against an FY-vs-CY mismatch (RESEARCH Pitfall 7) is strictly worse than no floor per D-10/D-11; (d) follow-up remains open — populate when a future LCCC quarterly publication supplies a clean CY aggregate. Matches the plan's `<autonomous_fallback>` clause verbatim. test_lccc_self_reconciliation_floor continues to skip cleanly with a D-11-citing reason string.

- **CHANGES.md [Unreleased] consolidated for Phase 4 exit.** Three new ### Added bullets (docs/data/index.md, mkdocs.yml Data nav tab, docs/index.md homepage link) + two new ### Changed bullets (docs/about/citation.md versioned-snapshot pattern, benchmarks.yaml Disposition C). Ready to become [0.2.0] on the first release tag. METHODOLOGY_VERSION stays "0.1.0" (bump is Phase 6+ at first public release per pre-existing D-12 chain). No new `## Methodology versions` entry added.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author docs/data/index.md (6 sections per D-27)** — `880c41e` (feat)
2. **Task 2: Wire nav — mkdocs.yml + docs/index.md homepage + docs/about/citation.md** — `caf7a41` (feat)
3. **Task 3 (checkpoint → resumed): Disposition C audit note in benchmarks.yaml** — `c4e80f2` (docs)
4. **Task 4: CHANGES.md consolidation** — `2a91a75` (docs)

**Plan metadata commit:** will be `docs(04-06): complete docs-and-benchmark-floor plan` (includes SUMMARY + STATE + ROADMAP + REQUIREMENTS).

**Test count:** 69 passed + 4 skipped — zero regressions. `test_lccc_self_reconciliation_floor` stays skipped per D-11 fallback; `test_external_benchmark_within_tolerance[NOTSET]` stays skipped per zero external entries.

## Checkpoint Disposition

**Task 3 was a `checkpoint:human-verify` gate.** The executor paused after Tasks 1 + 2 and presented the three-disposition decision matrix. User selected **Disposition C** with rationale:

> "Not opening the PDF; accepting the plan's autonomous-fallback default. Keep `lccc_self: []` empty (matches Phase 2 posture). Record a 2026-04-22 audit note in the YAML header: we re-examined the LCCC ARA 2024/25 question as part of Phase 4; without a quarterly breakdown the FY-vs-CY reconciliation (RESEARCH Pitfall 7) prevents activating the 0.1% floor; fallback preserved with explicit evidence."

**response_signal received:** "Disposition C — D-11 fallback re-confirmed; PDF not transcribed in this session; audit note recorded. approved"

Disposition A (clean CY 2024 transcription at 0.1% tolerance) and Disposition B (FY-only transcription at elevated tolerance) required human PDF reading and were not exercised. The plan's `<autonomous_fallback>` clause explicitly authorised Disposition C without human PDF transcription — that clause was activated at the user's explicit direction.

## Nav Count (before/after)

| Baseline | Post-plan | Delta |
|---|---|---|
| 22 top-level entries (Phase 3 D-04 tree) | 23 top-level entries | +1 Data tab |

Top-level order after Plan 06: Home / Cost / Recipients / Efficiency / Cannibalisation / Reliability / **Data** / About.

## Files Created/Modified

- **Created:** `docs/data/index.md` (144 lines) — six-section how-to-use-our-data page
- **Created:** `.planning/phases/04-publishing-layer/04-06-SUMMARY.md` (this file)
- **Modified:** `mkdocs.yml` — Data nav tab inserted between Reliability and About
- **Modified:** `docs/index.md` — "For journalists and academics → Use our data" homepage link
- **Modified:** `docs/about/citation.md` — "Citing a specific data snapshot" section with versioned-snapshot BibTeX template
- **Modified:** `tests/fixtures/benchmarks.yaml` — 12-line audit note block (Disposition C, 2026-04-22) added above `lccc_self: []`
- **Modified:** `CHANGES.md` — three ### Added + two ### Changed Plan 04-06 bullets
- **Modified:** `.planning/STATE.md` — Plan 04-06 closure; progress 18/19 → 19/19
- **Modified:** `.planning/ROADMAP.md` — Phase 4 plan-progress row (6/6 complete)
- **Modified:** `.planning/REQUIREMENTS.md` — PUB-04 traceability row marked Complete

## Decisions Made

- **Disposition C (D-11 fallback re-confirmed).** User explicit direction at checkpoint; rationale: ARA 2024/25 PDF reports FY only, no quarterly breakdown, 0.1% tolerance against FY-vs-CY mismatch is strictly worse than no floor per RESEARCH Pitfall 7 + Phase 2 D-10/D-11.
- **Data nav as single top-level page, not a section.** Only one data page exists; section wrapper would add hierarchy without navigational payoff. Promotion path to section documented in plan for future scheme-specific data pages.
- **Versioned-snapshot citation anchor on `releases/tag/v<YYYY.MM>` (not the manifest.json download URL).** Tag page is the canonical durable anchor (GitHub retention-guaranteed); manifest.json download URL lives in the BibTeX `note` field for machine-readable fetches.
- **Data nav slotted between Reliability and About.** Alphabetical-adjacent-to-About matches CONTEXT D-04 mental model (themes first, then meta tabs).

## Deviations from Plan

**None** — plan executed exactly as written, with one checkpoint decision handed to the user.

- Tasks 1 + 2 executed verbatim from plan `<action>` blocks (Plan 04-06 PLAN.md).
- Task 3 was a `checkpoint:human-verify` gate by design (not a deviation) — user selected Disposition C.
- Task 4 consolidation followed the plan's enumerated topic list.
- No Rule-1 bugs (nothing broken).
- No Rule-2 missing-critical-functionality (CLAUDE.md verified — all directives respected; docs snippets load-bearing rather than placeholder).
- No Rule-3 blocking issues (toolchain worked first pass).
- No Rule-4 architectural changes (no new tables, no new services).

**Total deviations:** 0. Plan is a clean, unmodified execution.

## Issues Encountered

None. All tasks completed first pass:

- `mkdocs build --strict` green on Task 2 (no broken links from the new nav entry).
- `uv run pytest tests/` stayed at 69 passed + 4 skipped across all four task commits.
- benchmarks.yaml YAML parse remained valid after the 12-line header extension (Pydantic `load_benchmarks()` returns the same `Benchmarks(lccc_self=[], ...)` shape).
- `test_lccc_self_reconciliation_floor` continues to skip cleanly with the D-11-citing reason string; no refactoring of the test needed.

Known non-blocker carried forward from Plan 04-05: the benign Material-for-MkDocs 2.0 warning block printed by `mkdocs build --strict`. Theme-framework-level advisory, not a build failure; unchanged from prior plans.

## Phase 4 Exit Checklist

Mapping the five ROADMAP success criteria to the plans that delivered them:

| ROADMAP Success Criterion | Delivered by Plan |
|---|---|
| Three-layer data pipeline (`data/raw/` → `data/derived/` → `site/data/`) operational for CfD | 04-02 (raw), 04-03 (derived), 04-04 (publish) |
| `tests/test_determinism.py` proves byte-identical Parquet rebuilds | 04-03 (10/10 green via `pyarrow.Table.equals`) |
| `manifest.json` exposes full provenance per dataset (GOV-02) | 04-04 (Pydantic Manifest + Dataset + Source models) |
| Daily refresh CI + tagged-release CI operational (GOV-03 + PUB-03) | 04-05 (.github/workflows/refresh.yml + deploy.yml) |
| `docs/data/index.md` + LCCC floor activation or D-11 fallback audit | **04-06** (this plan) |

All five criteria delivered. **Phase 4 complete: 6/6 plans shipped; 19/19 total plans across Phases 1–4.**

## User Setup Required

**None introduced by this plan.** Plan 04-05 left two dashboard-only user-setup items (enable "Allow GitHub Actions to create and approve pull requests" + create `daily-refresh`/`refresh-failure` labels); those remain outstanding and are not addressed by this plan. Plan 04-06 is pure on-disk edits — no external service configuration.

## Open Follow-ups (Deferred)

- **LCCC ARA 2024/25 calendar-year transcription** — when LCCC publishes a quarterly breakdown for 2024, activate the floor by populating `tests/fixtures/benchmarks.yaml::lccc_self` with the Q1+Q2+Q3+Q4 2024 sum at 0.1% tolerance. Append a dated audit entry to the YAML header recording the transcription source + date. Pattern established in this plan.
- **External benchmark anchor transcription** (OBR EFO calendar-year, DESNZ Energy Trends, HoC Library, NAO) — populate `benchmarks.yaml` sections as regulator-native figures become transcribable. Pre-existing todo from Phase 2.
- **docs/abbreviations.md glossary** (OQ5 from Phase 3) — populate `content.tooltips` Material feature. Pre-existing todo from Phase 3 Plan 04.
- **CF-formula pin test** `tests/test_capacity_factor.py` (OQ4 from Phase 3) — capacity-factor formula pinning. Pre-existing todo from Phase 3 Plan 04.

## Next Phase Readiness

**Phase 5 (Renewables Obligation module) is fully unblocked.** The full publishing-layer substrate exists:

- `src/uk_subsidy_tracker/schemes/cfd/` is the §6.1 Protocol-conformance template for `schemes/ro/`.
- `src/uk_subsidy_tracker/publish/manifest.py` iterates `refresh_all.SCHEMES`; adding RO is a one-line append.
- `src/uk_subsidy_tracker/schemas/` houses the Pydantic row models; Phase 5 adds RO-specific variants alongside the CfD five.
- `.github/workflows/refresh.yml` iterates SCHEMES via `refresh_all.py`; Phase 5's RO scheme slots in without workflow edits.
- `docs/data/index.md` snippets work unchanged for RO (consumers just pick a different `id` in `manifest.datasets`).
- `tests/fixtures/benchmarks.yaml` now carries the audit-note pattern; Phase 5 will extend it with RO aggregate benchmarks against Turver (RO-06).

## Verification Results

**Plan `<success_criteria>` block:**

| Criterion | Result |
|---|---|
| `docs/data/index.md` exists with all six D-27 sections | PASS (144 lines; grep -cE for H2 headers = 6) |
| pandas + DuckDB + R working snippets | PASS (pd.read_parquet, INSTALL httpfs, library(arrow) all present) |
| `docs/about/citation.md` references versioned-snapshot URL pattern | PASS (`releases/tag` + `releases/download` both grep-present) |
| `mkdocs.yml` has `Data` top-level nav tab | PASS (`- Data: data/index.md` between Reliability and About) |
| `mkdocs build --strict` green | PASS (0 warnings, 0 errors, 0.45s) |
| `docs/index.md` links to `docs/data/index.md` | PASS (`data/` path + 'Use our data' link text) |
| `benchmarks.yaml::lccc_self` posture explicit (floor activated OR D-11 audit note added) | PASS (Disposition C audit note 2026-04-22 added; `lccc_self: []` preserved) |
| `uv run pytest tests/` green | PASS (69 passed + 4 skipped) |
| `test_lccc_self_reconciliation_floor` skips with D-11 reason | PASS (skip reason cites D-11 fallback + points at ARA PDF) |
| `CHANGES.md` [Unreleased] consolidates Phase-4 artefacts + disposition | PASS (3 Added + 2 Changed Plan 06 bullets; PUB-04 + lccc_self + versioned-snapshot + 18+ req IDs grep-present) |

**Plan `<verification>` block:**

| Check | Result |
|---|---|
| `uv run mkdocs build --strict` | PASS (exit 0) |
| `uv run pytest tests/` | PASS (69 passed + 4 skipped) |
| `grep -q "data/index.md" mkdocs.yml && grep -q "data/" docs/index.md` | PASS |
| Six D-27 H2 sections in docs/data/index.md | PASS (grep count = 6) |
| `grep -q "releases/tag" docs/about/citation.md` | PASS |
| LCCC floor disposition documented in benchmarks.yaml | PASS (Disposition C audit block 2026-04-22) |
| `CHANGES.md` mentions PUB-04 | PASS (Added bullet explicitly cites PUB-04 + PUB-06) |

**Per-task acceptance criteria:** all 4 tasks hit 100% of their declared criteria.

## Self-Check: PASSED

- [x] `docs/data/index.md` exists (144 lines, committed in 880c41e)
- [x] `mkdocs.yml` Data nav tab present (committed in caf7a41)
- [x] `docs/index.md` homepage link present (committed in caf7a41)
- [x] `docs/about/citation.md` versioned-snapshot section present (committed in caf7a41)
- [x] `tests/fixtures/benchmarks.yaml` 2026-04-22 audit block present (committed in c4e80f2)
- [x] `CHANGES.md` consolidated (committed in 2a91a75)
- [x] Commit `880c41e` in git log (Task 1: feat docs/data/index.md)
- [x] Commit `caf7a41` in git log (Task 2: feat nav + homepage + citation)
- [x] Commit `c4e80f2` in git log (Task 3: docs Disposition C audit note)
- [x] Commit `2a91a75` in git log (Task 4: docs CHANGES consolidation)
- [x] `uv run mkdocs build --strict` green (0.45s)
- [x] `uv run pytest tests/` green (69 passed + 4 skipped)
- [x] No regression in `test_lccc_self_reconciliation_floor` (still skips with D-11 reason)
- [x] METHODOLOGY_VERSION unchanged ("0.1.0")
- [x] No new `## Methodology versions` header added to CHANGES.md

---
*Phase: 04-publishing-layer*
*Plan: 06 (Wave 6 — docs + benchmark floor; final plan in Phase 4)*
*Completed: 2026-04-22*
