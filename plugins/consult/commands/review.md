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
