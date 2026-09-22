import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://metixai-official.github.io",
  base: "/awesome-metix-platform-use-cases",
  trailingSlash: "always",
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
  },
});
