---
description: Diagnose Bambu printer connectivity and configuration issues — delegates to the bambu-doctor subagent.
---

# /bambu:doctor

Run the bambu-doctor subagent for full diagnostic coverage of the printer connection and config.

## Behavior

Delegate to the `bambu-doctor` subagent. Pass through any free-text problem description the user provided (if any) as the initial context.

The subagent will:

1. Verify the `bambu` CLI is installed.
2. Verify the required config keys are present **without** echoing secret values (`accessCode`, `ssh.password`).
3. Run `bambu doctor --json` for the structured diagnostic.
4. Run `bambu status --json` to capture current printer state.
5. Summarize findings and propose fix actions.
6. Never run destructive operations (cancel, ssh commands that modify state) without explicit user confirmation.

Surface the subagent's diagnostic report verbatim, with the verdict and next-step recommendations highlighted at the top.
