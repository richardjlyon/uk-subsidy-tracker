# Phase 1 Verification Notes

## User follow-ups

- [x] Create GitHub `correction` label on the repository
  Created against `richardjlyon/cfd-payment` (the current canonical slug) on
  2026-04-22 via:
  ```
  gh label create correction \
    --description "Correction to a published number, chart, or methodology" \
    --color "0E8A16" \
    --repo richardjlyon/cfd-payment
  ```
  GitHub auto-redirects after the UI rename, so the label travels with the
  repository to its new slug. Verified present via
  `gh label list --repo richardjlyon/cfd-payment | grep '^correction\b'`.

- [ ] **Confirm GitHub UI rename `cfd-payment` → `uk-subsidy-tracker` is
  complete.** As of this plan's execution (2026-04-22), `gh repo view
  richardjlyon/uk-subsidy-tracker` returns GraphQL 404 while
  `gh repo view richardjlyon/cfd-payment` still resolves. The rename has
  not yet been performed in the GitHub UI. Once renamed:

  1. GitHub auto-redirects the old slug, so existing clones, issue URLs,
     and the `correction` label all travel with the repo.
  2. Run `git remote set-url origin https://github.com/richardjlyon/uk-subsidy-tracker.git`
     in local clones to update the remote URL (optional; redirect works
     without it).
  3. Verify with `gh repo view richardjlyon/uk-subsidy-tracker --json name,url`.

  Canonical references in `mkdocs.yml`, `CITATION.cff`, `README.md`, and
  `docs/methodology/gas-counterfactual.md` already assume the new slug —
  they will only resolve correctly after the UI rename lands. (Today they
  get there via redirect.)
