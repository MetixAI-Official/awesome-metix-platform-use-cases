import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const bilingual = z.object({ en: z.string().min(1), zh: z.string().min(1) }).strict();

const cases = defineCollection({
  // One entry per cases/<slug>/case.yaml; the template folder starts with _ and is skipped.
  loader: glob({
    base: "../cases",
    pattern: "[!_]*/case.yaml",
    generateId: ({ entry }) => entry.split("/")[0],
  }),
  schema: z
    .object({
      slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
      type: z.enum(["study", "snapshot", "recipe", "agent"]),
      status: z.enum(["planned", "draft", "published"]),
      title: bilingual,
      dek: bilingual,
      datasets: z.array(z.enum(["people", "jobs", "companies"])).min(1),
      integration: z.array(z.enum(["rest", "mcp", "skills"])).min(1),
      topics: z.array(z.string()),
      regions: z.array(z.string()).min(1),
      snapshot: z.coerce.date().optional(),
      published: z.coerce.date().optional(),
      exploration_credits: z.number().int().nonnegative().optional(),
      // Up to three figures shown on the catalog row, copied from the case's aggregates.
      highlights: z
        .array(z.object({ value: z.string().min(1), label: bilingual }).strict())
        .max(3)
        .optional(),
    })
    .strict()
    .refine((c) => c.status !== "published" || (c.snapshot && c.published), {
      message: "a published case needs snapshot and published dates",
    }),
});

export const collections = { cases };
