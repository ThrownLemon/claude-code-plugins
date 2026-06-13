#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Claude Code Read Tool Damage Control
=====================================

Blocks reads of zero-access files via PreToolUse hook on Read tool.
Loads zeroAccessPaths from patterns.yaml.

Exit codes:
  0 = Allow read
  2 = Block read (stderr fed back to Claude)
"""

import json
import sys
from pathlib import Path

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from path_utils import load_config, match_path


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name != "Read":
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Load config only after validating this is a Read tool call
    config = load_config()

    for zero_path in config.get("zeroAccessPaths", []):
        if match_path(file_path, zero_path):
            print(
                f"SECURITY: Blocked read of zero-access path {zero_path}: {file_path}",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
