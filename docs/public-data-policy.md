# Public data policy

This repository is public. Everything pushed to it is published: GitHub, forks, clones, search engines, and archive services keep it after it is deleted, and a later commit that removes a file does not unpublish the earlier one. The same applies to branches, pull requests, issues, Actions logs, and the GitHub Pages site. A case marked `status: draft` is excluded from the site build, but its files are exactly as public as any other file once they are pushed.

So the rule is simple: if it should not be on the open web, it never reaches `git push`. Work that has not passed the checks below stays on the machine that produced it.

This page lists what may be published, what may not, and how the repository enforces it. When a case needs something this page does not cover, ask before publishing, and extend this page in the same pull request.

## Where the data may come from

Only from the public Metix AI Platform, through the REST API, the MCP server, or the metix-skills, with a normal Platform key. No case uses an internal database, export, or pipeline, and no case describes one. A number that someone with a key cannot reproduce does not belong here.

Prompts in `PROMPT.md` are published like everything else: they name public endpoints and fields only, and never contain a key, an internal term, or a customer.

## What may be published

Aggregates computed from the Metix AI Platform, provided they meet the small-cell rule below: counts, shares, medians, rankings, and flows between groups.

Query Spec trees, the JSON that each chart or table was computed from, so that anyone with a key can rerun it. A query must describe a population, never an individual.

Company names, used to refer to the company and nothing more. Counts attached to a company describe what is visible through the Metix AI Platform, not the company's headcount (see "Wording" below).

Facts from job postings, in aggregate: posting counts, locations, titles grouped into families, and salary ranges stated in the postings.

The run record for each case: when the queries ran, how many calls, results, and records they used, and how many Credits they cost.

Links to public sources (news articles, company pages, research trackers), attributed to their publisher.

## What never goes in

### Secrets

API keys (`METIX_KEY`, either key prefix), tokens, passwords, private keys, cookies, signed URLs, and `.env` files. `.env.example` holds the only placeholder key allowed in the tree.

### Data about individual people

No person is identifiable from anything in this repository. That excludes:

- names, including masked, blurred, abbreviated, or encoded names (base64, hashes, initials). A public repository cannot gate anything: an encoded name in page source is a published name.
- profile URLs, photos, email addresses, phone numbers, and street addresses.
- person ids returned by Search or Detail. They are encrypted, but anyone with a key can resolve them into a record.
- exact combinations of title, employer, location, and dates that point to one person, and quotes from profile text.
- record-level exports of any kind: CSV, JSON, parquet, notebooks with outputs, screenshots of records.

Raw records a case needs while it is being computed stay in `cases/<slug>/data/raw/`, which git ignores, and never leave that machine.

### Sensitive attributes and their proxies

No case infers or reports ethnicity, race, national origin, religion, gender, age, health, disability, or immigration and visa status, and no case uses a proxy for them. Names and spoken languages are proxies for national origin and are never used to classify people.

Where a study is about geography of education or work, it uses the stated location of an institution or employer and says so. The China-educated study defines its population by the country or region of the undergraduate institution, and by nothing else.

### Internal information

This repository describes the Metix AI Platform as a customer sees it. It does not describe how the Platform is built or run. That excludes:

- hostnames, IP addresses, and URLs that are not published on metix.ai or platform.metix.ai.
- names of internal services, pipelines, databases, tables, buckets, repositories, and fields that are not part of the public API contract (`GET /contract`).
- names of customers, prospects, trials, or deals, and any note on why a study was commissioned or who it was for.
- internal prices, costs, margins, coverage figures, or roadmap items that metix.ai does not publish.
- names and addresses of the people who build the Platform. The contact for this repository is `support@metix.ai`.
- local file paths, machine names, and agent or editor scratch files.

Because this page is itself public, it names these categories and never the internal terms. The concrete list of internal terms lives outside the repository (see "Enforcement").

## The small-cell rule

Any number derived from people (profiles, career moves, education) is published only when the group it counts has at least 10 people.

A cell from 1 to 9 is published as the string `"<10"`, never as the exact number, never as a share, and never inside a chart that lets a reader recover it (a bar length, a Sankey edge width, a tooltip). A zero may be published.

When a suppressed cell could be recovered by subtracting published cells from a published total, withhold that total or suppress a second cell of 10 or more in the same row or column. Merging the small groups into "Other" does not help while the total is published: the total minus the other cells still gives the merged cell back.

Differences are cells too. A group total minus its parts (people with no Bachelor entry, people whose job started earlier, people outside the US) is a count of people, and so is the overlap between rows that can share a person: the sum of the rows minus their union. Make rows that can overlap disjoint (count each person at the first row in a fixed order), so a total is simply the sum of its rows, and check every difference a reader can form before publishing.

A share or percentage is published only when its denominator is at least 30.

A salary statistic is published only when it rests on at least 10 postings that state a salary, and it is described as the posted range, not as pay.

Counts of job postings and of companies are not about people and carry no minimum.

