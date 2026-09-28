import { getCollection } from "astro:content";
import type { APIRoute } from "astro";
import { REPO, href } from "@site/i18n";

/**
 * What an agent reads first: every case with its one-line result and the prompt that
 * produced it, so it can rerun one on its own key. The platform's /llms.txt links here.
 */
export const GET: APIRoute = async ({ site }) => {
  const cases = (await getCollection("cases", (c) => c.data.status === "published")).map((c) => c.data);
  const lines = [
    "# Metix AI Platform Casebook",
    "",
    "> Job-market questions answered by an AI agent on the Metix AI Platform (people, job postings and companies, over REST, MCP or agent skills). Every case publishes its numbers, the queries behind them, what they cost in API Credits, and the prompt that produced it. API Credits are the Metix AI Platform's usage unit and are not interchangeable with the Mira Credits sold on metix.ai.",
    "",
    "Content is CC BY 4.0; code is Apache 2.0. Get a key at https://platform.metix.ai/signup?via=casebook (100 free API Credits).",
    "",
    "## Cases",
    "",
    ...cases.map(
      (c) =>
        `- [${c.title.en}](${new URL(href("en", c.slug), site).href}): ${c.dek.en} Prompt: ${REPO}/blob/main/cases/${c.slug}/PROMPT.md`,
    ),
    "",
  ];
  return new Response(lines.join("\n"), { headers: { "content-type": "text/plain; charset=utf-8" } });
};
