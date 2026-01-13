---
name: email
description: Gmail management using gmcli. Use when user wants to check, search, read, send, or manage emails.
triggers:
  - "check my email"
  - "check email"
  - "check emails"
  - "check my inbox"
  - "any new emails"
  - "unread emails"
  - "search emails"
  - "search my email"
  - "find email"
  - "find emails"
  - "look for email"
  - "send email"
  - "send an email"
  - "compose email"
  - "write email"
  - "draft email"
  - "email from"
  - "emails from"
  - "read email"
  - "read thread"
  - "open email"
  - "gmail"
  - "inbox"
  - "new messages"
---

# Gmail Email Management

When the user wants to manage their email from the terminal, delegate to the `gmail-assistant` subagent.

## When to Use

Use this skill when the user:
- Asks to check their email or inbox
- Wants to search for specific emails
- Needs to read an email thread
- Wants to send or compose an email
- Mentions Gmail or email management
- Asks about unread messages

## What the Subagent Handles

The `gmail-assistant` subagent uses gmcli to:

1. **Search Emails**
   - Use Gmail query syntax
   - Return formatted results
   - Offer to read specific threads


2. **Read Threads**
   - Display full conversation
   - Show attachments
   - Offer follow-up actions

3. **Send Emails**
   - Compose with to/cc/bcc
   - Support attachments
   - Confirm before sending

4. **Manage Drafts**
   - Create, edit, delete drafts
   - Send saved drafts

5. **Handle Labels**
   - List available labels
   - Add/remove labels from threads
   - Archive messages

## Default Behaviors

- **"Check my email"** - Search for unread emails: `is:unread newer_than:1d`
- **"Any new emails?"** - Same as above
- **"Check inbox"** - Show recent inbox: `in:inbox newer_than:1d`
- **"Email from X"** - Search: `from:X`

## Setup Required

If gmcli is not installed or configured, the subagent will guide the user through setup:
1. Install via npm
2. Configure Google OAuth credentials
3. Add Gmail account

## Example Triggers

- "Check if I have any new emails"
- "Search for emails from John about the project"
- "Send an email to alice@example.com"
- "Read that email thread"
- "Check my inbox for unread messages"
- "Any emails from my boss today?"
