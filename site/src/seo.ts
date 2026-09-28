/**
 * Structured data for Casebook pages.
 *
 * Every page names the same publisher as the rest of platform.metix.ai, the
 * Organization at https://www.metix.ai/#organization, so search engines read the
 * Casebook, the docs and the home page as one publisher's work. A case is an Article;
 * it is also a Dataset only when it publishes aggregate files under data/, and then
 * the Dataset lists those files, their licence and where to download them.
 */
import type { CollectionEntry } from "astro:content";
import { REPO, href, isoDate, ui, type Lang } from "@site/i18n";

export const ORGANIZATION = { "@id": "https://www.metix.ai/#organization" };
const RAW = "https://raw.githubusercontent.com/MetixAI-Official/awesome-metix-platform-use-cases/main";

/** Aggregate files per case, receipt.json aside: the files a Dataset can point at. */
const dataFiles: Record<string, string[]> = {};
for (const path of Object.keys(import.meta.glob("../../cases/*/data/*.json"))) {
  const [, slug, , file] = path.split("/cases/")[1].match(/^([^/]+)\/(data)\/(.+)$/) ?? [];
  if (!slug || file === "receipt.json") continue;
  (dataFiles[slug] ??= []).push(file);
}

const pageUrl = (site: URL, lang: Lang, path = "") => new URL(href(lang, path), site).href;

export function collectionJsonLd(site: URL, lang: Lang, cases: CollectionEntry<"cases">["data"][]) {
  const t = ui[lang];
  const url = pageUrl(site, lang);
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": `${url}#page`,
        url,
        name: `${t.casebook}: ${t.siteName}`,
        description: t.siteDescription,
        inLanguage: t.htmlLang,
        publisher: ORGANIZATION,
        isPartOf: { "@type": "WebSite", name: "Metix AI Platform", url: new URL("/", site).href },
        hasPart: cases.map((c) => ({ "@type": "Article", "@id": `${pageUrl(site, lang, c.slug)}#article`, headline: c.title[lang] })),
      },
      breadcrumbs(site, lang),
    ],
  };
}

export function caseJsonLd(site: URL, lang: Lang, data: CollectionEntry<"cases">["data"]) {
  const t = ui[lang];
  const url = pageUrl(site, lang, data.slug);
  const dates = {
    datePublished: data.published ? isoDate(data.published) : undefined,
    dateModified: data.snapshot ? isoDate(data.snapshot) : undefined,
  };
  const graph: Record<string, unknown>[] = [
    {
      "@type": "Article",
      "@id": `${url}#article`,
      url,
      headline: data.title[lang],
      description: data.dek[lang],
      inLanguage: t.htmlLang,
      ...dates,
      author: ORGANIZATION,
      publisher: ORGANIZATION,
      isPartOf: { "@id": `${pageUrl(site, lang)}#page` },
      license: "https://creativecommons.org/licenses/by/4.0/",
      keywords: data.topics.join(", "),
    },
    breadcrumbs(site, lang, data),
  ];
  const files = dataFiles[data.slug] ?? [];
  if (files.length > 0) {
    graph.push({
      "@type": "Dataset",
      "@id": `${url}#dataset`,
      name: data.title[lang],
      description: data.dek[lang],
      url,
      ...dates,
      creator: ORGANIZATION,
      publisher: ORGANIZATION,
      license: "https://creativecommons.org/licenses/by/4.0/",
      isAccessibleForFree: true,
      sameAs: `${REPO}/tree/main/cases/${data.slug}/data`,
      distribution: files.map((file) => ({
        "@type": "DataDownload",
        encodingFormat: "application/json",
        contentUrl: `${RAW}/cases/${data.slug}/data/${file}`,
      })),
    });
    (graph[0] as Record<string, unknown>).about = { "@id": `${url}#dataset` };
  }
  return { "@context": "https://schema.org", "@graph": graph };
}

function breadcrumbs(site: URL, lang: Lang, data?: CollectionEntry<"cases">["data"]) {
  const t = ui[lang];
  const items = [
    { name: "Metix AI Platform", item: new URL("/", site).href },
    { name: t.casebook, item: pageUrl(site, lang) },
    ...(data ? [{ name: data.title[lang], item: pageUrl(site, lang, data.slug) }] : []),
  ];
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map((entry, i) => ({ "@type": "ListItem", position: i + 1, ...entry })),
  };
}
