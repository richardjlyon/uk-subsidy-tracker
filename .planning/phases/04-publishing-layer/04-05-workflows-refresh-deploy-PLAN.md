---
phase: 04-publishing-layer
plan: 05
type: execute
wave: 5
depends_on:
  - 01
  - 02
  - 03
  - 04
files_modified:
  - .github/workflows/refresh.yml
  - .github/workflows/deploy.yml
  - .github/refresh-failure-template.md
  - CHANGES.md
autonomous: true
requirements:
  - GOV-03  # Daily refresh CI with per-scheme dirty-check
  - GOV-06  # Snapshot URL portion — deploy.yml fires on git tag push, produces release assets
  - PUB-03  # Snapshot on tag release
tags: [workflows, ci, cron, release, github-actions]
user_setup:
  - service: github-repo-settings
    why: "peter-evans/create-pull-request v8 requires the repo setting 'Allow GitHub Actions to create and approve pull requests' to be enabled; default GITHUB_TOKEN cannot cascade to ci.yml on refresh PRs (design; see D-16)."
    dashboard_config:
      - task: "Verify Settings → Actions → General → Workflow permissions: 'Allow GitHub Actions to create and approve pull requests' is ON"
        location: "https://github.com/richardjlyon/uk-subsidy-tracker/settings/actions"
      - task: "Create label `daily-refresh` (blue) and `refresh-failure` (red) via GitHub web UI or `gh label create`. Distinct from existing `correction` label (Phase 1)."
        location: "https://github.com/richardjlyon/uk-subsidy-tracker/labels"

must_haves:
  truths:
    - ".github/workflows/refresh.yml exists; fires on schedule (06:00 UTC) and workflow_dispatch"
    - ".github/workflows/deploy.yml exists; fires on git tag push (v*) and runs snapshot.py"
    - "Permissions blocks are least-privilege: refresh.yml = contents:write + pull-requests:write + issues:write; deploy.yml = contents:write only; ci.yml unchanged (default read)"
    - "Actions pinned to exact major versions (peter-evans/create-pull-request@v8, peter-evans/create-issue-from-file@v6, softprops/action-gh-release@v2, actions/checkout@v5, astral-sh/setup-uv@v8.1.0)"
    - "refresh-failure-template.md is a valid Markdown file referenced from refresh.yml"
    - "YAML parses cleanly (yamllint or python-yaml.safe_load succeeds); no action references `@main` or `@master` (supply-chain hygiene)"
    - "workflow_dispatch on refresh.yml allows manual trigger for initial smoke test"
  artifacts:
    - path: ".github/workflows/refresh.yml"
      provides: "Daily 06:00 UTC cron — runs refresh_all → mkdocs build --strict → peter-evans/create-pull-request if any diff; peter-evans/create-issue-from-file on failure"
      contains: "cron"
      min_lines: 50
    - path: ".github/workflows/deploy.yml"
      provides: "Tag-triggered (push: tags ['v*']) — runs snapshot.py and softprops/action-gh-release@v2 to upload artifacts"
      contains: "softprops/action-gh-release"
      min_lines: 30
    - path: ".github/refresh-failure-template.md"
      provides: "GitHub Issue body template referenced by refresh-failure step"
      min_lines: 10
  key_links:
    - from: ".github/workflows/refresh.yml"
      to: "src/uk_subsidy_tracker/refresh_all.py"
      via: "uv run --frozen python -m uk_subsidy_tracker.refresh_all"
      pattern: "refresh_all"
    - from: ".github/workflows/refresh.yml"
      to: "tests/test_benchmarks.py"
      via: "uv run --frozen pytest tests/test_benchmarks.py (LCCC floor gate BEFORE PR open)"
      pattern: "test_benchmarks"
    - from: ".github/workflows/deploy.yml"
      to: "src/uk_subsidy_tracker/publish/snapshot.py"
      via: "uv run --frozen python -m uk_subsidy_tracker.publish.snapshot --version ... --output snapshot-out/"
      pattern: "publish.snapshot"
    - from: ".github/workflows/deploy.yml"
      to: "GitHub Releases (remote)"
      via: "softprops/action-gh-release@v2 upload files glob from snapshot-out/"
      pattern: "snapshot-out"
    - from: ".github/workflows/refresh.yml"
      to: ".github/refresh-failure-template.md"
      via: "peter-evans/create-issue-from-file@v6 content-filepath: ./.github/refresh-failure-template.md"
      pattern: "refresh-failure-template"
