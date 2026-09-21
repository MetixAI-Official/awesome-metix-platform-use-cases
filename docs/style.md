# Style

This site is part of the Metix AI Platform, so it uses the Platform's visual language, not a new one. The Platform at platform.metix.ai is white, typographic, and technical: Sora for display, Geist for body text, Geist Mono for anything a developer would type or scan, a black pill for the primary action, and one teal accent taken from the cyan end of the brand gradient. This page fixes those choices for use case pages and adds what the Platform does not have: rules for charts and for long data stories.

Where this page and [brand.metix.ai](https://brand.metix.ai) disagree, brand.metix.ai wins.

## Brand

The product is **Metix AI Platform** and the company is **Metix AI**. Never METIX, MetixAI (outside the GitHub organization name), or Metix on its own. OpenJobs AI Inc. is the legal entity and appears only in the footer and legal text. <!-- check-public: allow brand -->

Use the official logo files. Do not recolor, outline, shadow, stretch, rotate, or rebuild the wordmark in another font. Keep clear space on every side of at least the height of the mark's X. Minimum height: 24 px for the full logo, 16 px for the mark alone. The header lockup matches the one on platform.metix.ai.

The signature gradient (teal `#0DEFC8` at 0%, blue `#1E79C2` at 70%, violet `#5B54EF` at 100%) belongs to the logo. The interface does not reuse it: no gradient text, buttons, borders, or backgrounds. The Platform made the same choice, and one accent color is what keeps dense pages calm.

## Voice

Write like the Platform's own pages: direct, specific, and checkable. A sentence that could appear on any vendor's site gets cut.

A title states the finding, in sentence case, in 90 characters or fewer. "Inference providers post more roles in cost engineering than in research" is a title. "Inference talent landscape 2026" is a label.

Every number carries its metric, scope, and date, following the wording rules in `docs/public-data-policy.md`. Write Credits with a capital C, as the Platform does. Dates in labels and data are ISO (`2026-09-18`); dates in prose are written out (September 18, 2026).

No hype adjectives, no emoji, no em or en dashes, no rhetorical questions as headings. English only for now.

## Composition

The page is built in three layers, in order of how much of it they take up.

The chassis is the Platform's own: white canvas, generous margins, a single reading column for prose, Sora headings, Geist body text, mono labels. It carries the reading.

The evidence is the product's native object: the chart, and next to it the Query Spec that produced it and what that query cost. Queries are shown as real JSON, never as a screenshot or an illustration.

The accent is one color, teal ink `#07545E`, used for links, the active filter, and the numbers that carry a finding. Nothing else on the page is colored except the charts.

## Tokens

```css
:root {
  color-scheme: light;

  /* surfaces */
  --canvas: #FCFDFD;           /* page ground, the Platform docs canvas */
  --surface: #FFFFFF;          /* figures, code, raised blocks */
  --surface-muted: #F4F6F6;    /* table headers, the receipt, code headers */

  /* ink */
  --ink: #161514;              /* headings, body, the primary pill */
  --ink-2: #4E4D4B;            /* deks, secondary text */
  --ink-3: #6B6A67;            /* captions, mono labels */
  --line: #E3E6E6;             /* dividers, table rules, input borders */

  /* accent: the cyan end of the brand gradient, as the Platform uses it */
  --accent-ink: #07545E;       /* links, key numbers, active filter text */
  --accent-tint: #DFF1F3;      /* selected filter ground */
  --accent-subtle: #F4FAFB;    /* row hover */
  --accent-line: #BFE3E8;      /* selected filter border, callout border */

  /* status, never used as a data series */
  --warn: #FF6614;
  --warn-tint: #FFF3EC;

  /* type */
  --display: "Sora", "Geist", system-ui, sans-serif;
  --sans: "Geist", system-ui, -apple-system, sans-serif;
  --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace;

  /* geometry */
  --radius: 10px;
  --pill: 999px;
  --measure: 68ch;             /* prose column */
  --figure: 760px;             /* chart column */
  --page: 1200px;              /* outer frame */
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

The site is light only, like metix.ai. Charts are designed and checked against the white surface.

Sora, Geist, and Geist Mono are all under the SIL Open Font License. The site self-hosts them as woff2 files with their license texts next to them, and loads nothing from a font CDN.

## Type

| Role | Face | Size / line height (desktop, mobile) | Used for |
| --- | --- | --- | --- |
| Case title | Sora 600 | 40/1.15, 30/1.2 | One per page |
| Section heading | Sora 600 | 26/1.25, 22/1.3 | Study sections, with a mono section number |
| Figure heading | Sora 600 | 18/1.35 | The finding a chart supports |
| Key number | Sora 600, tabular | 36/1.1, 30/1.1 | At most three per case, in accent ink |
| Dek | Geist 400 | 20/1.5, 18/1.5 | One sentence under the title |
| Body | Geist 400 | 17/1.65 | Prose, capped at `--measure` |
| Label | Geist Mono 500, uppercase, 0.06em tracking | 12/1.4 | Type labels, eyebrows, table headers, units |
| Receipt and code | Geist Mono 400, tabular | 13/1.55 | Query JSON, receipts, commands |

All numbers use `font-variant-numeric: tabular-nums`. Hierarchy comes from size and weight, never from color.

## Layout

### Catalog, 1440 px

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Metix AI Platform]   Use cases  Method  Docs  GitHub        (Get an API key)│
├──────────────────────────────────────────────────────────────────────────────┤
│  USE CASES                                                                   │
│  Questions answered with Metix AI Platform data, each with its queries       │
│  and what they cost to run.                                                  │
│                                                                              │
│  Type [All 7] [Study 3] [Snapshot 2] [Recipe 1] [Agent 1]                    │
│  Data [People] [Jobs] [Companies]                  7 use cases   Newest  v   │
│  ────────────────────────────────────────────────────────────────────────    │
│  STUDY · PEOPLE · JOBS · COMPANIES                              2026-09-18   │
│  <Title that states the finding, up to 90 characters>                        │
│  <Dek: scope, population, period>                                            │
│  N queries · N results · N Credits                                  Read ->  │
│  ────────────────────────────────────────────────────────────────────────    │
│  SNAPSHOT · JOBS                                                2026-09-18   │
│  ...                                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

The catalog is a list of full-width rows, not a grid of cards. Titles are sentences and need the width, and a list reads top to bottom in date order. The whole row is one link; the "Read" label only makes that visible.

The filter bar shows a count on every option, computed against the other active filters. An option whose count is 0 is disabled, so a click can never produce an empty list. Filters and sort live in the URL (`?type=study&data=jobs&sort=credits`), so a filtered view can be linked. When any filter is active, a "Clear filters" link appears next to the result count. Sort options: Newest (default) and Fewest Credits.

Without JavaScript, the filter bar stays hidden and every row shows.

### Case page, 1440 px

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [header]                                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  STUDY · 2026-09-18                                                          │
│  <Title that states the finding>                                             │
│  <Dek>                                                                       │
│  [People] [Jobs] [Companies]   REST   N Credits to rerun   View on GitHub -> │
│  ────────────────────────────────────────────────────────────────────────    │
│  <key number>          <key number>          <key number>                    │
│  metric, scope, date   metric, scope, date   metric, scope, date             │
│  ────────────────────────────────────────────────────────────────────────    │
│ 01 Question │  01  <Section heading>                                         │
│ 02 Supply   │  <Paragraph that states the finding>                           │
│ 03 Demand   │  ┌──────────────────────────────────────────┐                  │
│ 04 Flow     │  │ <Figure heading>                         │                  │
│ ...         │  │ chart, directly labeled                  │                  │
│ (sticky,    │  └──────────────────────────────────────────┘                  │
│  >= 1200px) │  Source: Metix AI index, profiles, 2026-09-18  [> Query, N Cr] │
│             │  ...                                                           │
│             │  Method and limits      (rendered from the case README.md)     │
│             │  Rerun this case        (receipt + commands)                   │
│             │  Related use cases      (two catalog rows)                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Metix AI Platform · Docs · API keys · Public data policy · OpenJobs AI Inc.  │
└──────────────────────────────────────────────────────────────────────────────┘
```

Studies get a sticky section index in the left margin at 1200 px and wider, highlighting the section in view. Below 1200 px it disappears and the mono section numbers in the headings carry the structure. Snapshots, recipes, and agent sessions have no index; they are short enough to scroll.

Recipes replace the figures with numbered steps, each a command or code block followed by the shape of its output. Agent sessions show the prompt, then each call the agent made as a query block, then the answer.

### 375 px

The header collapses to the mark, and one menu button that opens the same links plus Get an API key. Filter groups scroll sideways in one row each. Key numbers stack. Figures fit the column; a matrix or flow diagram that cannot shrink sits in a horizontally scrolling box with a minimum width and a "Scroll for the full chart" label above it.

## Signature element: the receipt

Every number on the site shows what it cost to produce. That is the Platform's own promise ("The limits are published, not discovered") made visible on the page, and it is the one thing a reader will remember about these pages.

It appears at three sizes, from the same data:

- On a catalog row: one mono line, `N queries · N results · N Credits`.
- Under each chart: a disclosure, `Query · N Credits`. Opening it shows the Query Spec JSON, a Copy button, and the rerun command for that query.
- At the end of a case: the full receipt from `data/receipt.json`, with the run date, calls, results, records, and Credits, plus the commands to rerun the whole case and a link to pricing.

The disclosure is a native `<details>` element, so it works with keyboard and screen readers and without JavaScript. The Copy button is an enhancement: it reads "Copy", changes to "Copied" for 1.5 seconds on success, and on failure selects the JSON and reads "Press Cmd+C" (or "Ctrl+C").

## Charts

Charts render as SVG at build time from committed aggregate files. They never read raw records and never recompute a number the aggregate file does not contain.

Label directly. Put values and category names on the bars or line ends; use a legend only when direct labels do not fit. Color is never the only way to tell series apart.

Default to focus: one series in accent ink, everything else in grey. Use several hues only when the categories themselves are the point.

Candidate palette, taken from the brand colors and to be checked for contrast and color-vision deficiency before the first chart ships:

| Role | Value |
| --- | --- |
| Series 1, and the focus series | `#07545E` teal ink |
| Series 2 | `#1E79C2` blue |
| Series 3 | `#5B54EF` violet |
| Series 4 | `#100D35` navy |
| Context and "Other" | `#C9CECE` grey |
| Sequential (heatmaps) | `#F4FAFB` to `#07545E`, interpolated in OKLCH |
| Diverging (inflow and outflow) | `#5B54EF`, neutral `#F4F6F6`, `#07545E` |

Blue and violet sit close together for some readers, which is one more reason for direct labels. The light brand tints, sky `#A3E4FF` and periwinkle `#B5B5FF`, fall below 3:1 on white and are used only for bands and backgrounds, never for marks that carry data. `--warn` marks data quality (low coverage, a suppressed cell) and is never a series.

No more than four colored series in one chart; group the rest into "Other" or split into small multiples. No dual axes, no 3D, no pie with more than three slices.

A suppressed cell is drawn as an empty outlined mark labeled `<10`, never as an estimate.

Every chart has a figure heading that states the finding, a source line in the bottom left (`Source: Metix AI index, profiles, 2026-09-18`), and a text alternative that states the same finding.

## Motion

Almost none. Filters apply instantly and rows do not animate into place. Row hover changes the ground to `--accent-subtle` over 120 ms. The query disclosure opens over 150 ms where the browser supports animating to `auto` height, and instantly elsewhere. With `prefers-reduced-motion: reduce`, nothing moves.

## Out of bounds

Grids of identical cards, a centered hero over three feature boxes, gradient text, glass or blur effects, decorative icons, stock illustrations, dark mode, and third-party logos.

## Done means rendered and checked

A page is finished when it has been rendered and looked at, at 1440 and 375 pixels wide, with real content, in these states:

- Catalog: unfiltered, filtered, sorted by Credits, a hand-edited URL that matches nothing, and JavaScript disabled.
- Filter option: default, hover, keyboard focus, selected, disabled.
- Row and link: hover and keyboard focus.
- Query disclosure: closed, open, Copy succeeded, Copy failed.
- Case pages: a snapshot with one chart and a study with ten; a 90-character title; long company names in a bar chart; a chart with suppressed cells; a matrix on a 375 px screen.
- The browser console is empty.
