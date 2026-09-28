/**
 * The platform's top bar and footer, as data.
 *
 * The Casebook is served at platform.metix.ai/casebook, so its pages carry the
 * platform's own bar and footer. They are not written here: shell/shell.json is a
 * snapshot of platform.metix.ai/brand/shell.json, refreshed by tools/sync-shell.mjs,
 * and CI fails when it falls behind. The build never reads the network.
 */
import shell from "./shell/shell.json";

export type NavItem = { href: string; label: string; badge?: string; document?: boolean };
export type FooterLink = { label: string; href: string; external?: boolean; document?: boolean };
export type RailItem = { label: string; value: number; unit?: string; decimals?: number; note?: string };

export const NAV = shell.nav as NavItem[];
export const FOOTER = shell.footer as {
  columns: { title: string; links: FooterLink[] }[];
  tagline: string;
  address: string[];
  legal: FooterLink[];
  copyright: string;
  rail: RailItem[];
  apiVersion: string;
};
export const LAYOUT = shell.layout;

/** The platform's tokens as CSS custom properties, `--pf-<name>`, for one :root rule. */
export function shellTokensCss(): string {
  const kebab = (name: string) => name.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`);
  const vars = Object.entries(shell.tokens).map(([name, value]) => `--pf-${kebab(name)}:${value}`);
  vars.push(`--pf-page:${LAYOUT.page}px`, `--pf-gutter:${LAYOUT.gutter}px`, `--pf-gutter-wide:${LAYOUT.gutterWide}px`);
  return `:root{${vars.join(";")}}`;
}

/** Sign-ups from the Casebook say so, like every other entry point. */
export const SIGNUP = "/signup?via=casebook";
export const SIGNIN = "/signin";
