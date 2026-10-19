(function () {
  const cards = document.querySelectorAll(".reveal");
  if (!cards.length) return;

  // Stagger delay per card (ms)
  cards.forEach(function (card, index) {
    card.style.setProperty("--reveal-delay", (index % 6) * 80 + "ms");
  });

  if (!("IntersectionObserver" in window)) {
    cards.forEach(function (card) {
      card.classList.add("is-visible");
    });
    return;
  }

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      root: null,
      rootMargin: "0px 0px -40px 0px",
      threshold: 0.12,
    }
  );

  cards.forEach(function (card) {
    observer.observe(card);
  });
})();