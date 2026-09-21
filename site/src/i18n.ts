export type Lang = "en" | "zh";

export const LANGS: Lang[] = ["en", "zh"];
export const REPO = "https://github.com/MetixAI-Official/awesome-metix-platform-use-cases";

/** Product names that must not split across lines in a title. */
const UNBROKEN = /\b(?:Claude Code|GitHub Copilot|Model Context Protocol)\b/g;

/** A title with non-breaking spaces inside product names, for display only. */
export const keepNames = (text: string) => text.replace(UNBROKEN, (name) => name.replaceAll(" ", "\u00a0"));

const CJK = /[\u3400-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]/;
const CLOSING = /^[，。、：；！？）」』》％…]/;
const OPENING = /[（「『《]$/;
/** Chinese words ICU segments wrongly in these titles; add a term when a title needs it. */
const PROTECTED = ["旧金山湾区", "湾区", "工程师", "编程", "薪资", "起薪", "预训练", "后训练", "写明", "本科", "中国大陆", "研究员", "个人档案", "前线部署"];
const escapeHtml = (text: string) =>
  text.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c] ?? c);

/**
 * A display title as HTML. Chinese has no spaces to break at, so the browser breaks
 * anywhere, splitting words such as 旧金山湾区. Here ICU word segmentation (Intl.Segmenter,
 * at build time) puts a <wbr> between words; with word-break: keep-all the browser breaks
 * only there and at spaces. Latin runs stay whole, closing punctuation stays with the word
 * before it, and opening punctuation with the word after.
 */
export function titleHtml(text: string, lang: Lang): string {
  const kept = keepNames(text);
  if (lang !== "zh") return escapeHtml(kept);
  const units: string[] = [];
  for (const { segment } of new Intl.Segmenter("zh", { granularity: "word" }).segment(kept)) {
    const prev = units[units.length - 1];
    const latin = !CJK.test(segment);
    if (prev !== undefined && ((latin && !CJK.test(prev.slice(-1))) || CLOSING.test(segment) || OPENING.test(prev))) {
      units[units.length - 1] = prev + segment;
    } else {
      units.push(segment);
    }
  }
  // ICU's dictionary splits some domain words (旧金山湾|区, 工程|师, 预|训练); never break inside these.
  let at = 0;
  const cuts = new Set(units.slice(0, -1).map((u) => (at += u.length)));
  for (const term of PROTECTED) {
    for (let i = kept.indexOf(term); i !== -1; i = kept.indexOf(term, i + 1)) {
      for (let c = i + 1; c < i + term.length; c += 1) cuts.delete(c);
    }
  }
  const pieces: string[] = [];
  let from = 0;
  for (const cut of [...cuts].sort((a, b) => a - b)) {
    pieces.push(kept.slice(from, cut));
    from = cut;
  }
  pieces.push(kept.slice(from));
  return pieces.map(escapeHtml).join("<wbr>");
}

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

/** Pay-as-you-go price on mira-api.metix.ai/docs/credits.md: $1 buys 30 Credits. */
export const CREDITS_PER_DOLLAR = 30;
/** New accounts get this many Credits once, valid for 30 days. */
export const FREE_CREDITS = 100;

