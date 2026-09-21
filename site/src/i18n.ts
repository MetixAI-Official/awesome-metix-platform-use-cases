export type Lang = "en" | "zh";

export const LANGS: Lang[] = ["en", "zh"];
export const REPO = "https://github.com/MetixAI-Official/awesome-metix-platform-use-cases";

/** Product names that must not split across lines in a title. */
const UNBROKEN = /\b(?:Claude Code|GitHub Copilot|Model Context Protocol)\b/g;

/** A title with non-breaking spaces inside product names, for display only. */
export const keepNames = (text: string) => text.replace(UNBROKEN, (name) => name.replaceAll(" ", "\u00a0"));

const BASE = import.meta.env.BASE_URL.replace(/\/?$/, "/");

/** Site-relative link in a language. `path` is relative to the language root, e.g. "cases/x/". */
export function href(lang: Lang, path = ""): string {
  return BASE + (lang === "zh" ? "zh/" : "") + path.replace(/^\//, "");
}

export function asset(path: string): string {
  return BASE + path.replace(/^\//, "");
}

export function number(lang: Lang, value: number, digits = 0): string {
  return new Intl.NumberFormat(lang === "zh" ? "zh-CN" : "en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function longDate(lang: Lang, date: Date): string {
  if (lang === "zh") {
    return `${date.getUTCFullYear()} 年 ${date.getUTCMonth() + 1} 月 ${date.getUTCDate()} 日`;
  }
  return new Intl.DateTimeFormat("en-US", { dateStyle: "long", timeZone: "UTC" }).format(date);
}

export function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export const ui = {
  en: {
    htmlLang: "en",
    casebook: "Casebook",
    mastLede:
      "Job-market questions answered by an AI agent on the Metix AI Platform. Every number ships with its query, its cost in Credits, and the prompt that produced it.",
    mastCases: "published cases",
    mastCredits: "Credits to rerun them all",
    mastRun: "latest run",
    reportsLabel: "Reports",
    reportsNote: "Long reads, many charts, one question looked at from several sides.",
    cardsLabel: "Cards",
    cardsNote: "One question, one number, one chart. Each card is its own case with its own prompt.",
    formats: { card: "Card", report: "Report" },
    readReport: "Read the report",
    openCard: "Open the card",
    toRerun: "Credits to rerun",
    seePrompt: "See the prompt",
    makeEyebrow: "Your card",
    makeTitle: "Make your own card",
    makeSteps: ["Read before querying", "Population", "Count first", "Budget", "Audit", "Clean", "Group", "Outputs", "Chart", "Limits"],
    makeBody:
      "Copy the prompt template, change the question, and let your agent run it on your own key. Every card here started as a prompt like that.",
    makeCta: "Prompt template",
    resultsNote: (records: number) =>
      `Search results are IDs returned by searches, one per count query and one per match on a full search. Records are postings or profiles read in full: ${records === 0 ? "this case reads none" : `${records} here`}.`,
    siteName: "Metix AI Platform use cases",
    siteDescription:
      "Job-market reports made by an AI agent on the Metix AI Platform, each with its queries, its cost in Credits, and the prompt that produced it.",
    navCases: "Use cases",
    navGithub: "GitHub",
    navKey: "Get an API key",
    navKeyShort: "API key",
    langLabel: "Language",
    catalogTitle: "Job-market reports, each made by an agent on the Metix AI Platform",
    catalogLede:
      "Every report shows the queries behind its numbers, what they cost in Credits, and the prompt that produced it, so you can run it again on your own key and change it to fit your own question.",
    published: "Reports",
    comingNext: "Coming next",
    comingNextNote: "Working titles. A published report is titled with its finding.",
    read: "Read",
    types: { study: "Study", snapshot: "Snapshot", recipe: "Recipe", agent: "Agent session" },
    datasets: { people: "People", jobs: "Jobs", companies: "Companies" },
    integration: { rest: "REST", mcp: "MCP", skills: "Skills" },
    calls: "calls",
    records: "records",
    countsOnly: "counts only, no records read",
    creditsToRerun: "Credits to rerun",
    promptTitle: "Run it with your agent",
    copyPrompt: "Copy prompt",
    copy: "Copy",
    copied: "Copied",
    copyFailed: "Selected. Press Ctrl+C",
    methodTitle: "Method and limits",
    receiptTitle: "Receipt",
    receiptLede:
      "What the last replay of this case cost, read from the Platform's own balance before and after the run.",
    ranAt: "Ran at",
    callsLabel: "Calls",
    resultsLabel: "Search results",
    recordsLabel: "Records read",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `Before writing the replay, the agent spent about ${n} Credits exploring the question: audits, trial queries, and runs it replaced. You do not pay that again when you rerun it.`,
    rerun: "Rerun it",
    caseFolder: "Case folder on GitHub",
    pricing: "Credits and pricing",
    allCases: "All use cases",
    query: "Query",
    queries: "Queries",
    footerDocs: "Docs",
    footerKeys: "API keys",
    footerPolicy: "Public data policy",
    footerSource: "Source on GitHub",
    legal:
      "Copyright 2026 OpenJobs AI Inc. Metix AI Platform is a product of OpenJobs AI Inc. Code under Apache-2.0; text, charts, and data under CC BY 4.0.",
  },
  zh: {
    htmlLang: "zh-CN",
    casebook: "Casebook",
    mastLede:
      "由 AI agent 在 Metix AI Platform 上回答的就业市场问题。每个数字都附带它的查询、花了多少 Credits，以及生成它的提示词。",
    mastCases: "个已发布案例",
    mastCredits: "Credits 可全部重跑",
    mastRun: "最近一次运行",
    reportsLabel: "报告",
    reportsNote: "长篇，多张图，从几个角度看同一个问题。",
    cardsLabel: "卡片",
    cardsNote: "一个问题，一个数字，一张图。每张卡片都是独立的案例，有自己的提示词。",
    formats: { card: "卡片", report: "报告" },
    readReport: "阅读报告",
    openCard: "打开卡片",
    toRerun: "Credits 可重跑",
    seePrompt: "查看提示词",
    makeEyebrow: "你的卡片",
    makeTitle: "做一张你自己的卡片",
    makeSteps: ["先读规则再查询", "人群定义", "先计数", "预算", "抽检", "清洗", "分组", "输出", "图表", "局限"],
    makeBody: "复制提示词模板，换成你的问题，让你的 agent 用你自己的 key 去跑。这里的每张卡片都是这样开始的。",
    makeCta: "提示词模板",
    resultsNote: (records: number) =>
      `搜索结果是搜索返回的 ID 数，每次计数查询算一个，完整搜索按命中数算。记录是完整读取的岗位或档案：${records === 0 ? "这个案例一条都没读" : `这里读了 ${records} 条`}。`,
    siteName: "Metix AI Platform 用例",
    siteDescription:
      "由 AI agent 在 Metix AI Platform 上完成的就业市场报告，每份都附带查询、Credits 花费和生成它的提示词。",
    navCases: "用例",
    navGithub: "GitHub",
    navKey: "获取 API key",
    navKeyShort: "API key",
    langLabel: "语言",
    catalogTitle: "就业市场报告，每一份都由 agent 在 Metix AI Platform 上完成",
    catalogLede:
      "每份报告都公开数字背后的查询、花了多少 Credits，以及生成它的提示词。你可以用自己的 key 重跑，也可以改成你自己的问题。",
    published: "报告",
    comingNext: "即将发布",
    comingNextNote: "暂定标题。正式发布时标题会换成结论。",
    read: "阅读",
    types: { study: "研究", snapshot: "快照", recipe: "配方", agent: "Agent 会话" },
    datasets: { people: "人才", jobs: "岗位", companies: "公司" },
    integration: { rest: "REST", mcp: "MCP", skills: "Skills" },
    calls: "次调用",
    records: "条记录",
    countsOnly: "只计数，未读取记录",
    creditsToRerun: "Credits 可重跑",
    promptTitle: "交给你的 agent 来跑",
    copyPrompt: "复制提示词",
    copy: "复制",
    copied: "已复制",
    copyFailed: "已选中，请按 Ctrl+C",
    methodTitle: "方法与局限",
    receiptTitle: "账单",
    receiptLede: "最近一次重跑这个案例的花费，取自运行前后 Platform 自己记录的余额。",
    ranAt: "运行时间",
    callsLabel: "调用次数",
    resultsLabel: "搜索结果",
    recordsLabel: "读取记录",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `写出重跑脚本之前，agent 在探索这个问题上花了大约 ${n} Credits，包括抽检、试探性查询和被替换掉的运行。你重跑时不会再花这部分。`,
    rerun: "重跑",
    caseFolder: "GitHub 上的案例目录",
    pricing: "Credits 与价格",
    allCases: "全部用例",
    query: "查询",
    queries: "查询",
    footerDocs: "文档",
    footerKeys: "API keys",
    footerPolicy: "公开数据规范",
    footerSource: "GitHub 源码",
    legal:
      "Copyright 2026 OpenJobs AI Inc. Metix AI Platform 是 OpenJobs AI Inc. 的产品。代码采用 Apache-2.0，文字、图表和数据采用 CC BY 4.0。",
  },
} as const;

export type UI = (typeof ui)[Lang];
