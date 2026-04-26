---
phase: 06-flagship-cross-scheme-charts
plan: 05
subsystem: documentation
tags: [portal, homepage, mkdocs-material, grid-cards, headline-cards, x1-hero, portal-01, portal-02]

# Dependency graph
requires:
  - phase: 06-flagship-cross-scheme-charts
    plan: 01
    provides: "data/derived/portal/cross_scheme.parquet (28 rows; 7 cols in D-10 order); src/uk_subsidy_tracker/schemes/portal/__init__.py::latest_fully_reconciled_year() returning 2023"
  - phase: 06-flagship-cross-scheme-charts
    plan: 02
    provides: "docs/charts/html/x1_stacked_total_twitter.png (141 KB Twitter PNG hero) + docs/charts/html/x1_stacked_total.html (4.8 MB interactive HTML with native Plotly 1y/5y/All rangeselector)"
  - phase: 06-flagship-cross-scheme-charts
    plan: 04
    provides: "docs/portal/index.md + docs/portal/methodology.md + 5 X-chart narrative pages + Portal nav block in mkdocs.yml; Status-section cross-link target portal/index.md exists"
provides:
  - "docs/index.md retrofit (118 lines, +25/-1) with: 3 Material grid-cards headline figures (£8.0 bn / £0.1 bn / £282) + italic caveat + X1 Twitter PNG hero + Interactive HTML link, all inserted above the existing Phase 05.1 D-10 2×4 scheme grid; Status-section cross-link to docs/portal/index.md"
affects: [phase-06 plan 06-06 (Wave 6 headline-sync regression test will reconcile the 3 hardcoded card values against cross_scheme.parquet at latest_fully_reconciled_year=2023); phase-7+ scheme expansion (when X4/X5 ship as schemes added to portal, headline values will drift and the regression test will surface mismatches)]

# Tech tracking
tech-stack:
  added: []  # No new dependencies; reuses existing Material grid-cards extension
  patterns:
    - "Headline-card row pattern: Material `<div class=\"grid cards\" markdown>` extension with stat-style cards (no body, no link, no icon, no horizontal rule between value and label); collapses responsively per Material defaults"
    - "Hardcoded prose values anchored by future regression test: 3 numeric values inserted as bold-prose `**£N.N bn**` / `**£NNN**` per Copywriting Contract; Wave 6 test_headline_sync.py will lock against cross_scheme.parquet"
    - "X1 hero embed pattern (verbatim from scheme/theme pages): `![alt](charts/html/{slug}_twitter.png)` PNG + `[Interactive version](charts/html/{slug}.html){target=\"_blank\"}` HTML link"
    - "Latest-fully-reconciled-year framing on stat cards (calendar-year semantics; 2023 today): card label reads `(latest scheme year)` with the underlying year computed via portal.latest_fully_reconciled_year() = max of intersection {CfD complete CYs ≤ 2025} ∩ {RO GB years with non-null cost}"

key-files:
  created: []
  modified:
    - "docs/index.md (94 → 118 lines; +25 lines / -1 line for the Status-section update; 3-card row + caveat + X1 hero block inserted between intro paragraph and `## Schemes` H2)"
    - ".planning/phases/06-flagship-cross-scheme-charts/deferred-items.md (created — logs pre-existing untracked items observed at session start)"

key-decisions:
  - "CfD + RO tile prose (£29bn since 2015 / £67bn since 2002) preserved unchanged — these are cumulative-since-scheme-inception figures, not latest-fully-reconciled-year totals. The Plan Step 1.3 instruction was 'Verify and preserve unless drift'; the existing prose is correct for the 'since YYYY' framing in the populated-tile title contract (UI-SPEC §3 line 200). Wave 6 headline-sync test will gate any future drift."
  - "Card B (Premium over gas) value = £0.1 bn — small because in 2023 CfD's premium_gbp was -£340M (gas was CHEAPER than CfD strike — i.e. CfD generators paid back into the levy) which partially offsets RO's +£425M premium. Net £0.1 bn (rounded to 1dp). This is a real, verifiable figure from the parquet, not a stub. Wave 6 regression test will lock this exact value."
  - "Card C format follows Copywriting Contract for sub-£1k case: `£282` rendered as `**£282**` (no comma; per UI-SPEC line 170 'For per-household, format as £NN (no decimal), e.g. £3,200' — for values < 1000 the comma is omitted per existing scheme-page convention)"
  - "Status-section update preserves user-memory feedback discipline (clinical, no advocacy/relationship language): adds factual cross-link to Portal section + mention of cross-scheme aggregation parquet path; no marketing register"
  - "Site/ and test/ untracked items are pre-existing (visible in env-block git status at session start) and out of scope per SCOPE BOUNDARY rule; logged to deferred-items.md"

