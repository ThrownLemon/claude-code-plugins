# ThrownLemon's Claude Code Plugin Marketplace

A curated collection of Claude Code plugins for code quality, security, productivity, design, and creative tools.

## Table of Contents

- [Quick Start](#quick-start)
- [Available Plugins](#available-plugins)
- [Plugin Details](#plugin-details)
  - [CodeRabbit](#coderabbit)
  - [Damage Control](#damage-control)
  - [Fork Terminal](#fork-terminal)
  - [ImageGen](#imagegen)
  - [UI/UX Pro Max](#uiux-pro-max)
  - [Gmail CLI](#gmail-cli)
- [Plugin Architecture](#plugin-architecture)
- [Adding New Plugins](#adding-new-plugins)
- [FAQ](#faq)
- [License](#license)

---

## Quick Start

### 1. Add the Marketplace

```bash
/plugin marketplace add ThrownLemon/claude-code-plugins
```

### 2. Install a Plugin

```bash
/plugin install <plugin-name>@travis-plugins
```

### 3. Use the Plugin

Plugins work in different ways:
- **Commands**: Type `/pluginname:command` (e.g., `/coderabbit:local`)
- **Skills**: Auto-triggered by natural language (e.g., "review my code")
- **Hooks**: Run automatically on specific events (e.g., before a command executes)

---

## Available Plugins

| Plugin | Category | Type | Description |
|--------|----------|------|-------------|
| [coderabbit](#coderabbit) | Productivity | Commands + Skills | AI-powered code review using CodeRabbit CLI |
| [damage-control](#damage-control) | Security | Hooks + Skills | Blocks dangerous commands and protects sensitive files |
| [fork-terminal](#fork-terminal) | Productivity | Skills | Spawn parallel AI agents in new terminal windows |
| [imagegen](#imagegen) | Creative | Commands + Skills | AI image generation with Google Gemini and OpenAI |
| [ui-ux-pro-max](#uiux-pro-max) | Design | Skills | Searchable database of UI/UX design intelligence |
| [gmcli](#gmail-cli) | Productivity | Commands + Skills | Gmail integration for terminal-based email management |

---

## Plugin Details

### CodeRabbit

AI-powered code review integration using the CodeRabbit CLI.

**Installation:**
```bash
/plugin install coderabbit@travis-plugins
```

**Prerequisites:**
- [CodeRabbit CLI](https://docs.coderabbit.ai/cli/overview) installed and authenticated

**Commands:**

| Command | Description |
|---------|-------------|
| `/coderabbit:local` | Review local changes before committing |
| `/coderabbit:pr` | View and address PR review comments |
| `/coderabbit:auth` | Authenticate with CodeRabbit CLI |
| `/coderabbit:config` | Configure plugin settings |
| `/coderabbit:log` | View review history and statistics |

**Auto-Triggers:**
- "Review my code"
- "Check my changes"
- "Run code review"
- "Find bugs in my code"

**Features:**
- Local code review before creating PRs
- PR comment management (CodeRabbit + other reviewers)
- Automated review -> fix -> review loops
- Rate limit handling for free tier users
- Automatic base branch detection

**Example Usage:**
```
> Review my changes before I commit
> /coderabbit:local --type staged
> Check for issues in what I've written
```

---

### Damage Control

Defense-in-depth security protection using PreToolUse hooks. Adapted from [disler/claude-code-damage-control](https://github.com/disler/claude-code-damage-control).

**Installation:**
```bash
/plugin install damage-control@travis-plugins
```

**Prerequisites:**
- [uv](https://docs.astral.sh/uv/) (Python package runner)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

**Protection Levels:**

| Level | Read | Write | Edit | Delete | Examples |
|-------|------|-------|------|--------|----------|
| **Zero Access** | Blocked | Blocked | Blocked | Blocked | `~/.ssh/`, `~/.aws/`, `.env`, `*.pem` |
| **Read Only** | Allowed | Blocked | Blocked | Blocked | `/etc/`, lock files, `node_modules/` |
| **No Delete** | Allowed | Allowed | Allowed | Blocked | `.git/`, `LICENSE`, `README.md` |

**What Gets Blocked:**
- Destructive bash commands: `rm -rf`, `git push --force`, `DROP TABLE`
- Sensitive file access: SSH keys, AWS credentials, environment files
- Dangerous operations: Database drops, cloud resource deletions
- Accidental modifications: Lock files, build outputs, critical configs

**Ask Patterns (prompts for confirmation):**
- `git checkout -- .` (discards uncommitted changes)
- `git stash drop` (permanently deletes a stash)
- SQL DELETE with WHERE clause

**Customization:**

Edit `patterns.yaml` in the plugin directory to add custom protections:

```yaml
# Block a custom command
bashToolPatterns:
  - pattern: '\bmy-dangerous-command\b'
    reason: Custom blocked command

# Protect a custom path
zeroAccessPaths:
  - "~/.my-secrets/"
  - "*.secret"
```

---

### Fork Terminal

Spawn parallel AI agents or CLI commands in new terminal windows. Adapted from [disler/fork-repository-skill](https://github.com/disler/fork-repository-skill).

**Installation:**
```bash
/plugin install fork-terminal@travis-plugins
```

**Supported AI Tools:**

| Tool | Trigger Pattern | Default Model | Fast Model | Heavy Model |
|------|-----------------|---------------|------------|-------------|
| Claude Code | "use claude code..." | opus | haiku | opus |
| Codex CLI | "use codex..." | gpt-5.1-codex-max | codex-mini | codex-max |
| Gemini CLI | "use gemini..." | gemini-3-pro-preview | flash | gemini-pro |
| Raw CLI | "run..." | N/A | N/A | N/A |

**Model Modifiers:**
- **fast**: Use lighter/faster models for quick tasks
- **heavy**: Use most capable models for complex tasks

**Platform Support:**
- macOS: Fully supported (AppleScript)
- Windows: Fully supported (cmd.exe)
- Linux: Not yet implemented

**Example Triggers:**
```
> Fork terminal use claude code to refactor the auth module
> Fork terminal use codex fast to write tests for the API
> Fork terminal use gemini to analyze this codebase
> Fork terminal run npm start
> Spawn a new terminal with claude to handle documentation
```

**Features:**
- Context handoff with conversation summaries
- Multiple concurrent agent sessions
- Cross-tool compatibility (Claude, Codex, Gemini)
- Raw command execution for non-AI tasks

---

### ImageGen

AI-powered image generation using Google Gemini (Imagen) and OpenAI GPT-Image.

**Installation:**
```bash
/plugin install imagegen@travis-plugins
```

**Prerequisites:**
```bash
# Install required packages
pip install google-genai openai Pillow

# Set API keys (at least one)
export GEMINI_API_KEY=your_key  # or GOOGLE_API_KEY
export OPENAI_API_KEY=your_key
```

**Commands:**

| Command | Description |
|---------|-------------|
| `/imagegen:generate` | Generate images from text prompts |
| `/imagegen:edit` | Edit existing images |
| `/imagegen:iterate` | Refine images through multiple steps |
| `/imagegen:compare` | Compare Google vs OpenAI providers |
| `/imagegen:assets` | Generate project assets (icons, favicons) |
| `/imagegen:moodboard` | Create design inspiration sets |
| `/imagegen:character` | Create consistent character sheets |
| `/imagegen:config` | Configure default provider and settings |

**Auto-Triggers:**
- "Generate an image of..."
- "Create a logo for..."
- "Edit this image to..."
- "Create app icons"
- "Design character sheet"

**Provider Comparison:**

| Feature | Google Gemini | OpenAI GPT-Image |
|---------|---------------|------------------|
| **Best For** | Style variety, character consistency | Text in images, precise edits |
| **Models** | gemini-2.5-flash-image, gemini-3-pro-image-preview | gpt-image-1.5, gpt-image-1-mini |
| **Transparent BG** | Limited | Supported |
| **Multi-turn iteration** | Strong | Limited |

**Size Options:**

| Format | Google (Aspect) | OpenAI (Pixels) |
|--------|-----------------|-----------------|
| Square | 1:1 | 1024x1024 |
| Landscape | 16:9 | 1536x1024 |
| Portrait | 9:16 | 1024x1536 |
| Wide | 21:9 | - |

**Example Usage:**
```
> Generate an image of a sunset over mountains in watercolor style
> /imagegen:generate --prompt "Minimalist logo for a tech startup" --provider openai
> Create icons for my mobile app
> Edit this image to add rain effects
```

---

### UI/UX Pro Max

Searchable database of UI/UX design intelligence. Adapted from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).

**Installation:**
```bash
/plugin install ui-ux-pro-max@travis-plugins
```

**Prerequisites:**
- Python 3.x

**What's Included:**

| Category | Count | Examples |
|----------|-------|----------|
| UI Styles | 57 | Glassmorphism, Neumorphism, Brutalism, Bento Grid, Dark Mode |
| Color Palettes | 96 | By product type: SaaS, E-commerce, Healthcare, Fintech |
| Font Pairings | 50 | With Google Fonts imports ready to use |
| Chart Types | 25 | With library recommendations (Chart.js, D3, Recharts) |
| UX Guidelines | 99 | Best practices and anti-patterns |
| Tech Stacks | 11 | React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind |

**Auto-Triggers:**
- "Design a landing page for..."
- "Build a dashboard"
- "What color palette for healthcare?"
- "Font pairing for luxury brand"
- "Tailwind best practices"
- "React component patterns"

**Search Domains:**

| Domain | Use For | Example |
|--------|---------|---------|
| `product` | Product type recommendations | "SaaS dashboard" |
| `style` | UI styles and effects | "glassmorphism dark" |
| `typography` | Font pairings | "elegant professional" |
| `color` | Color palettes | "healthcare fintech" |
| `landing` | Page structures | "hero pricing" |
| `chart` | Data visualization | "trend comparison" |
| `ux` | Best practices | "animation accessibility" |

**Supported Stacks:**

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities, responsive, a11y (default) |
| `react` | State, hooks, performance, patterns |
| `nextjs` | SSR, routing, images, API routes |
| `vue` | Composition API, Pinia, Vue Router |
| `svelte` | Runes, stores, SvelteKit |
| `swiftui` | Views, State, Navigation, Animation |
| `react-native` | Components, Navigation, Lists |
| `flutter` | Widgets, State, Layout, Theming |
| `shadcn` | shadcn/ui components, theming, forms |

**Example Usage:**
```
> Design a SaaS landing page with dark mode
> Build a dashboard for healthcare analytics
> What's the best font pairing for a luxury brand?
> Tailwind best practices for responsive design
```

---

### Gmail CLI

Gmail integration using gmcli for terminal-based email management.

**Installation:**
```bash
/plugin install gmcli@travis-plugins
```

**Prerequisites:**
- [gmcli](https://github.com/jrstrunk/gmcli) installed and authenticated
  ```bash
  npm install -g gmcli
  gmcli setup  # Follow OAuth setup
  ```

**Commands:**

| Command | Description |
|---------|-------------|
| `/gmcli:search` | Search emails with Gmail query syntax |
| `/gmcli:read` | Read individual messages and threads |
| `/gmcli:send` | Send emails with optional attachments |
| `/gmcli:draft` | Create and manage drafts |
| `/gmcli:labels` | Manage email labels |
| `/gmcli:setup` | Configure gmcli credentials |

**Auto-Triggers:**
- "Check my email"
- "Any new emails?"
- "Search for emails from..."
- "Send an email to..."
- "Read that thread"

**Default Behaviors:**

| Request | Query Executed |
|---------|----------------|
| "Check my email" | `is:unread newer_than:1d` |
| "Check inbox" | `in:inbox newer_than:1d` |
| "Emails from John" | `from:John` |

**Gmail Query Examples:**
```
> Search for unread emails from my boss
> Find emails about the quarterly report
> Check if I have any emails from support
> Send an email to alice@example.com about the meeting
```

---

## Plugin Architecture

Each plugin follows a consistent structure:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── commands/                 # Slash commands (/plugin:command)
│   └── *.md                 # YAML frontmatter + instructions
├── agents/                   # Subagents for complex tasks
│   └── *.md                 # Agent definition with tools, model
├── skills/                   # Auto-triggered behaviors
│   └── <skill>/
│       └── SKILL.md         # Triggers + instructions
├── hooks/                    # Event handlers
│   └── hooks.json           # PreToolUse, PostToolUse events
└── scripts/                  # Shell scripts for hooks
```

### Plugin Types

| Type | Trigger | Use Case |
|------|---------|----------|
| **Commands** | `/plugin:command` | User-initiated actions |
| **Skills** | Natural language | Auto-triggered assistance |
| **Hooks** | Tool events | Background automation |
| **Agents** | Delegated by commands/skills | Complex multi-step tasks |

---

## Adding New Plugins

### 1. Create Plugin Structure

```bash
mkdir -p plugins/my-plugin/.claude-plugin
```

### 2. Create Plugin Manifest

`plugins/my-plugin/.claude-plugin/plugin.json`:
```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

### 3. Add Components

- **Commands**: `plugins/my-plugin/commands/command-name.md`
- **Skills**: `plugins/my-plugin/skills/skill-name/SKILL.md`
- **Hooks**: `plugins/my-plugin/hooks/hooks.json`

### 4. Register in Marketplace

Update `.claude-plugin/marketplace.json`:
```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "description": "What this plugin does",
      "version": "1.0.0",
      "author": { "name": "Your Name" },
      "source": "./plugins/my-plugin",
      "category": "productivity"
    }
  ]
}
```

### 5. Submit

Commit, push, and create a PR.

---

## FAQ

**Q: How do I see what plugins are installed?**
```bash
/plugin list
```

**Q: How do I uninstall a plugin?**
```bash
/plugin uninstall <plugin-name>@travis-plugins
```

**Q: How do I update a plugin?**
```bash
/plugin update <plugin-name>@travis-plugins
```

**Q: Why isn't my skill triggering?**

Skills trigger on specific phrases. Try using exact trigger words from the skill's `triggers` list. You can also invoke the associated command directly.

**Q: Can I use multiple plugins together?**

Yes! Plugins are independent and can be used together. For example, use `damage-control` for security while using `coderabbit` for reviews.

**Q: How do I customize damage-control patterns?**

Edit `plugins/damage-control/patterns.yaml` in your Claude Code plugins directory.

**Q: Which image provider should I use?**

- **Google Gemini**: Better for style variety, character consistency, multi-turn iteration
- **OpenAI**: Better for text in images, transparent backgrounds, precise edits

---

## License

MIT
