#!/usr/bin/env python3
"""Screenshot the share images after the site is built.

    node tools/serve-origin.mjs 4331 &      (or let this script start it)
    python3 tools/og_shots.py

Every page under site/dist/og/ and site/dist/zh/og/ is a 1200x630 card drawn with
the site's own components (site/src/components/OgCard.astro). This opens each one
in Chromium and writes the PNG next to it: og/<slug>.png for a case, og.png for the
home page, and the same under zh/. Pages link them as og:image, so run this after
every build and before deploying.

Needs Playwright for Python and its Chromium (python -m playwright install chromium).
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "site" / "dist"
PORT = 4331
BASE = f"http://localhost:{PORT}/casebook"


def pages() -> list[tuple[str, Path]]:
    """(url path under /casebook, output png) for every og page in the build."""
    out = []
    for prefix in ("", "zh/"):
        folder = DIST / prefix / "og"
        if (DIST / f"{prefix}og.html").exists():
            out.append((f"{prefix}og", DIST / prefix / "og.png"))
        for html in sorted(folder.glob("*.html")):
            out.append((f"{prefix}og/{html.stem}", folder / f"{html.stem}.png"))
    return out


def main() -> int:
    targets = pages()
    if not targets:
        print("og_shots: no og pages in site/dist; build first", file=sys.stderr)
        return 1
    server = subprocess.Popen(["node", str(ROOT / "tools" / "serve-origin.mjs"), str(PORT)], stdout=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE, timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
            for path, png in targets:
                page.goto(f"{BASE}/{path}", wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
            browser.close()
    finally:
        server.terminate()
    print(f"og_shots: wrote {len(targets)} images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
