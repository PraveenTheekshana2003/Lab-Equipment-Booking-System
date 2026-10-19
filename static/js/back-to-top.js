(function () {
  const btn = document.getElementById("back-to-top");
  if (!btn) return;

  const toggle = () => {
    if (window.scrollY > 320) {
      btn.classList.add("is-visible");
    } else {
      btn.classList.remove("is-visible");
    }
  };

  window.addEventListener("scroll", toggle, { passive: true });
  toggle(); // run once on load

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();