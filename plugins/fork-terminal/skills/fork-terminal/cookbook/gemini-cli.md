# Gemini CLI Agent

Spawn a new Gemini CLI agent in a separate terminal window.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| DEFAULT_MODEL | gemini-pro-latest | Used when no modifier specified |
| FAST_MODEL | gemini-flash-latest | Used when "fast" modifier requested |

## Security Note

**Default mode is interactive** — Gemini opens an interactive REPL and will ask for
confirmation.  `-y` (yolo) bypasses confirmation prompts; only add it as an explicit
opt-in in trusted environments.

## Mode Guide

| Flag | Behaviour |
|------|-----------|
| _(none)_ | Interactive REPL — user drives the session |
| `-p "<prompt>"` | Headless single-shot — runs prompt and exits (autonomous opt-in) |
| `-y` | Yolo — bypasses confirmation prompts (combine with `-p` for fully autonomous) |

## Instructions

1. Before executing, run `gemini --help` to understand available options
2. Use interactive mode by default (no `-y`, no `-p`)
3. For an autonomous pane that runs and exits, use `-y -p "<prompt>"` as an explicit opt-in
4. Select model based on user request:
   - No modifier specified → DEFAULT_MODEL (gemini-pro-latest)
   - "fast" requested → FAST_MODEL (gemini-flash-latest)
   - "heavy" requested → DEFAULT_MODEL (gemini-pro-latest)

## Command Format

```bash
# Interactive (default — user drives the session)
gemini --model <MODEL>

# Autonomous opt-in (headless, bypasses prompts — use only in trusted environments)
gemini --model <MODEL> -y -p "<prompt>"
```

## Examples

```bash
# Interactive REPL (default)
gemini --model gemini-pro-latest

# Interactive REPL, fast model
gemini --model gemini-flash-latest

# Autonomous single-shot (explicit opt-in)
gemini --model gemini-pro-latest -y -p "analyze this codebase"
```
