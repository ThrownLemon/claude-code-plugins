# gmcli Plugin for Claude Code

Gmail CLI integration for Claude Code - search, read, send, and manage emails from your terminal using [gmcli](https://github.com/badlogic/gmcli).

## Features

- **Search emails** using Gmail's powerful query syntax
- **Read threads** with full conversation history and attachments
- **Send emails** with CC, BCC, and attachment support
- **Manage drafts** - create, edit, send, delete
- **Organize with labels** - add/remove labels, archive messages
- **Natural language** - just say "check my email" and it works

## Installation

```bash
# Install the plugin
/plugin marketplace add github:ThrownLemon/claude-code-plugins
/plugin add gmcli
```

## Prerequisites

### 1. Install gmcli

```bash
npm install -g @mariozechner/gmcli
```

### 2. Set up Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download the credentials JSON file
6. Configure gmcli:
   ```bash
   gmcli credentials add /path/to/credentials.json
   ```

### 3. Add your Gmail account

```bash
gmcli accounts add
```

This opens a browser for OAuth authentication.

Or use the setup command:

```bash
/gmcli:setup
```

## Commands

| Command | Description |
|---------|-------------|
| `/gmcli:search` | Search emails with Gmail query syntax |
| `/gmcli:read` | Read an email thread by ID |
| `/gmcli:send` | Send an email |
| `/gmcli:draft` | Create, edit, list, send, or delete drafts |
| `/gmcli:labels` | List labels or add/remove labels from threads |
| `/gmcli:setup` | Install gmcli and configure accounts |

## Usage Examples

### Search Emails

```bash
/gmcli:search --query "is:unread"
/gmcli:search --query "from:alice@example.com newer_than:7d"
/gmcli:search --query "subject:invoice has:attachment"
```

### Read a Thread

```bash
/gmcli:read --thread 18abc123def456
/gmcli:read --thread 18abc123def456 --download true
```

### Send Email

```bash
/gmcli:send --to "bob@example.com" --subject "Hello" --body "Message here"
/gmcli:send --to "team@company.com" --subject "Report" --body @report.txt --attach "/path/to/file.pdf"
```

### Manage Drafts

```bash
/gmcli:draft                          # List drafts
/gmcli:draft --action create --to "alice@example.com" --subject "Draft" --body "Content"
/gmcli:draft --action send --draft abc123
```

### Manage Labels

```bash
/gmcli:labels                         # List all labels
/gmcli:labels --action add --thread 18abc123 --label "Work"
/gmcli:labels --action remove --thread 18abc123 --label "INBOX"   # Archive
```

## Natural Language

The plugin responds to natural phrases:
- "Check my email"
- "Any new messages?"
- "Search for emails from John"
- "Send an email to alice@example.com"
- "Read that thread"

## Gmail Query Syntax

| Query | Meaning |
|-------|---------|
| `from:alice` | From alice |
| `to:bob` | Sent to bob |
| `subject:meeting` | Subject contains "meeting" |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `has:attachment` | Has attachments |
| `newer_than:1d` | Last 24 hours |
| `older_than:1w` | Older than 1 week |
| `label:work` | Has label "work" |
| `in:inbox` | In inbox |
| `in:sent` | In sent folder |

Combine queries: `from:boss is:unread newer_than:7d`

## Data Storage

gmcli stores data in `~/.gmcli/`:
- `credentials.json` - OAuth2 client credentials
- `accounts/` - Per-account tokens
- `attachments/` - Downloaded attachments

## Credits

Built on [gmcli](https://github.com/badlogic/gmcli) by Mario Zechner.
