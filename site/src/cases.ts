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

/** Order among cases published the same day: wide cards lead their rows so the three-column grid stays full. */
export const CARD_ORDER = [
  "ai-coding-tools-in-postings-2026",
  "inference-roles-us-metros-2026",
  "model-lifecycle-titles-2026",
  "forward-deployed-engineers-2026",
  "us-inference-pay-2026",
];

type Orderable = { data: { slug: string; format: string; published?: Date } };

/**
 * The one catalog order: newest first, then reports before cards, then CARD_ORDER. The
 * index's default sort, previous and next, and card numbers all follow it, so "Card 03"
 * is the third card wherever it appears.
 */
export function byCatalog(a: Orderable, b: Orderable): number {
  const rank = (slug: string) => (CARD_ORDER.includes(slug) ? CARD_ORDER.indexOf(slug) : CARD_ORDER.length);
  return (
    (b.data.published?.getTime() ?? 0) - (a.data.published?.getTime() ?? 0) ||
    Number(a.data.format === "card") - Number(b.data.format === "card") ||
    rank(a.data.slug) - rank(b.data.slug) ||
    a.data.slug.localeCompare(b.data.slug)
  );
}

/**
 * Color follows data: jobs blue, profiles violet, companies teal, several datasets navy.
 * Cards alternate the deep and light tone of their family by catalog position, so a card
 * looks the same on the catalog and on its own page.
 */
export function fieldColor(datasets: readonly string[], position = 0): string {
  if (datasets.length !== 1) return "navy";
  const family: Record<string, [string, string]> = {
    jobs: ["blue", "sky"],
    people: ["violet", "periwinkle"],
    companies: ["teal", "teal"],
  };
  return (family[datasets[0]] ?? ["navy", "navy"])[position % 2];
}

/** Dataset marks on light ground: the darker shade of each family, for 3:1 contrast. */
export const DATASET_INK: Record<string, string> = { jobs: "#1e79c2", people: "#5b54ef", companies: "#07545e" };

/** Search terms for each topic, in both languages, so "salary" or 薪资 finds the pay card. */
export const TOPIC_TERMS: Record<string, string> = {
  inference: "inference serving 推理",
  "ai-hiring": "ai hiring jobs postings 招聘 岗位",
  "forward-deployed": "forward deployed fde 前线部署",
  pay: "pay salary compensation wage 薪资 工资 薪酬 起薪",
  "ai-talent": "ai talent staff 人才 员工",
  education: "education degree university bachelor 教育 学历 本科 大学 院校",
  "model-lifecycle": "pre-training post-training lifecycle 预训练 后训练",
  "ai-tools": "ai tools coding assistant copilot 工具 编程助手",
  skills: "skills 技能",
  "coding-agents": "coding agents 编程",
};
