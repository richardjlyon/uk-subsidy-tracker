# Phase 3: Chart Triage Execution — Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Tidy and formally document the CfD chart set. Three concrete deliverables:

1. **Triage cleanup.** Delete `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` and `src/uk_subsidy_tracker/plotting/subsidy/scissors.py` from the working tree (preserved only in git history). These are the CUT/DELETE verdicts from ARCHITECTURE.md §5.2.
2. **Per-chart docs pages for 7 PROMOTE charts.** Write narrative documentation for: `cfd_payments_by_category`, `lorenz`, `subsidy_per_avoided_co2_tonne`, `capture_ratio`, `capacity_factor/seasonal`, `intermittency/generation_heatmap`, `intermittency/rolling_minimum`. Each page follows the standardised template (see D-01).
3. **5-theme navigation structure.** Restructure `docs/` so every PRODUCTION chart is reachable from one of five theme index pages (`cost`, `recipients`, `efficiency`, `cannibalisation`, `reliability`). `mkdocs build --strict` passes with the new tree.

**NOT in scope:**

- Cross-scheme portal top-strip / homepage redesign (ARCHITECTURE §5.6 iamkate pattern) — Phase 6.
- Publishing layer (`manifest.json`, CSV mirror, snapshot) — Phase 4.
- New charts or chart-code changes (`capture_ratio` etc. are EXISTING Python modules that already work; Phase 3 documents them, does not rewrite them).
- Fixing pre-existing Pyright diagnostics in PRODUCTION chart source files (e.g., `capture_ratio.py`, `intermittency/__init__.py`, `load_duration.py`) — tracked separately; unrelated to the triage/docs scope.

</domain>

<decisions>
## Implementation Decisions

### Per-chart page template (D-01)

