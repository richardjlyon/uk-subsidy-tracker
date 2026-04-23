---
phase: 04-publishing-layer
plan: 05
subsystem: workflows

tags: [workflows, ci, cron, release, github-actions, gov-03, pub-03, gov-06]

# Dependency graph
requires:
  - phase: 04-publishing-layer-04
    provides: "src/uk_subsidy_tracker/refresh_all.py orchestrator CLI (module entry point) + src/uk_subsidy_tracker/publish/snapshot.py CLI with --version/--output/--dry-run. refresh.yml invokes the former; deploy.yml invokes the latter. site/data/ carved out of .gitignore by Plan 04 (.gitignore restructure) so the refresh PR can commit regenerated manifest + Parquet + CSV back."
  - phase: 04-publishing-layer-03
    provides: "tests/test_determinism.py + tests/test_schemas.py + tests/test_aggregates.py Parquet variants — refresh.yml's in-workflow gate invokes these BEFORE opening the PR. Plan 03 established the benchmark floor shape (test_benchmarks.py) which refresh.yml invokes as a separate step per D-18."
  - phase: 02-test-benchmark-scaffolding
    provides: ".github/workflows/ci.yml Phase-2 pattern (actions/checkout@v5 + astral-sh/setup-uv@v8.1.0 + uv sync --frozen + uv run --frozen). refresh.yml + deploy.yml reuse this cluster verbatim."

provides:
  - ".github/workflows/refresh.yml — daily 06:00 UTC cron + manual dispatch automation. In-workflow gates (refresh_all → benchmark floor → determinism/schema/aggregates/constants/manifest/csv_mirror pytest → plotting → mkdocs --strict) run BEFORE the PR is opened, ensuring reviewers see only clean passing diffs. Fail-loud: any step error opens a `refresh-failure` labelled issue via `peter-evans/create-issue-from-file@v6` using the new `.github/refresh-failure-template.md`. Permissions least-privilege: contents:write + pull-requests:write + issues:write."
  - ".github/workflows/deploy.yml — tag-triggered release-asset upload. Validates tag format `v<YYYY.MM>(-rc<N>)?` (D-14) before running `snapshot.py` and uploading the 16-file artefact tree (1 manifest.json + 5 parquet + 5 csv + 5 schema.json) via `softprops/action-gh-release@v2`. Permissions minimal: contents:write only. Release body embeds the manifest.json download URL — the durable citation anchor."
  - ".github/refresh-failure-template.md — GitHub Issue body template referenced by refresh.yml on failure. Lists the four most-likely failure modes (upstream schema drift, benchmark floor trip, mkdocs --strict breakage, determinism/schema gate failure) and reinforces the `refresh-failure` vs `correction` label distinction."