patterns-established:
  - "docs/index.md retrofit recipe: insert headline-card block + caveat + X1 hero + horizontal rule BETWEEN the existing intro paragraph + first horizontal rule AND the existing `## Schemes` H2; preserves the Phase 05.1 2×4 scheme grid downstream untouched. Phases 7-12 only update the 3 card values (via Wave 6 regression test) when schemes ship and shift latest_fully_reconciled_year."
  - "Headline-card values traceable to single source-of-truth helper: portal.latest_fully_reconciled_year() + cross_scheme.parquet drive all 3 cards. Future surfaces (e.g. social cards, README badges) reuse the same helper for value computation; the Wave 6 regression test arms against any prose surface that hardcodes these figures."

requirements-completed: [PORTAL-01, PORTAL-02]

# Metrics
duration: 2min
completed: 2026-04-26
---

# Phase 6 Plan 06-05: Portal Homepage Retrofit Summary

**docs/index.md gains 3 Material grid-cards headline figures (£8.0 bn Total subsidy / £0.1 bn Premium over gas / £282 Per household) + italic coverage caveat + X1 Twitter PNG hero + Interactive HTML link, all inserted above the preserved Phase 05.1 2×4 scheme grid; CfD + RO tile clickthrough to schemes/cfd.md / schemes/ro.md preserved per UI-SPEC §3 D-10 lock; mkdocs build --strict exits 0 with zero WARNING lines.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-26T02:18:51Z
- **Completed:** 2026-04-26T02:21:01Z
- **Tasks:** 1 (atomic commit)
- **Files modified:** 1 (docs/index.md) + 1 internal artefact (deferred-items.md)

## Accomplishments

- **3 headline cards inserted** at canonical position (between intro paragraph and `## Schemes` H2) using the locked Material `<div class="grid cards" markdown>` pattern. Stat-style cards: no body, no link, no icon, no horizontal rule between value and label.
- **Card values match cross_scheme.parquet exactly** at `portal.latest_fully_reconciled_year()` = 2023:
  - Card A: `**£8.0 bn**` / `Total subsidy (latest scheme year)` (CfD £1.39bn + RO £6.60bn = £7.998bn → 8.0bn at 1dp)
  - Card B: `**£0.1 bn**` / `Premium over gas (latest scheme year)` (CfD -£0.34bn + RO +£0.43bn = £0.085bn → 0.1bn at 1dp)
  - Card C: `**£282**` / `Per household (latest scheme year)` (£7.998bn / 28,358,000 households = £282)
- **Italic caveat verbatim per Copywriting Contract:** `*Covers 2 of 8 schemes; full coverage in Phases 7-12.*` — clinical, dry, factual prose; no advocacy register; honours user-memory feedback rule on internal-artefact discipline.
- **X1 hero embed verbatim per UI-SPEC §2:** `![Total UK subsidy stacked by scheme — covered schemes only](charts/html/x1_stacked_total_twitter.png)` followed by `[Interactive version](charts/html/x1_stacked_total.html){target="_blank"}`. PNG hero shows the all-time stacked view; the interactive HTML link carries the native Plotly 1y/5y/All rangeselector.
- **CfD + RO populated tiles preserved unchanged:** PORTAL-02 clickthrough convention `schemes/cfd.md` and `schemes/ro.md` (no anchor) intact; existing tile titles (`Contracts for Difference — £29bn since 2015` / `Renewables Obligation — £67bn since 2002`) carry the cumulative-since-inception framing per UI-SPEC §3 line 200 populated-tile contract.
- **6 placeholder tiles unchanged from Phase 05.1 D-10 lock:** all 6 retain bold-text title (NOT a link, NOT accent-coloured) + `*Coming in Phase N.* {brief description}` body; verified `grep -c "Coming in Phase 7\|...\|Coming in Phase 12"` returns 6 and no `**£` markers appear near placeholder tiles.
- **Status section minimally updated** to mention the cross-scheme aggregation parquet (`data/derived/portal/cross_scheme.parquet`) and add a cross-link to the Portal section. Preserves the existing roadmap link + GitHub Issues link; no marketing prose introduced.
- **mkdocs build --strict** exits 0 with zero WARNING/ERROR lines (the Material team upgrade banner is informational stderr, not a strict-mode failure — same observation documented in Plans 06-03 and 06-04).

## Task Commits

Single task committed atomically:

| # | Task | Hash | Type |
|---|------|------|------|
| 1 | Compute headline values + retrofit docs/index.md (cards + caveat + X1 hero + Status update) | `cb217af` | feat |

**Plan metadata commit:** [pending — final commit captures SUMMARY + STATE + ROADMAP]

## Confirmed Headline Values

