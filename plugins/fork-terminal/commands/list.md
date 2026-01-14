---
description: List active worktrees and spawned worker sessions
arguments:
  - name: format
    description: "Output format: table or json (default: table)"
    required: false
  - name: all
    description: Show all worktrees, not just plugin-created workers
    required: false
---

# List Worktrees and Workers

Show active git worktrees and their associated Claude worker sessions.

## What This Does

1. **List git worktrees** in the current repository
2. **Show worker status** from the coordination file
3. **Display session info** (branch, path, task, status)

## Output Formats

### Table (default)

```
Worktrees for: my-project

ID   STATUS   BRANCH                    PATH                                      TASK
---- -------- ------------------------- ----------------------------------------- --------------
1    active   worktree/auth-refactor    /Users/me/my-project-auth-refactor       Refactor auth
2    active   worktree/api-tests        /Users/me/my-project-api-tests           Write API tests
```

### JSON

```json
[
  {
    "id": 1,
    "status": "active",
    "branch": "worktree/auth-refactor",
    "path": "/Users/me/my-project-auth-refactor",
    "task": "Refactor auth"
  }
]
```

## Examples

```bash
/fork-terminal:list
/fork-terminal:list --format json
/fork-terminal:list --all
```

## Execution

Run the coordination script to list workers:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/coordination.py list [--all] [--json]
```

For all worktrees (including non-plugin ones):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/worktree_manager.py list [--json]
```

## Cleanup Stale Workers

If workers show as "active" but their processes have ended, run cleanup:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/coordination.py cleanup
```

This will mark workers with dead processes as "stopped".
