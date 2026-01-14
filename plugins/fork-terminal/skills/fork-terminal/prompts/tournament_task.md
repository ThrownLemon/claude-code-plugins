# Tournament Task Template

This template is used to generate TASK.md files for tournament workers.

## Variables

| Variable | Description |
|----------|-------------|
| `${TASK_DESCRIPTION}` | The task to complete |
| `${TOURNAMENT_ID}` | Unique tournament identifier |
| `${CLI_TYPE}` | This worker's CLI (claude, gemini, codex) |
| `${OTHER_CLIS}` | Other CLIs competing |
| `${BRANCH}` | Git branch for this worker |
| `${WORKTREE_PATH}` | Path to the worktree |
| `${WORKER_ID}` | Worker number in tournament |

## Template

```markdown
# Tournament Task Assignment

## Task
${TASK_DESCRIPTION}

## Tournament Context
- **Tournament ID**: `${TOURNAMENT_ID}`
- **Your CLI**: `${CLI_TYPE}` (competing against: ${OTHER_CLIS})
- **Branch**: `${BRANCH}`
- **Worktree**: `${WORKTREE_PATH}`
- **Worker ID**: ${WORKER_ID}

## Instructions
1. Work on the task described above
2. Commit your changes as you go
3. **When complete, create DONE.md** in this directory with:
   - Summary of your approach
   - List of files modified
   - Key decisions made
   - Any trade-offs

## DONE.md Template

When finished, create a file called `DONE.md` with this structure:

\`\`\`markdown
# Solution Complete

## Summary
[Brief description of your approach - 2-3 sentences]

## Files Modified
- path/to/file1.ts - [what was changed]
- path/to/file2.ts - [what was changed]

## Key Decisions
- [Decision 1 and why you made it]
- [Decision 2 and why you made it]

## Trade-offs
- [Any limitations or trade-offs in your solution]
\`\`\`

## IMPORTANT
Your solution will not be reviewed until DONE.md exists in this directory!
```

## Usage

This template is rendered by `tournament.py:create_tournament_task_file()` when spawning tournament workers.