---

<objective>
Wire the GitHub Actions automation: a daily 06:00 UTC cron workflow
(`refresh.yml`) that runs `refresh_all.py` and opens a PR with any diff
(human reviews before merge — D-16 PR-based commit-back posture); a
tag-triggered release workflow (`deploy.yml`) that assembles the versioned
snapshot via `snapshot.py` and uploads it as release assets via
`softprops/action-gh-release@v2` (D-13); a markdown issue template the
refresh workflow references on failure (D-17 `refresh-failure` label).

Purpose: Phase-4 exit criterion #5 (daily refresh workflow committed and
functional) — GOV-03; PUB-03 + GOV-06 snapshot URL citable via release
artifact.

Out of scope: Cloudflare Pages `_redirects` rule for `v<date>/` virtual
URLs (Open Question 4) — default decision is "use Cloudflare Pages
_redirects file; plan-checker files it if/when it becomes needed." The
release-asset URL that `manifest.json::versioned_url` references is
directly citable without a redirect layer — that's acceptable per D-13.

Output: three new files in `.github/`; minimal-permissions surface on each
workflow; refresh PRs labelled `daily-refresh`; refresh failures open
issues labelled `refresh-failure`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/phases/04-publishing-layer/04-CONTEXT.md
@.planning/phases/04-publishing-layer/04-RESEARCH.md
@.planning/phases/04-publishing-layer/04-PATTERNS.md
@.planning/phases/04-04-SUMMARY.md
@.github/workflows/ci.yml

<interfaces>
<!-- Full ci.yml (Phase-2) to copy the astral-sh + actions/checkout idiom verbatim -->

```yaml
# .github/workflows/ci.yml:1-46 (existing; do NOT modify in this plan)
name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
      - name: Install dependencies
        run: uv sync --frozen
      - name: Run tests
        run: uv run --frozen pytest -v
  docs:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v5
      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
      - name: Install dependencies
        run: uv sync --frozen
      - name: Regenerate charts
        run: uv run --frozen python -m uk_subsidy_tracker.plotting
      - name: Build docs --strict
        run: uv run --frozen mkdocs build --strict
```

<!-- Refresh-workflow behaviour decision table (from CONTEXT D-16/D-17/D-18 + RESEARCH §Pattern 8 + Open Q1) -->

| Decision | Value | Rationale |
|----------|-------|-----------|
| Cron schedule | `0 6 * * *` (06:00 UTC) | LCCC publishes overnight; by 06:00 UTC the day's data is available |
| Manual trigger | `workflow_dispatch` enabled | Allows ops-team manual smoke runs |
| PR action | `peter-evans/create-pull-request@v8` | v8 is current major; D-16 default said v6 — either works; v8 chosen per RESEARCH Assumption A8 |
| Issue action | `peter-evans/create-issue-from-file@v6` | Latest major; D-17 fail-loud posture |
| PAT for CI cascade | NO | RESEARCH Open Q2 + A4 — default posture; reviewer manually triggers ci.yml on refresh PR or relies on pre-PR workflow checks |
| Permissions | `contents: write` + `pull-requests: write` + `issues: write` | Needed by peter-evans actions |
| Timeout | 30 min | Per ARCHITECTURE §7.3 sub-5-min typical; 30-min cap for worst case |
| Branch name | `refresh/${{ github.run_id }}` | Unique per run; `delete-branch: true` on PR close |
| PR label | `daily-refresh` | New label (user creates via dashboard per user_setup) |
| Issue label | `refresh-failure` | New label |
| File paths to add to PR | `data/raw/`, `data/derived/`, `docs/charts/html/`, `site/data/` | Full regenerated subtree |

