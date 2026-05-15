---
description: Quick zone overview — list all zones or get zone details
arguments:
  - name: action
    description: "Action to perform: list, get (default: list)"
    required: false
  - name: zone
    description: "Zone name for get action"
    required: false
---

You are providing a quick overview of Cloudflare zones using the `cf` CLI.

**For action=list (default):**
- Run `cf zones list --json`
- Display results in a readable table showing:
  - Zone name (domain)
  - Zone ID
  - Status (active, pending, etc.)
  - Name servers (abbreviated)
- Count total zones and display at the top

**For action=get:**
- Verify $ARGUMENTS.zone is provided
- Quote the zone value when shelling out. Run: `cf zones get "$ARGUMENTS.zone" --json`
- Display detailed zone information including:
  - Zone name and ID
  - Status
  - Name servers (full list)
  - Plan type
  - Created/modified dates
  - Any relevant settings or flags

If zone is required but not provided for the get action, prompt the user to provide the zone name.
