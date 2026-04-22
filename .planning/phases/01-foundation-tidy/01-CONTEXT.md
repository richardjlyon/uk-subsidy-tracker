# Phase 1: Foundation Tidy - Context

**Gathered:** 2026-04-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the repository correctly named, typed, and documented so every subsequent scheme phase starts from a clean, publishable baseline.

In scope:
- Python package rename: `cfd_payment` → `uk_subsidy_tracker` (hard cut, no alias)
- MkDocs theme swap: `readthedocs` → `material` with opinionated baseline config
- Root docs committed: `ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `CHANGES.md`, `CITATION.cff`
- `docs/about/corrections.md` page wired into site nav (GOV-05)
- `CITATION.cff` populated with author / repo URL / version metadata (GOV-06 doc portion)

Out of scope (belongs to later phases):
- Test scaffolding (Phase 2)
- Chart triage, file deletions, five-theme IA restructure (Phase 3)
- `site/data/manifest.json`, snapshot URLs, CI refresh workflow (Phase 4)
- Scheme modules (Phase 5+)

</domain>

<decisions>
## Implementation Decisions

### Material theme configuration

- **D-01:** Opinionated baseline config — not minimal, not full kitchen sink. Phase 3 inherits this without re-doing mkdocs.yml.
- **D-02:** Features enabled: `navigation.tabs`, `navigation.sections`, `toc.follow`, `search.suggest`, `search.highlight`, `content.code.copy`.
- **D-03:** Palette: light + dark with user toggle. `scheme: default` (light) + `scheme: slate` (dark), toggle in header. Plotly charts already render fine on both.
- **D-04:** No `navigation.instant`, no social-cards plugin, no git-revision-date, no glightbox in Phase 1. Reserved for later polish.

### Site identity

- **D-05:** `site_name: UK Renewable Subsidy Tracker` (replaces "CfD Payment Analysis").
- **D-06:** `site_url` and `repo_url` updated to `uk-subsidy-tracker` paths. Assumes the GitHub repo rename happens in the same session. GitHub auto-redirects from the old URL, but the canonical refs in mkdocs.yml must point to the new name.
- **D-07:** `repo_name: uk-subsidy-tracker`. Copyright line updated. README title updated.
- **D-08:** No logo or favicon in Phase 1 — text-only wordmark. Default Material typography carries the site.

### Navigation structure

- **D-09:** Minimal nav change. Keep existing top-level entries (`Home`, `Charts`, `Gas Counterfactual`) and add one new section: `About → Corrections`, `About → Citation`. Phase 3 owns the full five-theme IA restructure.
- **D-10:** Target nav after Phase 1:
  ```yaml
  nav:
    - Home: index.md
    - Charts:
        - Overview: charts/index.md
        - CfD Dynamics: charts/subsidy/cfd-dynamics.md
        - CfD vs Gas Cost: charts/subsidy/cfd-vs-gas-cost.md
        - Remaining Obligations: charts/subsidy/remaining-obligations.md
    - Gas Counterfactual: methodology/gas-counterfactual.md
    - About:
        - Corrections: about/corrections.md
        - Citation: about/citation.md
  ```
- **D-11:** Move `docs/technical-details/gas-counterfactual.md` → `docs/methodology/gas-counterfactual.md`. Update internal links in `docs/index.md` and any other references. Pre-empts Phase 3's naming convention and removes the `technical-details/` dead directory (already partially deleted per `git status`).
- **D-12:** `about/` section contains two pages: `corrections.md` (GOV-05 mechanism) + `citation.md` (stub linking to `CITATION.cff` and noting that versioned snapshot URLs ship in Phase 4). No methodology-version doc yet — GOV-04 belongs to Phase 2.

### Package rename (locked by prior context, listed for downstream agents)

- **D-13:** Hard cut — no backward-compatibility alias. Source of truth: STATE.md "Package rename is Phase 1 gate; all subsequent code assumes `uk_subsidy_tracker`."
- **D-14:** Use `git mv src/cfd_payment src/uk_subsidy_tracker` to preserve file history.
- **D-15:** All import sites must land in the same phase — the package must import cleanly (`uv run python -c 'import uk_subsidy_tracker'`) at phase exit per ROADMAP success criterion 1.

### Claude's Discretion

- **Package rename sweep breadth** — planner/executor decide scope: imports + `pyproject.toml` + `mkdocs.yml` + `__main__` are mandatory; docstrings, README code blocks, chart output filename prefixes (`subsidy_cfd_dynamics_twitter.png`) are judgment calls based on impact. Default: update everything that reads `cfd_payment` as a module/package name; leave narrative text describing the "CfD" scheme untouched.
- **`CITATION.cff` version field** — default to `version: "0.1.0"` (pre-portal). Bumps to `1.0.0` on first portal launch (ARCHITECTURE.md §12 version policy). Author: `Richard Lyon`, email `richlyon@fastmail.com`. ORCID deferred (user can add if they have one).
- **`CHANGES.md` format** — default Keep-a-Changelog style. Seed with a `0.1.0 — 2026-04-21` entry summarising the rename + theme swap + root-doc commits. Leave a `## Methodology versions` section header as the hook for GOV-04 in Phase 2.
- **`docs/about/corrections.md` content** — default: page shell with (a) statement of commitment, (b) how to file via GitHub Issues with the `correction` label, (c) table template (Date | Chart/Page | Issue | Resolution | Commit SHA). Empty table until first correction lands.
- **GitHub `correction` label creation** — create via `gh label create correction` as part of Phase 1 so the corrections page's "file via Issues" link is actually routable. If `gh` auth is unavailable, note in VERIFICATION.md and leave as a user follow-up.
- **GitHub remote rename coordination** — sequence the rename so the GitHub UI rename happens before we push the Phase 1 commits with new URLs. If the GH rename hasn't happened yet at commit time, keep old URLs in a final commit and do a follow-up URL-update commit after the user confirms rename.
- **Commit granularity** — atomic per task: (a) `git mv` package, (b) update imports + pyproject + mkdocs references, (c) switch theme + palette + nav, (d) add root docs, (e) add corrections page + nav wiring.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative spec
- `ARCHITECTURE.md` §11 P0 — Phase 1 entry/exit criteria verbatim. Exit: "Repo renamed, theme switched, `mkdocs build --strict` passes."
- `ARCHITECTURE.md` §14 — Decision log entry confirming `uk-subsidy-tracker` rename rationale.

