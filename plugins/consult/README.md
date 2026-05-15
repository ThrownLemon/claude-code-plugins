# Consult Plugin

Third-opinion AI consultation for Claude Code. Calls **Z.AI (GLM-4.6)** or **Google Gemini** directly via API for second-opinion answers, code reviews, and optional stop-gate review.

Think of it as the codex plugin's `/codex:rescue`, except the rescuer is a different model family — GLM or Gemini — and there is no separate CLI to install. Just one env var per provider.

## Why use it

- Independent perspective from a non-Claude model on hard decisions
- Code review from a different model family as a third reviewer (alongside Claude itself and any `/codex:*` / `/coderabbit:*` you use)
- Optional Stop hook: every time Claude wraps up a turn, GLM or Gemini grades the work and tells Claude to keep going if there are obvious issues remaining

## Install

```bash
/plugin marketplace add ThrownLemon/claude-code-plugins
/plugin install consult@travis-plugins
```

Requires Node 18+ (uses global `fetch`).

## Configure API keys

Set one or both — the commands let you choose `--provider`:

```bash
# Z.AI (GLM coding plan) — https://docs.z.ai
export ZAI_API_KEY="<your-zai-key>"

# Google Gemini — https://ai.google.dev
export GEMINI_API_KEY="<your-gemini-key>"
```

Verify with:

```bash
/consult:config
```

## Commands

### `/consult:ask <provider> "prompt"`

Send a one-shot question to GLM or Gemini. The provider is optional and defaults to `zai`.

```
/consult:ask zai     "Is dropping the unique index on user_emails safe given concurrent writes?"
/consult:ask gemini  "Critique this React hook design: <inline code>"
```

The remote model only sees what you put in the prompt — there is no filesystem access. Inline whatever the model needs.

### `/consult:review [provider] [base] [focus]`

Auto-collect the current git diff and ask the provider for a code review. Gathers branch, base, status, and diff for you.

```
/consult:review                            # zai, auto-detect base
/consult:review gemini                     # gemini reviewer
/consult:review zai origin/main "security" # explicit base + focus
```

The reviewer is asked to finish with `SHIP IT`, `NEEDS WORK`, or `BLOCKER` so the verdict is easy to spot.

### `/consult:stop-gate [provider]`

Same logic as the optional Stop hook, but run manually so you can preview it. The reviewer judges whether the most recent turn is complete or needs another pass and outputs `VERDICT: PASS | NEEDS FIXES`.

### `/consult:config`

Print provider/key status and docs URLs.

## Optional Stop hook

A Stop hook will run the consult reviewer after every Claude turn — useful for autonomous workflows but it consumes API tokens. It's **opt-in**. Add to your project `.claude/settings.json`:

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

When `VERDICT: NEEDS FIXES` is returned, the script exits with code 2 so Claude Code surfaces the reviewer's notes back to the model.

## Architecture

```text
plugins/consult/
├── .claude-plugin/plugin.json
├── commands/
│   ├── ask.md          /consult:ask
│   ├── review.md       /consult:review
│   ├── stop-gate.md    /consult:stop-gate
│   └── config.md       /consult:config
├── skills/
│   └── consult-second-opinion/SKILL.md
├── hooks/hooks.json     (no auto-hooks; opt-in via settings.json)
└── scripts/
    ├── consult.mjs      CLI entry point
    └── lib/
        ├── providers.mjs  provider registry (add new providers here)
        ├── client.mjs     OpenAI-compatible fetch client
        └── context.mjs    git context gatherer
```

Both providers expose an OpenAI-compatible `/chat/completions` endpoint, so a single client handles both. Adding a new provider (Anthropic, OpenAI, Mistral, etc.) is one entry in `providers.mjs`.

## Provider models

| Provider | Default model | Endpoint |
|----------|---------------|----------|
| `zai`    | `glm-4.6`     | `https://api.z.ai/api/coding/paas/v4/chat/completions` |
| `gemini` | `gemini-2.5-pro` | `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` |

Override with `--model` on the CLI or as a third positional arg pattern in scripts.

## License

MIT — see repository root.
