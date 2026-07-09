"""
Content for the individual service landing pages (/services/<slug>/).
Keyed by URL slug. Each entry drives website/service_detail.html.
"""

_PROCESS_STEPS = [
    {
        "num": "Step 01",
        "title": "We Talk",
        "text": "Book a free 15-minute call or send a message. Tell us what you're building, what's blocking you, and when you need it. No forms, no sales pitch.",
    },
    {
        "num": "Step 02",
        "title": "You Get a Clear Scope",
        "text": "Within 24 hours you'll have a written quote, timeline, and deliverable list. Fixed price. No hourly billing surprises. You approve before anything starts.",
    },
    {
        "num": "Step 03",
        "title": "We Build & Launch",
        "text": "The team moves fast, shares progress along the way, and hands over a live, fully-tested product. You get the code, the keys, and full ownership. Done.",
    },
]

SERVICES = {
    "shopify": {
        "slug": "shopify",
        "nav_label": "Shopify Stores",
        "icon": "fa-brands fa-shopify",
        "accent": "#10b981",
        "eyebrow": "Shopify Development",
        "title": "Professional Shopify Stores, Live in Days.",
        "lead": (
            "A complete, professional Shopify setup — theme, pages, products, payments, SEO, and "
            "launch support included. Delivered in 5–10 business days."
        ),
        "price_amount": "$1,000",
        "price_label": "starting price",
        "price_note": "Typically delivered in 5–10 business days. You keep full ownership of your store. Additional features priced separately.",
        "included": [
            "Shopify theme setup & customization",
            "Mobile-responsive design",
            "Home, About, Shop & Contact pages",
            "Privacy Policy, Terms & Refund Policy",
            "Up to 10 products uploaded",
            "Product collections setup",
            "Payment gateway configuration",
            "Basic shipping setup",
            "Navigation & menu setup",
            "Contact form setup",
            "Newsletter signup form",
            "Basic SEO setup",
            "Social media links",
            "Launch support",
        ],
        "process": _PROCESS_STEPS,
        "inquiry_key": "shopify",
        "calculator_product_id": "shopify",
        "images": [
            {
                "src": "/media/services/pexels-shoper-pl-550490863-16675632.jpg",
                "alt": "Setting up a new online store on a laptop",
            },
            {
                "src": "/media/services/pexels-mart-production-7679865.jpg",
                "alt": "Customizing product listings for an online store",
            },
        ],
        "cta_label": "Start My Shopify Store",
        "seo_title": "Professional Affordable Shopify Store Development | SwanTech",
        "seo_description": (
            "Professional, affordable Shopify store development. Custom theme setup, product "
            "uploads, payment integration, and SEO — done right, start to finish."
        ),
        "seo_keywords": (
            "affordable shopify store development, professional shopify developer, shopify "
            "ecommerce development, shopify store setup service, shopify theme customization, "
            "small business shopify store"
        ),
    },
    "custom-web-apps": {
        "slug": "custom-web-apps",
        "nav_label": "Custom Web Apps",
        "icon": "fa-solid fa-code",
        "accent": "#2563eb",
        "eyebrow": "Custom Web Development",
        "title": "Custom Web Applications, Built Around Your Workflow.",
        "lead": (
            "Dashboards, booking systems, SaaS platforms, and internal tools — designed and built "
            "to fit your exact process, not a generic template."
        ),
        "price_amount": "Custom quote",
        "price_label": "fixed price",
        "price_note": "Every project is scoped clearly and quoted at a fixed price before work starts — no hourly billing surprises.",
        "included": [
            "Requirements & technical scoping call",
            "Custom UI/UX design",
            "Responsive, production-grade front end",
            "Secure backend & database architecture",
            "Authentication & user accounts (if needed)",
            "Third-party API integrations",
            "Admin dashboard / internal tools",
            "Testing across devices & browsers",
            "Deployment & hosting setup",
            "30 days of post-launch support",
        ],
        "process": _PROCESS_STEPS,
        "inquiry_key": "web",
        "calculator_product_id": "custom",
        "cta_label": "Plan Your Build",
        "seo_title": "Custom Web Application Development | SwanTech",
        "seo_description": (
            "Custom web applications, dashboards, and SaaS platforms built around your exact "
            "workflow. Fixed price, quoted within 24 hours."
        ),
        "seo_keywords": (
            "custom web application development, SaaS development, web app developer, dashboard "
            "development, booking system development, custom software development, business web "
            "application"
        ),
    },
    "ios-apps": {
        "slug": "ios-apps",
        "nav_label": "iOS Apps",
        "icon": "fa-brands fa-apple",
        "accent": "#6d28d9",
        "eyebrow": "iOS App Development",
        "title": "Polished iOS Apps, From Idea to App Store.",
        "lead": (
            "Native iPhone apps for businesses, creators, and startups — clean design, real-world "
            "usability, and a smooth path through App Store review."
        ),
        "price_amount": "Custom quote",
        "price_label": "fixed price",
        "price_note": "Every project is scoped clearly and quoted at a fixed price before work starts — no hourly billing surprises.",
        "included": [
            "Product scoping & feature planning",
            "Native SwiftUI design & build",
            "Backend & API integration",
            "User accounts & authentication",
            "Push notifications (if needed)",
            "In-app purchases / subscriptions (if needed)",
            "QA across iPhone models & iOS versions",
            "App Store listing & submission",
            "App Store review support",
            "30 days of post-launch support",
        ],
        "process": _PROCESS_STEPS,
        "inquiry_key": "app",
        "cta_label": "Discuss Your App",
        "seo_title": "iOS App Development | SwanTech",
        "seo_description": (
            "Native iOS app design, development, and App Store launch support. Clean SwiftUI "
            "builds with hands-on developer access."
        ),
        "seo_keywords": (
            "iOS app development, iPhone app developer, SwiftUI development, App Store launch, "
            "native iOS app design, mobile app developer, custom iOS app"
        ),
    },
    "wix-websites": {
        "slug": "wix-websites",
        "nav_label": "Wix Websites",
        "icon": "fa-solid fa-globe",
        "accent": "#f59e0b",
        "eyebrow": "Wix Website Development",
        "title": "Simple, Professional Wix Websites.",
        "lead": (
            "Clean, easy-to-manage websites for service businesses and creators — built on Wix so "
            "you can make small updates yourself without touching code."
        ),
        "price_amount": "Affordable pricing",
        "price_label": "quoted after a quick call",
        "price_note": "Priced to fit small business budgets. You get full editor access so you're never locked out of your own site.",
        "included": [
            "Custom Wix template setup",
            "Mobile-responsive design",
            "Home, About, Services/Shop & Contact pages",
            "Domain connection",
            "Contact form setup",
            "Basic SEO setup",
            "Social media links",
            "Editor walkthrough so you can make updates yourself",
            "Launch support",
        ],
        "process": _PROCESS_STEPS,
        "inquiry_key": "wix",
        "calculator_product_id": "wix",
        "cta_label": "Get a Quote",
        "seo_title": "Wix Website Development | SwanTech",
        "seo_description": (
            "Simple, professional Wix websites for service businesses and creators. Affordable "
            "pricing, fast turnaround, easy to manage."
        ),
        "seo_keywords": (
            "Wix website development, Wix designer, small business website, affordable website "
            "design, Wix developer, professional Wix site"
        ),
    },
}

SERVICE_ORDER = ["shopify", "custom-web-apps", "ios-apps", "wix-websites"]
