// Helpers that gather review context (git diff, file lists, etc.) so the
// review command can ship a self-contained prompt without manual paste.

import { execFileSync } from "node:child_process";
import fs from "node:fs";

const MAX_DIFF_BYTES = 200_000;

function runGit(args, cwd) {
  try {
    return execFileSync("git", args, {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      maxBuffer: 32 * 1024 * 1024,
    });
  } catch (err) {
    if (err.stderr) return { error: err.stderr.toString().trim() };
    return { error: err.message };
  }
}

export function isGitRepo(cwd) {
  const result = runGit(["rev-parse", "--is-inside-work-tree"], cwd);
  return typeof result === "string" && result.trim() === "true";
}

export function collectGitContext({ cwd, base }) {
  if (!isGitRepo(cwd)) {
    return { error: "Not a git repository — cannot collect diff." };
  }

  const branch = runGit(["rev-parse", "--abbrev-ref", "HEAD"], cwd);
  const head = runGit(["rev-parse", "--short", "HEAD"], cwd);
  const status = runGit(["status", "--short"], cwd);

  let resolvedBase = typeof base === "string" && base.trim() ? base.trim() : null;
  if (!resolvedBase) {
    for (const candidate of ["origin/main", "origin/master", "main", "master"]) {
      const out = runGit(["rev-parse", "--verify", candidate], cwd);
      if (typeof out === "string" && out.trim()) {
        resolvedBase = candidate;
        break;
      }
    }
  }

  let diff;
  let diffMode;
  if (resolvedBase) {
    const out = runGit(["diff", `${resolvedBase}...HEAD`], cwd);
    if (typeof out === "string" && out.trim()) {
      diff = out;
      diffMode = `branch (${resolvedBase}...HEAD)`;
    }
  }
  if (!diff) {
    const out = runGit(["diff", "HEAD"], cwd);
    if (typeof out === "string" && out.trim()) {
      diff = out;
      diffMode = "working tree (HEAD)";
    }
  }
  if (!diff) {
    const staged = runGit(["diff", "--staged"], cwd);
    if (typeof staged === "string" && staged.trim()) {
      diff = staged;
      diffMode = "staged";
    }
  }

  const truncated = diff && diff.length > MAX_DIFF_BYTES;
  if (truncated) diff = diff.slice(0, MAX_DIFF_BYTES);

  return {
    branch: typeof branch === "string" ? branch.trim() : null,
    head: typeof head === "string" ? head.trim() : null,
    status: typeof status === "string" ? status.trim() : "",
    base: resolvedBase,
    diffMode,
    diff: diff || "",
    truncated,
  };
}

export function readFileSafe(path, maxBytes = 80_000) {
  try {
    const stat = fs.statSync(path);
    if (!stat.isFile()) return null;
    const raw = fs.readFileSync(path, "utf8");
    if (raw.length > maxBytes) return raw.slice(0, maxBytes) + "\n[... truncated ...]";
    return raw;
  } catch {
    return null;
  }
}
