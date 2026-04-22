# Phase 3: Chart Triage Execution — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md` — this log preserves the alternatives considered
> and the user's reasoning path through them.

**Date:** 2026-04-22
**Phase:** 03-chart-triage-execution
**Areas discussed:** Per-chart page template, Theme index page strategy, Chart rendering on docs pages, Navigation model + old URLs, Methodology organisation, Material theme features

---

## Gray-area selection

User chose to discuss all four initially-offered gray areas (multiSelect).

| Area offered | Selected |
|---|---|
| Per-chart page template | ✓ |
| Theme index page strategy | ✓ |
| Chart rendering on docs pages | ✓ |
| Navigation model + old URLs | ✓ |

## Per-chart page template

| Option | Description | Selected |
|--------|-------------|----------|
| Standardized 6-section template | Canonical template — What shows / Argument / Methodology / Caveats / Data & code / See also. All 7 new pages match; template becomes the pattern for all future scheme modules. | ✓ |
| Flexible template with mandatory sections | Require Methodology + Caveats + Data&code; other sections vary. | |
| Lighter scannable template | Short pages (40–60 lines); methodology pages carry the adversarial weight. | |
| Fuller adversarial template | ~200+ lines; explicit "What a hostile reader would say" + rebuttal + benchmark per chart. | |

**User's choice:** Standardized 6-section template.
**Notes:** Chosen option matches the existing three chart pages' implicit structure and gives all future scheme modules (Phases 5, 7, 8, 9, 10) a predictable template to copy.

---

## Theme index page strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid: short argument + chart gallery | 2–3 paragraph argument + iamkate-aesthetic gallery of 3–5 flagship charts + adjacent-theme pointers. | ✓ |
| Long-form argument essay | 500–1200 word essay per theme, embedding flagship charts at relevant paragraphs. | |
| Curated index / hub | One-sentence claim + table of chart links + methodology link. Minimal prose. | |
| Per-theme bespoke | Each theme gets its own format; no uniform template. | |

**User's choice:** Hybrid: short argument + chart gallery.
**Notes:** Matches the iamkate.com/grid aesthetic referenced in ARCHITECTURE.md §5.6; reader gets both argument and visual hook in under 60 seconds.

---

## Chart rendering on docs pages

| Option | Description | Selected |
|--------|-------------|----------|
| PNG inline + "view interactively" link | Main embed is static PNG; small link opens full Plotly HTML. Balances mobile perf, adversarial inspection, and social sharing. | ✓ |
| Interactive HTML embedded via iframe | Every chart fully interactive inline. Heavy page weight; doesn't index well. | |
| Both inline on every page | PNG + interactive HTML on every page; duplicates content. | |
| PNG only; HTML published but not linked | Just the PNG. Simplest; weakens adversarial inspection. | |

**User's choice:** PNG inline + "view interactively" link.
**Notes:** Chart HTML stays at `docs/charts/html/` (centralised, flat); paths don't change with theme restructure.

---

## Navigation model + old URLs

| Option | Description | Selected |
|--------|-------------|----------|
| Replace 'Charts' section entirely + break old URLs | New nav is 5 themes as top-level items. `git mv` existing chart pages into `docs/themes/cost/`. Old URLs break (no external users yet). | ✓ |
| Replace + preserve old URLs via mkdocs-redirects | Same as above but add mkdocs-redirects plugin for 3 permanent redirects. | |
| Themes under a parent 'Themes' umbrella in nav | Nav has single Themes entry expanding to 5. Less top-bar space; extra click. | |
| Keep 'Charts' as legacy aggregate alongside themes | Two parallel information architectures. | |

**User's choice:** Replace 'Charts' section entirely + break old URLs.
**Notes:** New repo (`uk-subsidy-tracker`) shipped today with ~0 inbound external links — clean break is cheaper than redirect maintenance.

---

## Methodology organisation (follow-up area)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep gas-counterfactual.md top-level + cost/methodology.md links to it | Shared cross-theme methodology at `docs/methodology/`; per-theme pages cover theme-specific math only. | ✓ |
| Move into docs/themes/cost/ as the canonical location | Relocate gas-counterfactual.md under Cost theme. | |
| Merge into a central docs/methodology/ hub | Add docs/methodology/index.md as a hub peer to themes. | |

**User's choice:** Keep gas-counterfactual.md top-level + cost/methodology.md links to it.
**Notes:** Gas counterfactual affects Cost + Efficiency themes; single source of truth avoids drift. Reflects the reality that methodology is cross-cutting across themes.

---

## Second-pass: anything else before context?

User selected two items (mixed signal — interpreted as "discuss Material features, then ready for context"):

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | 5 decisions enough; remaining small calls can be Claude's Discretion. | ✓ |
| GOV-01 test reference | Which specific test each chart cites. | |
| Portal top-strip timing | Whether iamkate portal homepage lands now or Phase 6. | |
| Material theme features | Which Material features to enable. | ✓ |

---

## Material theme features

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal + performance-focused | navigation.tabs(+sticky) + sections + top + instant + search.suggest/highlight + content.code.copy + content.tooltips + toc.integrate. Matches iamkate "fast & quiet" aesthetic. | ✓ |
| Maximalist Material | Above + footer, prune, edit/view actions, announce, feedback widget, autogenerated social cards. | |
| Absolute minimum | Search + dark mode only. | |
| I'll decide later | Planner picks during implementation. | |

**User's choice:** Minimal + performance-focused.
**Notes:** Palette (dark-mode toggle) already configured in mkdocs.yml; preserved.

---

## Claude's Discretion (captured in CONTEXT.md)

Items the user did not want to discuss explicitly; Claude picks sensibly during planning:

- GOV-01 test reference per chart — default pattern described in CONTEXT.md D-discretion block.
- Chart-page filename convention — `kebab-case.md` matching existing pattern.
- Theme ordering in nav — A→E order from ARCHITECTURE §5.1.
- Per-theme chart classification at index page (DOCUMENTED embedded, PRODUCTION linked).
- Chart-gallery visual implementation (CSS grid vs Material partial).

## Deferred Ideas (captured in CONTEXT.md)

- Cross-scheme portal top-strip on homepage → Phase 6.
- mkdocs-redirects plugin → not adopted (clean break).
- Tier 2/3 constant provenance → SEED-001, Phase 4.
- Pyright diagnostics cleanup → separate future cleanup pass.
- `mkdocs build --strict` as CI gate → planner may fold in or defer to Phase 4.
- Autogenerated social cards → Phase 6 with portal work.
