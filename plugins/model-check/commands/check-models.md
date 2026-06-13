---
description: Scan this project for AI model ids and check them against each provider's live /models endpoint (z.ai, OpenAI, Google). Flags stale ids and surfaces newer ones.
arguments:
  - name: provider
    description: "Limit to one provider: zai, openai, or gemini (default: all with a key set)"
    required: false
---

# Model Currency Check

Run the bundled checker against the current project and present the report.

## Input safety

`$ARGUMENTS.provider` is untrusted. Before using it, validate it is **exactly** one of `zai`, `openai`, or `gemini`. If it is anything else (empty is fine), ignore it and run without `--provider`. Never pass raw user text into the shell command.

## Behavior

Build the command from this fixed template, substituting only a validated provider value:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/check-models.mjs" [--provider <validated>]
```

- With no/invalid provider arg → run with no `--provider` (checks every provider whose API key is set).
- With a valid provider arg (`zai` | `openai` | `gemini`) → append `--provider <that value>`.

Run it from the project root so it scans the user's repo. Then summarize the output for the user:

- `✓` current · `↻` rolling alias · `↳` shortform — no action.
- `⚠` **not in live /models list** — call these out: the configured id may be removed/renamed, or simply brand-new and not yet listed. Recommend verifying the id still resolves.
- `🆕` live models not used in the repo — mention notable newer ones as upgrade candidates.

## Keys

Only providers with an API key in the environment are checked:
- z.ai: `ZAI_API_KEY` / `ZHIPU_API_KEY` / `GLM_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Google: `GEMINI_API_KEY` / `GOOGLE_API_KEY`

If a provider is skipped for a missing key, note which env var to set.
