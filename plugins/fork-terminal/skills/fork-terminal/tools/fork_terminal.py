#!/usr/bin/env python3
"""Fork a new terminal window with a command.

Cross-platform terminal spawner for macOS and Windows.
"""

import os
import platform
import shlex
import subprocess
import sys


def fork_terminal(command: str) -> str:
    """Open a new Terminal window and run the specified command.

    Args:
        command: The command to execute in the new terminal window

    Returns:
        Status message indicating success or failure
    """
    system = platform.system()
    cwd = os.getcwd()

    if system == "Darwin":  # macOS
        # Use shlex.quote to safely escape the directory path
        safe_cwd = shlex.quote(cwd)
        shell_command = f"cd {safe_cwd} && {command}"
        # Escape for AppleScript: backslashes first, then quotes
        escaped_shell_command = shell_command.replace("\\", "\\\\").replace('"', '\\"')

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
        # Use shlex.join to properly handle arguments with spaces/quotes
        output = fork_terminal(shlex.join(sys.argv[1:]))
        print(output)
    else:
        print("Usage: fork_terminal.py <command>")
        print("Example: fork_terminal.py 'claude --model opus'")
        sys.exit(1)
