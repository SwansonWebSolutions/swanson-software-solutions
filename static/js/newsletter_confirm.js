document.addEventListener("DOMContentLoaded", () => {
  const flashes = Array.from(document.querySelectorAll(".flash-success"));
  const hasNewsletterSuccess = flashes.some((el) =>
    (el.textContent || "").toLowerCase().includes("subscrib")
  );
  if (!hasNewsletterSuccess) return;

  const targets = [
    ...document.querySelectorAll(".newsletter-card"),
    ...document.querySelectorAll(".footer-newsletter"),
  ];
  targets.forEach((el) => {
    el.classList.add("confirm-anim");
    setTimeout(() => el.classList.remove("confirm-anim"), 1500);
  });
});