affects:
  - 04-06-docs-and-benchmark-floor  # Plan 06 activates the LCCC ARA 2024/25 self-reconciliation floor by filling tests/fixtures/benchmarks.yaml::lccc_self. The `Benchmark floor (LCCC self-reconciliation)` step in refresh.yml will become a real gate at that point — currently it skips 2 tests cleanly per D-11 fallback. No refresh.yml edit needed; the gate wires automatically once the YAML entries exist.
  - 05+                              # Every future scheme (RO, FiT, SEG, ...) appends one entry to refresh_all.SCHEMES; refresh.yml iterates that tuple verbatim without re-editing. Tag-push release workflow likewise inherits all schemes via snapshot.py which walks SCHEMES.

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GitHub Actions pinning discipline (supply-chain hygiene, T-04-05-02 mitigation): every `uses:` step in all three workflow files pinned to an explicit major version tag — no `@main`, no `@master`, no unpinned refs. Pins: actions/checkout@v5, astral-sh/setup-uv@v8.1.0, peter-evans/create-pull-request@v8, peter-evans/create-issue-from-file@v6, softprops/action-gh-release@v2. Acceptance-criteria grep `! grep -E 'uses:.*@(main|master)' .github/workflows/` enforces this per commit. Full SHA pinning not adopted per plan rationale (maintenance burden > supply-chain delta for a public open-data project)."
    - "Workflow-scoped least-privilege permissions (T-04-05-04 mitigation): each workflow declares its own top-level `permissions:` block, overriding the repo default. refresh.yml needs contents:write (branch push) + pull-requests:write (PR open) + issues:write (fail-loud issue). deploy.yml only needs contents:write (release asset upload). ci.yml unchanged (default read-only). Grep `! grep -E 'pull-requests:|issues:' .github/workflows/deploy.yml` verifies deploy.yml carries no excess write scopes."
    - "In-workflow gate BEFORE PR open (fail-fast reviewer UX): refresh.yml runs the full test pyramid (benchmark floor → determinism/schema/aggregates/constants/manifest/csv_mirror → plotting → mkdocs --strict) inside the refresh job BEFORE `peter-evans/create-pull-request@v8` fires. Consequence: if any gate fails, the failure step's `if: failure()` creates a refresh-failure Issue — the PR never opens, and the reviewer is not handed a broken diff. This compensates for Pitfall 2 (default GITHUB_TOKEN does not cascade ci.yml on PR open)."
    - "Tag-format validation as a job step (W-04): deploy.yml has an explicit `Validate tag format` bash step that regex-matches `^v[0-9]{4}\\.[0-9]{2}(-rc[0-9]+)?$` before any expensive work runs. Off-pattern pushes (e.g. `v1.0`, `v2026.4`, `vdev`) fail fast with a clear `::error::` annotation. Keeps calendar-tag discipline (D-14) enforceable in CI rather than by convention."
    - "PR body built from static template + runtime-only variables (T-04-05-03 mitigation): refresh.yml's PR body templating only interpolates github.run_id, github.repository, github.event.schedule, github.ref_name — all controlled by the GitHub Actions runtime, never scraper content. No `${{ steps.*.outputs.* }}` inlined from pipeline output could be hijacked by an upstream-returned string."

key-files:
  created:
    - ".github/workflows/refresh.yml — 89 lines. Daily cron + manual dispatch; in-workflow benchmark/determinism/schema/aggregates/manifest/csv_mirror gates; charts + docs --strict build; `peter-evans/create-pull-request@v8` opens daily-refresh-labelled PR on `refresh/<run_id>` branch with `add-paths: data/raw/ data/derived/ docs/charts/html/ site/data/`; `peter-evans/create-issue-from-file@v6` opens refresh-failure-labelled issue on any step failure. timeout-minutes: 30."
    - ".github/workflows/deploy.yml — 65 lines. Tag-trigger (`push: tags: ['v*']`); tag-format regex validation (D-14); `uv run python -m uk_subsidy_tracker.publish.snapshot --version ${{ github.ref_name }} --output snapshot-out/`; `softprops/action-gh-release@v2` uploads manifest.json + 3 globbed directories (**/*.parquet, **/*.csv, **/*.schema.json); release body carries citable manifest URL. timeout-minutes: 20."
    - ".github/refresh-failure-template.md — 19 lines. GitHub Issue body template; lists four canonical failure modes; calls out refresh-failure vs correction label distinction."
    - ".planning/phases/04-publishing-layer/04-05-SUMMARY.md (this file)"
  modified:
    - "CHANGES.md — [Unreleased] ### Added now leads with three new Plan 04-05 bullets (refresh.yml, deploy.yml, refresh-failure-template.md) in front of the Plan 04-04 publish/ package block. Each bullet cites controlling decisions (D-13/D-14/D-16/D-17/D-18), requirement IDs (GOV-03, PUB-03, GOV-06), pinned action majors, and documents Pitfall 2 + the REFRESH_PAT follow-up path."

