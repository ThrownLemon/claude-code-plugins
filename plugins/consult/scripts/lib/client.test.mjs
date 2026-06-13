// Unit tests for the streaming client's pure parsing/finalization logic.
// Zero dependencies — run with: node --test plugins/consult/scripts/lib/
import { test } from "node:test";
import assert from "node:assert/strict";

import { SSEParser, finalizeContent, resolveIdleTimeout, resolveTotalTimeout } from "./client.mjs";

const PROVIDER = { label: "Test", maxOutputTokens: 131072 };

function ev(obj) {
  return `data: ${JSON.stringify(obj)}\n`;
}

test("SSEParser accumulates content across multiple events in one chunk", () => {
  const p = new SSEParser();
  p.push(
    ev({ choices: [{ delta: { content: "Hello" } }] }) +
      ev({ choices: [{ delta: { content: " world" } }] }) +
      ev({ choices: [{ delta: {}, finish_reason: "stop" }] }) +
      "data: [DONE]\n",
  );
  p.end();
  assert.equal(p.content, "Hello world");
  assert.equal(p.finishReason, "stop");
});

test("SSEParser handles a line split across push() boundaries", () => {
  const p = new SSEParser();
  const line = ev({ choices: [{ delta: { content: "abc" } }] });
  const mid = Math.floor(line.length / 2);
  p.push(line.slice(0, mid));
  p.push(line.slice(mid));
  p.end();
  assert.equal(p.content, "abc");
});

test("SSEParser flushes a final event with no trailing newline", () => {
  const p = new SSEParser();
  // note: no "\n" — server closed mid-line
  p.push(`data: ${JSON.stringify({ choices: [{ delta: { content: "tail" }, finish_reason: "stop" }] })}`);
  assert.equal(p.content, ""); // not yet processed without newline
  p.end(); // flush
  assert.equal(p.content, "tail");
  assert.equal(p.finishReason, "stop");
});

test("SSEParser separates reasoning_content from content and captures usage", () => {
  const p = new SSEParser();
  p.push(
    ev({ choices: [{ delta: { reasoning_content: "thinking..." } }] }) +
      ev({ choices: [{ delta: { content: "answer" } }] }) +
      ev({ choices: [{ delta: {}, finish_reason: "stop" }], usage: { total_tokens: 42 } }),
  );
  p.end();
  assert.equal(p.reasoning, "thinking...");
  assert.equal(p.content, "answer");
  assert.deepEqual(p.usage, { total_tokens: 42 });
});

test("SSEParser ignores malformed JSON lines", () => {
  const p = new SSEParser();
  p.push("data: {not valid json}\n" + ev({ choices: [{ delta: { content: "ok" } }] }));
  p.end();
  assert.equal(p.content, "ok");
});

test("finalizeContent returns content and flags truncation on finish_reason=length", () => {
  const r = finalizeContent({
    provider: PROVIDER,
    model: "glm-5.2",
    content: "  partial answer  ",
    reasoning: "",
    finishReason: "length",
    usage: null,
  });
  assert.equal(r.content, "partial answer");
  assert.equal(r.truncated, true);
});

test("finalizeContent throws an actionable error when reasoning consumed the whole budget", () => {
  assert.throws(
    () =>
      finalizeContent({
        provider: PROVIDER,
        model: "glm-5.2",
        content: "",
        reasoning: "x".repeat(300),
        finishReason: "length",
        usage: null,
      }),
    /consumed by reasoning.*--max-tokens.*131072/s,
  );
});

test("finalizeContent throws a plain no-content error when nothing was produced", () => {
  assert.throws(
    () =>
      finalizeContent({
        provider: PROVIDER,
        model: "glm-5.2",
        content: "",
        reasoning: "",
        finishReason: "stop",
        usage: null,
      }),
    /returned no content/,
  );
});

test("resolveIdleTimeout: env > arg > default precedence", () => {
  const saved = process.env.CONSULT_TIMEOUT_MS;
  delete process.env.CONSULT_TIMEOUT_MS;
  assert.equal(resolveIdleTimeout(), 180_000); // default
  assert.equal(resolveIdleTimeout(5_000), 5_000); // arg
  process.env.CONSULT_TIMEOUT_MS = "9000";
  assert.equal(resolveIdleTimeout(5_000), 9_000); // env wins
  if (saved === undefined) delete process.env.CONSULT_TIMEOUT_MS;
  else process.env.CONSULT_TIMEOUT_MS = saved;
});

test("resolveTotalTimeout: env overrides default", () => {
  const saved = process.env.CONSULT_TOTAL_TIMEOUT_MS;
  delete process.env.CONSULT_TOTAL_TIMEOUT_MS;
  assert.equal(resolveTotalTimeout(), 600_000); // default
  process.env.CONSULT_TOTAL_TIMEOUT_MS = "120000";
  assert.equal(resolveTotalTimeout(), 120_000); // env wins
  process.env.CONSULT_TOTAL_TIMEOUT_MS = "-5";
  assert.equal(resolveTotalTimeout(), 600_000); // invalid ignored
  if (saved === undefined) delete process.env.CONSULT_TOTAL_TIMEOUT_MS;
  else process.env.CONSULT_TOTAL_TIMEOUT_MS = saved;
});
