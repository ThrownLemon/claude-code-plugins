// Provider registry for the consult plugin.
// All providers expose an OpenAI-compatible /chat/completions endpoint so a
// single client function handles them. Add new providers by appending an entry.

export const PROVIDERS = {
  zai: {
    label: "Z.AI (GLM)",
    url: "https://api.z.ai/api/coding/paas/v4/chat/completions",
    keyEnv: ["ZAI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY"],
    defaultModel: "glm-5.2",
    // glm-5.2 is the latest GLM Coding Plan flagship (2026-06-13, per
    // https://docs.z.ai/devpack/latest-model). It is served by the coding
    // endpoint below even though /models still lags (lists up to glm-5.1).
    // glm-5.x are reasoning models — they spend output tokens on internal
    // reasoning_content BEFORE producing visible content, so a small
    // max-tokens budget can be fully consumed by reasoning and yield empty
    // or truncated content. Always prefer high max-tokens budgets, and the
    // streaming client surfaces finish_reason=length truncation.
    models: ["glm-5.2", "glm-5.1", "glm-5-turbo", "glm-5", "glm-4.7", "glm-4.6", "glm-4.5", "glm-4.5-air"],
    // glm-5.x series: 1M-token context window, 128K (131072) max output.
    maxOutputTokens: 131072,
    // Enable the chain of thought for best results (max thinking). The raw
    // chat API exposes only thinking.type enabled|disabled — there is no
    // numeric reasoning budget (the /effort intensity mapping is a Claude
    // Code coding-plan feature, not available on the direct API). thinking
    // defaults to enabled, but we send it explicitly so a future default
    // flip cannot silently disable reasoning.
    extraBody: { thinking: { type: "enabled" } },
    docsUrl: "https://docs.z.ai",
  },
  gemini: {
    label: "Google Gemini",
    url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    keyEnv: ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    // gemini-flash-latest tracks Google's current top Flash model and has
    // much more generous free-tier limits than the Pro tier. Override per
    // call with `--model gemini-pro-latest` when you need the heavier model.
    defaultModel: "gemini-flash-latest",
    models: [
      "gemini-flash-latest",
      "gemini-pro-latest",
      "gemini-3.1-pro-preview",
      "gemini-3-pro-preview",
      "gemini-2.5-pro",
      "gemini-2.5-flash",
    ],
    docsUrl: "https://ai.google.dev/gemini-api/docs/openai",
  },
};

export function listProviders() {
  return Object.keys(PROVIDERS);
}

export function resolveProvider(name) {
  const provider = PROVIDERS[name];
  if (!provider) {
    const available = listProviders().join(", ");
    throw new Error(`Unknown provider "${name}". Available: ${available}`);
  }
  return provider;
}

export function findApiKey(provider) {
  for (const envName of provider.keyEnv) {
    const value = process.env[envName];
    if (value && value.trim()) return { key: value.trim(), envName };
  }
  return null;
}

export function describeKeyEnv(provider) {
  return provider.keyEnv.join(" or ");
}
