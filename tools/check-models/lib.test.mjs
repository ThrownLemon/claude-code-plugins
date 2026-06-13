// Unit tests for the model-currency checker's pure logic. Zero deps.
// Run: node --test tools/check-models/lib.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";

import { PROVIDERS, isAlias, extractIds, diffModels, familyOf } from "./lib.mjs";

test("extractIds: zai pattern matches real glm ids, not prose", () => {
  const text = "default glm-5.2, list glm-5.1 glm-4.6; not a model: glm-foo or glmish";
  const ids = extractIds("x glm-5.2 y glm-5.1 z glm-4.6 glm-foo", PROVIDERS.zai.idPattern);
  assert.deepEqual([...ids].sort(), ["glm-4.6", "glm-5.1", "glm-5.2"]);
});

test("extractIds: google pattern excludes 'gemini-cli', keeps versioned + latest aliases", () => {
  const text = "use gemini-cli with gemini-pro-latest and gemini-3-pro-preview and veo-3.1-generate-preview";
  const ids = extractIds(text, PROVIDERS.google.idPattern);
  assert.ok(ids.has("gemini-pro-latest"));
  assert.ok(ids.has("gemini-3-pro-preview"));
  assert.ok(ids.has("veo-3.1-generate-preview"));
  assert.ok(!ids.has("gemini-cli"));
});

test("extractIds: openai matches gpt-image/sora/alias, not bare gpt-image", () => {
  const ids = extractIds("gpt-image-2 gpt-image-1.5 sora-2 chatgpt-image-latest gpt-image", PROVIDERS.openai.idPattern);
  assert.ok(ids.has("gpt-image-2"));
  assert.ok(ids.has("gpt-image-1.5"));
  assert.ok(ids.has("sora-2"));
  assert.ok(ids.has("chatgpt-image-latest"));
  assert.ok(!ids.has("gpt-image"));
});

test("isAlias: only -latest suffixes are rolling aliases", () => {
  assert.ok(isAlias("gemini-pro-latest"));
  assert.ok(isAlias("chatgpt-image-latest"));
  assert.ok(!isAlias("glm-5.2"));
  assert.ok(!isAlias("gpt-image-2"));
});

test("diffModels: classifies present / absent / aliases / newLive", () => {
  const configured = new Set(["glm-5.2", "glm-4.6", "gemini-pro-latest"]);
  const live = ["glm-4.6", "glm-5.1", "glm-6", "glm-5-turbo"];
  const { present, absent, aliases, newLive } = diffModels(configured, live);
  assert.deepEqual(present, ["glm-4.6"]); // in both
  assert.deepEqual(absent, ["glm-5.2"]); // configured but not listed live (and no live id extends it)
  assert.deepEqual(aliases, ["gemini-pro-latest"]); // rolling, separate
  assert.ok(newLive.includes("glm-6")); // newer model the repo doesn't use yet
  assert.ok(newLive.includes("glm-5.1"));
});

test("diffModels: friendly shortforms are not flagged as absent", () => {
  const configured = new Set(["veo-3.1", "gemini-3-pro", "gpt-image-1"]);
  const live = ["veo-3.1-generate-preview", "gemini-3-pro-preview", "gpt-image-1", "gpt-image-1.5"];
  const { present, absent, shortforms } = diffModels(configured, live);
  assert.ok(shortforms.includes("veo-3.1")); // shortform of veo-3.1-generate-preview
  assert.ok(shortforms.includes("gemini-3-pro")); // shortform of gemini-3-pro-preview
  assert.ok(present.includes("gpt-image-1")); // real model, present despite being a prefix of gpt-image-1.5
  assert.ok(!absent.includes("gpt-image-1")); // and NOT mis-flagged
  assert.deepEqual(absent, []); // nothing genuinely stale here
});

test("extractIds: drops version-placeholder ids like glm-5.x", () => {
  const ids = extractIds("glm-5.x are reasoning models; default glm-5.2", PROVIDERS.zai.idPattern);
  assert.ok(ids.has("glm-5.2"));
  assert.ok(!ids.has("glm-5.x"));
});

test("familyOf: strips version to group families", () => {
  assert.equal(familyOf("glm-5.2"), "glm");
  assert.equal(familyOf("gpt-image-2"), "gpt-image");
  assert.equal(familyOf("veo-3.1-generate-preview"), "veo");
  assert.equal(familyOf("gemini-3-pro-preview"), "gemini");
});
