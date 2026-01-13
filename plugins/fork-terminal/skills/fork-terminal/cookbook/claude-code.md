# Claude Code Agent

Spawn a new Claude Code agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | opus | Used when no modifier specified |
| FAST_MODEL | haiku | Used when "fast" modifier requested |

## Security Note

The `--dangerously-skip-permissions` flag bypasses all permission prompts, allowing the agent to read/write files and execute commands without confirmation. Only use in trusted environments where you understand the risks of unattended AI agent execution.

## Instructions

1. Before executing, run `claude --help` to understand available options
2. Run in interactive mode (default, no special flags needed)
3. Use `--dangerously-skip-permissions` for autonomous execution
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (opus)
   - "fast" requested → FAST_MODEL (haiku)
   - "heavy" requested → DEFAULT_MODEL (opus)

## Command Format

```bash
claude --model <MODEL> --dangerously-skip-permissions
```

## Examples

```bash
# Default/Heavy (opus)
claude --model opus --dangerously-skip-permissions

# Fast (haiku)
claude --model haiku --dangerously-skip-permissions
```
