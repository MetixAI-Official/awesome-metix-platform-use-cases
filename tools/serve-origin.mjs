#!/usr/bin/env node
// Serve site/dist the way the Casebook's host will, for local testing behind the
// platform's /casebook rewrite.
//
//   node tools/serve-origin.mjs [port]          default 4330
//   CASEBOOK_ORIGIN=http://localhost:4330 pnpm dev   in the platform's web app
//
// It follows Cloudflare's static-asset rule html_handling: "drop-trailing-slash":
// /casebook/x serves casebook/x.html, /casebook serves casebook/index.html, and a
// trailing slash is redirected away. The files are served under /casebook, which is
// where the host will put them.

import { createServer } from "node:http";
import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const DIST = fileURLToPath(new URL("../site/dist/", import.meta.url));
const BASE = "/casebook";
const port = Number(process.argv[2] ?? 4330);
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".woff2": "font/woff2",
};

const file = (path) => existsSync(path) && statSync(path).isFile() && path;

createServer((req, res) => {
  const { pathname } = new URL(req.url, "http://origin");
  if (pathname !== BASE && !pathname.startsWith(`${BASE}/`)) {
    res.writeHead(404).end("not found\n");
    return;
  }
  if (pathname.length > 1 && pathname.endsWith("/")) {
    res.writeHead(307, { location: pathname.replace(/\/+$/, "") }).end();
    return;
  }
  const rel = normalize(decodeURIComponent(pathname.slice(BASE.length))).replace(/^\/+/, "");
  if (rel.startsWith("..")) {
    res.writeHead(400).end();
    return;
  }
  const hit = rel === "" ? file(join(DIST, "index.html")) : file(join(DIST, rel)) || file(join(DIST, `${rel}.html`)) || file(join(DIST, rel, "index.html"));
  if (!hit) {
    res.writeHead(404, { "content-type": "text/plain" }).end("not found\n");
    return;
  }
  res.writeHead(200, {
    "content-type": TYPES[extname(hit)] ?? "application/octet-stream",
    "cache-control": "no-cache",
    // Headers a real host might add, to prove the platform does not pass them on.
    "x-origin": "casebook-local",
  });
  res.end(readFileSync(hit));
}).listen(port, () => console.log(`casebook origin on http://localhost:${port}${BASE}`));
