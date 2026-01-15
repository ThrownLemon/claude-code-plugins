#!/usr/bin/env python3
"""
Aggregate findings from multiple AI reviewers.

Matches similar findings across CLIs and categorizes by agreement level.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from result_parser import parse_cli_output

# Pre-computed stop words set (created once, not per call)
_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "in", "on", "at", "to", "for", "of", "and", "or"
})


def get_output_dir() -> Path:
    """Get the output directory, expanding environment variables and tilde."""
    default = Path.home() / ".multi-ai-review"
    env_dir = os.environ.get("MULTI_REVIEW_OUTPUT_DIR", "")
    if env_dir:
        # Expand ~ and environment variables
        return Path(os.path.expanduser(os.path.expandvars(env_dir)))
    return default


def _tokenize_description(description: str) -> frozenset:
    """Tokenize a description, strip punctuation, and remove stop words.

    Returns a frozenset for efficient comparison operations.
    """
    if not description:
        return frozenset()
    # Strip punctuation from each word for better matching
    words = set(
        word.strip(".,;:!?\"'()[]{}")
        for word in description.lower().split()
    )
    # Remove empty strings that may result from stripping
    words.discard("")
    return frozenset(words - _STOP_WORDS)


def similarity_score(finding1: dict, finding2: dict,
                     tokens1: Optional[frozenset] = None, tokens2: Optional[frozenset] = None) -> float:
    """Calculate similarity between two findings.

    Args:
        finding1: First finding dict.
        finding2: Second finding dict.
        tokens1: Pre-computed tokens for finding1 (optional, for performance).
        tokens2: Pre-computed tokens for finding2 (optional, for performance).
    """
    score = 0.0

    # Same file is a strong indicator
    if finding1.get("file") and finding2.get("file"):
        if finding1["file"] == finding2["file"]:
            score += 0.4

            # Close line numbers (treat None/0 as missing)
            line1 = finding1.get("line")
            line2 = finding2.get("line")
            if line1 and line2:  # Both must be truthy (non-None, non-zero)
                line_diff = abs(line1 - line2)
                if line_diff == 0:
                    score += 0.3
                elif line_diff <= 5:
                    score += 0.2
                elif line_diff <= 10:
                    score += 0.1

    # Same category
    if finding1.get("category") == finding2.get("category"):
        score += 0.2

    # Same severity
    if finding1.get("severity") == finding2.get("severity"):
        score += 0.1

    # Description similarity (use pre-computed tokens if available)
    words1 = tokens1 if tokens1 is not None else _tokenize_description(finding1.get("description", ""))
    words2 = tokens2 if tokens2 is not None else _tokenize_description(finding2.get("description", ""))
    if words1 and words2:
        overlap = len(words1 & words2) / len(words1 | words2)
        score += overlap * 0.3

    return min(score, 1.0)


def find_matches(
    findings: dict[str, list[dict]],
    threshold: float = 0.5
) -> list[dict]:
    """Find matching findings across CLIs."""
    # Pre-compute tokenized descriptions for all findings (O(n) vs O(n^2))
    # Use (cli, index) tuple as stable cache key instead of id() which is fragile
    # Create shallow copies to avoid mutating input dicts
    token_cache: dict[tuple[str, int], frozenset] = {}
    findings_copy: dict[str, list[dict]] = {}
    for cli, cli_findings in findings.items():
        findings_copy[cli] = []
        for idx, f in enumerate(cli_findings):
            f_copy = f.copy()  # Shallow copy to avoid mutating caller's data
            f_copy["_matched"] = False
            f_copy["_cache_key"] = (cli, idx)  # Store stable key for later lookup
            findings_copy[cli].append(f_copy)
            token_cache[(cli, idx)] = _tokenize_description(f.get("description", ""))
    findings = findings_copy  # Use copies for the rest of the function

    matched_groups = []

    # Compare each pair of findings from different CLIs
    clis = list(findings.keys())
    for i, cli1 in enumerate(clis):
        for cli2 in clis[i + 1:]:
            for f1 in findings[cli1]:
                if f1.get("_matched"):
                    continue
                for f2 in findings[cli2]:
                    if f2.get("_matched"):
                        continue

                    # Pass pre-computed tokens to avoid re-tokenization
                    score = similarity_score(f1, f2, token_cache[f1["_cache_key"]], token_cache[f2["_cache_key"]])
                    if score >= threshold:
                        # Find or create a group
                        group_found = False
                        for group in matched_groups:
                            if f1 in group["findings"] or f2 in group["findings"]:
                                if f1 not in group["findings"]:
                                    group["findings"].append(f1)
                                    group["sources"].add(f1["source"])
                                if f2 not in group["findings"]:
                                    group["findings"].append(f2)
                                    group["sources"].add(f2["source"])
                                group_found = True
                                break

                        if not group_found:
                            matched_groups.append({
                                "findings": [f1, f2],
                                "sources": {f1["source"], f2["source"]}
                            })

                        f1["_matched"] = True
                        f2["_matched"] = True

    return matched_groups


def aggregate_findings(review_id: str) -> dict:
    """Aggregate findings from all CLIs for a review."""
    output_dir = get_output_dir() / review_id

    # Load metadata
    metadata_file = output_dir / "metadata.json"
    if not metadata_file.exists():
        raise ValueError(f"Review not found: {review_id}")

    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        raise ValueError(f"Could not load metadata for {review_id}: {e}")

    # Parse findings from each CLI
    findings: dict[str, list[dict]] = {}
    available_clis = metadata.get("available_clis", [])
    if not available_clis:
        raise ValueError(f"No CLIs found in review metadata for {review_id}")

    for cli in available_clis:
        output_file = output_dir / f"{cli}.json"
        findings[cli] = parse_cli_output(cli, output_file)

    # Find matches
    matched_groups = find_matches(findings)

    # Categorize by agreement level
    consensus = []  # All available CLIs agree
    majority = []   # 2+ CLIs agree
    unique = defaultdict(list)  # Only 1 found

    cli_count = len(findings)

    for group in matched_groups:
        source_count = len(group["sources"])

        # Create merged finding
        merged = {
            "id": group["findings"][0]["id"],
            "category": group["findings"][0]["category"],
            "severity": max(
                (f["severity"] for f in group["findings"]),
                key=lambda s: ["trivial", "minor", "major", "critical"].index(s)
            ),
            "file": group["findings"][0]["file"],
            "line": group["findings"][0]["line"],
            "sources": list(group["sources"]),
            "descriptions": {f["source"]: f["description"] for f in group["findings"]},
            "suggestions": {f["source"]: f["suggestion"] for f in group["findings"] if f.get("suggestion")}
        }

        if source_count >= cli_count and cli_count >= 3:
            consensus.append(merged)
        elif source_count >= 2:
            majority.append(merged)

    # Find unique (unmatched) findings
    for cli, cli_findings in findings.items():
        for f in cli_findings:
            if not f.get("_matched"):
                # Remove internal flags (_matched, _cache_key)
                clean_finding = {k: v for k, v in f.items() if not k.startswith("_")}
                unique[cli].append(clean_finding)

    # Sort by severity
    severity_order = {"critical": 0, "major": 1, "minor": 2, "trivial": 3}
    consensus.sort(key=lambda x: severity_order.get(x.get("severity", "trivial"), 3))
    majority.sort(key=lambda x: severity_order.get(x.get("severity", "trivial"), 3))

    return {
        "review_id": review_id,
        "metadata": metadata,
        "total_findings": sum(len(f) for f in findings.values()),
        "consensus": consensus,
        "majority": majority,
        "unique": dict(unique),
        "by_category": categorize_by_type(consensus + majority),
        "by_severity": categorize_by_severity(consensus + majority)
    }


def categorize_by_type(findings: list[dict]) -> dict[str, list[dict]]:
    """Group findings by category."""
    by_category: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_category[f.get("category", "other")].append(f)
    return dict(by_category)


def categorize_by_severity(findings: list[dict]) -> dict[str, list[dict]]:
    """Group findings by severity."""
    by_severity: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_severity[f.get("severity", "trivial")].append(f)
    return dict(by_severity)


def main():
    parser = argparse.ArgumentParser(description="Aggregate review findings")
    parser.add_argument("--review", "-r", required=True, help="Review ID")
    parser.add_argument("--output-format", choices=["json", "summary"], default="summary")

    args = parser.parse_args()

    try:
        results = aggregate_findings(args.review)

        if args.output_format == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"Review: {results['review_id']}")
            print(f"Total findings: {results['total_findings']}")
            print(f"Consensus (all agree): {len(results['consensus'])}")
            print(f"Majority (2+ agree): {len(results['majority'])}")
            print("Unique findings:")
            for cli, cli_findings in results['unique'].items():
                print(f"  {cli}: {len(cli_findings)}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
