---
name: fork-terminal
description: Fork terminal sessions to spawn parallel AI agents or CLI commands in new terminal windows. Supports git worktrees for isolated parallel development.
triggers:
  - "fork terminal"
  - "fork a terminal"
  - "spawn a new terminal"
  - "open new terminal"
  - "fork terminal use claude"
  - "fork terminal use codex"
  - "fork terminal use gemini"
  - "fork terminal run"
  - "run in new terminal"
  - "parallel agent"
  - "spawn agent"
  - "new terminal window"
  - "fork terminal in worktree"
  - "spawn worktree"
  - "parallel worktree"
  - "worktree spawn"
  - "fork in worktree"
  - "work in parallel on"
  - "spawn worker in worktree"
  - "spawn workers"
  - "tournament mode"
  - "tournament to"
  - "tournament with"
  - "compete claude vs gemini"
  - "compete claude vs codex"
  - "race to solve"
  - "have claude gemini codex compete"
  - "spawn tournament"
---

# Fork Terminal Skill

This skill enables forking terminal sessions to new windows using various AI coding tools or raw CLI commands.

## Supported Tools

| Tool | Trigger Pattern | Default Model |
|------|-----------------|---------------|
| Claude Code | "fork terminal use claude code..." | opus |
| Codex CLI | "fork terminal use codex..." | gpt-5.1-codex-max |
| Gemini CLI | "fork terminal use gemini..." | gemini-3-pro-preview |
| Raw CLI | "fork terminal run..." | N/A |

### Model Modifiers

- **fast**: Use lighter/faster models (haiku, codex-mini, flash)
- **heavy**: Use most capable models (opus, codex-max, gemini-pro)

## How to Execute

1. **Identify the tool** from the user's request
2. **Read the appropriate cookbook** for execution details
3. **Execute `fork_terminal(command)`** using the Python tool

### Tool Selection

Match the user's language against these patterns:

- "fork terminal use claude code to..." → Use `cookbook/claude-code.md`
- "fork terminal use codex to..." → Use `cookbook/codex-cli.md`
- "fork terminal use gemini to..." → Use `cookbook/gemini-cli.md`
- "fork terminal run..." → Use `cookbook/cli-command.md`

## Execution Steps

### For AI Coding Tools (Claude Code, Codex, Gemini)

1. Read the corresponding cookbook file to get model variables and command format
2. Determine model based on modifier (fast/heavy/default)
3. If the user requests "with summary" or context handoff:
   - Use the template in `prompts/fork_summary_user_prompt.md`
   - Fill in conversation history summary
   - Include the next user request
4. Execute via: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "<full_command>"`

### For Raw CLI Commands

1. Parse the command from the user's request
2. Run `<command> --help` first to understand options (if needed)
3. Execute via: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "<command>"`

## Example Commands

> **Security Warning**: The `--dangerously-*` flags and `-y` (yolo) mode bypass safety prompts. Only use in trusted environments where you understand the risks of unattended AI agent execution.

```bash
# Fork with Claude Code
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "claude --model opus --dangerously-skip-permissions"

# Fork with Codex CLI
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "codex --model gpt-5.1-codex-max --dangerously-bypass-approvals-and-sandbox"

# Fork with Gemini CLI
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "gemini --model gemini-3-pro-preview -y"

# Fork with raw CLI
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/fork_terminal.py "npm run dev"
```

## Platform Support

- **macOS**: Fully supported (AppleScript)
- **Windows**: Fully supported (cmd.exe)
- **Linux**: Not yet implemented

## Example Triggers

- "Fork terminal use claude code to refactor the auth module"
- "Fork terminal use codex fast to write tests"
- "Fork terminal run npm start"
- "Spawn a new terminal with gemini to analyze this codebase"

---

## Worktree Mode

Worktree mode creates **git-isolated workspaces** for parallel development. Each worker gets its own branch and worktree directory.

### When to Use Worktree Mode

Use worktree mode when:
- You need **git isolation** between parallel workers
- Working on **multiple features** simultaneously
- You want to **avoid file conflicts** between agents

### Worktree Trigger Patterns

