# CodeRabbit Plugin for Claude Code

AI-powered code review integration using the CodeRabbit CLI.

## Installation

1. Add the marketplace:
   ```
   /plugin marketplace add github:ThrownLemon/claude-code-plugins
   ```

2. Install the plugin:
   ```
   /plugin install coderabbit@travis-plugins
   ```

## Prerequisites

Install the CodeRabbit CLI:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

After installation, restart your terminal:
```bash
source ~/.zshrc  # or ~/.bashrc
```

## Commands

| Command | Description |
|---------|-------------|
| `/coderabbit:local` | Review local code changes before creating a PR |
| `/coderabbit:pr` | View and manage all PR review comments |
| `/coderabbit:auth` | Authenticate with CodeRabbit CLI |
| `/coderabbit:config` | Configure plugin preferences |
| `/coderabbit:log` | View review history and statistics |

## Usage

### Review Local Changes

```
/coderabbit:local
```

Review your uncommitted and committed changes using CodeRabbit CLI before pushing.

**Options:**
- `--type uncommitted` - Only review unstaged/staged changes
- `--type committed` - Only review committed changes
- `--type all` - Review both (default)
- `--base <branch>` - Compare against specific base branch

### Manage PR Comments

```
/coderabbit:pr
```

View and address review comments from:
- CodeRabbit (AI review bot)
- Other bots (SonarCloud, Codacy, Snyk, etc.)
- Human reviewers

**Options:**
- `--pr <number>` - Specify PR number
- `--filter <type>` - Filter by reviewer or severity

### Authenticate

```
/coderabbit:auth
```

Set up authentication with CodeRabbit CLI. Guides you through the browser-based login flow.

### Configure

```
/coderabbit:config
```

View and modify plugin settings.

### Review History

```
/coderabbit:log
```

View your review session history.

**Options:**
- `--action show` - Show recent reviews (default)
- `--action stats` - Show review statistics
- `--action clear` - Clear review history
- `--limit <n>` - Number of entries to show

**Example output:**

```
# /coderabbit:log --action show --limit 3
2026-01-13T10:30:00 | dir=/path/to/project | CodeRabbit review completed
2026-01-12T15:45:00 | dir=/path/to/project | CodeRabbit review completed
2026-01-12T09:20:00 | dir=/path/to/other | CodeRabbit review completed

# /coderabbit:log --action stats
Total reviews: 12
This week: 5
Average per day: 1.7

# /coderabbit:log --action clear
Review history cleared.
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CODERABBIT_HINT_FREQUENCY` | Show review hint every N edits (0 to disable) | `5` |
| `CODERABBIT_LOG_FILE` | Custom path for review log | `~/.claude/coderabbit-reviews.log` |

> **Note:** The log directory (`~/.claude/` by default) is created automatically by the plugin if it doesn't exist.

Example:
```bash
# Disable review hints
export CODERABBIT_HINT_FREQUENCY=0

# Show hint after every edit
export CODERABBIT_HINT_FREQUENCY=1
```

## Features

### Review Loop Workflow

The local review runs in an isolated subagent context:

1. Run `coderabbit --prompt-only` to get AI-optimized output
2. Parse and categorize issues by severity
3. Present summary with actionable items
4. On request, apply fixes and re-run review
5. Loop until all issues resolved

Benefits:
- Verbose CLI output stays in subagent context
- Main conversation remains clean
- Can run in background (Ctrl+B)
- Resumable if interrupted

### Multi-Source PR Comments

The PR command aggregates feedback from:
- **CodeRabbit MCP**: AI review comments with fix suggestions
- **GitHub API**: Human reviewer comments and other bot feedback

Comments are categorized by reviewer type and presented with clear attribution.

### Rate Limit Handling

CodeRabbit free tier has usage limits. When rate limited, the plugin will:
- Inform you of the limit
- Suggest alternatives (wait, smaller changeset, manual review)
- Offer to retry when the limit resets

## Subagents

This plugin includes two custom subagents:

| Agent | Purpose |
|-------|---------|
| `cr-reviewer` | Local code review with fix loop |
| `cr-pr-manager` | PR comment management |

## Skills

Model-invoked skills for automatic delegation:

| Skill | Example Triggers |
|-------|------------------|
| `cr-local` | "review my code", "check my changes", "analyze my code", "find bugs", "quality check" |
| `cr-pr` | "pr comments", "review feedback", "fix pr feedback", "show pr reviews" |

Skills are triggered automatically when you use natural language — any of the example triggers above will invoke the corresponding skill without needing a slash command.

## Hooks (Optional)

The plugin includes optional automation hooks:

| Hook | Event | Action |
|------|-------|--------|
| Review hint | After file edits | Occasionally reminds to run `/coderabbit:local` |
| Review log | After review completes | Logs completion to `~/.claude/coderabbit-reviews.log` |

To disable hooks, edit `hooks/hooks.json`.

## Troubleshooting

**CLI not found:**
- Ensure CodeRabbit CLI is installed
- Restart your terminal after installation

**Authentication failed:**
- Run `/coderabbit:auth` to re-authenticate
- Check your CodeRabbit account

**Rate limited:**
- Wait for the limit to reset
- Try reviewing a smaller changeset
- Consider upgrading to paid tier

## License

MIT
