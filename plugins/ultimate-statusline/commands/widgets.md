---
description: List all available statusline widgets with their descriptions and status
arguments:
  - name: category
    description: Filter by category (model, git, context, tokens, cost, time, system, metrics, custom)
    required: false
---

# Ultimate Statusline Widgets

List all available widgets, their descriptions, and current enabled/disabled status.

## Widget Categories

### Model Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `model_emoji` | Model emoji (🧠 Opus, 🎵 Sonnet, ⚡ Haiku) | enabled |
| `model_name` | Model name (short or full) | enabled |

### Git Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `git_branch` | Current branch name | enabled |
| `git_changes` | Uncommitted changes (+/-) | enabled |
| `git_worktree` | Worktree name | disabled |
| `commits_today` | Today's commit count | disabled |

### Context Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `context_percent` | Context usage % with progress bar | enabled |
| `context_length` | Token count (e.g., 45K/200K) | disabled |
| `context_usable` | Remaining context % | disabled |

### Token Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `tokens_input` | Input tokens consumed | disabled |
| `tokens_output` | Output tokens generated | disabled |
| `tokens_cached` | Cached tokens used | disabled |
| `tokens_total` | Total tokens used | disabled |

### Cost Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `session_cost` | Current session cost | enabled |
| `daily_cost` | Today's total cost (requires ccusage) | disabled |
| `weekly_cost` | This week's cost (requires ccusage) | disabled |
| `monthly_cost` | This month's cost (requires ccusage) | disabled |
| `burn_rate` | Cost per hour | enabled |
| `budget_alert` | Warning when budget threshold exceeded | disabled |

### Time Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `session_clock` | Session elapsed time | enabled |
| `block_timer` | 5-hour block timer | disabled |
| `reset_timer` | Time until rate limit reset | disabled |

### System Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `mcp_status` | MCP server health (🟢/🔴) | enabled |
| `tmux_info` | Tmux session/window info | disabled |
| `directory` | Current directory name | disabled |
| `version` | Claude Code version | disabled |
| `output_style` | Current output style | disabled |

### Metrics Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `response_time` | Response time in ms | disabled |
| `lines_changed` | Lines added/removed in git | disabled |
| `message_count` | Message count in session | disabled |

### Custom Widgets

| Widget | Description | Default |
|--------|-------------|---------|
| `custom_text` | Static custom text | disabled |
| `custom_command` | Output from shell command | disabled |
| `separator` | Visual separator between widgets | - |

## Execution

1. Read the current configuration from `~/.claude/statusline-config.json`
2. For each widget category (or filtered category):
   - List widget name, description, and enabled status
   - Show any custom configuration for enabled widgets
3. Display totals: X enabled, Y disabled

## Enabling/Disabling Widgets

Use the config command to toggle widgets:

```bash
/ultimate-statusline:config set widgets.mcp_status.enabled true
/ultimate-statusline:config set widgets.tokens_total.enabled false
```
