---
description: Show which consult providers (z.ai, Gemini) have API keys configured and how to set them.
---

# Consult — Config

Print provider/key status so the user can confirm setup.

## Behavior

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs config
```

Show the script's output verbatim.

## Setup help

If a provider is missing a key, surface the env var name and the docs URL. Suggest adding the export to the user's shell profile:

```bash
# Z.AI (GLM coding plan)
export ZAI_API_KEY="<your-key>"

# Gemini
export GEMINI_API_KEY="<your-key>"
```

Or per-project via direnv / `.env` files — but warn that the plugin reads from the process environment, so the variable must be present where Claude Code itself runs.
