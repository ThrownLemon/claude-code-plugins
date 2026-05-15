---
description: Ask a third-party AI (z.ai/GLM or Gemini) a single question. Useful for second-opinion analysis on tricky decisions.
arguments:
  - name: provider
    description: "Provider: zai or gemini (default: zai)"
    required: false
  - name: prompt
    description: The question or prompt to send
    required: true
---

# Consult — Ask

Send a one-shot prompt to a third-party model and stream the answer back.

Use this when you want a second opinion that is **not** Claude — useful for:
- Sanity-checking a design choice
- Asking a different model family for an alternate approach
- Bounce-off ideas that benefit from another perspective

## Behavior

Run the consult script with the user's prompt:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs ask \
  --provider ${ARGUMENTS.provider:-zai} \
  "${ARGUMENTS.prompt}"
```

Show the model's response verbatim. Do not paraphrase or summarize unless the user asks.

## Provider keys

- `zai` requires `ZAI_API_KEY` (or `ZHIPU_API_KEY` / `GLM_API_KEY`)
- `gemini` requires `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)

Run `/consult:config` to verify keys are configured.