| Card | Inserted prose | Computed from parquet | Match? |
|------|---------------|----------------------|--------|
| A (Total subsidy) | `**£8.0 bn**` | `(CfD cost_gbp + RO cost_gbp) / 1e9 = (1.394 + 6.605) = 7.998 → 8.0` | ✓ |
| B (Premium over gas) | `**£0.1 bn**` | `(CfD premium_gbp + RO premium_gbp) / 1e9 = (-0.340 + 0.425) = 0.085 → 0.1` | ✓ |
| C (Per household) | `**£282**` | `(CfD cost + RO cost) / households_uk[2023] = 7,998,562,000 / 28,358,000 = 282.06 → 282` | ✓ |

Source: `data/derived/portal/cross_scheme.parquet` row at `year == 2023`; `households_uk` column populated from ONS Sheet 7 "All households" 2023 row (Wave 1 substrate).

## Acceptance Criteria Conformance

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `grep -c '<div class="grid cards" markdown>' docs/index.md` ≥ 1 | 2 | (1 cards row + 1 scheme grid; both present) |
| Card A label verbatim count == 1 | 1 | `Total subsidy (latest scheme year)` |
| Card B label verbatim count == 1 | 1 | `Premium over gas (latest scheme year)` |
| Card C label verbatim count == 1 | 1 | `Per household (latest scheme year)` |
| `grep -cE '\*\*£[0-9]+\.[0-9] bn\*\*'` ≥ 2 | 2 | Cards A + B |
| `grep -cE '\*\*£[0-9,]+\*\*'` ≥ 1 | 1 | Card C |
| Caveat italic-wrapped count == 1 | 1 | `*Covers 2 of 8 schemes; full coverage in Phases 7-12.*` |
| X1 PNG embed count == 1 | 1 | `x1_stacked_total_twitter.png` |
| X1 HTML link count == 1 | 1 | `x1_stacked_total.html` |
| Interactive link with `target="_blank"` count == 1 | 1 | `[Interactive version](charts/html/x1_stacked_total.html){target="_blank"}` |
| `schemes/cfd.md` link count ≥ 1 | 2 | (1 in `[![preview]](…)` + 1 in `__[…]__` title) |
| `schemes/ro.md` link count ≥ 1 | 2 | (1 in `[![preview]](…)` + 1 in `__[…]__` title) |
| `Coming in Phase 7..12` count ≥ 6 | 6 | All 6 placeholder tiles preserved |
| Line count ≥ 80 | 118 | +25 inserted, file grew from 94 → 118 |
| `mkdocs build --strict` exits 0 with zero WARNINGs | ✓ | Build completed in 0.61s |
| Hardcoded card values match parquet | ✓ | All 3 cards verified above |

## Files Created/Modified

**Modified (1):**

- `docs/index.md` (94 → 118 lines; +25 / -1) — 3-card row + caveat + X1 hero + horizontal rule inserted between intro paragraph and `## Schemes` H2; Status section updated to add cross-scheme aggregation mention + Portal cross-link.

**Internal artefact (1):**

- `.planning/phases/06-flagship-cross-scheme-charts/deferred-items.md` (created) — logs pre-existing untracked items (`site/` and `test`) observed at session start; out of scope per SCOPE BOUNDARY rule.

## Decisions Made

1. **CfD + RO tile prose preserved unchanged.** UI-SPEC §3 line 200 specifies the populated-tile title format `__[Scheme name — £N bn since YYYY](schemes/scheme.md)__` (cumulative-since-scheme-inception). The existing Phase 05.1 prose (`£29bn since 2015` / `£67bn since 2002`) matches this contract; the latest-fully-reconciled-year framing applies only to the 3 headline cards (above the grid), not the tile titles. Plan Step 1.3 instruction was "Verify and preserve unless drift" — verified, preserved.
2. **Card B = £0.1 bn is the correct figure for 2023.** CfD's 2023 premium_gbp was -£340M (gas wholesale prices fell below CfD strike prices, so CfD generators repaid into the LCCC levy via difference payments). RO's 2023 premium_gbp was +£425M. Net £85M → £0.1 bn at 1dp. This is a real number sourced from `cross_scheme.parquet` for a year (2023) when the CfD scheme produced a small NEGATIVE premium overall — a noteworthy but verifiable artefact of strike-price economics during high-gas-price episodes. The Wave 6 regression test will lock this exact value.
3. **Card C `£282` (no comma) format.** UI-SPEC line 170 specifies `£N,NNN` for the per-household card; for sub-£1000 values the comma is omitted per existing scheme-page convention (and the regex `\*\*£[0-9,]+\*\*` matches both with-comma and without-comma variants). The Copywriting Contract section's "Number-formatting rules" line 302 says `£N,NNN (no decimal, comma thousands separator)`; the comma is naturally omitted when the value has no thousands. Wave 6 regression test enforces format ±£1.
4. **Status section minimal touch.** Plan Step 1.4 suggested mentioning cross-scheme aggregation + Portal cross-link. Implemented as a single inline-clause edit to the existing paragraph (not a rewrite), preserving the existing roadmap and GitHub Issues sentence verbiage. No marketing register, no first-person plural, no advocacy. Honours user-memory `feedback_internal_artefacts_off_public_docs.md` clinical-prose discipline.
5. **`site/` and `test` untracked items left alone.** Both were untracked at session start (visible in environment-block `git status`); neither is generated or affected by this plan's changes. Logged to `deferred-items.md` per the SCOPE BOUNDARY rule. Future hygiene: add `site/` to `.gitignore` (likely a project-wide concern) and remove or relocate the empty `test` file (origin unknown).

