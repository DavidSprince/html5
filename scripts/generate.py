#!/usr/bin/env python3
"""
Static site generator for ReelsHub Vault (plain HTML5/CSS/JS build).

Reads the same JSON data used by the React version (categories.json,
groupPages.json) and renders it through Jinja2 templates into a fully
static site: no build step required at runtime, works on any static host
(Vercel, Netlify, GitHub Pages, or a plain file server).

Run: python3 scripts/generate.py
Then: npm run build:css   (compiles Tailwind once, or run npm run build to do both)
"""
import json
import re
import sys
from pathlib import Path
from datetime import date

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from icons import icon_svg          # noqa: E402
from colors import get_color        # noqa: E402
from markdown import render_markdown  # noqa: E402

SITE_NAME = "ReelsHub Vault"
SITE_URL = "https://reelshub-vault.vercel.app"  # TODO: replace with your real domain
TODAY = date.today().strftime("%B %-d, %Y") if sys.platform != "win32" else date.today().strftime("%B %d, %Y")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
categories = json.loads((ROOT / "data" / "categories.json").read_text())
group_pages = json.loads((ROOT / "data" / "groupPages.json").read_text())

GROUP_SLUG = {g["group"]: g["slug"] for g in group_pages}


def group_href_html(group_name, root=""):
    slug = GROUP_SLUG.get(group_name)
    if slug:
        return f"{root}category/{slug}.html"
    return f"{root}bundles.html"


# ---------------------------------------------------------------------------
# Jinja2 environment
# ---------------------------------------------------------------------------
env = Environment(
    loader=FileSystemLoader(str(ROOT / "templates")),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
env.globals["icon"] = icon_svg
env.globals["get_color"] = get_color
env.filters["markdown"] = render_markdown
env.globals["group_href"] = group_href_html
env.globals["site_name"] = SITE_NAME
env.globals["site_url"] = SITE_URL
env.globals["today"] = TODAY
env.globals["all_categories"] = categories
env.globals["all_groups"] = group_pages

# footer needs a stable, readable subset of groups
FOOTER_GROUPS = group_pages[:6]
env.globals["footer_groups"] = FOOTER_GROUPS


def render(template_name, out_path: Path, **ctx):
    tmpl = env.get_template(template_name)
    html = tmpl.render(**ctx)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  wrote {out_path.relative_to(ROOT)}")


def base_ctx(path, title=None, description=None, keywords=None, og_type="website", json_ld=None, active_nav=None, root="./"):
    full_title = f"{title} | {SITE_NAME}" if title else f"{SITE_NAME} — Free Copyright-Free Reels & Digital Product Bundles"
    desc = description or (
        "Download free, copyright-free reels, ebooks, templates, courses and software bundles. "
        "Curated categories with genuine articles, tips, and one-click free downloads."
    )
    return dict(
        path=path,
        full_title=full_title,
        description=desc,
        keywords=keywords or [],
        og_type=og_type,
        json_ld=json_ld or [],
        active_nav=active_nav,
        root=root,
    )


print("Generating ReelsHub Vault static site...")

# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------
groups_order = []
seen = set()
for c in categories:
    if c["group"] not in seen:
        seen.add(c["group"])
        groups_order.append(c["group"])

group_counts = {}
for c in categories:
    group_counts[c["group"]] = group_counts.get(c["group"], 0) + 1

featured = categories[:8]

render(
    "pages/home.html",
    ROOT / "index.html",
    **base_ctx("/", active_nav="home", root="./"),
    total=len(categories),
    groups_order=groups_order,
    group_counts=group_counts,
    featured=featured,
)

# ---------------------------------------------------------------------------
# All Bundles page
# ---------------------------------------------------------------------------
groups_list = groups_order
render(
    "pages/bundles.html",
    ROOT / "bundles.html",
    **base_ctx(
        "/bundles.html",
        title="All Free Bundles",
        description="Browse all free, copyright-free reels, ebooks, templates, courses and software bundles across motivation, religious, anime, fitness, cars, art & craft and more.",
        active_nav="bundles",
        root="./",
    ),
    categories=categories,
    groups_list=groups_list,
    group_counts=group_counts,
)

# ---------------------------------------------------------------------------
# Category hub pages (25)
# ---------------------------------------------------------------------------
for gp in group_pages:
    items = [c for c in categories if c["group"] == gp["group"]]
    jsonld_collection = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{gp['group']} — Free Bundles",
        "description": re.sub(r"\*\*", "", gp["content"]["intro"])[:160],
        "about": ", ".join(gp["keywords"]),
    })
    jsonld_faq = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in gp["content"]["faq"]
        ],
    })
    render(
        "pages/category_hub.html",
        ROOT / "category" / f"{gp['slug']}.html",
        **base_ctx(
            f"/category/{gp['slug']}.html",
            title=f"{gp['group']} — Free Bundles & Guides",
            description=re.sub(r"\*\*", "", gp["content"]["intro"])[:155],
            keywords=gp["keywords"],
            og_type="website",
            json_ld=[jsonld_collection, jsonld_faq],
            root="../",
        ),
        hub=gp,
        items=items,
    )

