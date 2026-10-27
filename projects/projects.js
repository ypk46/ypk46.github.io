// Project filters: progressive enhancement. Without JavaScript the chips stay hidden and every card shows.
const filters = document.querySelector(".filters");
const cards = document.querySelectorAll(".project-card[data-category]");

filters.hidden = false;
filters.addEventListener("click", (event) => {
  const chip = event.target.closest("button[data-filter]");
  if (!chip) return;
  const filter = chip.dataset.filter;
  for (const button of filters.querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button === chip));
  }
  for (const card of cards) {
    card.hidden = filter !== "all" && card.dataset.category !== filter;
  }
});
