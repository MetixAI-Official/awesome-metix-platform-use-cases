import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";

// The Casebook is served at platform.metix.ai/casebook: the platform's Next
// server rewrites /casebook/* to wherever this build is hosted. No trailing
// slashes, and one .html file per page, because Next drops a trailing slash with
// a 308 and a static host that added one back would bounce the reader between
// the two forever. The host must serve /casebook/x from casebook/x.html and
// /casebook from casebook/index.html without redirecting.
export default defineConfig({
  site: "https://platform.metix.ai",
  base: "/casebook",
  trailingSlash: "never",
  build: { format: "file" },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "zh"],
    routing: { prefixDefaultLocale: false },
  },
  markdown: { syntaxHighlight: false, smartypants: false },
  vite: {
    resolve: {
      alias: { "@site": fileURLToPath(new URL("./src", import.meta.url)) },
    },
    // Case folders live next to the site, one level up.
    server: { fs: { allow: [".."] } },
    // Never inline a script: the page runs under script-src 'self', which allows
    // script files from this origin and nothing written into the HTML.
    build: { assetsInlineLimit: 0 },
  },
});
