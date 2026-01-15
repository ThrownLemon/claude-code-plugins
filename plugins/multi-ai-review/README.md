# Multi-AI Review Plugin

Run parallel code reviews with multiple AI CLIs (Claude, Gemini, Codex) and get a consensus analysis showing where they agree and disagree.

## Features

- **Visual Tmux Mode**: Watch all 3 CLIs reviewing your code simultaneously in split panes
- **Parallel Execution**: Run all three AI CLIs at the same time
- **Consensus Analysis**: See which findings all AIs agree on (highest confidence)
- **Majority Detection**: Identify issues found by 2+ AIs
- **Unique Insights**: Discover findings only one AI caught
- **Comprehensive Coverage**: Security, quality, architecture, performance, best practices

## Installation

This plugin requires the following CLIs to be installed:

```bash
# Claude Code (already installed if using this plugin)

# Gemini CLI
npm install -g @google/gemini-cli

# Codex CLI
npm install -g @openai/codex
```

## Commands

### `/multi-ai-review:scan`

Run a full project code review:

```bash
# Full review with all CLIs
/multi-ai-review:scan

# Security-focused review
/multi-ai-review:scan --focus security

# Use specific CLIs
/multi-ai-review:scan --clis claude,gemini

# Custom timeout
/multi-ai-review:scan --timeout 15
```

### `/multi-ai-review:status`

Check review progress:

```bash
/multi-ai-review:status
/multi-ai-review:status --review review-1736889600
```

### `/multi-ai-review:report`

View or regenerate a report:

```bash
/multi-ai-review:report
/multi-ai-review:report --section consensus
/multi-ai-review:report --format json
```

### `/multi-ai-review:config`

View configuration and check CLI availability:

```bash
/multi-ai-review:config
```

## Report Format

The report groups findings by agreement level:

### Consensus (All Agree)

Issues all three CLIs identified - **highest confidence**, address these first.

### Majority (2+ Agree)

Issues at least two CLIs found - **likely valid**, worth investigating.

### Unique

Issues only one CLI found - **may need human review** to determine validity.

## Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MULTI_REVIEW_TIMEOUT` | `10` | Minutes per CLI |
| `MULTI_REVIEW_CLIS` | `claude,gemini,codex` | Default CLIs |
| `MULTI_REVIEW_CLAUDE_MODEL` | `opus` | Claude model |
| `MULTI_REVIEW_GEMINI_MODEL` | `gemini-2.5-pro` | Gemini model |
| `MULTI_REVIEW_CODEX_MODEL` | `o3` | Codex model |
| `MULTI_REVIEW_OUTPUT_DIR` | `~/.multi-ai-review` | Results directory |

## Natural Language Triggers

The plugin also responds to natural language:

- "Run a multi-AI review"
- "What do different AIs think about my code?"
- "Get a consensus review"
- "Compare AI opinions on this project"
- "Do a comprehensive code review"

## Tmux Mode (Default)

By default, reviews run in a tmux session with split panes so you can watch all CLIs working simultaneously:

```
┌─────────────────────┬─────────────────────┐
│   🤖 CLAUDE         │   🤖 GEMINI         │
│                     │                     │
│   Reviewing...      │   Reviewing...      │
│                     │                     │
├─────────────────────┴─────────────────────┤
│   🤖 CODEX                                │
│                                           │
│   Reviewing...                            │
│                                           │
└───────────────────────────────────────────┘
```

**Tmux Controls:**

| Keys | Action |
|------|--------|
| `Ctrl+B` then `D` | Detach (reviews continue in background) |
| `Ctrl+B` then `z` | Zoom/unzoom current pane |
| `Ctrl+B` then `o` | Switch between panes |
| `Ctrl+B` then `[` | Scroll mode (q to exit) |

To run in headless mode instead: `/multi-ai-review:scan --mode background`

## How It Works

1. **Tmux Session**: Creates split panes, one per CLI, opens in new terminal tab
2. **Parallel Execution**: Each CLI runs with the same review prompt
3. **Output Collection**: Raw outputs are saved to files
4. **Parsing**: Each CLI's output is normalized to a common finding format
5. **Matching**: Similar findings are matched using file/line proximity and description similarity
6. **Aggregation**: Findings are grouped by how many CLIs agree
7. **Reporting**: A formatted report shows consensus first, then majority, then unique

## Example Output

```markdown
## Summary

| Agreement | Count | Description |
|-----------|-------|-------------|
| Consensus | 8 | All CLIs agree |
| Majority | 22 | 2+ CLIs agree |
| Unique | 17 | Only one found |

## Consensus Findings (All Agree)

### 1. Security Issue
**File**: `src/api/auth.ts:45`
**Severity**: 🔴 Critical
**Agreement**: claude, gemini, codex

**Reviewer Notes**:
- **claude**: SQL injection via unsanitized input
- **gemini**: User input directly concatenated into query
- **codex**: Missing parameterized queries

**Suggested Fix**: Use prepared statements
```

## License

MIT
