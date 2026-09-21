# Style

The site is **Casebook**: a publication of job-market cases made on the Metix AI Platform. It has its own look, looser than metix.ai or platform.metix.ai, and every case is free to find a look of its own. What stays fixed is small: brand names and terms, the shell that frames every page, the blocks every case ends with, accessibility, and the chart rules.

Where this page and [brand.metix.ai](https://brand.metix.ai) disagree, brand.metix.ai wins.

## Brand and terms

This site belongs to the **Metix AI Platform** (platform.metix.ai), not to the main site at metix.ai, and the name says so every time. Write the product as Metix AI Platform, in full, wherever it appears as a name: headings, body text, alt text, metadata, and Chinese pages, where it stays in English and untranslated. After the first mention on an English page, "the Platform" may stand in. Refer to the main site by its domain, metix.ai, and to its report library as metix.ai/reports. The legal entity OpenJobs AI Inc. appears only in the copyright line, "Copyright 2026 OpenJobs AI Inc. Metix AI Platform is a product of OpenJobs AI Inc." Casebook is the name of this site, never of the product.

Forms that are never written: Metix AI on its own (it names the company and the main site), Metix on its own, METIX, MetixAI outside the GitHub organization MetixAI-Official, Metix.ai with a capital M, and translations such as Metix AI 平台. No CSS `text-transform` on any element that can contain the name, because uppercase turns it into METIX. `scripts/check_public.py` catches the written forms; nothing catches a transform, so the review checklist does. <!-- check-public: allow brand -->

Write Credits with a capital C. Third-party product names are written the way their makers write them: Claude Code, GitHub Copilot, LangChain, LlamaIndex, CrewAI, AutoGen, DSPy, the Model Context Protocol.

The Platform has no logo artwork of its own, and Casebook does not make one. The header and footer use the lockup from platform.metix.ai: the official logo file (`site/public/brand/metix-logo.svg`, from the kit at brand.metix.ai), a 1 px hairline as tall as the wordmark's capitals, then "Platform" in the mono face, uppercase, weight 600, in the wordmark's navy `#100D35`. The label's capitals match the wordmark's x-height (13.85 px at the 24 px logo, 12 px on phones). Every part of the header row, the logo, the label, and the site name, shares the logo's vertical center, measured on the rendered capitals rather than on the line boxes, so the row reads level. Never set the mark beside the product name typed out in a font, since brand.metix.ai forbids rebuilding the wordmark and the Platform UI removed exactly that pattern. The logo image carries an empty alt and the element around the lockup carries the accessible name "Metix AI Platform", so a screen reader says the name once. Do not recolor, outline, shadow, stretch, or rotate the logo. Keep clear space of at least the height of the mark's X. Minimum height is 24 px for the full logo at every width, and 16 px for the mark alone, which is what to use when 24 px does not fit.

The brand colors are teal `#0DEFC8`, blue `#1E79C2`, violet `#5B54EF`, navy `#100D35`, periwinkle `#B5B5FF`, and sky `#A3E4FF`. Casebook uses them as whole fields of color, and color means data: the blue family (blue, sky) is jobs, the violet family (violet, periwinkle) is profiles, teal is companies, and navy is a case that uses more than one dataset. `fieldColor()` in `site/src/cases.ts` picks the field from a case's datasets, alternating the deep and light tone of the family by catalog position, so a card looks the same on the catalog and on its own page. The index and its filters show the same meaning as a dot, in each family's darker shade (`DATASET_INK`) so the dot reaches 3:1 on the ground. The signature gradient belongs to the logo and is not reused.

## Voice

Direct, specific, and checkable, in both languages. A title states the finding in sentence case, in 90 characters or fewer: "Job titles name inference eight times as often as pre-training" is a title, "Model lifecycle hiring" is a label. Every number carries its metric, scope, and date, following `docs/public-data-policy.md`. No hype adjectives, no emoji, no em or en dashes (in Chinese too, including the doubled Chinese dash), and no rhetorical questions as headings.

English is the default at `/`; Chinese lives at `/zh/`, and the language switch keeps the reader on the same page. Chinese copy is written for Chinese readers rather than translated word for word, with product names, field names, and code left in English and full-width punctuation around them.

## Two formats

**Card.** One question, one number, one small chart. On the catalog a card is a field of color with a meta line, the finding as its title, a big number, a mini chart, and a receipt stub at the bottom (a perforated line with punched notches, then the Credits to reproduce and the date). A card's own page opens with a hero in the same color carrying the number and the finding only, then the full detail chart and the closing blocks, so the chart is never shown twice.

**Report.** A long read with many figures. On the catalog the newest report is a full-width dark band with the finding, three highlight numbers, and a call to read it. A report's page brings its own hero and theme.

## The shell

```css
:root {
  --ground: #EEF0F4;          /* cool paper, the page behind everything */
  --surface: #FFFFFF;         /* figures, code, the body of case pages */
  --surface-muted: #F4F5F8;
  --ink: #0B0A1F;             /* text, the primary pill */
  --ink-2: #3F3D56;
  --ink-3: #6A6880;           /* captions, mono labels (5.3:1 on white) */
  --line: #D8DBE3;
  --accent: #5B54EF;          /* focus rings, links */

  --display: "Sora Variable", "Geist Variable", system-ui, var(--cjk);
  --sans: "Geist Variable", system-ui, -apple-system, var(--cjk);
  --mono: "Geist Mono Variable", ui-monospace, "SF Mono", Menlo, var(--cjk), monospace;
  --cjk: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
}
```

Sora carries titles and big numbers (700 for the masthead and the numbers, 600 for headings), Geist carries reading, and Geist Mono carries anything a developer would scan: labels, meta lines, receipts, queries. Chinese falls back to the system CJK faces in every stack, the mono one included. All numbers use tabular figures.

The shell owns the header (logo, Casebook, language switch, GitHub, Get an API key), the footer, the home page, and the blocks every case page ends with.

The home page is ordered for a first visit: a masthead that says in one sentence what the Metix AI Platform is and what a case is, with "Run your first case" as the one primary action; a start strip (get a key, connect your agent, check the setup) that is the only part of the page on the white surface; a featured shelf (the newest report and three cards); the "All cases" index, a list rather than tiles so it stays usable at sixty cases, with search across both languages, format and dataset filters, sort by newest or by cost, and the state in the URL so a dataset tag on a case page lands on a filtered list; then coming next. Without JavaScript the index is simply the full list.

Every case page ends with, in this order: **Run it** (three paths, below), **Method and limits** (folded at its subsections, Limits open), **The last replay** (the measured cost of the replay script, then what making the case cost), and previous and next cases in index order. A breadcrumb (Casebook / Reports or Cards) opens the hero.

### Run it and cost

Every cost the site shows is one the reader can check. A case states two: the replay script's cost, from `data/receipt.json`, and what an agent following `PROMPT.md` spends, recorded as `agent_run: {low, high, cap}` in `case.yaml` (the counts plus the reads the prompt asks for, and the ceiling the prompt stops at). The prompt must name that ceiling in Credits, and the build fails if it does not. Costs are shown in Credits and in dollars at the pay-as-you-go price ($1 buys 30 Credits), with whether they fit the 100 Credits a new account gets once. What making the case cost (the author's exploration) is labelled as that and never presented as the price of a rerun.