- "fork terminal in worktree use claude to..." → Worktree + Claude
- "spawn worktree for..." → Create worktree with task
- "spawn 3 worktrees to..." → Multiple workers
- "fork in worktree from develop..." → Specify base branch

### How to Execute Worktree Mode

1. **Identify worktree mode** from trigger patterns above
2. **Ask the user which execution mode they prefer** using the `AskUserQuestion` tool:
   - **Interactive** (default): Claude stays open for follow-up questions
   - **Autonomous**: Claude runs the task and exits when done
3. **Read the cookbook**: `cookbook/worktree.md`
4. **Execute spawn_session.py**:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "<task description>" \
  [--branch "<branch-name>"] \
  [--base "<base-branch>"] \
  [--count <1-4>] \
  [--model <opus|haiku>] \
  [--mode <interactive|autonomous>] \
  [--terminal <auto|tmux|window>]
```

### Worktree Examples

```bash
# Single worker
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "implement user authentication"

# Multiple workers
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "write API tests" \
  --count 3

# From specific base branch
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/spawn_session.py \
  --task "fix bug in login" \
  --base develop \
  --branch "fix/login-bug"
```

### Terminal Detection

Worktree mode automatically detects the terminal environment:
- **Inside tmux**: Creates new tmux window
- **tmux available**: Creates new tmux session
- **No tmux**: Falls back to new terminal window (same as regular fork)

### Management Commands

After spawning worktree workers:
- `/fork-terminal:list` - Show active worktrees and workers
- `/fork-terminal:remove --path <path>` - Clean up a worktree

### Worktree Example Triggers

- "Spawn worktree to implement the search feature"
- "Fork in worktree to refactor the database layer"
- "Spawn 2 worktrees to work on frontend and backend"
- "Fork terminal in worktree from develop to fix the auth bug"

---

## Tournament Mode

Tournament mode spawns multiple AI CLIs (Claude, Gemini, Codex) to **compete** on the same task in separate worktrees. After all workers complete, the main session reviews solutions and creates a combined branch with the best parts.

### When to Use Tournament Mode

Use tournament mode when:
- You want **multiple approaches** to the same problem
- You want to **compare** how different AI tools solve a task
- You need the **best solution** from multiple attempts

### Tournament Trigger Patterns

- "tournament mode to implement X" → All CLIs (claude, gemini, codex)
- "tournament with claude and gemini to fix Y" → Claude + Gemini
- "have claude vs codex compete on Z" → Claude + Codex
- "race to solve X" → All CLIs

### How to Execute Tournament Mode

1. **Identify tournament mode** from trigger patterns above
2. **Parse CLIs to use**: Default is all three, or parse from request
3. **Read the cookbook**: `cookbook/tournament.md`
4. **Execute tournament spawning**:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py spawn \
  --task "<task description>" \
  [--clis claude,gemini,codex] \
  [--base <base-branch>] \
  [--terminal auto|tmux|window]
```

### Tournament Workflow

1. **Spawn**: Creates worktrees and starts CLI sessions
2. **Compete**: Workers independently solve the task
3. **Complete**: Workers write DONE.md when finished
4. **Status**: User checks progress with `/fork-terminal:status`
5. **Review**: User triggers review with `/fork-terminal:review`
6. **Combine**: Create combined branch with best parts

### Tournament Commands

| Command | Description |
|---------|-------------|
| `/fork-terminal:status` | Check tournament progress |
| `/fork-terminal:review` | Review completed solutions |
| `/fork-terminal:list` | List all worktrees |
| `/fork-terminal:remove` | Clean up worktrees |

### Tournament Example

```bash
# Spawn tournament
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py spawn \
  --task "implement user authentication" \
  --clis claude,gemini,codex

# Check status
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament.py status \
  --tournament "<tournament-id>"

# Generate review report
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py report \
  --tournament "<tournament-id>"

# Create combined branch
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fork-terminal/tools/tournament_review.py combine \
  --tournament "<tournament-id>"
```

### Tournament Example Triggers

- "Tournament mode to implement user authentication"
- "Have claude, gemini, and codex compete on adding caching"
- "Race to solve the performance issue"
- "Tournament with claude and gemini to refactor the API"
