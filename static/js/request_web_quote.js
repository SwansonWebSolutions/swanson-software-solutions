(function () {
  "use strict";

  const form = document.querySelector(".quote-form");
  if (!form) return;

  const steps = Array.from(document.querySelectorAll("[data-step]"));
  const progress = document.querySelector(".quote-progress");
  const progressFill = document.querySelector("[data-progress-fill]");
  const progressLabel = document.querySelector("[data-progress-label]");
  const nextButton = document.querySelector("[data-next]");
  const backButton = document.querySelector("[data-prev]");
  const submitButton = document.querySelector("[data-submit]");
  let currentStep = 1;

  function updateConditionalFields() {
    const goal = form.querySelector('input[name="primary_goal"]:checked');
    const otherFeature = form.querySelector('input[name="features"][value="other"]:checked');
    const goalOther = form.querySelector('[data-show-for="primary_goal"]');
    const featureOther = form.querySelector('[data-show-for="features"]');
    goalOther.hidden = !goal || goal.value !== "other";
    featureOther.hidden = !otherFeature;
    goalOther.querySelector("textarea").required = !goalOther.hidden;
    featureOther.querySelector("textarea").required = !featureOther.hidden;
  }

  function validateStep() {
    const active = steps.find(function (step) { return Number(step.dataset.step) === currentStep; });
    const fields = Array.from(active.querySelectorAll("input, select, textarea")).filter(function (field) {
      return !field.disabled && field.type !== "hidden";
    });
    for (const field of fields) {
      if (!field.checkValidity()) {
        field.reportValidity();
        return false;
      }
    }
    return true;
  }

  function showStep(stepNumber) {
    currentStep = Math.min(Math.max(stepNumber, 1), steps.length);
    steps.forEach(function (step) {
      step.hidden = Number(step.dataset.step) !== currentStep;
      step.classList.toggle("is-active", Number(step.dataset.step) === currentStep);
    });
    progressFill.style.width = ((currentStep / steps.length) * 100) + "%";
    progressLabel.textContent = "Step " + currentStep + " of " + steps.length;
    progress.setAttribute("aria-valuenow", String(currentStep));
    backButton.hidden = currentStep === 1;
    nextButton.hidden = currentStep >= steps.length;
    submitButton.hidden = currentStep !== steps.length;
    window.scrollTo({ top: form.closest(".quote-content").offsetTop - 24, behavior: "smooth" });
  }

  form.addEventListener("change", function (event) {
    if (event.target.name === "maintenance") {
      const maintenanceInputs = Array.from(form.querySelectorAll('input[name="maintenance"]'));
      if (event.target.value === "none" && event.target.checked) {
        maintenanceInputs.forEach(function (input) { if (input.value !== "none") input.checked = false; });
      } else if (event.target.value !== "none" && event.target.checked) {
        const noneInput = form.querySelector('input[name="maintenance"][value="none"]');
        if (noneInput) noneInput.checked = false;
      }
    }
    updateConditionalFields();
  });
  nextButton.addEventListener("click", function () {
    if (currentStep < steps.length && validateStep()) showStep(currentStep + 1);
  });
  backButton.addEventListener("click", function () {
    if (currentStep > 1) showStep(currentStep - 1);
  });

  updateConditionalFields();
  showStep(1);
})();
