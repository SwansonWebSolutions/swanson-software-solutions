"""
City-specific content for local SEO landing pages.
Keyed by city slug. Each entry supports:
  - intro:  list of paragraph strings (rendered as <p> tags)
  - fit:    list of business-type strings shown as tags
"""

CITY_PROFILES = {
    "paso-robles": {
        "intro": [
            "Paso Robles is the heart of California's Central Coast wine country, with over 200 wineries and a tourism-driven economy that's grown significantly over the past decade. The city's historic downtown has become a genuine destination — drawing visitors for wine tasting, restaurants, events, and boutique retail — and that foot traffic creates real online opportunity for businesses that know how to capture it.",
            "For Paso Robles wineries, tasting rooms, and wine-adjacent businesses, direct-to-consumer eCommerce is one of the highest-leverage investments available. A customer who visits your tasting room and has a great experience will buy again — but only if you make it easy. A Shopify store with wine club signups, online ordering, and a clean mobile experience turns one-time visitors into recurring revenue.",
            "Beyond wine, Paso Robles' growing hospitality, food, and artisan retail sector has the same need: a web presence that converts tourist curiosity into lasting customer relationships.",
        ],
        "fit": [
            "Wineries & tasting rooms",
            "Wine club & DTC wine sales",
            "Hospitality & restaurants",
            "Agritourism",
            "Boutique retail",
            "Artisan food & beverage producers",
        ],
    },
    "westlake-village": {
        "intro": [
            "Westlake Village straddles the Los Angeles and Ventura County line and has developed into one of the region's most concentrated hubs for financial services, insurance, healthcare, legal, and professional consulting firms. The presence of major companies like Dole Food Company (historically) and a dense cluster of wealth management and advisory firms gives the city an unusually professional business character for its size.",
            "Businesses in Westlake Village serve high-net-worth clients who evaluate credibility carefully. A polished, fast, well-structured website — especially for service businesses where trust is everything — is the first filter a prospect applies before ever making contact. SwanTech builds professional web presences for Westlake Village businesses where first impressions carry real weight.",
        ],
        "fit": [
            "Financial & wealth management",
            "Legal & professional services",
            "Insurance",
            "Healthcare & medical practices",
            "High-end consulting",
            "Real estate",
        ],
    },
    "moorpark": {
        "intro": [
            "Moorpark is one of Ventura County's smaller cities — more agricultural in character, home to Moorpark College, and less commercially dense than its neighbors. That means businesses here often serve a loyal but limited local market, and those looking to grow typically need to reach customers beyond city limits.",
            "A well-built Shopify store or professional website opens that door. It lets a Moorpark-based business sell to Simi Valley, Camarillo, Thousand Oaks, and beyond without adding overhead. For agricultural businesses, specialty food producers, and small artisan brands in the Moorpark area, eCommerce is often the most practical path to meaningful growth.",
        ],
        "fit": [
            "Agricultural & food producers",
            "Specialty & artisan brands",
            "Small retail",
            "Moorpark College–adjacent services",
            "Home & landscaping services",
        ],
    },
    "simi-valley": {
        "intro": [
            "Simi Valley is best known nationally as the home of the Ronald Reagan Presidential Library — a major tourism draw that brings hundreds of thousands of visitors to the area annually. Locally, it's a large, family-oriented suburban city with a growing small business base that's increasingly looking to compete online.",
            "The city's population has grown significantly in recent years as residents and businesses move in from more expensive parts of LA County, bringing demand for professional services, local retail, and consumer-facing businesses that need a solid web presence to attract a new customer base that doesn't know them yet.",
            "For Simi Valley businesses, a professional website is often the credibility signal that converts a stranger into a first customer.",
        ],
        "fit": [
            "Local retail & services",
            "Family-oriented businesses",
            "Healthcare & wellness",
            "Real estate & home services",
            "Businesses moving from referral-only to online discovery",
        ],
    },
    "calabasas": {
        "intro": [
            "Calabasas is one of the most affluent communities in Los Angeles County — home to high-profile residents, gated neighborhoods, and a retail and dining culture that caters to a discerning, high-spending clientele. Businesses that operate here, or that target the Calabasas demographic, need a web presence that matches the expectation of quality the local market carries.",
            "That means more than just a functional website. It means thoughtful design, fast load times, polished product photography integration, and a checkout experience that doesn't give customers a reason to hesitate. For Calabasas-based brands — in beauty, lifestyle, luxury retail, fitness, or professional services — the website is often the first and strongest signal of brand quality.",
            "SwanTech builds Shopify stores and web experiences for Calabasas businesses that take their brand seriously.",
        ],
        "fit": [
            "Luxury & lifestyle retail",
            "Beauty & wellness",
            "High-end professional services",
            "Personal brands",
            "Fitness & health",
        ],
    },
    "agoura-hills": {
        "intro": [
            "Agoura Hills sits in the eastern Conejo Valley, tucked between the Santa Monica Mountains and the 101 — a quieter community with a tight-knit small business base and a loyal local customer demographic. It's not a city that gets a lot of attention from large agencies, which means local business owners have often made do with outdated websites or free website builder plans that don't reflect the quality of what they actually offer.",
            "The live music and events community around Agoura Hills — anchored historically by venues like The Canyon — also creates demand from event-adjacent businesses: photographers, caterers, local hospitality operators, and service businesses serving the entertainment corridor.",
            "SwanTech builds for businesses in Agoura Hills that are ready for a website that actually works — clean, fast, and built to convert local traffic into real customers.",
        ],
        "fit": [
            "Local retail & services",
            "Events & hospitality",
            "Home services",
            "Outdoor & recreation",
            "Small professional practices",
        ],
    },
    "los-angeles": {
        "intro": [
            "Los Angeles is the second-largest city in the country and one of the most competitive markets in the world for online retail, apps, and digital services. The sheer size of the opportunity — and the density of potential customers — makes a strong web presence non-negotiable for any LA-area business with growth ambitions.",
            "LA businesses also face a specific challenge: the market is flooded with agencies charging LA prices. SwanTech offers a direct alternative — professional Shopify stores, custom web apps, and iOS development at rates that make sense for growing businesses, not just funded startups. No account managers, no bloated retainers, no handoffs.",
            "The industries we work with most in LA include fashion and apparel, food and beverage, creative and media-adjacent businesses, fitness and wellness, and product brands using Shopify as their primary sales channel.",
        ],
        "fit": [
            "Fashion & apparel",
            "DTC product brands",
            "Creative industry services",
            "Food & beverage",
            "Fitness & wellness",
            "Entertainment-adjacent businesses",
            "Startups",
        ],
    },
    "santa-barbara": {
        "intro": [
            "Santa Barbara operates at a different pace and price point than most of Southern California. Tourism is a pillar — the city draws millions of visitors annually to its white architecture, wine country, waterfront, and State Street retail — but it's also home to a deeply rooted community of independent business owners who've built something worth protecting.",
            "For retail and hospitality businesses in Santa Barbara, the opportunity is in converting tourist interest into lasting online customers. A visitor who discovers a boutique on State Street should have an easy path to buying again from home. That requires a real Shopify store with a shopping experience that matches the quality of the in-person brand.",
            "UCSB also feeds a steady pipeline of startups and small tech ventures into the area that often need their first professional web presence built quickly and affordably.",
        ],
        "fit": [
            "Tourism retail & hospitality",
            "Wine & food brands",
            "Boutique & lifestyle brands",
            "UCSB-adjacent startups",
            "Professional services",
        ],
    },
    "thousand-oaks": {
        "intro": [
            "Thousand Oaks is home to Amgen's global headquarters — one of the world's largest biotech companies — and that anchor shapes the local economy in meaningful ways. The city draws well-educated, high-income residents and the professional service businesses that serve them: financial advisors, health and wellness practices, specialty retailers, and consulting firms.",
            "Business owners here are typically sophisticated buyers who care about quality, attention to detail, and long-term reliability. They're not looking for the cheapest option — they're looking for the right one. SwanTech's direct, no-agency-overhead model fits well: you work with the developer, not a rotating cast of account managers.",
            "Thousand Oaks businesses also serve a population that researches online before spending. A polished, fast, mobile-optimized website isn't a nice-to-have here — it's a baseline expectation.",
        ],
        "fit": [
            "Professional & financial services",
            "Health & wellness",
            "Specialty retail",
            "Biotech-adjacent consulting",
            "High-end home services",
        ],
    },
    "camarillo": {
        "intro": [
            "Camarillo has two distinct business personalities. The first is the Camarillo Premium Outlets — one of the busiest shopping destinations on the Central Coast, drawing visitors from across Southern California. The second is a quieter but growing professional and tech corridor, anchored in part by Cal State Channel Islands and a steady influx of businesses relocating from more expensive LA County markets.",
            "Both sides of Camarillo create web development demand. Outlet-adjacent retail brands often need their own direct-to-consumer Shopify store alongside their physical presence. And the growing class of professional services firms, consultants, and small tech companies in Camarillo need credible, fast-loading websites that reflect the quality of their work.",
        ],
        "fit": [
            "Retail & outlet-adjacent brands",
            "Professional services",
            "Businesses relocating from LA",
            "CSU Channel Islands ecosystem",
            "Real estate & property services",
        ],
    },
    "oxnard": {
        "intro": [
            "Oxnard is Ventura County's largest city and one of the most economically diverse — a working port, one of the state's most productive agricultural regions, and a growing residential base that often gets overlooked by tech vendors focused on more affluent neighboring cities. That gap is an opportunity.",
            "Businesses in Oxnard — from strawberry distributors to harbor-side seafood restaurants to retail shops serving the Navy base community at Point Mugu — frequently have strong local customer bases but minimal digital infrastructure. A well-built Shopify store or service website levels the playing field against competitors who got online earlier.",
            "SwanTech builds for Oxnard businesses that are ready to stop relying entirely on foot traffic and word of mouth.",
        ],
        "fit": [
            "Agricultural & food businesses",
            "Port & logistics adjacent",
            "Military community retail & services",
            "Multicultural retail",
            "Waterfront hospitality",
        ],
    },
    "ventura": {
        "intro": [
            "Ventura's business community is built around independent ownership. The downtown corridor along Main Street is packed with locally-run boutiques, surf shops, restaurants, and galleries — the kind of businesses where the owner is also the one opening the door in the morning. That independence is a strength, but it also means web presence often lags behind the quality of the actual product or service.",
            "SwanTech is based right here in Ventura. We work with local businesses that want a real online presence — not a template from a national agency that's never set foot on California Street. Whether you're selling goods at the Ventura Farmers Market and want to expand online, running a surf brand out of the harbor area, or operating a service business serving Ventura County, we build what you actually need.",
        ],
        "fit": [
            "Tourism retail",
            "Surf & outdoor brands",
            "Restaurant & hospitality",
            "Arts & gallery",
            "Professional services",
            "Channel Islands tourism",
        ],
    },
}
