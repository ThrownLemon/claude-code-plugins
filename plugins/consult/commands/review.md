---
description: Get a third-opinion code review of the current git diff from z.ai (GLM-4.6) or Gemini. Mirrors the codex plugin's review pattern but uses a different model family.
arguments:
  - name: provider
    description: "Provider: zai or gemini (default: zai)"
    required: false
  - name: base
    description: "Base ref to diff against (default: auto-detect origin/main, origin/master, etc.)"
    required: false
  - name: focus
    description: "Optional reviewer focus (e.g. 'security', 'database migrations', 'auth flow')"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Consult — Review

Ask a different model family for a code review of the current branch. Useful as a third opinion alongside Claude and any other reviewer (codex, coderabbit, etc.).

The script gathers branch, base, status, and diff automatically — no need to paste anything.

## Behavior

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs review \
  --provider ${ARGUMENTS.provider:-zai} \
  ${ARGUMENTS.base:+--base "$ARGUMENTS.base"} \
  ${ARGUMENTS.focus:+--focus "$ARGUMENTS.focus"}
```

Surface the response in full. The reviewer is instructed to end with a one-line verdict — SHIP IT, NEEDS WORK, or BLOCKER — relay that verdict at the top of your reply.

## When this is most useful

- Right before opening a PR, as a sanity check
- After a large refactor, to catch regressions Claude may have missed
- Stacked with `/codex:rescue` and `/coderabbit:local` for a 3-way independent review

Run `/consult:config` if you get a "missing key" error.
