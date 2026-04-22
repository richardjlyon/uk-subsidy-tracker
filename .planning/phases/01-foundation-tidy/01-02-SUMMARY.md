---
phase: 01-foundation-tidy
plan: 02
subsystem: docs-infrastructure
tags: [mkdocs, material-theme, navigation, docs-ia, rename-sweep]
requirements: [FND-02]
dependency_graph:
  requires: [01-01]
  provides:
    - docs-methodology-path
    - material-theme-baseline
    - nav-with-about-section
  affects:
    - plan-01-03: must create docs/about/corrections.md and docs/about/citation.md (nav entries already wired, currently warn as missing)
    - plan-01-04: strict-build gate unblocked on dead technical-details/ methodology links
tech-stack:
  added:
    - mkdocs-material (theme swap; already in uv.lock)
  patterns:
    - opinionated-baseline-config (6 features + palette toggle, no plugins beyond search)
    - methodology/ docs dir (replaces technical-details/)
key-files:
  created:
    - docs/methodology/gas-counterfactual.md (via git mv from docs/technical-details/)
  modified:
    - mkdocs.yml (theme, palette, site identity, nav, header comment, extra.social URL)
    - docs/index.md (6 line edits)
    - docs/charts/index.md (4 line edits)
    - docs/charts/subsidy/cfd-dynamics.md (4 line edits)
    - docs/charts/subsidy/cfd-vs-gas-cost.md (4 line edits + 2 richlyon/ typo fixes)
    - docs/charts/subsidy/remaining-obligations.md (2 line edits)
  deleted:
    - docs/technical-details/ (directory; became empty after git mv)
decisions:
  - Task 1 landed as two atomic commits (rename + content edits) rather than one combined commit because git's rename detection consolidated away the three line-level edits during staging; follow-up commit b34ec6d finalized them. Logical outcome identical; see Deviations for detail.
  - Kept the `(4-panel)` suffix removal from nav per D-10 — "CfD Dynamics (4-panel)" became "CfD Dynamics".
  - Non-strict `mkdocs build` substituted for `--strict` per plan instruction: strict gate lives in Plan 01-04 after Plan 01-03 creates about/corrections.md + about/citation.md.
metrics:
  duration_sec: 250
  duration_human: "4m10s"
  completed_at: "2026-04-22T02:08:10Z"
  commits: 4
  tasks_completed: 3
  files_modified: 6
  files_deleted: 1  # (empty technical-details/ dir)
---

# Phase 1 Plan 02: MkDocs Material Theme + Nav/Identity Rename + Methodology Move — Summary

Swapped MkDocs from `readthedocs` to `material` with the opinionated 6-feature baseline and light/dark palette toggle; renamed site identity everywhere to `uk-subsidy-tracker`; moved `docs/technical-details/gas-counterfactual.md` to `docs/methodology/gas-counterfactual.md` with `git mv` (history preserved); swept 5 docs pages for rename tokens and dead `technical-details/` links; fixed both pre-existing `richlyon/cfd-payment` URL typos. Delivers FND-02 and unblocks Plan 01-04's strict-build gate.

## Commits

| Task | Commit    | Message                                                                       |
| ---- | --------- | ----------------------------------------------------------------------------- |
| 1a   | `6da1bb0` | docs(01-02): move gas-counterfactual to methodology/ and fix GitHub URL      |
| 1b   | `b34ec6d` | docs(01-02): update gas-counterfactual internal references (Task 1 follow-up) |
| 2    | `152a714` | feat(01-02): swap MkDocs theme to Material with opinionated baseline          |
| 3    | `d807dae` | docs(01-02): sweep 5 docs pages for rename tokens and dead methodology links  |

## Task 1: Move gas-counterfactual.md to docs/methodology/ + fix GitHub URL

Used `git mv docs/technical-details/gas-counterfactual.md docs/methodology/gas-counterfactual.md` to preserve history. Three line-level edits applied on top:

- **Line 108** — Fixed BOTH the pre-existing `richlyon/cfd-payment` typo (→ `richardjlyon/uk-subsidy-tracker`) and the `cfd_payment` → `uk_subsidy_tracker` package rename in the same markdown link (display path + URL path).
- **Line 121** — Reproduce command updated to `uv run python -m uk_subsidy_tracker.plotting.subsidy.cfd_vs_gas_cost`.
- **Line 127** — Python import updated to `from uk_subsidy_tracker.counterfactual import (`.

