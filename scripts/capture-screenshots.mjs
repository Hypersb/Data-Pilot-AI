/**
 * Capture README screenshots for Prisma AI v3.0.0-rc.1
 * Usage: node scripts/capture-screenshots.mjs [baseUrl] [apiUrl]
 */
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "docs", "assets");

const baseUrl = process.argv[2] ?? "http://localhost:3001";
const apiUrl = process.argv[3] ?? "http://127.0.0.1:8082";

async function shot(page, name, url, waitMs = 2500) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 120000 });
  await page.waitForTimeout(waitMs);
  await page.screenshot({ path: path.join(outDir, name), fullPage: false });
  console.log(`Saved ${name}`);
}

async function main() {
  await mkdir(outDir, { recursive: true });

  const sampleRes = await fetch(`${apiUrl}/api/samples/sales/load`, { method: "POST" });
  if (!sampleRes.ok) throw new Error(`Sample load failed: ${await sampleRes.text()}`);
  const { session_id: sessionId } = await sampleRes.json();
  console.log(`Session: ${sessionId}`);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  await shot(page, "landing.png", `${baseUrl}/`, 2000);
  await shot(page, "overview.png", `${baseUrl}/analyze/${sessionId}`, 12000);
  await shot(page, "forecast.png", `${baseUrl}/analyze/${sessionId}/forecast`, 25000);
  await shot(page, "chat.png", `${baseUrl}/analyze/${sessionId}/chat`, 6000);
  await shot(page, "report.png", `${baseUrl}/analyze/${sessionId}/report`, 8000);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