- **D-01:** Every PRODUCTION chart page follows a standardised 6-section template. This becomes the canonical template that future scheme modules (Phases 5, 7, 8, 9, 10) copy when documenting RO / FiT / SEG / Capacity Market / Constraints charts.

  Canonical section order:

  1. **What the chart shows** — short description of the chart, panels/layout, axes. Embedded image + "view interactively" link (see D-03).
  2. **The argument** — what the chart reveals, phrased adversarially per the project's "survives hostile reading" constraint. This is the rhetorical payload.
  3. **Methodology** — how every number was computed. Link back to `docs/methodology/gas-counterfactual.md` where applicable (D-05). Cite the specific constants used and their `Provenance:` blocks in `src/uk_subsidy_tracker/counterfactual.py` (Tier 1 pattern from today's commit `efdfbbc`). Reference the external regulator sources with URLs.
  4. **Caveats** — limits of the model, known assumptions, scenarios where the chart would mislead.
  5. **Data & code** — GitHub permalinks to the Python source (`src/uk_subsidy_tracker/plotting/<path>/<chart>.py`), raw data files (`data/<file>.csv`), and the test file that validates the underlying data (GOV-01 four-way coverage).
  6. **See also** — cross-links to sibling charts in the same theme + cross-theme pointers where relevant.

  Length target: 100–170 lines (in line with existing `docs/charts/subsidy/cfd-dynamics.md` at 105 lines and `cfd-vs-gas-cost.md` at 169 lines). Do not pad. Do not compress below 100 unless the chart is genuinely simpler than the reference three.

### Theme index page strategy (D-02)

- **D-02:** Each of the 5 theme index pages (`docs/themes/<theme>/index.md`) follows a **hybrid structure**: short adversarial argument + chart gallery in the iamkate-portal aesthetic (ARCHITECTURE §5.6).

  Canonical section order per theme index:

  1. **Theme argument** — 2–3 paragraphs stating the theme's claim directly and adversarially. For Recipients: *"Most of this spending goes to a handful of offshore wind farms and Drax."* For Efficiency: *"Even if you accept the climate premise, this is not a cost-effective way to decarbonise."* These come from ARCHITECTURE §5.1.
  2. **Chart gallery** — 3–5 cards in an iamkate-grid aesthetic. Each card: PNG thumbnail → chart page, one-sentence caption. Flagship chart for the theme first.
  3. **What to look at next** — pointer block to adjacent themes (cross-sell). For Cost → "Then: Where the money goes (Recipients)."
  4. **Methodology link** — single-line pointer: *"How every number on this page was computed → [theme methodology](./methodology.md)"*.

  Reader covers the argument + visual hook in under 60 seconds; hostile reader can dive into any chart for proof.

### Chart rendering on pages (D-03)

- **D-03:** Every chart page embeds the **PNG inline** as the primary visual (fast load, works without JS, indexable, social-card friendly, Twitter-native). Below the PNG, a small link: *"→ Interactive version"* that opens the full Plotly HTML at its existing `docs/charts/html/<name>.html` location in a new tab or modal.
- **D-03a:** Chart HTML stays at `docs/charts/html/` (flat, centralised). Chart PNGs likewise stay at `docs/charts/html/` (the current location). Paths do not change during the theme restructure. This avoids re-running chart generation with path tweaks; only Markdown references change.
- **D-03b:** Chart regeneration pipeline unchanged: `uv run python -m uk_subsidy_tracker.plotting` populates `docs/charts/html/` (still gitignored). `uv run mkdocs build --strict` runs after chart generation. Downstream Phase 4 or Phase 6 may introduce a CI chart-regeneration step.

### Navigation model + old URLs (D-04)

- **D-04:** Nav is reorganised by theme. The existing top-level `Charts` section is **removed entirely**. The three existing CfD chart pages in `docs/charts/subsidy/` are `git mv`'d to their theme homes:

  | Old path | New path |
  |---|---|
  | `docs/charts/subsidy/cfd-dynamics.md` | `docs/themes/cost/cfd-dynamics.md` |
  | `docs/charts/subsidy/cfd-vs-gas-cost.md` | `docs/themes/cost/cfd-vs-gas-cost.md` |
  | `docs/charts/subsidy/remaining-obligations.md` | `docs/themes/cost/remaining-obligations.md` |
  | `docs/charts/index.md` | *(deleted — theme index pages replace it)* |

  New nav top-level (in `mkdocs.yml`):
  ```
  Home: index.md
  Cost: themes/cost/index.md
  Recipients: themes/recipients/index.md
  Efficiency: themes/efficiency/index.md
  Cannibalisation: themes/cannibalisation/index.md
  Reliability: themes/reliability/index.md
  Methodology: methodology/gas-counterfactual.md  (keep existing)
  About: about/...
  ```

  Each theme name appears as a **top-level nav item** (not nested under a "Themes" umbrella) because each theme is a distinct argument deserving top-level visibility.

- **D-04a:** **Old URLs break.** No `mkdocs-redirects` plugin. Justification: the repo published today has ~0 external inbound links (new repo, old repo archived). A clean restructure is cheaper than redirect maintenance. `mkdocs build --strict` validates internal references.

### Methodology organisation (D-05)

- **D-05:** `docs/methodology/gas-counterfactual.md` **stays at its current top-level location** as a shared methodology reference. It is not moved into any theme directory. The Cost theme's `docs/themes/cost/methodology.md` covers cost-specific methodology (aggregation logic, allocation-round handling, £-per-MWh derivation) and **links out** to `../../methodology/gas-counterfactual.md` for counterfactual math. The Efficiency theme methodology similarly links to gas-counterfactual for the £-per-tCO2 avoided arithmetic.

  Rationale: the gas counterfactual affects multiple themes (Cost directly; Efficiency for £/tCO2 avoided). A single source of truth avoids duplication and drift. Reader clicks the shared methodology and sees today's Tier 1 `Provenance:` block discipline applied there.

- **D-05a:** Per-theme `methodology.md` pages cover what's theme-specific only. If a piece of methodology appears in more than one theme, it lives at `docs/methodology/<topic>.md` and every theme links to it. This enforces no-duplication.

### Material theme features (D-06)

- **D-06:** Minimal + performance-focused feature set. Matches the iamkate "fast & quiet" aesthetic.

  Features enabled (`mkdocs.yml → theme.features`):

  - `navigation.tabs` — top-bar theme tabs
  - `navigation.tabs.sticky` — theme bar visible on scroll
  - `navigation.sections` — top-level sections expand in sidebar
  - `navigation.top` — back-to-top button
  - `navigation.instant` — XHR page loads, no full reload
  - `search.suggest`, `search.highlight` — search UX
  - `content.code.copy` — copy buttons on code blocks
  - `content.tooltips` — hover tooltips on abbreviations
  - `toc.integrate` — table of contents in left sidebar

  Palette: dark-mode toggle already configured; preserved.

  Features explicitly NOT enabled: announcement bars, cookie banners, feedback widget (requires external infra), version banner (no versioning scheme until v1.0.0 public release), autogenerated social cards (defer to Phase 6 portal work), `navigation.prune` (not needed at current site size).

### Claude's Discretion

- **GOV-01 test reference per chart.** Each PRODUCTION chart page's "Data & code" section cites the test file(s) that validate the underlying data: default to `tests/test_schemas.py` + `tests/test_aggregates.py` for any chart that reads LCCC data; `tests/test_counterfactual.py` for any chart involving `compute_counterfactual()`; `tests/test_benchmarks.py` for any chart whose aggregate has a benchmark anchor. Claude picks the specific set per chart during planning.
- **Chart-page filename convention.** Follow the existing `kebab-case.md` pattern (e.g. `cfd-payments-by-category.md`, `capacity-factor-seasonal.md`). Applies to all new files. Existing files keep their current slugs after `git mv`.
- **Theme ordering in nav.** Order is Cost → Recipients → Efficiency → Cannibalisation → Reliability (ARCHITECTURE §5.1 ordering A–E). Planner may adjust if reader flow tests suggest otherwise.
- **Per-theme chart classification at index.** DOCUMENTED charts (no dedicated page) are embedded inline in the theme `index.md` with the gallery's smaller cards. PRODUCTION charts get their full page linked from the gallery's flagship cards. Per ARCHITECTURE §5.5 lines 1–9.
- **Chart-gallery visual implementation.** The iamkate-grid aesthetic is the reference. Concrete implementation (CSS grid in a Material theme `attr_list` + `md_in_html` block, or a reusable `theme.card` partial) is a planning-time call.

### Folded Todos

No todos matched Phase 3 (todo-match returned 0).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (researcher, planner, executor) MUST read these before acting.**

### Spec / scope

- `ARCHITECTURE.md` §5.1 — The 5 themes and their arguments. Authoritative for theme names, slugs, and rhetorical framing.
- `ARCHITECTURE.md` §5.2 — Chart triage verdicts (PRODUCTION / PROMOTE / DOCUMENTED / CUT / DELETE). Authoritative for which files to delete and which to write docs for. Note: the spec text says "Post-triage counts: 9 PRODUCTION, 4 DOCUMENTED, 1 CUT, 1 DELETE" but the table sums to 10 PRODUCTION — this is a spec typo; the table is authoritative (3 existing-PRODUCTION + 7 PROMOTE-to-PRODUCTION = 10 total; Phase 3 writes 7 new pages).
- `ARCHITECTURE.md` §5.5 — Theme page structure (`index.md` + `methodology.md` + per-chart.md for PRODUCTION only). Authoritative.
- `ARCHITECTURE.md` §5.6 — Portal top-strip iamkate pattern. Aesthetic reference (used for chart gallery cards); full portal page implementation is Phase 6, NOT Phase 3.
- `.planning/REQUIREMENTS.md` TRIAGE-01..04 + GOV-01 — scope and four-way coverage requirement.

### Template source (structural precedent)

- `docs/charts/subsidy/cfd-dynamics.md` (105 lines) — the canonical 4-panel diagnostic page; template reference for `capacity-factor-seasonal`, `generation-heatmap`, `rolling-minimum`, and other multi-panel PROMOTE charts.
- `docs/charts/subsidy/cfd-vs-gas-cost.md` (169 lines) — the longest existing page; template reference for argument-heavy pages (`lorenz`, `subsidy-per-avoided-co2-tonne`).
- `docs/charts/subsidy/remaining-obligations.md` (114 lines) — includes a "What's not in this chart" section worth generalising.

### Methodology reference

- `docs/methodology/gas-counterfactual.md` — cross-theme methodology reference (just updated today with Tier 1 `Provenance:` discipline; commit `efdfbbc`). Cost + Efficiency theme pages link here.
- `src/uk_subsidy_tracker/counterfactual.py` — every `Provenance:` docstring is a source of truth for the methodology pages. Grep-discoverable via `grep -rn "^Provenance:" src/ tests/`.

### Configuration

- `mkdocs.yml` — current nav + theme config. Phase 3 rewrites the `nav:` block and adds features to `theme.features`.
- `src/uk_subsidy_tracker/plotting/__main__.py` — chart regeneration entry point. Unchanged by Phase 3 (paths don't move).

### Related follow-up

- `.planning/seeds/SEED-001-constant-provenance-tiers-2-3.md` — Tier 2/3 of the provenance discipline lands in Phase 4, not Phase 3. Phase 3 consumes the Tier 1 output (the `Provenance:` blocks).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **`src/uk_subsidy_tracker/plotting/chart_builder.py`** — shared chart construction utility used by all chart modules. Not modified in Phase 3.
- **`src/uk_subsidy_tracker/plotting/colors.py`** — shared colour palette (`TECHNOLOGY_COLORS` etc.). Not modified.
- **`src/uk_subsidy_tracker/plotting/theme.py`** — dark Plotly theme. Not modified.
- **`src/uk_subsidy_tracker/plotting/utils.py`** — `save_chart()` and other utilities. Not modified.
- **All 10 PRODUCTION chart Python modules exist and run today.** Phase 3 writes docs; it does not change the Python source.

### Established patterns

- **Docs-as-audit-trail.** Existing three chart pages demonstrate the adversarial-proofing tone: matter-of-fact description, explicit methodology section, explicit caveats. The 6-section template (D-01) codifies this.
- **Plotly → PNG + HTML dual output.** Every chart module produces both via `save_chart()` helpers. Phase 3 consumes both (D-03).
- **Gitignore pattern.** `docs/charts/html/*.html` and `*.png` are gitignored; regenerated from source via `uv run python -m uk_subsidy_tracker.plotting`. mkdocs build assumes they exist.

### Integration points

- **`mkdocs.yml → nav`** — one of the main files Phase 3 edits.
- **`docs/` directory tree** — restructured by Phase 3 (new `themes/` subtree, old `charts/` subtree removed).
- **`.github/workflows/ci.yml`** — Phase 2's CI. Phase 3 should not need to modify it; `mkdocs build --strict` could be added as a CI step, but that is a Phase 3/4 scope call (ARCHITECTURE suggests Phase 3 for the build gate; Phase 2 explicitly deferred it per CONTEXT-02's "no mkdocs-strict gate in Phase 2").

### Known pre-existing diagnostics (not Phase 3 scope)

- `src/uk_subsidy_tracker/plotting/cannibalisation/capture_ratio.py` line 98 — Pyright `reportIndexIssue`.
- `src/uk_subsidy_tracker/plotting/intermittency/__init__.py` line 58 — Pyright `reportReturnType`.
- `src/uk_subsidy_tracker/plotting/intermittency/load_duration.py` line 76 — Pyright `reportReturnType`.
- Various unused-variable warnings elsewhere.

Per `pyrightconfig.json` only `reportMissingImports` is actively enforced, so these are non-blocking. Phase 3 does NOT fix these — they are tracked separately. Planner should not conflate "chart module has a Pyright diagnostic" with "chart module needs rework in Phase 3."

### Files to delete (not modify) per TRIAGE-01

- `src/uk_subsidy_tracker/plotting/subsidy/scissors.py` — CUT per ARCHITECTURE §5.2. Also carries pre-existing Pyright diagnostics that will vanish with the file. Before deletion, confirm no remaining imports via `grep -rn "from uk_subsidy_tracker.plotting.subsidy.scissors\|import scissors" src/ tests/ docs/`.
- `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` — DELETE per §5.2 (obsolete version superseded by `bang_for_buck.py` which is kept as DOCUMENTED). Same import check applies.

</code_context>

<specifics>
## Specific Ideas

- **iamkate.com/grid aesthetic.** The theme-index chart gallery cards visually follow iamkate's grid pattern — subdued, high-information-density, minimal chrome. Full portal implementation is Phase 6; Phase 3 ships the gallery pattern in theme index pages as the aesthetic rehearsal.
- **Adversarial hostile-reader framing.** Each theme argument is stated as a claim the hostile reader would attack, not defensively. Example: instead of *"CfD electricity cost more than gas would have cost"* say *"The CfD scheme cost £14.9bn more than keeping the gas fleet would have."* This is the tone the existing three chart pages already use.
- **"Six projects = 50%" headline** for the `lorenz` chart on the Recipients theme — per ARCHITECTURE §5.2 triage note. The chart page should lead with this figure.
- **DESNZ-assumption challenge** for `capacity_factor/seasonal` chart on the Reliability theme — per §5.2 triage note. The page argues DESNZ's capacity factor assumptions are optimistic.
- **Drought / "longer than any battery" argument** for `rolling_minimum` chart — per §5.2.

</specifics>

<deferred>
## Deferred Ideas

- **Cross-scheme portal top-strip + scheme-grid tiles.** Full iamkate portal pattern on `docs/index.md` per ARCHITECTURE §5.6. Deferred to **Phase 6: Flagship Cross-Scheme Charts**, when X1/X2/X3 charts exist to populate the strip and scheme grid tiles have content from RO + FiT modules (Phases 5 + 7). Phase 3 uses the iamkate aesthetic only in theme-index chart galleries, not in the homepage.
- **mkdocs-redirects plugin.** Rejected in favour of clean break (D-04a). Revisit only if the new site accumulates external inbound links that need to survive a future restructure.
- **Tier 2/3 constant provenance.** Tracked in `.planning/seeds/SEED-001-constant-provenance-tiers-2-3.md`; lands in Phase 4 publishing layer, not here.
- **Pyright diagnostics in chart modules.** Non-blocking per project `pyrightconfig.json`. Worth a dedicated cleanup later but not Phase 3.
- **mkdocs-strict as a CI gate.** Phase 2 explicitly deferred this. Phase 3 is a natural home (now that the docs tree stabilises). Planner may fold in or leave for Phase 4 depending on scope appetite.
- **Autogenerated social cards per page.** Material theme feature. Useful for Twitter/Substack sharing but requires per-page front-matter. Defer to Phase 6 with the portal work.

### Reviewed Todos (not folded)

None — todo-match returned 0 for Phase 3.

</deferred>

---

*Phase: 03-chart-triage-execution*
*Context gathered: 2026-04-22*
