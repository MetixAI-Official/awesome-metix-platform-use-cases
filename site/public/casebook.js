// The Casebook's only script. It is a file, not inline, so the page can run under a
// policy that allows no inline script at all (see docs/style.md, "Same origin as the
// console"). It reads and writes one storage key, AGENT_KEY, and nothing else: the
// platform's login tokens live in localStorage on this same origin, and CI fails a
// build that reaches for any other key, for cookies, or for sessionStorage.

const AGENT_KEY = "casebook:agent";

// Copy buttons: data-copy holds a selector inside the nearest [data-copy-root].
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-copy]");
  if (!button) return;
  const root = button.closest("[data-copy-root]");
  const source = root && root.querySelector(button.dataset.copy);
  if (!source) return;
  const label = button.dataset.label || button.textContent;
  button.dataset.label = label;
  try {
    // innerText keeps the line breaks between the per-line spans of a code block.
    await navigator.clipboard.writeText((source.innerText || source.textContent).trim());
    button.textContent = button.dataset.done;
  } catch {
    // The clipboard can be blocked, and the prompt's source is hidden, so selecting
    // it would copy nothing. Show the text in a box, selected, next to the button.
    const anchor = button.closest(".code-block, .rs-head, .prompt-foot") || button.parentElement;
    let box = anchor.nextElementSibling;
    if (!box || !box.classList.contains("copy-fallback")) {
      box = document.createElement("textarea");
      box.className = "copy-fallback";
      box.readOnly = true;
      anchor.insertAdjacentElement("afterend", box);
    }
    box.value = (source.innerText || source.textContent).trim();
    box.focus();
    box.select();
    const mac = /Mac|iPhone|iPad/.test(navigator.userAgent);
    button.textContent = button.dataset.fail.replace("Ctrl+C", mac ? "Cmd+C" : "Ctrl+C");
    clearTimeout(button._reset);
    button._reset = setTimeout(() => (button.textContent = label), 6000);
    return;
  }
  clearTimeout(button._reset);
  button._reset = setTimeout(() => (button.textContent = label), 1500);
});

// Run it: the paths are links to their panels; with JavaScript one panel shows at a
// time. A hash naming a panel, or anything inside one (#prompt, #step-3), opens it.
// A panel is hidden when the browser looks for the hash, so scroll once it shows.
const runRoots = [...document.querySelectorAll("[data-run]")];
const hashTarget = () => location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
const scrollToHash = () => {
  const target = hashTarget();
  if (target && target.closest("[data-run], [data-steps]")) requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
};
// Below the rail breakpoint the paths sit above the panels, so a choice would swap
// content out of sight; bring the panel's heading up.
const stacked = window.matchMedia("(max-width: 959px)");
const showRunPath = (root, key) => {
  for (const panel of root.querySelectorAll("[data-panel]")) panel.hidden = panel.dataset.panel !== key;
  for (const link of root.querySelectorAll("[data-path]")) link.setAttribute("aria-current", String(link.dataset.path === key));
};
const runFromHash = () => {
  for (const root of runRoots) {
    const target = hashTarget();
    const panel = target && root.contains(target) && target.closest("[data-panel]");
    showRunPath(root, panel ? panel.dataset.panel : root.querySelector("[data-path]").dataset.path);
  }
};
for (const root of runRoots) {
  for (const link of root.querySelectorAll("[data-path]")) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showRunPath(root, link.dataset.path);
      history.replaceState(null, "", `#run-${link.dataset.path}`);
      if (stacked.matches) document.getElementById(`run-${link.dataset.path}`)?.scrollIntoView({ block: "start" });
    });
  }
}
runFromHash();

