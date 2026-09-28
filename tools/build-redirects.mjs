#!/usr/bin/env node
// Build the pages that keep the old github.io addresses working.
//
//   node tools/build-redirects.mjs [out]        default site/redirects
//
// The Casebook moved from metixai-official.github.io/awesome-metix-platform-use-cases
// to platform.metix.ai/casebook. GitHub Pages cannot send a 301, so every old address
// gets a tiny page with a canonical link, an instant meta refresh, and a plain link:
// search engines treat that pair as a redirect, and a reader without meta refresh
// still has somewhere to click. The pages are deployed to GitHub Pages in place of
// the site. Keep them for at least six months.

import { mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const out = process.argv[2] ?? join(ROOT, "site", "redirects");
const NEW = "https://platform.metix.ai/casebook";

const published = readdirSync(join(ROOT, "cases"), { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
  .map((d) => d.name)
  .filter((slug) => {
    const yaml = join(ROOT, "cases", slug, "case.yaml");
    return existsSync(yaml) && /^status:\s*published\s*$/m.test(readFileSync(yaml, "utf8"));
  });

const page = (target) => `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved to ${target}</title>
<link rel="canonical" href="${target}">
<meta http-equiv="refresh" content="0; url=${target}">
</head>
<body>
<p>The Casebook has moved to <a href="${target}">${target}</a>.</p>
</body>
</html>
`;

rmSync(out, { recursive: true, force: true });
const write = (path, target) => {
  const file = join(out, path, "index.html");
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, page(target));
};

write("", NEW);
write("zh", `${NEW}/zh`);
for (const slug of published) {
  write(`cases/${slug}`, `${NEW}/${slug}`);
  write(`zh/cases/${slug}`, `${NEW}/zh/${slug}`);
}
// Any other old address (a case removed later, a mistyped link) lands on the index.
writeFileSync(join(out, "404.html"), page(NEW));
writeFileSync(join(out, ".nojekyll"), "");
console.log(`build-redirects: ${2 + published.length * 2} pages in ${out}`);
