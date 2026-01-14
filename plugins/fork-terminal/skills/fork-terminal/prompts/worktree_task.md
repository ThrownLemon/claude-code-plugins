# Worktree Task Handoff Template

Use this template when creating TASK.md files for worktree workers.

## Template

```markdown
# Task Assignment

## Task
${TASK_DESCRIPTION}

## Context
- **Branch**: `${BRANCH}`
- **Worktree**: `${WORKTREE_PATH}`
- **Worker ID**: ${WORKER_ID}
- **Created**: ${TIMESTAMP}

## Instructions
1. Read this file to understand your task
2. Work on the task described above
3. Commit your changes when complete
4. This is your isolated workspace - you won't conflict with other workers

## Getting Started
Run `git status` to see your current state, then begin implementing.
```

## Variables

| Variable | Description |
|----------|-------------|
| `${TASK_DESCRIPTION}` | The user's task description |
| `${BRANCH}` | Git branch name for this worktree |
| `${WORKTREE_PATH}` | Absolute path to the worktree |
| `${WORKER_ID}` | Worker number (1, 2, 3, etc.) |
| `${TIMESTAMP}` | ISO timestamp when created |

## Multi-Worker Variation

For multi-worker scenarios, append to the task description:

```markdown
## Task
${TASK_DESCRIPTION}

(Worker ${WORKER_ID} of ${TOTAL_WORKERS})
```

## Initial Prompt for Claude

When spawning Claude in the worktree, use this prompt:

```
Read TASK.md in your current directory and begin working on the assigned task.
```

This ensures Claude:
1. Reads the context file first
2. Understands it's in an isolated worktree
3. Knows to commit when done
