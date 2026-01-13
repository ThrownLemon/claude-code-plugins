---
description: Set up gmcli - install, configure credentials, and add Gmail accounts
arguments:
  - name: action
    description: "Action: install, credentials, add-account, list-accounts, remove-account, status"
    required: false
---

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