Directory cleanup: `docs/technical-details/` removed via `rmdir` after becoming empty.

History check: `git log --follow docs/methodology/gas-counterfactual.md` traces back through commit `2bc363e` (pre-move). Rename preservation confirmed.

## Task 2: Rewrite mkdocs.yml with Material theme

Applied 7 block-level edits (header comment, site identity, repo, theme, nav, extra.social URL — copyright + markdown_extensions + plugins preserved verbatim):

| Block                   | Before                                        | After                                                                  |
| ----------------------- | --------------------------------------------- | ---------------------------------------------------------------------- |
| Header comment          | "CfD Payment Analysis" + `cfd_payment`        | "UK Renewable Subsidy Tracker" + `uk_subsidy_tracker`                  |
| `site_name`             | `CfD Payment Analysis`                        | `UK Renewable Subsidy Tracker`                                         |
| `site_url`              | `.../cfd-payment/`                            | `.../uk-subsidy-tracker/`                                              |
| `site_description`      | "Analysis of UK CfD..."                       | "Independent, open, data-driven audit of UK renewable..."              |
| `repo_name`             | `cfd-payment`                                 | `uk-subsidy-tracker`                                                   |
| `repo_url`              | `...richardjlyon/cfd-payment`                 | `...richardjlyon/uk-subsidy-tracker`                                   |
| `theme.name`            | `readthedocs`                                 | `material` (+ 6 features, light/dark palette toggle)                   |
| `nav`                   | `Gas Counterfactual: technical-details/...`   | `Gas Counterfactual: methodology/...` + new `About` section (2 entries) |
| `extra.social[0].link`  | `.../cfd-payment`                             | `.../uk-subsidy-tracker`                                               |
| `markdown_extensions`   | (unchanged — 18 extensions preserved)         | (unchanged)                                                            |
| `plugins`               | `- search` (unchanged per D-04)               | `- search` (unchanged)                                                 |
| `copyright`             | `Copyright © 2026 Richard Lyon` (unchanged)   | `Copyright © 2026 Richard Lyon` (unchanged)                            |

Also dropped `(4-panel)` suffix from `CfD Dynamics` nav entry per D-10.

### Non-strict `mkdocs build` sanity check

```
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/rjl/Code/github/cfd-payment/site
WARNING -  A reference to 'about/corrections.md' is included in the 'nav' configuration, which is not found in the documentation files.
WARNING -  A reference to 'about/citation.md' is included in the 'nav' configuration, which is not found in the documentation files.
INFO    -  Documentation built in 0.26 seconds
```

