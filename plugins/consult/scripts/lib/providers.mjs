// Provider registry for the consult plugin.
// All providers expose an OpenAI-compatible /chat/completions endpoint so a
// single client function handles them. Add new providers by appending an entry.

export const PROVIDERS = {
  zai: {
    label: "Z.AI (GLM)",
    url: "https://api.z.ai/api/coding/paas/v4/chat/completions",
    keyEnv: ["ZAI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY"],
    defaultModel: "glm-4.6",
    models: ["glm-4.6", "glm-4.5", "glm-4.5-air"],
    docsUrl: "https://docs.z.ai/guides/llm/glm-4.6",
  },
  gemini: {
    label: "Google Gemini",
    url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    keyEnv: ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    defaultModel: "gemini-2.5-pro",
    models: ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
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