key-decisions:
  - "peter-evans/create-pull-request pinned to @v8 (not @v6 which was the CONTEXT D-16 default). Research §Pattern 8 Assumption A8 authorised either v6 or v8; chose v8 as the current stable major. v8 is backwards-compatible with v6's inputs (commit-message, title, body, branch, labels, add-paths, delete-branch) — no action input change needed. If a future Node-runtime deprecation forces a v8-specific adjustment, it will surface in the action's own release notes and CI will break loudly on its deprecation warning."
  - "softprops/action-gh-release pinned to @v2 (NOT @v3). @v3 requires Node-24 which is not yet stable across all GitHub-hosted runners (per RESEARCH §Supporting Actions); v2 (v2.6.2) is Node-20-compatible and recommended for the current windows-latest / ubuntu-latest fleet. Revisit at Phase-4.1 or beyond when Node-24 reaches green across the matrix."
  - "In-workflow gate ordering: refresh_all → benchmark floor → determinism/schema/aggregates/constants/manifest/csv_mirror → charts → mkdocs. Rationale: (1) refresh_all must run first because the downstream tests read data/derived output; (2) benchmark floor fires cheaply against published LCCC aggregates — catches upstream schema/content drift before the expensive chart regen; (3) the pytest group bundles six test modules in one invocation (better runner turnaround than 6 separate pytest jobs); (4) charts + mkdocs --strict last because they regenerate derived output files the PR body adds via add-paths. Order matches the daily-refresh mental model: 'fetch fresh data, verify it, render it, ship it'."
  - "PAT for ci.yml cascade on refresh PR: NOT configured (Pitfall 2 documented in workflow header + CHANGES.md + PR body). A future Phase-4.1 follow-up would: (a) have user create REFRESH_PAT secret, (b) substitute ${{ secrets.REFRESH_PAT }} for the default token in the create-pull-request step, (c) also add `if: github.event_name != 'pull_request'` guard on refresh.yml to prevent the cascade loop T-04-05-07 calls out. Out of scope for Plan 04-05 per D-16 default posture."
  - "Tag-format validation as a script step (not an action): the D-14 format `v<YYYY.MM>(-rc<N>)?` is constrained enough to regex-match inline. Introducing a validation action (e.g. `mathieudutour/github-tag-action`) would bring another supply-chain dependency and more YAML for a 5-line bash step. Kept inline — grep-visible, no external action needed, and the `::error::` annotation renders identically to an action-level failure on the GitHub UI."
  - "deploy.yml permissions = contents:write only, NOT pull-requests or issues. Deploy strictly uploads release assets; no PR creation, no issue creation. Applying the minimum-permissions discipline (T-04-05-04 mitigation) per-workflow rather than uniformly — different workflows have different attack surfaces and different write-scope needs. Acceptance criterion `! grep -E 'pull-requests:|issues:' .github/workflows/deploy.yml` enforces this going forward."

patterns-established:
  - "Future scheme workflows inherit this pattern verbatim: refresh.yml's `uv run python -m uk_subsidy_tracker.refresh_all` iterates the SCHEMES tuple (currently just CfD); adding RO/FiT/SEG/etc. in Phase 5+ is a one-line edit to `refresh_all.SCHEMES` with NO workflow change. deploy.yml's snapshot.py invocation likewise walks SCHEMES, so release assets auto-grow as schemes ship."
  - "Fail-loud issue-on-any-step-failure is the reliability posture for automated cron workflows: `if: failure()` + `peter-evans/create-issue-from-file@v6` + `content-filepath` pointed at a committed markdown template. Future automated workflows (e.g. dependency drift scan, snapshot integrity audit) can copy this step verbatim with a workflow-specific label + template."
  - "Committed template + static PR body = hijacking-resistant automation (T-04-05-03). The refresh-failure template lives at `.github/refresh-failure-template.md` as a tracked file (not generated at runtime); refresh.yml only references it by path. Any future template content review happens at commit time, not inside the pipeline."

