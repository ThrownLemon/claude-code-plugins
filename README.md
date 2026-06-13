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
  - [Consult](#consult)
- [Related Marketplaces](#related-marketplaces)
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

| Plugin | Description |
|--------|-------------|
| [coderabbit](#coderabbit) | AI-powered code review using CodeRabbit CLI |
| [damage-control](#damage-control) | Blocks dangerous commands and protects sensitive files |
| [fork-terminal](#fork-terminal) | Spawn parallel AI agents in new terminal windows or git worktrees |
| [imagegen](#imagegen) | AI image generation with Google Gemini and OpenAI |
| [ui-ux-pro-max](#uiux-pro-max) | Searchable database of UI/UX design intelligence |
| [gmcli](#gmail-cli) | Gmail integration for terminal-based email management |
| [consult](#consult) | Third-opinion AI consultation via z.ai (GLM-5.2) and Gemini — second opinions, reviews, optional stop-gate hook |
| [cloudflare](#cloudflare) | Cloudflare management via the cf CLI — DNS, tunnels, zones, cache purge, zero-trust diagnostics |
| [bambu](#bambu) | Bambu Lab X1Plus 3D printer control — status, send prints, calibration, filament, diagnostics |
| [unifi](#unifi) | UniFi network management — sites, clients, devices, port forwards, troubleshooter agent |
| [multi-ai-review](#multi-ai-review) | Parallel code review across Claude, Gemini, and Codex CLIs with consensus comparison |
| [video-gen](#video-gen) | AI video generation via Google Veo and OpenAI Sora with smart model routing |
| [audio-feedback](#audio-feedback) | Sound effects and Kokoro-TTS voice announcements for Claude Code events |
| [ultimate-statusline](#ultimate-statusline) | Configurable statusline with 30+ widgets — model, git, context, cost, rate limits |

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

#### Commands

**`/coderabbit:local`** - Review local code changes before creating a PR

| Argument | Description | Default |
|----------|-------------|---------|
| `--type` | Review scope: `uncommitted`, `committed`, or `all` | `all` |
| `--base` | Base branch to compare against | auto-detect |

```bash
/coderabbit:local
/coderabbit:local --type uncommitted
/coderabbit:local --base develop
/coderabbit:local --type committed --base main
```

**`/coderabbit:pr`** - View and manage all PR review comments

| Argument | Description | Default |
|----------|-------------|---------|
| `--pr` | PR number to manage | auto-detect from branch |
| `--filter` | Filter by reviewer (`coderabbit`, `human`, `bot`) or severity (`critical`, `major`, `minor`) | none |

```bash
/coderabbit:pr
/coderabbit:pr --pr 123
/coderabbit:pr --filter coderabbit
/coderabbit:pr --pr 456 --filter critical
```

**`/coderabbit:auth`** - Authenticate with CodeRabbit CLI

**`/coderabbit:config`** - Configure plugin settings

**`/coderabbit:log`** - View review history and statistics

#### Subagents

**`cr-reviewer`** - Code review specialist

Handles the full review workflow:
1. Checks prerequisites (CLI installed, authenticated)
2. Auto-detects base branch if not specified
3. Runs `coderabbit review --agent` with specified options
4. Categorizes findings by severity (Critical, Major, Minor, Trivial)
5. Interactive fix loop - apply fixes and re-run review to verify
6. Handles rate limiting gracefully

| Property | Value |
|----------|-------|
| Tools | Bash, Read, Edit, Write, Grep, Glob |
| Permission Mode | acceptEdits |

**`cr-pr-manager`** - PR comment manager

Manages review comments from all sources:
1. Auto-detects PR from current branch
2. Fetches comments from CodeRabbit, other bots, and human reviewers
3. Categorizes by reviewer and severity
4. Interactive actions: view details, apply fixes, mark resolved, reply

| Property | Value |
|----------|-------|
| Tools | Bash, Read, Edit, Write, Grep, Glob |

#### Hooks

| Event | Trigger | Action |
|-------|---------|--------|
| `PostToolUse` | Edit or Write | Notifies that review is available for new changes |
| `SubagentStop` | cr-reviewer completes | Logs review completion for statistics |

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

#### Hooks

This plugin uses `PreToolUse` hooks to intercept commands before execution:

| Event | Trigger | Script | Action |
|-------|---------|--------|--------|
| `PreToolUse` | Bash | `bash-tool-damage-control.py` | Blocks dangerous commands, prompts for risky ones |
| `PreToolUse` | Edit | `edit-tool-damage-control.py` | Protects sensitive files from modification |
| `PreToolUse` | Write | `write-tool-damage-control.py` | Prevents writing to protected paths |

All hooks run with a 5-second timeout and use `uv` for Python execution.

---

### Fork Terminal

Spawn parallel AI agents or CLI commands in new terminal windows. Now with **git worktree support** for isolated parallel development. Adapted from [disler/fork-repository-skill](https://github.com/disler/fork-repository-skill).

**Installation:**
```bash
/plugin install fork-terminal@travis-plugins
```

**Three Modes:**

| Mode | Use Case | Git Isolation |
|------|----------|---------------|
| **Standard** | Quick parallel help on current task | No - same directory |
| **Worktree** | Parallel feature development | Yes - separate branches |
| **Tournament** | Multiple CLIs compete on same task | Yes - separate branches per CLI |

**Execution Modes (Worktree):**

When spawning worktree workers, you'll be prompted to choose:

| Mode | Behavior |
|------|----------|
| **Interactive** (Recommended) | Worker stays open for follow-up questions and manual oversight |
| **Autonomous** | Worker runs the task and exits when done (fire-and-forget) |

**Supported AI Tools:**

| Tool | Trigger Pattern | Default Model | Fast Model |
|------|-----------------|---------------|------------|
| Claude Code | "use claude code..." | opus | sonnet |
| Codex CLI | "use codex..." | gpt-5.2-codex | gpt-5.1-codex-mini |
| Gemini CLI | "use gemini..." | gemini-pro-latest | gemini-flash-latest |
| Raw CLI | "run..." | N/A | N/A |

**Model Modifiers:**
- **fast**: Use lighter/faster models for quick tasks
- **heavy**: Use most capable models for complex tasks

**Platform Support:**
- macOS: Fully supported (Warp, Terminal.app, tmux)
- Windows: Fully supported (cmd.exe)
- Linux: Not yet implemented

**Terminal Support (macOS):**

| Terminal | Support Level |
|----------|--------------|
| **Warp** | Full automation (opens new tab, pastes and executes) |
| **Terminal.app** | Full automation via AppleScript |
| **tmux** | Creates new windows/sessions (when inside tmux) |

**Example Triggers (Standard Mode):**
```
> Fork terminal use claude code to refactor the auth module
> Fork terminal use codex fast to write tests for the API
> Fork terminal run npm start
```

**Example Triggers (Worktree Mode):**
```
> Spawn worktree to implement user authentication
> Fork in worktree to work on the API refactor
> Spawn 2 worktrees to write tests
> Fork terminal in worktree from develop to fix the login bug
```

**Example Triggers (Tournament Mode):**
```
> Tournament mode to implement user authentication
> Have claude, gemini, and codex compete on adding caching
> Race to solve the performance issue
> Tournament with claude and gemini to refactor the API
```

**Tournament Mode Workflow:**

1. **Spawn**: Creates worktrees for each CLI (e.g., Claude, Gemini, Codex)
2. **Compete**: Workers independently solve the same task
3. **Complete**: Workers write `DONE.md` when finished
4. **Review**: Main session compares solutions with `/fork-terminal:review`
5. **Combine**: Create a combined branch with best parts from each solution

**Features:**
- Context handoff with conversation summaries
- Multiple concurrent agent sessions (up to 4 workers)
- Cross-tool compatibility (Claude, Codex, Gemini)
- Raw command execution for non-AI tasks
- **Git worktree support** for branch-isolated parallel work
- **Tournament mode** for multi-CLI competition on same task
- **Warp terminal automation** with reliable command execution
- **tmux integration** for terminal multiplexing
- Worker coordination and tracking via JSON registry
- TASK.md context files for spawned workers
- AI-assisted solution review and combined branch creation

#### Commands

**`/fork-terminal:list`** - Show active worktrees and workers

| Argument | Description | Default |
|----------|-------------|---------|
| `--format` | Output format: `table` or `json` | `table` |
| `--all` | Show all worktrees, not just plugin-created | false |

**`/fork-terminal:remove`** - Clean up a worktree

| Argument | Description | Default |
|----------|-------------|---------|
| `--path` | Worktree path or branch name | required |
| `--force` | Force removal with uncommitted changes | false |
| `--delete-branch` | Also delete the git branch | false |

**`/fork-terminal:status`** - Check tournament progress

| Argument | Description | Default |
|----------|-------------|---------|
| `--tournament` | Specific tournament ID | all active |
| `--format` | Output format: `table` or `json` | `table` |

**`/fork-terminal:review`** - Review tournament solutions

| Argument | Description | Default |
|----------|-------------|---------|
| `--tournament` | Tournament ID | most recent |
| `--format` | Report format: `markdown` or `json` | `markdown` |

```bash
/fork-terminal:list
/fork-terminal:remove --path ../my-project-auth --delete-branch --force
/fork-terminal:status --tournament tournament-1234567890
/fork-terminal:review --tournament tournament-1234567890
```

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
| **Models** | gemini-2.5-flash-image, gemini-3-pro-image-preview | gpt-image-2 (default), gpt-image-1.5 (edits), chatgpt-image-latest |
| **Transparent BG** | Limited | Supported |
| **Multi-turn iteration** | Strong | Limited |

**Size Options:**

| Format | Google (Aspect) | OpenAI (Pixels) |
|--------|-----------------|-----------------|
| Square | 1:1 | 1024x1024 |
| Landscape | 16:9 | 1536x1024 |
| Portrait | 9:16 | 1024x1536 |
| Wide | 21:9 | - |

#### Commands

**`/imagegen:generate`** - Generate images from text prompts

| Argument | Description | Default |
|----------|-------------|---------|
| `--prompt` | Text description of the image to generate | required |
| `--provider` | Provider: `google` or `openai` | from config |
| `--model` | Specific model (e.g., `gemini-2.5-flash-image`, `gpt-image-1.5`) | provider default |
| `--size` | Size/aspect ratio: `1:1`, `16:9`, `square`, `landscape`, `portrait` | `1:1` |
| `--count` | Number of images to generate (1-4) | `1` |
| `--output` | Output file path | auto-generated |

```bash
/imagegen:generate --prompt "A serene mountain lake at sunset"
/imagegen:generate --prompt "Logo for a tech startup" --provider openai --size square
/imagegen:generate --prompt "Cyberpunk cityscape" --provider google --size 16:9
/imagegen:generate --prompt "Cute robot mascot" --count 4
```

**`/imagegen:edit`** - Edit existing images with AI

| Argument | Description | Default |
|----------|-------------|---------|
| `--image` | Path to the image to edit | required |
| `--prompt` | Edit instructions (what changes to make) | required |
| `--provider` | Provider: `google` or `openai` | from config |
| `--mask` | Path to mask image for inpainting (OpenAI only) | none |
| `--output` | Output file path | auto-generated |

```bash
/imagegen:edit --image photo.png --prompt "Add a rainbow in the sky"
/imagegen:edit --image portrait.jpg --prompt "Convert to watercolor painting style"
/imagegen:edit --image scene.png --prompt "Remove the person on the left" --provider openai --mask mask.png
```

**`/imagegen:iterate`** - Refine images through multiple steps

**`/imagegen:compare`** - Compare Google vs OpenAI providers side-by-side

**`/imagegen:assets`** - Generate project assets (icons, favicons, social images)

**`/imagegen:moodboard`** - Create design inspiration sets

**`/imagegen:character`** - Create consistent character sheets

**`/imagegen:config`** - Configure default provider and settings

#### Subagents

**`image-generator`** - AI image generation specialist

Handles all image generation workflows:
1. Checks API keys are configured
2. Executes the appropriate Python script based on request type
3. Presents results with file paths
4. Suggests next steps (iterate, edit, generate variations)
5. Handles errors gracefully (missing keys, rate limits, invalid paths)

| Property | Value |
|----------|-------|
| Tools | Bash, Read, Write, Glob |
| Permission Mode | acceptEdits |

**Available Scripts:**

| Script | Purpose |
|--------|---------|
| `generate.py` | Generate images from text prompts |
| `edit.py` | Edit existing images with text instructions |
| `iterate.py` | Multi-step image refinement sessions |
| `compare.py` | Compare Google vs OpenAI outputs |
| `assets.py` | Generate app icons, favicons, social images |
| `moodboard.py` | Create multiple related images |
| `character.py` | Generate consistent character sheets |

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

#### Commands

**`/gmcli:search`** - Search Gmail using query syntax

| Argument | Description | Default |
|----------|-------------|---------|
| `--query` | Gmail search query (e.g., `from:alice subject:meeting`) | required |
| `--account` | Gmail account to search | default account |
| `--limit` | Maximum threads to return | `10` |

```bash
/gmcli:search --query "is:unread"
/gmcli:search --query "from:boss@company.com newer_than:1d"
/gmcli:search --query "subject:invoice has:attachment" --limit 5
```

**Gmail Query Syntax:**

| Query | Description |
|-------|-------------|
| `from:alice` | Emails from alice |
| `to:bob` | Emails sent to bob |
| `subject:meeting` | Subject contains "meeting" |
| `is:unread` | Unread emails |
| `is:starred` | Starred emails |
| `has:attachment` | Has attachments |
| `newer_than:1d` | Last 24 hours |
| `older_than:1w` | Older than 1 week |
| `label:work` | Has label "work" |

Combine queries: `from:alice is:unread newer_than:7d`

**`/gmcli:send`** - Send an email

| Argument | Description | Default |
|----------|-------------|---------|
| `--to` | Recipient email(s), comma-separated | required |
| `--subject` | Email subject line | required |
| `--body` | Email body text (or `@/path/to/file`) | required |
| `--cc` | CC recipients, comma-separated | none |
| `--bcc` | BCC recipients, comma-separated | none |
| `--attach` | File path(s) to attach, comma-separated | none |
| `--account` | Gmail account to send from | default account |

```bash
/gmcli:send --to "alice@example.com" --subject "Quick question" --body "Are we meeting tomorrow?"
/gmcli:send --to "bob@example.com" --subject "Report" --body @report.txt --attach "/path/to/report.pdf"
/gmcli:send --to "team@example.com,lead@example.com" --subject "Update" --body "Status update..."
```

**`/gmcli:read`** - Read individual messages and threads

**`/gmcli:draft`** - Create and manage drafts

**`/gmcli:labels`** - Manage email labels

**`/gmcli:setup`** - Configure gmcli credentials

#### Subagents

**`gmail-assistant`** - Gmail management specialist

Handles all email operations:
1. Checks prerequisites (gmcli installed, accounts configured)
2. Executes the appropriate gmcli command
3. Formats results for easy reading
4. Offers follow-up actions (read thread, reply, apply labels)
5. Confirms before sending emails or deleting drafts

| Property | Value |
|----------|-------|
| Tools | Bash, Read, Write |
| Permission Mode | default (prompts for confirmation) |

**Supported Operations:**

| Operation | gmcli Command |
|-----------|--------------|
| Search | `gmcli search "<query>"` |
| Read thread | `gmcli thread <id>` |
| Send email | `gmcli send --to ... --subject ... --body ...` |
| List drafts | `gmcli drafts` |
| Create draft | `gmcli draft create ...` |
| List labels | `gmcli labels` |
| Add label | `gmcli label add <thread_id> "<labels>"` |

---

### Consult

**Description**: Third-opinion AI consultation. Calls **Z.AI (GLM-5.2)** or **Google Gemini** directly via API for second opinions, code reviews, and an optional stop-gate review hook.

Use it the same way you'd use the codex plugin's `/codex:rescue` — except the rescuer is a different model family, and there's nothing to install beyond an API key. No external CLI binary required (uses Node 18+ `fetch`).

**Setup:**

```bash
export ZAI_API_KEY="<your-zai-key>"        # https://docs.z.ai
export GEMINI_API_KEY="<your-gemini-key>"  # https://ai.google.dev
```

**Commands:**

| Command | Purpose |
|--------|---------|
| `/consult:ask <provider> "prompt"` | One-shot question to GLM or Gemini |
| `/consult:review [provider] [base] [focus]` | Auto-collected git-diff review with `SHIP IT / NEEDS WORK / BLOCKER` verdict |
| `/consult:stop-gate [provider]` | Stop-gate review pass; outputs `VERDICT: PASS \| NEEDS FIXES` |
| `/consult:config` | Show provider/key status |

**Examples:**

```
/consult:ask zai     "Is dropping the unique index on user_emails safe under concurrent writes?"
/consult:review gemini origin/main "security"
/consult:stop-gate zai
```

**Optional Stop hook** (opt-in — consumes API tokens on every turn). Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "node ${CLAUDE_PLUGIN_ROOT}/scripts/consult.mjs stop --provider zai"
      }]
    }]
  }
}
```

When the gate returns `NEEDS FIXES`, the script exits 2 and Claude Code surfaces the reviewer's notes back to the model.

Both providers share an OpenAI-compatible client, so adding more (Anthropic, Mistral, etc.) is a single entry in `scripts/lib/providers.mjs`.

---

### Multi-AI Review

Run the same code review in parallel across the Claude, Gemini, and Codex CLIs, then compare findings for consensus. Requires the relevant CLIs installed and on `PATH`.

**Commands**: `/multi-ai-review:scan`, `/multi-ai-review:report`, `/multi-ai-review:status`, `/multi-ai-review:config`
**Subagents**: `review-coordinator`, `report-generator`

Defaults: Claude `opus`, Gemini `gemini-pro-latest`, Codex `gpt-5.2-codex` (run via `codex exec --sandbox read-only`). Override with `MULTI_REVIEW_CLAUDE_MODEL` / `MULTI_REVIEW_GEMINI_MODEL` / `MULTI_REVIEW_CODEX_MODEL`; pick CLIs with `MULTI_REVIEW_CLIS`. Codex sandbox bypass is opt-in via `MULTI_REVIEW_CODEX_UNSAFE=1`.

---

### Video Gen

AI video generation with smart routing between **Google Veo** and **OpenAI Sora**.

**Commands**: `/video-gen:generate` (auto-routes), `/video-gen:veo`, `/video-gen:sora`, `/video-gen:status`
**Subagents**: `video-generator`

**Setup**: `GOOGLE_API_KEY` / `GEMINI_API_KEY` for Veo, `OPENAI_API_KEY` for Sora.

> ⚠️ The OpenAI Sora `/v1/videos` API retires **2026-09-24**; after that date the Sora path errors out at runtime and Veo is the supported route.

---

### Audio Feedback

Sound effects and spoken announcements for Claude Code events (session start/end, tool completion, subagent finish) via a local **Kokoro TTS** server.

**Commands**: `/audio-feedback:config`, `/audio-feedback:test`
**Hooks**: `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PostToolUse`, `SubagentStop` (all fire-and-forget).

**Setup**: point `KOKORO_TTS_URL` at a running [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) server (v0.5.0 changed voice/model IDs — see `/audio-feedback:config`).

---

### Ultimate Statusline

A configurable Claude Code statusline with 30+ widgets — model, git status, context usage, session cost, burn rate, rate limits, MCP status, and more, with themes.

**Commands**: install/configure the statusline and preview widgets; the `statusline-setup` skill wires it into `settings.json`.

> The installer backs up `~/.claude/settings.json` before modifying `statusLine`. The optional custom-command widget executes config-supplied commands and is **disabled by default** — enable only with trusted config.

---

### Cloudflare

Manage Cloudflare via the `cf` CLI — DNS, tunnels, zones, cache purge, and zero-trust diagnostics. (Uses a private CLI.)

**Commands**: `/cloudflare:setup`, `/cloudflare:dns`, `/cloudflare:zones`, `/cloudflare:purge`, `/cloudflare:tunnel`, `/cloudflare:diagnose`
**Subagents**: `cf-diagnostician`

**Setup**: a scoped **API Token** (`CLOUDFLARE_API_TOKEN`) is recommended over the legacy Global API Key (`CF_API_KEY` + `CF_API_EMAIL`); `CF_ACCOUNT_ID` is optional for zone-scoped ops.

---

### Bambu

Control Bambu Lab X1Plus 3D printers via the `bambu` CLI — status, prints, calibration, filament, and diagnostics with confirmations on destructive actions. (Uses a private CLI.)

**Commands**: `/bambu:status`, `/bambu:print`, `/bambu:control`, `/bambu:calibrate`, `/bambu:doctor`
**Subagents**: `bambu-doctor`

> Credential note: prefer SSH key auth over `sshpass` (which exposes the printer password via process args).

---

### UniFi

Manage UniFi network devices, clients, and sites via the `unifi` CLI, with a network-awareness skill and troubleshooter agent. (Uses a private CLI.)

**Commands**: `/unifi:sites`, `/unifi:devices`, `/unifi:clients`
**Subagents**: `unifi-troubleshooter`

**Setup**: `UNIFI_CONTROLLER_URL` plus `UNIFI_API_TOKEN` (preferred) or `UNIFI_USERNAME`/`UNIFI_PASSWORD`; `UNIFI_SITE` to target a non-default site.

---

## Related Marketplaces

Other Claude Code marketplaces I maintain that are kept separate (different scope, different update cadence):

### [servicenow-plugin](https://github.com/ThrownLemon/servicenow-plugin)

ServiceNow domain expertise plugin — catalog builder, report builder, UI-component scaffolder, and a docs-first workflow with Playwright verification.

Useful if you work with ServiceNow (catalog items, reports, Now Experience components). It is its own single-plugin marketplace, so install it independently:

```bash
/plugin marketplace add ThrownLemon/servicenow-plugin
/plugin install servicenow-plugin@servicenow-plugin
```

Skills auto-trigger on phrases like *"create a catalog item"*, *"build a report"*, *"scaffold a Now Experience component"*. Includes a `SessionStart` hook that checks for required CLIs (`snc`, `cr`, etc.) and a `PreToolUse` preflight on Bash commands.

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

## Maintenance

AI model ids go stale quickly. [`tools/check-models`](./tools/check-models) discovers every model id used across the repo, queries each provider's live `/models` endpoint, and flags stale ids while surfacing newer ones:

```bash
node tools/check-models/check-models.mjs            # all providers with a key set
node tools/check-models/check-models.mjs --provider zai --json
```

A weekly GitHub Action (`.github/workflows/check-models.yml`) runs it automatically and posts the report to the workflow summary — add `ZAI_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` as repo secrets to enable each provider.

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
