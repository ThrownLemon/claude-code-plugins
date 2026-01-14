---
description: Check status of tournaments and workers
arguments:
  - name: tournament
    description: Specific tournament ID (default: all active)
    required: false
  - name: format
    description: "Output format: table or json (default: table)"
    required: false
---

# Tournament Status

Check the status of active tournaments and their workers.

## What This Does

1. **List active tournaments** if no tournament ID specified
2. **Show detailed status** for a specific tournament
3. **Check for DONE.md** files to detect completion
4. **Report progress** (done/total workers)

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--tournament` | Specific tournament ID | all active |
| `--format` | `table` or `json` | `table` |

## Examples

```bash
# Show all active tournaments
/fork-terminal:status

# Show status of specific tournament
/fork-terminal:status --tournament tournament-1736889600

# Get JSON output
/fork-terminal:status --format json
```

## Execution

Run the tournament status command:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py status \
  [--tournament "<tournament-id>"] \
  [--json]
```

## Output Examples

### All Active Tournaments

```
Active tournaments: 2

  tournament-1736889600
    Task: implement user authentication
    CLIs: claude, gemini, codex
    Progress: 2/3

  tournament-1736889700
    Task: add logging
    CLIs: claude, gemini
    Progress: 0/2
```

### Specific Tournament

```
Tournament: tournament-1736889600
Task: implement user authentication
Status: running
CLIs: claude, gemini, codex

Workers:
  CLAUDE: DONE
    Branch: tournament/auth-claude-1
    Path: /Users/me/project-auth-claude-1
  GEMINI: DONE
    Branch: tournament/auth-gemini-2
    Path: /Users/me/project-auth-gemini-2
  CODEX: pending
    Branch: tournament/auth-codex-3
    Path: /Users/me/project-auth-codex-3

Completion: 2/3
```

### Ready for Review

When all workers are done:

```
Completion: 3/3
Ready for review!
```

Use `/fork-terminal:review` to start the review process.

## Related Commands

- `/fork-terminal:list` - List all worktrees and workers
- `/fork-terminal:review` - Review tournament solutions
- `/fork-terminal:remove` - Clean up a worktree
