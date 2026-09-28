import { getCollection } from "astro:content";
import type { APIRoute } from "astro";
import { href, isoDate } from "@site/i18n";
import { receipts } from "@site/cases";

/**
 * The published cases as data, for the platform's pages that link here (the home
 * page's cases block, a dataset page's "see it used"). The platform reads this file
 * rather than keeping its own list.
 */
export const GET: APIRoute = async ({ site }) => {
  const cases = (await getCollection("cases", (c) => c.data.status === "published")).map(({ data }) => ({
    slug: data.slug,
    url: new URL(href("en", data.slug), site).href,
    urlZh: new URL(href("zh", data.slug), site).href,
    title: data.title,
    dek: data.dek,
    format: data.format,
    datasets: data.datasets,
    topics: data.topics,
    snapshot: data.snapshot ? isoDate(data.snapshot) : null,
    published: data.published ? isoDate(data.published) : null,
    reproduceApiCredits: receipts[data.slug]?.credits ?? null,
    highlight: data.highlights?.[0] ?? null,
  }));
  return new Response(`${JSON.stringify({ version: 1, cases }, null, 2)}\n`, {
    headers: { "content-type": "application/json; charset=utf-8" },
  });
};
