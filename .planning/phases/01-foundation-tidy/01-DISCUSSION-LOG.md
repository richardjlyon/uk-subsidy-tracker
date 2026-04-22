# Phase 1: Foundation Tidy - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-21
**Phase:** 01-foundation-tidy
**Areas discussed:** Material config depth, Nav shell scope

---

## Gray Areas Offered

| Area | Description | Selected |
|------|-------------|----------|
| Material config depth | Minimal vs opinionated vs full kitchen sink | ✓ |
| Nav shell scope | Theme swap + About vs target-nav stub vs hybrid | ✓ |
| CITATION & CHANGES init | Version number, format, ORCID, seed entries | |
| Corrections flow scope | Page shell vs page + protocol + GH label | |

---

## Material config depth

### How opinionated should the Material config be?

| Option | Description | Selected |
|--------|-------------|----------|
| Opinionated baseline (Recommended) | light+dark toggle, nav.tabs/sections, toc.follow, search.suggest/highlight, content.code.copy | ✓ |
| Minimal swap | Just `theme.name: material` with defaults | |
| Full kitchen sink | All of above + navigation.instant, social cards, glightbox, git-revision-date | |

**User's choice:** Opinionated baseline (Recommended)

### Palette strategy — light, dark, or toggle?

| Option | Description | Selected |
|--------|-------------|----------|
| Light + dark with toggle (Recommended) | `scheme: default` + `scheme: slate`, header toggle | ✓ |
| Dark only | Match existing Plotly dark theme | |
| Light only | Standard docs look | |

**User's choice:** Light + dark with toggle (Recommended)

### Site identity — rename site + URL now?

| Option | Description | Selected |
|--------|-------------|----------|
| Rename all (Recommended) | site_name, site_url, repo_url, copyright, README all to `uk-subsidy-tracker` | ✓ |
| Rename site only, keep URLs | site_name changes but URLs stay on `cfd-payment` until GH rename | |
| Defer until custom domain picked | Keep existing URLs; revisit when domain decided | |

**User's choice:** Rename all (Recommended)

### Logo / favicon / brand assets now?

| Option | Description | Selected |
|--------|-------------|----------|
| Skip — text-only wordmark (Recommended) | No logo/favicon; Material default typography carries it | ✓ |
| Placeholder favicon only | Simple emoji or text-initial favicon | |
| Design logo + favicon now | Flagged as scope creep | |

**User's choice:** Skip — text-only wordmark (Recommended)

---

## Nav shell scope

### How much nav structure should Phase 1 lay down?

| Option | Description | Selected |
|--------|-------------|----------|
| Just theme swap + About section (Recommended) | Keep current Charts nav, add `About → Corrections` | ✓ |
| Stub target top-level sections | Home / Themes / Schemes / Data / About shell with stubs | |
| Hybrid: About + Data stubs only | Add About + Data, leave Themes/Schemes for Phase 3 | |

**User's choice:** Just theme swap + About section (Recommended)

### Where does `gas-counterfactual.md` live after theme swap?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave under technical-details/ (Recommended) | Keep existing path; Phase 3 relocates | |
| Move to docs/methodology/gas-counterfactual.md now | Pre-empt Phase 3 naming; saves one mv later | ✓ |
| Delete and defer to Phase 3 | Clean slate but site loses methodology page in P1–P2 interim | |

**User's choice:** Move to docs/methodology/gas-counterfactual.md now

**Notes:** User overrode the recommended option. Rationale inferred: `docs/technical-details/` is already partially deleted per git status (index.md, methodology.md, data-sources.md all marked D). Pre-empting the rename now finishes the cleanup in Phase 1 and avoids a split commit later.

### About section — what goes in it now beyond corrections?

| Option | Description | Selected |
|--------|-------------|----------|
| Corrections + Citation stub (Recommended) | `about/corrections.md` + `about/citation.md` linking to CITATION.cff | ✓ |
| Corrections only | Just the corrections page; cleaner | |
| Corrections + Citation + Methodology-version | Adds page documenting methodology_version (but mechanism is Phase 2) | |

**User's choice:** Corrections + Citation stub (Recommended)

---

## Claude's Discretion

Areas not discussed; sensible defaults documented in 01-CONTEXT.md under "Claude's Discretion":

- Package rename sweep breadth (imports/pyproject/mkdocs vs. docstrings + README + chart filenames)
- `CITATION.cff` version field (0.1.0 pre-portal, 1.0.0 at portal launch), author + ORCID
- `CHANGES.md` format (Keep-a-Changelog with Methodology-versions hook for GOV-04)
- Corrections page content shape (statement + GitHub Issues route + correction table)
- GitHub `correction` label creation (via `gh label create` if auth available)
- GitHub remote rename coordination (sequence: GH UI rename → push commits with new URLs)
- Commit granularity (atomic per task)

## Deferred Ideas

- Logo + favicon design — later polish phase
- Custom domain (`uk-subsidy-tracker.org`) — revisit after portal launch
- Social-cards plugin, `navigation.instant`, git-revision-date, glightbox — later polish
- Zenodo DOI registration — V2-COMM-01, after Phase 5
- `about/methodology-version.md` — follows GOV-04 mechanism in Phase 2
