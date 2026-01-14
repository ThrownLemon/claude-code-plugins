# Gemini CLI Agent

Spawn a new Gemini CLI agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | gemini-3-pro-preview | Used when no modifier specified |
| FAST_MODEL | gemini-3-flash-preview | Used when "fast" modifier requested |

## Security Note

The `-y` (yolo) flag bypasses confirmation prompts, allowing autonomous execution. Only use in trusted environments where you understand the risks of unattended AI agent execution.

## Instructions

1. Before executing, run `gemini --help` to understand available options
2. Use `-y` (yolo mode) for autonomous execution
3. Optionally use `-i "<instruction>"` to start with an initial task (omit for plain interactive mode)
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (gemini-3-pro-preview)
   - "fast" requested → FAST_MODEL (gemini-3-flash-preview)
   - "heavy" requested → DEFAULT_MODEL (gemini-3-pro-preview)

## Command Format

```bash
gemini --model <MODEL> -y -i "<instruction>"
```

## Examples

```bash
# Default/Heavy (gemini-3-pro-preview)
gemini --model gemini-3-pro-preview -y

# Fast (gemini-3-flash-preview)
gemini --model gemini-3-flash-preview -y

# With instruction
gemini --model gemini-3-pro-preview -y -i "analyze this codebase"
```
