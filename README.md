# ThrownLemon's Claude Code Plugin Marketplace

A collection of Claude Code plugins for code quality, productivity, and development tools.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add ThrownLemon/claude-code-plugins
```

Then install individual plugins:

```
/plugin install <plugin-name>@travis-plugins
```

## Available Plugins

| Plugin | Description | Commands |
|--------|-------------|----------|
| [coderabbit](./plugins/coderabbit/) | CodeRabbit integration - local code review and PR comment management | `/coderabbit:local`, `/coderabbit:pr`, `/coderabbit:auth`, `/coderabbit:config` |
| [damage-control](./plugins/damage-control/) | Security protection - blocks dangerous commands and protects sensitive files | (hooks only) |

## Plugin Details

### CodeRabbit

AI-powered code review integration using the CodeRabbit CLI.

**Features:**
- Local code review before creating PRs
- PR comment management (CodeRabbit + other reviewers)
- Automated review → fix → review loops
- Rate limit handling for free tier

**Installation:**
```
/plugin install coderabbit@travis-plugins
```

**Prerequisites:**
- [CodeRabbit CLI](https://docs.coderabbit.ai/cli/overview)

### Damage Control

Defense-in-depth security protection using PreToolUse hooks. Adapted from [disler/claude-code-damage-control](https://github.com/disler/claude-code-damage-control).

**Features:**
- Blocks dangerous bash commands (rm -rf, git push --force, DROP TABLE, etc.)
- Protects sensitive files (.env, ~/.ssh/, credentials, API keys)
- Three protection tiers: zero-access, read-only, no-delete
- Ask patterns for confirmation on risky-but-valid operations
- 100+ dangerous command patterns out of the box

**Installation:**
```
/plugin install damage-control@travis-plugins
```

**Prerequisites:**
- [uv](https://docs.astral.sh/uv/) (Python package runner)

## Adding New Plugins

To add a new plugin to this marketplace:

1. Create a new directory under `plugins/`
2. Add the plugin structure (`.claude-plugin/plugin.json`, commands, agents, etc.)
3. Update `.claude-plugin/marketplace.json` to include the new plugin
4. Commit and push

## License

MIT