requirements-completed:
  - GOV-03    # Daily refresh CI workflow (06:00 UTC cron, dirty-check per scheme) — refresh.yml wired end-to-end
  - PUB-03    # Snapshot on tag release — deploy.yml fires on tag push, runs snapshot.py, uploads release assets

# GOV-06 was already closed in Plan 04-04 (versioned_url on every Dataset
# entry). Plan 04-05 ships the deploy.yml that makes those URLs resolvable
# — the citation anchor becomes end-to-end operational, not newly closed.

# Metrics
duration: 3min
completed: 2026-04-23
---

# Phase 4 Plan 05: Workflows — Refresh + Deploy Summary

**Wired the CI automation: `.github/workflows/refresh.yml` fires at 06:00 UTC daily (plus on-demand via workflow_dispatch) to run `refresh_all.py` + in-workflow test gates + `mkdocs build --strict` and open a `daily-refresh`-labelled PR via `peter-evans/create-pull-request@v8` when anything upstream changed; `.github/workflows/deploy.yml` fires on `git push --tags` (v* pattern), validates the D-14 calendar-tag format, runs `snapshot.py`, and uploads the 16-file artefact tree via `softprops/action-gh-release@v2`; both workflows carry least-privilege permissions, pinned actions only (no @main/@master), and fail-loud issue-on-step-failure via the new `.github/refresh-failure-template.md`. All five plan success criteria green; full pytest + mkdocs --strict green.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-04-22T23:59:19Z
- **Completed:** 2026-04-23T00:02:04Z
- **Tasks:** 3 completed (3/3)
- **Files changed:** 4 (3 new in .github/ + 1 CHANGES.md modification)

## Accomplishments

- **Daily-refresh automation is wired end-to-end.** `refresh.yml` fires at 06:00 UTC (cron `0 6 * * *`) and on `workflow_dispatch`. Pinned `actions/checkout@v5` + `astral-sh/setup-uv@v8.1.0` + `peter-evans/create-pull-request@v8` + `peter-evans/create-issue-from-file@v6` — no `@main`/`@master` refs anywhere. Permissions minimal: `contents: write + pull-requests: write + issues: write`. `timeout-minutes: 30` caps the worst-case run. In-workflow gates fire BEFORE the PR is opened: `refresh_all` → LCCC benchmark floor → six-module pytest gate (`test_determinism`, `test_schemas`, `test_aggregates`, `test_constants_provenance`, `test_manifest`, `test_csv_mirror`) → chart regen → `mkdocs build --strict`. Any failure fires `peter-evans/create-issue-from-file@v6` with label `refresh-failure` using the new `.github/refresh-failure-template.md`. Closes GOV-03.

- **Tag-triggered release automation is wired end-to-end.** `deploy.yml` fires on `push: tags: ['v*']`. First step validates the tag against the D-14 calendar format `^v[0-9]{4}\.[0-9]{2}(-rc[0-9]+)?$` — off-pattern pushes fail fast with a `::error::` annotation before any expensive step runs. Runs `uv run python -m uk_subsidy_tracker.publish.snapshot --version ${{ github.ref_name }} --output snapshot-out/` (matches the Plan 04-04 snapshot CLI contract). Uploads via `softprops/action-gh-release@v2` with an explicit 4-glob allowlist: `manifest.json` + `**/*.parquet` + `**/*.csv` + `**/*.schema.json`. Permissions `contents: write` only — no pr/issues. Release body embeds the manifest.json download URL, the durable citation anchor. Closes PUB-03 and operationalises GOV-06's snapshot-URL portion (closed at manifest-field level in Plan 04-04).

- **Fail-loud issue-on-failure pattern shipped.** The `refresh-failure-template.md` enumerates four canonical failure modes (upstream schema drift, benchmark floor trip, `mkdocs --strict` breakage, determinism/schema gate failure) and calls out the `refresh-failure` vs `correction` label distinction (D-17). Future automated workflows can copy this step + template shape verbatim.

