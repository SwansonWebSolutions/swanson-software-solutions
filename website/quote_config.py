"""Pricing and choice configuration for the web quote request flow."""

PROJECT_TYPE_CHOICES = (
    ("new_website", "New website"),
    ("redesign", "Redesign an existing website"),
    ("ecommerce", "E-commerce or online store"),
    ("custom_advanced", "Custom website with advanced functionality"),
    ("updates", "Website updates or improvements"),
    ("not_sure", "I’m not sure yet"),
)

PRIMARY_GOAL_CHOICES = (
    ("leads", "Generate leads"),
    ("products", "Sell products"),
    ("services", "Explain my services"),
    ("bookings", "Accept bookings or appointments"),
    ("members", "Provide customer/member access"),
    ("replace", "Replace an outdated website"),
    ("other", "Other"),
)

PAGE_COUNT_CHOICES = (
    ("1_5", "1–5"),
    ("6_10", "6–10"),
    ("11_20", "11–20"),
    ("more_20", "More than 20"),
    ("not_sure", "I’m not sure"),
)

FEATURE_CHOICES = (
    ("contact_forms", "Contact forms"),
    ("booking", "Booking or scheduling"),
    ("ecommerce", "E-commerce"),
    ("blog", "Blog or content management"),
    ("accounts", "Customer accounts"),
    ("payments", "Payments or subscriptions"),
    ("admin", "Admin dashboard"),
    ("integrations", "External system integrations"),
    ("seo", "Search engine optimization"),
    ("other", "Other"),
)

MAINTENANCE_CHOICES = (
    ("hosting", "Hosting and website maintenance"),
    ("blog_post", "SEO blog posts"),
    ("product_upload", "New product additions"),
    ("content_update", "Updated website content"),
    ("reporting", "Automated reporting"),
    ("none", "No ongoing maintenance needed"),
)

BASE_PRICES = {
    "standard": 800,
    "custom_advanced": 3000,
}

# These are the initial working estimates. They are deliberately centralized so
# pricing can be revised without changing the form or view logic.
PAGE_PRICES = {
    "1_5": 0,
    "6_10": 200,
    "11_20": 600,
    "more_20": 1000,
    "not_sure": 0,
}

FEATURE_PRICES = {
    "contact_forms": 0,
    "booking": 250,
    "ecommerce": 200,
    "blog": 150,
    "accounts": 250,
    "payments": 250,
    "admin": 250,
    "integrations": 250,
    "seo": 0,
    "other": 0,
}

MAINTENANCE_PRICES = {
    "hosting": {"amount": 50, "unit": "month", "label": "Hosting and website maintenance"},
    "blog_post": {"amount": 100, "unit": "month", "label": "SEO blog posts (2 per month)"},
    "product_upload": {"amount": 5, "unit": "product", "label": "New product upload"},
    "content_update": {"amount": 50, "unit": "month", "label": "Content updates"},
    "reporting": {"amount": 50, "unit": "month", "label": "Automated reporting"},
}

FRONTEND_PRICING = {
    "base": BASE_PRICES,
    "pages": PAGE_PRICES,
    "features": FEATURE_PRICES,
    "maintenance": MAINTENANCE_PRICES,
}


def choice_label(choices, value):
    return dict(choices).get(value, value or "Not specified")


def calculate_quote(data):
    """Return an itemized preliminary estimate for validated form data."""
    project_type = data.get("project_type")
    base = BASE_PRICES["custom_advanced"] if project_type == "custom_advanced" else BASE_PRICES["standard"]
    one_time_lines = [{
        "label": f"{choice_label(PROJECT_TYPE_CHOICES, project_type)} base project",
        "amount": base,
    }]

    page_count = data.get("page_count")
    page_amount = PAGE_PRICES.get(page_count, 0)
    if page_amount:
        one_time_lines.append({
            "label": f"Website size: {choice_label(PAGE_COUNT_CHOICES, page_count)} pages",
            "amount": page_amount,
        })

    for feature in data.get("features", []):
        amount = FEATURE_PRICES.get(feature, 0)
        one_time_lines.append({
            "label": choice_label(FEATURE_CHOICES, feature),
            "amount": amount,
        })

    maintenance_lines = []
    monthly_total = 0
    variable_rates = []
    for maintenance in data.get("maintenance", []):
        if maintenance == "none":
            continue
        item = MAINTENANCE_PRICES[maintenance]
        line = {
            "label": item["label"],
            "amount": item["amount"],
            "unit": item["unit"],
        }
        maintenance_lines.append(line)
        if item["unit"] == "month":
            monthly_total += item["amount"]
        else:
            variable_rates.append(line)

    return {
        "one_time_lines": one_time_lines,
        "maintenance_lines": maintenance_lines,
        "variable_rates": variable_rates,
        "one_time_total": sum(line["amount"] for line in one_time_lines),
        "monthly_total": monthly_total,
    }