The checker enforces the 1 to 9 rule on every aggregate file whose `unit` is `profiles` (see `docs/framework.md` for the file shape). It cannot see differences between cells, so the recovery rule and the share rule need a human reviewer, or a check in the case's own script before it writes anything: `cases/china-educated-ai-talent-2026/fetch.py` stops when any difference of published cells is between 1 and 9.

## Named people and public events

A case never names an individual from Metix AI Platform data.

A case may refer to a public event involving a person, such as an executive hire reported by the press, only by linking to the publisher and attributing the claim to it. Describe the role rather than the name wherever the point survives without it ("a post-training lead moved from one lab to another, according to Bloomberg"). A case never adds Metix AI Platform data about that person, never places them in a chart, and never infers anything about them.

## Wording

A count of profiles is "visible through the Metix AI Platform" and never a company's headcount. It is usually a lower bound, since many people have no visible profile, but profiles left out of date count as current; where a case finds more current profiles than a company's reported headcount, it says a count is neither a headcount nor a guaranteed floor. "412 visible profiles in inference roles at the company as of 2026-09-18" is right. "The company has 412 inference engineers" is wrong.

Job counts describe demand and profile counts describe supply. A chart never mixes the two under one label.

Every number states its metric, its scope, and its snapshot date, in the text or in the chart caption. A bare `n = 412` is not enough.

Use neutral verbs for career moves: move, join, leave, return, hire. Never poach, defect, hunt, drain, raid, steal, or war metaphors, and never language that treats a person's origin as a question of loyalty.

Claims about a company's intent ("is cutting", "is pivoting to") need a public source. Otherwise, describe what the data shows ("the share of postings in sales roles rose from 31% to 44%").

## Brand and third parties

Write the product as Metix AI Platform, in full, on every page and in both languages. This repository belongs to the Platform, not to the main site, so it refers to the main site by its domain, metix.ai. The legal entity is OpenJobs AI Inc., in the copyright line only. The full rules are in `docs/style.md` and on [brand.metix.ai](https://brand.metix.ai).

Third-party names are used only to refer to those companies. No third-party logos, and no wording that suggests a company endorses, partners with, or supplied data to this repository.

## Enforcement

### Automated check

`scripts/check_public.py` scans every tracked and untracked (not ignored) file, or only the staged content with `--staged`. It fails on:

- API keys and common credential formats.
- email addresses other than `support@metix.ai` and placeholder domains.
- phone numbers, profile URLs, local home-directory paths, and private IP addresses.
- person-level fields (names, profile URLs, contact fields, person ids) in files under `cases/*/data/`.
- cells from 1 to 9 in aggregate files whose `unit` is `profiles`.
- the product name written any way other than Metix AI Platform, and em or en dashes in prose.
- any term from the private denylist.

It prints the file, line, and rule for each finding and never prints the matched text, because Actions logs on a public repository are public too.

The checker reads one line at a time and matches literal text. A value split across lines or assembled from pieces in code (the checker's own tests build their fake secrets that way) passes it. A clean run means no known pattern appeared, not that nothing leaked, which is why review still reads code and query files.

A line that trips a rule for a documented reason can carry an inline allowance, for example `<!-- check-public: allow brand -->` in Markdown or `# check-public: allow email` in code. Every allowance names one rule, and review looks at each one.

### Private denylist

Internal terms are loaded from `PUBLIC_CHECK_DENYLIST` (one term per line, set as an Actions secret) and from `.public-denylist` in the repository root (ignored by git, for local runs). Neither is ever committed. Pull requests from forks run without the denylist, which is why a maintainer reviews them before merge.

### Where it runs

- locally before each commit, through a `pre-commit` hook that runs `python3 scripts/check_public.py --staged`. This is the check that sees every commit.
- in CI on every push and pull request (`.github/workflows/public-check.yml`). CI checks the files at the tip of the push, so a secret added in one commit and deleted in the next passes CI while staying in history. That is why the hook matters, and why a key that ever reached a commit gets revoked.

### Human review before `status: published`

The checker catches patterns. A reviewer other than the author checks meaning:

1. Every number traces to a committed aggregate file and the query that produced it.
2. No suppressed cell can be recovered from totals, charts, or neighboring tables.
3. No chart, sentence, example, or query in `queries/` narrows to one person. The checker does not read query files for this.
4. Definitions of sensitive populations use institution or employer location only.
5. Company-level wording says visible profiles and never a headcount (a lower bound only where nothing can inflate it), and intent claims have a source.
6. Nothing describes internal systems, customers, or why the study exists.
7. On the rendered page, in both languages, the product reads Metix AI Platform everywhere, including uppercase labels. The checker reads source text and cannot see a CSS `text-transform`.

## If something leaks

A key: revoke it at [platform.metix.ai/api-keys](https://platform.metix.ai/api-keys) first, then remove it from the tree. Revocation is the fix; history rewriting is optional once the key is dead.

Personal data or internal information: remove it from the tree in a new commit at once and tell the repository owner. Purging it from history needs a force push and a GitHub support request to clear cached views. The owner makes that call, not the contributor who found it.
