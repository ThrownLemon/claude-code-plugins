#!/usr/bin/env python3
"""Fork a new terminal window with a command.

Cross-platform terminal spawner for macOS and Windows.
Supports Terminal.app and Warp on macOS.
"""

import os
import platform
import shlex
import subprocess
import sys


def escape_applescript_string(s: str) -> str:
    """Properly escape a string for use in AppleScript double-quoted strings.

    This prevents AppleScript injection by escaping all special characters.
    """
    # Order matters: escape backslash first
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\r", "\\r")
    s = s.replace("\n", "\\n")
    s = s.replace("\t", "\\t")
    return s


def fork_terminal(command: str, terminal: str = None) -> str:
    """Open a new terminal window and run the specified command.

    Args:
        command: The command to execute in the new terminal window
        terminal: Terminal to use - "warp", "terminal", or auto-detect (default)

    Returns:
        Status message indicating success or failure
    """
    system = platform.system()
    cwd = os.getcwd()

    # Auto-detect terminal preference from env var, default to "warp" if installed
    if terminal is None:
        terminal = os.environ.get("FORK_TERMINAL", "auto")

    if terminal == "auto":
        # Check if Warp is installed
        warp_check = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to exists application process "Warp"'],
            capture_output=True, text=True
        )
        # Also check if Warp app exists
        warp_exists = os.path.exists("/Applications/Warp.app")
        terminal = "warp" if warp_exists else "terminal"

    if system == "Darwin":  # macOS
        safe_cwd = shlex.quote(cwd)
        shell_command = f"cd {safe_cwd} && {command}"

        if terminal == "warp":
            try:
                # Warp doesn't support command execution via URL scheme
                # Use AppleScript to open new tab and type command
                escaped_cmd = escape_applescript_string(shell_command)
                applescript = f'''
                    tell application "Warp" to activate
                    delay 0.5
                    tell application "System Events"
                        tell process "Warp"
                            keystroke "t" using command down
                            delay 0.5
                            keystroke "{escaped_cmd}"
                            delay 0.8
                            keystroke return
                        end tell
                    end tell
                '''
                result = subprocess.run(
                    ["osascript", "-e", applescript],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return "Warp terminal launched"
                else:
                    return f"Warp error: {result.stderr.strip()}"
            except (OSError, subprocess.SubprocessError) as e:
                return f"Error: {str(e)}"
        else:
            # Default: Terminal.app
            escaped_shell_command = escape_applescript_string(shell_command)
            try:
                result = subprocess.run(
                    ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_shell_command}"'],
                    capture_output=True,
                    text=True,
                )
                output = f"stdout: {result.stdout.strip()}\nstderr: {result.stderr.strip()}\nreturn_code: {result.returncode}"
                return output
            except (OSError, subprocess.SubprocessError) as e:
                return f"Error: {str(e)}"

    elif system == "Windows":
        # Escape double quotes and backslashes in path for Windows cmd
        safe_cwd = cwd.replace("\\", "\\\\").replace('"', '""')
        full_command = f'cd /d "{safe_cwd}" && {command}'
        try:
            # Don't use shell=True - pass command list directly
            subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", full_command])
            return "Windows terminal launched"
        except (OSError, subprocess.SubprocessError) as e:
            return f"Error: {str(e)}"

    else:  # Linux and others
        raise NotImplementedError(f"Platform {system} not supported. Linux support coming soon.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join arguments with space - the command should be passed as a single quoted arg
        # e.g., fork_terminal.py "echo 'hello world'"
        output = fork_terminal(" ".join(sys.argv[1:]))
        print(output)
    else:
        print("Usage: fork_terminal.py <command>")
        print("Example: fork_terminal.py 'claude --model opus'")
        print("")
        print("Environment variables:")
        print("  FORK_TERMINAL=warp|terminal|auto  (default: auto)")
        sys.exit(1)
