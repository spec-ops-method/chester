# Acting, Ledger, and Sequencing (Steps 3–5)

## Step 3: Act according to classification

**Recovered & valid** → Preserve the behavior exactly through the modernization. You may re-express it in modern idiom, but the observable behavior — including timing, ordering, and error handling — must survive. Write a characterization test that pins the behavior *before* you touch it, so the refactor is verifiable.

**Recovered & obsolete** → You may remove it, but: (a) state the evidence of obsolescence in the ledger and the commit message, (b) remove it in its own commit, separate from stylistic refactoring, so it can be reverted surgically, and (c) where feasible, replace the fence with an assertion or alert that fires if the "impossible" condition recurs — a tripwire where the fence stood.

**Purpose unknown** → Default to preservation. Carry the behavior forward verbatim, wrap it in a characterization test, and mark it in the ledger as an open question for the maintainers. If the user explicitly directs removal anyway, comply but say plainly what is being risked: "I could not determine why this exists; removing it may reintroduce whatever failure it was guarding against. I recommend deploying this change in isolation and watching X." Never silently drop an unexplained behavior as a side effect of a broader rewrite.

## Step 4: Write the fence ledger

Modernization is the moment the implementation's memory gets transcribed back into human-readable form — or lost forever. Produce a ledger (markdown file, e.g. `FENCE_LEDGER.md`, or section of the migration doc) with one entry per fence:

```markdown
## Fence: 17-second timeout on gateway client (src/payments/client.py:214)
- **What it does:** Aborts gateway calls after 17s instead of library default 30s.
- **Archaeology:** Added in a3f91c (2019-03-02), msg "fix payment gateway hangs",
  same commit adds test_gateway_slow_response. References INC-4412 (inaccessible).
- **Classification:** Purpose recovered, still valid — gateway v2 docs still list
  20s server-side kill; 17s ensures client fails first and retries cleanly.
- **Action:** Preserved. Value extracted to GATEWAY_TIMEOUT_S with explanatory
  comment. Characterization test kept.
```

The ledger serves three audiences: the reviewer approving your change, the future maintainer who inherits the system, and the future AI agent that will otherwise re-flag the same fence as "cleanup" next year. Where the fence survives in the new code, also leave the explanation **at the site** — a comment stating the why, not the what, with the incident/commit reference. Turn tribal knowledge into written knowledge; that is half the value of the modernization.

## Step 5: Sequence changes for reversibility

Structure the work so that fence-affecting changes are individually revertible:

- Behavior-preserving refactors and behavior-changing removals go in **separate commits/PRs**.
- One fence removal per commit where practical.
- Characterization tests land *before* the refactor that they protect.
- For high-uncertainty removals, prefer a staged retreat: feature-flag the old path, or log-and-continue where the fence used to act, before deleting outright.
