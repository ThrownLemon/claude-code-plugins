---
description: Manage Gmail labels - list, add, or remove labels from threads
arguments:
  - name: action
    description: "Action: list, add, remove (default: list)"
    required: false
  - name: thread
    description: Thread ID to modify (for add/remove)
    required: false
  - name: label
    description: Label name(s) to add/remove, comma-separated
    required: false
  - name: account
    description: Gmail account (default: default account)
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Manage Gmail Labels

List available labels or add/remove labels from email threads.

## What This Does

This command delegates to the `gmail-assistant` subagent which will handle label operations:

### List Labels (default)
Shows all available labels in your Gmail account including system labels and custom labels.

### Add Labels
Applies one or more labels to a thread. The thread will appear in those label folders.

### Remove Labels
Removes labels from a thread. Common use: archive (remove INBOX label).

## System Labels

Gmail has built-in system labels:

- `INBOX` - Main inbox
- `STARRED` - Starred messages
- `IMPORTANT` - Marked important
- `SENT` - Sent mail
- `DRAFT` - Drafts
- `SPAM` - Spam folder
- `TRASH` - Deleted items
- `UNREAD` - Unread messages (pseudo-label)

## Examples

```bash
# List all labels
/gmcli:labels
/gmcli:labels --action list

# Add label to thread
/gmcli:labels --action add --thread 18abc123 --label "Work"

# Add multiple labels
/gmcli:labels --action add --thread 18abc123 --label "Work,Urgent"

# Remove label (archive = remove INBOX)
/gmcli:labels --action remove --thread 18abc123 --label "INBOX"

# Mark as read
/gmcli:labels --action remove --thread 18abc123 --label "UNREAD"
```

## Workflow Example

```bash
# Search for unread emails
/gmcli:search --query "is:unread from:team@company.com"

# Read the thread
/gmcli:read --thread 18abc123

# Archive and label it
/gmcli:labels --action add --thread 18abc123 --label "Projects"
/gmcli:labels --action remove --thread 18abc123 --label "INBOX"
```

Use the `gmail-assistant` subagent to manage labels. Pass the arguments:
- action: $ARGUMENTS.action or "list"
- thread: $ARGUMENTS.thread (for add/remove)
- label: $ARGUMENTS.label (for add/remove)
- account: $ARGUMENTS.account (optional)
