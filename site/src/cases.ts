import type { AstroComponentFactory } from "astro/runtime/server/index.js";

export type Receipt = {
  ran_at: string;
  calls: number;
  results: number;
  records: number;
  credits: number;
  credits_source: string;
};

/** A case's PROMPT.md: the fenced prompt comes from the source, the rest from the rendered HTML. */
export type PromptModule = {
  Content: AstroComponentFactory;
  rawContent: () => string;
  compiledContent: () => Promise<string>;
};

const slugOf = (path: string) => path.split("/cases/")[1].split("/")[0];

function bySlug<T>(modules: Record<string, T>): Record<string, T> {
  return Object.fromEntries(Object.entries(modules).map(([path, mod]) => [slugOf(path), mod]));
}

export const receipts = bySlug(
  import.meta.glob<Receipt>("../../cases/*/data/receipt.json", { eager: true, import: "default" }),
);

export const reports = bySlug(
  import.meta.glob<AstroComponentFactory>("../../cases/*/report/Report.astro", {
    eager: true,
    import: "default",
  }),
);

export const prompts = {
  en: bySlug(import.meta.glob<PromptModule>("../../cases/*/PROMPT.md", { eager: true })),
  zh: bySlug(import.meta.glob<PromptModule>("../../cases/*/PROMPT.zh.md", { eager: true })),
};

/** Catalog order for cards: wide cards lead their rows so the three-column grid stays full. */
export const CARD_ORDER = [
  "ai-coding-tools-in-postings-2026",
  "inference-roles-us-metros-2026",
  "model-lifecycle-titles-2026",
  "forward-deployed-engineers-2026",
  "us-inference-pay-2026",
];

export function byCardOrder(a: { data: { slug: string } }, b: { data: { slug: string } }): number {
  const rank = (slug: string) => (CARD_ORDER.includes(slug) ? CARD_ORDER.indexOf(slug) : CARD_ORDER.length);
  return rank(a.data.slug) - rank(b.data.slug) || a.data.slug.localeCompare(b.data.slug);
}