### Roadmap + requirements
- `.planning/ROADMAP.md` Phase 1 — Success criteria (5 items) this phase must satisfy.
- `.planning/REQUIREMENTS.md` — FND-01 (repo rename), FND-02 (Material theme), FND-03 (root docs), GOV-05 (corrections page), GOV-06 (CITATION.cff portion — snapshot URLs split to Phase 4 per STATE.md).
- `.planning/PROJECT.md` — Core value, non-goals, constraints, key decisions including the Material-theme and package-rename decisions.
- `.planning/STATE.md` — Brownfield note; confirms "Package rename is Phase 1 gate" is locked.

### Codebase maps
- `.planning/codebase/STRUCTURE.md` — Current directory layout + target post-rename layout (§ "Project Layout Gaps vs Target").
- `.planning/codebase/ARCHITECTURE.md` — Pattern, layers, chart inventory (to be renamed with package, not content changes).

### Files to modify
- `pyproject.toml` — `name`, wheel `packages` path.
- `mkdocs.yml` — theme, palette, features, site_name, site_url, repo_url, repo_name, nav, copyright.
- `src/cfd_payment/` — rename to `src/uk_subsidy_tracker/`; every `from cfd_payment` → `from uk_subsidy_tracker`.
- `docs/index.md` — clone-and-run code block references (`cfd-payment`, `cfd_payment.plotting`), GitHub URLs.
- `docs/technical-details/gas-counterfactual.md` — move to `docs/methodology/gas-counterfactual.md`; update links.
- `README.md` — title, clone URL, any module-path examples.

### Files to create
- `ARCHITECTURE.md` — already present untracked; commit as-is.
- `RO-MODULE-SPEC.md` — already present untracked; commit as-is.
- `CHANGES.md` — new, Keep-a-Changelog format with `0.1.0` seed entry.
- `CITATION.cff` — new, CFF 1.2.0 format.
- `docs/about/corrections.md` — new, GOV-05 mechanism.
- `docs/about/citation.md` — new, stub linking to CITATION.cff.

