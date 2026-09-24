import type { PromptModule } from "@site/cases";
import type { Lang } from "@site/i18n";

export type PromptStep = { n: number; title: string; body: string };

export type ParsedPrompt = {
  /** The prompt exactly as committed: the one fenced text block in PROMPT.md. */
  raw: string;
  /** Its first paragraph: the question and the access rules. */
  question: string;
  steps: PromptStep[];
  /** The Markdown before the prompt, rendered. */
  intro: string;
  /** The sections after the prompt ("Adapt it", "What to ask before running it"), rendered. */
  sections: { title: string; body: string }[];
};

/**
 * Splits a case's PROMPT.md into the parts the page lays out separately. Fails the build
 * when the prompt breaks the template's contract, so a page can never show a prompt that
 * contradicts it: every step reads "N. Title. Body" ("N. 标题。正文" in Chinese), and the
 * prompt names the Credit ceiling the page promises it stops at.
 */
export async function parsePrompt(prompt: PromptModule, slug: string, lang: Lang, cap?: number): Promise<ParsedPrompt> {
  const file = `cases/${slug}/PROMPT${lang === "zh" ? ".zh" : ""}.md`;
  const raw = prompt.rawContent().match(/```text\n([\s\S]*?)\n```/)?.[1];
  if (!raw) throw new Error(`${file} has no text block`);
  // A ceiling of 1,000 or more is written with a thousands comma, as every number in a prompt is.
  if (cap !== undefined && ![String(cap), cap.toLocaleString("en-US")].some((c) => raw.includes(`${c} Credits`))) {
    throw new Error(`${file} never says it stops at ${cap} Credits, the cap in case.yaml`);
  }
  const [question, ...paragraphs] = raw.split(/\n{2,}/);
  const steps = paragraphs.map((para) => {
    const m = para.match(/^(\d+)\.\s+(.+?)(?:\.\s|。)([\s\S]*)$/);
    if (!m) throw new Error(`${file}: a step does not read "N. Title. Body": ${para.slice(0, 60)}`);
    return { n: Number(m[1]), title: m[2], body: m[3].trim() };
  });
  const html = (await prompt.compiledContent()).replace(/<h1[^>]*>[\s\S]*?<\/h1>/, "");
  const intro = html.slice(0, html.indexOf("<pre"));
  const sections = html
    .slice(html.indexOf("</pre>") + "</pre>".length)
    .split(/(?=<h2[\s>])/)
    .map((part) => part.match(/^<h2[^>]*>([\s\S]*?)<\/h2>([\s\S]*)$/))
    .filter((m): m is RegExpMatchArray => m !== null)
    .map((m) => ({ title: m[1], body: m[2] }));
  return { raw, question, steps, intro, sections };
}
