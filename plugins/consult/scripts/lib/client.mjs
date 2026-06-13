// Minimal OpenAI-compatible chat completion client. No SDK dependency —
// uses global fetch (Node 18+).
//
// Streaming is mandatory here on purpose. The GLM-5.x models are reasoning
// models: they emit a long internal `reasoning_content` stream before any
// visible `content`. A non-streaming call therefore holds the socket open
// with no bytes for the entire reasoning phase, which routinely tripped the
// old fixed 120s wall-clock timeout on `review`/`stop` and surfaced to users
// as "it timed out / got cut off". Streaming lets us use an *idle* timeout
// (reset on every chunk) instead — a long-but-progressing answer is never
// killed, while a genuinely stalled connection still aborts.

// Idle timeout: max gap allowed BETWEEN chunks (not total wall time).
// Override with CONSULT_TIMEOUT_MS. Generous default because the first
// reasoning burst can take a while to arrive on large prompts.
const DEFAULT_IDLE_TIMEOUT_MS = 180_000;

export function resolveIdleTimeout(timeoutMs) {
  const envVal = Number(process.env.CONSULT_TIMEOUT_MS);
  if (Number.isFinite(envVal) && envVal > 0) return envVal;
  if (Number.isFinite(timeoutMs) && timeoutMs > 0) return timeoutMs;
  return DEFAULT_IDLE_TIMEOUT_MS;
}

// Hard wall-clock ceiling per attempt, on top of the idle timeout. The idle
// timeout stops a *stalled* stream; this stops a stream that drips one byte
// at a time forever. Override with CONSULT_TOTAL_TIMEOUT_MS.
const DEFAULT_TOTAL_TIMEOUT_MS = 600_000;

export function resolveTotalTimeout() {
  const envVal = Number(process.env.CONSULT_TOTAL_TIMEOUT_MS);
  if (Number.isFinite(envVal) && envVal > 0) return envVal;
  return DEFAULT_TOTAL_TIMEOUT_MS;
}

// Transient failures worth retrying before the stream starts. We never retry
// once content has begun arriving (the response is not idempotent mid-stream).
const RETRYABLE_STATUS = new Set([429, 500, 502, 503, 504]);
const MAX_RETRIES = 2; // 3 attempts total
const RETRY_BASE_MS = 600;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// An abort surfaces inconsistently across Node versions: AbortError,
// DOMException, or a TypeError carrying code ABORT_ERR. Treat the
// controller's own flag as the source of truth so a real stall is never
// misreported as a generic stream error.
function isAbort(err, controller) {
  return (
    controller.signal.aborted ||
    err?.name === "AbortError" ||
    err?.code === "ABORT_ERR"
  );
}

// Incremental Server-Sent-Events parser for OpenAI-compatible chat streams.
// Stateful so it can be fed arbitrary byte-chunk boundaries; `end()` flushes
// any trailing line the server left un-terminated. Kept as an exported unit
// so the parsing rules are testable without a live socket.
export class SSEParser {
  constructor() {
    this.buffer = "";
    this.content = "";
    this.reasoning = "";
    this.finishReason = null;
    this.usage = null;
  }

  push(text) {
    this.buffer += text;
    this.#drain();
  }

  // Flush: a server may close the stream without a trailing newline on the
  // final event. Append one so the last line is processed, then drain.
  end() {
    if (this.buffer.length > 0) {
      this.buffer += "\n";
      this.#drain();
    }
  }

  #drain() {
    let nl;
    while ((nl = this.buffer.indexOf("\n")) >= 0) {
      const line = this.buffer.slice(0, nl).trim();
      this.buffer = this.buffer.slice(nl + 1);
      this.#handleLine(line);
    }
  }

  #handleLine(line) {
    if (!line.startsWith("data:")) return;
    const data = line.slice(5).trim();
    if (!data || data === "[DONE]") return;

    let event;
    try {
      event = JSON.parse(data);
    } catch {
      return; // skip malformed/partial event line
    }
    const choice = event.choices?.[0];
    const delta = choice?.delta;
    if (delta?.content) this.content += delta.content;
    if (delta?.reasoning_content) this.reasoning += delta.reasoning_content;
    if (choice?.finish_reason) this.finishReason = choice.finish_reason;
    if (event.usage) this.usage = event.usage;
  }
}

