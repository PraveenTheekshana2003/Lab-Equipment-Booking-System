(function () {
  const root = document.documentElement;
  const btn = document.getElementById("theme-toggle");
  const key = "labspace-theme";

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(key, theme);
  }

  function toggleTheme() {
    const current = root.getAttribute("data-theme") || "dark";
    setTheme(current === "dark" ? "light" : "dark");
  }

  const saved = localStorage.getItem(key);
  if (saved === "light" || saved === "dark") {
    setTheme(saved);
  }

  if (btn) {
    btn.addEventListener("click", toggleTheme);
  }
})();