- **Supply-chain hygiene is grep-verifiable.** `! grep -rE 'uses:.*@(main|master)' .github/workflows/` returns no matches across all three workflow files (refresh.yml + deploy.yml + the pre-existing ci.yml). Every pinned action is at an explicit major version tag. `grep -qE "pull-requests:|issues:" .github/workflows/deploy.yml` returns no matches — deploy.yml's least-privilege posture is grep-enforceable going forward.

- **Pitfall 2 documented, not fought.** The default `GITHUB_TOKEN` will NOT trigger downstream `ci.yml` workflows on the refresh PR. Rather than add a PAT (which would require user secret setup + a cascade-loop guard), the plan ships in-workflow gates that run BEFORE the PR opens — the reviewer sees only clean passing diffs. CHANGES.md + the refresh.yml header + the PR body all document this posture + the REFRESH_PAT follow-up path for future upgrade.

## Task Commits

Each task was committed atomically:

1. **Task 1: refresh.yml + refresh-failure-template.md** — `f3b9e33` (feat)
2. **Task 2: deploy.yml** — `bbb421d` (feat)
3. **Task 3: CHANGES.md entry** — `20b7701` (docs)

**Test count:** 69 passed + 4 skipped — zero regressions (workflows do not affect tests; verified with `uv run --frozen pytest -q` at HEAD).

## Action Pins (supply-chain audit)

| Action | Pinned version | Used in |
|---|---|---|
| `actions/checkout` | `@v5` | ci.yml, refresh.yml, deploy.yml |
| `astral-sh/setup-uv` | `@v8.1.0` | ci.yml, refresh.yml, deploy.yml |
| `peter-evans/create-pull-request` | `@v8` | refresh.yml |
| `peter-evans/create-issue-from-file` | `@v6` | refresh.yml |
| `softprops/action-gh-release` | `@v2` | deploy.yml |

No `@main` or `@master` refs. No full-SHA pins (per CONTEXT discretion — maintenance burden > supply-chain delta for this public open-data project; reconsider if repo moves to paid Enterprise).

## User Setup Required

Two GitHub-dashboard-only steps the user must complete before the first refresh run can succeed end-to-end:

1. **Enable "Allow GitHub Actions to create and approve pull requests"** at https://github.com/richardjlyon/uk-subsidy-tracker/settings/actions (Settings → Actions → General → Workflow permissions). Required by `peter-evans/create-pull-request@v8`.
2. **Create two labels** at https://github.com/richardjlyon/uk-subsidy-tracker/labels:
   - `daily-refresh` (blue) — applied to every refresh PR
   - `refresh-failure` (red) — applied to every fail-loud issue
   Distinct from the pre-existing `correction` label (Phase 1), which tracks published corrections rather than automation breakage (D-17).

Neither step was performed by the executor (agent cannot authenticate to the GitHub web UI on behalf of the user). The workflows will run on the next scheduled tick regardless; the PR/Issue creation steps will error loudly if either setup item is missing.

**Smoke test (post-user-setup):** `gh workflow run refresh.yml` from a feature branch triggers the manual-dispatch path. Expected outcome on clean state: `refresh_all` short-circuits with "no upstream changes; skipping manifest rebuild" (Pitfall 3), all gates pass, no PR opens (nothing to commit), no failure issue opens. Confirms the wiring without requiring actual upstream content changes.

## Deviations from Plan

None — plan executed exactly as written.

- All three tasks completed in the specified order.
- YAML authored verbatim from the plan's `<action>` blocks (which were themselves verbatim from RESEARCH §Pattern 8 + the CONTEXT decision tables).
- No Rule-1/2/3 auto-fixes needed.
- No auth gates (no GitHub API calls performed by the executor — workflow files live on disk; runtime is GitHub Actions).
- Plan's `<success_criteria>` and `<verification>` blocks pass 100%.

## Issues Encountered

