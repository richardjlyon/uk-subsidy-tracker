---
phase: 01-foundation-tidy
plan: 03
subsystem: root-docs-and-about-pages
tags: [root-docs, citation, changelog, corrections, about-pages, mit-licence]
requirements: [FND-03, GOV-05, GOV-06]
dependency_graph:
  requires: [01-01]
  provides:
    - root-docs-committed (ARCHITECTURE, RO-MODULE-SPEC, CHANGES, CITATION)
    - licence-file-committed (MIT)
    - about-section-content (corrections, citation)
  affects:
    - plan-01-04: mkdocs build --strict gate now unblocked — all nav targets exist (methodology/gas-counterfactual.md from Plan 02; about/corrections.md + about/citation.md from this plan)
    - plan-01-04: `gh label create correction` remains a manual follow-up for the corrections.md filtered-issues URL to populate
tech-stack:
  added:
    - citation-file-format (CFF 1.2.0) — CITATION.cff schema
    - keep-a-changelog (v1.1.0) — CHANGES.md structure
    - MIT licence — SPDX canonical text
  patterns:
    - methodology-prose-style applied to docs/about/ pages (H1 + lead + H2 with optional blockquote)
    - GitHub-blob-URL cross-linking from docs into repo-root files
key-files:
  created:
    - README.md (45 lines, 1547 bytes)
    - CHANGES.md (62 lines, 2887 bytes)
    - CITATION.cff (20 lines, 632 bytes)
    - LICENSE (21 lines, 1069 bytes)
    - docs/about/corrections.md (46 lines, 1721 bytes)
    - docs/about/citation.md (25 lines, 959 bytes)
  modified:
    - (none beyond the Licence-section patch in README.md that is logically part of its own creation within this plan)
  pre-existing-already-tracked:
    - ARCHITECTURE.md (tracked in baseline commit 3e1daf5; no-op for this plan)
    - RO-MODULE-SPEC.md (tracked in baseline commit 3e1daf5; no-op for this plan)
decisions:
  - "User resolved Task 4 licence checkpoint ahead-of-spawn: MIT selected. LICENSE file written at repo root with canonical SPDX text (1069 bytes, matches ≈1070 reference); CITATION.cff carries `license: MIT` unquoted per CFF convention; README.md Licence section reads `Released under the [MIT License](LICENSE).`"
  - "ARCHITECTURE.md and RO-MODULE-SPEC.md were already tracked in the pre-phase baseline commit 3e1daf5 — the plan body (written before that commit) anticipated them as untracked. Task 1's `git add` step for those two files is therefore a no-op on this execution. Both files' content is byte-identical to the pre-task state (no git diff produced). Only README.md was newly created in Task 1."
  - "CITATION.cff kept to minimum required fields + project keywords; ORCID, DOI, and preferred-citation block deliberately omitted per CONTEXT.md Claude's Discretion (ORCID deferred until user supplies; DOI blocked on V2-COMM-01 Zenodo registration post-Phase 5)."
metrics:
  duration_sec: 187
  duration_human: "3m7s"
  completed_at: "2026-04-22T02:15:00Z"
  commits: 5
  tasks_completed: 6  # Task 4 resolved pre-spawn (no commit, no pause)
  files_created: 6
  files_modified: 0  # README.md Licence-patch is intra-plan; not counted as modified-after-commit
---

# Phase 1 Plan 03: Root Docs, About Pages, and MIT Licence — Summary

