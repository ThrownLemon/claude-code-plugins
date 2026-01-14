#!/usr/bin/env python3
"""Tournament review and combined branch creation.

Gathers solutions from tournament workers, compares them, and helps
create a combined branch with the best parts from each solution.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

from coordination import (
    get_tournament,
    update_tournament,
    check_tournament_completion
)


def gather_solutions(tournament_id: str) -> List[dict]:
    """Collect DONE.md summaries and git diffs from all workers.

    Args:
        tournament_id: Tournament ID.

    Returns:
        List of solution dicts:
        [
            {
                "worker_id": int,
                "cli": str,
                "branch": str,
                "path": str,
                "done_md": str,  # Contents of DONE.md
                "git_diff": str,  # Diff vs base
                "files_changed": [str],
                "commit_count": int
            },
            ...
        ]
    """
    tournament = get_tournament(tournament_id)
    if not tournament:
        raise ValueError(f"Tournament not found: {tournament_id}")

    solutions = []

    for worker in tournament.workers:
        solution = {
            "worker_id": worker.worker_id,
            "cli": worker.cli,
            "branch": worker.branch,
            "path": worker.path,
            "done_md": None,
            "git_diff": None,
            "files_changed": [],
            "commit_count": 0,
            "done": worker.done
        }

        # Read DONE.md if it exists
        done_path = os.path.join(worker.path, "DONE.md")
        if os.path.exists(done_path):
            with open(done_path, "r") as f:
                solution["done_md"] = f.read()

        # Get git diff from worktree
        try:
            # Change to worktree directory for git commands
            diff_result = subprocess.run(
                ["git", "diff", f"{tournament.base}...{worker.branch}", "--stat"],
                capture_output=True,
                text=True,
                cwd=worker.path
            )
            if diff_result.returncode == 0:
                solution["git_diff"] = diff_result.stdout

            # Get changed files
            files_result = subprocess.run(
                ["git", "diff", f"{tournament.base}...{worker.branch}", "--name-only"],
                capture_output=True,
                text=True,
                cwd=worker.path
            )
            if files_result.returncode == 0:
                solution["files_changed"] = [
                    f.strip() for f in files_result.stdout.strip().split("\n")
                    if f.strip()
                ]

            # Get commit count
            log_result = subprocess.run(
                ["git", "rev-list", "--count", f"{tournament.base}..{worker.branch}"],
                capture_output=True,
                text=True,
                cwd=worker.path
            )
            if log_result.returncode == 0:
                solution["commit_count"] = int(log_result.stdout.strip())

        except Exception as e:
            solution["error"] = str(e)

        solutions.append(solution)

    return solutions


def generate_review_report(tournament_id: str) -> dict:
    """Generate a structured report for AI review.

    Args:
        tournament_id: Tournament ID.

    Returns:
        Report dict with tournament info and solutions.
    """
    tournament = get_tournament(tournament_id)
    if not tournament:
        raise ValueError(f"Tournament not found: {tournament_id}")

    completion = check_tournament_completion(tournament_id)
    solutions = gather_solutions(tournament_id)

    report = {
        "tournament": {
            "id": tournament.id,
            "task": tournament.task,
            "base": tournament.base,
            "clis": tournament.clis,
            "status": tournament.status
        },
        "completion": completion,
        "solutions": solutions,
        "summary": {
            "total_workers": len(solutions),
            "completed_workers": sum(1 for s in solutions if s["done"]),
            "total_files_changed": sum(len(s["files_changed"]) for s in solutions),
            "total_commits": sum(s["commit_count"] for s in solutions)
        }
    }

    # Mark tournament as reviewing
    if completion["complete"]:
        update_tournament(tournament_id, {"status": "reviewing"})

    return report


def format_review_for_ai(report: dict) -> str:
    """Format the review report as a prompt for AI analysis.

    Args:
        report: Report from generate_review_report().

    Returns:
        Formatted string for AI review.
    """
    lines = [
        "# Tournament Review",
        "",
        f"## Task: {report['tournament']['task']}",
        "",
        f"Base branch: {report['tournament']['base']}",
        f"Competing CLIs: {', '.join(report['tournament']['clis'])}",
        "",
        "---",
        ""
    ]

    for solution in report["solutions"]:
        lines.extend([
            f"## Solution from {solution['cli'].upper()} (Worker {solution['worker_id']})",
            "",
            f"**Branch**: `{solution['branch']}`",
            f"**Commits**: {solution['commit_count']}",
            f"**Files changed**: {len(solution['files_changed'])}",
            ""
        ])

        if solution.get("done_md"):
            lines.extend([
                "### DONE.md Summary:",
                "```",
                solution["done_md"],
                "```",
                ""
            ])

        if solution.get("git_diff"):
            lines.extend([
                "### Git Diff Stats:",
                "```",
                solution["git_diff"],
                "```",
                ""
            ])

        if solution.get("files_changed"):
            lines.extend([
                "### Files Modified:",
            ])
            for f in solution["files_changed"]:
                lines.append(f"- `{f}`")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.extend([
        "## Review Questions",
        "",
        "1. Which solution has the best overall approach?",
        "2. What are the strengths of each solution?",
        "3. What parts from each solution should be combined?",
        "4. Are there any issues or concerns with any solution?",
        ""
    ])

    return "\n".join(lines)


def get_file_diff(tournament_id: str, worker_id: int, file_path: str) -> str:
    """Get the full diff for a specific file from a worker.

    Args:
        tournament_id: Tournament ID.
        worker_id: Worker ID.
        file_path: Path to the file.

    Returns:
        Full diff content for the file.
    """
    tournament = get_tournament(tournament_id)
    if not tournament:
        raise ValueError(f"Tournament not found: {tournament_id}")

    worker = None
    for w in tournament.workers:
        if w.worker_id == worker_id:
            worker = w
            break

    if not worker:
        raise ValueError(f"Worker not found: {worker_id}")

    result = subprocess.run(
        ["git", "diff", f"{tournament.base}...{worker.branch}", "--", file_path],
        capture_output=True,
        text=True,
        cwd=worker.path
    )

    return result.stdout


def create_combined_branch(
    tournament_id: str,
    branch_name: str = None,
    selections: dict = None
) -> str:
    """Create a combined branch from tournament solutions.

    This creates a new branch from the base and applies selected
    changes from each worker branch.

    Args:
        tournament_id: Tournament ID.
        branch_name: Name for combined branch (default: tournament/<task>-combined).
        selections: Dict mapping file paths to source CLI.
                   If None, creates empty branch for manual merge.

    Returns:
        Name of the created branch.
    """
    tournament = get_tournament(tournament_id)
    if not tournament:
        raise ValueError(f"Tournament not found: {tournament_id}")

    # Generate branch name
    if branch_name is None:
        from worktree_manager import sanitize_branch_name
        task_slug = sanitize_branch_name(tournament.task).replace("worktree/", "")
        branch_name = f"tournament/{task_slug}-combined"

    # Get the main repo root (not a worktree)
    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True
    ).stdout.strip()

    # Create the combined branch from base
    subprocess.run(
        ["git", "checkout", "-b", branch_name, tournament.base],
        cwd=repo_root,
        check=True
    )

    if selections:
        # Apply selected changes
        for file_path, source_cli in selections.items():
            # Find the worker for this CLI
            worker = None
            for w in tournament.workers:
                if w.cli == source_cli:
                    worker = w
                    break

            if worker:
                # Checkout this file from the worker's branch
                subprocess.run(
                    ["git", "checkout", worker.branch, "--", file_path],
                    cwd=repo_root,
                    check=True
                )

        # Commit the combined changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_root,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"Combined solution from tournament {tournament_id}"],
            cwd=repo_root,
            check=True
        )

    # Update tournament with combined branch
    update_tournament(tournament_id, {
        "combined_branch": branch_name,
        "status": "complete"
    })

    # Return to original branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_root
    )

    return branch_name


# CLI interface
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Tournament review tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Gather command
    gather_parser = subparsers.add_parser("gather", help="Gather solutions from workers")
    gather_parser.add_argument("--tournament", "-t", required=True, help="Tournament ID")
    gather_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate review report")
    report_parser.add_argument("--tournament", "-t", required=True, help="Tournament ID")
    report_parser.add_argument("--format", choices=["json", "markdown"], default="markdown")

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Get file diff from worker")
    diff_parser.add_argument("--tournament", "-t", required=True, help="Tournament ID")
    diff_parser.add_argument("--worker", "-w", type=int, required=True, help="Worker ID")
    diff_parser.add_argument("--file", "-f", required=True, help="File path")

    # Combine command
    combine_parser = subparsers.add_parser("combine", help="Create combined branch")
    combine_parser.add_argument("--tournament", "-t", required=True, help="Tournament ID")
    combine_parser.add_argument("--branch", "-b", help="Branch name (optional)")

    args = parser.parse_args()

    try:
        if args.command == "gather":
            solutions = gather_solutions(args.tournament)

            if args.json:
                print(json.dumps(solutions, indent=2))
            else:
                for s in solutions:
                    done_str = "DONE" if s["done"] else "pending"
                    print(f"\n{s['cli'].upper()} (Worker {s['worker_id']}): {done_str}")
                    print(f"  Branch: {s['branch']}")
                    print(f"  Commits: {s['commit_count']}")
                    print(f"  Files changed: {len(s['files_changed'])}")
                    if s["files_changed"]:
                        for f in s["files_changed"][:5]:
                            print(f"    - {f}")
                        if len(s["files_changed"]) > 5:
                            print(f"    ... and {len(s['files_changed']) - 5} more")

        elif args.command == "report":
            report = generate_review_report(args.tournament)

            if args.format == "json":
                print(json.dumps(report, indent=2))
            else:
                print(format_review_for_ai(report))

        elif args.command == "diff":
            diff = get_file_diff(args.tournament, args.worker, args.file)
            print(diff)

        elif args.command == "combine":
            branch = create_combined_branch(
                args.tournament,
                branch_name=args.branch
            )
            print(f"Created combined branch: {branch}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
