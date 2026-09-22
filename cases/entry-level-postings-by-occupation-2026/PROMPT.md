# Bootstrap prompt

Paste the prompt below into an agent that can reach the Metix AI Platform: one with the [metix-skills](https://github.com/MetixAI-Official/metix-skills) installed, the MCP server connected, or plain REST access with `METIX_KEY` set. Followed end to end, it costs about 211 to 261 Credits: 126 for the published counts, 75 to 105 to read the audit slices, and 10 to 30 for the counts that size slices and exclude words. It stops and asks before 300. Every published number is a count; the reads only audit the title families.

```text
Answer one question with the Metix AI Platform: among open US job postings, what share of each occupation's postings is open to someone starting out, and is a narrow entry door specific to software and AI roles or shared by occupations that research calls AI-exposed? Work only through the public Platform (REST at https://mira-api.metix.ai, the MCP server, or the metix-skills) with the key in METIX_KEY, and never print the key.

1. Read before querying. Call GET /contract (free) and build every condition from querySpecByEntity.job; read GET /docs/api/jobs (free) too. seniority takes one of seven exact values (Associate, Director, Entry level, Executive, Internship, Mid-Senior level, Not Applicable), is_open is true on every posting in the index, and a total of 100,000 or more comes back as the string "100000+". A query holds at most 64 conditions and nests at most 6 levels. A count with size 1 costs 1 Credit, a search 1 Credit per 25 IDs returned, and a detail read 1 Credit per 5 postings, so plan every published number as a count. Check the balance with GET /auth/key/status (free) at the start and at the end, and stop and ask before the run passes 300 Credits.

2. Population. Open postings (is_open eq true) with location.country eq "United States". Twelve occupation families, each a list of title terms (title match: every word of a term must appear, in any order): AI and machine learning (machine learning, artificial intelligence, AI, ML, LLM, deep learning; exclude data center, data centers); software engineering (software engineer, software developer); data analyst (data analyst; exclude security, prevention); financial analyst (financial analyst, finance analyst); accountant; paralegal and legal assistant (paralegal, legal assistant); graphic designer (graphic designer, graphic design); marketing; customer service (customer service, customer support, customer care; exclude driver); registered nurse (registered nurse, RN); electrician; truck and CDL driver (truck driver, CDL driver). Ahead of them all, take out AI training and annotation work: an AI term together with trainer, tutor, annotator, annotation, or rater. Count each posting once: it belongs to the first family in this order whose terms it matches and whose exclude words it does not match, and a posting that matches exclude words moves on to the families after it. Write the families, their order, and the reason for each exclude word to a file.

3. Audit before counting. Search returns the best-matching titles first, so the top of a search makes a family look cleaner than it is. Read whole slices instead: one family's postings from a single posted_date in a few named states, chosen so the slice holds 10 to 50 postings, every one of them read (POST /entity/v1/jobs/detail-by-id with _source title, seniority, min_experience_months, company.name). Read about 40 titles for the noisy families (AI, software, data analyst, financial analyst, marketing, customer service) and about 20 for the others. Report the on-topic share for each family, name the noise, size every candidate exclude word with a count, and add it only for noise the reads found. Keep the records out of every published file.

4. Two measures. The label door: postings whose seniority is Internship or Entry level, as a share of all the family's postings. seniority is filled on every posting, so it is a label from the source, not a requirement the employer wrote. The requirement door: postings with min_experience_months lte 24 (0 included), as a share of the postings where min_experience_months exists; print that coverage beside every requirement share, because it differs a lot between families. Never define entry level by age.

5. Count. For each family: the total; seniority eq Internship, Entry level, Associate, and Not Applicable, one count each; min_experience_months exists; min_experience_months lte 24; and seniority in [Internship, Entry level] together with each of the last two. Count every total first. When a count comes back "100000+", count the family in disjoint title parts (registered nurse; RN without registered nurse) and add them. Then count four subgroups the audits called for: AI training work (total and label door); AI-family postings that also have a software term; customer service postings whose industries match neither Retail nor Restaurants; registered nurse postings with travel in the title. Take the rest of each family by subtraction.

6. Clean. Counts are postings, not openings: an employer posting one job in several places counts once per posting, so report how many audited postings repeat the title and employer of another in the same slice. A posting without min_experience_months is outside the requirement measure, never a zero.

7. Compare. Split the postings that state a requirement by both measures (labelled entry and asking 24 months or less; labelled entry and asking more; not labelled entry and asking 24 or less; neither) and report where the two disagree. Report the share of the label door that is labelled Internship. For AI exposure, cite Brynjolfsson, Chandar, and Chen, "Canaries in the Coal Mine? Six Facts about the Recent Employment Effects of Artificial Intelligence" (Stanford Digital Economy Lab), and attach only the quintile its Online Appendix Tables A.2 to A.6 give the matching occupation; a family whose occupation those tables do not list gets none, and no family gets a score.

8. Outputs. Write families.json and subgroups.json with "unit": "jobs", the snapshot date, and the query files they came from. Publish a share only when its denominator is at least 30. The records read for the audits stay private.

9. Charts. The label door by family, sorted, with each family's exposure quintile marked; the requirement door beside it, with its coverage; the four-way split of postings that state a requirement; the internship share of the door; AI-titled against other software titles; travel against other nursing postings. Draw shares on an axis from 0 to 100%, label the bars directly, and give each chart a title that states its finding in neutral words.

10. Limits. One day of open postings, not a trend: the data cannot say whether the door narrowed. Postings are demand, not hires, and a label or a stated requirement is what the posting says, not who is hired. The title families approximate the paper's occupations and hold jobs at every level. Requirement coverage differs by family. Say how far travel nursing and store counter jobs shape the nurse and customer service figures.
```

## Adapt it

| To change | Edit | For example |
| --- | --- | --- |
| The occupations | Step 2, and audit every new family in step 3 | Pharmacist, teacher, or web developer titles |
| What counts as the door | Step 4 | 12 months or less, or the Associate label as well |
| The country | location.country in step 2 | United Kingdom, with its own title words |
| The Credit ceiling | Steps 1 and 3 | Skip the audit reads to stay near 126 Credits |

## What to ask before running it

When someone brings a looser version of this question, settle these first. Each one changes the query or the cost:

1. Which occupations, and which title words stand for each?
2. What counts as open to someone starting out: the source's label, the stated requirement, or both?
3. Which country?
4. How many Credits may the audits spend on reads?
