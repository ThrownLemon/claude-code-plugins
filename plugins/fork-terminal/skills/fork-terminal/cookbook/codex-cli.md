# Codex CLI Agent

Spawn a new Codex CLI agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | gpt-5.1-codex-max | Used when no modifier specified |
| FAST_MODEL | gpt-5.1-codex-mini | Used when "fast" modifier requested |

## Security Note

The `--dangerously-bypass-approvals-and-sandbox` flag bypasses all approval prompts and sandboxing, allowing the agent to read/write files and execute commands without confirmation. Only use in trusted environments where you understand the risks of unattended AI agent execution.

## Instructions

1. Before executing, run `codex --help` to understand available options
2. Run in interactive mode (default, no special flags needed)
3. Use `--dangerously-bypass-approvals-and-sandbox` for autonomous execution
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (gpt-5.1-codex-max)
   - "fast" requested → FAST_MODEL (gpt-5.1-codex-mini)
   - "heavy" requested → DEFAULT_MODEL (gpt-5.1-codex-max)

## Command Format

```bash
codex --model <MODEL> --dangerously-bypass-approvals-and-sandbox
```

## Examples

```bash
# Default/Heavy (codex-max)
codex --model gpt-5.1-codex-max --dangerously-bypass-approvals-and-sandbox

# Fast (codex-mini)
codex --model gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox
```
