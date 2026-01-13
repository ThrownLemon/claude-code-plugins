---
name: damage-control
description: Security protection system that blocks dangerous commands and protects sensitive files
triggers:
  - damage control
  - security protection
  - block dangerous commands
  - protect files
  - file protection
  - command protection
---

# Damage Control Security System

You are helping a user with the damage-control security plugin. This plugin provides defense-in-depth protection for Claude Code by intercepting tool calls before execution.

## What This Plugin Does

The damage-control plugin uses PreToolUse hooks to:

1. **Block dangerous bash commands** - Prevents destructive operations like `rm -rf`, `git push --force`, database drops, cloud resource deletions
2. **Protect sensitive files** - Blocks access to secrets, credentials, and system files
3. **Guard against accidental modifications** - Prevents edits to lock files, build outputs, and critical configs

## Protection Levels

| Level | Read | Write | Edit | Delete | Examples |
|-------|------|-------|------|--------|----------|
| **zeroAccessPaths** | Blocked | Blocked | Blocked | Blocked | ~/.ssh/, ~/.aws/, .env files, *.pem |
| **readOnlyPaths** | Allowed | Blocked | Blocked | Blocked | /etc/, lock files, node_modules/ |
| **noDeletePaths** | Allowed | Allowed | Allowed | Blocked | .git/, LICENSE, README.md |

## Configuration

The protection patterns are defined in `patterns.yaml`. Users can customize:

- **bashToolPatterns**: Regex patterns for dangerous commands
- **zeroAccessPaths**: Files/directories with no access allowed
- **readOnlyPaths**: Files that can be read but not modified
- **noDeletePaths**: Files that can be modified but not deleted

### Ask Patterns

Some patterns use `ask: true` to prompt for confirmation instead of blocking outright:
- `git checkout -- .` (discards uncommitted changes)
- `git stash drop` (permanently deletes a stash)
- SQL DELETE with WHERE clause

## Requirements

This plugin requires **uv** (Python package runner) to be installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Testing the Protection

Try these commands to verify the hooks are working:

```bash
# Should be blocked (dangerous command pattern: rm with -rf flags)
rm -rf /tmp/test

# Should be blocked (zero-access path: ~/.ssh/)
cat ~/.ssh/id_rsa

# Should prompt for confirmation (ask pattern: discards uncommitted changes)
git checkout -- .
```

## Customizing Patterns

To add custom patterns, edit the `patterns.yaml` file in the plugin directory. For example, to block a specific command:

```yaml
bashToolPatterns:
  - pattern: '\bmy-dangerous-command\b'
    reason: Custom blocked command
```

Or to protect a custom path:

```yaml
zeroAccessPaths:
  - "~/.my-secrets/"
  - "*.secret"
```
