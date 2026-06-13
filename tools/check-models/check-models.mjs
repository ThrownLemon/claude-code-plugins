#!/usr/bin/env node
// check-models — flag stale AI model ids and surface newer ones.
//
// Discovers every model id referenced across the repo, queries each provider's
// live /models endpoint, and reports which configured ids are still current,
// which are missing (verify), and which live models the repo doesn't use yet.
//
// Usage:
//   node tools/check-models/check-models.mjs [--provider zai|openai|google]
//                                            [--json] [--strict] [--root <dir>]
//
// Keys (only providers whose key is set are checked):
//   ZAI_API_KEY / ZHIPU_API_KEY / GLM_API_KEY
//   OPENAI_API_KEY
//   GEMINI_API_KEY / GOOGLE_API_KEY
//
// --strict exits non-zero if any configured id is absent from a live list.

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import { PROVIDERS, extractIds, diffModels } from "./lib.mjs";

const SCAN_EXTS = new Set([
  ".mjs", ".js", ".cjs", ".ts", ".py", ".sh", ".json", ".md", ".csv", ".toml", ".yaml", ".yml", ".txt",
]);
const SKIP_DIRS = new Set([".git", "node_modules"]);
const FETCH_TIMEOUT_MS = 15_000;

function parseArgs(argv) {
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (!t.startsWith("--")) continue;
    const key = t.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) flags[key] = true;
    else { flags[key] = next; i++; }
  }
  return flags;
}

function* walk(dir, root) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    const rel = path.relative(root, full);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      if (rel.startsWith(path.join("tools", "check-models"))) continue; // don't scan ourselves
      yield* walk(full, root);
    } else if (entry.isFile()) {
      if (/^AUDIT-.*\.md$/.test(entry.name)) continue; // one-off audit prose, not config
      if (SCAN_EXTS.has(path.extname(entry.name))) yield full;
    }
  }
}

function discoverConfigured(root) {
  const found = {};
  for (const name of Object.keys(PROVIDERS)) found[name] = new Set();
  for (const file of walk(root, root)) {
    let text;
    try { text = fs.readFileSync(file, "utf8"); } catch { continue; }
    for (const [name, provider] of Object.entries(PROVIDERS)) {
      for (const id of extractIds(text, provider.idPattern)) found[name].add(id);
    }
  }
  return found;
}

function findKey(provider) {
  for (const env of provider.keyEnv) {
    const v = process.env[env];
    if (v && v.trim()) return v.trim();
  }
  return null;
}

async function fetchLive(provider, key) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const url = provider.auth === "query" ? `${provider.modelsUrl}?key=${encodeURIComponent(key)}` : provider.modelsUrl;
    const headers = provider.auth === "bearer" ? { Authorization: `Bearer ${key}` } : {};
    const res = await fetch(url, { headers, signal: controller.signal });
    const body = await res.text();
    if (!res.ok) return { error: `HTTP ${res.status}: ${body.slice(0, 160)}` };
    return { models: provider.parse(JSON.parse(body)) };
  } catch (err) {
    return { error: err.name === "AbortError" ? `timed out after ${FETCH_TIMEOUT_MS}ms` : err.message };
  } finally {
    clearTimeout(timer);
  }
}

async function run() {
  const flags = parseArgs(process.argv.slice(2));
  const root = path.resolve(flags.root || process.cwd());
  const only = flags.provider;
  const configured = discoverConfigured(root);

  const report = {};
  let anyAbsent = false;

  for (const [name, provider] of Object.entries(PROVIDERS)) {
    if (only && only !== name) continue;
    const used = configured[name];
    const entry = { provider: provider.label, configured: [...used].sort() };
    const key = findKey(provider);
    if (!key) {
      entry.status = "skipped";
      entry.note = `no API key (set ${provider.keyEnv.join(" or ")})`;
      report[name] = entry;
      continue;
    }
    const live = await fetchLive(provider, key);
    if (live.error) {
      entry.status = "error";
      entry.note = live.error;
      report[name] = entry;
      continue;
    }
    const diff = diffModels(used, live.models);
    entry.status = "ok";
    Object.assign(entry, diff, { liveCount: live.models.length });
    if (diff.absent.length) anyAbsent = true;
    report[name] = entry;
  }

  if (flags.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    printHuman(report);
  }

  if (flags.strict && anyAbsent) process.exit(1);
}

function printHuman(report) {
  const C = process.stdout.isTTY
    ? { dim: "\x1b[2m", red: "\x1b[31m", grn: "\x1b[32m", yel: "\x1b[33m", cyn: "\x1b[36m", rst: "\x1b[0m", bld: "\x1b[1m" }
    : { dim: "", red: "", grn: "", yel: "", cyn: "", rst: "", bld: "" };
  console.log(`${C.bld}Model currency check${C.rst}\n`);
  for (const [name, e] of Object.entries(report)) {
    console.log(`${C.bld}${e.provider}${C.rst} ${C.dim}(${name})${C.rst}`);
    if (e.status === "skipped" || e.status === "error") {
      const sym = e.status === "skipped" ? `${C.dim}∅` : `${C.red}✗`;
      console.log(`  ${sym} ${e.status}: ${e.note}${C.rst}`);
      if (e.configured.length) console.log(`  ${C.dim}configured: ${e.configured.join(", ")}${C.rst}`);
      console.log("");
      continue;
    }
    for (const id of e.present) console.log(`  ${C.grn}✓${C.rst} ${id} ${C.dim}— in live list${C.rst}`);
    for (const id of e.aliases) console.log(`  ${C.cyn}↻${C.rst} ${id} ${C.dim}— rolling alias (always current)${C.rst}`);
    for (const id of e.shortforms ?? []) console.log(`  ${C.dim}↳ ${id} — friendly shortform of a live id${C.rst}`);
    for (const id of e.absent) console.log(`  ${C.yel}⚠${C.rst} ${id} ${C.yel}— NOT in live /models list — verify (may be a removed or unlisted model)${C.rst}`);
    if (e.newLive.length) {
      const shown = e.newLive.slice(0, 12);
      console.log(`  ${C.cyn}🆕 ${e.newLive.length} live model(s) not used in repo:${C.rst} ${C.dim}${shown.join(", ")}${e.newLive.length > shown.length ? ", …" : ""}${C.rst}`);
    }
    console.log("");
  }
  console.log(`${C.dim}✓ current · ↻ rolling alias · ⚠ verify · 🆕 candidate. Some valid models aren't in /models — ⚠ means "check", not "broken".${C.rst}`);
}

run().catch((err) => {
  console.error(`check-models failed: ${err.message}`);
  process.exit(2);
});
