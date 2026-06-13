---
name: consult-second-opinion
description: Use when the user asks for a "second opinion", "third opinion", "what does GLM/Gemini think", or wants another model to weigh in on code, design, or review. Routes to the consult plugin's CLI which calls z.ai (GLM-5.2) or Gemini directly via API.
triggers:
  - "second opinion"
  - "third opinion"
  - "ask glm"
  - "ask gemini"
  - "ask z.ai"
  - "what does glm think"
  - "what does gemini think"
  - "another model"
  - "consult zai"
  - "consult gemini"
---

# Consult — Second Opinion Skill

This skill activates when the user wants another model family to weigh in. The plugin ships a small CLI (`scripts/consult.mjs`) that hits z.ai's GLM-5.2 or Google Gemini directly. No extra CLI binaries needed — just an API key in env.

## When to use

- "Get a second opinion from GLM on this design"
- "Ask Gemini whether this migration is safe"
- "What would z.ai do here?"
- "Run a third-party review of this PR"

## How to invoke

For free-form questions:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs ask --provider zai "<the question, with all needed context inlined>"
```

For a code review of the current branch (auto-gathers git diff):

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs review --provider zai
node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs review --provider gemini --focus "security"
```

Use `--provider gemini` when the user explicitly asks for Gemini, otherwise default to `zai`.

## Important context guidelines

- The remote model has **no access to the local filesystem**. Inline every piece of relevant code or context into the prompt argument. Don't reference files it can't see.
- Keep prompts focused. Long context dumps are fine when justified, but trim to what's load-bearing.
- For reviews, the script handles diff extraction — don't paste a diff manually.

## Provider keys

Verify with `/consult:config`. If missing, ask the user to set:
- `ZAI_API_KEY` for z.ai (GLM)
- `GEMINI_API_KEY` for Google Gemini

## Output handling

Show the model's response verbatim. Surface its verdict (if any) at the top of your reply so the user sees it without scrolling. If it's a code review and the verdict is BLOCKER or NEEDS WORK, list the cited issues clearly.
