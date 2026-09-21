# Style

The site is **Casebook**: a publication of job-market cases made on the Metix AI Platform. It has its own look, looser than metix.ai or platform.metix.ai, and every case is free to find a look of its own. What stays fixed is small: brand names and terms, the shell that frames every page, the blocks every case ends with, accessibility, and the chart rules.

Where this page and [brand.metix.ai](https://brand.metix.ai) disagree, brand.metix.ai wins.

## Brand and terms

This site belongs to the **Metix AI Platform** (platform.metix.ai), not to the main site at metix.ai, and the name says so every time. Write the product as Metix AI Platform, in full, wherever it appears as a name: headings, body text, alt text, metadata, and Chinese pages, where it stays in English and untranslated. After the first mention on an English page, "the Platform" may stand in. Refer to the main site by its domain, metix.ai, and to its report library as metix.ai/reports. The legal entity OpenJobs AI Inc. appears only in the copyright line, "Copyright 2026 OpenJobs AI Inc. Metix AI Platform is a product of OpenJobs AI Inc." Casebook is the name of this site, never of the product.

Forms that are never written: Metix AI on its own (it names the company and the main site), Metix on its own, METIX, MetixAI outside the GitHub organization MetixAI-Official, Metix.ai with a capital M, and translations such as Metix AI 平台. No CSS `text-transform` on any element that can contain the name, because uppercase turns it into METIX. `scripts/check_public.py` catches the written forms; nothing catches a transform, so the review checklist does. <!-- check-public: allow brand -->

Write Credits with a capital C. Third-party product names are written the way their makers write them: Claude Code, GitHub Copilot, LangChain, LlamaIndex, CrewAI, AutoGen, DSPy, the Model Context Protocol.

The Platform has no logo artwork of its own, and Casebook does not make one. The header and footer use the lockup from platform.metix.ai: the official logo file (`site/public/brand/metix-logo.svg`, from the kit at brand.metix.ai), a 1 px hairline at 14% ink, then "Platform" in the mono face, uppercase, muted. Never set the mark beside the product name typed out in a font, since brand.metix.ai forbids rebuilding the wordmark and the Platform UI removed exactly that pattern. The logo image carries an empty alt and the element around the lockup carries the accessible name "Metix AI Platform", so a screen reader says the name once. Do not recolor, outline, shadow, stretch, or rotate the logo. Keep clear space of at least the height of the mark's X. Minimum height is 24 px for the full logo at every width, and 16 px for the mark alone, which is what to use when 24 px does not fit.

The brand colors are teal `#0DEFC8`, blue `#1E79C2`, violet `#5B54EF`, navy `#100D35`, periwinkle `#B5B5FF`, and sky `#A3E4FF`. Casebook uses them as whole fields of color rather than as accents. The signature gradient belongs to the logo and is not reused.

## Voice

Direct, specific, and checkable, in both languages. A title states the finding in sentence case, in 90 characters or fewer: "Job titles name inference eight times as often as pre-training" is a title, "Model lifecycle hiring" is a label. Every number carries its metric, scope, and date, following `docs/public-data-policy.md`. No hype adjectives, no emoji, no em or en dashes (in Chinese too, including the doubled Chinese dash), and no rhetorical questions as headings.

English is the default at `/`; Chinese lives at `/zh/`, and the language switch keeps the reader on the same page. Chinese copy is written for Chinese readers rather than translated word for word, with product names, field names, and code left in English and full-width punctuation around them.

## Two formats

**Card.** One question, one number, one small chart. On the catalog a card is a field of color with a meta line, the finding as its title, a big number, a mini chart, and a receipt stub at the bottom (a perforated line with punched notches, then the Credits to rerun and the date). A card's own page opens with a hero in the same color and a larger version of the same card, then the detail chart and the closing blocks.

**Report.** A long read with many figures. On the catalog a report is a full-width dark band with the finding, three highlight numbers, and a call to read it. A report's page brings its own hero and theme.

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

The shell owns the header (logo, Casebook, language switch, GitHub, Get an API key), the catalog (a masthead with live totals, then reports, cards, a make-your-own tile, and coming next), the footer, and three blocks every case ends with, in this order: **Run it with your agent** (the bootstrap prompt with Copy at both ends), **Method and limits**, and **Receipt**.

### Card fields

Each card picks one field. The text and chart colors on each field are fixed so that every mark carrying data reaches 3:1 against the field:

| Field | Background | Text | Focus mark | Other marks |
| --- | --- | --- | --- | --- |
| violet | `#5B54EF` | white (5.3:1) | teal `#0DEFC8` (3.6:1) | `#D9D7FF` (3.8:1) |
| navy | `#100D35` | white | sky `#A3E4FF` (13.4:1) | `#8C8AA8` (5.6:1) |
| blue | `#1E79C2` | white (4.6:1) | ink `#0B0A1F` (4.2:1) | `#C9F6FF` (4.0:1) |
| teal | `#0DEFC8` | ink (13.2:1) | ink | `#5E5C78` (4.3:1) |
| signal | `#FF6614` | ink (6.7:1) | ink | `#7A2E0B` (3.2:1) |

Sky and periwinkle fields are available with ink text and `#3D3A8C` marks. Orange never carries a mark on white; on white the focus orange is `#C24A08`.

## Per-case design

Each card and report records its choices in a short "Design" comment at the top of its `report/Report.astro`: the palette, the type treatment, and the one element it will be remembered by. Examples in this repository: the metro card scales bars to the share of all postings with a dashed line at 50%; the coding-tools card draws strict counts in front of an outline of the looser count; the tool-stack report puts profiles and postings on two sides of one spine.

Guardrails every case keeps: the shell and the three closing blocks; 4.5:1 for body text and 3:1 for data marks; both languages; 375 px as well as 1440; the chart rules below; nothing from the list at the end of this page.

## Charts

Charts render at build time from committed aggregate files. They never read raw records and never compute a number the aggregate files do not contain. Shared pieces live in `site/src/components/charts/`: `Figure` (heading, subtitle, text alternative, source line, queries) and `BarList` (labelled bars with focus, other, residual, and lower-bound styles, and an optional outline for a looser count).

- Label directly; color is never the only key.
- One series in the focus color, the rest in grey, unless the categories themselves are the point. Never more than four hues.
- Say what a bar is scaled to. Shares of a total are drawn against the total, so a bar that is half the total fills half the width.
- Lower bounds and leftover buckets are hatched. A suppressed cell is an empty outline labelled `<10`.
- A log scale is allowed for ratios, with the one-to-one line drawn and labelled.
- Do not draw a result that a definition forces. A tool counted only when named with another tool will always co-occur with another tool, so it does not get a co-mention row.
- Every figure has a heading that states the finding, a source line, a text alternative, and its queries.

## Motion

Cards and report bands lift by 2 to 3 px on hover; the query disclosure opens over 150 ms where the browser can animate height. With `prefers-reduced-motion: reduce`, nothing moves.

## Out of bounds

A grid of identical cards (cards here differ in color, chart, and size because their content differs), a centered hero over three feature boxes, gradient text, glass or blur, decorative icons or shapes, stock illustrations, third-party logos, and the stock AI looks (purple gradient on dark, cream with a serif and terracotta, near-black with an acid accent).

## Done means rendered and checked

A page is finished when it has been rendered and looked at, at 1440 and 375 pixels wide, in both languages, with no horizontal overflow and an empty console: the catalog with and without JavaScript, every card page, every report, the language switch, hover and keyboard focus, the query disclosure open and closed, Copy succeeding and failing.
