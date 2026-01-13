---
name: fork-terminal
description: Fork terminal sessions to spawn parallel AI agents or CLI commands in new terminal windows
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
