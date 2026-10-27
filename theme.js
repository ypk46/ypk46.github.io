// Theme toggle. Each page's <head> applies a saved choice before first paint; with no saved choice the
// page follows the system setting. The button only shows when the <head> script has added .js.
const toggle = document.querySelector(".theme-toggle");
const systemDark = matchMedia("(prefers-color-scheme: dark)");
const root = document.documentElement;

const isDark = () => (root.dataset.theme ? root.dataset.theme === "dark" : systemDark.matches);
const sync = () => toggle.setAttribute("aria-pressed", String(isDark()));

if (toggle) {
  sync();
  systemDark.addEventListener("change", sync);
  toggle.addEventListener("click", () => {
    const theme = isDark() ? "light" : "dark";
    root.dataset.theme = theme;
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // Storage blocked: the choice lasts until the page is left.
    }
    sync();
  });
}
