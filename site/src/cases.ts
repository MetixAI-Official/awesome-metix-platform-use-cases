import type { AstroComponentFactory } from "astro/runtime/server/index.js";

export type Receipt = {
  ran_at: string;
  calls: number;
  results: number;
  records: number;
  credits: number;
  credits_source: string;
};

type MarkdownModule = { Content: AstroComponentFactory };

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
  en: bySlug(import.meta.glob<MarkdownModule>("../../cases/*/PROMPT.md", { eager: true })),
  zh: bySlug(import.meta.glob<MarkdownModule>("../../cases/*/PROMPT.zh.md", { eager: true })),
};
