---
description: Manage Cloudflare Tunnels — list, create, inspect, routes
arguments:
  - name: action
    description: "Action to perform: list, create, get, connections, routes (default: list)"
    required: false
  - name: name-or-id
    description: "Tunnel name or ID for get, connections actions"
    required: false
  - name: network
    description: "CIDR network for routes create (e.g., 10.0.0.0/8)"
    required: false
---

You are managing Cloudflare Tunnels using the `cf` CLI. Based on the provided arguments, execute the appropriate command.

**Quote every user-supplied value when shelling out** (e.g. `"$ARGUMENTS.name-or-id"`, `"$ARGUMENTS.network"`). Tunnel names and CIDR strings could otherwise let shell metacharacters execute.

**For action=list (default):**
- Run `cf tunnels list --json`
- Display results in a readable table showing tunnel name, ID, status, and creation date

**For action=create:**
- Verify $ARGUMENTS.name-or-id is provided (this will be the tunnel name)
- Run `cf tunnels create "$ARGUMENTS.name-or-id" --json`
- Display the created tunnel details including the tunnel ID
- Show the cloudflared configuration snippet the user needs:

  ```yaml
  tunnel: <TUNNEL_ID>
  credentials-file: /path/to/<TUNNEL_ID>.json
  
  ingress:
    - hostname: <your-domain>.com
      service: http://localhost:8080
    - service: http_status:404
  ```

- Remind the user to download the tunnel credentials file

**For action=get:**
- Verify $ARGUMENTS.name-or-id is provided
- Run `cf tunnels get "$ARGUMENTS.name-or-id" --json`
- Display detailed tunnel information including configuration options

**For action=connections:**
- Verify $ARGUMENTS.name-or-id is provided
- Run `cf tunnels connections "$ARGUMENTS.name-or-id" --json`
- Display active connections, their IDs, IP addresses, and connection times

**For action=routes:**
- If both $ARGUMENTS.name-or-id and $ARGUMENTS.network are provided, this is a route-create request:
  - Confirm with the user: "Create route $ARGUMENTS.network on tunnel $ARGUMENTS.name-or-id? (yes/no)"
  - On confirmation, run `cf tunnels routes create "$ARGUMENTS.name-or-id" --network "$ARGUMENTS.network" --json`
  - Display the created route
- Otherwise, list existing routes:
  - Run `cf tunnels routes list --json`
  - Display configured routes in a readable format

If any required parameters are missing for the specified action, prompt the user to provide them.
