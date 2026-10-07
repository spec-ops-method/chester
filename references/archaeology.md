# Inventory and Archaeology (Steps 1–2)

## Why this matters for you specifically

You have a strong aesthetic prior toward clean, idiomatic, simplified code. In greenfield work that prior is an asset. In legacy work it is a hazard, because **weird-looking legacy code pattern-matches to "mistake" when it is often scar tissue** — a deliberate, hard-won response to a failure you cannot see. Cleanliness and correctness are different properties. A refactor that makes code beautiful while silently discarding a defensive check is not a refactor; it is the reintroduction of a bug that someone already paid to fix once.

In most mature codebases **nobody can tell you why the fence is there anymore.** The engineer who added the retry loop left years ago. The incident that motivated the 17-second timeout is in a ticketing system that was decommissioned. The organization forgot; the implementation remembers. You cannot satisfy Chesterton by asking someone — you satisfy him by recovering the purpose from evidence, and when the purpose cannot be recovered, treating the code as load-bearing until proven otherwise.

Resist these instincts unless investigation clears them:

- Normalizing a "redundant" null/empty/bounds check into a single check
- Replacing a hand-rolled retry, backoff, or timeout with a "standard" one that has different values
- Reordering operations that "obviously" don't depend on each other
- Removing catch blocks that appear to swallow errors
- Deleting code that appears unreachable or unused
- Rounding a magic number to something sensible (17s → 15s, 97 → 100)
- Collapsing near-duplicate code paths into one

Every one of these is sometimes correct. None of them is correct *by default*.

## Step 1: Inventory the fences

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

Record each fence in the ledger (see [acting.md](acting.md)) before proceeding.

## Step 2: Do the archaeology

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