Run it offers three paths, as links to their panels so each deep-links and the section works without JavaScript: **Run it in your agent** (key, connect with the shared agent picker, a setup check that runs no search, then the prompt as its question and ten folded steps), **Reproduce the numbers** (clone and run the script), and **Adapt it** (the prompt's own "Adapt it" table and the questions to settle first). The agent picker shows only setups the Platform documents and has run: Claude Code, Codex, the skills installer, and the endpoint and header for any other MCP client. It remembers the reader's choice across pages.

### Card fields

The field comes from the case's datasets (see Brand and terms). The text and chart colors on each field are fixed so that every mark carrying data reaches 3:1 against the field, and secondary text on the violet and blue fields is solid white:

| Field | Background | Text | Focus mark | Other marks |
| --- | --- | --- | --- | --- |
| violet | `#5B54EF` | white (5.3:1) | teal `#0DEFC8` (3.6:1) | `#D9D7FF` (3.8:1) |
| navy | `#100D35` | white | sky `#A3E4FF` (13.4:1) | `#8C8AA8` (5.6:1) |
| blue | `#1E79C2` | white (4.6:1) | ink `#0B0A1F` (4.2:1) | `#C9F6FF` (4.0:1) |
| teal | `#0DEFC8` | ink (13.2:1) | ink | `#5E5C78` (4.3:1) |

Sky and periwinkle fields use ink text and `#3D3A8C` marks. On white, the focus color of every chart is teal ink `#07545E` and other marks are grey `#7E8787`.

## Per-case design

Each card and report records its choices in a short "Design" comment at the top of its `report/Report.astro`: the palette, the type treatment, and the one element it will be remembered by. Examples in this repository: the metro card scales bars to the share of all postings with a dashed line at 50%; the coding-tools card draws strict counts in front of an outline of the looser count; the tool-stack report puts profiles and postings on two sides of one spine.

Guardrails every case keeps: the shell and the closing blocks; 4.5:1 for body text and 3:1 for data marks; both languages; 375 px as well as 1440; the chart rules below; nothing from the list at the end of this page.

## Charts

Charts render at build time from committed aggregate files. They never read raw records and never compute a number the aggregate files do not contain. Shared pieces live in `site/src/components/charts/`: `Figure` (heading, subtitle, text alternative, source line, queries) and `BarList` (labelled bars with focus, other, residual, and lower-bound styles, and an optional outline for a looser count).

- Label directly; color is never the only key.
- One series in the focus color, the rest in grey, unless the categories themselves are the point. Never more than four hues.
- Say what a bar is scaled to. Shares of a total are drawn against the total, so a bar that is half the total fills half the width.
- Hatching means one thing: a lower bound (a strict count, such as a tool counted only when another tool is named too). Every hatched mark has a key where it appears. Leftover buckets (everywhere else, no city given, rest of the world) are drawn like the other marks and told apart by their label and their place last. A cell that does not apply says so in words ("same tool"). A suppressed cell is an empty outline labelled `<10`.
- A log scale is allowed for ratios, with the one-to-one line drawn and labelled.
- Do not draw a result that a definition forces. A tool counted only when named with another tool will always co-occur with another tool, so it does not get a co-mention row.
- Every figure has a heading that states the finding, a source line, a text alternative, and its queries.

## Chinese typesetting

Chinese has no spaces, so a browser left alone breaks titles anywhere, splitting words such as 旧金山湾区. Display titles go through `titleHtml()` in `site/src/i18n.ts`: ICU word segmentation at build time puts a break opportunity between words, product names and Latin runs stay whole, closing punctuation stays with the word before it, and `word-break: keep-all` stops the browser from breaking anywhere else. ICU splits a few domain words wrongly, so `PROTECTED` lists terms that never break (湾区, 工程师, 预训练, 薪资, and so on); add a term when a new title needs it. Body text uses the browser's normal Chinese line breaking.

## Size and touch

No text is smaller than 12 px. On phones, every link a thumb is meant to hit (breadcrumbs, dataset tags, hero chips, footer links, filters, tabs) is at least 44 px tall.

## Motion

Cards and report bands lift by 2 to 3 px on hover; the query disclosure and the folds open over 150 to 220 ms where the browser can animate height. With `prefers-reduced-motion: reduce`, nothing moves.

## Out of bounds

A grid of identical cards (cards here differ in chart and number because their content differs, and the catalog lists every case in an index rather than a wall of tiles), a centered hero over three feature boxes, gradient text, glass or blur, decorative icons or shapes, stock illustrations, third-party logos, and the stock AI looks (purple gradient on dark, cream with a serif and terracotta, near-black with an acid accent).

## Done means rendered and checked

A page is finished when it has been rendered and looked at, at 1440 and 375 pixels wide, in both languages, with no horizontal overflow and an empty console: the home page with and without JavaScript, the index with a search, each filter, each sort, and a filtered URL, every card page, every report, each Run it path, each agent tab, the language switch, hover and keyboard focus, the query disclosure and the folds open and closed, Copy succeeding and failing.
