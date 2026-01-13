# Codex CLI Agent

Spawn a new Codex CLI agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | o4-mini | Used when no modifier specified |
| FAST_MODEL | o4-mini | Used when "fast" modifier requested |

## Security Note

The `--full-auto` flag enables low-friction sandboxed automatic execution. For fully autonomous (dangerous) mode, use `--dangerously-bypass-approvals-and-sandbox` which skips all confirmation prompts and sandboxing. Only use in trusted environments.

## Instructions

1. Before executing, run `codex --help` to understand available options
2. Run in interactive mode (default)
3. Use `--full-auto` for sandboxed automatic execution
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (o4-mini)
   - "fast" requested → FAST_MODEL (o4-mini)
   - "heavy" requested → DEFAULT_MODEL (o4-mini)

## Command Format

```bash
codex --model <MODEL> --full-auto "<prompt>"
```

## Examples

```bash
# Interactive mode with prompt
codex "analyze this codebase"

# Full auto mode (sandboxed)
codex --full-auto "refactor the auth module"

# Dangerous mode (no sandbox, no prompts)
codex --dangerously-bypass-approvals-and-sandbox "fix all tests"
```
