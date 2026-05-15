---
description: Read a Gmail thread by ID, showing all messages and attachments
arguments:
  - name: thread
    description: Thread ID to read (from search results)
    required: true
  - name: account
    description: Gmail account (default: default account)
    required: false
  - name: download
    description: Download attachments (default: false)
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Read Gmail Thread

View the complete contents of an email thread including all messages and attachments.

## What This Does

This command delegates to the `gmail-assistant` subagent which will:

1. **Fetch Thread**
   - Retrieve thread by ID
   - Show all messages in conversation order

2. **Display Content**
   - Show sender, recipients, date for each message
   - Display full message body
   - List any attachments

3. **Attachment Handling**
   - List attachments with file names and sizes
   - Optionally download to ~/.gmcli/attachments/

## Getting Thread IDs

Thread IDs are returned from `/gmcli:search`. Example workflow:

```bash
/gmcli:search --query "from:alice"
# Returns: Thread 18abc123... "Meeting tomorrow"

/gmcli:read --thread 18abc123
```

## Examples

```bash
/gmcli:read --thread 18abc123def456
/gmcli:read --thread 18abc123def456 --download true
/gmcli:read --thread 18abc123def456 --account work@gmail.com
```

Use the `gmail-assistant` subagent to read the thread. Pass the arguments:
- thread: $ARGUMENTS.thread
- account: $ARGUMENTS.account (optional)
- download: $ARGUMENTS.download or false
- action: read
