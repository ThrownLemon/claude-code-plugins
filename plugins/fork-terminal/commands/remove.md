---
description: Remove a worktree and clean up its worker session
arguments:
  - name: path
    description: Worktree path or branch name to remove
    required: true
  - name: force
    description: Force removal even with uncommitted changes
    required: false
  - name: delete-branch
    description: Also delete the associated git branch
    required: false
---

# Remove Worktree

Clean up a git worktree created by fork-terminal and unregister its worker.

## What This Does

1. **Unregister the worker** from the coordination file
2. **Remove the git worktree** directory
3. **Optionally delete the branch** if `--delete-branch` is specified

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--path` | Worktree path or branch name | required |
| `--force` | Force removal with uncommitted changes | false |
| `--delete-branch` | Also delete the git branch | false |

## Examples

```bash
# Remove by path
/fork-terminal:remove --path ../my-project-auth-refactor

# Remove by branch name
/fork-terminal:remove --path worktree/auth-refactor

# Force remove with uncommitted changes
/fork-terminal:remove --path ../my-project-tests --force

# Remove worktree and delete the branch
/fork-terminal:remove --path worktree/old-feature --delete-branch --force
```

## Execution

### Step 1: Unregister Worker

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/coordination.py unregister --path "<path>"
```

### Step 2: Remove Worktree

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/worktree_manager.py remove "<path>" [--force] [--delete-branch]
```

Or combined:

```bash
# Get branch name first if needed
git worktree list --porcelain | grep -A2 "<path>"

# Remove worktree
git worktree remove [--force] "<path>"

# Delete branch if requested
git branch -D "<branch-name>"
```

## Safety Checks

Before removing, the command will:
1. Check for uncommitted changes (unless `--force`)
2. Warn if the worktree is the current directory
3. Confirm branch deletion if `--delete-branch`

## After Removal

The worktree directory and its contents will be deleted. If you have uncommitted changes you want to keep:
1. Commit them first in the worktree
2. Or use `git stash` before removing
3. Or copy files manually before removal

## Troubleshooting

### "Worktree is locked"

```bash
git worktree unlock <path>
/fork-terminal:remove --path <path>
```

### "Directory does not exist"

The worktree may have been manually deleted. Clean up the git reference:

```bash
git worktree prune
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/coordination.py remove --path "<path>"
```
