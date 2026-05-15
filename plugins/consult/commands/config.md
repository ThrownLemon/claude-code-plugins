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

If a provider is missing a key, surface the env var name and the docs URL. **Do not suggest adding the export to `.bashrc`/`.zshrc`** — shell profiles get backed up to git/cloud via dotfile managers, are readable by any process in the user's session, and are easy to forget about. Recommend in this order:

1. **direnv with a project-local `.env` file** (`chmod 600`) — auto-loads when entering the directory, only exists in shells the user spawns there:
   ```bash
   # .env (chmod 600)
   ZAI_API_KEY=<your-key>
   GEMINI_API_KEY=<your-key>
   ```
2. **macOS Keychain / OS secrets manager** with a tiny wrapper:
   ```bash
   export ZAI_API_KEY="$(security find-generic-password -s zai-api-key -w)"
   ```
3. **Temporary session export only** (for one-off testing):
   ```bash
   export ZAI_API_KEY="<your-key>"   # current shell only — exit to revoke
   ```

Whichever method, the variable must be present in the process Claude Code itself runs in.