### External references
- Keep a Changelog v1.1.0: https://keepachangelog.com/en/1.1.0/ (format spec — use plain Markdown, no dependency).
- Citation File Format (CFF) 1.2.0: https://citation-file-format.github.io/ (schema for `CITATION.cff`).
- MkDocs Material features: https://squidfunk.github.io/mkdocs-material/setup/ (reference for the opinionated config list).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Plotly theme (`src/cfd_payment/plotting/theme.py`)** — works on both light and dark Material palettes; no change needed. Palette toggle doesn't require chart regeneration.
- **Pandera schemas (`src/cfd_payment/data/lccc.py`)** — rename-only; schema logic untouched.
- **`pyproject.toml` hatch build config** — already uses `packages = ["src/cfd_payment"]`; one-line update.

### Established Patterns
- **Snake_case package + module naming** (per CLAUDE.md conventions) — `uk_subsidy_tracker` fits the pattern. Directory: `src/uk_subsidy_tracker/`.
- **Absolute imports from package root** (e.g., `from cfd_payment import DATA_DIR`) — mechanical find+replace to `from uk_subsidy_tracker import DATA_DIR` across all call sites.
- **Entry point invocation** `uv run python -m cfd_payment.plotting` — becomes `uv run python -m uk_subsidy_tracker.plotting`. Update README + docs/index.md.

### Integration Points
- **`mkdocs.yml`** — single file carrying theme, nav, identity, repo metadata. All Material config lives here.
- **`docs/charts/html/`** is `.gitignore`d — chart output filenames don't need to be renamed in git history; regenerated on next `python -m uk_subsidy_tracker.plotting`.
- **`docs/technical-details/` directory is partially deleted already** (per `git status`: `D docs/technical-details/data-sources.md`, `D docs/technical-details/index.md`, `D docs/technical-details/methodology.md`). Only `gas-counterfactual.md` remains. Phase 1 finishes the cleanup by moving it to `docs/methodology/`.
- **Untracked files at repo root** that Phase 1 commits: `ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `website-notes.md` (not for commit — personal notes, verify before adding), plus several `docs/charts/subsidy/*.md` that belong to later phases.
- **Currently modified but Phase-3-related** (per `git status`): `docs/charts/index.md`, `docs/charts/subsidy/cfd-vs-gas-cost.md`, `src/cfd_payment/plotting/__main__.py`, `src/cfd_payment/plotting/subsidy/cfd_vs_gas_cost.py`, new `docs/charts/subsidy/cfd-dynamics.md`, `docs/charts/subsidy/remaining-obligations.md`, `src/cfd_payment/plotting/subsidy/cfd_dynamics.py`. **Planner must decide:** include in Phase 1 rename sweep (mechanical rename only) or quarantine to Phase 3. Recommended: include in rename sweep (anything that imports `cfd_payment` must move in one atomic commit), leave chart content changes to Phase 3.

</code_context>

<specifics>
## Specific Ideas

- Text-only wordmark — "Serious site, easy to cite" is the mood; Material's default typography carries this without a logo.
- `docs/methodology/` as the naming convention (chosen over `technical-details/`) — pre-empts Phase 3 and matches the serious/formal tone.
- Keep-a-Changelog with a `## Methodology versions` hook ready for GOV-04 in Phase 2 — `counterfactual.py` will carry a `methodology_version` string that CHANGES.md logs against.

</specifics>

<deferred>
## Deferred Ideas

- **Logo + favicon design** — later polish phase; not tied to a specific phase number.
- **Custom domain (`uk-subsidy-tracker.org` or similar)** — revisit after portal launch (Phase 6); creates URL churn if picked now.
- **Social-cards plugin, `navigation.instant`, git-revision-date, glightbox** — Material features reserved for later polish.
- **Zenodo DOI registration** — deferred per V2-COMM-01 (triggered after Phase 5).
- **`about/methodology-version.md` page** — GOV-04 belongs to Phase 2; page follows its mechanism.

</deferred>

---

*Phase: 01-foundation-tidy*
*Context gathered: 2026-04-21*