Zero `ERROR` or `Traceback`. The two warnings are expected (nav entries for Plan 01-03's content files). After Task 3 landed, the 4 dead-link warnings from docs pages also vanished (swept in Task 3).

## Task 3: Sweep 5 docs pages

| File                                            | Line edits | Summary                                                                              |
| ----------------------------------------------- | ---------- | ------------------------------------------------------------------------------------ |
| `docs/index.md`                                 | 6          | methodology link, clone URL, cd target, reproduce command, Source link, Issues link  |
| `docs/charts/index.md`                          | 4          | methodology link, bulk reproduce, per-chart reproduce, Source link                   |
| `docs/charts/subsidy/cfd-dynamics.md`           | 4          | chart source bullet, counterfactual model bullet, reproduce command, See-also link   |
| `docs/charts/subsidy/cfd-vs-gas-cost.md`        | 4          | methodology link + BOTH `richlyon/cfd-payment` typo fixes (lines 162+163) + reproduce |
| `docs/charts/subsidy/remaining-obligations.md`  | 2          | chart source bullet, reproduce command                                               |

Total: **20 line-level edits across 5 files** (commit shows 20 insertions / 20 deletions).

### Repo-wide sanity greps

Both returned **zero matches** after Task 3:

```bash
grep -rn "cfd-payment\|cfd_payment\." docs/ --include="*.md"   # 0 matches
grep -rn "technical-details/" docs/ --include="*.md"            # 0 matches
grep -rn "richlyon/cfd-payment" docs/                           # 0 matches (both typos fixed)
```

Narrative H1 `# CfD Payment Analysis` on `docs/index.md` preserved verbatim per CONTEXT.md Claude's Discretion ("leave narrative text describing the 'CfD' scheme untouched").

## Both `richlyon/cfd-payment` URL typos fixed

Confirmed across both instances flagged by the planner:

| Instance | File                                       | Line    | Status |
| -------- | ------------------------------------------ | ------- | ------ |
| 1st      | `docs/methodology/gas-counterfactual.md`   | 108     | Fixed in commit `b34ec6d` |
| 2nd+3rd  | `docs/charts/subsidy/cfd-vs-gas-cost.md`   | 162,163 | Fixed in commit `d807dae` |

Post-sweep grep: `grep -c "richlyon/cfd-payment" docs/methodology/gas-counterfactual.md docs/charts/subsidy/cfd-vs-gas-cost.md` returns `0:0`.

## Deviations from Plan

### Tracked deviations

**1. [Rule 1 — Bug] Task 1 landed as two commits instead of one**

- **Found during:** Task 1 commit stage
- **Issue:** After `git mv` + three line-level edits, `git add <old-path> <new-path>` caused git's rename detection to consolidate the staged change as a pure rename, dropping the three content edits from the index. The on-disk file had the correct edits, but commit `6da1bb0` contained the OLD content at the new path.
- **Detection:** Inspected `git show HEAD -- docs/methodology/gas-counterfactual.md` immediately after commit; noticed it showed the new file with `richlyon/cfd-payment` unfixed at line 108, contradicting the action intent.
- **Fix:** Followed up with commit `b34ec6d` containing the three line-edits (3 insertions / 3 deletions). The file on disk was already correct; only the index needed re-syncing.
- **Files modified:** `docs/methodology/gas-counterfactual.md`
- **Commits:** `6da1bb0` (rename only) + `b34ec6d` (content edits) — logically one Task-1 outcome.
- **Lesson for future plans:** When combining `git mv` with line-edits, either (a) stage the rename and edits separately from the start, or (b) use `git add -A` on the file after edits so git detects the change correctly. Do NOT rely on `git add <old-path> <new-path>` to preserve both rename and edits atomically.

**2. [Rule 3 — Blocking] Multi-line string mismatch on docs/index.md line 80**

- **Found during:** Task 3 Part A (edit 4)
- **Issue:** Initial `Edit` call used the full sentence `Corrections and contributions welcome via [GitHub Issues]...` as `old_string`, but the sentence wrapped across lines 79–80 in the file with different whitespace than what the plan quoted.
- **Fix:** Scoped `old_string` to the second-line fragment only (`welcome via [GitHub Issues](https://github.com/richardjlyon/cfd-payment/issues).`) which uniquely identified the target.
- **Files modified:** `docs/index.md`
- **Commit:** Consolidated into Task 3's `d807dae`.

### No other deviations

All three tasks executed per plan. No auth gates, no Rule 4 architectural escalations, no out-of-scope discoveries.

## Hand-off notes

**To Plan 01-03:** Nav entries `about/corrections.md` and `about/citation.md` are wired into `mkdocs.yml`; you must create these content files before Plan 01-04's `mkdocs build --strict` gate. Non-strict build will warn on them until they exist.

**To Plan 01-04:** All dead `technical-details/` methodology links in `docs/` are rewritten to the new `methodology/gas-counterfactual.md` path; the strict-build gate is unblocked on that dimension. The only remaining strict-build blocker is the missing `about/` content (Plan 01-03's scope).

## Self-Check: PASSED

**Files verified to exist:**
- FOUND: `docs/methodology/gas-counterfactual.md`
- MISSING (expected): `docs/technical-details/gas-counterfactual.md` (moved)
- FOUND: `mkdocs.yml` (updated)
- FOUND: `docs/index.md` (updated)
- FOUND: `docs/charts/index.md` (updated)
- FOUND: `docs/charts/subsidy/cfd-dynamics.md` (updated)
- FOUND: `docs/charts/subsidy/cfd-vs-gas-cost.md` (updated)
- FOUND: `docs/charts/subsidy/remaining-obligations.md` (updated)

**Commits verified in git log:**
- FOUND: `6da1bb0` — rename + GitHub URL fix (Task 1a)
- FOUND: `b34ec6d` — gas-counterfactual internal refs (Task 1b)
- FOUND: `152a714` — Material theme swap (Task 2)
- FOUND: `d807dae` — 5 docs pages swept (Task 3)

**Phase-level verification all passed (7/7 checks).**
