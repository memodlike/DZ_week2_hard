// build/slides.html → submission/*.pdf и PNG-превью каждого слайда.
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = "file://" + path.join(root, "build", "slides.html");
const out = path.join(root, "submission");

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(html, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);

// Контроль вёрстки: ничего не должно выходить за пределы слайда.
const overflow = await page.evaluate(() =>
  [...document.querySelectorAll(".slide")].flatMap((s, i) => {
    const box = s.getBoundingClientRect();
    return [...s.children]
      .filter((el) => !el.closest(".house") && !el.classList.contains("cover") && el.getBoundingClientRect().bottom > box.bottom - 70 && !el.closest(".foot"))
      .slice(0, 1)
      .map((el) => `slide ${i + 1}: ${el.className || el.tagName}`);
  }),
);
if (overflow.length) console.warn("Возможное наложение на подвал:", overflow);

await page.pdf({ path: path.join(out, "RFM_Week2_Hard_bcc.pdf"), width: "1920px", height: "1080px", printBackground: true });

const slides = await page.$$(".slide");
for (const [i, s] of slides.entries()) {
  await s.screenshot({ path: path.join(out, `slide-${String(i + 1).padStart(2, "0")}.png`) });
}
await browser.close();
console.log(`PDF и ${slides.length} PNG в submission/`);
