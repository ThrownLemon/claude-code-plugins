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