export function dollars(lang: Lang, credits: number): string {
  const value = number(lang, credits / CREDITS_PER_DOLLAR, 2);
  return lang === "zh" ? `${value} 美元` : `$${value}`;
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
    toRerun: (n: string) => `${n} Credits to reproduce`,
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
    home: {
      lede:
        "Job-market questions answered by AI agents on the Metix AI Platform, a data API for professional profiles, job postings, and companies that agents reach through MCP, skills, or REST. Each case publishes the finding, the queries behind it, what it cost, and the prompt that produced it.",
      ctaStart: "Run your first case",
      ctaBrowse: "Browse all cases",
      statCases: "published cases",
      statCheapest: "Credits for the cheapest agent run",
      statFree: "free Credits for a new account",
      featured: "Featured",
      featuredNote: "The newest report and three cards. Every case is in the index below.",
      index: "All cases",
      indexNote: "Search by title, filter by format and data, sort by cost.",
      search: "Search cases",
      searchPlaceholder: "Search titles",
      format: "Format",
      formatAll: "All",
      data: "Data",
      sort: "Sort",
      sortNewest: "Newest",
      sortReproduce: "Cheapest to reproduce",
      sortAgent: "Cheapest in an agent",
      count: (n: number) => (n === 1 ? "1 case" : `${n} cases`),
      noResults: "No case matches these filters.",
      clear: "Clear filters",
      reproduceShort: (n: string) => `reproduce ${n}`,
      agentShort: (range: string) => `agent ${range}`,
      makeOwn: "Make your own case",
      makeOwnBody: "Start from the prompt template: change the question, keep the ten steps, run it on your key.",
    },
    caseNav: { prev: "Previous case", next: "Next case", all: "All cases" },
    run: {
      title: "Run it",
      lede: "Three ways in, from the cheapest to the fullest. Each says what it costs before you start.",
      pathsLabel: "How to run it",
      reproduce: "Reproduce the numbers",
      reproduceHint: "Counts only, no agent needed",
      agent: "Run it in your agent",
      agentHint: "The whole method, with its audits",
      adapt: "Adapt it",
      adaptHint: "Ask your own question",
      reproduceLede:
        "A short standard-library Python script sends the committed queries as counts and writes the aggregate files this page is built from. It needs Python and your key; your agent can run these lines for you as well.",
      reproduceGet:
        "data/*.json and data/receipt.json. Compare them with the committed files: the numbers should match, apart from what changed in the data since the snapshot.",
      agentLede:
        "Your agent follows the ten-step prompt: it reads the rules, counts, audits the definitions by reading records, and writes the files and the chart. Use an agent that can write files, such as Claude Code or Codex.",
      stepKey: "Get a key",
      keyBody: "Create one on the Metix AI Platform. New accounts get 100 Credits once, valid for 30 days. Set it in the shell you start your agent from:",
      createKey: "Create a key",
      stepConnect: "Connect your agent",
      stepCheck: "Check the setup",
      checkBody: "Ask this first. It reads your balance and the field list, runs no search, and costs nothing:",
      checkPrompt:
        "Use the Metix AI Platform: call metix_get_key_status and metix_get_contract, then tell me my Credit balance and which datasets I can query. Do not run any search.",
      stepPrompt: "Paste the prompt",
      agentGet:
        "The aggregate files and the chart, a note on what the audits found and what they changed, and the Credits the run spent, read from the balance before and after.",
      getLabel: "What you get",
      adaptLede:
        "The prompt is the case. Change the parts in this table and your agent answers your question instead, with the same checks and the same way of reporting cost.",
      emptyBalance: "A call that returns 402 insufficient_quota means the key works and the balance is empty.",
    },
    cost: {
      title: "What it costs",
      reproduce: "Reproduce",
      agent: "Agent run",
      credits: (lo: number, hi: number = lo) => (lo === hi ? `${lo} Credits` : `${lo} to ${hi} Credits`),
      capNote: (n: number) => `The prompt stops and asks before ${n} Credits.`,
      free: "Fits in the 100 free Credits",
      notFree: "More than the 100 free Credits",
      unitNote: "1 Credit buys 25 search results or 5 full records; $1 buys 30 Credits.",
    },
    setup: {
      label: "Your agent",
      claude: "Claude Code",
      codex: "Codex",
      skills: "Skills",
      other: "Other MCP clients",
      claudeNote: "Registers the Platform for every project. Start claude in any folder and the ten metix tools are there.",
      codexNote: "Registers the same server. The key stays in your environment instead of the config file.",
      skillsNote: "Four skills that teach any agent the Platform's endpoints and query rules. They work with or without MCP; Codex reads them too.",
      otherNote: "Point the client at this endpoint over streamable HTTP, with your key as a Bearer token. Older clients use /sse on the same host.",
      docs: "MCP setup guide",
    },
    start: {
      title: "Run your first case",
      lede: "Three steps, a few minutes, and a new account's free Credits cover every card.",
      pick: "Pick a case",
      pickBody: "Every case below says what reproducing it and running it in your agent cost. Open one and use its Run it section.",
      cheapest: (n: number) => `The cheapest runs in your agent for ${n} Credits.`,
    },
    promptTitle: "Run it with your agent",
    copyPrompt: "Copy prompt",
    expandAll: "Expand all",
    collapseAll: "Collapse all",
    questionLabel: "The question",
    stepsLabel: (n: number) => `${n} steps`,
    makeItYours: "Make it yours",
    methodLede: "How the population was defined, counted, and checked, and what the numbers cannot show. Limits starts open.",
    copy: "Copy",
    copied: "Copied",
    copyFailed: "Could not copy. The text is selected below: press Ctrl+C",
    methodTitle: "Method and limits",
    receiptTitle: "The last replay",
    receiptLede:
      "What reproducing this case cost the last time the script ran, read from the Platform's own balance before and after.",
    ranAt: "Ran at",
    callsLabel: "Calls",
    resultsLabel: "Search results",
    recordsLabel: "Records read",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `Making this case cost about ${n} Credits more: the agent's audits, trial queries, and runs it replaced before the replay existed. You do not pay that again.`,
    rerun: "Reproduce it",
    caseFolder: "Case folder on GitHub",
    pricing: "Credits and pricing",
    allCases: "All cases",
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
    toRerun: (n: string) => `重跑需 ${n} Credits`,
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
    home: {
      lede: "由 AI agent 在 Metix AI Platform 上回答的就业市场问题。Metix AI Platform 是职业档案、招聘岗位和公司的数据 API，agent 可以通过 MCP、skills 或 REST 访问。每个案例都公开结论、背后的查询、花了多少，以及生成它的提示词。",
      ctaStart: "跑你的第一个案例",
      ctaBrowse: "浏览全部案例",
      statCases: "个已发布案例",
      statCheapest: "Credits，交给 agent 跑最便宜的一个",
      statFree: "Credits，新账户一次性赠送",
      featured: "精选",
      featuredNote: "最新的一份报告和三张卡片。全部案例都在下面的索引里。",
      index: "全部案例",
      indexNote: "按标题搜索，按形式和数据筛选，按花费排序。",
      search: "搜索案例",
      searchPlaceholder: "搜索标题",
      format: "形式",
      formatAll: "全部",
      data: "数据",
      sort: "排序",
      sortNewest: "最新",
      sortReproduce: "复现最便宜",
      sortAgent: "交给 agent 最便宜",
      count: (n: number) => `${n} 个案例`,
      noResults: "没有符合这些筛选条件的案例。",
      clear: "清除筛选",
      reproduceShort: (n: string) => `复现 ${n}`,
      agentShort: (range: string) => `agent ${range}`,
      makeOwn: "做你自己的案例",
      makeOwnBody: "从提示词模板开始：换成你的问题，保留十个步骤，用你自己的 key 运行。",
    },
    caseNav: { prev: "上一个案例", next: "下一个案例", all: "全部案例" },
    run: {
      title: "运行这个案例",
      lede: "三种方式，从最省到最完整。每一种都先告诉你要花多少。",
      pathsLabel: "运行方式",
      reproduce: "复现数字",
      reproduceHint: "只计数，不需要 agent",
      agent: "交给你的 agent 来跑",
      agentHint: "完整方法，包括抽检",
      adapt: "改成你的问题",
      adaptHint: "问你自己的问题",
      reproduceLede:
        "一个只用 Python 标准库的小脚本，把已提交的查询按计数发出去，写出这个页面所用的聚合文件。只需要 Python 和你的 key，也可以让你的 agent 替你运行这几行。",
      reproduceGet: "data/*.json 和 data/receipt.json。和已提交的文件对比：除去快照之后数据本身的变化，数字应该一致。",
      agentLede:
        "你的 agent 按十步提示词执行：先读规则，再计数，读取记录来抽检定义，最后写出文件和图表。请使用能写文件的 agent，比如 Claude Code 或 Codex。",
      stepKey: "获取 key",
      keyBody: "在 Metix AI Platform 上创建。新账户一次性赠送 100 Credits，30 天内有效。在启动 agent 的终端里设置：",
      createKey: "创建 key",
      stepConnect: "连接你的 agent",
      stepCheck: "检查配置",
      checkBody: "先问这一句。它只读取余额和字段列表，不做任何搜索，不花 Credits：",
      checkPrompt:
        "使用 Metix AI Platform：调用 metix_get_key_status 和 metix_get_contract，然后告诉我我的 Credit 余额和可以查询哪些数据集。不要做任何搜索。",
      stepPrompt: "粘贴提示词",
      agentGet: "聚合文件和图表，一段说明抽检发现了什么、改了什么，以及这次运行花了多少 Credits（取自运行前后的余额）。",
      getLabel: "你会得到",
      adaptLede: "提示词就是这个案例本身。改掉下表里的部分，你的 agent 就会回答你的问题，用同样的检查和同样的花费记录方式。",
      emptyBalance: "如果调用返回 402 insufficient_quota，说明 key 有效，只是余额用完了。",
    },
    cost: {
      title: "花费",
      reproduce: "复现",
      agent: "Agent 运行",
      credits: (lo: number, hi: number = lo) => (lo === hi ? `${lo} Credits` : `${lo} 到 ${hi} Credits`),
      capNote: (n: number) => `提示词会在超过 ${n} Credits 之前先停下来问你。`,
      free: "新账户赠送的 100 Credits 够用",
      notFree: "超过新账户赠送的 100 Credits",
      unitNote: "1 Credit 可以买 25 个搜索结果或 5 条完整记录；1 美元可以买 30 Credits。",
    },
    setup: {
      label: "你的 agent",
      claude: "Claude Code",
      codex: "Codex",
      skills: "Skills",
      other: "其他 MCP 客户端",
      claudeNote: "为所有项目注册 Platform。在任意目录启动 claude，就能看到十个 metix 工具。",
      codexNote: "注册同一个服务。key 留在环境变量里，不写进配置文件。",
      skillsNote: "四个 skill，教任何 agent 使用 Platform 的接口和查询规则。有没有 MCP 都能用，Codex 也会读取它们。",
      otherNote: "让客户端通过 streamable HTTP 连接这个地址，用你的 key 作为 Bearer token。较旧的客户端使用同一主机上的 /sse。",
      docs: "MCP 配置指南",
    },
    start: {
      title: "跑你的第一个案例",
      lede: "三步，几分钟。新账户赠送的 Credits 够跑每一张卡片。",
      pick: "选一个案例",
      pickBody: "下面每个案例都写明了复现要花多少、交给 agent 跑要花多少。打开一个，用它的运行部分。",
      cheapest: (n: number) => `最便宜的一个交给 agent 跑只要 ${n} Credits。`,
    },
    promptTitle: "交给你的 agent 来跑",
    copyPrompt: "复制提示词",
    expandAll: "全部展开",
    collapseAll: "全部收起",
    questionLabel: "要回答的问题",
    stepsLabel: (n: number) => `${n} 个步骤`,
    makeItYours: "改成你的问题",
    methodLede: "人群怎么定义、怎么计数和抽检，以及这些数字不能说明什么。局限默认展开。",
    copy: "复制",
    copied: "已复制",
    copyFailed: "无法自动复制，文字已在下方选中，请按 Ctrl+C",
    methodTitle: "方法与局限",
    receiptTitle: "最近一次重跑",
    receiptLede: "上一次运行重跑脚本复现这个案例的花费，取自运行前后 Platform 自己记录的余额。",
    ranAt: "运行时间",
    callsLabel: "调用次数",
    resultsLabel: "搜索结果",
    recordsLabel: "读取记录",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `做这个案例另外花了大约 ${n} Credits：重跑脚本写出来之前 agent 做的抽检、试探性查询和被替换掉的运行。你不需要再花这部分。`,
    rerun: "复现",
    caseFolder: "GitHub 上的案例目录",
    pricing: "Credits 与价格",
    allCases: "全部案例",
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
