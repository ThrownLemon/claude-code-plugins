---
description: Create, edit, list, or send drafts
arguments:
  - name: action
    description: "Action: create, list, edit, delete, send (default: list)"
    required: false
  - name: to
    description: Recipient for new draft
    required: false
  - name: subject
    description: Subject for new draft
    required: false
  - name: body
    description: Body for new draft (or @/path/to/file)
    required: false
  - name: draft
    description: Draft ID for edit/delete/send operations
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

# Manage Gmail Drafts

Create, edit, list, delete, or send email drafts.

## What This Does

This command delegates to the `gmail-assistant` subagent which will handle draft operations:

### List Drafts (default)
Shows all saved drafts with IDs, subjects, and recipients.

### Create Draft
Creates a new draft with the specified content. The draft is saved but not sent.

### Edit Draft
Modifies an existing draft by ID. Can update to, subject, or body.

### Delete Draft
Permanently removes a draft by ID.

### Send Draft
Sends an existing draft, removing it from drafts folder.

## Examples

```bash
# List all drafts
/gmcli:draft
/gmcli:draft --action list

# Create a new draft
/gmcli:draft --action create --to "alice@example.com" --subject "Project Update" --body "Draft content here..."

# Edit an existing draft
/gmcli:draft --action edit --draft abc123 --body "Updated content"

# Send a draft
/gmcli:draft --action send --draft abc123

# Delete a draft
/gmcli:draft --action delete --draft abc123
```

## Workflow Example

```bash
# Create draft for review
/gmcli:draft --action create --to "boss@company.com" --subject "Proposal" --body @proposal.txt

# Review it later
/gmcli:draft --action list

# Make changes
/gmcli:draft --action edit --draft <id> --body @proposal-v2.txt

# Send when ready
/gmcli:draft --action send --draft <id>
```

Use the `gmail-assistant` subagent to manage drafts. Pass the arguments:
- action: $ARGUMENTS.action or "list"
- to: $ARGUMENTS.to (for create)
- subject: $ARGUMENTS.subject (for create)
- body: $ARGUMENTS.body (for create/edit)
- draft: $ARGUMENTS.draft (for edit/delete/send)
- account: $ARGUMENTS.account (optional)