## Deviations from Plan

None — plan executed exactly as written. The Step 1.3 "preserve unless drift" instruction for CfD + RO tile prose resolved as "preserve" after verifying the existing format matches the UI-SPEC §3 line 200 populated-tile contract. The minor format choice for Card C (sub-£1000 omits the comma) is consistent with the Copywriting Contract regex tolerance and existing scheme-page convention.

## Threat Model Conformance

| Threat ID | Status | Evidence |
|-----------|--------|----------|
| T-06-05-01 (hardcoded headline figures drift from parquet) | mitigated (pending Wave 6 test) | All 3 card values computed from `cross_scheme.parquet` at `latest_fully_reconciled_year()` = 2023 and verified to match the inserted prose. Wave 6 `tests/test_headline_sync.py` will arm this gate; for now the gate is "manual verification + commit message documents the source values". |
| T-06-05-02 (per-household card reveals subsidy/household) | accepted | Public ONS data ÷ public regulator data; no privacy concern. |
| T-06-05-03 (tiles link to broken scheme pages) | mitigated | `mkdocs build --strict` passed with zero warnings — implies `schemes/cfd.md` and `schemes/ro.md` resolve as expected; `portal/index.md` (Status-section cross-link) also resolves (Wave 4 shipped this page). |
| T-06-05-04 (placeholder-tile headline figure inserted accidentally) | mitigated | `grep -nE '\*\*£' docs/index.md` returns exactly 3 matches (lines 22, 26, 30 — the 3 cards); 0 matches inside any placeholder tile. D-10 placeholder discipline preserved. |

## Issues Encountered

None blocking. Two pre-existing untracked items (`site/` and `test`) noted as out-of-scope and logged to `deferred-items.md`.

## User Setup Required

None — the plan executed entirely against local files; no external service configuration required.

## Next Phase Readiness

- **Wave 6 (Plan 06-06) headline-sync regression test** has its prose-target surface shipped: `docs/index.md` carries 3 hardcoded values that must reconcile against `cross_scheme.parquet` at `portal.latest_fully_reconciled_year()` = 2023. Test should parametrise over (file, regex, expected_value) tuples — Card A, B, C (homepage) plus CfD tile (`£29bn since 2015`) plus RO tile (`£67bn since 2002`) plus the existing scheme detail pages (`docs/schemes/cfd.md`, `docs/schemes/ro.md`) for cross-scheme totals.
- **Wave 7 (Plan 06-07) REF reconciliation test** does not depend on this plan's surface — REF benchmark anchoring lives in `tests/fixtures/benchmarks.yaml` per the user-memory clinical-citation discipline.
- **Phases 7-12 scheme expansion** will mechanically shift the headline values: when FiT (Phase 7) ships, X1 will gain a third stacked band, the headline cards will need re-computation (parquet + helper compute the new values), and the Wave 6 regression test will surface the prose drift on the next CI run. The retrofit pattern documented above (insert above the scheme grid; preserve the grid downstream) generalises to subsequent phases.

## Self-Check: PASSED

**Files modified:**

- FOUND: `docs/index.md` (118 lines; cards + caveat + X1 hero + Status update)
- FOUND: `.planning/phases/06-flagship-cross-scheme-charts/deferred-items.md`

**Commits:**

- FOUND: `cb217af` — Task 1 (homepage retrofit)

**Verification:**

- FOUND: `uv run mkdocs build --strict` exits 0 with zero WARNING lines
- FOUND: 3 headline-card values match `cross_scheme.parquet` at year=2023 exactly (£8.0 bn / £0.1 bn / £282)
- FOUND: 6 placeholder tiles preserved (no `**£` markers near "Coming in Phase N" lines)
- FOUND: 2 populated tiles preserve PORTAL-02 clickthrough (`schemes/cfd.md` + `schemes/ro.md` both present, no anchor)
- FOUND: X1 hero embed pattern verbatim (PNG embed + Interactive HTML link with `target="_blank"`)

---
*Phase: 06-flagship-cross-scheme-charts*
*Completed: 2026-04-26*