# ---------------------------------------------------------------------------
# Bundle post pages (57)
# ---------------------------------------------------------------------------
for item in categories:
    related = [c for c in categories if c["group"] == item["group"] and c["slug"] != item["slug"]][:4]
    article = item["article"]
    word_count = len(
        " ".join(
            [article["intro"], article["para2"], article["cta"], article["closer"],
             article["useCases"], article["deepDive"], article["platformTips"]]
            + article["whatsIncluded"] + article["whyUse"] + article["howToUse"] + article["tips"]
            + [f"{f['q']} {f['a']}" for f in article["faq"]]
        ).split()
    )
    reading_time = max(1, round(word_count / 220))

    jsonld_article = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["title"],
        "articleSection": item["group"],
        "inLanguage": item["language"],
        "keywords": ", ".join(item.get("keywords", item["tags"])),
        "about": ", ".join(item["tags"]),
    })
    jsonld_faq = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in article["faq"]
        ],
    })

    render(
        "pages/category_post.html",
        ROOT / "bundles" / f"{item['slug']}.html",
        **base_ctx(
            f"/bundles/{item['slug']}.html",
            title=item["title"],
            description=re.sub(r"\*\*", "", article["intro"])[:155],
            keywords=item.get("keywords", item["tags"]),
            og_type="article",
            json_ld=[jsonld_article, jsonld_faq],
            root="../",
        ),
        item=item,
        related=related,
        reading_time=reading_time,
    )

# ---------------------------------------------------------------------------
# Static informational / legal pages
# ---------------------------------------------------------------------------
render(
    "pages/about.html",
    ROOT / "about.html",
    **base_ctx(
        "/about.html",
        title="About Us",
        description="Learn about ReelsHub Vault — a free library of copyright-free reels, ebooks, templates, courses and software bundles for creators and entrepreneurs.",
        active_nav="about",
        root="./",
    ),
    total=len(categories),
)

render(
    "pages/contact.html",
    ROOT / "contact.html",
    **base_ctx(
        "/contact.html",
        title="Contact Us",
        description="Get in touch with the ReelsHub Vault team — report broken links, suggest new bundles, or ask a question.",
        active_nav="contact",
        root="./",
    ),
)

LEGAL_PAGES = [
    ("privacy-policy", "Privacy Policy", "pages/privacy.html", "Read the ReelsHub Vault privacy policy, including how we use cookies and third-party advertising."),
    ("terms", "Terms of Service", "pages/terms.html", "Terms of Service for ReelsHub Vault — rules and conditions for using our free bundle library."),
    ("disclaimer", "Disclaimer", "pages/disclaimer.html", "Important disclaimer regarding third-party content, copyright status, and use of bundles listed on ReelsHub Vault."),
    ("dmca", "DMCA Policy", "pages/dmca.html", "How to submit a DMCA takedown request for content linked on ReelsHub Vault."),
]
for slug, title, template, desc in LEGAL_PAGES:
    render(
        template,
        ROOT / f"{slug}.html",
        **base_ctx(f"/{slug}.html", title=title, description=desc, root="./"),
    )

# ---------------------------------------------------------------------------
# 404 page
# ---------------------------------------------------------------------------
render(
    "pages/404.html",
    ROOT / "404.html",
    **base_ctx("/404.html", title="Page Not Found", root="./"),
)

# ---------------------------------------------------------------------------
# sitemap.xml + robots.txt
# ---------------------------------------------------------------------------
urls = ["/", "/bundles.html", "/about.html", "/contact.html", "/privacy-policy.html",
        "/terms.html", "/disclaimer.html", "/dmca.html"]
urls += [f"/category/{g['slug']}.html" for g in group_pages]
urls += [f"/bundles/{c['slug']}.html" for c in categories]

sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sitemap_xml += f"  <url>\n    <loc>{SITE_URL}{u}</loc>\n  </url>\n"
sitemap_xml += "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
print(f"  wrote sitemap.xml ({len(urls)} urls)")

robots_txt = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
(ROOT / "robots.txt").write_text(robots_txt, encoding="utf-8")
print("  wrote robots.txt")

ads_txt = (
    "# Replace this line with the exact snippet Google AdSense gives you\n"
    "# after your site is approved, e.g.:\n"
    "# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n"
)
(ROOT / "ads.txt").write_text(ads_txt, encoding="utf-8")
print("  wrote ads.txt")

print(f"\nDone. Generated {2 + len(group_pages) + len(categories) + len(LEGAL_PAGES) + 1} HTML pages.")
