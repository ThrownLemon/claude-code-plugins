---
description: Purge Cloudflare cache — all URLs or specific URLs
arguments:
  - name: zone
    description: "Zone name (domain) to purge cache for"
    required: true
  - name: url
    description: "Comma-separated list of specific URLs to purge (omit to purge entire cache)"
    required: false
---

You are purging Cloudflare cache for a zone. This is a destructive operation that will immediately affect users serving content from the edge.

**ALWAYS confirm with the user before purging.**

**Quote every user-supplied value when shelling out.** Always wrap `$ARGUMENTS.zone` and `$ARGUMENTS.url` in double quotes so shell metacharacters (`&`, `;`, `$()`, etc.) cannot execute.

First, verify the zone exists by running `cf zones get "$ARGUMENTS.zone" --json`. If the zone doesn't exist, inform the user.

Then, based on the parameters:

**If $ARGUMENTS.url is provided (purge specific URLs):**
- Parse the comma-separated URLs
- Display what will be purged: "I will purge cache for these URLs: <list>"
- Ask for confirmation: "Are you sure you want to proceed? (yes/no)"
- Only proceed if user confirms with "yes" or "y"
- Run `cf zones purge "$ARGUMENTS.zone" "$ARGUMENTS.url" --json`
- Display purged URLs and confirmation

**If $ARGUMENTS.url is not provided (purge entire cache):**
- Display a strong warning: "⚠️  WARNING: This will purge the ENTIRE cache for zone $ARGUMENTS.zone. All cached content will need to be re-fetched from origin."
- Ask for confirmation: "Type 'yes' to confirm you want to purge the entire cache for $ARGUMENTS.zone:"
- Only proceed if user confirms with exactly "yes"
- Run `cf zones purge "$ARGUMENTS.zone" --json`
- Display confirmation that entire cache was purged

After successful purge, remind the user: "Cache has been purged. It may take a few moments for changes to propagate across all edge locations."
