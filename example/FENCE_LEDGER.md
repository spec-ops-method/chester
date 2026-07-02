# Fence Ledger — billing_client.py modernization (2026-07-02)

Archaeological record of every non-obvious behavior encountered during
modernization, per the Chesterton's Fence discipline. One entry per fence.

## Fence 1: 17-second gateway timeout (`GATEWAY_TIMEOUT_S`)
- **What it does:** Aborts ingest calls at 17s instead of the previous 30s.
- **Archaeology:** Added in 1777ac4 (2020-11-03, 02:47 — a production hotfix).
  Commit message documents INC-4412: Acme kills idle connections server-side
  at 20s, returns 502 with no idempotency guarantee; blind retries after the
  server kill double-billed 340 invoices. Regression test added same commit.
- **Classification:** PURPOSE RECOVERED, STILL VALID. We remain on Acme ingest;
  no evidence the 20s server-side kill changed.
- **Action:** Preserved exactly. Extracted to named constant with the incident
  history at the site. Regression test updated to track the constant.

## Fence 2: JSON key sorting in `post_batch` (`sort_keys=True`)
- **What it does:** Alphabetized payload keys before POSTing.
- **Archaeology:** Added in d64dad6 (2018-02-20) solely for the Acme **v1**
  endpoint's XML-bridge parser (vendor case #88301). Commit b67e5c2
  (2019-08-14) migrated us to the v2 native-JSON endpoint; the bridge is no
  longer in our request path. Repo-wide search: no internal consumer of key
  ordering.
- **Classification:** PURPOSE RECOVERED, OBSOLETE. Scar tissue outliving the wound.
- **Action:** Removed in isolated commit 82f6bfa. Residual Hyrum's Law risk
  (unknown *external* consumers of payload ordering) noted in the commit;
  recommend deploying that commit alone and watching ingest error rates.
  Revert 82f6bfa surgically if errors rise.

## Fence 3: `MAX_BATCH = 97`
- **What it does:** Caps invoice batches at 97 items.
- **Archaeology:** Present since the initial 2017 import from the Perl system
  ("behavior kept identical to the Perl version"). No ticket, no test, no
  comment, no other reference in the repository. The Perl source predates this
  repo and is unavailable. **Archaeology failed.**
- **Classification:** PURPOSE UNKNOWN.
- **Action:** Preserved verbatim per the preservation default. Pinned by a new
  characterization test. **Open question for maintainers:** does anyone recall
  a batch limit in the old Perl system or an Acme payload cap? Plausible
  hypotheses (payload size limit, off-by-something from a 100-row DB page)
  are recorded here as hypotheses, not facts.

## Fence 4: 0.5s inter-batch delay (`INTER_BATCH_DELAY_S`)
- **What it does:** Sleeps half a second between batch POSTs.
- **Archaeology:** Also from the 2017 import; no explanation found. Intent
  (throttling) is legible but the value's origin and whether Acme still
  requires it are not.
- **Classification:** PURPOSE UNKNOWN.
- **Action:** Preserved verbatim; pinned by characterization test. Open
  question: check Acme's current rate-limit documentation before removing.

## Non-fences (cleaned freely)
- Unused `os` import and the index-based loop with throwaway names in
  `sync_invoices`: blame traces both to c87661a ("logging hook (reverted),
  misc edits") — cosmetic residue of a reverted change, no behavioral role.
  Removed in the behavior-preserving refactor without ceremony.
