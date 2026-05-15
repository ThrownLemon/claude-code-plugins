---
description: Set up gmcli - install, configure credentials, and add Gmail accounts
arguments:
  - name: action
    description: "Action: install, credentials, add-account, list-accounts, remove-account, status"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Gmail CLI Setup

Set up and configure gmcli for managing Gmail from the terminal.

## What This Does

This command delegates to the `gmail-assistant` subagent which will guide you through setup:

### Status (default)
Check if gmcli is installed and configured, show account status.

### Install
Install gmcli via npm:
```bash
npm install -g @mariozechner/gmcli
```

### Credentials
Guide through Google Cloud Console setup:
1. Create a project
2. Enable Gmail API
3. Create OAuth2 credentials
4. Download and configure credentials.json

### Add Account
Add a Gmail account to gmcli. Requires credentials to be configured first.

### List Accounts
Show all configured Gmail accounts.

### Remove Account
Remove a Gmail account from gmcli configuration.

## First-Time Setup Workflow

1. **Install gmcli**
   ```
   /gmcli:setup --action install
   ```

2. **Configure Google credentials**
   ```
   /gmcli:setup --action credentials
   ```
   This will guide you through creating OAuth2 credentials in Google Cloud Console.

3. **Add your Gmail account**
   ```
   /gmcli:setup --action add-account
   ```
   Opens browser for OAuth authentication.

4. **Verify setup**
   ```
   /gmcli:setup --action status
   ```

## Examples

```bash
# Check current status
/gmcli:setup
/gmcli:setup --action status

# Full setup from scratch
/gmcli:setup --action install
/gmcli:setup --action credentials
/gmcli:setup --action add-account

# Manage accounts
/gmcli:setup --action list-accounts
/gmcli:setup --action remove-account
```

## Data Storage

gmcli stores all data in `~/.gmcli/`:
- `credentials.json` - OAuth2 client credentials
- `accounts/` - Per-account tokens
- `attachments/` - Downloaded attachments

Use the `gmail-assistant` subagent to handle setup. Pass the arguments:
- action: $ARGUMENTS.action or "status"
