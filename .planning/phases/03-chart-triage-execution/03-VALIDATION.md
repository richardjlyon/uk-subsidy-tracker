---
phase: 3
slug: chart-triage-execution
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Derived from `03-RESEARCH.md § Validation Architecture`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | implicit — pytest autodiscovers `tests/`; `tests/__init__.py` is the package marker |
| **Quick run command** | `uv run pytest -x` |
| **Full suite command** | `uv run pytest` |
| **Docs build assertion** | `uv run mkdocs build --strict` (Phase 3 primary gate) |
| **Chart regeneration** | `uv run python -m uk_subsidy_tracker.plotting` (precondition for docs build) |
| **Estimated full runtime** | ~5 seconds pytest + ~10 seconds docs build |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -x` plus the filesystem/grep assertion(s) specific to the task in play.
- **After every plan wave:** Run `uv run python -m uk_subsidy_tracker.plotting && uv run mkdocs build --strict` (regenerate PNGs → assert docs build).
- **Before `/gsd-verify-work`:** Full suite green AND `mkdocs build --strict` exits 0.
- **Max feedback latency:** <30 seconds (pytest + build combined).

---

## Per-Task Verification Map

> Task IDs will be assigned by the planner; this table lists the **verification anchors** each task will claim. Planner populates `<automated>` / `<files_modified>` to match.

| Anchor | Req | Behaviour | Test Type | Automated Command | Wave 0? |
|--------|-----|-----------|-----------|-------------------|---------|
| V-T01-01 | TRIAGE-01 | `scissors.py` absent | FS | `test ! -f src/uk_subsidy_tracker/plotting/subsidy/scissors.py` | ❌ |
| V-T01-02 | TRIAGE-01 | `bang_for_buck_old.py` absent | FS | `test ! -f src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` | ❌ |
| V-T01-03 | TRIAGE-01 | No dangling imports | Grep | `! grep -rn "from uk_subsidy_tracker.plotting.subsidy.scissors\|import scissors\|bang_for_buck_old" src/ tests/` | ❌ |
| V-T01-04 | TRIAGE-01 | `__main__.py` no `scissors` ref | Grep | `! grep -n "scissors" src/uk_subsidy_tracker/plotting/__main__.py` | ❌ |
| V-T01-05 | TRIAGE-01 | `counterfactual.py:139` docstring updated | Grep | `! grep -n "scissors" src/uk_subsidy_tracker/counterfactual.py` | ❌ |
| V-T02-01 | TRIAGE-02 | 7 new chart pages exist at theme paths | FS | `for f in docs/themes/cost/cfd-payments-by-category.md docs/themes/recipients/lorenz.md docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md docs/themes/cannibalisation/capture-ratio.md docs/themes/reliability/capacity-factor-seasonal.md docs/themes/reliability/generation-heatmap.md docs/themes/reliability/rolling-minimum.md; do test -f "$f" \|\| exit 1; done` | ❌ |
| V-T02-02 | TRIAGE-02 | Each has 6 D-01 section headers | Grep | per-page grep for `## What the chart shows`, `## The argument`, `## Methodology`, `## Caveats`, `## Data & code`, `## See also` | ❌ |
| V-T02-03 | TRIAGE-02 | Each embeds PNG | Grep | `grep -qE "!\[.*\]\(.*/charts/html/.*_twitter.png\)"` per page | ❌ |
| V-T02-04 | TRIAGE-02 | Each cites Python source permalink | Grep | `grep -qE "github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/"` per page | ❌ |
| V-T02-05 | TRIAGE-02 | 3 existing CfD pages moved via `git mv` | FS | `test -f docs/themes/cost/cfd-dynamics.md && test -f docs/themes/cost/cfd-vs-gas-cost.md && test -f docs/themes/cost/remaining-obligations.md && test ! -f docs/charts/subsidy/cfd-dynamics.md` | ❌ |
| V-T03-01 | TRIAGE-03 | 5 theme directories exist | FS | `for d in cost recipients efficiency cannibalisation reliability; do test -d "docs/themes/$d" \|\| exit 1; done` | ❌ |
| V-T03-02 | TRIAGE-03 | Each theme has `index.md` + `methodology.md` | FS | per-theme `test -f index.md && test -f methodology.md` | ❌ |
| V-T03-03 | TRIAGE-03 | Theme index.md pages use `grid cards` pattern | Grep | `grep -q "grid cards" docs/themes/<theme>/index.md` per theme | ❌ |
| V-T03-04 | TRIAGE-03 | Old `docs/charts/` cleaned up | FS | `test ! -f docs/charts/index.md && test -z "$(ls -A docs/charts/subsidy 2>/dev/null)"` | ❌ |
| V-T04-01 | TRIAGE-04 | `mkdocs.yml` has `validation:` block promoting orphans | Grep | `grep -A2 "validation:" mkdocs.yml \| grep -q "omitted_files: warn"` | ❌ |
| V-T04-02 | TRIAGE-04 | `mkdocs build --strict` exits 0 with no orphan pages | Build | `uv run mkdocs build --strict` | ❌ |
| V-T04-03 | TRIAGE-04 | Every PRODUCTION chart reachable from its theme index | Grep | for each PROMOTE chart page, its theme `index.md` contains a link to it | ❌ |
| V-T06-01 | D-06 | Material features additions land in `mkdocs.yml` | Grep | `grep -q "navigation.tabs.sticky" mkdocs.yml && grep -q "navigation.instant" mkdocs.yml && grep -q "content.tooltips" mkdocs.yml && grep -q "toc.integrate" mkdocs.yml` | ❌ |
| V-G01-01 | GOV-01 | Each PRODUCTION page has 4-way coverage: narrative + methodology link + test permalink + source permalink | Grep | per page: 1 PNG embed + 1 `/docs/methodology/` link OR theme `methodology.md` link + 1 `/blob/main/tests/test_*.py` permalink + 1 `/blob/main/src/uk_subsidy_tracker/plotting/*.py` permalink | ❌ |
| V-PHASE-01 | phase gate | Full pytest suite green | Test | `uv run pytest` | ✓ (green today) |
| V-PHASE-02 | phase gate | Docs build clean under `--strict` | Build | `uv run mkdocs build --strict` | ❌ |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. All Wave-0-marked anchors are red by definition — files don't exist yet.*