export async function chat({ provider, apiKey, model, messages, maxTokens, temperature, timeoutMs }) {
  const idleMs = resolveIdleTimeout(timeoutMs);
  const totalMs = resolveTotalTimeout();

  // Clamp the output budget: at least 1, at most the model's real ceiling so
  // neither a zero/negative nor an over-eager --max-tokens can 400 the call.
  const requested = Math.max(1, maxTokens ?? 4096);
  const cap = provider.maxOutputTokens ?? Infinity;
  const resolvedMaxTokens = Math.min(requested, cap);

  const body = {
    model,
    messages,
    max_tokens: resolvedMaxTokens,
    stream: true,
    ...(provider.extraBody ?? {}),
  };
  if (typeof temperature === "number") body.temperature = temperature;
  const payload = JSON.stringify(body);

  let lastError;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    if (attempt > 0) await sleep(RETRY_BASE_MS * 2 ** (attempt - 1));

    const controller = new AbortController();
    let idleTimer = setTimeout(() => controller.abort(), idleMs);
    const totalTimer = setTimeout(() => controller.abort(), totalMs);
    const clearTimers = () => {
      clearTimeout(idleTimer);
      clearTimeout(totalTimer);
    };
    const resetIdle = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => controller.abort(), idleMs);
    };

    let response;
    try {
      response = await fetch(provider.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: payload,
        signal: controller.signal,
      });
    } catch (err) {
      clearTimers();
      if (isAbort(err, controller)) {
        throw new Error(`Request to ${provider.label} timed out (idle ${idleMs}ms / total ${totalMs}ms)`);
      }
      // Transient network blip — retry if attempts remain.
      lastError = new Error(`Network error contacting ${provider.label}: ${err.message}`);
      if (attempt < MAX_RETRIES) continue;
      throw lastError;
    }

    if (!response.ok) {
      clearTimers();
      const errText = await response.text().catch(() => "");
      if (RETRYABLE_STATUS.has(response.status) && attempt < MAX_RETRIES) {
        lastError = new Error(`${provider.label} returned ${response.status}: ${errText.slice(0, 200)}`);
        continue;
      }
      throw new Error(`${provider.label} returned ${response.status}: ${errText.slice(0, 500)}`);
    }

    const contentType = response.headers.get("content-type") || "";

    // Some providers/proxies ignore stream:true and return a single JSON body.
    // Fall back to non-streaming parsing rather than mis-parsing it as SSE.
    if (!contentType.includes("event-stream")) {
      clearTimers();
      const rawText = await response.text();
      return finalizeFromJson({ provider, model, rawText });
    }

    // Stream has started — past this point the response is NOT idempotent, so
    // we never retry; a mid-stream failure surfaces directly.
    const parser = new SSEParser();
    const decoder = new TextDecoder();
    try {
      for await (const part of response.body) {
        resetIdle();
        parser.push(decoder.decode(part, { stream: true }));
      }
      parser.push(decoder.decode()); // flush any buffered multibyte tail
      parser.end();
    } catch (err) {
      clearTimers();
      if (isAbort(err, controller)) {
        throw new Error(`Stream from ${provider.label} timed out (idle ${idleMs}ms / total ${totalMs}ms)`);
      }
      throw new Error(`Stream error from ${provider.label}: ${err.message}`);
    }
    clearTimers();

    return finalizeContent({
      provider,
      model,
      content: parser.content,
      reasoning: parser.reasoning,
      finishReason: parser.finishReason,
      usage: parser.usage,
    });
  }

  // Loop exhausted — every attempt hit a retryable failure.
  throw lastError ?? new Error(`${provider.label}: request failed after ${MAX_RETRIES + 1} attempts`);
}

// Build the result from accumulated content, turning the two reasoning-model
// failure modes into clear, actionable signals instead of a generic
// "no content" error or a silent truncation.
export function finalizeContent({ provider, model, content, reasoning, finishReason, usage }) {
  const truncated = finishReason === "length";
  const text = (content ?? "").trim();

  if (!text) {
    if (reasoning) {
      // The model spent its entire output budget on internal reasoning and
      // never reached a visible answer. This is THE cause of the reported
      // "capped / cut off" behaviour. Tell the caller exactly how to fix it.
      throw new Error(
        `${provider.label} produced ${reasoning.length} chars of internal reasoning but no answer ` +
          `(finish_reason=${finishReason}). The max-tokens budget was consumed by reasoning — ` +
          `raise it with --max-tokens (model ceiling ${provider.maxOutputTokens ?? "unknown"}).`,
      );
    }
    throw new Error(`${provider.label} returned no content (finish_reason=${finishReason ?? "unknown"}).`);
  }

  return {
    content: text,
    reasoning: reasoning || null,
    model,
    finishReason,
    usage,
    truncated,
  };
}

// Non-streaming fallback when a provider ignores stream:true.
function finalizeFromJson({ provider, model, rawText }) {
  let parsed;
  try {
    parsed = JSON.parse(rawText);
  } catch {
    throw new Error(`${provider.label} returned non-JSON response: ${rawText.slice(0, 200)}`);
  }
  const choice = parsed.choices?.[0];
  const message = choice?.message ?? {};
  const content = typeof message.content === "string" ? message.content : JSON.stringify(message.content ?? "");
  return finalizeContent({
    provider,
    model: parsed.model ?? model,
    content,
    reasoning: message.reasoning_content || "",
    finishReason: choice?.finish_reason ?? null,
    usage: parsed.usage ?? null,
  });
}
