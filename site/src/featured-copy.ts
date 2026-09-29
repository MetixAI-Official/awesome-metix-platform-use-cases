import type { Lang } from "@site/i18n";

/** Short preview copy; the underlying reports, numbers, and methodology stay intact. */
export const featuredCopy: Record<string, Record<Lang, { title: string; summary: string; note?: string; highlights?: string[] }>> = {
  "class-of-2023-ai-companies-2026": {
    en: {
      title: "AI’s share of new companies tripled after ChatGPT",
      summary: "2023-25 vs. 2019-22: nearly 3× by today’s AI definition; just 1.18× using older tags.",
      highlights: ["AI share in the 2023-25 cohort; 0.56% in 2019-22.", "Share ratio using older AI tags; 2.9× with the full definition.", "Of 2025 AI companies mention agents; 7% in 2021."],
    },
    zh: {
      title: "ChatGPT 后，新公司中 AI 公司占比翻三倍",
      summary: "2023-25 年对比 2019-22 年：按当前 AI 定义约为 3 倍，按旧标签仅为 1.18 倍。",
      highlights: ["2023-25 年新公司中的 AI 占比；2019-22 年为 0.56%。", "旧 AI 标签下的占比倍数；完整定义下为 2.9 倍。", "2025 年成立的 AI 公司提到 agent 的比例；2021 年为 7%。"],
    },
  },
  "ai-coding-tools-in-postings-2026": {
    en: { title: "Claude Code leads AI-tool mentions in job postings", summary: "Open postings naming Claude Code; 36,208 name any of the five tools.", note: "Hatched = another tool must be named too. Bars scaled to largest count." },
    zh: { title: "AI 编程工具招聘提及量，Claude Code 领先", summary: "个在招岗位提到 Claude Code；提到任一工具的共 36,208 个。", note: "斜线：须同时提到另一工具。条形按最大值缩放。" },
  },
  "inference-roles-us-metros-2026": {
    en: { title: "Nearly half of US inference openings are in the Bay Area", summary: "176 of 353 distinct US inference postings.", note: "Share of distinct postings · dashed line = 50%." },
    zh: { title: "美国推理岗位，近一半在湾区", summary: "353 个美国推理岗位中，176 个在湾区（已去重）。", note: "占全部去重岗位的比例 · 虚线为 50%。" },
  },
  "model-lifecycle-titles-2026": {
    en: { title: "Inference leads model-stage job titles", summary: "Job titles: 516 inference vs. 63 pre-training." },
    zh: { title: "模型阶段招聘，推理岗位领先", summary: "职位标题：推理 516 个，预训练 63 个。" },
  },
};
