#!/usr/bin/env node
// consult.mjs — entry point for the `consult` plugin.
//
// Subcommands:
//   ask     — single-shot prompt to a provider
//   review  — review current git diff against a provider
//   stop    — stop-hook review pass; reads transcript path from CLAUDE env
//   config  — show provider/key status
//
// Usage:
//   node consult.mjs ask --provider zai [--model glm-4.6] "prompt text"
//   echo "prompt" | node consult.mjs ask --provider gemini
//   node consult.mjs review --provider zai [--base origin/main] [--focus "..."]
//   node consult.mjs config

import process from "node:process";
import fs from "node:fs";
import path from "node:path";

import { chat } from "./lib/client.mjs";
import {
  PROVIDERS,
  describeKeyEnv,
  findApiKey,
  listProviders,
  resolveProvider,
} from "./lib/providers.mjs";
import { collectGitContext, readFileSafe } from "./lib/context.mjs";

function parseArgs(argv) {
  const args = { _: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token.startsWith("--")) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) {
        args.flags[key] = true;
      } else {
        args.flags[key] = next;
        i++;
      }
    } else {
      args._.push(token);
    }
  }
  return args;
}

function readStdinIfPiped() {
  if (process.stdin.isTTY) return "";
  const chunks = [];
  let chunk;
  try {
    while ((chunk = fs.readFileSync(0)) && chunk.length) {
      chunks.push(chunk);
      break;
    }
  } catch {
    return "";
  }
  return Buffer.concat(chunks).toString("utf8");
}

function printUsage() {
  console.log(`Usage:
  consult ask     --provider <name> [--model <id>] [--max-tokens N] "prompt"
  consult review  --provider <name> [--model <id>] [--base <ref>] [--focus "text"]
  consult stop    --provider <name> [--model <id>] [--transcript <path>]
  consult config

Providers: ${listProviders().join(", ")}
Env vars : ${Object.entries(PROVIDERS).map(([k, p]) => `${k}=${describeKeyEnv(p)}`).join("  ")}
`);
}

function buildReviewPrompt({ context, focus }) {
  const focusLine = focus ? `Reviewer focus: ${focus}\n\n` : "";
  const diffBlock = context.diff
    ? `Diff (${context.diffMode}${context.truncated ? ", TRUNCATED" : ""}):\n\n\`\`\`diff\n${context.diff}\n\`\`\``
    : "(no diff content — nothing changed vs base)";
  return `You are a senior code reviewer giving a SECOND OPINION. Another AI has already implemented these changes.
Be concrete and skeptical. Cite file paths and line numbers from the diff. Flag bugs, regressions,
security issues, missing tests, and contract changes. Skip nitpicks unless they hide a real issue.
End with a one-line verdict: SHIP IT, NEEDS WORK, or BLOCKER.

${focusLine}Branch: ${context.branch ?? "unknown"} @ ${context.head ?? "?"}
Base: ${context.base ?? "(no upstream)"}
Working-tree status:
${context.status || "(clean)"}

${diffBlock}`;
}

async function runProviderCall({ providerName, modelOverride, system, user, maxTokens, temperature }) {
  const provider = resolveProvider(providerName);
  const apiKeyHit = findApiKey(provider);
  if (!apiKeyHit) {
    throw new Error(
      `No API key in env for ${provider.label}. Set one of: ${describeKeyEnv(provider)}.`,
    );
  }
  const model = modelOverride || provider.defaultModel;
  const messages = [];
  if (system) messages.push({ role: "system", content: system });
  messages.push({ role: "user", content: user });

  return chat({
    provider,
    apiKey: apiKeyHit.key,
    model,
    messages,
    maxTokens,
    temperature,
  });
}

async function cmdAsk(args) {
  const providerName = args.flags.provider || args.flags.p;
  if (!providerName) throw new Error("--provider is required (e.g. --provider zai)");
  const modelOverride = args.flags.model || args.flags.m;
  const maxTokens = args.flags["max-tokens"] ? Number(args.flags["max-tokens"]) : 8192;
  const system = args.flags.system || null;

  const positional = args._.slice(1).join(" ").trim();
  const stdin = readStdinIfPiped().trim();
  const prompt = [positional, stdin].filter(Boolean).join("\n\n");
  if (!prompt) throw new Error("No prompt provided (positional arg or stdin).");

  const result = await runProviderCall({
    providerName,
    modelOverride,
    system,
    user: prompt,
    maxTokens,
  });

  console.log(result.content.trim());
  if (process.env.CONSULT_VERBOSE === "1" && result.usage) {
    console.error(`\n[model=${result.model} usage=${JSON.stringify(result.usage)}]`);
  }
}

