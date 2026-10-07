---
name: chester
description: "**WORKFLOW SKILL** — Investigate legacy code before removing or simplifying it. USE FOR: refactoring, modernizing, migrating, or cleaning up mature code; deleting dead code or workarounds; code that looks redundant or inexplicable (magic numbers, odd timeouts, duplicate checks, empty catches). DO NOT USE FOR: greenfield code, code written this session, pure formatting."
license: MIT
---

# Chesterton's Fence

Don't remove code you don't understand. Legacy code is often the only record of past incidents; weird code is often scar tissue, not a mistake.

## Workflow

1. **Inventory fences.** Before editing, list everything whose purpose isn't self-evident: magic numbers, defensive checks, odd ordering, nonstandard retries, swallowed exceptions, dead-looking code.
2. **Do the archaeology.** Use `git blame`, `git log -p`, tests, callers, and tickets, then ask the user. Classify each fence as *valid*, *obsolete*, or *unknown*. See [archaeology.md](references/archaeology.md).
3. **Act by classification.** Valid: preserve behavior, pin with a characterization test first. Obsolete: remove in its own commit with evidence and leave a tripwire. Unknown: preserve, test, and flag it.
4. **Write the fence ledger.** One entry per fence; put the *why* in a comment at the site.
5. **Sequence for reversibility.** Tests before refactors; refactors and removals in separate commits.

Details and ledger template: [acting.md](references/acting.md). Avoiding over-caution: [calibration.md](references/calibration.md).

## Examples

- `timeout=17` from a hotfix citing an incident: preserve, name it, move the history into a comment.
- A vendor-bug workaround made dead by a later migration: remove in an isolated commit.
- `MAX_BATCH = 97` with no history: keep verbatim, pin with a test.

Worked example: [example/README.md](example/README.md).

## Troubleshooting

- **No history survives:** default to preservation and record an open question.
- **User insists on removing an unknown fence:** comply, state the risk, and isolate the change.
