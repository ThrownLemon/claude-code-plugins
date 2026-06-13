// Pure, testable helpers for the model-currency checker. No IO here so the
// matching/diff logic can be unit-tested without a network or filesystem.

// Provider registry: each entry knows how to recognise its model ids in repo
// text, where its live /models list lives, and how to parse that list.
//
// idPattern requires a version-ish token (a digit, or a known rolling suffix)
// so we match real model ids like `glm-5.2` / `gemini-3-pro-preview` but NOT
// incidental words like `gemini-cli` or a `veo-generate.sh` filename.
export const PROVIDERS = {
  zai: {
    label: "Z.AI (GLM)",
    keyEnv: ["ZAI_API_KEY", "ZHIPU_API_KEY", "GLM_API_KEY"],
    modelsUrl: "https://api.z.ai/api/coding/paas/v4/models",
    auth: "bearer",
    idPattern: /\bglm-[0-9][a-z0-9.-]*\b/gi,
    parse: (json) => (json?.data ?? []).map((m) => m.id).filter(Boolean),
  },
  openai: {
    label: "OpenAI (image/video)",
    keyEnv: ["OPENAI_API_KEY"],
    modelsUrl: "https://api.openai.com/v1/models",
    auth: "bearer",
    idPattern: /\b(?:gpt-image-[0-9][a-z0-9.-]*|chatgpt-image-latest|sora-[0-9][a-z0-9.-]*)\b/gi,
    parse: (json) => (json?.data ?? []).map((m) => m.id).filter(Boolean),
  },
  google: {
    label: "Google (Gemini/Veo/Imagen)",
    keyEnv: ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    modelsUrl: "https://generativelanguage.googleapis.com/v1beta/models",
    auth: "query", // ?key=
    idPattern:
      /\b(?:gemini-(?:pro-latest|flash-latest|[0-9][a-z0-9.-]*)|veo-[0-9][a-z0-9.-]*|imagen-[0-9][a-z0-9.-]*)\b/gi,
    parse: (json) =>
      (json?.models ?? [])
        .map((m) => (m.name ?? "").replace(/^models\//, ""))
        .filter(Boolean),
  },
};

// Rolling aliases track "latest" on the provider side, so they are always
// current by definition and must never be flagged as stale.
export function isAlias(id) {
  return /(?:^|-)latest$/.test(id);
}

// Version-placeholder ids that appear in prose/comments, not real models:
// `glm-5.x`, `gemini-4.x`, a trailing `-x`, etc.
function isPlaceholder(id) {
  return /\.x(?:$|[-.])/.test(id) || /-x$/.test(id);
}

// Extract the set of model ids matching a provider's pattern from a blob of text.
export function extractIds(text, pattern) {
  const re = new RegExp(pattern.source, pattern.flags.includes("g") ? pattern.flags : pattern.flags + "g");
  const out = new Set();
  let m;
  while ((m = re.exec(text)) !== null) {
    const id = m[0].toLowerCase();
    if (!isPlaceholder(id)) out.add(id);
  }
  return out;
}

// Is `short` a friendly shortform of a real live id? (e.g. `veo-3.1` for
// `veo-3.1-generate-preview`, `gemini-3-pro` for `gemini-3-pro-preview`.)
// True only when a live id continues `short` with a `-`/`.` separator — which
// is why a real standalone model that is also a prefix (e.g. `gpt-image-1` vs
// `gpt-image-1.5`) is NOT caught here: it's present in the live list itself and
// never reaches this check.
function isShortformOf(short, liveSet) {
  for (const live of liveSet) {
    if (live !== short && live.startsWith(short) && /[-.]/.test(live[short.length] ?? "")) return true;
  }
  return false;
}

// Compare what the repo uses against the provider's live list.
//   present  – configured id found in the live list (✓ current)
//   absent   – configured id NOT in the live list (⚠ verify; some valid
//              models are not always listed, so this is a warning not a failure)
//   aliases  – rolling aliases (always current, reported separately)
//   newLive  – live ids the repo does not reference (🆕 candidates incl. newer models)
export function diffModels(configured, live) {
  const liveSet = new Set(live.map((s) => s.toLowerCase()));
  const present = [];
  const absent = [];
  const aliases = [];
  const shortforms = [];

  for (const id of [...configured].sort()) {
    if (isAlias(id)) aliases.push(id);
    else if (liveSet.has(id)) present.push(id);
    else if (isShortformOf(id, liveSet)) shortforms.push(id); // friendly alias of a real id
    else absent.push(id);
  }

  const configuredSet = new Set([...configured].map((s) => s.toLowerCase()));
  const newLive = live
    .map((s) => s.toLowerCase())
    .filter((id, i, arr) => arr.indexOf(id) === i)
    .filter((id) => !configuredSet.has(id))
    .sort();

  return { present, absent, aliases, shortforms, newLive };
}

// Group ids by family (everything up to the first version digit) so the report
// can hint "you use glm-5.2, the provider also offers glm-6".
export function familyOf(id) {
  const m = id.match(/^([a-z-]*?)-?[0-9]/i);
  return m ? m[1] : id;
}
