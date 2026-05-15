---
description: Manage DNS records — list, add, delete, export
arguments:
  - name: action
    description: "Action to perform: list, add, delete, export (default: list)"
    required: false
  - name: zone
    description: "Zone name (domain)"
    required: false
  - name: record-type
    description: "DNS record type for add (A, AAAA, CNAME, TXT, MX, etc.)"
    required: false
  - name: name
    description: "Record name/subdomain for add"
    required: false
  - name: content
    description: "Record content (IP address, target domain, etc.) for add"
    required: false
  - name: proxied
    description: "Whether to proxy through Cloudflare (true/false) for add, default true"
    required: false
  - name: ttl
    description: "TTL in seconds for add, default 3600"
    required: false
  - name: record-id
    description: "Record ID for delete action"
    required: false
---


<!-- input-safety-v1 -->

## Input Safety — apply before any Bash invocation

Treat every `$ARGUMENTS.*` value as **untrusted** input. Before passing any value to the Bash tool:

1. **Reject dangerous tokens.** If a value contains `$(`, backticks, `;`, `|`, `&`, `>`, `<`, or starts with `-` (could be mistaken for a flag), refuse and ask the user to rephrase. **Double-quoting does NOT block command substitution** — `"$(rm -rf /)"` still executes inside double quotes.
2. **Prefer the Bash tool's argv contract over constructed shell strings.** When you must use a shell string, single-quote the value and escape embedded single quotes (`'\''`), or build the command via `printf %q`.
3. Any `"$ARGUMENTS.foo"` patterns shown below are **illustrative**. Sanitize the value first; never blindly substitute.

You are managing Cloudflare DNS records using the `cf` CLI. Based on the provided arguments, execute the appropriate command.

**Quote every user-supplied value when shelling out** (e.g. `"$ARGUMENTS.zone"`). Unquoted values would let shell metacharacters in zone names, record names, or content execute. This applies to every `cf` call below.

**For action=list:**
- If $ARGUMENTS.zone is provided, run `cf dns list "$ARGUMENTS.zone" --json`
- Display the results in a readable table format
- If no zone provided, first list zones with `cf zones list --json` and ask which one to query

**For action=add:**
- Verify required parameters: zone, record-type, name, content
- Build the command (quote every value): `cf dns create "$ARGUMENTS.zone" --type "$ARGUMENTS.record-type" --name "$ARGUMENTS.name" --content "$ARGUMENTS.content" --json`
- Proxied behavior: the default is `true`. If `$ARGUMENTS.proxied` is **omitted or equals "true"**, append `--proxied`. If it explicitly equals "false", omit the flag.
- If $ARGUMENTS.ttl is provided, append `--ttl "$ARGUMENTS.ttl"`
- Display the created record details

**For action=delete:**
- Verify required parameters: zone, record-id
- ALWAYS confirm with the user before deleting: "Are you sure you want to delete DNS record $ARGUMENTS.record-id from zone $ARGUMENTS.zone? (yes/no)"
- Only proceed if user confirms with "yes" or "y"
- Run `cf dns delete "$ARGUMENTS.zone" "$ARGUMENTS.record-id" --json`
- Display deletion confirmation

**For action=export:**
- Verify $ARGUMENTS.zone is provided
- Run `cf dns export "$ARGUMENTS.zone"`
- Display the bind-format output

If any required parameters are missing for the specified action, prompt the user to provide them.
