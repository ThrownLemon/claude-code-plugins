---
description: View and modify multi-ai-review plugin settings
---

# Multi-AI Review Configuration

View and configure plugin settings for multi-AI code review.

## Configuration Options

### CLI Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Claude model | `MULTI_REVIEW_CLAUDE_MODEL` | `opus` | Claude Code model to use |
| Gemini model | `MULTI_REVIEW_GEMINI_MODEL` | `gemini-2.5-pro` | Gemini CLI model |
| Codex model | `MULTI_REVIEW_CODEX_MODEL` | `o3` | Codex CLI model |

### Review Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Default timeout | `MULTI_REVIEW_TIMEOUT` | `10` | Minutes per CLI |
| Default CLIs | `MULTI_REVIEW_CLIS` | `claude,gemini,codex` | CLIs to use |
| Output directory | `MULTI_REVIEW_OUTPUT_DIR` | `~/.multi-ai-review` | Where results are stored |

## Configuring Settings

### Option 1: Environment Variables

```bash
export MULTI_REVIEW_TIMEOUT=15
export MULTI_REVIEW_CLIS=claude,gemini
export MULTI_REVIEW_CLAUDE_MODEL=sonnet
```

### Option 2: Project .env File

Add to your project's `.env`:

```text
MULTI_REVIEW_TIMEOUT=15
MULTI_REVIEW_CLIS=claude,gemini
```

## CLI Installation

Check which CLIs are installed:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_runner.py check
```

### Installation Instructions

**Claude Code** (already installed if you're using this plugin)

**Gemini CLI**:
```bash
npm install -g @google/gemini-cli
```

**Codex CLI**:
```bash
npm install -g @openai/codex
```

## Steps

1. Display current configuration from environment
2. Check which CLIs are installed
3. Show any missing CLIs with install instructions
4. List recent reviews if any exist
