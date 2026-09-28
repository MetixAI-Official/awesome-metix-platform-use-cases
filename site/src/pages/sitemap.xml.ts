import { getCollection } from "astro:content";
import type { APIRoute } from "astro";
import { LANGS, href, isoDate } from "@site/i18n";

/**
 * Every Casebook page in both editions, each entry listing its other edition, so a
 * search engine pairs them. The platform's robots.txt points here.
 */
export const GET: APIRoute = async ({ site }) => {
  const cases = (await getCollection("cases", (c) => c.data.status === "published")).map((c) => c.data);
  const latest = cases.map((c) => c.snapshot).filter((d): d is Date => Boolean(d)).sort((a, b) => +b - +a)[0];
  const pages = [{ path: "", modified: latest }, ...cases.map((c) => ({ path: c.slug, modified: c.snapshot }))];
  const url = (lang: (typeof LANGS)[number], path: string) => new URL(href(lang, path), site).href;
  const entries = pages.flatMap(({ path, modified }) =>
    LANGS.map(
      (lang) => `  <url>
    <loc>${url(lang, path)}</loc>${modified ? `\n    <lastmod>${isoDate(modified)}</lastmod>` : ""}
${LANGS.map((alt) => `    <xhtml:link rel="alternate" hreflang="${alt}" href="${url(alt, path)}"/>`).join("\n")}
    <xhtml:link rel="alternate" hreflang="x-default" href="${url("en", path)}"/>
  </url>`,
    ),
  );
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${entries.join("\n")}
</urlset>
`;
  return new Response(body, { headers: { "content-type": "application/xml; charset=utf-8" } });
};
