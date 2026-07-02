# Chester — a skill for AI-assisted legacy modernization

> "If you don't see the use of it, I certainly won't let you clear it away. Go away and think. Then, when you can come back and tell me that you do see the use of it, I may allow you to destroy it." — G.K. Chesterton, *The Thing* (1929)

![G.K. Chesterton](250px-Gilbert_Chesterton.jpg)

An [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) that teaches AI coding tools to investigate before they remove. It applies the principle of Chesterton's Fence to the codebases where the principle is hardest to follow: mature systems where nobody remembers why the fence was built.

## The problem

In legacy systems, the weirdest-looking code is sometimes the most important. The random 17-second timeout, the "redundant" validation, the retry loop with odd backoff values — [these are often scar tissue](https://aicoding.leaflet.pub/3mobohx4fq22x) from production incidents, vendor quirks, and race conditions that the organization has long since forgotten. The people left; the tickets were archived; the Slack threads vanished. The implementation is the only surviving record of decisions made by the team.

AI coding tools can make this dangerous at scale. Asked to "modernize" or "clean up" a codebase, they bring a strong aesthetic bias toward simplification — and weird-but-load-bearing code pattern-matches to "mistake." Cleanliness and correctness are different properties, and a refactor that silently discards a defensive check may reintroduce a bug that someone already paid to fix once.

## What this skill does

When active, the skill directs the AI agent to:

1. **Inventory the fences** — catalog every magic number, defensive check, odd ordering, and inexplicable construct in the target code before changing anything.
2. **Do the archaeology** — recover each fence's purpose from evidence: git history and blame, co-located tests, repository-wide dependency search (Hyrum's Law applies), referenced tickets, and finally humans.
3. **Act by classification** — preserve fences whose purpose is recovered and still valid; remove obsolete ones confidently but in isolated, revertible commits, ideally leaving a tripwire (assertion or alert) where the fence stood; and critically, **default to preservation when the purpose cannot be determined**, pinning the behavior with a characterization test rather than silently dropping it.
4. **Write a fence ledger** — a document recording each fence, the evidence found, and the decision made. Modernization is the last chance to transcribe the implementation's memory back into human-readable form; the ledger and restored "why" comments are that transcription.
5. **Sequence for reversibility** — behavior-preserving refactors and behavior-changing removals in separate commits, tests landing before the refactors they protect.

The skill also includes a calibration section so it can't be weaponized as a blanket defense of cruft: proven-obsolete code should be removed, rigor scales with blast radius, and brand-new code has no fences.

## Installation

Chester's guidance is written as a structured prompt that works with any AI coding agent. Choose the setup that matches your tool:

### Claude

**Claude.ai / Claude Desktop:** upload `chester.skill` in a conversation and click **Save skill**, or add it via Settings → Capabilities.

**Claude Code:** copy the `chester/` directory into your skills folder (e.g. `~/.claude/skills/` for personal use, or `.claude/skills/` in a repository to share it with your team).

### GitHub Copilot

Copy `SKILL.md` into your repository as a Copilot instructions file:

```bash
cp SKILL.md .github/copilot-instructions.md
```

Or, to scope it as a reusable instruction file that you can reference on demand:

```bash
mkdir -p .github/instructions
cp SKILL.md .github/instructions/chester.instructions.md
```

Add the YAML front matter so Copilot knows when to apply it:

```yaml
---
description: 'Chesterton''s Fence discipline for legacy code modernization'
applyTo: '**'
---
```

See [Customizing Copilot with instruction files](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) for details.

### Cursor

Copy `SKILL.md` into your project as a Cursor rules file:

```bash
mkdir -p .cursor/rules
cp SKILL.md .cursor/rules/chester.mdc
```

Cursor will automatically pick up rules from `.cursor/rules/`. See [Cursor Rules](https://docs.cursor.com/context/rules) for more options.

### OpenAI Codex

Copy `SKILL.md` into your repository as the Codex system prompt:

```bash
cp SKILL.md AGENTS.md
```

Codex reads `AGENTS.md` from the repository root automatically. See [Codex documentation](https://openai.com/index/introducing-codex/) for details.

### Other agents

For any agent that supports custom system prompts or instruction files, paste the contents of `SKILL.md` into the appropriate configuration. The skill is plain Markdown with no tool-specific syntax.

### When does it activate?

The skill triggers automatically on tasks involving legacy code, refactoring, migration, modernization, dead-code removal, or inexplicable-looking code — no special invocation needed.

## Repository contents

```
chester/
└── SKILL.md              # the skill itself
chester.skill             # packaged, installable version
```

## Background

Inspired by G.K. Chesterton's fence parable and by the observation that in long-lived systems, institutional knowledge survives only in the implementation — so the code deserves to be treated as an archaeological record, not noise to be tidied away.

## Image attribution

Photograph of G.K. Chesterton by Ernest Herbert Mills, 1909. National Portrait Gallery, London ([NPG x134952](https://www.npg.org.uk/collections/search/portrait/mw196875)). Public domain in the United States. Source: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Gilbert_Chesterton.jpg).