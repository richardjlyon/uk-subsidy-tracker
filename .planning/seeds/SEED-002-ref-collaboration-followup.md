---
id: SEED-002
status: planted
planted: 2026-04-24
planted_during: "Post-Phase-5.1 RO data strategy exploration (`/gsd-explore`)"
trigger_when: "REF replies to outreach, OR a future RO-related phase begins (e.g., Phase 5.2 RO Data Reconstruction completion or Phase 6 portal launch), OR backlog item 999.x (credentialed RER scraper) is dequeued"
scope: small (re-engagement) → medium (formal collaboration) → large (joint publication)
---

# SEED-002: REF (Renewable Energy Foundation) Collaboration Follow-Up

## Why This Matters

REF (Renewable Energy Foundation, `ref.org.uk`) has been the most consistent independent published analyst of UK renewable subsidy costs for over 15 years. REF Constable 2025 — the project's primary RO benchmark anchor (transcribed verbatim into `tests/fixtures/benchmarks.yaml`) — is one of their published outputs. Their stated mission overlaps almost exactly with this project's core value: independent, methodologically defensible, public-interest scrutiny of UK renewable subsidies.

The user (Richard Lyon, project maintainer) sent an outreach email to REF on 2026-04-24 raising the possibility of collaboration. **No reply received yet.** The project proceeds under the operational assumption that REF data is unavailable, but the possibility of future collaboration changes the data-access calculus enough to be worth keeping in view.

## What Could Unlock

If REF responds positively, three escalating possibilities open:

1. **Data-sharing (small)** — REF holds the underlying station-level data they used to compute their published tables. Sharing that data could unblock the deferred S4 (concentration / Lorenz) and S5 (forward projection) chart slots **without needing the credentialed RER scraper at all** (i.e., obviates backlog item 999.x).

2. **Cross-citation / methodology endorsement (medium)** — REF endorses the project's methodology, this project cites REF reciprocally, and both sites link to each other. Strengthens the project's positioning from "independent reconstruction" to "independently verified by REF".

3. **Co-publication (large)** — Joint publication of cross-scheme analysis. Project becomes a technical platform; REF provides domain credibility and audience reach. Would require its own milestone and probably its own governance structure.

## Re-Engagement Triggers

Surface this seed when any of these happen:

- **REF replies** — handle the response on its own terms; this seed becomes activated
- **Phase 5.2 completes** (RO Data Reconstruction Aggregate-Grain) — second outreach attempt is reasonable; we now have a working RO page they can review
- **Phase 6 starts** (portal launch) — third outreach attempt; portal makes the project visible enough that REF may engage on hearing about it
- **Backlog 999.x is about to be picked up** (credentialed RER scraper) — pause and try REF one more time first; data-sharing could obviate the entire scraper buildout
- **Ofgem announces further data-access changes** — REF will know more than we do about what's actually changing

## What to Send

Initial outreach (2026-04-24) was a feeler. Future re-engagement should include:

- A link to the live published portal (once Phase 6 is up) — concrete evidence the project ships finished work
- The Phase 5.2 methodology page (once written) explicitly citing REF Constable 2025 as the benchmark anchor
- A specific ask: data-sharing for the station register, OR methodology review, OR cross-citation
- Acknowledgement that the project's adversarial-proof posture deliberately mirrors REF's own discipline

## Why This Is Strictly Forward-Looking

The current Phase 5.2 plan deliberately does NOT depend on REF responding. If they never reply, the project still ships a working RO page from publicly-downloadable Ofgem data. REF involvement would be a strict upgrade — never a blocker.

## References

- `.planning/notes/ro-data-strategy-option-a1.md` — primary data strategy decision
- `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` — REF Constable benchmark sentinel
- `tests/fixtures/benchmarks.yaml` — the 22 REF Constable 2025 entries already in use
- `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` — the formal A1↔A2 cross-check
- REF website: `https://ref.org.uk`
