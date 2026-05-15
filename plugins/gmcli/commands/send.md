---
description: Send an email directly from the command line
arguments:
  - name: to
    description: Recipient email address(es), comma-separated
    required: true
  - name: subject
    description: Email subject line
    required: true
  - name: body
    description: Email body text (or path to file with @/path/to/file)
    required: true
  - name: cc
    description: CC recipients, comma-separated
    required: false
  - name: bcc
    description: BCC recipients, comma-separated
    required: false
  - name: attach
    description: File path(s) to attach, comma-separated
    required: false
  - name: account
    description: Gmail account to send from (default: default account)
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

# Send Email

Send an email directly from the terminal with full support for CC, BCC, and attachments.

## What This Does

This command delegates to the `gmail-assistant` subagent which will:

1. **Validate Input**
   - Check email addresses are valid
   - Verify attachments exist
   - Confirm account is authenticated

2. **Compose Email**
   - Format message with provided details
   - Attach files if specified

3. **Send and Confirm**
   - Execute send via gmcli
   - Report success/failure
   - Show sent message details

## Body Content

The body can be:
- Inline text: `--body "Hello, this is my message"`
- File reference: `--body @/path/to/message.txt`

For multi-paragraph emails, using a file is recommended.

## Examples

```bash
# Simple email
/gmcli:send --to "alice@example.com" --subject "Quick question" --body "Are we meeting tomorrow?"

# With CC and attachment
/gmcli:send --to "bob@example.com" --subject "Report" --body @report-email.txt --cc "manager@example.com" --attach "/path/to/report.pdf"

# Multiple recipients
/gmcli:send --to "team@example.com,lead@example.com" --subject "Update" --body "Project status update..."

# From specific account
/gmcli:send --to "client@example.com" --subject "Proposal" --body @proposal.txt --account work@gmail.com
```

## Security Note

Be careful with attachments - ensure you're attaching the correct files. The subagent will confirm before sending.

Use the `gmail-assistant` subagent to send the email. Pass the arguments:
- to: $ARGUMENTS.to
- subject: $ARGUMENTS.subject
- body: $ARGUMENTS.body
- cc: $ARGUMENTS.cc (optional)
- bcc: $ARGUMENTS.bcc (optional)
- attach: $ARGUMENTS.attach (optional)
- account: $ARGUMENTS.account (optional)
- action: send