<!-- Deploy-workflow decision table (from CONTEXT D-13/D-14 + RESEARCH §Pattern 8) -->

| Decision | Value |
|----------|-------|
| Trigger | `push: tags: ['v*']` |
| Tag name example | `v2026.04` (calendar-based, D-14) |
| snapshot.py invocation | `uv run --frozen python -m uk_subsidy_tracker.publish.snapshot --version "${{ github.ref_name }}" --output snapshot-out/` |
| Release-asset upload | `softprops/action-gh-release@v2` with files glob `snapshot-out/**/*` |
| Permissions | `contents: write` only |
| Release body | Manifest URL + link back to CHANGES.md entry |
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author .github/workflows/refresh.yml</name>
  <files>.github/workflows/refresh.yml, .github/refresh-failure-template.md</files>
  <read_first>
    - .github/workflows/ci.yml (Phase-2 pattern — copy checkout + setup-uv verbatim)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 8 lines 1062-1139 (refresh.yml full template), Pitfall 2 (GITHUB_TOKEN cascade limitation — documented as accepted)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-16, D-17, D-18
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §H (workflow pinning discipline)
  </read_first>
  <action>
    ### Step 1A — `.github/refresh-failure-template.md`

    ```markdown
    <!-- Referenced by .github/workflows/refresh.yml on step failure.
         Rendered as GitHub Issue body via peter-evans/create-issue-from-file@v6.
         Label applied: `refresh-failure`. -->

    The daily refresh workflow failed.

    **Run:** https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
    **Triggered:** ${{ github.event.schedule || 'manual' }}

    Check the run logs for the failing step. Common causes:

    - LCCC / Elexon / ONS upstream server returned a non-200 response or changed schema (pandera validation fired in a loader).
    - Benchmark floor (`test_lccc_self_reconciliation_floor`) tripped — pipeline divergence from published LCCC calendar-year total exceeded 0.1%.
    - `mkdocs build --strict` surfaced a broken link or nav omission.
    - Determinism test or schema conformance test failed (pyarrow writer drift, Pydantic schema mismatch, or raw file content drift with unchanged sidecar).

    **Label:** `refresh-failure` (distinct from `correction`, which tracks published corrections).

    Assign to the maintainer reviewer; re-run after root-cause fix. Do NOT close this issue without a documented resolution.
    ```

    ### Step 1B — `.github/workflows/refresh.yml`

    Full file. Pin every action to an explicit major; use Phase-2 ci.yml's
    verbatim setup-uv block. Reproduce RESEARCH §Pattern 8 lines 1062-1139
    with the exact decisions from the interface block above:

    ```yaml
    # .github/workflows/refresh.yml
    # Daily data-refresh automation (Phase 4 GOV-03, D-16/D-17/D-18).
    #
    # Decisions:
    #   - PR-based commit-back (NOT direct commit to main) so a human reviews
    #     every day's diff before it goes live on Cloudflare Pages.
    #   - `peter-evans/create-pull-request@v8` — current stable major.
    #   - PAT for cascading ci.yml on the refresh PR: NOT configured — relies
    #     on in-workflow `pytest -v` + `mkdocs build --strict` before PR open.
    #     If a future maintainer wants full ci.yml to re-run on the PR, create
    #     a REFRESH_PAT secret with `contents: write` + `pull-requests: write`
    #     and substitute `${{ secrets.REFRESH_PAT }}` for the default token below.
    #   - Fail-loud on any step: the final `peter-evans/create-issue-from-file`
    #     step opens a `refresh-failure` issue with the template in
    #     `.github/refresh-failure-template.md`.
    name: Daily Refresh

    on:
      schedule:
        - cron: '0 6 * * *'          # 06:00 UTC
      workflow_dispatch:               # manual trigger for smoke tests

    permissions:
      contents: write                  # push the refresh branch
      pull-requests: write             # peter-evans/create-pull-request@v8
      issues: write                    # peter-evans/create-issue-from-file@v6

    jobs:
      refresh:
        runs-on: ubuntu-latest
        timeout-minutes: 30

        steps:
          - uses: actions/checkout@v5
            with:
              fetch-depth: 0           # git log --follow for sidecar git ops

          - name: Install uv
            uses: astral-sh/setup-uv@v8.1.0
            with:
              enable-cache: true
              python-version: "3.12"

          - name: Install deps
            run: uv sync --frozen

          - name: Refresh (per-scheme dirty-check)
            id: refresh
            run: uv run --frozen python -m uk_subsidy_tracker.refresh_all

          - name: Benchmark floor (LCCC self-reconciliation)
            run: uv run --frozen pytest tests/test_benchmarks.py -v

          - name: Determinism + schema + aggregates gate
            run: uv run --frozen pytest tests/test_determinism.py tests/test_schemas.py tests/test_aggregates.py tests/test_constants_provenance.py tests/test_manifest.py tests/test_csv_mirror.py -v

          - name: Regenerate charts
            run: uv run --frozen python -m uk_subsidy_tracker.plotting

          - name: Build docs --strict
            run: uv run --frozen mkdocs build --strict

          - name: Open PR if anything changed
            uses: peter-evans/create-pull-request@v8
            with:
              commit-message: "chore(refresh): daily data refresh ${{ github.run_id }}"
              title: "Daily refresh ${{ github.run_id }}"
              body: |
                Automated daily refresh opened by refresh.yml.

                **Run:** https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}

                Review the Parquet / CSV / chart / manifest diffs below before merging. CI on this PR will NOT trigger automatically with the default `GITHUB_TOKEN` (Pitfall 2 — security feature); dispatch ci.yml manually on this branch if a full test re-run is needed before merge.
              branch: refresh/${{ github.run_id }}
              delete-branch: true
              labels: daily-refresh
              add-paths: |
                data/raw/
                data/derived/
                docs/charts/html/
                site/data/

          - name: Open issue on any-step failure
            if: failure()
            uses: peter-evans/create-issue-from-file@v6
            with:
              title: "Refresh failure — run ${{ github.run_id }}"
              content-filepath: ./.github/refresh-failure-template.md
              labels: refresh-failure
    ```
  </action>
  <verify>
    <automated>test -f .github/workflows/refresh.yml &amp;&amp; test -f .github/refresh-failure-template.md &amp;&amp; uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh.yml'))"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .github/workflows/refresh.yml` exits 0
    - `test -f .github/refresh-failure-template.md` exits 0
    - Valid YAML: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh.yml'))"` exits 0
    - Cron schedule correct: `grep -q "cron: '0 6 \* \* \*'" .github/workflows/refresh.yml` OR similar quote style
    - `grep -q "workflow_dispatch" .github/workflows/refresh.yml` exits 0
    - Permissions block present: `grep -qE "^\s*contents:\s*write" .github/workflows/refresh.yml` exits 0
    - `grep -qE "^\s*pull-requests:\s*write" .github/workflows/refresh.yml` exits 0
    - `grep -qE "^\s*issues:\s*write" .github/workflows/refresh.yml` exits 0
    - Actions pinned (not @main or @master): `! grep -E 'uses:.*@(main|master)' .github/workflows/refresh.yml` returns no matches
    - Specific pins: `grep -q "actions/checkout@v5" .github/workflows/refresh.yml` AND `grep -q "astral-sh/setup-uv@v8.1.0" .github/workflows/refresh.yml` AND `grep -q "peter-evans/create-pull-request@v8" .github/workflows/refresh.yml` AND `grep -q "peter-evans/create-issue-from-file@v6" .github/workflows/refresh.yml`
    - `grep -q "refresh_all" .github/workflows/refresh.yml` exits 0
    - `grep -q "test_benchmarks" .github/workflows/refresh.yml` exits 0
    - `grep -q "mkdocs build --strict" .github/workflows/refresh.yml` exits 0
    - Issue-on-failure wired: `grep -q "if: failure()" .github/workflows/refresh.yml` exits 0
    - `grep -q "refresh-failure-template.md" .github/workflows/refresh.yml` exits 0
    - Template file has run_id reference: `grep -q "github.run_id" .github/refresh-failure-template.md` exits 0
    - `grep -q "refresh-failure" .github/workflows/refresh.yml` exits 0 (label assignment)
    - `grep -q "daily-refresh" .github/workflows/refresh.yml` exits 0 (label assignment)
    - `grep -q "timeout-minutes: 30" .github/workflows/refresh.yml` exits 0
  </acceptance_criteria>
  <done>refresh.yml + refresh-failure-template.md ship with least-privilege permissions, pinned actions, cron + manual dispatch, in-workflow test gates BEFORE PR open, and fail-loud issue creation on any step error.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Author .github/workflows/deploy.yml</name>
  <files>.github/workflows/deploy.yml</files>
  <read_first>
    - .github/workflows/ci.yml (Phase-2 checkout + setup-uv pattern)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 8 lines 1161-1201 (deploy.yml template)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-13, D-14
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §H (action pinning)
    - src/uk_subsidy_tracker/publish/snapshot.py (CLI contract: --version, --output)
  </read_first>
  <action>
    ```yaml
    # .github/workflows/deploy.yml
    # Versioned-snapshot release workflow (Phase 4 PUB-03, GOV-06, D-13/D-14).
    #
    # Fires on `git push --tags` where the tag matches `v*` (e.g. `v2026.04`,
    # `v2026.04-rc1`, `v2027.01`). Builds a self-contained snapshot via
    # `snapshot.py` and uploads the contents as release assets.
    #
    # The manifest.json inside the snapshot carries `versioned_url` fields
    # that point at the release asset URLs — academics cite these in papers;
    # GitHub's release storage is effectively permanent.
    name: Release snapshot

    on:
      push:
        tags:
          - 'v*'

    permissions:
      contents: write                  # upload release assets only

    jobs:
      release:
        runs-on: ubuntu-latest
        timeout-minutes: 20

        steps:
          - uses: actions/checkout@v5

          - name: Install uv
            uses: astral-sh/setup-uv@v8.1.0
            with:
              enable-cache: true
              python-version: "3.12"

          - name: Install deps
            run: uv sync --frozen

          - name: Build snapshot artifacts
            run: |
              uv run --frozen python -m uk_subsidy_tracker.publish.snapshot \
                --version "${{ github.ref_name }}" \
                --output snapshot-out/

          - name: Publish release assets
            uses: softprops/action-gh-release@v2
            with:
              files: |
                snapshot-out/manifest.json
                snapshot-out/**/*.parquet
                snapshot-out/**/*.csv
                snapshot-out/**/*.schema.json
              body: |
                Immutable snapshot ${{ github.ref_name }}.

                **Manifest:** https://github.com/${{ github.repository }}/releases/download/${{ github.ref_name }}/manifest.json

                See the manifest for dataset URLs and SHA-256 checksums. Every figure in this release is reproducible from `git clone` at the tag + `uv sync --frozen` + `uv run python -m uk_subsidy_tracker.refresh_all`.
    ```
  </action>
  <verify>
    <automated>test -f .github/workflows/deploy.yml &amp;&amp; uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .github/workflows/deploy.yml` exits 0
    - Valid YAML: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"` exits 0
    - Trigger correct: `grep -qE "tags:[[:space:]]*\[.*v\*" .github/workflows/deploy.yml || grep -qE "['\"]v\*['\"]" .github/workflows/deploy.yml`
    - Permissions tight: `grep -qE "^\s*contents:\s*write" .github/workflows/deploy.yml` exits 0
    - `! grep -E 'pull-requests:|issues:' .github/workflows/deploy.yml` returns no matches (deploy does NOT need those)
    - Actions pinned: `grep -q "actions/checkout@v5" .github/workflows/deploy.yml` AND `grep -q "astral-sh/setup-uv@v8.1.0" .github/workflows/deploy.yml` AND `grep -q "softprops/action-gh-release@v2" .github/workflows/deploy.yml`
    - `! grep -E 'uses:.*@(main|master)' .github/workflows/deploy.yml` returns no matches
    - snapshot.py invoked: `grep -q "uk_subsidy_tracker.publish.snapshot" .github/workflows/deploy.yml` exits 0
    - `--version` flag passed: `grep -q '[-]-version' .github/workflows/deploy.yml` exits 0
    - `github.ref_name` used for version: `grep -q "github.ref_name" .github/workflows/deploy.yml` exits 0
    - `--output snapshot-out/` used: `grep -q 'snapshot-out' .github/workflows/deploy.yml` exits 0
    - files glob present for all 4 artefact types: `grep -c "snapshot-out/\*\*" .github/workflows/deploy.yml` ≥ 3 (manifest.json is a single path; **/*.parquet + **/*.csv + **/*.schema.json are 3)
    - Release body references manifest URL: `grep -q "releases/download" .github/workflows/deploy.yml` exits 0
  </acceptance_criteria>
  <done>deploy.yml ships with minimal permissions, pinned actions, snapshot.py CLI invocation matching its contract, and release-asset upload glob covering all four artefact types.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: CHANGES.md entry for workflows</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md (existing [Unreleased] — Plans 01-04 entries)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-13/D-14/D-16/D-17/D-18
  </read_first>
  <action>
    Under `### Added`:

    ```markdown
    - `.github/workflows/refresh.yml` — daily 06:00 UTC cron automation. PR-based posture (D-16): scheme dirty-check (`refresh_all.py`) runs on a scheduled trigger; if any raw file's SHA-256 drifted, workflow regenerates Parquet + charts + manifest + rebuilds docs, then opens a PR on `refresh/<run_id>` via `peter-evans/create-pull-request@v8` with label `daily-refresh`. In-workflow test gates (benchmark floor, determinism, schema, aggregates, constants drift, manifest round-trip, CSV mirror) run BEFORE the PR is opened — catches issues upstream of the reviewer. On any step failure, `peter-evans/create-issue-from-file@v6` opens an Issue with label `refresh-failure` using the new `.github/refresh-failure-template.md` (distinct from the `correction` label — automation-breakage vs published-corrections are different concerns, D-17). Permissions least-privilege: `contents: write + pull-requests: write + issues: write`. Default `GITHUB_TOKEN` does not cascade to `ci.yml` on the refresh PR (Pitfall 2 — a GitHub security feature); reviewers dispatch ci.yml manually if they want a pre-merge test run. Adding `REFRESH_PAT` is a future Phase-4.1 option documented in the workflow file.
    - `.github/workflows/deploy.yml` — on `git push --tags` matching `v*`, assembles a self-contained versioned snapshot via `uk_subsidy_tracker.publish.snapshot` and uploads the manifest + per-table parquet/csv/schema.json as release assets via `softprops/action-gh-release@v2`. The `manifest.json::versioned_url` fields resolve to these release-asset URLs — academic citations are durable because GitHub releases are retention-guaranteed (D-13, D-14, GOV-06).
    - `.github/refresh-failure-template.md` — GitHub Issue body template referenced by refresh.yml on failure.
    ```
  </action>
  <verify>
    <automated>grep -q "refresh.yml" CHANGES.md &amp;&amp; grep -q "deploy.yml" CHANGES.md &amp;&amp; grep -q "refresh-failure" CHANGES.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "refresh.yml" CHANGES.md` exits 0
    - `grep -q "deploy.yml" CHANGES.md` exits 0
    - `grep -q "refresh-failure" CHANGES.md` exits 0
    - `grep -q "daily-refresh" CHANGES.md` exits 0
    - `grep -q "peter-evans/create-pull-request\|peter-evans/create-issue-from-file\|softprops/action-gh-release" CHANGES.md` exits 0
    - `grep -q "GOV-03\|PUB-03\|GOV-06\|D-1[3-8]" CHANGES.md` exits 0 (at least one req ID or decision ref)
    - `uv run mkdocs build --strict` green
  </acceptance_criteria>
  <done>CHANGES.md records the full workflow shipment + rationale + known PAT limitation.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries (primary Phase-4 security carrier — per planning context)

| Boundary | Description |
|----------|-------------|
| `GITHUB_TOKEN` (auto-generated) → repo write operations | Workflows run under this token; default scope is repo-level with workflow-level permission gates. |
| Third-party action version (`peter-evans/*`, `softprops/*`, `astral-sh/*`, `actions/*`) → pipeline behaviour | An action pinned to `@main` could be hijacked via upstream commit; pinning to a version tag or SHA is required. |
| Upstream data content (LCCC / Elexon / ONS responses) → PR body / Issue body | Untrusted input: a malicious upstream could attempt to inject markdown / shell via body templating. |
| Release assets uploaded from `snapshot-out/` → public GitHub Releases | Overwrite or mis-naming could break citation lineage. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-05-01 (T-04-W) | Elevation of Privilege | `contents: write` token leaked via log injection | mitigate | Permissions block declared at workflow level (`permissions:` block — workflow-scoped, not repo-default). `contents: write` is required for PR branch creation; no step echoes `GITHUB_TOKEN` or secrets; `uv sync --frozen` + `uv run --frozen` prevent dependency-resolution-time package execution. |
| T-04-05-02 | Tampering | Action hijacked via upstream `@main` reference | mitigate | Every `uses:` pinned to a major version tag (v5/v8/v8.1.0/v2/v6). `! grep -E 'uses:.*@(main|master)' .github/workflows/*.yml` — acceptance criteria enforce this. Phase 4 discretion: not pinning to full SHA (maintenance burden > supply-chain delta for this public open-data project; reconsider when repo moves to paid Enterprise). |
| T-04-05-03 | Tampering | Upstream LCCC response contains markdown / HTML that breaks the PR body or Issue template | mitigate | PR body is a static template in the YAML — no `${{ steps.*.outputs.* }}` inlined from scraper output. Issue template is a committed markdown file. Only `github.run_id`, `github.event.schedule`, `github.repository`, `github.ref_name` are templated — all are controlled by the GitHub Actions runtime, not by scraper content. |
| T-04-05-04 | Tampering | `refresh.yml` permissions over-grant (e.g. `contents: write` on a read-only workflow) | mitigate | Minimal permissions per workflow: refresh.yml (contents:write + pull-requests:write + issues:write); deploy.yml (contents:write only); ci.yml unchanged (default read-only). Acceptance criteria: `grep -c "pull-requests\|issues" .github/workflows/deploy.yml` returns 0. |
| T-04-05-05 (T-04-R) | Tampering | Release asset upload includes wrong file or overwrites prior release | mitigate | `softprops/action-gh-release@v2` uploads from `snapshot-out/` (not repo root) with an explicit allowlist of globs (`snapshot-out/**/*.parquet`, etc.). snapshot.py writes to a fresh tempdir per invocation (Task 3 of Plan 04 — `--output` must be empty or `--dry-run` used). `github.ref_name` is the tag name — GitHub Releases create a new release per tag; re-uploading the same tag requires manual intervention. |
| T-04-05-06 | Denial of Service | Cron runs forever on a scraper hang | mitigate | `timeout-minutes: 30` on refresh.yml (research budget <5 min typical per ARCH §7.3); 20 min on deploy.yml. |
| T-04-05-07 | Denial of Service | CI-cascade loop: refresh PR triggers ci.yml triggers refresh.yml | mitigate | BY DESIGN: default `GITHUB_TOKEN` does NOT trigger downstream workflows on PR creation (documented Pitfall 2). A future PAT-based approach would need `refresh.yml` to filter `github.event_name != 'pull_request'` — noted in CHANGES.md for Phase 4.1 follow-up. |
| T-04-05-08 | Information Disclosure | A future secret (e.g. `REFRESH_PAT`) leaked via action logging | accept | No secrets today; `REFRESH_PAT` is explicitly out of scope. If added later: pin `environment: production` + require reviewer approval + log-redaction-safe usage pattern. |
| T-04-05-09 | Repudiation | A refresh PR merged, but its provenance (who, when, for which upstream SHA) unclear | mitigate | PR title includes `${{ github.run_id }}`; PR body links to the run; `refresh_all.py` logs the SHA comparison per scheme; manifest.json embeds `pipeline_git_sha` (set by Plan 04 manifest.py). Full lineage: commit SHA → manifest SHA → PR → run → raw file SHA. |
</threat_model>

<verification>
Phase-4 Plan 05 verifications:

1. YAML validity: `uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh.yml')); yaml.safe_load(open('.github/workflows/deploy.yml'))"` → exits 0.
2. No `@main`/`@master` pins: `! grep -rE 'uses:.*@(main|master)' .github/workflows/`.
3. Refresh template present: `test -f .github/refresh-failure-template.md`.
4. `uv run pytest tests/` still green (workflows do not affect tests).
5. Manual (requires GitHub dashboard access):
   - user_setup item: "Allow GitHub Actions to create and approve pull requests" enabled.
   - Labels `daily-refresh` + `refresh-failure` exist.
6. Smoke test (post-merge): run `gh workflow run refresh.yml` from a feature branch via manual dispatch — observe PR opens with expected label + body.
7. Snapshot dry-run (pre-Phase-5 exit checkpoint): `git tag v2026.04-rc1 && git push --tags` OR manual dispatch of deploy.yml → release assets upload cleanly.
</verification>

<success_criteria>
- `.github/workflows/refresh.yml` exists and parses as valid YAML
- `.github/workflows/deploy.yml` exists and parses as valid YAML
- `.github/refresh-failure-template.md` exists
- All third-party actions pinned to explicit major versions; no `@main` or `@master`
- Permissions blocks are least-privilege (ci.yml unchanged read-only; refresh.yml write on contents+pr+issues; deploy.yml write on contents only)
- refresh.yml fires on cron + workflow_dispatch
- deploy.yml fires on tag push matching `v*`
- refresh.yml invokes `refresh_all.py` + test gates + mkdocs strict + create-PR + create-issue-on-failure
- deploy.yml invokes `snapshot.py` + softprops release upload
- `uv run pytest tests/` still green after YAML adds
- `CHANGES.md` records both workflows + template
- user_setup documents the two dashboard-only steps (repo setting toggle + label creation)
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-05-SUMMARY.md`. Must include:
- Confirmation that both YAML files parse via `yaml.safe_load`
- Full list of action pins with their major versions
- Whether the user completed the two user_setup dashboard steps (label creation + repo toggle)
- Smoke result if the user ran `gh workflow run refresh.yml` manually (expected: refresh finds no upstream changes since raw sidecar shas match)
- Open follow-up: PAT-based ci.yml cascade for refresh PR (deferred to Phase 4.1 per D-16)
</output>
