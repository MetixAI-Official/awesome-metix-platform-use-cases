#!/usr/bin/env node
// Copy the platform's top bar and footer, as data, into the Casebook.
//
//   node tools/sync-shell.mjs                       fetch from platform.metix.ai and write the snapshot
//   node tools/sync-shell.mjs --origin http://localhost:3217
//   node tools/sync-shell.mjs --check               exit 1 when the snapshot is stale
//
// The Casebook draws the same bar and footer as the rest of platform.metix.ai, from
// /brand/shell.json. The build reads the committed snapshot in site/src/shell/, never
// the network, so a platform outage cannot break a Casebook build; this script is how
// the snapshot is refreshed, and --check is how CI notices it has fallen behind.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SNAPSHOT = join(dirname(fileURLToPath(import.meta.url)), "..", "site", "src", "shell", "shell.json");
const args = process.argv.slice(2);
const check = args.includes("--check");
const at = args.indexOf("--origin");
const origin = (at === -1 ? "https://platform.metix.ai" : args[at + 1]).replace(/\/+$/, "");

const response = await fetch(`${origin}/brand/shell.json`, { headers: { accept: "application/json" } });
if (!response.ok) {
  console.error(`sync-shell: ${origin}/brand/shell.json answered ${response.status}`);
  process.exit(2);
}
const shell = await response.json();
if (shell.version !== 1 || !Array.isArray(shell.nav) || !shell.footer || !shell.tokens) {
  console.error(`sync-shell: unexpected shape (version ${shell.version}); update site/src/shell.ts first`);
  process.exit(2);
}
// The origin is where the copy came from, not part of the shell; keep it out so a
// snapshot taken from a local server matches one taken from production.
delete shell.origin;
const text = `${JSON.stringify(shell, null, 2)}\n`;

if (check) {
  let current = "";
  try {
    current = readFileSync(SNAPSHOT, "utf8");
  } catch {}
  if (current !== text) {
    console.error(`sync-shell: site/src/shell/shell.json differs from ${origin}; run node tools/sync-shell.mjs`);
    process.exit(1);
  }
  console.log("sync-shell: snapshot is current");
} else {
  mkdirSync(dirname(SNAPSHOT), { recursive: true });
  writeFileSync(SNAPSHOT, text);
  console.log(`sync-shell: wrote site/src/shell/shell.json from ${origin}`);
}
