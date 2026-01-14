#!/usr/bin/env python3
"""Git worktree management for fork-terminal plugin.

Provides functions to create, list, and remove git worktrees
for parallel Claude Code sessions.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class WorktreeInfo:
    """Information about a git worktree."""
    path: str
    branch: str
    commit: str
    is_main: bool = False
    is_locked: bool = False


def get_repo_root() -> str:
    """Get the root directory of the main git repository.

    Returns:
        Absolute path to the repository root.

    Raises:
        RuntimeError: If not in a git repository.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Not in a git repository")
    return result.stdout.strip()


def list_worktrees() -> List[WorktreeInfo]:
    """List all git worktrees for the current repository.

    Returns:
        List of WorktreeInfo objects for each worktree.
    """
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return []

    worktrees = []
    current_wt = {}

    for line in result.stdout.strip().split("\n"):
        if not line:
            if current_wt:
                worktrees.append(WorktreeInfo(
                    path=current_wt.get("worktree", ""),
                    branch=current_wt.get("branch", "").replace("refs/heads/", ""),
                    commit=current_wt.get("HEAD", "")[:7],
                    is_main=current_wt.get("bare", False) or not current_wt.get("branch"),
                    is_locked=current_wt.get("locked", False)
                ))
                current_wt = {}
            continue

        if line.startswith("worktree "):
            current_wt["worktree"] = line[9:]
        elif line.startswith("HEAD "):
            current_wt["HEAD"] = line[5:]
        elif line.startswith("branch "):
            current_wt["branch"] = line[7:]
        elif line == "bare":
            current_wt["bare"] = True
        elif line == "locked":
            current_wt["locked"] = True

    # Don't forget the last worktree
    if current_wt:
        worktrees.append(WorktreeInfo(
            path=current_wt.get("worktree", ""),
            branch=current_wt.get("branch", "").replace("refs/heads/", ""),
            commit=current_wt.get("HEAD", "")[:7],
            is_main=current_wt.get("bare", False) or "worktree" not in current_wt,
            is_locked=current_wt.get("locked", False)
        ))

    return worktrees


def sanitize_branch_name(task: str) -> str:
    """Convert a task description to a valid git branch name.

    Args:
        task: Task description text.

    Returns:
        Sanitized branch name.
    """
    # Lowercase and replace spaces with hyphens
    name = task.lower().strip()

    # Remove or replace invalid characters
    name = re.sub(r'[^a-z0-9\-_/]', '-', name)

    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)

    # Remove leading/trailing hyphens
    name = name.strip('-')

    # Truncate to reasonable length
    if len(name) > 50:
        name = name[:50].rsplit('-', 1)[0]

    # Add prefix if it doesn't have one
    if '/' not in name:
        name = f"worktree/{name}"

    return name


def get_sibling_path(branch_or_name: str) -> str:
    """Generate a sibling directory path for a new worktree.

    Worktrees are placed as siblings to the main repo directory.
    E.g., if main repo is /path/to/project, worktrees go to /path/to/project-<name>

    Args:
        branch_or_name: Branch name or worktree name.

    Returns:
        Absolute path for the new worktree.
    """
    repo_root = get_repo_root()
    repo_name = os.path.basename(repo_root)
    parent_dir = os.path.dirname(repo_root)

    # Extract a short name from the branch
    short_name = branch_or_name.replace("worktree/", "").replace("/", "-")

    # Create the sibling path
    worktree_path = os.path.join(parent_dir, f"{repo_name}-{short_name}")

    return worktree_path


def create_worktree(
    branch: str,
    path: Optional[str] = None,
    base: str = "HEAD",
    create_branch: bool = True
) -> str:
    """Create a new git worktree.

    Args:
        branch: Branch name for the worktree.
        path: Path for the worktree (default: auto-generate sibling path).
        base: Base commit/branch to start from.
        create_branch: Whether to create a new branch (True) or use existing.

    Returns:
        Path to the created worktree.

    Raises:
        RuntimeError: If worktree creation fails.
    """
    if path is None:
        path = get_sibling_path(branch)

    # Check if path already exists
    if os.path.exists(path):
        raise RuntimeError(f"Path already exists: {path}")

    # Build the command
    cmd = ["git", "worktree", "add"]

    if create_branch:
        # Create new branch from base
        cmd.extend(["-b", branch, path, base])
    else:
        # Use existing branch
        cmd.extend([path, branch])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Failed to create worktree: {error_msg}")

    return path