---

## Wave 0 Requirements

Wave 0 must install (or confirm) these assertion primitives before any Phase 3 work touches the docs tree:

- [ ] `mkdocs.yml` — add a `validation:` block promoting `nav.omitted_files: warn`, `links.anchors: warn`, `links.absolute_links: warn` so `--strict` catches orphans (without this TRIAGE-04 has no teeth — per research §3).
- [ ] `mkdocs.yml` — add missing D-06 features (`navigation.tabs.sticky`, `navigation.top`, `navigation.instant`, `content.tooltips`); swap `toc.follow` → `toc.integrate`.
- [ ] `tests/test_docs_structure.py` — OPTIONAL but recommended: structural invariants as pytest (theme dirs exist, 6 template sections present, cut files absent). Research §9.4 provides the full skeleton.

*If the planner declines `tests/test_docs_structure.py`, the bash/grep assertions above still cover the invariants — just not as a permanent regression guard.*

---

## Manual-Only Verifications

| Behaviour | Requirement | Why Manual | Test Instructions |
|-----------|-------------|------------|-------------------|
| Adversarial tone in argument sections | TRIAGE-02 (D-01) | Rhetorical judgement, not machine-checkable | Reviewer reads each of 7 new pages and each of 5 theme index pages; confirms hostile framing (e.g., "Six projects took 50% of the pot", not "the pot was unevenly distributed"). Cross-reference existing `cfd-vs-gas-cost.md` tone. |
| Visual quality of chart gallery grid | D-02 | Requires rendered-page inspection | Run `uv run mkdocs serve`; visit each `/themes/<name>/` page; confirm grid-card layout matches iamkate.com/grid aesthetic density; PNG thumbnails load without shift. |
| Open-question resolution | research §OQ1-5 | Planning decisions, not test assertions | Planner captures resolutions in PLAN.md frontmatter (`open_questions_resolved:`) — e.g., OQ1 theme placement of `cfd-payments-by-category`. Treat Phase 3 as a planner-judgement exercise. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or point at a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers the `mkdocs.yml` validation block + D-06 feature delta before the docs-tree tasks start
- [ ] No watch-mode flags used
- [ ] Feedback latency <30s per sampling cycle
- [ ] `nyquist_compliant: true` set in frontmatter after planner fills all `<automated>` fields

**Approval:** pending — planner sets `nyquist_compliant: true` in frontmatter once all Phase-3 tasks carry automated verify hooks or named Wave-0 dependencies.
