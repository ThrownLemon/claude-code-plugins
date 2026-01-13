# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Claude Code plugin marketplace** - a collection of plugins that extend Claude Code with new commands, agents, skills, and hooks. The marketplace is hosted on GitHub and users install plugins via `/plugin marketplace add github:ThrownLemon/claude-code-plugins`.

## Architecture

### Marketplace Structure

```text
.claude-plugin/marketplace.json    # Marketplace catalog (lists all plugins)
plugins/                           # All plugins live here
  <plugin-name>/                   # Each plugin is a subdirectory
    .claude-plugin/plugin.json     # Plugin manifest
    commands/                      # Slash commands (/plugin:command)
    agents/                        # Subagents (autonomous task handlers)
    skills/                        # Model-invoked behaviors (SKILL.md)
    hooks/                         # Event-triggered automation (hooks.json)
    scripts/                       # Shell scripts for hooks
    .mcp.json                      # MCP server configuration
```

### Plugin Components

- **Commands** (`commands/*.md`): User-invocable via `/pluginname:command`. YAML frontmatter defines arguments.
- **Agents** (`agents/*.md`): Subagents with isolated context for complex tasks. Frontmatter defines tools, model, and permission mode.
- **Skills** (`skills/*/SKILL.md`): Model-invoked when triggers match user intent. Unlike commands, skills are auto-triggered.
- **Hooks** (`hooks/hooks.json`): Event handlers (PostToolUse, SubagentStop, etc.) that run shell scripts.

### Current Plugins

**coderabbit** - CodeRabbit CLI integration for code review:
- `/coderabbit:local` - Review local changes (delegates to `cr-reviewer` subagent)
- `/coderabbit:pr` - Manage PR comments from all reviewers (delegates to `cr-pr-manager` subagent)
- `/coderabbit:auth` - CLI authentication
- `/coderabbit:config` - Plugin configuration
- `/coderabbit:log` - View review history and statistics

## Adding a New Plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, description
2. Add commands, agents, skills, hooks as needed
3. Update `.claude-plugin/marketplace.json` to include the plugin in the `plugins` array
4. Plugin `source` should be a relative path like `./plugins/<name>`

## Key Patterns

### Subagent Delegation

Commands delegate to subagents for complex tasks. This keeps verbose output (like CLI results) in the subagent's isolated context while returning concise summaries to the main conversation. Example from `commands/local.md`:

```text
Use the `cr-reviewer` subagent to perform the review. Pass the arguments:
- type: $ARGUMENTS.type or "all"
- base: $ARGUMENTS.base or auto-detect from git
```

### Hooks with Plugin Root

Hooks use `${CLAUDE_PLUGIN_ROOT}` to reference scripts relative to the plugin directory. Plugin hooks require a `hooks` wrapper (unlike settings.json):

```json
{
  "description": "Description of hooks",
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/script.sh"}]
    }]
  }
}
```

### Skill Triggers vs Commands

- Skills have `triggers` array for auto-invocation on matching phrases
- Commands are explicit: user types `/pluginname:command`
- Skills delegate to the same subagents as commands