// Agent tabs: arrow keys, Home and End move between them, and the choice carries
// across pages however it was made.
let savedAgent = null;
try {
  savedAgent = localStorage.getItem(AGENT_KEY);
} catch {}
for (const box of document.querySelectorAll("[data-agent-setup]")) {
  const tabs = [...box.querySelectorAll('[role="tab"]')];
  const select = (key, byUser) => {
    for (const tab of tabs) {
      const on = tab.dataset.agent === key;
      tab.setAttribute("aria-selected", String(on));
      tab.tabIndex = on ? 0 : -1;
      if (on && byUser) tab.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
    for (const panel of box.querySelectorAll("[data-agent-panel]")) panel.hidden = panel.dataset.agentPanel !== key;
    if (!byUser) return;
    try {
      localStorage.setItem(AGENT_KEY, key);
    } catch {}
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => select(tab.dataset.agent, true));
    tab.addEventListener("keydown", (event) => {
      const to = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[event.key];
      if (to === undefined) return;
      event.preventDefault();
      const next = tabs[(to + tabs.length) % tabs.length];
      select(next.dataset.agent, true);
      next.focus();
    });
  });
  select(tabs.some((tab) => tab.dataset.agent === savedAgent) ? savedAgent : tabs[0].dataset.agent);
}
// A reader who has chosen an agent before has done the setup; fold it away for them.
if (savedAgent) for (const fold of document.querySelectorAll("[data-setup-once]")) fold.open = false;

// Expand all / Collapse all: the label follows the folds, including ones opened by hand.
for (const button of document.querySelectorAll("[data-fold-toggle]")) {
  const list = document.getElementById(button.getAttribute("aria-controls"));
  if (!list) continue;
  const folds = () => [...list.querySelectorAll("details")];
  const sync = () => {
    const all = folds().every((d) => d.open);
    button.textContent = all ? button.dataset.collapse : button.dataset.expand;
    button.setAttribute("aria-expanded", String(all));
  };
  button.addEventListener("click", () => {
    const open = !folds().every((d) => d.open);
    for (const d of folds()) d.open = open;
    sync();
  });
  list.addEventListener("toggle", sync, true);
}

// A link to a folded step (#step-3) opens it.
const openTarget = () => {
  const target = hashTarget();
  const fold = target && target.id.startsWith("step-") && target.querySelector("details");
  if (fold) fold.open = true;
  const setup = target && target.closest("[data-setup-once]");
  if (setup) setup.open = true;
};
openTarget();
scrollToHash();
window.addEventListener("hashchange", () => {
  runFromHash();
  openTarget();
  scrollToHash();
});


// The top bar's menu sheet, below 1024px. Tap, Escape, the scrim, or a wider window
// close it; focus goes in on open and back to the button on close.
const menuButton = document.querySelector("[data-pf-menu]");
const sheet = document.querySelector("[data-pf-sheet]");
if (menuButton && sheet) {
  const label = menuButton.querySelector("[data-pf-menu-label]");
  let closing = 0;
  const setOpen = (open) => {
    menuButton.setAttribute("aria-expanded", String(open));
    if (label) label.textContent = open ? label.dataset.close : label.dataset.open;
    clearTimeout(closing);
    if (open) {
      sheet.hidden = false;
      document.body.style.overflow = "hidden";
      requestAnimationFrame(() => requestAnimationFrame(() => sheet.setAttribute("data-shown", "")));
      sheet.querySelector("a[href]")?.focus();
    } else {
      sheet.removeAttribute("data-shown");
      document.body.style.overflow = "";
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      closing = setTimeout(() => (sheet.hidden = true), reduced ? 0 : 260);
    }
  };
  const isOpen = () => menuButton.getAttribute("aria-expanded") === "true";
  menuButton.addEventListener("click", () => setOpen(!isOpen()));
  sheet.querySelector("[data-pf-scrim]")?.addEventListener("click", () => setOpen(false));
  document.addEventListener("keydown", (event) => {
    if (!isOpen()) return;
    if (event.key === "Escape") {
      setOpen(false);
      menuButton.focus();
      return;
    }
    // The sheet is modal: Tab cycles through the sheet and the close button only.
    if (event.key !== "Tab") return;
    const stops = [menuButton, ...sheet.querySelectorAll("a[href]")];
    const at = stops.indexOf(document.activeElement);
    const next = event.shiftKey ? (at <= 0 ? stops.length - 1 : at - 1) : at === stops.length - 1 || at === -1 ? 0 : at + 1;
    event.preventDefault();
    stops[next].focus();
  });
  window.addEventListener("resize", () => {
    if (isOpen() && window.innerWidth >= 1024) setOpen(false);
  });
}

// Footer columns fold on a phone, as on the platform.
for (const column of document.querySelectorAll("[data-pf-col]")) {
  const head = column.querySelector("button");
  head?.addEventListener("click", () => {
    const open = !column.hasAttribute("data-open");
    column.toggleAttribute("data-open", open);
    head.setAttribute("aria-expanded", String(open));
  });
}