async function cmdReview(args) {
  const providerName = args.flags.provider || args.flags.p;
  if (!providerName) throw new Error("--provider is required");
  const modelOverride = args.flags.model || args.flags.m;
  const base = args.flags.base || null;
  const focus = args.flags.focus || null;
  const cwd = args.flags.cwd || process.cwd();

  const context = collectGitContext({ cwd, base });
  if (context.error) throw new Error(context.error);

  const prompt = buildReviewPrompt({ context, focus });
  const result = await runProviderCall({
    providerName,
    modelOverride,
    system: null,
    user: prompt,
    maxTokens: 8192,
  });

  console.log(result.content.trim());
}

async function cmdStop(args) {
  const providerName = args.flags.provider || args.flags.p || "zai";
  const modelOverride = args.flags.model || args.flags.m;

  // Stop hooks receive a JSON payload on stdin (transcript_path, cwd,
  // session_id, etc.). When invoked manually via /consult:stop-gate, stdin
  // is empty — we degrade to plain-text mode so humans can read the result.
  let transcriptPath = args.flags.transcript || process.env.CLAUDE_TRANSCRIPT_PATH;
  let hookPayload = null;
  if (!process.stdin.isTTY) {
    const raw = readStdinIfPiped().trim();
    if (raw) {
      try {
        hookPayload = JSON.parse(raw);
        if (!transcriptPath) {
          transcriptPath = hookPayload.transcript_path || hookPayload.transcriptPath;
        }
      } catch {
        // not JSON — treat as plain context
      }
    }
  }
  const isHookInvocation = hookPayload !== null;

  const tail = transcriptPath ? readFileSafe(transcriptPath, 60_000) : null;
  const cwd = (hookPayload && hookPayload.cwd) || process.cwd();
  const context = collectGitContext({ cwd, base: null });

  const transcriptBlock = tail
    ? `Recent transcript (truncated):\n\n\`\`\`\n${tail}\n\`\`\``
    : "(no transcript available — review diff only)";
  const diffBlock = context.diff && !context.error
    ? `\n\nLatest diff (${context.diffMode}):\n\n\`\`\`diff\n${context.diff}\n\`\`\``
    : "";

  const user = `You are a stop-gate reviewer. The previous Claude turn just finished. Determine whether the
work is done correctly or whether issues remain. Be terse. List concrete problems (file:line) if any.
End with a single line: VERDICT: PASS | NEEDS FIXES.

${transcriptBlock}${diffBlock}`;

  const result = await runProviderCall({
    providerName,
    modelOverride,
    system: null,
    user,
    maxTokens: 4096,
  });

  const text = result.content.trim();
  const needsFixes = /VERDICT:\s*NEEDS FIXES/i.test(text);

  if (isHookInvocation) {
    // Structured decision protocol — Claude Code reads stdout as JSON and
    // surfaces `reason` back into the conversation when `decision === "block"`.
    if (needsFixes) {
      console.log(JSON.stringify({ decision: "block", reason: text }));
    }
    // PASS → emit nothing; exit 0 lets the Stop proceed.
    return;
  }

  // Manual invocation (e.g. /consult:stop-gate) — show human-readable output.
  console.log(text);
  if (needsFixes) process.exit(2);
}

function cmdConfig() {
  const lines = ["Consult plugin — provider status:\n"];
  for (const [name, provider] of Object.entries(PROVIDERS)) {
    const hit = findApiKey(provider);
    const status = hit ? `OK (via ${hit.envName})` : `missing — set ${describeKeyEnv(provider)}`;
    lines.push(`  ${name.padEnd(8)} ${provider.label.padEnd(20)} model=${provider.defaultModel.padEnd(18)} key=${status}`);
  }
  lines.push("\nDocs:");
  for (const [name, provider] of Object.entries(PROVIDERS)) {
    lines.push(`  ${name}: ${provider.docsUrl}`);
  }
  console.log(lines.join("\n"));
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv[0] === "-h" || argv[0] === "--help") {
    printUsage();
    return;
  }

  const command = argv[0];
  const args = parseArgs(argv);

  try {
    switch (command) {
      case "ask":
        await cmdAsk(args);
        break;
      case "review":
        await cmdReview(args);
        break;
      case "stop":
        await cmdStop(args);
        break;
      case "config":
        cmdConfig();
        break;
      default:
        printUsage();
        process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
