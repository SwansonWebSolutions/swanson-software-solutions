/*  SwanTech — Embedded pricing calculator (service pages)
    Reads all pricing data from PRICING_CONFIG below. Update prices,
    features, and add-ons here only — rendering/calculation logic
    reads entirely from this object.
*/
(function () {
  "use strict";

  const PRICING_CONFIG = {
    products: [
      {
        id: "shopify",
        name: "eCommerce Store (Shopify)",
        basePrice: 1000,
        includedFeatures: [
          "Theme customization",
          "Mobile-responsive design",
          "Up to 10 pages",
          "Collaborative copywriting",
          "Up to 10 product uploads",
          "Basic navigation setup",
          "Payment gateway setup",
          "Basic shipping setup",
          "Technical SEO setup",
          "Social media integration",
          "Contact form",
          "Newsletter signup"
        ],
        addOns: [
          { id: "pages", label: "Additional pages", priceType: "perUnit", inputType: "quantity", price: 40, unitLabel: "page" },
          { id: "products", label: "Additional product uploads", priceType: "perUnit", inputType: "quantity", price: 5, unitLabel: "product" },
          { id: "banners", label: "Custom banners / graphics", priceType: "perUnit", inputType: "quantity", price: 30, unitLabel: "image" },
          { id: "logo", label: "Logo design (6 sizes)", priceType: "flat", inputType: "toggle", price: 200 },
          { id: "blog", label: "Blog setup", priceType: "flat", inputType: "toggle", price: 150 },
          { id: "ga", label: "Google Analytics setup", priceType: "flat", inputType: "toggle", price: 75 },
          { id: "maintenance", label: "Maintenance plan", priceType: "flat", inputType: "toggle", price: 50, recurring: true, unitLabel: "month" }
        ]
      },
      {
        id: "wix",
        name: "Business Website (Wix)",
        basePrice: 1000,
        includedFeatures: [
          "Wix platform setup",
          "Theme customization",
          "Mobile-responsive design",
          "Up to 10 pages",
          "Collaborative copywriting",
          "Basic navigation setup",
          "Contact form integration",
          "Social media integration",
          "Newsletter signup",
          "Basic booking / contact system",
          "Technical SEO setup",
          "Up to 3 rounds of revisions"
        ],
        addOns: [
          { id: "pages", label: "Additional pages", priceType: "perUnit", inputType: "quantity", price: 40, unitLabel: "page" },
          { id: "products", label: "Additional product uploads", priceType: "perUnit", inputType: "quantity", price: 5, unitLabel: "product" },
          { id: "banners", label: "Custom banners / graphics", priceType: "perUnit", inputType: "quantity", price: 30, unitLabel: "image" },
          { id: "logo", label: "Logo design (6 sizes)", priceType: "flat", inputType: "toggle", price: 200 },
          { id: "blog", label: "Blog setup", priceType: "flat", inputType: "toggle", price: 150 },
          { id: "ga", label: "Google Analytics setup", priceType: "flat", inputType: "toggle", price: 75 },
          { id: "maintenance", label: "Maintenance plan", priceType: "flat", inputType: "toggle", price: 50, recurring: true, unitLabel: "month" }
        ]
      },
      {
        id: "custom",
        name: "Custom Web Solutions / SaaS Development",
        basePrice: 8000,
        note: "Hosting is billed monthly directly by your host provider and is separate from this estimate.",
        includedFeatures: [
          "Discovery & planning session",
          "Custom UI/UX design",
          "Mobile-responsive development",
          "Authentication & login system",
          "Admin dashboard",
          "Database setup",
          "API integrations",
          "Contact forms & lead capture",
          "Payment gateway integration",
          "Email notifications",
          "Technical SEO setup",
          "Performance optimization",
          "Security best practices",
          "Deployment assistance",
          "Collaborative copywriting",
          "Up to 3 rounds of revisions"
        ],
        addOns: [
          { id: "pages", label: "Additional pages / UI views", priceType: "perUnit", inputType: "quantity", price: 100, unitLabel: "page", startingAt: true },
          { id: "api", label: "Advanced API integrations", priceType: "perUnit", inputType: "quantity", price: 250, unitLabel: "integration", startingAt: true },
          { id: "payments", label: "Payment / subscription systems", priceType: "flat", inputType: "toggle", price: 250, startingAt: true },
          { id: "ai", label: "AI features / automation", priceType: "custom", inputType: "toggle", price: null, customQuote: true },
          { id: "analytics", label: "Advanced analytics dashboard", priceType: "flat", inputType: "toggle", price: 300, startingAt: true },
          { id: "adminFeatures", label: "Custom admin features", priceType: "flat", inputType: "toggle", price: 250, startingAt: true },
          { id: "blog", label: "Blog / content system", priceType: "flat", inputType: "toggle", price: 150, startingAt: true },
          { id: "ga", label: "Google Analytics setup", priceType: "flat", inputType: "toggle", price: 75 },
          { id: "maintenance", label: "Maintenance & support", priceType: "flat", inputType: "toggle", price: 100, recurring: true, unitLabel: "month" }
        ]
      }
    ]
  };

  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  });

  function formatCurrency(amount) {
    return currencyFormatter.format(amount);
  }

  function getProduct(productId) {
    return PRICING_CONFIG.products.find(function (p) { return p.id === productId; });
  }

  function createState(product) {
    const state = {};
    product.addOns.forEach(function (addon) {
      state[addon.id] = { enabled: false, qty: 0 };
    });
    return state;
  }

  function formatAddOnPriceLabel(addon) {
    const prefix = addon.startingAt ? "Starting at " : "";
    if (addon.priceType === "custom") {
      return "Contact us for pricing";
    }
    const amount = formatCurrency(addon.price);
    if (addon.inputType === "quantity") {
      return prefix + amount + " / " + addon.unitLabel;
    }
    if (addon.recurring) {
      return prefix + amount + " / month";
    }
    return prefix + amount + " one-time";
  }

  function calculateTotals(product, state) {
    let oneTime = product.basePrice;
    let recurring = 0;
    let hasStartingAt = false;
    let hasCustomQuote = false;
    const oneTimeLines = [{ label: product.name + " (base)", amount: product.basePrice, recurring: false }];
    const recurringLines = [];

    product.addOns.forEach(function (addon) {
      const s = state[addon.id] || { enabled: false, qty: 0 };

      if (addon.priceType === "custom") {
        if (s.enabled) hasCustomQuote = true;
        return;
      }

      let cost = 0;
      let qtyLabel = "";

      if (addon.inputType === "quantity") {
        const qty = Number(s.qty) || 0;
        cost = qty * addon.price;
        if (qty > 0) qtyLabel = " (x" + qty + ")";
      } else if (s.enabled) {
        cost = addon.price;
      }

      if (cost <= 0) return;

      if (addon.startingAt) hasStartingAt = true;

      const line = { label: addon.label + qtyLabel, amount: cost, recurring: !!addon.recurring };

      if (addon.recurring) {
        recurring += cost;
        recurringLines.push(line);
      } else {
        oneTime += cost;
        oneTimeLines.push(line);
      }
    });

    return {
      oneTime: oneTime,
      recurring: recurring,
      hasStartingAt: hasStartingAt,
      hasCustomQuote: hasCustomQuote,
      lines: oneTimeLines.concat(recurringLines)
    };
  }

  function renderFeatures(root, product) {
    const list = root.querySelector("[data-calc-features]");
    list.innerHTML = "";
    product.includedFeatures.forEach(function (feature) {
      const li = document.createElement("li");
      li.textContent = feature;
      list.appendChild(li);
    });
  }

  function renderAddOns(root, product, state, onChange) {
    const container = root.querySelector("[data-calc-addons]");
    const idPrefix = root.id || "calc";
    container.innerHTML = "";

    product.addOns.forEach(function (addon) {
      const row = document.createElement("div");
      row.className = "calc-addon-row";

      const labelWrap = document.createElement("div");
      labelWrap.className = "calc-addon-row-label";

      const inputId = idPrefix + "-addon-" + addon.id;

      const labelEl = document.createElement("label");
      labelEl.setAttribute("for", inputId);
      labelEl.textContent = addon.label;
      if (addon.recurring) {
        const badge = document.createElement("span");
        badge.className = "calc-recurring-badge";
        badge.textContent = "Recurring";
        labelEl.appendChild(badge);
      }

      const priceEl = document.createElement("span");
      priceEl.className = "calc-addon-price" + (addon.customQuote ? " calc-addon-price--quote" : "");
      priceEl.textContent = formatAddOnPriceLabel(addon);

      labelWrap.appendChild(labelEl);
      labelWrap.appendChild(priceEl);

      const control = document.createElement("div");
      control.className = "calc-addon-control";

      if (addon.inputType === "quantity") {
        const input = document.createElement("input");
        input.type = "number";
        input.min = "0";
        input.step = "1";
        input.inputMode = "numeric";
        input.id = inputId;
        input.value = state[addon.id].qty || 0;
        input.addEventListener("input", function () {
          let val = parseInt(input.value, 10);
          if (isNaN(val) || val < 0) val = 0;
          state[addon.id].qty = val;
          onChange();
        });
        control.appendChild(input);
      } else {
        const input = document.createElement("input");
        input.type = "checkbox";
        input.id = inputId;
        input.checked = !!state[addon.id].enabled;
        input.addEventListener("change", function () {
          state[addon.id].enabled = input.checked;
          onChange();
        });
        control.appendChild(input);
      }

      row.appendChild(labelWrap);
      row.appendChild(control);
      container.appendChild(row);
    });
  }

  function renderSummary(root, product, state) {
    const totals = calculateTotals(product, state);

    const breakdown = root.querySelector("[data-calc-breakdown]");
    breakdown.innerHTML = "";
    totals.lines.forEach(function (line) {
      const li = document.createElement("li");
      li.innerHTML = "<span>" + line.label + "</span><span>" + formatCurrency(line.amount) + (line.recurring ? "/mo" : "") + "</span>";
      breakdown.appendChild(li);
    });

    root.querySelector("[data-calc-onetime]").textContent = formatCurrency(totals.oneTime);

    const recurringRow = root.querySelector("[data-calc-recurring-row]");
    if (totals.recurring > 0) {
      recurringRow.hidden = false;
      root.querySelector("[data-calc-recurring]").textContent = formatCurrency(totals.recurring) + "/month";
    } else {
      recurringRow.hidden = true;
    }

    root.querySelector("[data-calc-starting-note]").hidden = !totals.hasStartingAt;
    root.querySelector("[data-calc-quote-note]").hidden = !totals.hasCustomQuote;

    const payloadField = root.querySelector("[data-calc-payload]");
    if (payloadField) {
      payloadField.value = JSON.stringify({
        lines: totals.lines,
        oneTime: totals.oneTime,
        recurring: totals.recurring,
        hasStartingAt: totals.hasStartingAt,
        hasCustomQuote: totals.hasCustomQuote
      });
    }
  }

  function initCalculator(root) {
    const productId = root.getAttribute("data-locked-product");
    const product = getProduct(productId);
    if (!product) return;

    let state = createState(product);

    function update() {
      renderSummary(root, product, state);
    }

    renderFeatures(root, product);
    renderAddOns(root, product, state, update);
    update();

    const resetBtn = root.querySelector("[data-calc-reset]");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        state = createState(product);
        renderAddOns(root, product, state, update);
        update();
      });
    }
  }

  function init() {
    document.querySelectorAll("[data-calc-root]").forEach(initCalculator);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