None. Both YAML files parsed cleanly on first write; the full pytest suite + `mkdocs build --strict` stayed green; no destabilisation of the existing ci.yml pipeline.

Known non-blocker carried forward from Plan 04-04: the benign `RuntimeWarning` emitted by `python -m uk_subsidy_tracker.publish.snapshot` (publish/__init__.py eagerly imports snapshot, and `-m` re-executes it). Does not affect functionality; deferred to future workflow tweak (`-W ignore::RuntimeWarning` on the snapshot step in deploy.yml) if the warning noise becomes operational friction.

## Verification Results

**Plan `<success_criteria>` block:**

| Criterion | Result |
|---|---|
| `.github/workflows/refresh.yml` exists and parses as valid YAML | PASS (`yaml.safe_load` clean) |
| `.github/workflows/deploy.yml` exists and parses as valid YAML | PASS (`yaml.safe_load` clean) |
| `.github/refresh-failure-template.md` exists | PASS |
| All third-party actions pinned to explicit major versions; no @main or @master | PASS (grep `! grep -rE 'uses:.*@(main\|master)' .github/workflows/` empty) |
| Permissions blocks are least-privilege (ci.yml unchanged read-only; refresh.yml write on contents+pr+issues; deploy.yml write on contents only) | PASS (three separate grep checks green) |
| refresh.yml fires on cron + workflow_dispatch | PASS |
| deploy.yml fires on tag push matching `v*` | PASS |
| refresh.yml invokes refresh_all.py + test gates + mkdocs strict + create-PR + create-issue-on-failure | PASS |
| deploy.yml invokes snapshot.py + softprops release upload | PASS |
| `uv run pytest tests/` still green after YAML adds | PASS (69 passed + 4 skipped) |
| `CHANGES.md` records both workflows + template | PASS (6/6 grep checks green) |
| user_setup documents the two dashboard-only steps | PASS (documented in plan frontmatter + this summary) |

**Plan `<verification>` block:**

| Check | Result |
|---|---|
| `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh.yml')); yaml.safe_load(open('.github/workflows/deploy.yml'))"` → exits 0 | PASS ("Both YAMLs parse") |
| `! grep -rE 'uses:.*@(main\|master)' .github/workflows/` returns no matches | PASS |
| `test -f .github/refresh-failure-template.md` | PASS |
| `uv run pytest tests/` still green | PASS (69 passed + 4 skipped) |
| Manual (GitHub dashboard): "Allow GitHub Actions to create and approve pull requests" enabled | DEFERRED to user (dashboard-only step, plan `user_setup`) |
| Manual (GitHub dashboard): labels `daily-refresh` + `refresh-failure` created | DEFERRED to user (dashboard-only step, plan `user_setup`) |
| Smoke test: `gh workflow run refresh.yml` from a feature branch | DEFERRED — requires post-merge commit on main + user setup complete |
| Snapshot dry-run (pre-Phase-5 checkpoint): `git tag v2026.04-rc1 && git push --tags` | DEFERRED to user (tag push is intentional user action, not executor-automated) |

**Per-task acceptance criteria:** all 3 tasks hit 100% of their declared criteria (every grep check green, both YAMLs parse, files exist, test suite green, mkdocs strict green).

## Open Follow-up (deferred to Phase 4.1)

**PAT-based ci.yml cascade for refresh PR** (per D-16, Pitfall 2, CONTEXT Open Q2). Default posture shipped today: in-workflow gates run BEFORE PR open; reviewer sees clean diffs; if they want pytest to re-run on the PR branch specifically, they `gh workflow run ci.yml --ref refresh/<run_id>` manually. Upgrade path when it becomes operational friction:

1. User creates `REFRESH_PAT` classic token with `repo` scope (or fine-grained with `contents: write + pull-requests: write`) and stores as repo secret.
2. Add `token: ${{ secrets.REFRESH_PAT }}` to the `peter-evans/create-pull-request@v8` step.
3. Add `if: github.event_name != 'pull_request'` guard to the top-level `refresh` job to prevent the ci.yml → refresh.yml cascade loop (T-04-05-07).
4. Document the secret + guard in CHANGES.md + the refresh.yml header.

