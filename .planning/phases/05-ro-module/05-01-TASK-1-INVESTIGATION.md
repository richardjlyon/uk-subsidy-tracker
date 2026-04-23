# Plan 05-01 Task 1 — Programmatic-RER Access Investigation

**Investigated:** 2026-04-23
**Investigator:** GSD executor agent (auto-mode, sequential)
**Outcome:** Option D (deterministic fallback) adopted; real-credentials path deferred to Plan 05-13 post-execution review.

---

## Probe Results (2026-04-23 04:36 UTC)

All probes used `curl -sI --max-time 10` (HEAD, 10-second timeout) so the
investigation never stalls.

| URL | HTTP Status | Content-Type | Notes |
|-----|-------------|--------------|-------|
| `https://rer.ofgem.gov.uk/` | **403** | `text/html` (Azure-fronted) | Auth-walled SharePoint. `x-azure-ref` header confirms Microsoft 365 / Entra ID OIDC backing. Public access blocked. |
| `https://renewablesandchp.ofgem.gov.uk/` | (no response) | — | Legacy register decommissioned 2025-05-14 per RESEARCH §2; confirms RESEARCH's TLS-cert-error finding. |
| `https://www.ofgem.gov.uk/` | 200 | `text/html` | Top-level site reachable. |
| `https://www.ofgem.gov.uk/transparency-document/renewables-obligation-ro-buy-out-price-mutualisation-threshold-and-mutualisation-ceilings-2024-25` | **404** | `text/html` | RESEARCH-suggested transparency-document URL pattern is stale. |
| `https://www.ofgem.gov.uk/sites/default/files/2024-12/Renewables-Obligation-Annual-Report-2023-24.pdf` | **404** | `text/html` | RESEARCH-suggested annual-report PDF path does not resolve. |
| `https://www.ofgem.gov.uk/publications/renewables-obligation-buy-out-price-and-mutualisation-ceilings` | **404** | `text/html` | Stable-URL publications listing not at this path. |

**Conclusion:** No stable, public, programmatic HTTPS endpoint for any of the
three datasets is reachable from outside Ofgem's auth wall as of
2026-04-23. The RER (`rer.ofgem.gov.uk`) requires SharePoint-OIDC
authentication; the legacy register is decommissioned; the public
transparency-document and PDF-publication URL patterns surfaced by
RESEARCH §2 are stale (404).

---

## Option Assessment

### Option A — Playwright + RER SharePoint-OIDC (BLOCKED)

- **Feasibility:** Blocked without user action.
- **Cost:**
  - **Dependency:** Playwright not in `pyproject.toml` (verified via
    `grep -i playwright pyproject.toml`). Adding it would land
    `playwright>=1.4.0` + `pytest-playwright` + the Chromium binary
    (`npx playwright install chromium`, ~80 MB extra wheels +
    ~150 MB Chromium runtime).
  - **Secrets:** Two GitHub Secrets required — `OFGEM_RER_EMAIL`
    (registered with `renewable.enquiry@ofgem.gov.uk`) and
    `OFGEM_RER_SESSION_COOKIE` (re-issued every ~30 days; user must
    refresh manually).
  - **LOC:** ~200 lines of Playwright wrangling for the SharePoint-OIDC
    flow (login, MFA prompt handling, file-tree navigation, download).
  - **Brittleness:** SharePoint UI changes break the scraper silently;
    every UI revision requires re-recording the click path.
- **NOT EXECUTED** in this task — the plan explicitly forbids attempting
  Playwright without prior user approval (no Chromium binary; no
  credential plumbing; no shipping a 200-LOC dep on a brittle surface
  during autonomous execution).

### Option B/C — Direct HTTPS on stable Ofgem URLs (BROKEN)

- **Feasibility:** Broken / partial.
- **Probe outcome:** Six URLs probed; all but the Ofgem homepage return
  403/404/timeout. RESEARCH §2's URL templates do not resolve in 2026-04.
- **Conclusion:** No live stable-URL programmatic path exists for any of
  the three datasets without paging through dynamic Ofgem-website navigation
  + parsing HTML for the current month's PDF link. Even then, the result
  would be aggregate-only (Option C — PDF extraction), not station-level
  XLSX or monthly-issuance CSV.

### Option C alternative — PDF transcription for `roc-prices.csv` (PARTIAL VIABILITY)

- **Feasibility:** Potentially viable for the buyout + recycle + e-ROC +
  mutualisation prices CSV (single-row-per-year time series; small surface).
- **Practical blocker today:** The transparency-document URL pattern
  surfaced by RESEARCH does not resolve (404). To find a stable PDF URL,
  the executor would need to fetch the Ofgem website's publications search
  page, parse HTML for the current month's PDF link, then download — a
  fragile multi-step path that this autonomous task is not equipped to
  execute reliably without escalating to the user. **Deferred to Plan
  05-13 review** alongside the register + generation files.
- **Stub seed strategy:** Ship a header-only stub today (Step 3.iii in
  this plan); transcription happens during Plan 05-13 review when the
  user can confirm the current Ofgem PDF URL + scope (year range, NIRO
  inclusion) interactively.

### Option D — Manual seed + stub scrapers (ADOPTED)

- **Feasibility:** Implemented in this task.
- **Surface:** Three header-only stub raw files committed under
  `data/raw/ofgem/`; three `.meta.json` sidecars (sha256 + upstream_url +
  retrieved_at + http_status + publisher_last_modified). Scraper
  functions raise `RuntimeError("manual refresh — see
  .planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md ...")`
  when invoked, so an accidental cron invocation surfaces the issue
  immediately instead of silently overwriting the seeded file.
