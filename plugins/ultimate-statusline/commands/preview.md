---
description: Preview the statusline output with sample data
arguments:
  - name: theme
    description: Theme to preview (default, gruvbox, nord, tokyo-night, rose-pine, powerline)
    required: false
  - name: layout
    description: Custom layout to preview (JSON array)
    required: false
  - name: context
    description: Simulated context usage percentage (0-100) for testing thresholds
    required: false
---

# Ultimate Statusline Preview

Preview how your statusline will look with sample data, without modifying settings.

## Usage

### Preview Current Configuration

```bash
/ultimate-statusline:preview
```

### Preview with Different Theme

```bash
/ultimate-statusline:preview --theme gruvbox
/ultimate-statusline:preview --theme tokyo-night
```

### Preview Custom Layout

```bash
/ultimate-statusline:preview --layout '[["model_emoji", "model_name", "separator", "session_cost"]]'
```

## Execution

1. Load current configuration (or use provided theme/layout)
2. Generate sample JSON input data simulating a Claude Code session:
   ```json
   {
     "model": {"id": "claude-opus-4-7", "display_name": "Opus 4.7"},
     "context_window": {
       "total_input_tokens": 45000,
       "total_output_tokens": 8000,
       "context_window_size": 200000
     },
     "cost": {"total_cost_usd": 2.34, "total_duration_ms": 3600000},
     "workspace": {"current_dir": "/Users/you/project"}
   }
   ```
3. Run the statusline script with the sample data
4. Display the rendered output

## Sample Output Examples

**Default Theme** (cyan/magenta accents):

```text
🧠 Opus │  main +2 │ 27% ██░░░░░░░░ │ $2.34 │ 🔥 $2.34/hr │ ⏱ 1h 0m │ 🟢 MCP
```

**Gruvbox Theme** (warm orange/yellow accents):

```text
🧠 Opus │  main +2 │ 27% ██░░░░░░░░ │ $2.34 │ 🔥 $2.34/hr │ ⏱ 1h 0m │ 🟢 MCP
```

**Powerline Theme** (background colors with arrow separators):

```text
 🧠 Opus   main   27%   $2.34   ⏱ 1h
```

## Testing Different Scenarios

Preview with different context levels:
- Low usage: `--context 25`
- Medium usage: `--context 60`
- High usage: `--context 95`

This helps visualize threshold-based coloring.
