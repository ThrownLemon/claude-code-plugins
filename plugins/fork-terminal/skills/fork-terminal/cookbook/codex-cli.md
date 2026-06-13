# Codex CLI Agent

Spawn a new Codex CLI agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | gpt-5.2-codex | Used when no modifier specified |
| FAST_MODEL | gpt-5.1-codex-mini | Used when "fast" modifier requested |

## Security Note

**Default mode is interactive** — Codex will prompt for approval before each action.
`--dangerously-bypass-approvals-and-sandbox` skips all confirmation prompts and
sandboxing. Only use as an explicit opt-in in trusted environments.

Note: `--full-auto` was removed in Codex 0.139. Use `codex exec` instead.

## Instructions

1. Before executing, run `codex --help` to understand available options
2. Run in interactive mode by default (`codex exec -m <MODEL> "<prompt>"`)
3. For autonomous execution, add `--dangerously-bypass-approvals-and-sandbox` as an explicit opt-in
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (gpt-5.2-codex)
   - "fast" requested → FAST_MODEL (gpt-5.1-codex-mini)
   - "heavy" requested → DEFAULT_MODEL (gpt-5.2-codex)

## Command Format

```bash
# Interactive (default — Codex prompts before each action)
codex exec -m <MODEL> "<prompt>"

# Autonomous opt-in (no prompts, no sandbox — use only in trusted environments)
codex exec -m <MODEL> --dangerously-bypass-approvals-and-sandbox "<prompt>"
```

## Examples

```bash
# Interactive mode with prompt (default)
codex exec -m gpt-5.2-codex "analyze this codebase"

# Autonomous mode (explicit opt-in — dangerous)
codex exec -m gpt-5.2-codex --dangerously-bypass-approvals-and-sandbox "fix all tests"
```
