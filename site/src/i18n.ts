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
const PROTECTED = ["清华大学", "北京大学", "浙江大学", "上海交通大学", "中国科学技术大学", "旧金山湾区", "湾区", "工程师", "编程", "薪资", "起薪", "预训练", "后训练", "写明", "本科", "中国大陆", "研究员", "个人档案", "前线部署", "以上", "以下", "职位名称", "点名", "留给新人", "客户服务", "注册护士", "暴露度", "五分之一", "软件工程", "职业族"];
/** A line never starts with these particles; they belong to the word before. */
const NO_BREAK_BEFORE = /^[的地得了着过吗呢吧里]/;
/** 被 and 把 bind to the verb that follows. */
const NO_BREAK_AFTER = /[被把]$/;
/** Measure words: a number, its classifier, and the noun after it stay on one line. */
const CLASSIFIER = /[个份家名条位倍万亿岁]$/;
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
  // A short uppercase compound such as "US-based" never breaks at its hyphen.
  if (lang !== "zh") return escapeHtml(kept).replace(/\b([A-Z]{2,3}-[a-z]+)\b/g, '<span class="nowrap">$1</span>');
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
  for (const cut of [...cuts]) {
    const before = kept.slice(0, cut);
    const after = kept.slice(cut);
    const numbered = CLASSIFIER.test(before) && /\d[\s\u00a0]?[个份家名条位倍万亿岁]$/.test(before);
    const unit =
      (/\d[\s\u00a0]$/.test(before) && /^[\u3400-\u9fff%]/.test(after)) ||
      (/[一二三四五六七八九十两百千几每这那]$/.test(before) && /^[个份家名条位倍万亿岁成]/.test(after));
    if (NO_BREAK_BEFORE.test(after) || NO_BREAK_AFTER.test(before) || numbered || unit) cuts.delete(cut);
  }
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
  // The space in "3.3 倍" is a break opportunity too; a number keeps its unit.
  return pieces.map((piece) => escapeHtml(piece.replace(/(\d) (?=[\u3400-\u9fff%])/g, "$1\u00a0"))).join("<wbr>");
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
    planned: "Planned",
    read: "Read",
    types: { study: "Study", snapshot: "Snapshot", recipe: "Recipe", agent: "Agent session" },
    datasets: { people: "Profiles", jobs: "Jobs", companies: "Companies" },
    integration: { rest: "REST", mcp: "MCP", skills: "Skills" },
    calls: "calls",
    records: "records",
    countsOnly: "counts only, no records read",
    creditsToRerun: "Credits to reproduce",
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
      indexNote: "Search titles, summaries, and topics; filter by format and data; sort by cost.",
      search: "Search cases",
      searchPlaceholder: "Search titles, summaries, topics",
      format: "Format",
      formatAll: "All",
      data: "Data",
      sort: "Sort",
      sortNewest: "Newest",
      sortReproduce: "Cheapest to reproduce",
      sortAgent: "Cheapest in an agent",
      count: (n: number) => (n === 1 ? "1 case" : `${n} cases`),
      noResults: "No case matches these filters.",
      clear: "Clear search and filters",
      reproduceShort: (n: string) => `reproduce ${n} Credits`,
      agentShort: (range: string) => `agent run ${range} Credits`,
      makeOwn: "Make your own case",
      makeOwnBody: "Start from the prompt template: change the question, keep the ten steps, run it on your key.",
    },
    caseNav: { prev: "Previous case", next: "Next case", all: "All cases", more: "More cases" },
    run: {
      title: "Run it",
      lede: "Three ways in. Each says what it costs before you start.",
      pathsLabel: "How to run it",
      reproduce: "Reproduce the numbers",
      reproduceHint: (records: number) =>
        records === 0 ? "Counts only, no agent needed" : `Counts plus ${records} records read, no agent needed`,
      agent: "Run it in your agent",
      agentHint: (same: boolean) => (same ? "The same queries, run by your agent" : "The whole method, with its audits"),
      adapt: "Adapt it",
      adaptHint: "Ask your own question",
      reproduceLede: (records: number) =>
        `A short standard-library Python script sends the committed queries${records === 0 ? " as counts" : `, reads the ${records} records the method needs,`} and writes the aggregate files this page is built from. It needs Python and METIX_KEY set in the shell (step 1 of the agent path); your agent can run these lines for you as well.`,
      reproduceGet: (slug: string) =>
        `data/*.json and data/receipt.json. Run git diff cases/${slug}/data to see what moved: the numbers should match, apart from what changed in the data since the snapshot.`,
      agentLede:
        "Your agent follows the ten-step prompt: it reads the rules, runs the counts, checks the definitions the prompt asks it to check, and writes the files and the chart. Use an agent that can write files, such as Claude Code or Codex.",
      stepKey: "Get a key",
      keyBody:
        "New accounts get 100 Credits once, valid for 30 days. Set the key in the shell you start your agent from, or add the line to ~/.zshrc or ~/.bashrc so every new terminal has it:",
      createKey: "Create a key on the Metix AI Platform",
      stepConnect: "Connect your agent",
      stepCheck: "Check the setup",
      checkBody: "Ask this first. It reads your balance and the field list, runs no search, and costs nothing:",
      checkPrompt:
        "Use the Metix AI Platform to check my key status and read the contract; both are free. Then tell me my Credit balance and which datasets I can query. Do not run any search.",
      stepPrompt: "Paste the prompt",
      stepPromptBody: "Start your agent in an empty folder, then paste. It writes its files there.",
      setupOnce: "Set up once",
      setupOnceNote: "Key, connection, and a free check. Skip this if your agent already reaches the Platform.",
      viewSource: "PROMPT.md on GitHub",
      agentGet:
        "The aggregate files and the chart, a note on what the audits found and what they changed, and the Credits the run spent, read from the balance before and after.",
      getLabel: "What you get",
      adaptLede:
        "The prompt is the case. Change the parts in this table and your agent answers your question instead, with the same checks and the same way of reporting cost.",
      adaptCost: "Costs what your version reads. Write your own ceiling into step 1 of the prompt.",
      emptyBalance: "A call that returns 402 insufficient_quota means the key works and the balance is empty.",
    },
    cost: {
      title: "What it costs",
      reproduce: "Reproduce",
      agent: "Agent run",
      credits: (lo: number, hi: number = lo) => (lo === hi ? `${lo} Credits` : `${lo} to ${hi} Credits`),
      capNote: (n: number) => `Your agent stops and asks before spending more than ${n} Credits.`,
      free: "Fits in the 100 free Credits",
      maybe: "May run past the 100 free Credits",
      notFree: "More than the 100 free Credits",
      unitNote: "1 Credit buys 25 search results or 5 full records; $1 buys 30 Credits.",
    },
    setup: {
      label: "How your agent connects",
      claude: "Claude Code",
      codex: "Codex",
      skills: "Skills",
      other: "Other MCP",
      claudeNote: "Registers the Platform for every project. Start claude in any folder and the ten metix tools are there.",
      codexNote: "Registers the same server. The key stays in your environment instead of the config file.",
      skillsNote:
        "Four skills that teach any agent the Platform's endpoints and query rules, for agents without MCP. The installer starts with none ticked: press space on each, then enter.",
      otherNote:
        "Point the client at this endpoint over streamable HTTP with both headers; without the Accept header the server answers 406. Older clients use /sse on the same host.",
      docs: "MCP setup guide",
      skillsDocs: "Skills install guide",
    },
    start: {
      title: "Run your first case",
      lede: (total: number, reproduce: number, agent: number) =>
        `Four steps, a few minutes. A new account's 100 free Credits reproduce ${reproduce === total ? `all ${total} cases` : `${reproduce} of the ${total} cases`} and run ${agent} of them end to end in your agent.`,
      stepRun: "Run a case",
      connectBody: "Pick the agent you use. Each tab gives the one step that connects it to the Metix AI Platform.",
      openPrompt: "Open its prompt",
      runBody: "Start with the cheapest one. Its prompt is ready to copy, and every other case says its cost the same way.",
    },
    promptTitle: "Run it with your agent",
    copyPrompt: "Copy prompt",
    expandAll: "Expand all",
    collapseAll: "Collapse all",
    questionLabel: "The question",
    stepsLabel: (n: number) => `${n} steps`,
    makeItYours: "Make it yours",
    methodLede: "How the population was defined, counted, and checked, and what the numbers cannot show.",
    copy: "Copy",
    code: { shell: "Shell", prompt: "Prompt for your agent", mcp: "Endpoint and headers" },
    copied: "Copied",
    copyFailed: "Could not copy. The text is selected below: press Ctrl+C",
    methodTitle: "Method and limits",
    receiptTitle: "The last reproduction",
    receiptLede:
      "What reproducing this case cost the last time the script ran, read from the Platform's own balance before and after.",
    ranAt: "Ran on",
    callsLabel: "Calls",
    resultsLabel: "Search results",
    recordsLabel: "Records read",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `Making this case cost about ${n} Credits more: the agent's audits, trial queries, and runs it replaced before the reproduce script existed. You do not pay that again.`,
    rerun: "Reproduce it",
    caseFolder: "Case folder on GitHub",
    pricing: "Credits and pricing",
    allCases: "All cases",
    skipLink: "Skip to content",
    crumbs: "Breadcrumb",
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
    mastCredits: "Credits 可全部复现",
    mastRun: "最近一次运行",
    reportsLabel: "报告",
    reportsNote: "长篇，多张图，从几个角度看同一个问题。",
    cardsLabel: "卡片",
    cardsNote: "一个问题，一个数字，一张图。每张卡片都是独立的案例，有自己的提示词。",
    formats: { card: "卡片", report: "报告" },
    readReport: "阅读报告",
    openCard: "打开卡片",
    toRerun: (n: string) => `复现需 ${n} Credits`,
    seePrompt: "查看提示词",
    makeEyebrow: "你的卡片",
    makeTitle: "做一张你自己的卡片",
    makeSteps: ["先读规则再查询", "人群定义", "先计数", "预算", "抽检", "清洗", "分组", "输出", "图表", "局限"],
    makeBody: "复制提示词模板，换成你的问题，让你的 agent 用你自己的 key 去跑。这里的每张卡片都是这样开始的。",
    makeCta: "提示词模板",
    resultsNote: (records: number) =>
      `搜索结果是搜索返回的 ID 数，每次计数查询算一个，完整搜索按命中数算。记录是完整读取的岗位或档案：${records === 0 ? "这个案例一条都没读" : `这里读了 ${records} 条`}。`,
    siteName: "Metix AI Platform 案例集",
    siteDescription:
      "由 AI agent 在 Metix AI Platform 上完成的就业市场报告，每份都附带查询、Credits 花费和生成它的提示词。",
    navCases: "案例",
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
    planned: "计划中",
    read: "阅读",
    types: { study: "研究", snapshot: "快照", recipe: "配方", agent: "agent 会话" },
    datasets: { people: "个人档案", jobs: "岗位", companies: "公司" },
    integration: { rest: "REST", mcp: "MCP", skills: "Skills" },
    calls: "次调用",
    records: "条记录",
    countsOnly: "只计数，未读取记录",
    creditsToRerun: "Credits 可复现",
    home: {
      lede: "由 AI agent 在 Metix AI Platform 上回答的就业市场问题。Metix AI Platform 是职业档案、招聘岗位和公司的数据 API，agent 可以通过 MCP、skills 或 REST 访问。每个案例都公开结论、背后的查询、花了多少，以及生成它的提示词。",
      ctaStart: "跑你的第一个案例",
      ctaBrowse: "浏览全部案例",
      statCases: "个已发布案例",
      statCheapest: "Credits，最便宜的案例交给\u00a0agent\u00a0跑",
      statFree: "Credits，新账户赠送",
      featured: "精选",
      featuredNote: "最新的一份报告和三张卡片。全部案例都在下面的索引里。",
      index: "全部案例",
      indexNote: "搜索标题、摘要和主题，按形式和数据筛选，按花费排序。",
      search: "搜索案例",
      searchPlaceholder: "搜索标题、摘要、主题",
      format: "形式",
      formatAll: "全部",
      data: "数据",
      sort: "排序",
      sortNewest: "最新",
      sortReproduce: "复现最便宜",
      sortAgent: "交给 agent 最便宜",
      count: (n: number) => `${n} 个案例`,
      noResults: "没有符合这些筛选条件的案例。",
      clear: "清除搜索和筛选",
      reproduceShort: (n: string) => `复现 ${n} Credits`,
      agentShort: (range: string) => `agent 运行 ${range} Credits`,
      makeOwn: "做你自己的案例",
      makeOwnBody: "从提示词模板开始：换成你的问题，保留十个步骤，用你自己的 key 运行。",
    },
    caseNav: { prev: "上一个案例", next: "下一个案例", all: "全部案例", more: "更多案例" },
    run: {
      title: "运行这个案例",
      lede: "三种方式，每一种都先告诉你要花多少。",
      pathsLabel: "运行方式",
      reproduce: "复现数字",
      reproduceHint: (records: number) => (records === 0 ? "只计数，不需要 agent" : `计数，另读取 ${records} 条记录，不需要 agent`),
      agent: "交给你的 agent 来跑",
      agentHint: (same: boolean) => (same ? "同样的查询，由你的 agent 来跑" : "完整方法，包括抽检"),
      adapt: "改成你的问题",
      adaptHint: "问你自己的问题",
      reproduceLede: (records: number) =>
        `一个只用 Python 标准库的小脚本，把已提交的查询${records === 0 ? "按计数发出去" : `发出去，读取方法需要的 ${records} 条记录`}，写出这个页面所用的聚合文件。需要 Python，并在终端里设置好 METIX_KEY（见 agent 路径的第 1 步），也可以让你的 agent 替你运行这几行。`,
      reproduceGet: (slug: string) =>
        `data/*.json 和 data/receipt.json。运行 git diff cases/${slug}/data 看哪些数字变了：除去快照之后数据本身的变化，数字应该一致。`,
      agentLede:
        "你的 agent 按十步提示词执行：先读规则，再计数，按提示词的要求检查定义，最后写出文件和图表。请使用能写文件的 agent，比如 Claude Code 或 Codex。",
      stepKey: "获取 key",
      keyBody: "新账户一次性赠送 100 Credits，30 天内有效。在启动 agent 的终端里设置，或者把这一行写进 ~/.zshrc 或 ~/.bashrc，新开的终端也能用：",
      createKey: "在 Metix AI Platform 上创建 key",
      stepConnect: "连接你的 agent",
      stepCheck: "检查配置",
      checkBody: "先问这一句。它只读取余额和字段列表，不做任何搜索，不花 Credits：",
      checkPrompt:
        "使用 Metix AI Platform：查询我的 key 状态并读取 contract，这两项都免费。然后告诉我我的 Credit 余额和可以查询哪些数据集。不要做任何搜索。",
      stepPrompt: "粘贴提示词",
      stepPromptBody: "在一个空文件夹里启动 agent，再粘贴。它会把文件写在那里。",
      setupOnce: "一次性配置",
      setupOnceNote: "key、连接和一次免费检查。如果你的 agent 已经接入 Metix AI Platform，可以跳过。",
      viewSource: "GitHub 上的 PROMPT.md",
      agentGet: "聚合文件和图表，一段说明抽检发现了什么、改了什么，以及这次运行花了多少 Credits（取自运行前后的余额）。",
      getLabel: "你会得到",
      adaptLede: "提示词就是这个案例本身。改掉下表里的部分，你的 agent 就会回答你的问题，用同样的检查和同样的花费记录方式。",
      adaptCost: "花费取决于你的版本读取多少。在提示词第 1 步里写上你自己的上限。",
      emptyBalance: "如果调用返回 402 insufficient_quota，说明 key 有效，只是余额用完了。",
    },
    cost: {
      title: "花费",
      reproduce: "复现",
      agent: "agent 运行",
      credits: (lo: number, hi: number = lo) => (lo === hi ? `${lo} Credits` : `${lo} 到 ${hi} Credits`),
      capNote: (n: number) => `花费超过 ${n} Credits 之前，agent 会先停下来问你。`,
      free: "新账户赠送的 100 Credits 够用",
      maybe: "可能超出赠送的 100 Credits",
      notFree: "超过新账户赠送的 100 Credits",
      unitNote: "1 Credit 可以买 25 个搜索结果或 5 条完整记录；1 美元可以买 30 Credits。",
    },
    setup: {
      label: "连接方式",
      claude: "Claude Code",
      codex: "Codex",
      skills: "Skills",
      other: "其他 MCP",
      claudeNote: "为所有项目注册 Metix AI Platform。在任意目录启动 claude，就能看到十个 metix 工具。",
      codexNote: "注册同一个服务。key 留在环境变量里，不写进配置文件。",
      skillsNote: "四个 skill，教任何 agent 使用 Metix AI Platform 的接口和查询规则，适合不支持 MCP 的 agent。安装程序默认一项都不勾选：在每一项上按空格，再按回车。",
      otherNote: "让客户端通过 streamable HTTP 连接这个地址，并带上这两个请求头；缺少 Accept 请求头时服务器会返回 406。较旧的客户端使用同一主机上的 /sse。",
      docs: "MCP 配置指南",
      skillsDocs: "Skills 安装说明",
    },
    start: {
      title: "跑你的第一个案例",
      lede: (total: number, reproduce: number, agent: number) =>
        `四步，几分钟。新账户赠送的 100 Credits 可以复现${reproduce === total ? `全部 ${total} 个案例` : ` ${total} 个案例中的 ${reproduce} 个`}，并交给 agent 完整跑完其中 ${agent} 个。`,
      connectBody: "选你用的 agent。每个标签页给出把它接入 Metix AI Platform 的那一步。",
      stepRun: "跑一个案例",
      openPrompt: "打开它的提示词",
      runBody: "从最便宜的一个开始，它的提示词可以直接复制。其他案例也用同样的方式写明花费。",
    },
    promptTitle: "交给你的 agent 来跑",
    copyPrompt: "复制提示词",
    expandAll: "全部展开",
    collapseAll: "全部收起",
    questionLabel: "要回答的问题",
    stepsLabel: (n: number) => `${n} 个步骤`,
    makeItYours: "改成你的问题",
    methodLede: "统计范围怎么定义、怎么计数和抽检，以及这些数字不能说明什么。",
    copy: "复制",
    code: { shell: "终端", prompt: "发给 agent 的提示", mcp: "地址和请求头" },
    copied: "已复制",
    copyFailed: "无法自动复制，文字已在下方选中，请按 Ctrl+C",
    methodTitle: "方法与局限",
    receiptTitle: "最近一次复现",
    receiptLede: "上一次复现花了多少，取自运行前后 Metix AI Platform 记录的余额。",
    ranAt: "运行日期",
    callsLabel: "调用次数",
    resultsLabel: "搜索结果",
    recordsLabel: "读取记录",
    creditsLabel: "Credits",
    exploration: (n: number) =>
      `做这个案例另外花了大约 ${n} Credits：复现脚本写出来之前 agent 做的抽检、试探性查询和被替换掉的运行。你不需要再花这部分。`,
    rerun: "复现",
    caseFolder: "GitHub 上的案例目录",
    pricing: "Credits 与价格",
    allCases: "全部案例",
    skipLink: "跳到正文",
    crumbs: "页面路径",
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

/** "Figures 04 and 05" / "图 04、05": the figures a report chapter holds. */
export function chapterFigures(lang: Lang, figures: string[]): string {
  if (lang === "zh") return `图 ${figures.join("、")}`;
  const list = figures.length === 1 ? figures[0] : figures.length === 2 ? figures.join(" and ") : `${figures[0]} to ${figures[figures.length - 1]}`;
  return `${figures.length === 1 ? "Figure" : "Figures"} ${list}`;
}
