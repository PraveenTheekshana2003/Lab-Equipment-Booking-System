/**
 * Auth page tab switching (Login / Register)
 */
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".auth-tabs button");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (!tabs.length) return;

  function showTab(name) {
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
    if (loginForm) loginForm.style.display = name === "login" ? "block" : "none";
    if (registerForm) registerForm.style.display = name === "register" ? "block" : "none";
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => showTab(btn.dataset.tab));
  });

  // Honour server-side active tab
  const initial = document.body.dataset.activeTab || "login";
  showTab(initial);
});