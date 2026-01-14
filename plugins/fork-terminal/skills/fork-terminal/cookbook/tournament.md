# Tournament Mode Cookbook

This cookbook describes how to execute tournament mode - spawning multiple AI CLIs to compete on the same task.

## Overview

Tournament mode:
1. Spawns multiple workers (Claude, Gemini, Codex) in separate worktrees
2. Each worker gets the same task with instructions to write DONE.md when complete
3. Main session monitors for completion
4. Reviews all solutions and creates combined branch with best parts

## Supported CLIs

| CLI | Default Model | Command Pattern |
|-----|---------------|-----------------|
| Claude Code | opus | `claude --model {model} --dangerously-skip-permissions -p '{prompt}'` |
| Gemini CLI | gemini-3-pro-preview | `gemini --model {model} -y -i '{prompt}'` |
| Codex CLI | gpt-5.2-codex | `codex --model {model} --dangerously-bypass-approvals-and-sandbox '{prompt}'` |

## Execution Steps

### Step 1: Parse Tournament Request

Identify from user request:
- **Task description**: What the workers should implement
- **CLIs to use**: Default is all three (claude, gemini, codex)
- **Base branch**: Starting point (default: HEAD)

Example triggers:
- "tournament mode to implement X" → All CLIs
- "tournament with claude and gemini to fix Y" → Claude + Gemini only
- "have claude vs codex compete on Z" → Claude + Codex

### Step 2: Spawn Tournament

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py spawn \
  --task "<task description>" \
  [--clis claude,gemini,codex] \
  [--base <base-branch>] \
  [--terminal auto|tmux|window]
```

This will:
1. Create worktrees for each CLI (e.g., `project-auth-claude-1`, `project-auth-gemini-2`)
2. Create branches (e.g., `tournament/auth-claude-1`, `tournament/auth-gemini-2`)
3. Generate TASK.md in each worktree with tournament context
4. Spawn terminal sessions running each CLI
5. Register tournament in coordination file

### Step 3: Report to User

After spawning, report:
- Tournament ID
- Workers created (CLI, branch, path)
- Next steps (check status, wait for DONE.md)

Example output:
```
Tournament spawned: tournament-1736889600

Workers:
  claude: tournament/auth-claude-1
    Path: /Users/me/project-auth-claude-1
    Status: Warp terminal launched
  gemini: tournament/auth-gemini-2
    Path: /Users/me/project-auth-gemini-2
    Status: Warp terminal launched
  codex: tournament/auth-codex-3
    Path: /Users/me/project-auth-codex-3
    Status: Warp terminal launched

Workers are now competing! Check status with:
  /fork-terminal:status --tournament tournament-1736889600
```

### Step 4: Monitor Completion

Users can check progress with:
```bash
/fork-terminal:status --tournament <tournament-id>
```

Or programmatically:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py status \
  --tournament "<tournament-id>"
```

### Step 5: Review Solutions

When all workers are done (all have DONE.md):

```bash
/fork-terminal:review --tournament <tournament-id>
```

Or programmatically:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py report \
  --tournament "<tournament-id>"
```

### Step 6: Create Combined Branch

After reviewing, create a combined branch:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py combine \
  --tournament "<tournament-id>" \
  [--branch "<branch-name>"]
```

## Example: Full Tournament Flow

```
User: "tournament mode to implement user authentication with claude, gemini, codex"

1. Claude spawns tournament:
   python3 .../tournament.py spawn --task "implement user authentication" --clis claude,gemini,codex

2. Claude reports to user:
   "Tournament spawned: tournament-1736889600
    3 workers competing: claude, gemini, codex
    Check status with /fork-terminal:status"

3. User waits for workers to complete (or works on other things)

4. User checks status:
   /fork-terminal:status --tournament tournament-1736889600
   → "Completion: 3/3 - Ready for review!"

5. User requests review:
   /fork-terminal:review --tournament tournament-1736889600

6. Claude reads review report, analyzes solutions:
   - Claude's solution: JWT-based, 8 files, clean architecture
   - Gemini's solution: OAuth2, 12 files, flexible providers
   - Codex's solution: Session-based, 5 files, simple

7. Claude recommends best parts and creates combined branch
```

## Partial CLI Lists

You can run tournaments with any combination of CLIs:

```bash
# Claude vs Gemini only
python3 .../tournament.py spawn --task "fix auth bug" --clis claude,gemini

# Just Claude and Codex
python3 .../tournament.py spawn --task "add logging" --clis claude,codex

# Single CLI (creates one worker in worktree mode)
python3 .../tournament.py spawn --task "refactor database" --clis claude
```

## Error Handling

- If a worktree already exists for a branch, that worker will be skipped
- If a CLI fails to spawn, the tournament continues with remaining workers
- If no workers spawn successfully, the tournament fails

## Cleanup

After reviewing and merging, clean up worktrees:

```bash
# Remove individual worktree
/fork-terminal:remove --path ../project-auth-claude-1 --delete-branch

# Or manually for each:
git worktree remove ../project-auth-claude-1
git branch -D tournament/auth-claude-1
```
