#!/usr/bin/env node
/**
 * Fetch OpenAPI schema from running FastAPI and write a TypeScript declaration stub.
 * Usage: node scripts/generate-api-types.mjs [API_URL]
 */
import { writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const API = process.argv[2] ?? "http://127.0.0.1:8080";
const out = resolve(dirname(fileURLToPath(import.meta.url)), "../frontend/src/lib/api-schema.d.ts");

const res = await fetch(`${API}/openapi.json`);
if (!res.ok) {
  console.error(`Failed to fetch OpenAPI from ${API}: ${res.status}`);
  process.exit(1);
}

const schema = await res.json();
const paths = Object.keys(schema.paths ?? {}).sort();

const content = `/* Auto-generated from ${API}/openapi.json — do not edit by hand */
/* Run: node scripts/generate-api-types.mjs */

export type OpenApiPaths =
${paths.map((p) => `  | ${JSON.stringify(p)}`).join("\n")};

export interface OpenApiDocument {
  openapi: string;
  info: { title: string; version: string };
  paths: Record<string, unknown>;
}
`;

writeFileSync(out, content);
console.log(`Wrote ${out} (${paths.length} paths)`);