def remove_worktree(path: str, force: bool = False) -> bool:
    """Remove a git worktree.

    Args:
        path: Path to the worktree to remove.
        force: Force removal even with uncommitted changes.

    Returns:
        True if removal succeeded.

    Raises:
        RuntimeError: If removal fails.
    """
    # Resolve path if it's a branch name
    if not os.path.isabs(path) and not os.path.exists(path):
        # Try to find worktree by branch name
        worktrees = list_worktrees()
        for wt in worktrees:
            if wt.branch == path or wt.branch.endswith(f"/{path}"):
                path = wt.path
                break

    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(path)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Failed to remove worktree: {error_msg}")

    return True


def delete_branch(branch: str, force: bool = False) -> bool:
    """Delete a git branch.

    Args:
        branch: Branch name to delete.
        force: Force deletion even if not fully merged.

    Returns:
        True if deletion succeeded.
    """
    flag = "-D" if force else "-d"
    result = subprocess.run(
        ["git", "branch", flag, branch],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def worktree_exists(branch: str) -> Optional[str]:
    """Check if a worktree exists for the given branch.

    Args:
        branch: Branch name to check.

    Returns:
        Path to existing worktree, or None if not found.
    """
    worktrees = list_worktrees()
    for wt in worktrees:
        if wt.branch == branch or wt.branch.endswith(f"/{branch}"):
            return wt.path
    return None


def create_task_file(worktree_path: str, task: str, branch: str, worker_id: int = 1) -> str:
    """Create a TASK.md file in the worktree with context.

    Args:
        worktree_path: Path to the worktree.
        task: Task description.
        branch: Branch name.
        worker_id: Worker number for multi-worker scenarios.

    Returns:
        Path to the created TASK.md file.
    """
    from datetime import datetime

    task_content = f"""# Task Assignment

## Task
{task}

## Context
- **Branch**: `{branch}`
- **Worktree**: `{worktree_path}`
- **Worker ID**: {worker_id}
- **Created**: {datetime.now().isoformat()}

## Instructions
1. Read this file to understand your task
2. Work on the task described above
3. Commit your changes when complete
4. This is your isolated workspace - you won't conflict with other workers

## Getting Started
Run `git status` to see your current state, then begin implementing.
"""

    task_file = os.path.join(worktree_path, "TASK.md")
    with open(task_file, "w") as f:
        f.write(task_content)

    # Add to .gitignore if it exists
    gitignore_path = os.path.join(worktree_path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "a") as f:
            f.write("\n# Fork-terminal worktree task file\nTASK.md\n")

    return task_file


# CLI interface for direct script execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Git worktree manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List worktrees")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a worktree")
    create_parser.add_argument("--branch", "-b", required=True, help="Branch name")
    create_parser.add_argument("--base", default="HEAD", help="Base commit/branch")
    create_parser.add_argument("--path", help="Custom path (default: sibling)")
    create_parser.add_argument("--task", help="Task description for TASK.md")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a worktree")
    remove_parser.add_argument("path", help="Worktree path or branch name")
    remove_parser.add_argument("--force", "-f", action="store_true", help="Force removal")
    remove_parser.add_argument("--delete-branch", action="store_true", help="Also delete branch")

    args = parser.parse_args()

    try:
        if args.command == "list":
            worktrees = list_worktrees()
            if args.json:
                print(json.dumps([{
                    "path": wt.path,
                    "branch": wt.branch,
                    "commit": wt.commit,
                    "is_main": wt.is_main
                } for wt in worktrees], indent=2))
            else:
                print(f"{'PATH':<50} {'BRANCH':<30} {'COMMIT':<10}")
                print("-" * 90)
                for wt in worktrees:
                    main_marker = "(main)" if wt.is_main else ""
                    print(f"{wt.path:<50} {wt.branch:<30} {wt.commit:<10} {main_marker}")

        elif args.command == "create":
            path = create_worktree(
                branch=args.branch,
                path=args.path,
                base=args.base
            )
            if args.task:
                create_task_file(path, args.task, args.branch)
            print(f"Created worktree at: {path}")

        elif args.command == "remove":
            branch = None
            # Get branch before removing
            worktrees = list_worktrees()
            for wt in worktrees:
                if wt.path == args.path or wt.branch == args.path:
                    branch = wt.branch
                    break

            remove_worktree(args.path, force=args.force)
            print(f"Removed worktree: {args.path}")

            if args.delete_branch and branch:
                if delete_branch(branch, force=args.force):
                    print(f"Deleted branch: {branch}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
