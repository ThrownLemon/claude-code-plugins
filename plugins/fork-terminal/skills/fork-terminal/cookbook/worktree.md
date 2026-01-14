# Worktree Mode Cookbook

This cookbook describes how to spawn Claude Code sessions in git worktrees for parallel development with git isolation.

## When to Use Worktree Mode

Use worktree mode when:
- You need **git isolation** between parallel workers
- Working on **multiple features** simultaneously
- You want to **avoid file conflicts** between agents
- Each worker should be on a **separate branch**

Use regular fork mode (same directory) when:
- You need quick help on the current task
- Workers can coordinate on the same files
- You don't need branch separation

## Trigger Patterns

Worktree mode activates on these patterns:
- "fork terminal in worktree..."
- "spawn worktree for..."
- "parallel worktree..."
- "fork in worktree..."
- "spawn worker in worktree..."

## Execution Steps

### 1. Parse the Request

Extract from user's request:
- **Task description**: What they want the worker to do
- **Branch name** (optional): If they specify a branch
- **Worker count** (optional): "spawn 3 worktrees", "2 workers", etc.
- **Base branch** (optional): "from develop", "based on main"
- **Model preference** (optional): "fast", "heavy", or specific model

### 2. Spawn Workers

Execute the spawn_session.py script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "<task description>" \
  [--branch "<branch-name>"] \
  [--base "<base-branch>"] \
  [--count <1-4>] \
  [--model <opus|haiku>] \
  [--terminal <auto|tmux|window>]
```

### 3. Report Results

After spawning, report to the user:
- Number of workers spawned
- Worktree paths created
- Branch names
- How to manage workers (`/fork-terminal:list`, `/fork-terminal:remove`)

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_MODEL` | opus | Claude model for workers |
| `FAST_MODEL` | haiku | Model when "fast" specified |
| `MAX_WORKERS` | 4 | Maximum parallel workers |

## Examples

### Single Worker

User: "spawn worktree to implement user authentication"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "implement user authentication" \
  --model opus
```

### Multiple Workers

User: "spawn 3 worktrees to write tests for the API"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "write tests for the API" \
  --count 3 \
  --model opus
```

### With Branch Specification

User: "fork in worktree on branch feature/auth to refactor login"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "refactor login" \
  --branch "feature/auth" \
  --model opus
```

### Fast Model

User: "spawn worktree fast to fix the typo in config"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "fix the typo in config" \
  --model haiku
```

### From Specific Base

User: "spawn worktree from develop to implement the new feature"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "implement the new feature" \
  --base develop \
  --model opus
```

## Terminal Detection

The script automatically detects the terminal environment:

1. **Inside tmux**: Creates a new tmux window in the current session
2. **tmux available**: Creates a new detached tmux session
3. **No tmux**: Falls back to new terminal window (AppleScript on macOS, cmd.exe on Windows)

Users can override with `--terminal tmux` or `--terminal window`.

## Worktree Location

Worktrees are created as **sibling directories** to the main repo:

```
/path/to/
├── my-project/              # Main repo
├── my-project-auth/         # Worktree 1
├── my-project-tests-1/      # Worktree 2
└── my-project-tests-2/      # Worktree 3
```

## TASK.md Context File

Each worktree gets a `TASK.md` file with:
- Task description
- Branch name
- Worker ID (for multi-worker)
- Instructions for the Claude agent

## Management Commands

After spawning, users can manage workers with:

- `/fork-terminal:list` - Show active worktrees and workers
- `/fork-terminal:remove --path <path>` - Clean up a worktree

## Security Warning

> **Warning**: Workers are spawned with `--dangerously-skip-permissions` to enable autonomous operation. Only use in trusted environments where you understand the risks of unattended AI agent execution.