This is a Phase 4.1 candidate, not a Phase 4 blocker.

## Next Plan Readiness

**Plan 04-06 (docs + benchmark floor) is fully unblocked.** With workflows shipped, Plan 06 can:
- Author `docs/data/index.md` journalist-how-to with DuckDB + pandas + R snippets that fetch `manifest.json` (published by the daily refresh) and follow URL fields to Parquet/CSV — full end-to-end citation workflow.
- Activate the LCCC ARA 2024/25 self-reconciliation floor by transcribing the calendar-year CfD aggregate into `tests/fixtures/benchmarks.yaml::lccc_self`. The `Benchmark floor (LCCC self-reconciliation)` step in refresh.yml already invokes `tests/test_benchmarks.py` — no workflow edit needed when the YAML fills.
- Demonstrate the versioned-URL citation pattern (`https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v2026.04/manifest.json`) as the durable academic anchor now that deploy.yml exists.

**No known blockers** for Plan 04-06, the final plan in Phase 4.

## Self-Check: PASSED

- [x] `.github/workflows/refresh.yml` exists (89 lines)
- [x] `.github/workflows/deploy.yml` exists (65 lines)
- [x] `.github/refresh-failure-template.md` exists (19 lines)
- [x] Both workflow YAMLs parse via `yaml.safe_load`
- [x] No `@main`/`@master` refs in `.github/workflows/` (grep empty)
- [x] refresh.yml pins: actions/checkout@v5, astral-sh/setup-uv@v8.1.0, peter-evans/create-pull-request@v8, peter-evans/create-issue-from-file@v6
- [x] deploy.yml pins: actions/checkout@v5, astral-sh/setup-uv@v8.1.0, softprops/action-gh-release@v2
- [x] refresh.yml carries `permissions: contents: write + pull-requests: write + issues: write`
- [x] deploy.yml carries `permissions: contents: write` only (no pr/issues)
- [x] refresh.yml cron `'0 6 * * *'` + `workflow_dispatch`
- [x] deploy.yml trigger `push: tags: ['v*']`
- [x] refresh.yml invokes `uk_subsidy_tracker.refresh_all`
- [x] refresh.yml invokes `tests/test_benchmarks.py`
- [x] refresh.yml invokes `mkdocs build --strict`
- [x] refresh.yml has `if: failure()` issue-on-failure step with `content-filepath: ./.github/refresh-failure-template.md`
- [x] refresh.yml labels: `daily-refresh` (PR) + `refresh-failure` (Issue)
- [x] refresh.yml timeout-minutes: 30
- [x] deploy.yml has tag-format validation step (D-14 regex)
- [x] deploy.yml invokes `uk_subsidy_tracker.publish.snapshot` with `--version` + `--output snapshot-out/`
- [x] deploy.yml upload globs: manifest.json + **/*.parquet + **/*.csv + **/*.schema.json
- [x] deploy.yml release body references `releases/download/` URL (GOV-06 anchor)
- [x] CHANGES.md modified (refresh.yml, deploy.yml, refresh-failure, daily-refresh, peter-evans actions, GOV-03/PUB-03/GOV-06/D-numbers all grep-present)
- [x] Commit `f3b9e33` in git log (Task 1: feat refresh workflow + template)
- [x] Commit `bbb421d` in git log (Task 2: feat deploy workflow)
- [x] Commit `20b7701` in git log (Task 3: docs CHANGES)
- [x] Full test suite: 69 passed + 4 skipped
- [x] `uv run mkdocs build --strict` — exit 0 in 0.42s

---
*Phase: 04-publishing-layer*
*Plan: 05 (Wave 5 — workflows: refresh + deploy)*
*Completed: 2026-04-23*
