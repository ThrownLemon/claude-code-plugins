// Minimal OpenAI-compatible chat completion client. No SDK dependency —
// uses global fetch (Node 18+).

const DEFAULT_TIMEOUT_MS = 120_000;

export async function chat({ provider, apiKey, model, messages, maxTokens, temperature, timeoutMs }) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs ?? DEFAULT_TIMEOUT_MS);

  const body = {
    model,
    messages,
    max_tokens: maxTokens ?? 4096,
  };
  if (typeof temperature === "number") body.temperature = temperature;

  let response;
  try {
    response = await fetch(provider.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      throw new Error(`Request to ${provider.label} timed out after ${timeoutMs ?? DEFAULT_TIMEOUT_MS}ms`);
    }
    throw new Error(`Network error contacting ${provider.label}: ${err.message}`);
  }
  clearTimeout(timeout);

  const rawText = await response.text();
  if (!response.ok) {
    throw new Error(`${provider.label} returned ${response.status}: ${rawText.slice(0, 500)}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(rawText);
  } catch {
    throw new Error(`${provider.label} returned non-JSON response: ${rawText.slice(0, 200)}`);
  }

  const choice = parsed.choices?.[0];
  const content = choice?.message?.content;
  if (!content) {
    throw new Error(`${provider.label} returned no content. Full response: ${rawText.slice(0, 500)}`);
  }

  return {
    content: typeof content === "string" ? content : JSON.stringify(content),
    model: parsed.model ?? model,
    finishReason: choice.finish_reason,
    usage: parsed.usage ?? null,
    raw: parsed,
  };
}
