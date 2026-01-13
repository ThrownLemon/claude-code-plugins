# ThrownLemon's Claude Code Plugin Marketplace

A collection of Claude Code plugins for code quality, productivity, and development tools.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add ThrownLemon/claude-code-plugins
```

Then install individual plugins:

```
/plugin install <plugin-name>@travis-plugins
```

## Available Plugins

| Plugin | Description | Commands |
|--------|-------------|----------|
| [coderabbit](./plugins/coderabbit/) | CodeRabbit integration - local code review and PR comment management | `/coderabbit:local`, `/coderabbit:pr`, `/coderabbit:auth`, `/coderabbit:config` |
| [damage-control](./plugins/damage-control/) | Security protection - blocks dangerous commands and protects sensitive files | (hooks only) |
| [fork-terminal](./plugins/fork-terminal/) | Fork terminal sessions to spawn parallel AI agents or CLI commands | (skill auto-triggered) |
| [imagegen](./plugins/imagegen/) | AI image generation using Google Gemini and OpenAI GPT-Image | `/imagegen:generate`, `/imagegen:edit`, `/imagegen:iterate` |
| [ui-ux-pro-max](./plugins/ui-ux-pro-max/) | UI/UX design intelligence - 57 styles, 96 palettes, 50 fonts, 25 charts, 11 stacks | (skill auto-triggered) |
| [gmcli](./plugins/gmcli/) | Gmail CLI integration - search, read, send, and manage emails | `/gmcli:search`, `/gmcli:read`, `/gmcli:send` |

## Plugin Details

### CodeRabbit

AI-powered code review integration using the CodeRabbit CLI.

**Features:**
- Local code review before creating PRs
- PR comment management (CodeRabbit + other reviewers)
- Automated review → fix → review loops
- Rate limit handling for free tier

**Installation:**
```
/plugin install coderabbit@travis-plugins
```

**Prerequisites:**
- [CodeRabbit CLI](https://docs.coderabbit.ai/cli/overview)

### Damage Control

Defense-in-depth security protection using PreToolUse hooks. Adapted from [disler/claude-code-damage-control](https://github.com/disler/claude-code-damage-control).

**Features:**
- Blocks dangerous bash commands (rm -rf, git push --force, DROP TABLE, etc.)
- Protects sensitive files (.env, ~/.ssh/, credentials, API keys)
- Three protection tiers: zero-access, read-only, no-delete
- Ask patterns for confirmation on risky-but-valid operations
- 100+ dangerous command patterns out of the box

**Installation:**
```
/plugin install damage-control@travis-plugins
```

**Prerequisites:**
- [uv](https://docs.astral.sh/uv/) (Python package runner)

### Fork Terminal

Spawn parallel AI agents or CLI commands in new terminal windows. Adapted from [disler/fork-repository-skill](https://github.com/disler/fork-repository-skill).

**Features:**
- Fork terminal sessions with Claude Code, Codex CLI, or Gemini CLI
- Run raw CLI commands in separate terminal windows
- Model modifiers: "fast" for lighter models, "heavy" for most capable
- Context handoff with conversation summaries
- Cross-platform: macOS and Windows

**Installation:**
```
/plugin install fork-terminal@travis-plugins
```

**Supported Tools:**
| Tool | Trigger | Default Model |
|------|---------|---------------|
| Claude Code | "fork terminal use claude code..." | opus |
| Codex CLI | "fork terminal use codex..." | gpt-5.1-codex-max |
| Gemini CLI | "fork terminal use gemini..." | gemini-3-pro-preview |
| Raw CLI | "fork terminal run..." | N/A |

**Example Triggers:**
- "Fork terminal use claude code to refactor the auth module"
- "Fork terminal use codex fast to write tests"
- "Fork terminal run npm start"

### ImageGen

AI-powered image generation using Google Gemini (Imagen) and OpenAI GPT-Image.

**Features:**
- Generate images from text prompts
- Edit and iterate on existing images
- Create project assets (icons, favicons, social images)
- Generate moodboards and character sheets
- Compare providers side-by-side

**Installation:**
```
/plugin install imagegen@travis-plugins
```

**Prerequisites:**
- Python 3.x with `google-genai`, `openai`, `Pillow`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` for Google
- `OPENAI_API_KEY` for OpenAI

### UI/UX Pro Max

Searchable database of UI/UX design intelligence. Adapted from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).

**Features:**
- 57 UI styles (glassmorphism, neumorphism, brutalism, etc.)
- 96 color palettes by product type
- 50 font pairings with Google Fonts imports
- 25 chart type recommendations
- 99 UX guidelines and anti-patterns
- 11 tech stack best practices (React, Next.js, Vue, Tailwind, etc.)

**Installation:**
```
/plugin install ui-ux-pro-max@travis-plugins
```

**Example Triggers:**
- "Design a SaaS landing page"
- "What color palette for healthcare?"
- "Font pairing for luxury brand"
- "Tailwind best practices for responsive"

**Prerequisites:**
- Python 3.x (for search scripts)

### Gmail CLI

Gmail integration using gmcli for terminal-based email management.

**Features:**
- Search emails with Gmail query syntax
- Read individual messages and threads
- Send emails with attachments
- Manage labels and drafts

**Installation:**
```
/plugin install gmcli@travis-plugins
```

**Prerequisites:**
- [gmcli](https://github.com/jrstrunk/gmcli) installed and authenticated

## Adding New Plugins

To add a new plugin to this marketplace:

1. Create a new directory under `plugins/`
2. Add the plugin structure (`.claude-plugin/plugin.json`, commands, agents, etc.)
3. Update `.claude-plugin/marketplace.json` to include the new plugin
4. Commit and push

## License

MIT
