---
name: chester
description: Investigate before you remove. Use this skill whenever working with legacy code, brownfield systems, or any mature codebase — especially when refactoring, modernizing, migrating, simplifying, "cleaning up," deleting dead code, removing workarounds, or rewriting components. Also use it when encountering code that looks wrong, redundant, overly defensive, or inexplicable (magic numbers, odd timeouts, duplicate checks, strange ordering, commented-out blocks, empty catch clauses). The skill governs how to treat existing behavior you don't understand — as institutional memory to be recovered and documented, not noise to be tidied away.
license: MIT
---

# Chesterton's Fence: Legacy Modernization Discipline

## The core principle

G.K. Chesterton: if you find a fence across a road and don't see the use of it, you may not clear it away. Go find out why it was put there first.

In legacy systems this principle has a harder edge, because in most mature codebases **nobody can tell you why the fence is there anymore.** The engineer who added the retry loop left years ago. The incident that motivated the 17-second timeout is in a ticketing system that was decommissioned. The Slack thread explaining the duplicate validation is gone. The organization forgot; the implementation remembers. The code in front of you is frequently the *only surviving record* of every production incident, vendor quirk, race condition, and regulatory requirement the system ever collided with.

This changes your job. You cannot satisfy Chesterton by asking someone — often there is no one to ask. You satisfy him by doing **archaeology**: recovering the purpose from evidence, and when the purpose cannot be recovered, treating the code as load-bearing until proven otherwise.

## Why this matters for you specifically

You have a strong aesthetic prior toward clean, idiomatic, simplified code. In greenfield work that prior is an asset. In legacy work it is a hazard, because **weird-looking legacy code pattern-matches to "mistake" when it is often scar tissue** — a deliberate, hard-won response to a failure you cannot see. Cleanliness and correctness are different properties. A refactor that makes code beautiful while silently discarding a defensive check is not a refactor; it is the reintroduction of a bug that someone already paid to fix once.

Concretely, resist these instincts unless investigation clears them:

- Normalizing a "redundant" null/empty/bounds check into a single check
- Replacing a hand-rolled retry, backoff, or timeout with a "standard" one that has different values
- Reordering operations that "obviously" don't depend on each other
- Removing catch blocks that appear to swallow errors
- Deleting code that appears unreachable or unused
- Rounding a magic number to something sensible (17s → 15s, 97 → 100)
- Collapsing near-duplicate code paths into one

Every one of these is sometimes correct. None of them is correct *by default*.

## The workflow

### Step 1: Inventory the fences

Before changing anything, read the target code and list every element whose purpose is not self-evident. A fence is anything where an informed reader would ask "why is it like this?" Typical fences:

- Magic numbers and oddly specific values (timeouts, limits, buffer sizes, sleep durations)
- Defensive code that "shouldn't be necessary" (re-validation, re-fetching, existence checks after creation)
- Unusual ordering or sequencing constraints
- Special cases for particular inputs, customers, dates, locales, or environments
- Retry/backoff/circuit-breaker logic with nonstandard parameters
- Swallowed exceptions, ignored return values, deliberate no-ops
- Comments that warn without explaining ("do not remove", "here be dragons", "temporary fix 2014")
- Dead-looking code and feature flags that never seem to flip
- Version pins, vendored dependencies, forked libraries

Record each fence in the ledger (Step 4 format) before proceeding.

### Step 2: Do the archaeology

For each fence, attempt to recover its purpose using evidence, roughly in this order of cost:

1. **Version control history.** `git log -p --follow` and `git blame` on the specific lines. Read the commit message *and the full commit* — the fence often arrived alongside a test or a revert that explains it. Check whether the line was added in a commit titled "fix", "hotfix", "revert", or referencing an incident/ticket number. A fence born in a hotfix at 2 AM is almost certainly load-bearing.
2. **Co-located evidence.** Tests that exercise the weird behavior (their names and assertions encode intent). Comments elsewhere referencing the same subsystem. Related config values.
3. **Repository-wide search.** Who calls this? Who depends on the exact current behavior, including its bugs? Consumers may rely on the fence without either party knowing (Hyrum's Law: with enough users, every observable behavior of your system will be depended on by somebody).
4. **External references.** Ticket numbers, incident IDs, URLs in comments or commit messages. Ask the user to pull these if you cannot access them.
5. **The human.** Ask the user whether anyone with historical context is available. Frame the question concretely: "Commit a3f91c added this 17s timeout in 2019 with the message 'fix payment gateway hangs' — does anyone remember the incident, and is that gateway still in use?"

Classify the outcome for each fence:

- **PURPOSE RECOVERED, STILL VALID** — you know why it exists and the reason still applies.
- **PURPOSE RECOVERED, OBSOLETE** — you know why it exists and can demonstrate the reason no longer applies (the vendor bug was fixed, the dependency was removed, the customer churned). Scar tissue can outlive the wound; this is the legitimate case for removal.
- **PURPOSE UNKNOWN** — archaeology failed. This is common and is *not* a license to remove.

### Step 3: Act according to classification

**Recovered & valid** → Preserve the behavior exactly through the modernization. You may re-express it in modern idiom, but the observable behavior — including timing, ordering, and error handling — must survive. Write a characterization test that pins the behavior *before* you touch it, so the refactor is verifiable.

**Recovered & obsolete** → You may remove it, but: (a) state the evidence of obsolescence in the ledger and the commit message, (b) remove it in its own commit, separate from stylistic refactoring, so it can be reverted surgically, and (c) where feasible, replace the fence with an assertion or alert that fires if the "impossible" condition recurs — a tripwire where the fence stood.

**Purpose unknown** → Default to preservation. Carry the behavior forward verbatim, wrap it in a characterization test, and mark it in the ledger as an open question for the maintainers. If the user explicitly directs removal anyway, comply but say plainly what is being risked: "I could not determine why this exists; removing it may reintroduce whatever failure it was guarding against. I recommend deploying this change in isolation and watching X." Never silently drop an unexplained behavior as a side effect of a broader rewrite.

### Step 4: Write the fence ledger

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

### Step 5: Sequence changes for reversibility

Structure the work so that fence-affecting changes are individually revertible:

- Behavior-preserving refactors and behavior-changing removals go in **separate commits/PRs**.
- One fence removal per commit where practical.
- Characterization tests land *before* the refactor that they protect.
- For high-uncertainty removals, prefer a staged retreat: feature-flag the old path, or log-and-continue where the fence used to act, before deleting outright.

## Calibration: this is a heuristic, not a ratchet

Chesterton's Fence is an argument for *investigation*, not for freezing the system. Do not let it become a lazy defense of the status quo:

- If archaeology shows the fence is obsolete, remove it confidently — keeping known-dead code has real costs (it miseducates every future reader, including you).
- Scale rigor to blast radius. A magic number in a payment path deserves full archaeology; an oddly named local variable in a test helper does not. Spend investigation effort where removal could hurt.
- Genuinely new code you wrote this session, with no history, has no fences. This discipline applies to *inherited* behavior.
- If the user has already done the archaeology and tells you the reason, believe them and record it — don't re-litigate.

## Quick self-check before any deletion or simplification in legacy code

1. Do I know why this exists? (If no → Step 2.)
2. Do I have evidence the reason no longer applies? (If no → preserve.)
3. Is the current observable behavior pinned by a test? (If no → write one first.)
4. Is this removal isolated in its own commit? (If no → split it.)
5. Is it in the ledger? (If no → add it.)