- **Refresh-loop interaction:** `schemes/ro/_refresh.py::upstream_changed()`
  (shipped in a later Plan 05-XX) returns False on byte-matching
  sidecars, so the daily cron auto-skips. The stub scrapers are
  **never invoked under normal operation**; they are a fail-loud guard
  against the loop accidentally firing.

---

## Recommendation

**Option D — adopted.**

## Fallback Rationale

Real programmatic access to Ofgem's RO datasets is gated behind
SharePoint-OIDC authentication (RER returns HTTP 403 from
`rer.ofgem.gov.uk` without a session token). The legacy register at
`renewablesandchp.ofgem.gov.uk` is decommissioned (RESEARCH §2 confirmed
TLS error; this investigation confirmed no DNS/TLS response within 10
seconds). Public-facing transparency-document and annual-report PDF
URLs surfaced by RESEARCH §2 return HTTP 404 in 2026-04, so even the
PDF-extraction Option C cannot be implemented without first paging
through the Ofgem website's publications search to locate the current
month's stable PDF — a fragile multi-step path inappropriate for
autonomous execution. Playwright (Option A) requires user-managed
GitHub Secrets (`OFGEM_RER_EMAIL` + `OFGEM_RER_SESSION_COOKIE`) plus a
~200-LOC SharePoint-OIDC click path plus a ~150 MB Chromium runtime —
all of which require explicit user approval (the plan explicitly
forbids attempting Option A without prior approval). Option D is
therefore the only path that lands the autonomous deliverables (raw
files + sidecars + scrapers + tests + investigation report) without
introducing user-action prerequisites, brittle dependencies, or
unauthorised credentials. The Phase-4 D-17 fail-loud discipline is
preserved: stub scrapers raise loudly on invocation so the daily refresh
workflow surfaces the issue if it accidentally fires; under normal
operation `upstream_changed()` returns False and the stubs are never
called. All human-resolvable follow-ups are routed to Plan 05-13 Task 5
post-execution review (see `## Plan 05-13 Follow-Ups` below).

---

## Plan 05-13 Follow-Ups

The following items require human decision and/or action; they are
deferred to Plan 05-13 post-execution review (Task 5) per the autonomous
execution discipline of this plan.

1. **Replace `data/raw/ofgem/ro-register.xlsx` stub with real Ofgem
   station register export.** Stub today is a header-only XLSX
   (~9 columns, 0 data rows). Real export: Ofgem RER station-register
   spreadsheet covering all accredited stations (GB + NI). User options:
   (a) email `renewable.enquiry@ofgem.gov.uk`, request RER access, and
   manually download once into `data/raw/ofgem/ro-register.xlsx`; or
   (b) approve Plan-05-13 follow-on plan to plumb Playwright + GitHub
   Secrets for automated SharePoint-OIDC scraping.

2. **Replace `data/raw/ofgem/ro-generation.csv` stub with real Ofgem
   monthly ROC issuance export.** Same source/auth as register.
   Same options (a)/(b) as above.

3. **Transcribe `data/raw/ofgem/roc-prices.csv` from Ofgem public PDFs.**
   The buyout + recycle + e-ROC + mutualisation tables are public record;
   transcription is a per-year manual data-entry task spanning 22 rows
   (obligation years 2002-03 → 2023-24 per RESEARCH §4). Options:
   (a) user opens the current Ofgem transparency-document PDF and
   transcribes by hand; (b) future plan adds `pdfplumber` dependency and
   automates PDF table extraction; (c) defer until REF Constable 2025
   benchmark anchor lands (which sources the same prices). The committed
   stub file is header-only today; transcription unblocks Plan 05-05
   `cost_model.py` from consuming real prices.

4. **Plumb `OFGEM_RER_EMAIL` + `OFGEM_RER_SESSION_COOKIE` GitHub Secrets**
   IF the user approves the real-scraper path. Setup steps:
   - Register an Ofgem RER account at `rer.ofgem.gov.uk` (1-2 day
     turnaround for email approval).
   - Capture session cookie from authenticated browser session.
   - Add both to https://github.com/richardjlyon/uk-subsidy-tracker/settings/secrets/actions.
   - Add `playwright>=1.4.0` to `pyproject.toml`; run `npx playwright
     install chromium` in `.github/workflows/refresh.yml`.
   - Re-run Plan 05-01 Task 1 to populate `_REGISTER_URL` /
     `_GENERATION_URL` constants in `src/uk_subsidy_tracker/data/ofgem_ro.py`
     with real RER URLs. Stub `RuntimeError` paths fall away once URLs
     are non-empty.

5. **Decide whether to ship Option C (PDF extraction) as an interim
   middle-ground.** If user prefers not to plumb Playwright but does want
   automated annual updates of `roc-prices.csv`, a future plan could add
   `pdfplumber` + a `download_roc_prices_pdf()` function that fetches
   the current Ofgem transparency-document PDF from a planner-located
   stable URL. Aggregate-only (no station-level), but stable for the
   prices CSV.

6. **Re-examine the RESEARCH §2 URL templates.** This investigation
   found three RESEARCH-suggested URLs returning 404; either Ofgem moved
   them or the templates were never validated. Plan 05-13 reviewer should
   re-run `curl -sI` against each and either (a) update RESEARCH or
   (b) close as superseded by Option D.

---

*Investigation report: 2026-04-23. Read by Plan 05-13 Task 5 post-execution reviewer.*
