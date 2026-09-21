# Style

The site has two layers with different rules. The shell (header, catalog, footer, and the blocks every report shares) is fixed and belongs to the Metix AI Platform. The report inside it is free: each report picks a visual direction for its own subject, within the guardrails below. Readers should always know they are on the Metix AI Platform, and no two reports need to look alike.

Where this page and [brand.metix.ai](https://brand.metix.ai) disagree, brand.metix.ai wins.

## Brand

The product is **Metix AI Platform** and the company is **Metix AI**. Never METIX, MetixAI (outside the GitHub organization name), or Metix on its own. OpenJobs AI Inc. is the legal entity and appears only in the footer and legal text. <!-- check-public: allow brand -->

Use the official logo files. Do not recolor, outline, shadow, stretch, rotate, or rebuild the wordmark in another font. Keep clear space on every side of at least the height of the mark's X. Minimum height: 24 px for the full logo, 16 px for the mark alone.

The brand colors are teal `#0DEFC8`, blue `#1E79C2`, violet `#5B54EF`, navy `#100D35`, periwinkle `#B5B5FF`, and sky `#A3E4FF`. The signature gradient (teal 0%, blue 70%, violet 100%) belongs to the logo; the shell does not reuse it.

## Voice

Direct, specific, and checkable, in both languages. A sentence that could appear on any vendor's site gets cut.

A title states the finding, in sentence case, in 90 characters or fewer. "Nearly half of US inference openings are in the Bay Area" is a title. "Inference talent landscape 2026" is a label.

Every number carries its metric, scope, and date, following the wording rules in `docs/public-data-policy.md`. Write Credits with a capital C. Dates in labels and data are ISO (`2026-09-21`); dates in prose are written out.

No hype adjectives, no emoji, no em or en dashes (in Chinese too, including the doubled Chinese dash), and no rhetorical questions as headings.

## Languages

English is the default and lives at `/`; Chinese lives at `/zh/`. Every page exists in both, and the language switch keeps the reader on the same page. Chinese copy is written for Chinese readers, not translated word for word: shorter sentences, and product names, field names, and code left in English.

## The shell

The shell uses the Platform's own language, so the site reads as part of platform.metix.ai.

```css
:root {
  --canvas: #FCFDFD;          /* page ground */
  --surface: #FFFFFF;         /* figures, code, raised blocks */
  --surface-muted: #F4F6F6;   /* table headers, receipts, code headers */
  --ink: #161514;             /* text, the primary pill */
  --ink-2: #4E4D4B;           /* secondary text */
  --ink-3: #6B6A67;           /* captions, mono labels */
  --line: #E3E6E6;
  --accent-ink: #07545E;      /* links, active states: the cyan end of the brand gradient */
  --accent-tint: #DFF1F3;
  --accent-subtle: #F4FAFB;
  --accent-line: #BFE3E8;
  --warn: #FF6614;            /* status only, never a data series */

  --display: "Sora Variable", "Geist Variable", system-ui, sans-serif;
  --sans: "Geist Variable", system-ui, -apple-system, sans-serif;
  --mono: "Geist Mono Variable", ui-monospace, "SF Mono", Menlo, monospace;
  --cjk: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
}
```

Type roles: Sora for titles and key numbers, Geist for reading, Geist Mono for anything a developer would scan (labels, eyebrows, receipts, queries, units). Chinese text falls back to the system CJK faces in `--cjk`; the site ships no CJK web font. All numbers use tabular figures.

The shell owns:

- The header: the Metix AI Platform mark, Use cases, the language switch, GitHub, and one primary action, Get an API key. It never changes between pages.
- The catalog: full-width rows, not a grid of cards, because titles are sentences and need the width.
- Three blocks every report ends with, so readers find them in the same place every time: **Run it with your agent** (the bootstrap prompt, with Copy), **Method and limits**, and **Receipt** (what the replay cost).
- The per-chart query disclosure, `Query · N Credits`, a native `<details>` element that shows the Query Spec and a Copy button.
- The footer.

### Signature: the receipt and the prompt

Every report shows what its numbers cost and the prompt that produced them. That is what a Platform report offers and a report library does not: the reader can check the work, rerun it for the stated Credits, and adapt the prompt to their own question.

## The report

Each report chooses its own palette, display treatment, and chart style for its subject, and records the choice in a short "Design" note at the top of its `report/Report.astro`: four to six named colors, the type treatment, and the one element the report will be remembered by. It reuses the shell's fonts unless the subject gives a reason not to.

Guardrails that every report keeps:

- The shell stays intact: header, footer, and the three closing blocks.
- Body text meets 4.5:1 contrast; marks that carry data meet 3:1 against their background.
- Both languages, and 375 px wide as well as 1440.
- The chart rules below.
- None of the defaults on the "Out of bounds" list.

### This snapshot: inference roles by US metro

- Palette: navy `#100D35` hero ground; sky `#A3E4FF` for the key number on navy (13.4:1); teal ink `#07545E` for the focus bar (8.6:1 on white); grey `#7E8787` for the other metros (3.7:1); "elsewhere" and "no city given" as hatched outlines in the same grey. A lighter grey such as `#C9CECE` reads better as a background but fails the 3:1 rule for marks (1.6:1), so it is not used for bars.
- Type: the shell's faces; the key number in Sora at 96 px (56 px on phones).
- Signature: bars scaled to the share of all postings, not to the largest bar, with a dashed line at 50% marked "half of all postings". The Bay Area bar reaches it.

## Charts

Charts render at build time from committed aggregate files. They never read raw records and never compute a number the aggregate file does not contain.

- Label directly: values and names on the bars or line ends. Color is never the only key.
- Default to focus: one series in the report's accent, everything else in grey. Use several hues only when the categories are the point, and never more than four.
- No dual axes, no 3D, no pie with more than three slices.
- A suppressed cell is drawn as an empty outlined mark labeled `<10`, never as an estimate.
- Every chart has a heading that states the finding, a source line (`Source: Metix AI Platform, jobs, 2026-09-21`), and a text alternative stating the same finding.
- A figure that cannot shrink to 375 px sits in a horizontally scrolling box with a "Scroll for the full chart" label.

## Motion

Almost none. Row hover changes the ground over 120 ms; the query disclosure opens over 150 ms where the browser can animate to `auto` height. With `prefers-reduced-motion: reduce`, nothing moves.

## Out of bounds

Grids of identical cards, a centered hero over three feature boxes, gradient text, glass or blur effects, decorative icons, stock illustrations, third-party logos, and the stock AI looks (purple gradient on dark, cream with a serif and terracotta accent, near-black with an acid accent).

## Done means rendered and checked

A page is finished when it has been rendered and looked at, at 1440 and 375 pixels wide, in both languages, with real content, in these states: the catalog with and without JavaScript; the language switch on every page; row and link hover and keyboard focus; the query disclosure closed and open; Copy succeeded and failed; long titles and long labels. The browser console is empty.
