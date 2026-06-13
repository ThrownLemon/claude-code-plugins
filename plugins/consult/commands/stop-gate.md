---
description: Run a one-shot stop-gate review (z.ai or Gemini) on the current state. Used both manually and as the optional Stop hook.
arguments:
  - name: provider
    description: "Provider: zai or gemini (default: zai)"
    required: false
---

# Consult — Stop Gate

Run a stop-gate-style review. The reviewer is asked: "is this turn done correctly, or are there issues remaining?" and produces `VERDICT: PASS | NEEDS FIXES`.

This command runs the same logic the optional Stop hook uses, so you can preview behavior before enabling the hook.

## Behavior

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs stop \
  --provider ${ARGUMENTS.provider:-zai}
```

Surface the verdict and any listed issues. If `NEEDS FIXES`, the underlying script also exits non-zero — but in manual invocation just show the result; don't treat it as a script failure.

## Enabling the Stop hook

The Stop hook is **opt-in**. To enable it, add this to your project's `.claude/settings.json` (or use the global `~/.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs stop --provider zai"
      }]
    }]
  }
}
```

When `VERDICT: NEEDS FIXES` is returned, the script exits 2 and Claude Code surfaces the reviewer's notes back to the model, prompting another turn.

> **`${CLAUDE_PLUGIN_ROOT}` caveat:** that variable is expanded for hooks defined in a plugin's own `hooks/hooks.json`, but it may **not** be substituted inside a user-authored `.claude/settings.json`. If the hook fails to find the script, replace `${CLAUDE_PLUGIN_ROOT}` with the absolute path to the plugin's `scripts/consult.mjs`.

> **Privacy / consent:** the stop gate sends the **tail of your transcript and the current git diff** to a third-party API (z.ai or Google). Only enable it on work you're comfortable sharing with that provider, and avoid it in repos containing secrets or regulated data. Redact sensitive content before enabling, or point `--provider` at a provider whose data policy you accept.
