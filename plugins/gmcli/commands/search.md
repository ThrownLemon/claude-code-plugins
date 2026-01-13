---
description: Search Gmail threads using Gmail's query syntax
arguments:
  - name: query
    description: "Gmail search query (e.g., 'from:alice subject:meeting', 'is:unread', 'newer_than:1d')"
    required: true
  - name: account
    description: Gmail account to search (default: default account)
    required: false
  - name: limit
    description: Maximum number of threads to return (default: 10)
    required: false
---

# Gmail Search

Search your Gmail inbox using Gmail's powerful query syntax.

## What This Does

This command delegates to the `gmail-assistant` subagent which will:

1. **Check Prerequisites**
   - Verify gmcli is installed
   - Check if accounts are configured
   - Guide through setup if needed

2. **Execute Search**
   - Run `gmcli search` with the provided query
   - Parse and format results

3. **Present Results**
   - Show thread summaries (subject, sender, date, snippet)
   - Offer to read specific threads
   - Show thread IDs for follow-up actions

## Gmail Query Syntax Examples

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
| `in:inbox` | In inbox |
| `in:sent` | In sent folder |

Combine with spaces: `from:alice is:unread newer_than:7d`

## Examples

```bash
/gmcli:search --query "is:unread"
/gmcli:search --query "from:boss@company.com newer_than:1d"
/gmcli:search --query "subject:invoice has:attachment" --limit 5
/gmcli:search --query "is:starred" --account work@gmail.com
```

Use the `gmail-assistant` subagent to perform the search. Pass the arguments:
- query: $ARGUMENTS.query
- account: $ARGUMENTS.account (optional)
- limit: $ARGUMENTS.limit or 10
- action: search