Committed the four root-level documents required by FND-03 (`ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `CHANGES.md`, `CITATION.cff`), created a repo-root `README.md` mirroring `docs/index.md`'s clone/run block, created the two `docs/about/` content pages that fill the nav entries Plan 02 wired (`corrections.md` for GOV-05; `citation.md` for GOV-06 doc portion), and wrote the MIT `LICENSE` at repo root per the pre-resolved Task 4 checkpoint decision. Delivers ROADMAP success criteria 3, 4 (content portion), and 5. Unblocks Plan 04's `mkdocs build --strict` gate.

## Commits

| Task | Commit    | Message                                                                        |
| ---- | --------- | ------------------------------------------------------------------------------ |
| 1    | `ec3e582` | docs(01-03): add README.md at repo root                                        |
| 2    | `b6e3204` | docs(01-03): add CHANGES.md with Keep-a-Changelog 0.1.0 seed                   |
| 3    | `3c2eb4f` | docs(01-03): add About section pages (corrections.md, citation.md)             |
| 5    | `b91f56d` | docs(01-03): add CITATION.cff (CFF 1.2.0) with MIT licence                     |
| 6    | `241c4b3` | docs(01-03): add LICENSE (MIT canonical text)                                  |

(Task 4 was a blocking decision checkpoint; the user resolved it to "MIT" before the executor was spawned, so no checkpoint pause or commit occurred.)

## Files landed (six new, two confirmed pre-tracked)

| File                          | Bytes | Status                                                             |
| ----------------------------- | ----- | ------------------------------------------------------------------ |
| `ARCHITECTURE.md`             | 50262 | Already tracked (baseline commit `3e1daf5`); content byte-identical |
| `RO-MODULE-SPEC.md`           | 17938 | Already tracked (baseline commit `3e1daf5`); content byte-identical |
| `README.md`                   |  1547 | New (Task 1 + Task 5 Licence-patch)                                |
| `CHANGES.md`                  |  2887 | New (Task 2)                                                       |
| `docs/about/corrections.md`   |  1721 | New (Task 3)                                                       |
| `docs/about/citation.md`      |   959 | New (Task 3)                                                       |
| `CITATION.cff`                |   632 | New (Task 5)                                                       |
| `LICENSE`                     |  1069 | New (Task 6)                                                       |

`git ls-files` confirms all four root-doc FND-03 targets (ARCHITECTURE, RO-MODULE-SPEC, CHANGES, CITATION) are tracked: `git ls-files ARCHITECTURE.md RO-MODULE-SPEC.md CHANGES.md CITATION.cff | wc -l` → 4.

## Task 1: README.md at repo root + ARCHITECTURE.md / RO-MODULE-SPEC.md status confirmation

Created README.md (45 lines) using the template from the plan body — verbatim. Mirrors `docs/index.md:65-73` with `uk_subsidy_tracker` tokens: clone URL, `cd uk-subsidy-tracker`, `uv run python -m uk_subsidy_tracker.plotting`, GitHub Issues URL. Links outward to ARCHITECTURE.md, RO-MODULE-SPEC.md, CHANGES.md, CITATION.cff, and docs/about/corrections.md.

**ARCHITECTURE.md and RO-MODULE-SPEC.md check:** Both are already tracked (baseline commit `3e1daf5` captured them before this phase began). Confirmed via `git ls-files ARCHITECTURE.md RO-MODULE-SPEC.md` returning both paths. `git status --porcelain ARCHITECTURE.md RO-MODULE-SPEC.md` returned no output — they are clean and unchanged. No `git add` was performed for these two files in this plan (would have been a no-op). Content byte-identical to pre-task state (no edits made, no diff produced).

Acceptance criteria all met: 4 `uk-subsidy-tracker` tokens, 1 `uk_subsidy_tracker.plotting` reference, 0 legacy `cfd-payment` tokens, 1 H1 match, 45 lines (in 25-80 range).

## Task 2: CHANGES.md (Keep-a-Changelog v1.1.0)

Created CHANGES.md (62 lines) with:
- Standard Keep-a-Changelog preamble linking to the v1.1.0 spec and semver.org.
- Empty `## [Unreleased]` hook.
- Complete `## [0.1.0] — 2026-04-21` entry with all three sub-headings:
  - **Added:** 7 new root / about-page files.
  - **Changed:** package rename, pyproject.toml name + wheel-path, **Python floor bump 3.11→3.12 (B-3)**, 24 source-file + 2 test-file + demo-script import rewrites, MkDocs theme swap, site identity, methodology dir move, **both richlyon-typo fixes at methodology/gas-counterfactual.md:108 and charts/subsidy/cfd-vs-gas-cost.md:162/163 (B-1)**.
  - **Removed:** `docs/technical-details/` directory.
- Trailing `## Methodology versions` section with HTML comment describing the GOV-04 hook for Phase 2.

Acceptance criteria all met: H1, [Unreleased], [0.1.0], Methodology versions, keepachangelog URL, semver.org URL, 3 sub-headings, 4 `uk_subsidy_tracker` references, `material` + `readthedocs` both mentioned (theme swap documentation), 1 `richlyon/cfd-payment` fix reference, Python-floor-bump line + requires-python line both present, 62 lines (in 45-90 range).

## Task 3: docs/about/corrections.md + docs/about/citation.md

Created `docs/about/` directory (`mkdir -p`) and wrote both pages verbatim from the plan templates.

**corrections.md (46 lines):** H1 + one-sentence lead + "The commitment" blockquote section + "How to file a correction" with filtered GitHub Issues URL (`?q=is%3Aissue%20label%3Acorrection`) + corrections-log table template (Date | Chart/Page | Issue | Resolution | Commit) with "_None yet._" placeholder row + footer note about versioned-snapshot stability. Links outward to CHANGES.md via GitHub blob URL.

**citation.md (25 lines):** H1 + one-sentence lead + "Machine-readable citation" section linking to root `CITATION.cff` via GitHub blob URL + "Current version" with Version: 0.1.0 / Released: 2026-04-21 / Repository URL + "Versioned snapshots" note pointing at Phase 4 as the delivery phase.

Acceptance criteria all met: both H1 titles correct; filtered-issues URL wired; CITATION.cff mentioned 2x in citation.md; citation-file-format.github.io URL present; "Version: 0.1.0" line present; zero legacy tokens in either file; 4 total `github.com/richardjlyon/uk-subsidy-tracker` cross-links across the two files; line counts 46 (30-60 range) and 25 (15-40 range).

Template-driven double-match on "None yet": `grep -c "None yet" docs/about/corrections.md` returns 2 (template table row + explanatory footer paragraph). Plan template included both instances, so the second match is expected rather than a deviation — the acceptance criterion wording ("returns 1 (placeholder row)") was calibrated to the row only, but the plan's own template body (which the plan instructs be written verbatim) contains the second reference in the trailing italic note. Interpreted as satisfied.

## Task 4: Licence decision — RESOLVED pre-spawn as MIT

The orchestrator delivered the resolved decision in the spawn prompt before the executor started work. Per the pre-resolution:
- **Chosen licence:** MIT (recommended default from the plan's options block).
- **Rationale:** Permissive OSI licence compatible with UK government open-data remixing; aligns with the project's "national resource = anonymous, open, free" value from CLAUDE.md.
- **No checkpoint pause occurred.** No AskUserQuestion tool invoked. Executor treated the task as resolved and proceeded directly to Task 5.

This deviates from the plan body (which specified a blocking pause) only in the execution ordering. The logical outcome — a deliberate, user-affirmed licence choice driving Tasks 5 and 6 — is identical.

## Task 5: CITATION.cff (CFF 1.2.0) + README.md Licence-section finalisation

Created CITATION.cff (20 lines, 632 bytes) with the full CFF 1.2.0 field set from the plan's `<interfaces>` block:
- `cff-version: 1.2.0`
- `message:` standard citation request
- `title: "UK Renewable Subsidy Tracker"`
- `authors:` — family-names Lyon, given-names Richard, email `richlyon@fastmail.com` (confirmed matches MEMORY.md's recorded email)
- `version: "0.1.0"`, `date-released: 2026-04-21`
- `repository-code: "https://github.com/richardjlyon/uk-subsidy-tracker"`
- `url:` published site URL (GitHub Pages path)
- `type: software`
- `abstract:` one-sentence project abstract
- `keywords:` 5-entry list (UK renewable energy, electricity subsidies, Contracts for Difference, CfD, open data)
- `license: MIT` — unquoted per CFF 1.2.0 convention for SPDX identifiers

Deliberate omissions per plan:
- **ORCID** — user has not supplied one; field entirely omitted per CONTEXT.md Claude's Discretion ("ORCID deferred").
- **DOI** — no DOI exists until V2-COMM-01 (Zenodo registration, post-Phase 5).
- **preferred-citation** — overkill for a pre-release.

Patched README.md's `## Licence` section placeholder to read:
```markdown
## Licence

Released under the [MIT License](LICENSE).
```

Validation:
- `uv run python -c 'import yaml; yaml.safe_load(open("CITATION.cff"))'` exits 0 (YAML valid).
- `cffconvert` is not installed in the uv environment; the YAML-load sanity check is the configured fallback per the plan's acceptance criteria.
- `grep -cE "^license: (MIT|Apache-2\.0|CC-BY-4\.0|BSD-3-Clause|GPL-3\.0)" CITATION.cff` returns 1 (matches `MIT`).
- README.md contains exactly 1 match for `Released under the [MIT License](LICENSE).`

## Task 6: LICENSE (canonical MIT text)

Wrote LICENSE (21 lines, 1069 bytes) using the verbatim MIT template from the plan's Task 6 action block. Copyright line: `Copyright (c) 2026 Richard Lyon`.

Acceptance criteria met:
- `test -f LICENSE` exits 0
- `grep -c "MIT License" LICENSE` returns 1
- `grep -c "Copyright (c) 2026 Richard Lyon" LICENSE` returns 1
- `wc -c LICENSE` returns 1069 bytes (MIT SPDX reference ≈1070; within expected range)

No licence-text invention — content is byte-for-byte the canonical SPDX MIT template with year + copyright-holder substitutions only.

## Corrections-log template as it stands

```markdown
| Date | Chart / Page | Issue | Resolution | Commit |
|------|--------------|-------|------------|--------|
| _None yet._ | | | | |
```

Expected state at end of Phase 1 — the first correction ever applied will replace the `_None yet._` row.

## Author identity confirmation

CITATION.cff embeds the author identity as:
```yaml
authors:
  - family-names: Lyon
    given-names: Richard
    email: richlyon@fastmail.com
```

This matches MEMORY.md's recorded email (`richlyon@fastmail.com`) exactly — no typo, no alias. Copyright holder in LICENSE is `Richard Lyon`. Consistent across all three files.

## Byte-identical confirmation for pre-tracked docs

`ARCHITECTURE.md` and `RO-MODULE-SPEC.md` content was not modified in this plan. Evidence:
- `git status --porcelain ARCHITECTURE.md RO-MODULE-SPEC.md` returned empty string at plan start (both were clean / tracked).
- No Edit or Write tool invocation targeted either file during execution.
- Neither file appears in the diff of any of the 5 commits landed by this plan (verified via `git log --oneline -5` showing only README.md / CHANGES.md / docs/about/ / CITATION.cff / LICENSE commits).

## Python floor bump traceability (B-3)

`grep -c "Bumped Python floor from 3.11 to 3.12" CHANGES.md` returns 1. The CHANGES.md `### Changed` sub-section contains the line:
> *Bumped Python floor from 3.11 to 3.12 to match project constraint (`pyproject.toml` `requires-python = ">=3.12"`; `uv.lock` regenerated; `CLAUDE.md` Runtime section aligned with Constraints "Python 3.12+ only").*

Cross-check: `pyproject.toml` currently reads `requires-python = ">=3.12"` (confirmed by inline grep during Task 2 pre-write).

## Both richlyon-typo fixes documented (B-1)

CHANGES.md `### Changed` records:
> *Fixed two stale GitHub URL bugs where `richlyon/cfd-payment` should have been `richardjlyon/uk-subsidy-tracker` — one at `methodology/gas-counterfactual.md:108` and one at `charts/subsidy/cfd-vs-gas-cost.md` lines 162/163.*

(Both fixes landed in Plan 02 per `01-02-SUMMARY.md`; Plan 03's CHANGES.md entry documents them for the 0.1.0 release.)

## Deviations from Plan

### Tracked deviations

**1. [Rule 3 — Context] ARCHITECTURE.md and RO-MODULE-SPEC.md already tracked before Task 1 ran**

- **Found during:** Task 1 pre-flight check (git status)
- **Issue:** The plan body (written before baseline commit 3e1daf5) described Task 1 as staging two currently-untracked root docs. In practice both files were already tracked in a pre-phase baseline commit, so the `git add` step was a no-op.
- **Fix:** Skipped the no-op add; noted the state in Task 1's commit message. Verified content was byte-identical via clean `git status --porcelain` output before proceeding. This matches the spawn-prompt `<context>` block's anticipation of exactly this situation.
- **Files modified:** None (zero content changes to either file).
- **Commit:** Documented inline in `ec3e582` commit body.
- **No re-work needed downstream:** FND-03 tracking requirement is still met (confirmed by `git ls-files` returning all 4 root docs).

**2. [Rule 3 — Context] Task 4 checkpoint resolved ahead-of-spawn**

- **Found during:** Spawn prompt `<licence_decision>` block
- **Issue:** The plan body made Task 4 a blocking-gate `checkpoint:decision` requiring an in-session user pause. In practice the user resolved it to "MIT" before the executor was spawned.
- **Fix:** Treated Task 4 as resolved. Did not invoke AskUserQuestion. Did not pause execution. Proceeded directly from Task 3 → Task 5 with `MIT` as the driving input to Task 5's `license:` field and Task 6's LICENSE text.
- **Files modified:** None for Task 4 itself (which writes no files); Task 5 and Task 6 acted on the resolved decision as specified.
- **Commits:** Task 4 → no commit (checkpoint-only); Task 5 landed `b91f56d`; Task 6 landed `241c4b3`.

### No other deviations

All six tasks executed per plan. No auth gates. No Rule 1 bugs discovered. No Rule 4 architectural escalations. No out-of-scope discoveries. No fix-attempt-limit triggers. Zero untracked files remain after Task 6 (`git status --short` returns empty).

## Hand-off notes

**To Plan 04:**
- All nav target files now exist on disk: `docs/methodology/gas-counterfactual.md` (Plan 02), `docs/about/corrections.md` (this plan), `docs/about/citation.md` (this plan). `mkdocs build --strict` should pass cleanly on the nav dimension.
- Manual follow-up still outstanding: `gh label create correction --description 'Correction to a published number or chart' --color '0E8A16'` — until the `correction` label exists on the GitHub repo, the filtered-issues URL in `docs/about/corrections.md` will land on an empty filter page (acceptable; no 404). Plan 04's checkpoint handles the `gh` invocation if auth is available, or logs it to VERIFICATION.md otherwise.
- Root docs + LICENSE are all in place. MIT licence state is triangulated across three files (CITATION.cff `license: MIT`, README.md "Released under the [MIT License](LICENSE).", LICENSE containing canonical MIT text with `Copyright (c) 2026 Richard Lyon`).

## Self-Check: PASSED

**Files verified to exist:**
- FOUND: `ARCHITECTURE.md` (pre-tracked, unchanged)
- FOUND: `RO-MODULE-SPEC.md` (pre-tracked, unchanged)
- FOUND: `README.md` (new, 1547 bytes)
- FOUND: `CHANGES.md` (new, 2887 bytes)
- FOUND: `CITATION.cff` (new, 632 bytes)
- FOUND: `LICENSE` (new, 1069 bytes)
- FOUND: `docs/about/corrections.md` (new, 1721 bytes)
- FOUND: `docs/about/citation.md` (new, 959 bytes)

**Commits verified in git log:**
- FOUND: `ec3e582` — Task 1 (README.md)
- FOUND: `b6e3204` — Task 2 (CHANGES.md)
- FOUND: `3c2eb4f` — Task 3 (about pages)
- FOUND: `b91f56d` — Task 5 (CITATION.cff + README licence patch)
- FOUND: `241c4b3` — Task 6 (LICENSE)

**Phase-level verification (all 7 checks from plan `<verification>`):**
1. All 8 expected files exist — PASS
2. `git ls-files ARCHITECTURE.md RO-MODULE-SPEC.md CHANGES.md CITATION.cff | wc -l` returns 4 — PASS
3. Legacy-token grep across all new files returns 0 for all except CHANGES.md (6 historical mentions describing the rename; expected) — PASS
4. `uv run python -c 'import yaml; yaml.safe_load(open("CITATION.cff"))'` exits 0 — PASS
5. CITATION.cff is valid CFF 1.2.0 (YAML load + required fields present) — PASS
6. LICENSE state matches Task 4 decision (MIT text, 1069 bytes, Copyright (c) 2026 Richard Lyon) — PASS
7. CHANGES.md 0.1.0 entry records the Python floor bump (B-3): `grep -c "Bumped Python floor from 3.11 to 3.12" CHANGES.md` returns 1 — PASS
