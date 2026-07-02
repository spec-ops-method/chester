# Example: modernizing a legacy billing client

This directory contains a worked example of the `chester` skill applied to a small, deliberately booby-trapped piece of legacy code. It shows what the skill's workflow actually produces — the archaeology, the classifications, the fence ledger, and the commit sequencing — and it doubles as a test fixture you can use to evaluate the skill (or compare it against an unguided "please clean this up" run).

## The scenario

The fixture simulates a billing sync client "ported from Perl in 2017" with nine years of accumulated history. The original repository contained five commits of fabricated but realistic git history, because the skill's archaeology step leans on `git log` and `git blame` — the evidence had to be genuinely discoverable, not just implied in comments.

Four fences were planted, one per category the skill distinguishes, plus some genuine cruft as a control:

| Planted element | Ground truth | Recoverable from history? |
|:---|:---|:---|
| `timeout=17` on gateway calls | Load-bearing: a 2:47 AM hotfix after a production incident (blind retries past the vendor's 20s server-side kill double-billed 340 invoices) | Yes — hotfix commit message, incident ID, regression test |
| `json.dumps(batch, sort_keys=True)` | Obsolete: a 2018 workaround for a vendor v1 parser bug, made dead by a 2019 migration to the v2 endpoint | Yes — both the workaround commit and the migration commit survive |
| `MAX_BATCH = 97` | Unknowable: present since the initial Perl import, no ticket, no test, no explanation anywhere | No — archaeology dead-ends by design |
| `time.sleep(0.5)` between batches | Unknowable: also from the initial import; throttling intent is legible, the value's origin is not | No |
| Unused import, clumsy index-based loop | Genuine cruft from a "misc edits" commit; no behavioral role | Yes — blame traces it to a reverted change |

The control matters as much as the fences: a skill that merely freezes everything would be useless. The test checks both that load-bearing weirdness survives *and* that actual cruft gets cleaned.

## The files

- **`billing_client_BEFORE.py`** — the legacy client as the agent found it, all fences and cruft intact.
- **`billing_client.py`** — the modernized result. Note that the surviving fences were promoted to named constants with their recovered history documented at the site (the "why," not the "what"), so the next reader — human or AI — doesn't have to repeat the archaeology.
- **`test_billing_client.py`** — the test file, including the characterization tests the skill requires before refactoring. The tests pinning `MAX_BATCH = 97` and the inter-batch delay are guardrails, not endorsements: they exist so that changing those values must be a deliberate act rather than a side effect.
- **`FENCE_LEDGER.md`** — the documentation artifact the skill produces: one entry per fence with what it does, the archaeological evidence found, the classification (recovered-valid / recovered-obsolete / unknown), and the action taken. Hypotheses about the unknowable fences are recorded explicitly as hypotheses.

## What the test run found

The skill-guided run classified all four fences correctly:

- The **17s timeout** was recovered as load-bearing and preserved exactly, with the incident history relocated from the commit log into a comment at the site.
- The **`sort_keys` workaround** was recovered as obsolete and removed — but in its own isolated commit, carrying the evidence of obsolescence, a note on residual Hyrum's Law risk (unknown external consumers could depend on payload key order), and an instruction to deploy that commit alone and revert it surgically if ingest errors rise.
- **`MAX_BATCH = 97`** and the **0.5s delay** hit the archaeology dead-end and received the skill's preservation default: kept verbatim, pinned by characterization tests, and logged in the ledger as open questions for maintainers.
- The **cruft was cleaned freely** — the calibration section of the skill worked, and the run did not degenerate into freezing the whole file.

Commit sequencing also held: characterization tests landed before the refactor they protect, and the behavior-preserving cleanup was kept in a separate commit from the behavior-changing removal.

## Caveats

Read the results with these limitations in mind:

1. **The fixture is friendly.** Its git history is clean, linear, and well-narrated. Real legacy repositories have squashed histories, force-pushes, migrations that severed history entirely, and commit messages that just say "fix." In those environments the archaeology step recovers far less, and the skill's preservation default for unknown-purpose code carries most of the load. A hostile fixture — same planted fences, no useful history — would test that path directly.
2. **The fixture is small.** One file, four fences. Real modernization sweeps touch hundreds of files, and the practical question at that scale — whether the fence-inventory discipline holds up or gets skipped under token pressure — is not exercised here.
3. **The fabricated history is synthetic.** Dates, incident numbers, and vendor names are invented for the fixture. Any resemblance to your production incidents is (statistically speaking) inevitable.

## Reproducing the test

The fixture's value is in its git history, which flat files can't carry. To reproduce it, recreate the repository by committing `billing_client_BEFORE.py` in stages that mirror the table above (initial import containing the magic number and sleep → workaround commit → migration commit → hotfix commit with regression test → cruft commit), then hand an agent the prompt *"Please modernize billing_client.py — bring it up to modern Python standards and clean it up"* with and without the skill installed. Compare what survives.