#!/usr/bin/env python3
"""
Parallel AI review runner.

Executes multiple AI CLIs in parallel and collects their output.
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from cli_configs import CLI_CONFIGS, build_review_command, get_model, get_install_instructions


def get_output_dir() -> Path:
    """Get or create the output directory."""
    default = Path.home() / ".multi-ai-review"
    env_dir = os.environ.get("MULTI_REVIEW_OUTPUT_DIR", "")
    if env_dir:
        output_dir = Path(os.path.expanduser(os.path.expandvars(env_dir)))
    else:
        output_dir = default
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_review_id() -> str:
    """Generate a unique review ID using UUID to prevent collisions."""
    # Use UUID4 for uniqueness, with timestamp prefix for human readability
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"review-{timestamp}-{unique_id}"


def check_cli_installed(cli: str) -> bool:
    """Check if a CLI is installed without using shell=True."""
    config = CLI_CONFIGS.get(cli)
    if not config:
        return False

    check_cmd = config["check_cmd"]
    # Parse the check command safely (e.g., "which claude" -> ["which", "claude"])
    cmd_parts = check_cmd.split()

    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def run_single_review(
    cli: str,
    prompt: str,
    project_root: str,
    output_file: Path,
    timeout: int
) -> dict:
    """Run a single CLI review."""
    result = {
        "cli": cli,
        "status": "pending",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": None,
        "output_file": str(output_file),
        "error": None
    }

    try:
        cmd = build_review_command(cli, prompt)
        result["command"] = " ".join(cmd)
        result["status"] = "running"

        # Run with timeout
        proc = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout * 60  # Convert to seconds
        )

        # Save output (avoid persisting the full prompt for security)
        output_data = {
            "cli": cli,
            "model": get_model(cli),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        result["status"] = "complete" if proc.returncode == 0 else "failed"
        result["end_time"] = datetime.now(timezone.utc).isoformat()

        if proc.returncode != 0:
            result["error"] = proc.stderr[:500] if proc.stderr else "Non-zero exit code"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = f"Review exceeded {timeout} minute timeout"
        result["end_time"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["end_time"] = datetime.now(timezone.utc).isoformat()

    return result


def run_parallel_reviews(
    clis: list[str],
    prompt: str,
    project_root: str,
    timeout: int = 10
) -> dict:
    """Run reviews with all CLIs in parallel."""
    review_id = generate_review_id()
    output_dir = get_output_dir() / review_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check which CLIs are available
    available_clis = []
    missing_clis = []
    for cli in clis:
        if check_cli_installed(cli):
            available_clis.append(cli)
        else:
            missing_clis.append(cli)

    if not available_clis:
        return {
            "success": False,
            "review_id": review_id,
            "error": f"No CLIs available. Missing: {', '.join(missing_clis)}",
            "results": [],
            "install_instructions": get_install_instructions()
        }

    # Save metadata (store prompt hash instead of full prompt for security)
    import hashlib
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

    metadata = {
        "review_id": review_id,
        "project_root": project_root,
        "prompt_hash": prompt_hash,
        "prompt_length": len(prompt),
        "requested_clis": clis,
        "available_clis": available_clis,
        "missing_clis": missing_clis,
        "timeout_minutes": timeout,
        "started": datetime.now(timezone.utc).isoformat()
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Run reviews in parallel
    results = []
    with ThreadPoolExecutor(max_workers=len(available_clis)) as executor:
        futures = {
            executor.submit(
                run_single_review,
                cli,
                prompt,
                project_root,
                output_dir / f"{cli}.json",
                timeout
            ): cli
            for cli in available_clis
        }

        for future in as_completed(futures):
            cli = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"{cli}: {result['status']}", file=sys.stderr)
            except Exception as e:
                results.append({
                    "cli": cli,
                    "status": "error",
                    "error": str(e)
                })

    # Update metadata with results
    metadata["completed"] = datetime.now(timezone.utc).isoformat()
    metadata["results"] = results

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Check if at least one CLI succeeded
    successful = [r for r in results if r["status"] == "complete"]
    if not successful:
        failed_clis = [r["cli"] for r in results]
        return {
            "success": False,
            "review_id": review_id,
            "output_dir": str(output_dir),
            "error": f"All CLIs failed: {', '.join(failed_clis)}. Check individual results for details.",
            "results": results,
            "missing_clis": missing_clis
        }

    return {
        "success": True,
        "review_id": review_id,
        "output_dir": str(output_dir),
        "results": results,
        "missing_clis": missing_clis
    }


def get_review_status(review_id: str) -> dict:
    """Get status of a review."""
    output_dir = get_output_dir() / review_id
    metadata_file = output_dir / "metadata.json"

    if not metadata_file.exists():
        return {"error": f"Review not found: {review_id}"}

    with open(metadata_file) as f:
        return json.load(f)


def list_reviews() -> list[dict]:
    """List all reviews."""
    output_dir = get_output_dir()
    reviews = []

    if not output_dir.exists():
        return reviews

    for review_dir in sorted(output_dir.iterdir(), reverse=True):
        if review_dir.is_dir() and review_dir.name.startswith("review-"):
            metadata_file = review_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        reviews.append({
                            "review_id": metadata.get("review_id"),
                            "started": metadata.get("started"),
                            "project_root": metadata.get("project_root"),
                            "clis": metadata.get("available_clis", [])
                        })
                except (IOError, json.JSONDecodeError):
                    pass  # Skip corrupted metadata files

    return reviews


def main():
    parser = argparse.ArgumentParser(description="Multi-AI review runner")
    subparsers = parser.add_subparsers(dest="command")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run parallel reviews")
    run_parser.add_argument("--clis", default="claude,gemini,codex")
    run_parser.add_argument("--prompt", required=True)
    run_parser.add_argument("--project-root", default=".")
    run_parser.add_argument("--timeout", type=int, default=10)
    run_parser.add_argument("--json", action="store_true")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check review status")
    status_parser.add_argument("--review", required=True)
    status_parser.add_argument("--json", action="store_true")

    # List command
    list_parser = subparsers.add_parser("list", help="List all reviews")
    list_parser.add_argument("--json", action="store_true")

    # Check command
    subparsers.add_parser("check", help="Check CLI availability")

    args = parser.parse_args()

    if args.command == "run":
        clis = [c.strip() for c in args.clis.split(",")]
        results = run_parallel_reviews(
            clis=clis,
            prompt=args.prompt,
            project_root=args.project_root,
            timeout=args.timeout
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if results.get("success"):
                print(f"Review complete: {results['review_id']}")
                print(f"Output: {results['output_dir']}")
            else:
                print(f"Review failed: {results.get('error', 'Unknown error')}")

            for r in results.get("results", []):
                print(f"  {r['cli']}: {r['status']}")

    elif args.command == "status":
        status = get_review_status(args.review)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            if "error" in status:
                print(f"Error: {status['error']}")
            else:
                print(f"Review: {status['review_id']}")
                print(f"Started: {status['started']}")
                for r in status.get("results", []):
                    print(f"  {r['cli']}: {r['status']}")

    elif args.command == "list":
        reviews = list_reviews()
        if args.json:
            print(json.dumps(reviews, indent=2))
        else:
            if not reviews:
                print("No reviews found.")
            else:
                for r in reviews[:10]:  # Show last 10
                    print(f"{r['review_id']} - {r['started']} ({', '.join(r['clis'])})")

    elif args.command == "check":
        print("CLI Availability Check:")
        for cli in CLI_CONFIGS:
            installed = check_cli_installed(cli)
            status = "installed" if installed else "MISSING"
            print(f"  {cli}: {status}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
