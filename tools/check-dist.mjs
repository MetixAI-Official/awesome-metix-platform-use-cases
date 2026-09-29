#!/usr/bin/env node
// Fail a Casebook build that could reach the platform's login.
//
//   node tools/check-dist.mjs [site/dist]
//
// The Casebook is served from platform.metix.ai, the same origin as the console,
// whose login tokens sit in localStorage. Any script on a Casebook page could read
// them. This repository is public and takes outside pull requests, so the rules are
// checked on what the build produced, not on what a reviewer noticed:
//
//   - no inline <script> (JSON-LD excepted) and no inline event handlers: the pages
//     run under script-src 'self', and an inline script is also the easiest thing to
//     slip into a report;
//   - no script from another origin;
//   - in every script file: no document.cookie, no sessionStorage, no eval or
//     new Function, and localStorage only through getItem, setItem, or removeItem
//     on AGENT_KEY, the Casebook's one key.
//
// docs/style.md, "Same origin as the console", explains the rule to contributors.

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const dist = process.argv[2] ?? "site/dist";
const findings = [];
const walk = (dir) =>
  readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });

const lineOf = (text, index) => text.slice(0, index).split("\n").length;
const report = (file, text, index, rule) => findings.push(`${relative(dist, file)}:${lineOf(text, index)}: ${rule}`);

/** On a line that starts as a // comment. Minified bundles carry no comments. */
const inComment = (text, index) => /^\s*\/\//.test(text.slice(text.lastIndexOf("\n", index) + 1, index));

const SCRIPT = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
const HANDLER = /<[a-z][^>]*\s(on[a-z]+)\s*=/gi;
const JS_URL = /\s(?:href|src|action)\s*=\s*["']?\s*javascript:/gi;
const STORAGE_USE = /localStorage\s*\.\s*(getItem|setItem|removeItem)\s*\(\s*AGENT_KEY\b/g;

for (const file of walk(dist)) {
  // Every share card page needs its screenshot, or og:image is a 404
  // (tools/og_shots.py writes them into site/public).
  if (/(^|\/)og(\/[^/]+)?\.html$/.test(relative(dist, file)) && !existsSync(file.replace(/\.html$/, ".png"))) {
    findings.push(`${relative(dist, file)}: no ${relative(dist, file).replace(/\.html$/, ".png")}; run tools/og_shots.py`);
  }
  if (!/\.(html|js|mjs)$/.test(file)) continue;
  const text = readFileSync(file, "utf8");
  if (file.endsWith(".html")) {
    for (const m of text.matchAll(SCRIPT)) {
      const attrs = m[1];
      if (/type\s*=\s*["']?application\/ld\+json/i.test(attrs)) continue;
      const src = attrs.match(/\ssrc\s*=\s*["']?([^"'\s>]+)/i)?.[1];
      if (!src) report(file, text, m.index, "inline <script>; put it in a file");
      else if (/^(?:[a-z]+:)?\/\//i.test(src)) report(file, text, m.index, "script from another origin");
    }
    for (const m of text.matchAll(HANDLER)) report(file, text, m.index, `inline event handler ${m[1]}`);
    for (const m of text.matchAll(JS_URL)) report(file, text, m.index, "javascript: URL");
  } else if (file.endsWith(".js") || file.endsWith(".mjs")) {
    for (const [pattern, rule] of [
      [/document\s*\.\s*cookie/g, "document.cookie"],
      [/sessionStorage/g, "sessionStorage"],
      [/\beval\s*\(/g, "eval"],
      [/new\s+Function\s*\(/g, "new Function"],
    ]) {
      for (const m of text.matchAll(pattern)) if (!inComment(text, m.index)) report(file, text, m.index, rule);
    }
    const allowed = new Set([...text.matchAll(STORAGE_USE)].map((m) => m.index));
    for (const m of text.matchAll(/localStorage/g)) {
      if (!allowed.has(m.index) && !inComment(text, m.index)) report(file, text, m.index, "localStorage other than AGENT_KEY");
    }
    if (!/const AGENT_KEY = "casebook:[a-z-]+";/.test(text) && allowed.size > 0) {  // check-public: allow credential
      report(file, text, 0, "AGENT_KEY must be a casebook: key");
    }
  }
}

if (findings.length) {
  console.error(findings.join("\n"));
  console.error(`check-dist: ${findings.length} finding(s). See docs/style.md, "Same origin as the console".`);
  process.exit(1);
}
console.log(`check-dist: ${dist} clean`);
